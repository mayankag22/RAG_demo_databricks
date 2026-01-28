import os
import tempfile
from typing import List
from langchain_community.document_loaders import PyPDFLoader

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from databricks import sql
from src.config import settings
INDEX_DIR = "data/faiss_index"


def load_text_policies(data_dir: str) -> List:
    docs = []
    for fname in os.listdir(data_dir):
        if fname.lower().endswith(".txt"):
            path = os.path.join(data_dir, fname)
            from langchain_community.document_loaders import TextLoader
            loader = TextLoader(path, encoding="utf-8")
            docs.extend(loader.load())
    return docs


def chunk_docs(docs, chunk_size: int = 600, chunk_overlap: int = 100):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\nSection", "\n\n", "\n", " "],
    )
    return splitter.split_documents(docs)


def build_faiss_index(chunks, index_dir: str = INDEX_DIR):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vs = FAISS.from_documents(chunks, embedding=embeddings)
    os.makedirs(index_dir, exist_ok=True)
    vs.save_local(index_dir)
    return vs


def ingest_uploaded_pdfs(uploaded_files):
    """
    Ingest PDFs uploaded by the user on the fly.
    Updates FAISS index (creates if missing).
    """
    docs = []

    # Save uploaded PDFs temporarily and load them
    for file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file.read())
            loader = PyPDFLoader(tmp.name)
            docs.extend(loader.load())

    # Chunking
    chunks = chunk_docs(docs)

    # Embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Update or create FAISS index
    if os.path.exists(INDEX_DIR):
        vs = FAISS.load_local(INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
        vs.add_documents(chunks)
        vs.save_local(INDEX_DIR)
    else:
        vs = FAISS.from_documents(chunks, embedding=embeddings)
        os.makedirs(INDEX_DIR, exist_ok=True)
        vs.save_local(INDEX_DIR)

    return len(chunks)

def ingest_from_databricks(
    server_hostname: str = None,
    http_path: str = None,
    access_token: str = None,
    table_name: str = None
):
    """
    Fetches policy rows from Databricks, chunks them, embeds them,
    and updates the FAISS index.
    """

    server_hostname = server_hostname or settings.DATABRICKS_SERVER_HOSTNAME 
    http_path = http_path or settings.DATABRICKS_HTTP_PATH 
    access_token = access_token or settings.DATABRICKS_ACCESS_TOKEN 
    table_name = table_name or settings.DATABRICKS_TABLE

    # Connect to Databricks
    conn = sql.connect(
        server_hostname=server_hostname,
        http_path=http_path,
        access_token=access_token
    )

    cursor = conn.cursor()
    cursor.execute(f"SELECT policy_id, section_id, section_title, text FROM {table_name}")
    rows = cursor.fetchall()

    docs = []
    for row in rows:
        policy_id, section_id, section_title, text = row
        docs.append(
            {
                "page_content": text,
                "metadata": {
                    "policy_id": policy_id,
                    "section_id": section_id,
                    "section_title": section_title,
                    "source": f"databricks:{policy_id}:{section_id}"
                }
            }
        )

    cursor.close()
    conn.close()

    # Convert to LangChain Document objects
    
    lc_docs = [Document(page_content=d["page_content"], metadata=d["metadata"]) for d in docs]

    # Chunk
    chunks = chunk_docs(lc_docs)

    # Embed + update FAISS
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    if os.path.exists(INDEX_DIR):
        vs = FAISS.load_local(INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
        vs.add_documents(chunks)
        vs.save_local(INDEX_DIR)
    else:
        vs = FAISS.from_documents(chunks, embedding=embeddings)
        os.makedirs(INDEX_DIR, exist_ok=True)
        vs.save_local(INDEX_DIR)

    return len(chunks)



def clear_faiss_index():
    """
    Deletes the FAISS index directory and all ingested data.
    """
    if os.path.exists(INDEX_DIR):
        for root, dirs, files in os.walk(INDEX_DIR, topdown=False):
            for f in files:
                os.remove(os.path.join(root, f))
            for d in dirs:
                os.rmdir(os.path.join(root, d))
        os.rmdir(INDEX_DIR)
        return True
    return False


if __name__ == "__main__":
    # Optional: initial ingestion of text files
    docs = load_text_policies("data/sample_policies")
    chunks = chunk_docs(docs)
    build_faiss_index(chunks)
    print(f"Ingested {len(docs)} docs into {len(chunks)} chunks.")
