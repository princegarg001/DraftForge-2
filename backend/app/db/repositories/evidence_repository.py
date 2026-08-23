from typing import Any, Dict, List
from app.db.repositories.base_repository import BaseRepository


class EvidenceRepository(BaseRepository):
    def __init__(self):
        super().__init__(table_name="evaluation_evidence")

    def create_batch(self, evaluation_id: str, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        payloads = []
        for f in findings:
            p = {
                "evaluation_id": evaluation_id,
                "category": f["category"],
                "criterion": f["criterion"],
                "status": f["status"],
                "score": f["score"],
                "max_score": f["max_score"],
                "student_evidence": f.get("student_evidence"),
                "reference_evidence": f.get("reference_evidence"),
                "source_document": f.get("source_document"),
                "source_page": f.get("source_page"),
                "source_section": f.get("source_section"),
                "explanation": f["explanation"],
            }
            payloads.append(p)

        if not payloads:
            return []

        res = self.client.table(self.table_name).insert(payloads).execute()
        return res.data or []

    def get_by_evaluation_id(self, evaluation_id: str) -> List[Dict[str, Any]]:
        res = self.client.table(self.table_name).select("*").eq("evaluation_id", evaluation_id).execute()
        return res.data or []