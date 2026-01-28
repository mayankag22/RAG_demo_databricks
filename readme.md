## 🧱 Architecture

The system runs as two coordinated Docker containers — one for the MCP server and one for the Streamlit UI — both sharing the same ingestion, retrieval, and RAG pipeline.

### 🔧 High‑Level Architecture Diagram

```mermaid
flowchart LR

    %% Docker Layer
    subgraph DOCKER[Docker Compose Environment]
        direction LR

        %% MCP Container
        subgraph MCP_CONTAINER[MCP Server Container]
            M1[/search_policy/]
            M2[/get_section/]
            M3[/check_compliance/]
        end

        %% Streamlit Container
        subgraph UI_CONTAINER[Streamlit UI Container]
            UI[Streamlit UI<br/>User Questions]
        end
    end

    %% Ingestion Layer
    subgraph INGEST[Ingestion Layer]
        I1[📄 Text Files]
        I2[📑 PDF Uploads]
        I3[🟦 Databricks Table]
    end

    %% Document Processing
    subgraph PROCESSING[Document Processing]
        C1[Chunker]
        C2[Embeddings<br/>text-embedding-3-small]
        C3[FAISS Index]
        C4[BM25 Index]
    end

    %% RAG Pipeline
    subgraph RAG[RAG Pipeline]
        R1[Hybrid Retriever<br/>FAISS + BM25]
        R2[Cross-Encoder Reranker]
        R3[LLM Answer Generator<br/>GPT-4o-mini]
    end

    %% Monitoring
    subgraph MONITORING[Monitoring & Evaluation]
        L1[Latency Tracking]
        L2[Retrieval Metrics<br/>Precision@k, MRR]
        L3[Audit Logs]
    end

    %% Connections
    UI --> R1
    R1 --> R2 --> R3 --> UI

    UI -->|Tool Calls| MCP_CONTAINER
    MCP_CONTAINER -->|Policy Sections| UI

    I1 --> PROCESSING
    I2 --> PROCESSING
    I3 --> PROCESSING

    PROCESSING --> R1

    UI --> MONITORING
    MCP_CONTAINER --> MONITORING