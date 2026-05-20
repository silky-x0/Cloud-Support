"""
Integration test — Scenario 1: Single-agent technical resolution.

Flow: POST /conversations → POST /conversations/{id}/messages
      Triage → technical → TechnicalAgent returns KB-cited answer
LLM calls are mocked so no API cost. Retriever is also mocked.
"""
import json
# pyrefly: ignore [missing-import]
import pytest
from unittest.mock import AsyncMock, patch

# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient
from main import app
from models.message import Citation

client = TestClient(app)

_TRIAGE_RESPONSE = json.dumps({
    "intent": "technical_issue",
    "routing_decision": "technical",
    "entities": {"product": "aws_integration"},
    "urgency": "medium",
})

_TECHNICAL_RESPONSE = (
    "Based on KB article [KB-007], AWS integration credentials must be re-authorized "
    "in Settings → Integrations → AWS after a credential rotation. "
    "Step 1: Go to your CloudDash dashboard..."
)

_CITATION = Citation(
    kb_id="KB-007",
    title="AWS Integration Troubleshooting",
    snippet="Re-authorize credentials after rotation...",
    score=0.91,
)


def test_scenario1_technical_resolution():
    # 1. Create conversation
    resp = client.post("/api/v1/conversations", json={"customer_id": "cust-s1"})
    assert resp.status_code == 200
    conv_id = resp.json()["conversation_id"]

    with (
        patch("agents.triage_agent.TriageAgent._call_llm",
              new=AsyncMock(return_value=_TRIAGE_RESPONSE)),
        patch("agents.technical_agent.TechnicalAgent._call_llm",
              new=AsyncMock(return_value=_TECHNICAL_RESPONSE)),
        # Patch at class level so every instance gets the mock
        patch("retrieval.retriever.Retriever.retrieve",
              return_value=("[KB-007] Re-authorize credentials...", [_CITATION])),
    ):
        resp = client.post(
            f"/api/v1/conversations/{conv_id}/messages",
            json={"content": "My CloudDash alerts stopped firing after I updated my AWS integration credentials yesterday."}
        )

    # 2. Assertions on the response
    assert resp.status_code == 200
    data = resp.json()
    assert data["agent"] == "technical"
    assert "KB-007" in data["content"] or len(data["citations"]) > 0

    # 3. Verify history has 2 turns
    hist = client.get(f"/api/v1/conversations/{conv_id}/history")
    assert hist.status_code == 200
    messages = hist.json()
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["agent"] == "technical"
