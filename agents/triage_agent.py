import json
import logging
from typing import Optional

from agents.base_agent import BaseAgent
from models.conversation import ConversationState
from models.agent_response import AgentResponse

logger = logging.getLogger(__name__)

class TriageAgent(BaseAgent):
    """
    The first point of contact.
    Classifies the user's intent and extracts relevant entities using configured prompts.
    """

    def __init__(self, name: str, config: Optional[dict] = None):
        super().__init__(name, config)

    async def handle(self, query: str, state: ConversationState) -> AgentResponse:
        self._log_invocation(state)

        try:
            # Triage usually needs very little history to classify the latest intent
            history = self._build_history(state, last_n=2)
            
            raw_response = await self._call_llm(
                system_prompt=self.system_prompt,
                user_message=query,
                history=history,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            # Extract JSON from the response (handle potential markdown wrapping)
            clean_json = raw_response.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean_json)

            intent = data.get("intent", "general_inquiry")
            routing_decision = data.get("routing_decision", "triage")
            entities = data.get("entities", {})
            urgency = data.get("urgency", "low")

            # Update state with extracted entities and urgency
            state.extracted_entities.update(entities)
            state.extracted_entities["urgency"] = urgency
            
            # If customer_id was extracted, update the main field
            if "customer_id" in entities:
                state.customer_id = entities["customer_id"]

            return AgentResponse(
                agent=self.name,
                content=f"Understood. I'm looking into your request regarding {intent}.",
                routing_decision=routing_decision,
                confidence=1.0
            )

        except Exception as e:
            logger.error(f"Triage error: {str(e)}", exc_info=True)
            return self._error_response("classification_failed")
