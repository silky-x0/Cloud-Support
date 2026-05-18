# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime


class HandoverPayload(BaseModel):
    handover_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_agent: str
    target_agent: str
    reason: str
    conversation_id: str
    trace_id: str
    extracted_entities: Dict[str, Any] = {}
    full_history: List[Dict[str, Any]] = []
    priority: str = "P2"  # P1 | P2 | P3
