import logging
from typing import Optional

from agents.base_agent import BaseAgent
from models.conversation import ConversationState
from models.agent_response import AgentResponse

logger = logging.getLogger(__name__)

class EscalationAgent(BaseAgent):
    """
    Handles critical issues and prepares a summary for human handover.
    Does not use retrieval; focuses on conversation context.
    """

    def __init__(self, name: str, config: Optional[dict] = None):
        super().__init__(name, config)

    async def handle(self, query: str, state: ConversationState) -> AgentResponse:
        self._log_invocation(state)

        # 1. Build a full summary of the conversation history for the LLM
        history_str = "\n".join([
            f"{m.role.upper()}: {m.content}"
            for m in state.messages
        ])

        full_system_prompt = f"""
{self.system_prompt}

CONVERSATION HISTORY:
{history_str}

LATEST USER QUERY:
{query}
"""

        try:
            # 2. Call LLM to generate the final response/summary
            # We don't pass history separately here as we've included it in the prompt
            content = await self._call_llm(
                system_prompt=full_system_prompt,
                user_message="Please provide the escalation summary and reassuring message to the user.",
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            return AgentResponse(
                agent=self.name,
                content=content,
                citations=[],
                escalate=False, # We are already at the end of the line
                confidence=1.0
            )

        except Exception as e:
            logger.error(f"Escalation Agent error: {str(e)}", exc_info=True)
            return self._error_response("escalation_failed")
