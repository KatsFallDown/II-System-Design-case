import os

import httpx

from app.llm.factory import llm_mode


def get_llm_health() -> dict:
    mode = llm_mode()
    if mode == "mock":
        return {"mode": mode, "available": True}
    base_url = os.getenv("LLAMA_BASE_URL", "http://llama-cpu:8080").rstrip("/")
    try:
        response = httpx.get(f"{base_url}/health", timeout=2.0)
        return {"mode": mode, "available": response.status_code == 200}
    except httpx.HTTPError:
        return {"mode": mode, "available": False}
