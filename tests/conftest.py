import pytest

from app.config import Settings
from app.llm.mock import MockLLMAdapter
from app.pipeline import TicketPipeline
from app.schemas import Prediction, RetrievedExample


class StubClassifier:
    def __init__(self, label: str, confidence: float):
        self.prediction = Prediction(label=label, confidence=confidence)

    def predict(self, _text: str) -> Prediction:
        return self.prediction


class StubRetriever:
    def search(self, _text: str, _candidates: int, _limit: int, _threshold: float):
        return [
            RetrievedExample(
                id=42,
                subject="Historical password reset",
                body="The reset message did not arrive after multiple attempts.",
                answer="Verify the account email and retry the reset flow.",
                queue="Technical Support",
                priority="low",
                similarity=0.9,
            )
        ]


def make_pipeline(category="Technical Support", risk="low", llm=None):
    return TicketPipeline(
        Settings(),
        StubClassifier(category, 0.9),
        StubClassifier(risk, 0.9),
        StubRetriever(),
        llm or MockLLMAdapter(),
    )


@pytest.fixture
def happy_pipeline():
    return make_pipeline()
