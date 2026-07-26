import json

import httpx
import pytest
from pydantic import ValidationError

from app.llm.llama_cpp import LlamaCppAdapter
from app.schemas import Prediction, RetrievedExample, TicketInput


def inputs():
    return (
        TicketInput(ticket_id="llama-test", subject="Reset", message="Reset link missing"),
        Prediction(label="Technical Support", confidence=0.8),
        Prediction(label="low", confidence=0.7),
        [],
    )


def test_llama_adapter_validates_structured_json(monkeypatch):
    content = {
        "information_sufficient": False,
        "recommended_action": "ASK_CLARIFICATION",
        "user_message": "Which email address is associated with the account?",
        "operator_summary": "Reset link is missing.",
        "missing_information": ["account email"],
        "reason": "Account identifier is missing.",
    }

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": json.dumps(content)}}]}

    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: Response())
    analysis = LlamaCppAdapter("http://llama:8080").analyze(*inputs())
    assert analysis.recommended_action == "ASK_CLARIFICATION"


def test_llama_adapter_rejects_invalid_json(monkeypatch):
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": "not-json"}}]}

    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: Response())
    with pytest.raises(ValidationError):
        LlamaCppAdapter("http://llama:8080").analyze(*inputs())
