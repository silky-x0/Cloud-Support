import logging
from typing import Optional

from agents.base_agent import BaseAgent
from models.conversation import ConversationState
from models.agent_response import AgentResponse
from retrieval.retriever import Retriever

logger = logging.getLogger(__name__)

class TechnicalAgent(BaseAgent):
    """
    Resolves technical issues using KB articles and troubleshooting guides.
    Uses configured prompts and retrieval parameters.
    """

    def __init__(self, name: str, config: Optional[dict] = None):
        super().__init__(name, config)
        self.retriever = Retriever()
        self.retrieval_top_k = self.config.get("retrieval_top_k", 5)

    async def handle(self, query: str, state: ConversationState) -> AgentResponse:
        self._log_invocation(state)

        context, citations = self.retriever.retrieve(query, k=self.retrieval_top_k)

        full_system_prompt = f"""
{self.system_prompt}

KNOWLEDGE BASE CONTEXT:
{context}
"""

        try:
            history = self._build_history(state, last_n=4)
            
            content = await self._call_llm(
                system_prompt=full_system_prompt,
                user_message=query,
                history=history,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            escalate = False
            if "I don't have verified information" in content:
                escalate = True

            # Detect if we need to handover to billing (Scenario 2)
            handover_required = False
            handover_target = None
            
            billing_triggers = ["upgrade", "billing", "invoice", "plan", "subscription", "enterprise", "pro"]
            has_billing_intent = any(trigger in query.lower() for trigger in billing_triggers)
            has_billing_entity = state.extracted_entities.get("plan_change") is not None
            
            if has_billing_intent or has_billing_entity:
                handover_required = True
                handover_target = "billing"
                logger.info(f"Technical agent triggering handover to {handover_target}")

            return AgentResponse(
                agent=self.name,
                content=content,
                citations=citations,
                handover_required=handover_required,
                handover_target=handover_target,
                escalate=escalate,
                confidence=1.0 if citations else 0.5
            )

        except Exception as e:
            logger.error(f"Technical Agent error: {str(e)}", exc_info=True)
            return self._error_response("technical_resolution_failed")
