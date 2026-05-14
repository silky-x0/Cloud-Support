# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from models.message import Message


class ConversationState(BaseModel):
    conversation_id: str
    trace_id: str
    current_agent: str = "triage"
    messages: List[Message] = Field(default_factory=list)
    extracted_entities: Dict[str, Any] = Field(default_factory=dict)
    handover_history: List[Dict[str, Any]] = Field(default_factory=list)
    customer_id: str = ""
    created_at: str = ""
