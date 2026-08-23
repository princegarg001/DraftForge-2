from typing import Any, Dict, List, Optional
from app.db.repositories.base_repository import BaseRepository


class EvaluationRepository(BaseRepository):
    def __init__(self):
        super().__init__(table_name="evaluations")

    def get_with_evidence(self, evaluation_id: str) -> Optional[Dict[str, Any]]:
        res = (
            self.client.table(self.table_name)
            .select("*, evaluation_evidence(*)")
            .eq("id", evaluation_id)
            .execute()
        )
        if res.data and len(res.data) > 0:
            return res.data[0]
        return None

    def get_by_draft_version(self, draft_version_id: str) -> Optional[Dict[str, Any]]:
        res = (
            self.client.table(self.table_name)
            .select("*, evaluation_evidence(*)")
            .eq("draft_version_id", draft_version_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        if res.data and len(res.data) > 0:
            return res.data[0]
        return None