import json
from pathlib import Path
import pandas as pd
from app.ml.classifiers import train_classifier


REQUIRED_COLUMNS = {"subject", "body", "answer", "queue", "priority", "language"}


def load_english_data(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}. Set DATASET_PATH.")
    frame = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Dataset is missing columns: {sorted(missing)}")
    frame = frame.loc[frame["language"].eq("en")].copy()
    for column in ("subject", "body", "answer"):
        frame[column] = frame[column].fillna("")
    return frame


def load_or_train(settings):
    frame = load_english_data(settings.dataset_path)
    category, category_metrics = train_classifier(frame, "queue", settings.artifacts_dir / "category.joblib")
    risk, risk_metrics = train_classifier(frame, "priority", settings.artifacts_dir / "risk.joblib")
    metrics = {"category": category_metrics, "risk": risk_metrics}
    settings.artifacts_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = settings.artifacts_dir / "metrics.json"
    if not metrics_path.exists() or not category_metrics["reused"]:
        metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return frame, category, risk, metrics
