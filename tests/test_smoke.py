from fastapi.testclient import TestClient

import app.main as api_module
from app.main import app


def test_health_and_process_api(monkeypatch, happy_pipeline):
    monkeypatch.setattr(api_module, "get_pipeline", lambda: happy_pipeline)
    client = TestClient(app)

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["llm_mode"] == "mock"

    response = client.post(
        "/tickets/process",
        json={
            "ticket_id": "api-smoke",
            "subject": "Password reset email",
            "message": (
                "The reset email has not arrived after three attempts. "
                "My account email is correct."
            ),
            "history": [],
        },
    )
    body = response.json()
    assert response.status_code == 200
    assert body["action"] == "AUTO_REPLY"
    assert len(body["trace"]) == 6
    assert body["trace"][0]["step"] == "input_validation"
