from typing import Any, Dict, List, Optional
from app.core.constants import DocumentType
from app.db.repositories.base_repository import BaseRepository


class AssignmentRepository(BaseRepository):
    def __init__(self):
        super().__init__(table_name="assignments")

    def list_teacher_assignments(self, teacher_id: str) -> List[Dict[str, Any]]:
        res = (
            self.client.table(self.table_name)
            .select("*, submissions(count)")
            .eq("teacher_id", teacher_id)
            .order("created_at", desc=True)
            .execute()
        )
        return res.data or []

    def list_active_assignments(self, doc_type: Optional[DocumentType] = None) -> List[Dict[str, Any]]:
        query = self.client.table(self.table_name).select("*").eq("status", "PUBLISHED")
        if doc_type:
            query = query.eq("document_type", doc_type.value)
        res = query.order("created_at", desc=True).execute()
        return res.data or []

    def get_assignment_with_submissions(self, assignment_id: str) -> Optional[Dict[str, Any]]:
        res = (
            self.client.table(self.table_name)
            .select("*, submissions(*, profiles(full_name, email), evaluations(*))")
            .eq("id", assignment_id)
            .execute()
        )
        return res.data[0] if res.data else None