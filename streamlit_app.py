import streamlit as st
from src.rag_pipeline.qa_chain import BankingPolicyQA
from src.rag_pipeline.ingest import ingest_uploaded_pdfs, clear_faiss_index
from src.config import settings
# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="Banking Policy Q&A",
    page_icon="🏦",
    layout="wide",
)

# ---------------------------
# Custom CSS
# ---------------------------
st.markdown("""
<style>
.big-title {
    font-size: 36px !important;
    font-weight: 700 !important;
    color: #1a4f8b !important;
    margin-bottom: 0.2em;
}
.response-box {
    padding: 1.2em;
    background-color: #f7f9fc;
    border-radius: 10px;
    border: 1px solid #e3e6eb;
    margin-top: 1em;
}
.citation {
    font-size: 14px;
    color: #4a4a4a;
    margin-left: 0.5em;
}
.mcp-box {
    padding: 1em;
    background-color: #fffdf5;
    border-left: 4px solid #f4c542;
    border-radius: 6px;
    margin-bottom: 1em;
}
div.stButton > button:first-child {
    background-color: #d9534f;
    color: white;
    border-radius: 6px;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Sidebar
# ---------------------------
st.sidebar.title("⚙️ Controls")

if st.sidebar.button("🔄 Reset Page"):
    st.session_state.clear()
    st.rerun()

#st.sidebar.subheader("🗑 Manage Ingested Data")

if st.sidebar.button("🧹 Clear Uploaded Policies"):
    removed = clear_faiss_index()
    st.session_state.clear()
    if removed:
        st.sidebar.success("All uploaded policy data has been cleared.")
    else:
        st.sidebar.info("No uploaded policy data found.")
    st.rerun()
st.sidebar.markdown("---")

st.sidebar.markdown("""
### Upload PDFs
You can upload banking policy PDFs and the system will ingest them instantly.

### Example questions
- What's the maximum wire transfer amount without manager approval  
- Who can approve transactions above $100,000  
""")

# ---------------------------
# Main Title
# ---------------------------
st.markdown('<div class="big-title">🏦 Banking Policy Q&A Assistant</div>', unsafe_allow_html=True)
st.write("A lightweight RAG + MCP demo running entirely on your laptop.")

# ---------------------------
# PDF Upload Section
# ---------------------------
st.subheader("📄 Upload Policy PDFs")

uploaded_files = st.file_uploader(
    "Upload PDF policy files",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("Process PDFs"):
        with st.spinner("Processing and indexing PDFs…"):
            num_chunks = ingest_uploaded_pdfs(uploaded_files)

        st.success(f"Processed {len(uploaded_files)} file(s) into {num_chunks} chunks.")
        st.session_state.qa = BankingPolicyQA()  # reload RAG pipeline
        st.rerun()

st.subheader("📡 Ingest from Databricks")

server = st.text_input("Server Hostname",value=settings.DATABRICKS_SERVER_HOSTNAME)
http_path = st.text_input("HTTP Path", value=settings.DATABRICKS_HTTP_PATH)
token = st.text_input("Access Token", value=settings.DATABRICKS_ACCESS_TOKEN, type="password")
table = st.text_input("Table Name", value=settings.DATABRICKS_TABLE)

if st.button("Ingest from Databricks"):
    from src.rag_pipeline.ingest import ingest_from_databricks

    with st.spinner("Fetching and indexing policies from Databricks…"):
        num_chunks = ingest_from_databricks(server, http_path, token, table)

    st.success(f"Ingested {num_chunks} chunks from Databricks.")
    st.session_state.qa = BankingPolicyQA()
    st.rerun()


# ---------------------------
# Initialize QA system
# ---------------------------
if "qa" not in st.session_state:
    st.session_state.qa = BankingPolicyQA()

qa = st.session_state.qa

# ---------------------------
# Layout: Two Columns
# ---------------------------
left, right = st.columns([1.2, 1])

with left:
    st.subheader("Ask a Question")
    question = st.text_input(
        "Enter your banking policy question:",
        value="What's the maximum wire transfer amount without manager approval?",
        placeholder="Type your question here...",
    )

    if st.button("Ask"):
        with st.spinner("Analyzing policies…"):
            result = qa.answer(question)

        st.markdown("### 🧠 Answer")
        st.markdown(f'<div class="response-box">{result["answer"]}</div>', unsafe_allow_html=True)

        st.markdown("### 📚 Citations")
        for c in result["citations"]:
            st.markdown(f"- <span class='citation'>{c}</span>", unsafe_allow_html=True)

with right:
    st.subheader("📄 MCP Policy Sections")
    mcp_sections = qa.mcp.search_policy(question)

    for sec in mcp_sections:
        st.markdown(
            f"""
            <div class="mcp-box">
            <strong>{sec['title']} – Section {sec['section_id']}</strong><br>
            {sec['text']}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("✔️ Compliance Check")
    if "result" in locals():
        st.json(result["compliance"])
