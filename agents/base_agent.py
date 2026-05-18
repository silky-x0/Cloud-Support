from abc import ABC, abstractmethod
from typing import Optional
import logging
import os
from openai import AsyncOpenAI

from models.conversation import ConversationState
from models.agent_response import AgentResponse
from config.settings import settings

logger = logging.getLogger(__name__)

_openai_client: Optional[AsyncOpenAI] = None


def get_openai_client() -> AsyncOpenAI:
    """Shared singleton so every agent reuses the same HTTP connection pool."""
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client


class BaseAgent(ABC):
    """
    Contract that every agent must satisfy.

    Orchestrator only knows about BaseAgent — never about concrete classes.
    That's why:
      - Adding a new agent = new file + YAML entry, zero changes here or in orchestrator.
      - orchestrator does: response = await agent.handle(query, state)
        regardless of which agent it's talking to.
    """

    def __init__(self, name: str, config: Optional[dict] = None):
        self.name = name
        self.config = config or {}
        self.model = settings.OPENAI_MODEL
        self.system_prompt = self.config.get("system_prompt", "")
        self.temperature = self.config.get("temperature", 0.3)
        self.max_tokens = self.config.get("max_tokens", 1024)



    @abstractmethod
    async def handle(self, query: str, state: ConversationState) -> AgentResponse:
        """
        Process a user query given the current conversation state.
        Must return an AgentResponse — always. Never raise from here;
        catch internally and return a graceful error response instead.
        """


    async def _call_llm(
        self,
        system_prompt: str,
        user_message: str,
        history: Optional[list] = None,
        max_tokens: int = 1024,
        temperature: float = 0.3,
    ) -> str:
        """
        Call OpenAI chat completion.
        history = last N messages already formatted as [{"role": ..., "content": ...}]
        """
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        client = get_openai_client()

        logger.info(
            "LLM_CALL",
            extra={
                "agent": self.name,
                "model": self.model,
                "message_count": len(messages),
                "max_tokens": max_tokens,
            },
        )

        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""

    def _build_history(self, state: ConversationState, last_n: int = 6) -> list:
        """
        Convert the last N ConversationState messages into OpenAI chat format.
        Keeps the context window sane without dumping the full history.
        """
        return [
            {"role": m.role, "content": m.content}
            for m in state.messages[-last_n:]
            if m.role in ("user", "assistant")
        ]

    def _log_invocation(self, state: ConversationState) -> None:
        logger.info(
            "AGENT_INVOCATION",
            extra={
                "agent": self.name,
                "conversation_id": state.conversation_id,
                "trace_id": state.trace_id,
                "history_length": len(state.messages),
            },
        )

    def _error_response(self, reason: str) -> AgentResponse:
        """
        Return a safe, user-friendly response when something goes wrong internally.
        Prevents raw exceptions from reaching the customer.
        """
        return AgentResponse(
            agent=self.name,
            content=(
                "I'm sorry, I ran into an issue processing your request. "
                "Let me connect you with our support team."
            ),
            escalate=True,
            confidence=0.0,
        )
