"""
Integration test — Scenario 2: Cross-agent handover (Technical → Billing).

Flow: Triage → technical (SSO), then handover_required=True → billing (upgrade)
LLM and retriever are mocked. Validates HandoverManager writes audit log.
"""
import json
# pyrefly: ignore [missing-import]
import os
# pyrefly: ignore [missing-import]
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient
from main import app
from models.agent_response import AgentResponse
from models.message import Citation

client = TestClient(app)

_TRIAGE_RESPONSE = json.dumps({
    "intent": "technical_issue",
    "routing_decision": "technical",
    "entities": {"plan_change": "pro_to_enterprise"},
    "urgency": "medium",
})

# Technical agent asks for handover to billing after handling SSO
_TECHNICAL_RESPONSE = "I've addressed your SSO issue. Transferring you to billing for the Enterprise upgrade."

_BILLING_RESPONSE = "I can see you'd like to upgrade from Pro to Enterprise. Here are the details..."


def test_scenario2_cross_agent_handover():
    resp = client.post("/api/v1/conversations", json={"customer_id": "cust-s2"})
    assert resp.status_code == 200
    conv_id = resp.json()["conversation_id"]

    mock_citation = Citation(
        kb_id="KB-012",
        title="SSO SAML Configuration",
        snippet="Configure SSO via Settings → Auth → SAML...",
        score=0.88
    )

    # Technical agent response that triggers handover
    tech_agent_response = AgentResponse(
        agent="technical",
        content=_TECHNICAL_RESPONSE,
        citations=[mock_citation],
        handover_required=True,
        handover_target="billing",
        escalate=False,
        routing_decision=None
    )

    billing_agent_response = AgentResponse(
        agent="billing",
        content=_BILLING_RESPONSE,
        citations=[],
        handover_required=False,
        escalate=False,
        routing_decision=None
    )

    with (
        patch("agents.triage_agent.TriageAgent._call_llm",
              new=AsyncMock(return_value=_TRIAGE_RESPONSE)),
        patch("agents.technical_agent.TechnicalAgent.handle",
              new=AsyncMock(return_value=tech_agent_response)),
        patch("agents.billing_agent.BillingAgent.handle",
              new=AsyncMock(return_value=billing_agent_response)),
    ):
        resp = client.post(
            f"/api/v1/conversations/{conv_id}/messages",
            json={"content": "I want to upgrade from Pro to Enterprise, but first check my SSO issue."}
        )

    assert resp.status_code == 200
    data = resp.json()
    # Final response should contain aggregated content from both agents
    assert data["agent"] == "billing"
    content = data["content"].lower()
    assert "sso" in content
    assert "address" in content or "transfer" in content
    assert "upgrade" in content or "enterprise" in content

    # Verify handover audit log was written
    assert os.path.exists("handover/audit.jsonl"), "Handover audit log should exist"
    with open("handover/audit.jsonl") as f:
        lines = [l for l in f.readlines() if l.strip()]
    assert len(lines) >= 1
    last_entry = json.loads(lines[-1])
    assert last_entry["source_agent"] == "technical"
    assert last_entry["target_agent"] == "billing"
