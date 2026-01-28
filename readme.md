# Banking Policy Q&A

🏦 Overview
This project is an intelligent Banking Policy Q&A system that uses:

RAG (Retrieval‑Augmented Generation)

MCP (Model Context Protocol) server

Hybrid retrieval (FAISS + BM25)

Local cross‑encoder reranking

Streamlit UI

Databricks ingestion support

The system answers questions about banking policies, regulations, and procedures using structured and unstructured data sources.

It is designed to run entirely on a personal laptop, with optional low‑cost LLM calls.

## Architecture

```mermaid
flowchart LR

    %% UI
    A[Streamlit UI<br/>User Questions] --> B[RAG Pipeline]

    %% Ingestion Paths
    subgraph INGEST[Ingestion Layer]
        I1[📄 Text Files<br/>Local .txt Policies]
        I2[📑 PDF Uploads<br/>User Provided]
        I3[🟦 Databricks Table<br/>banking_policies]
    end

    I1 --> D1
    I2 --> D1
    I3 --> D1

    %% Chunking + Embedding
    subgraph D1[Document Processing]
        C1[Chunker<br/>Citation‑Aware]
        C2[Embeddings<br/>text-embedding-3-small]
        C3[FAISS Index<br/>Vector Store]
        C4[BM25 Index<br/>Keyword Store]
    end

    %% RAG Pipeline
    subgraph RAG[RAG Pipeline]
        B1[Hybrid Retriever<br/>FAISS + BM25]
        B2[Local Cross‑Encoder Reranker]
        B3[LLM Answer Generator<br/>GPT‑4o‑mini]
    end

    B --> B1 --> B2 --> B3 --> A

    %% MCP Server
    subgraph MCP[MCP Server (FastAPI)]
        M1[/search_policy/]
        M2[/get_section/]
        M3[/check_compliance/]
    end

    B -->|Tool Calls| MCP
    MCP -->|Policy Sections| B

    %% Monitoring
    subgraph MON[Monitoring]
        L1[Latency Tracking]
        L2[Audit Logs]
    end

    A --> MON
    MCP --> MON

