"""
Integration test — Scenario 3: Billing dispute → escalation to human.

Flow: Triage → billing → BillingAgent detects "refund"+"manager" → escalate=True
      → EscalationAgent produces human-handover package (priority P1)
LLM and retriever are mocked.
"""
import json
# pyrefly: ignore [missing-import]
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

_TRIAGE_RESPONSE = json.dumps({
    "intent": "billing_inquiry",
    "routing_decision": "billing",
    "entities": {"issue": "duplicate_charge", "urgency": "high"},
    "urgency": "high",
})

_BILLING_RESPONSE = (
    "I can see there may be a duplicate charge on your account. "
    "Given you're requesting a refund and to speak to a manager, I'm escalating this immediately."
)

_ESCALATION_RESPONSE = (
    "Your case has been escalated with priority P1. A support manager will contact you within 2 hours. "
    "Ticket ID: ESC-20260520-001. We apologise for the billing inconvenience."
)


def test_scenario3_escalation():
    resp = client.post("/api/v1/conversations", json={"customer_id": "cust-s3"})
    assert resp.status_code == 200
    conv_id = resp.json()["conversation_id"]

    # Billing agent returns escalate=True
    billing_agent_response = MagicMock()
    billing_agent_response.agent = "billing"
    billing_agent_response.content = _BILLING_RESPONSE
    billing_agent_response.citations = []
    billing_agent_response.handover_required = False
    billing_agent_response.handover_target = None
    billing_agent_response.escalate = True
    billing_agent_response.routing_decision = None

    # Escalation agent produces human-handover package
    escalation_agent_response = MagicMock()
    escalation_agent_response.agent = "escalation"
    escalation_agent_response.content = _ESCALATION_RESPONSE
    escalation_agent_response.citations = []
    escalation_agent_response.handover_required = False
    escalation_agent_response.escalate = False
    escalation_agent_response.routing_decision = None

    with (
        patch("agents.triage_agent.TriageAgent._call_llm",
              new=AsyncMock(return_value=_TRIAGE_RESPONSE)),
        patch("agents.billing_agent.BillingAgent.handle",
              new=AsyncMock(return_value=billing_agent_response)),
        patch("agents.escalation_agent.EscalationAgent.handle",
              new=AsyncMock(return_value=escalation_agent_response)),
    ):
        resp = client.post(
            f"/api/v1/conversations/{conv_id}/messages",
            json={"content": "I've been charged twice for April. I need an immediate refund and I want to speak to a manager."}
        )

    assert resp.status_code == 200
    data = resp.json()
    # Final response must come from escalation agent
    assert data["agent"] == "escalation"
    # Should mention escalation or manager
    assert any(kw in data["content"].lower() for kw in ["escalat", "manager", "priority", "ticket"])
