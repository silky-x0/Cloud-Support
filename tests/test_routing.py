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
