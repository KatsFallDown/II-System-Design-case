from app.schemas import Action, TicketInput

from conftest import make_pipeline


def test_unauthorized_payment_can_never_auto_reply():
    pipeline = make_pipeline(category="Billing and Payments", risk="low")
    result = pipeline.process(
        TicketInput(
            ticket_id="risky-test",
            subject="Unauthorized payment from stolen account",
            message=(
                "I did not approve this payment. Please secure the account "
                "and investigate the transaction."
            ),
        )
    )

    assert result.action == Action.ESCALATE
    assert result.risk == "high"
    assert result.support_ticket is not None
    assert "operator" in result.trace[-1].lower()
