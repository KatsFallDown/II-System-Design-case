import json

import httpx

from app.llm.base import LLMAdapter
from app.schemas import LLMAnalysis


class LlamaCppAdapter(LLMAdapter):
    def __init__(
        self,
        base_url: str,
        model: str = "Qwen3.5-4B-Q8_0.gguf",
        timeout_seconds: float = 45.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def analyze(self, ticket, category, risk, examples) -> LLMAnalysis:
        context = {
            "ticket": ticket.model_dump(mode="json"),
            "category": category.model_dump(mode="json"),
            "risk": risk.model_dump(mode="json"),
            "historical_examples": [
                example.model_dump(mode="json") for example in examples
            ],
        }
        response = httpx.post(
            f"{self.base_url}/v1/chat/completions",
            timeout=self.timeout_seconds,
            json={
                "model": self.model,
                "temperature": 0,
                "max_tokens": 500,
                "reasoning_effort": "none",
                "chat_template_kwargs": {"enable_thinking": False},
                "response_format": {"type": "json_object"},
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Analyze the support ticket using only supplied facts. "
                            "Never invent policies, account facts, or troubleshooting outcomes. "
                            "Do not choose final safety policy; only recommend. Return JSON with "
                            "exactly: information_sufficient (boolean), recommended_action "
                            "(AUTO_REPLY|ASK_CLARIFICATION|ESCALATE), user_message (string), "
                            "operator_summary (string), missing_information (string array), "
                            "reason (short string). Do not include hidden reasoning or markdown."
                        ),
                    },
                    {"role": "user", "content": json.dumps(context, ensure_ascii=False)},
                ],
            },
        )
        response.raise_for_status()
        payload = response.json()
        content = payload["choices"][0]["message"]["content"]
        return LLMAnalysis.model_validate_json(content)
