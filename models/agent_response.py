# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from typing import Optional, List
from models.message import Citation


class AgentResponse(BaseModel):
    agent: str
    content: str
    citations: List[Citation] = []
    routing_decision: Optional[str] = None
    handover_required: bool = False
    handover_target: Optional[str] = None

    escalate: bool = False
    confidence: float = 1.0
