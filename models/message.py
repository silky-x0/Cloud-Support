# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime, timezone


class Citation(BaseModel):
    kb_id: str
    title: str
    snippet: str
    score: float


class Message(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str
    agent: str  # which agent produced this message
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    citations: List[Citation] = []
