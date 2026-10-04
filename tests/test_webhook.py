import pytest
from fastapi.testclient import TestClient
from app.main import app 

client = TestClient(app)

def test_webhook_deterministic_rule_hit():
    """Verifies that an incoming scam message returns a RED alert warning banner."""
    mock_payload = {
        "message": {
            "text": "Join our VIP investment group today! Guaranteed 30% profits.",
            "chat": {"id": 987654321}
        }
    }
    response = client.post("/v1/webhooks/message-channel", json=mock_payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "processed"
    assert "🚨 *सचेत WARNING!*" in json_data["reply"]

def test_webhook_clear_message_fallback():
    """Verifies that normal message strings clear our layer 1 rule parameters safely."""
    mock_payload = {
        "message": {
            "text": "Hello, is this service operational?",
            "chat": {"id": 11223344}
        }
    }
    response = client.post("/v1/webhooks/message-channel", json=mock_payload)
    assert response.status_code == 200
    assert "No immediate deterministic red flags" in response.json()["reply"]

def test_webhook_empty_payload_rejection():
    """Verifies that an empty input packet immediately drops with an HTTP 400 error."""
    invalid_payload = {
        "message": {
            "text": "",
            "chat": {"id": 55555}
        }
    }
    response = client.post("/v1/webhooks/message-channel", json=invalid_payload)
    assert response.status_code == 400
