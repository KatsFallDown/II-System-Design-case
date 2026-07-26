from app.config import AUTO_REPLY_ALLOWLIST
from app.schemas import Action


def decide(category, risk, examples, llm, settings):
    if risk.label == "high":
        if not llm.information_sufficient and llm.missing_information:
            return Action.ASK_CLARIFICATION, "high_risk_missing_information"
        return Action.ESCALATE, "high_risk_requires_operator"
    top_similarity = examples[0].similarity if examples else 0.0
    auto_allowed = (
        category.confidence >= settings.category_confidence_threshold
        and risk.confidence >= settings.risk_confidence_threshold
        and top_similarity >= settings.retrieval_similarity_threshold
        and llm.information_sufficient
        and category.label in AUTO_REPLY_ALLOWLIST
    )
    if risk.label == "low" and auto_allowed:
        return Action.AUTO_REPLY, "all_low_risk_gates_passed"
    if risk.label == "medium":
        return Action.ESCALATE, "medium_risk_not_allowlisted"
    if llm.missing_information:
        return Action.ASK_CLARIFICATION, "specific_information_missing"
    return Action.ESCALATE, "automation_gates_not_satisfied"
