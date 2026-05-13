# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class ConversationState(BaseModel):

    conversation_id: str

    trace_id: str

    current_agent: str = "triage"

    messages: List[Dict[str, Any]] = Field(default_factory=list)

    extracted_entities: Dict[str, Any] = Field(default_factory=dict)

    handover_history: List[Dict[str, Any]] = Field(default_factory=list)