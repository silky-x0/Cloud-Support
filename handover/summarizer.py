import logging
from models.conversation import ConversationState
# pyrefly: ignore [missing-import]
from openai import AsyncOpenAI
from config.settings import settings

logger = logging.getLogger(__name__)

class ConversationSummarizer:
    def __init__(self):
        self.model = settings.OPENAI_MODEL
        self.api_key = settings.OPEN_ROUTER_KEY or settings.OPENAI_API_KEY
        self.base_url = "https://openrouter.ai/api/v1" if settings.OPEN_ROUTER_KEY else None
        
        if self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            self.client = None

    async def summarize(self, state: ConversationState) -> str:
        """
        Summarizes the conversation history in 3 sentences or less.
        """
        if not state.messages:
            return "No conversation history."

        history_str = "\n".join([
            f"{m.role.upper()} ({m.agent}): {m.content}"
            for m in state.messages
        ])

        if not self.client:
            return f"Conversation with {len(state.messages)} turns. Last turn: {state.messages[-1].content[:100]}"

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a support system assistant. Summarize the following customer support conversation in 3 sentences or less, highlighting the customer's main issue, what has been resolved, and what remains pending."
                    },
                    {
                        "role": "user",
                        "content": history_str
                    }
                ],
                temperature=0.2,
                max_tokens=256
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Failed to generate summary: {str(e)}")
            return f"Conversation with {len(state.messages)} turns (summarization failed)."
