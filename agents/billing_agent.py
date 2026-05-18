import logging
from typing import Optional

from agents.base_agent import BaseAgent
from models.conversation import ConversationState
from models.agent_response import AgentResponse
from retrieval.retriever import Retriever

logger = logging.getLogger(__name__)

class BillingAgent(BaseAgent):
    """
    Handles billing inquiries, plan upgrades, and invoice questions.
    Uses configured prompts and retrieval from the billing category.
    """

    def __init__(self, name: str, config: Optional[dict] = None):
        super().__init__(name, config)
        self.retriever = Retriever()
        self.retrieval_top_k = self.config.get("retrieval_top_k", 3)

    async def handle(self, query: str, state: ConversationState) -> AgentResponse:
        self._log_invocation(state)

        # 1. Retrieve relevant context from Knowledge Base
        # We could filter by 'billing' category if the retriever supported it,
        # but for now we rely on similarity.
        context, citations = self.retriever.retrieve(query, k=self.retrieval_top_k)

        # 2. Build the specialized system prompt
        # We inject customer plan info if available in extracted_entities
        customer_info = f"Customer ID: {state.customer_id}\n"
        if state.extracted_entities:
            customer_info += f"Extracted Context: {state.extracted_entities}\n"

        full_system_prompt = f"""
{self.system_prompt}

CUSTOMER INFORMATION:
{customer_info}

KNOWLEDGE BASE CONTEXT:
{context}
"""

        try:
            # 3. Call LLM
            history = self._build_history(state, last_n=4)
            
            content = await self._call_llm(
                system_prompt=full_system_prompt,
                user_message=query,
                history=history,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            # 4. Check for escalation (billing disputes or refund requests)
            escalate = False
            triggers = ["refund", "manager", "dispute", "charged twice", "double charge"]
            if any(trigger in query.lower() for trigger in triggers) or any(trigger in content.lower() for trigger in triggers):
                escalate = True

            return AgentResponse(
                agent=self.name,
                content=content,
                citations=citations,
                escalate=escalate,
                confidence=0.9
            )

        except Exception as e:
            logger.error(f"Billing Agent error: {str(e)}", exc_info=True)
            return self._error_response("billing_resolution_failed")
