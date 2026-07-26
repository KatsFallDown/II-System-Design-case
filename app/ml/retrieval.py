import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.ml.classifiers import full_text
from app.schemas import RetrievedExample


class TicketRetriever:
    def __init__(self, frame: pd.DataFrame):
        self.frame = frame.reset_index(drop=False).rename(columns={"index": "source_id"})
        self.vectorizer = TfidfVectorizer(max_features=30_000, ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform(full_text(self.frame))

    def search(self, text: str, candidates: int, limit: int, min_similarity: float):
        scores = cosine_similarity(self.vectorizer.transform([text]), self.matrix).ravel()
        results = []
        for position in scores.argsort()[::-1][:candidates]:
            score = min(1.0, max(0.0, float(scores[position])))
            if score < min_similarity or len(results) >= limit:
                continue
            row = self.frame.iloc[position]
            results.append(RetrievedExample(
                id=int(row["source_id"]), subject=str(row["subject"])[:200],
                body=str(row["body"])[:500], answer=str(row["answer"])[:1000],
                queue=str(row["queue"]), priority=str(row["priority"]), similarity=score,
            ))
        return results
