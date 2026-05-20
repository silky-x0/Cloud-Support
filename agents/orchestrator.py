import uuid
import logging
import yaml
import os
from datetime import datetime, timezone
from typing import Optional

from agents.base_agent import BaseAgent
from models.conversation import ConversationState
from models.agent_response import AgentResponse
from models.message import Message
from utils.trace import trace_context
from handover.handover_manager import HandoverManager

logger = logging.getLogger(__name__)

_sessions: dict[str, ConversationState] = {}
_handover_manager = HandoverManager()
# ---------------------------------------------------------------------------
_agents: dict[str, BaseAgent] = {}


def _load_agents() -> dict[str, BaseAgent]:
    """
    Load agent configurations from YAML and instantiate agent classes dynamically.
    """
    from agents.triage_agent import TriageAgent
    from agents.technical_agent import TechnicalAgent
    from agents.billing_agent import BillingAgent
    from agents.escalation_agent import EscalationAgent

    # Map of agent names to their concrete classes
    agent_classes = {
        "triage": TriageAgent,
        "technical": TechnicalAgent,
        "billing": BillingAgent,
        "escalation": EscalationAgent,
    }

    config_path = "config/agents.yaml"
    if not os.path.exists(config_path):
        logger.error(f"Agent config not found at {config_path}")
        return {}

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    agents_config = config.get("agents", {})
    loaded_agents = {}

    for name, agent_config in agents_config.items():
        if name in agent_classes:
            loaded_agents[name] = agent_classes[name](name=name, config=agent_config)
            logger.info(f"Loaded agent: {name}")

    return loaded_agents


def get_agents() -> dict[str, BaseAgent]:
    global _agents
    if not _agents:
        _agents = _load_agents()
    return _agents


# ---------------------------------------------------------------------------
# Public helpers used by routes.py
# ---------------------------------------------------------------------------


def create_conversation(customer_id: str = "") -> ConversationState:
    """Start a new conversation and persist it."""
    state = ConversationState(
        conversation_id=str(uuid.uuid4()),
        trace_id=str(uuid.uuid4()),
        customer_id=customer_id,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    _sessions[state.conversation_id] = state
    with trace_context(state.trace_id):
        logger.info(
            "CONVERSATION_STARTED",
            extra={"conversation_id": state.conversation_id, "trace_id": state.trace_id},
        )
    return state


def get_conversation(conversation_id: str) -> Optional[ConversationState]:
    return _sessions.get(conversation_id)


async def chat(conversation_id: str, user_message: str) -> AgentResponse:
    """
    Main pipeline:
      1. Load or 404 the session
      2. Triage  → classify intent, extract entities, set routing_decision
      3. Dispatch to specialist agent
      4. Handle handover if requested (up to MAX_HANDOVERS times)
      5. Handle escalation if flagged
      6. Append both turns to history
      7. Return AgentResponse to the route handler
    """
    MAX_HANDOVERS = 3

    state = _sessions.get(conversation_id)
    if state is None:
        raise KeyError(f"Conversation {conversation_id!r} not found")

    with trace_context(state.trace_id):
        agents = get_agents()

        # ── Step 1: Triage ──────────────────────────────────────────────────────
        # Always re-triage so multi-intent follow-ups route correctly.
        triage_response: AgentResponse = await agents["triage"].handle(
            user_message, state
        )

        # Triage may update entities (customer_id, plan, urgency, etc.)
        if triage_response.routing_decision:
            state.current_agent = triage_response.routing_decision

        logger.info(
            "AGENT_INVOCATION",
            extra={
                "agent": "triage",
                "routed_to": state.current_agent,
            },
        )

        # ── Step 2: Specialist agent ─────────────────────────────────────────────
        # Persist user message before agents start processing
        state.messages.append(Message(role="user", content=user_message, agent="user"))

        response: AgentResponse = await agents[state.current_agent].handle(
            user_message, state
        )

        # Accumulate content and citations
        accumulated_content = response.content
        accumulated_citations = list(response.citations)
        last_agent = state.current_agent

        logger.info(
            "AGENT_INVOCATION",
            extra={
                "agent": state.current_agent,
                "citations": len(response.citations),
                "handover_required": response.handover_required,
                "escalate": response.escalate,
            },
        )

        # ── Step 3: Handover loop ────────────────────────────────────────────────
        handover_count = 0
        while response.handover_required and handover_count < MAX_HANDOVERS:
            # Persist current agent's response before handing over
            state.messages.append(
                Message(
                    role="assistant",
                    content=response.content,
                    agent=state.current_agent,
                    citations=response.citations,
                )
            )

            target = response.handover_target or "triage"
            _handover_manager.execute(
                state,
                source=state.current_agent,
                target=target,
                reason=f"agent_requested_handover_to_{target}",
            )
            try:
                response = await agents[state.current_agent].handle(user_message, state)
                # Append new response parts
                accumulated_content += "\n\n" + response.content
                accumulated_citations.extend(response.citations)
                last_agent = state.current_agent
            except Exception as exc:
                logger.error(
                    "HANDOVER_FAILED",
                    extra={"target": target, "error": str(exc)},
                )
                # Fallback: route back to triage, then escalate if it fails again
                if state.current_agent != "triage":
                    _handover_manager.execute(
                        state,
                        source=state.current_agent,
                        target="triage",
                        reason="handover_failure_fallback",
                    )
                    response = await agents["triage"].handle(user_message, state)
                    accumulated_content += "\n\n" + response.content
                    last_agent = "triage"
                else:
                    response.escalate = True
                break
            handover_count += 1

        # Force escalation if we exceeded handover limit
        if handover_count >= MAX_HANDOVERS:
            response.escalate = True

        # ── Step 4: Escalation ───────────────────────────────────────────────────
        if response.escalate:
            logger.info("ESCALATION", extra={"reason": "agent_flagged"})
            response = await agents["escalation"].handle(user_message, state)
            accumulated_content += "\n\n" + response.content
            last_agent = "escalation"

        # Apply Output Guardrail
        from guardrails.output_guard import redact_pii
        final_content = redact_pii(accumulated_content)

        # ── Step 5: Persist final turn to history ────────────────────────────────
        state.messages.append(
            Message(
                role="assistant",
                content=response.content,
                agent=last_agent,
                citations=response.citations,
            )
        )
        _sessions[conversation_id] = state

        # Return the aggregated response for the API
        return AgentResponse(
            agent=last_agent,
            content=final_content,
            citations=accumulated_citations,
            handover_required=False,
            escalate=False
        )


