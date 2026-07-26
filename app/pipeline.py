import re
from app.policy import decide
from app.schemas import Action, LLMAnalysis, Prediction, ProcessResult, RiskLevel, SupportTicket


SENSITIVE_PATTERNS = (
    "fraud", "stolen account", "unauthorized payment", "unauthorised payment",
    "personal data leak", "security breach", "legal threat", "mass outage",
    "service unavailable for everyone",
)


class TicketPipeline:
    def __init__(self, settings, category_classifier, risk_classifier, retriever, llm):
        self.settings = settings
        self.category_classifier = category_classifier
        self.risk_classifier = risk_classifier
        self.retriever = retriever
        self.llm = llm

    def process(self, ticket):
        text = re.sub(r"\s+", " ", f"{ticket.subject} {ticket.message}").strip()
        trace = ["Input validated and text normalized"]
        category = self.category_classifier.predict(text)
        trace.append(f"Category={category.label}, confidence={category.confidence:.3f}")
        risk = self.risk_classifier.predict(text)
        rule = next((pattern for pattern in SENSITIVE_PATTERNS if pattern in text.lower()), None)
        if rule and risk.label != "high":
            risk = Prediction(label="high", confidence=max(risk.confidence, 0.99))
        trace.append(f"Risk={risk.label}, confidence={risk.confidence:.3f}, override={rule or 'none'}")
        examples = self.retriever.search(
            text, self.settings.retrieval_candidates, self.settings.retrieval_context_limit,
            self.settings.retrieval_similarity_threshold,
        )
        trace.append("Retrieval scores=" + str([round(item.similarity, 3) for item in examples]))
        fallback_reason = None
        try:
            analysis = self.llm.analyze(ticket, category, risk, examples)
            trace.append(f"LLM recommendation={analysis.recommended_action}")
            action, reason = decide(category, risk, examples, analysis, self.settings)
        except Exception as exc:
            action, reason = Action.ESCALATE, "llm_failure"
            fallback_reason = f"{type(exc).__name__}: {exc}"
            analysis = LLMAnalysis(
                information_sufficient=False, recommended_action=Action.ESCALATE,
                user_message="We are forwarding this request to a support specialist.",
                operator_summary="LLM analysis failed; safe fallback applied.",
                missing_information=[], reason="LLM failure.",
            )
        trace.append(f"Decision={action}, reason={reason}")
        if action == Action.ESCALATE and analysis.recommended_action != Action.ESCALATE:
            analysis.user_message = "We are forwarding this request to a support specialist."
        support_ticket = None
        if action == Action.ESCALATE:
            support_ticket = SupportTicket(
                subject=ticket.subject, original_message=ticket.message, history=ticket.history,
                predicted_category=category.label, risk=RiskLevel(risk.label),
                category_confidence=category.confidence, risk_confidence=risk.confidence,
                summary=analysis.operator_summary, missing_information=analysis.missing_information,
                similar_case_ids=[item.id for item in examples],
            )
        return ProcessResult(
            ticket_id=ticket.ticket_id, category=category.label,
            category_confidence=category.confidence, risk=RiskLevel(risk.label),
            risk_confidence=risk.confidence, action=action, user_message=analysis.user_message,
            support_ticket=support_ticket, retrieved_examples=examples, trace=trace,
            fallback_reason=fallback_reason,
        )
