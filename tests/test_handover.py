# pyrefly: ignore [missing-import]
import os
# pyrefly: ignore [missing-import]
import pytest
import tempfile
from datetime import datetime, timezone

from models.conversation import ConversationState
from models.handover import HandoverPayload
from handover.handover_manager import HandoverManager

def test_handover_execution():
    # 1. Setup temporary file for audit log
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as tmp:
        temp_log_path = tmp.name

    try:
        # 2. Setup state
        state = ConversationState(
            conversation_id="conv-123",
            trace_id="trace-abc",
            current_agent="triage",
            customer_id="cust-456",
            created_at=datetime.now(timezone.utc).isoformat()
        )

        # 3. Instantiate and run HandoverManager
        manager = HandoverManager(audit_log_path=temp_log_path)
        reason = "User requested manager escalation refund"
        payload = manager.execute(state, source="triage", target="escalation", reason=reason)

        # 4. Assertions on returned payload and state
        assert isinstance(payload, HandoverPayload)
        assert payload.source_agent == "triage"
        assert payload.target_agent == "escalation"
        assert payload.reason == reason
        assert payload.conversation_id == "conv-123"
        assert payload.trace_id == "trace-abc"
        assert payload.priority == "P1"  # Reason contains "refund", should escalate priority to P1

        # Check state changes
        assert state.current_agent == "escalation"
        assert len(state.handover_history) == 1
        assert state.handover_history[0]["source_agent"] == "triage"
        assert state.handover_history[0]["target_agent"] == "escalation"
        assert state.handover_history[0]["priority"] == "P1"

        # Check audit log file contents
        assert os.path.exists(temp_log_path)
        with open(temp_log_path, "r") as f:
            lines = f.readlines()
        assert len(lines) == 1
        import json
        logged_data = json.loads(lines[0])
        assert logged_data["source_agent"] == "triage"
        assert logged_data["target_agent"] == "escalation"
        assert logged_data["priority"] == "P1"

    finally:
        # Cleanup
        if os.path.exists(temp_log_path):
            os.remove(temp_log_path)

