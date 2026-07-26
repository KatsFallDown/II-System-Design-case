import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    dataset_path: Path = Path(os.getenv("DATASET_PATH", "dataset-tickets-multi-lang-4-20k.csv"))
    artifacts_dir: Path = Path(os.getenv("ARTIFACTS_DIR", "artifacts"))
    category_confidence_threshold: float = float(os.getenv("CATEGORY_CONFIDENCE_THRESHOLD", "0.65"))
    risk_confidence_threshold: float = float(os.getenv("RISK_CONFIDENCE_THRESHOLD", "0.60"))
    retrieval_similarity_threshold: float = float(os.getenv("RETRIEVAL_SIMILARITY_THRESHOLD", "0.25"))
    retrieval_candidates: int = 20
    retrieval_context_limit: int = 5


AUTO_REPLY_ALLOWLIST = {"Technical Support", "Product Support", "Customer Service", "General Inquiry"}
