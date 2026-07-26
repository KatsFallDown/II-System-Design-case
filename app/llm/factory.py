import os

from app.llm.llama_cpp import LlamaCppAdapter
from app.llm.mock import MockLLMAdapter


def llm_mode() -> str:
    mode = os.getenv("LLM_MODE", "mock").strip().lower()
    if mode not in {"mock", "llama_cpp"}:
        raise ValueError("LLM_MODE must be 'mock' or 'llama_cpp'")
    return mode


def create_llm_adapter():
    if llm_mode() == "mock":
        return MockLLMAdapter()
    return LlamaCppAdapter(
        base_url=os.getenv("LLAMA_BASE_URL", "http://llama-cpu:8080"),
        model=os.getenv("LLAMA_MODEL", "Qwen3.5-4B-Q8_0.gguf"),
        timeout_seconds=float(os.getenv("LLAMA_TIMEOUT_SECONDS", "45")),
    )
