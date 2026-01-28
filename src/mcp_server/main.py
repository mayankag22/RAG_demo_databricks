from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from .policy_store import InMemoryPolicyStore, PolicySection

app = FastAPI(title="Banking Policy MCP Server", version="0.1.0")

store = InMemoryPolicyStore()
store.load_sample_policies()


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class SearchResponse(BaseModel):
    results: List[PolicySection]


class SectionRequest(BaseModel):
    policy_id: str
    section_id: str


class ComplianceRequest(BaseModel):
    question: str
    answer: str
    referenced_sections: List[Dict[str, Any]]
    user_role: Optional[str] = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tools/search_policy", response_model=SearchResponse)
def search_policy(req: SearchRequest):
    results = store.search_policy(req.query, req.top_k)
    return SearchResponse(results=results)


@app.post("/tools/get_section", response_model=Optional[PolicySection])
def get_section(req: SectionRequest):
    return store.get_section(req.policy_id, req.section_id)


@app.post("/tools/check_compliance")
def check_compliance(req: ComplianceRequest):
    # Stubbed compliance check for demo
    return {
        "compliant": True,
        "issues": [],
        "notes": "Answer appears consistent with referenced policy sections.",
    }
