from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class PolicySection(BaseModel):
    policy_id: str
    title: str
    section_id: str
    section_title: str
    text: str


class InMemoryPolicyStore:
    def __init__(self):
        self._sections: List[PolicySection] = []

    def load_sample_policies(self):
        # Hard-coded demo sections matching sample text files
        self._sections = [
            PolicySection(
                policy_id="wire-transfer-v2.3",
                title="Wire Transfer Policy v2.3",
                section_id="4.2",
                section_title="Approval Thresholds",
                text=(
                    "Amounts up to $25,000 can be processed without manager "
                    "approval for verified customers. Amounts between "
                    "$25,000 and $100,000 require branch manager approval. "
                    "Amounts above $100,000 require regional director approval."
                ),
            ),
            PolicySection(
                policy_id="approval-matrix-v1.1",
                title="Approval Matrix v1.1",
                section_id="2.1",
                section_title="Transaction Limits",
                text=(
                    "Tellers may approve transactions up to $10,000. "
                    "Branch managers may approve transactions up to $100,000. "
                    "Regional directors may approve transactions above $100,000."
                ),
            ),
        ]

    def search_policy(self, query: str, top_k: int = 5) -> List[PolicySection]:
        query_lower = query.lower()
        scored: List[tuple[int, PolicySection]] = []
        for sec in self._sections:
            score = sec.text.lower().count(query_lower)
            if score > 0:
                scored.append((score, sec))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [s[1] for s in scored[:top_k]]

    def get_section(self, policy_id: str, section_id: str) -> Optional[PolicySection]:
        for sec in self._sections:
            if sec.policy_id == policy_id and sec.section_id == section_id:
                return sec
        return None
