from pathlib import Path
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from app.schemas import Prediction


def full_text(frame: pd.DataFrame) -> pd.Series:
    subject = frame["subject"].fillna("").astype(str).str.strip()
    body = frame["body"].fillna("").astype(str).str.strip()
    return (subject + " " + body).str.strip()


class TextClassifier:
    def __init__(self, model: Pipeline):
        self.model = model

    @classmethod
    def load(cls, path: Path):
        return cls(joblib.load(path))

    def predict(self, text: str) -> Prediction:
        probabilities = self.model.predict_proba([text])[0]
        position = int(probabilities.argmax())
        return Prediction(label=str(self.model.classes_[position]), confidence=float(probabilities[position]))


def train_classifier(frame: pd.DataFrame, target: str, path: Path):
    if path.exists():
        return TextClassifier.load(path), {"reused": True}
    texts = full_text(frame)
    valid = texts.ne("") & frame[target].notna()
    x_train, x_valid, y_train, y_valid = train_test_split(
        texts[valid], frame.loc[valid, target].astype(str), test_size=0.2,
        random_state=42, stratify=frame.loc[valid, target],
    )
    model = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=30_000, ngram_range=(1, 2))),
        ("classifier", LogisticRegression(max_iter=500, class_weight="balanced", random_state=42)),
    ])
    model.fit(x_train, y_train)
    predicted = model.predict(x_valid)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
    metrics = {
        "reused": False,
        "accuracy": float(accuracy_score(y_valid, predicted)),
        "macro_f1": float(f1_score(y_valid, predicted, average="macro")),
        "train_rows": len(x_train),
        "validation_rows": len(x_valid),
        "class_distribution": frame.loc[valid, target].value_counts().to_dict(),
    }
    return TextClassifier(model), metrics
