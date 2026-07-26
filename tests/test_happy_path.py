from app.schemas import Action, TicketInput


def test_safe_detailed_ticket_is_auto_replied(happy_pipeline):
    result = happy_pipeline.process(
        TicketInput(
            ticket_id="happy-test",
            subject="Password reset email",
            message=(
                "The reset email has not arrived after three attempts. "
                "I verified that my account email is correct."
            ),
        )
    )

    assert result.action == Action.AUTO_REPLY
    assert result.risk == "low"
    assert result.support_ticket is None
    assert len(result.trace) == 6
