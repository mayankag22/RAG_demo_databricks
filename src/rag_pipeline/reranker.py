from typing import List, Tuple

from sentence_transformers import CrossEncoder
from langchain_core.documents import Document


class LocalCrossEncoderReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, docs: List[Tuple[Document, float]]) -> List[Document]:
        if not docs:
            return []

        pairs = [(query, d.page_content) for d, _ in docs]
        scores = self.model.predict(pairs)
        ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
        return [d for (d, _), _ in ranked]