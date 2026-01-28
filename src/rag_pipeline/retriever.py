from typing import List, Tuple

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from rank_bm25 import BM25Okapi
from langchain_core.documents import Document


class HybridRetriever:
    def __init__(self, faiss_dir: str = "data/faiss_index"):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vs = FAISS.load_local(
            faiss_dir,
            self.embeddings,
            allow_dangerous_deserialization=True,
        )

        self.docs: List[Document] = list(self.vs.docstore._dict.values())
        corpus = [d.page_content.split() for d in self.docs]
        self.bm25 = BM25Okapi(corpus)

    def retrieve(self, query: str, k: int = 8) -> List[Tuple[Document, float]]:
        vec_docs = self.vs.similarity_search_with_score(query, k=k)

        tokenized_query = query.split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        bm25_ranked = sorted(
            zip(self.docs, bm25_scores),
            key=lambda x: x[1],
            reverse=True,
        )[:k]

        combined = []
        for d, dist in vec_docs:
            combined.append((d, -float(dist)))  # invert distance to score
        combined.extend(bm25_ranked)

        seen = set()
        merged: List[Tuple[Document, float]] = []
        for d, s in sorted(combined, key=lambda x: x[1], reverse=True):
            key = (d.metadata.get("source"), d.metadata.get("page"))
            if key not in seen:
                seen.add(key)
                merged.append((d, s))
        return merged[:k]