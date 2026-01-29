## 🧱 Architecture

The system runs as two coordinated Docker containers — one for the MCP server and one for the Streamlit UI — both sharing the same ingestion, retrieval, and RAG pipeline.

### 🔧 High‑Level Architecture Diagram

```mermaid
graph TB
    %% Styling
    classDef ingestStyle fill:#e1f5ff,stroke:#01579b,stroke-width:2px,color:#000
    classDef processStyle fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    classDef ragStyle fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
    classDef dockerStyle fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#000
    classDef monitorStyle fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#000
    
    %% Data Sources
    subgraph SOURCES["📥 Data Sources"]
        direction TB
        TXT["📄 Text Files"]
        PDF["📑 PDF Documents"]
        DB["🟦 Databricks Table"]
    end
    
    %% Document Processing Pipeline
    subgraph PROCESS["⚙️ Document Processing Pipeline"]
        direction TB
        CHUNK["🔪 Text Chunker<br/><i>Semantic Segmentation</i>"]
        EMBED["🧠 Embedding Model<br/><i>text-embedding-3-small</i>"]
        
        subgraph INDEXES["Index Storage"]
            direction LR
            FAISS["📊 FAISS Index<br/><i>Vector Search</i>"]
            BM25["📈 BM25 Index<br/><i>Keyword Search</i>"]
        end
    end
    
    %% Docker Environment
    subgraph DOCKER["🐳 Docker Compose Environment"]
        direction TB
        
        subgraph MCP["MCP Server Container"]
            direction TB
            MCP_TOOLS["🔧 MCP Tools"]
            TOOL1["search_policy"]
            TOOL2["get_section"]
            TOOL3["check_compliance"]
            
            MCP_TOOLS --- TOOL1
            MCP_TOOLS --- TOOL2
            MCP_TOOLS --- TOOL3
        end
        
        subgraph STREAMLIT["Streamlit UI Container"]
            direction TB
            UI["💬 Streamlit Interface<br/><i>User Interaction</i>"]
        end
    end
    
    %% RAG Pipeline
    subgraph RAG["🤖 RAG Pipeline"]
        direction TB
        RETRIEVER["🔍 Hybrid Retriever<br/><i>FAISS + BM25 Fusion</i>"]
        RERANK["⚡ Cross-Encoder Reranker<br/><i>ms-marco-MiniLM-L-6-v2</i>"]
        LLM["🎯 LLM Generator<br/><i>GPT-4o-mini</i>"]
    end
    
    %% Monitoring & Observability
    subgraph MONITOR["📊 Monitoring & Evaluation"]
        direction LR
        LATENCY["⏱️ Latency Tracking"]
        METRICS["📈 Retrieval Metrics<br/><i>Precision@k, MRR</i>"]
        AUDIT["📝 Audit Logs"]
    end
    
    %% Data Flow Connections
    TXT -->|Ingest| CHUNK
    PDF -->|Ingest| CHUNK
    DB -->|Ingest| CHUNK
    
    CHUNK -->|Split Text| EMBED
    EMBED -->|Generate Vectors| FAISS
    EMBED -->|Generate Tokens| BM25
    
    UI -->|User Query| RETRIEVER
    
    FAISS -->|Vector Results| RETRIEVER
    BM25 -->|Keyword Results| RETRIEVER
    
    RETRIEVER -->|Top-8 Candidates| RERANK
    RERANK -->|Ranked Documents| LLM
    LLM -->|Generated Answer| UI
    
    UI <-->|Tool Invocation| MCP_TOOLS
    MCP_TOOLS -->|Policy Sections| UI
    
    UI -.->|Log Events| MONITOR
    MCP -.->|Log Events| MONITOR
    RAG -.->|Performance Metrics| MONITOR
    
    %% Apply Styles
    class TXT,PDF,DB ingestStyle
    class CHUNK,EMBED,FAISS,BM25 processStyle
    class RETRIEVER,RERANK,LLM ragStyle
    class MCP,STREAMLIT,MCP_TOOLS,TOOL1,TOOL2,TOOL3,UI dockerStyle
    class LATENCY,METRICS,AUDIT monitorStyle
