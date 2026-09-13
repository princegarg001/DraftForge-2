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

    def get_owner_id(self, evaluation_id: str) -> Optional[str]:
        """Resolve the student who owns ``evaluation_id``.

        evaluations carries no user column, so ownership is only reachable by
        walking evaluations -> draft_versions -> drafts.user_id. Without this,
        evaluation endpoints match on a bare id and expose any student's scores
        and draft evidence to any authenticated caller.
        """
        res = (
            self.client.table(self.table_name)
            .select("id, draft_versions!inner(id, drafts!inner(user_id))")
            .eq("id", evaluation_id)
            .limit(1)
            .execute()
        )
        if not res.data:
            return None

        version = res.data[0].get("draft_versions") or {}
        if isinstance(version, list):
            version = version[0] if version else {}
        draft = version.get("drafts") or {}
        if isinstance(draft, list):
            draft = draft[0] if draft else {}
        return draft.get("user_id")

    def is_visible_to_teacher(self, evaluation_id: str, teacher_id: str) -> bool:
        """True when the evaluation was submitted to an assignment this teacher owns."""
        res = (
            self.client.table("submissions")
            .select("id, assignments!inner(teacher_id)")
            .eq("evaluation_id", evaluation_id)
            .execute()
        )
        for row in res.data or []:
            assignment = row.get("assignments") or {}
            if isinstance(assignment, list):
                assignment = assignment[0] if assignment else {}
            if assignment.get("teacher_id") == teacher_id:
                return True
        return False

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