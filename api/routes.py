import logging
import uuid
from typing import Optional, List
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException
# pyrefly: ignore [missing-import]
from pydantic import BaseModel

from agents.orchestrator import create_conversation, get_conversation, chat
from models.message import Message, Citation
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


class CreateConversationRequest(BaseModel):
    customer_id: Optional[str] = ""


class CreateConversationResponse(BaseModel):
    conversation_id: str
    trace_id: str


class MessageRequest(BaseModel):
    content: str


class MessageResponse(BaseModel):
    agent: str
    content: str
    citations: List[Citation] = []


@router.post("/conversations", response_model=CreateConversationResponse)
async def start_conversation(body: CreateConversationRequest = None):
    customer_id = body.customer_id if body else ""
    state = create_conversation(customer_id)
    return CreateConversationResponse(
        conversation_id=state.conversation_id,
        trace_id=state.trace_id
    )


@router.post("/conversations/{id}/messages", response_model=MessageResponse)
async def send_message(id: str, body: MessageRequest):
    # Apply Input Guardrail
    from guardrails.input_guard import check_input
    guard_result = check_input(body.content)
    if not guard_result.passed:
        logger.warning(
            "GUARDRAIL_TRIGGERED",
            extra={"reason": guard_result.reason, "conversation_id": id}
        )
        raise HTTPException(
            status_code=400,
            detail=f"Guardrail violation: {guard_result.reason}"
        )

    try:
        response = await chat(id, body.content)
        return MessageResponse(
            agent=response.agent,
            content=response.content,
            citations=response.citations
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/conversations/{id}/history", response_model=List[Message])
async def get_history(id: str):
    state = get_conversation(id)
    if state is None:
        raise HTTPException(status_code=404, detail=f"Conversation {id} not found")
    return state.messages
