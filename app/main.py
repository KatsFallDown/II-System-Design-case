from pathlib import Path

from fastapi import FastAPI, HTTPException

from app.config import Settings
from app.presentation import api_payload
from app.runtime import get_pipeline
from app.schemas import TicketInput


app = FastAPI(title="Support Ticket Automation PoC", version="0.2.0")


@app.get("/health")
def health() -> dict:
    settings = Settings()
    artifacts = {
        "category": (settings.artifacts_dir / "category.joblib").exists(),
        "risk": (settings.artifacts_dir / "risk.joblib").exists(),
    }
    return {
        "status": "ok" if settings.dataset_path.exists() and all(artifacts.values()) else "degraded",
        "llm_mode": "mock",
        "dataset_available": settings.dataset_path.exists(),
        "models": artifacts,
    }


@app.post("/tickets/process")
def process_ticket(ticket: TicketInput) -> dict:
    try:
        return api_payload(get_pipeline().process(ticket))
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
