"""
Unit tests for TriageAgent intent classification.
All LLM calls are mocked — zero API cost.
"""
import json
# pyrefly: ignore [missing-import]
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from datetime import datetime

from agents.triage_agent import TriageAgent
from models.conversation import ConversationState


def _make_state() -> ConversationState:
    return ConversationState(
        conversation_id="test-conv",
        trace_id="test-trace",
        created_at=datetime.utcnow().isoformat(),
    )


def _llm_response(intent: str, routing: str, entities: dict = None) -> str:
    return json.dumps({
        "intent": intent,
        "routing_decision": routing,
        "entities": entities or {},
        "urgency": "medium",
    })


@pytest.mark.asyncio
async def test_scenario1_technical_issue():
    """AWS alerts query → routed to 'technical'."""
    agent = TriageAgent("triage", {"temperature": 0.2, "max_tokens": 512})
    query = "My CloudDash alerts stopped firing after I updated my AWS integration credentials yesterday."

    with patch.object(agent, "_call_llm", new=AsyncMock(return_value=_llm_response(
        "technical_issue", "technical", {"product": "aws_integration"}
    ))):
        response = await agent.handle(query, _make_state())

    assert response.routing_decision == "technical"


@pytest.mark.asyncio
async def test_scenario2_cross_agent():
    """SSO + upgrade query → routed to 'technical' first (primary intent)."""
    agent = TriageAgent("triage", {"temperature": 0.2, "max_tokens": 512})
    query = "I want to upgrade from Pro to Enterprise, but first check my SSO issue."

    with patch.object(agent, "_call_llm", new=AsyncMock(return_value=_llm_response(
        "technical_issue", "technical", {"plan_change": "pro_to_enterprise"}
    ))):
        response = await agent.handle(query, _make_state())

    assert response.routing_decision == "technical"


@pytest.mark.asyncio
async def test_scenario3_billing_escalation():
    """Double-charge + refund query → routed to 'billing'."""
    agent = TriageAgent("triage", {"temperature": 0.2, "max_tokens": 512})
    query = "I've been charged twice for April. I need an immediate refund and I want to speak to a manager."

    with patch.object(agent, "_call_llm", new=AsyncMock(return_value=_llm_response(
        "billing_inquiry", "billing", {"urgency": "high", "issue": "duplicate_charge"}
    ))):
        response = await agent.handle(query, _make_state())

    assert response.routing_decision == "billing"


@pytest.mark.asyncio
async def test_scenario4_general_inquiry():
    """Datadog integration query (no KB) → routed to 'technical' for retrieval attempt."""
    agent = TriageAgent("triage", {"temperature": 0.2, "max_tokens": 512})
    query = "Does CloudDash support integration with Datadog?"

    with patch.object(agent, "_call_llm", new=AsyncMock(return_value=_llm_response(
        "general_inquiry", "technical"
    ))):
        response = await agent.handle(query, _make_state())

    assert response.routing_decision in ("technical", "triage")


@pytest.mark.asyncio
async def test_triage_llm_failure_returns_error_response():
    """When LLM raises an exception, triage must return a graceful error response."""
    agent = TriageAgent("triage", {"temperature": 0.2, "max_tokens": 512})

    with patch.object(agent, "_call_llm", new=AsyncMock(side_effect=Exception("timeout"))):
        response = await agent.handle("anything", _make_state())

    assert response.agent == "triage"
    assert response.content  # some non-empty fallback message
