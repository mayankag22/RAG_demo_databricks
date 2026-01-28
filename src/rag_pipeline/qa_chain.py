from typing import Dict, Any, List

from openai import OpenAI

from .retriever import HybridRetriever
from .reranker import LocalCrossEncoderReranker
from .mcp_client import MCPClient


client = OpenAI()


class BankingPolicyQA:
    def __init__(self, faiss_dir: str = "data/faiss_index"):
        self.retriever = HybridRetriever(faiss_dir)
        self.reranker = LocalCrossEncoderReranker()
        self.mcp = MCPClient()

    def answer(self, question: str) -> Dict[str, Any]:
        # 1. MCP search over curated policy store
        mcp_results = self.mcp.search_policy(question, top_k=3)

        # 2. Hybrid retrieval over full corpus
        retrieved = self.retriever.retrieve(question, k=8)

        # 3. Local cross-encoder reranking
        reranked_docs = self.reranker.rerank(question, retrieved)
        top_docs = reranked_docs[:4]

        # 4. Build context with simple citations
        context_blocks = []
        citations = []
        for i, d in enumerate(top_docs, start=1):
            src = d.metadata.get("source", "unknown")
            page = d.metadata.get("page", "N/A")
            citation = f"[{i}] {src}, page {page}"
            citations.append(citation)
            context_blocks.append(f"{citation}\n{d.page_content}")

        full_context = "\n\n---\n\n".join(context_blocks)

        prompt = f"""
You are a banking policy assistant. Answer the user's question
STRICTLY based on the context below. Always include citations like [1], [2]
in your answer.

Question: {question}

Context:
{full_context}

Answer:
"""

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        answer_text = resp.choices[0].message.content

        compliance = self.mcp.check_compliance(
            question=question,
            answer=answer_text,
            referenced_sections=mcp_results,
        )

        return {
            "answer": answer_text,
            "citations": citations,
            "mcp_sections": mcp_results,
            "compliance": compliance,
        }