from app.schemas import ProcessResult


TRACE_STEPS = (
    "input_validation",
    "category_classification",
    "risk_classification",
    "similar_ticket_retrieval",
    "llm_analysis",
    "decision_policy",
)


def structured_trace(result: ProcessResult) -> list[dict]:
    entries = []
    for index, raw in enumerate(result.trace):
        entries.append(
            {
                "step": TRACE_STEPS[index] if index < len(TRACE_STEPS) else "pipeline",
                "status": "fallback" if result.fallback_reason and index >= 4 else "ok",
                "details": {"summary": raw},
            }
        )
    return entries


def api_payload(result: ProcessResult) -> dict:
    payload = result.model_dump(mode="json")
    payload["trace"] = structured_trace(result)
    return payload
