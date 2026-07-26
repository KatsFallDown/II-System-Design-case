from app.llm.base import LLMAdapter
from app.schemas import Action, LLMAnalysis


class MockLLMAdapter(LLMAdapter):
    def analyze(self, ticket, category, risk, examples):
        text = f"{ticket.subject} {ticket.message}".lower()
        if risk.label == "high":
            return LLMAnalysis(
                information_sufficient=True, recommended_action=Action.ESCALATE,
                user_message="This needs specialist review. We escalated it; please secure the affected account or payment method.",
                operator_summary=f"High-risk report: {ticket.subject}.",
                missing_information=[], reason="High-risk prediction requires human review.",
            )
        incomplete = len(ticket.message.split()) < 5 or (
            any(value in text for value in ("help me", "not working", "problem"))
            and len(ticket.message.split()) < 12
        )
        if incomplete:
            return LLMAnalysis(
                information_sufficient=False, recommended_action=Action.ASK_CLARIFICATION,
                user_message="Please provide the exact error and troubleshooting steps already tried.",
                operator_summary="User request lacks diagnostic details.",
                missing_information=["exact error", "steps already tried"],
                reason="Specific diagnostic information is missing.",
            )
        if examples:
            return LLMAnalysis(
                information_sufficient=True, recommended_action=Action.AUTO_REPLY,
                user_message="Thank you for the details. Verify the relevant settings and retry the documented troubleshooting steps. Reply with the exact error if it continues.",
                operator_summary="Safe request with a similar historical resolution.",
                missing_information=[], reason="Detailed request with similar cases.",
            )
        return LLMAnalysis(
            information_sufficient=False, recommended_action=Action.ESCALATE,
            user_message="We are forwarding this request to a support specialist.",
            operator_summary="No sufficiently similar historical case was found.",
            missing_information=[], reason="Insufficient grounded context.",
        )
