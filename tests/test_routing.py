# pyrefly: ignore [missing-import]
import pytest
# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_chat_stub_returns_mock_response():

    test_message = "Hello, CloudDash!"
    response = client.post(
        "/api/v1/chat",
        json={"message": test_message}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert test_message in data["reply"]
    assert "STUB:" in data["reply"]
    
    assert "trace_id" in data
    assert len(data["trace_id"]) > 0
    
    try:
        import uuid
        uuid.UUID(data["trace_id"])
    except ValueError:
        pytest.fail("trace_id is not a valid UUID")

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_full_conversation_lifecycle():
    # 1. Create a conversation
    response = client.post(
        "/api/v1/conversations",
        json={"customer_id": "cust-test-123"}
    )
    assert response.status_code == 200
    conv_data = response.json()
    assert "conversation_id" in conv_data
    assert "trace_id" in conv_data
    conv_id = conv_data["conversation_id"]

    # 2. Send a message
    response = client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        json={"content": "My alerts stopped firing after I updated AWS integration credentials yesterday."}
    )
    assert response.status_code == 200
    msg_data = response.json()
    assert "agent" in msg_data
    assert "content" in msg_data
    assert "citations" in msg_data

    # 3. Get history
    response = client.get(f"/api/v1/conversations/{conv_id}/history")
    assert response.status_code == 200
    history = response.json()
    assert len(history) == 2  # one user message, one assistant message
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"
    assert history[1]["agent"] == msg_data["agent"]
