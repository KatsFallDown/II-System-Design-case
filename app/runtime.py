from functools import lru_cache

from app.config import Settings
from app.llm.factory import create_llm_adapter
from app.ml.retrieval import TicketRetriever
from app.ml.train import load_or_train
from app.pipeline import TicketPipeline


@lru_cache(maxsize=1)
def get_pipeline() -> TicketPipeline:
    settings = Settings()
    frame, category, risk, _ = load_or_train(settings)
    return TicketPipeline(
        settings,
        category,
        risk,
        TicketRetriever(frame),
        create_llm_adapter(),
    )
