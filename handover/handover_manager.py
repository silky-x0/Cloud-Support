import uuid
import json
import os
from datetime import datetime, timezone
from typing import Dict, Any
# pyrefly: ignore [missing-import]
from pydantic import BaseModel

from models.conversation import ConversationState
from models.handover import HandoverPayload

class HandoverManager:
    def __init__(self, audit_log_path: str = "handover/audit.jsonl"):
        self.audit_log_path = audit_log_path

    def execute(self, state: ConversationState, source: str, target: str, reason: str) -> HandoverPayload:
        """
        Executes a handover from source agent to target agent.
        Builds the HandoverPayload, logs it to audit.jsonl, and updates the conversation state.
        """
        full_history = []
        for msg in state.messages:
            full_history.append({
                "role": msg.role,
                "content": msg.content,
                "agent": msg.agent,
                "timestamp": msg.timestamp.isoformat() if hasattr(msg.timestamp, "isoformat") else str(msg.timestamp),
                "citations": [cit.model_dump() for cit in msg.citations]
            })

        # Determine priority based on reason/history keywords
        priority = "P2"
        content_lower = reason.lower()
        if "refund" in content_lower or "manager" in content_lower or "urgent" in content_lower or "dispute" in content_lower:
            priority = "P1"

        payload = HandoverPayload(
            handover_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            source_agent=source,
            target_agent=target,
            reason=reason,
            conversation_id=state.conversation_id,
            trace_id=state.trace_id,
            extracted_entities=state.extracted_entities,
            full_history=full_history,
            priority=priority
        )

        # Log audit entry
        self._audit_log(payload)

        # Update state
        state.current_agent = target
        state.handover_history.append(payload.model_dump(mode="json"))

        return payload

    def _audit_log(self, payload: HandoverPayload) -> None:
        os.makedirs(os.path.dirname(self.audit_log_path), exist_ok=True)
        with open(self.audit_log_path, "a") as f:
            f.write(payload.model_dump_json() + "\n")

