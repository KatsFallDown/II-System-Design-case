from app.llm.base import LLMAdapter
from app.schemas import Action, TicketInput

from conftest import make_pipeline


class UnavailableLLM(LLMAdapter):
    def analyze(self, ticket, category, risk, examples):
        raise TimeoutError("simulated timeout")


def test_llm_failure_safely_escalates():
    result = make_pipeline(llm=UnavailableLLM()).process(
        TicketInput(
            ticket_id="fallback-test",
            subject="Password reset",
            message="The reset email is missing after several attempts.",
        )
    )

    assert result.action == Action.ESCALATE
    assert result.support_ticket is not None
    assert result.fallback_reason == "TimeoutError: simulated timeout"
    assert "llm_failure" in result.trace[-1]
