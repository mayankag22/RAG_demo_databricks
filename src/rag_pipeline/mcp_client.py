from typing import List, Dict, Any
import requests


class MCPClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def search_policy(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        resp = requests.post(
            f"{self.base_url}/tools/search_policy",
            json={"query": query, "top_k": top_k},
            timeout=5,
        )
        resp.raise_for_status()
        return resp.json()["results"]

    def get_section(self, policy_id: str, section_id: str) -> Dict[str, Any] | None:
        resp = requests.post(
            f"{self.base_url}/tools/get_section",
            json={"policy_id": policy_id, "section_id": section_id},
            timeout=5,
        )
        resp.raise_for_status()
        return resp.json()

    def check_compliance(
        self,
        question: str,
        answer: str,
        referenced_sections: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/tools/check_compliance",
            json={
                "question": question,
                "answer": answer,
                "referenced_sections": referenced_sections,
            },
            timeout=5,
        )
        resp.raise_for_status()
        return resp.json()