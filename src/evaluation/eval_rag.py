from typing import List, Dict, Any

from src.rag_pipeline.retriever import HybridRetriever


def compute_retrieval_metrics(
    retriever: HybridRetriever,
    eval_data: List[Dict[str, Any]],
    k: int = 5,
) -> Dict[str, float]:
    """
    eval_data: list of {question, relevant_sources: [(source, page), ...]}
    """
    p_at_k = []
    mrr = []

    for row in eval_data:
        q = row["question"]
        relevant = set(tuple(x) for x in row["relevant_sources"])
        results = retriever.retrieve(q, k=k)
        doc_ids = [
            (d.metadata.get("source"), d.metadata.get("page")) for d, _ in results
        ]

        hits = sum(1 for did in doc_ids if did in relevant)
        p_at_k.append(hits / k)

        rank = None
        for i, did in enumerate(doc_ids, start=1):
            if did in relevant:
                rank = i
                break
        mrr.append(1 / rank if rank is not None else 0.0)

    return {
        "precision_at_k": sum(p_at_k) / len(p_at_k) if p_at_k else 0.0,
        "mrr": sum(mrr) / len(mrr) if mrr else 0.0,
    }
