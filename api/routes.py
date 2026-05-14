import logging
import uuid
# pyrefly: ignore [missing-import]
from fastapi import APIRouter
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from utils.trace import trace_context

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    trace_id: str


@router.post("/chat", response_model=ChatResponse)
async def chat_stub(body: ChatRequest):
    """
    Temporary stub endpoint for initial integration testing.
    Returns a hardcoded response and the active trace_id.
    """
    with trace_context() as trace_id:
        logger.info("CHAT_STUB_INVOKED", extra={"user_message": body.message})
        
        return ChatResponse(
            reply=f"STUB: I received your message: '{body.message}'. Full agent orchestration is coming soon!",
            trace_id=trace_id
        )


@router.get("/health")
async def health():
    return {"status": "ok"}
