from typing import Any, Dict, List, Optional
from app.db.repositories.base_repository import BaseRepository


class SubmissionRepository(BaseRepository):
    def __init__(self):
        super().__init__(table_name="submissions")

    def get_student_submission(self, assignment_id: str, student_id: str) -> Optional[Dict[str, Any]]:
        res = (
            self.client.table(self.table_name)
            .select("*, assignments(*), evaluations(*)")
            .eq("assignment_id", assignment_id)
            .eq("student_id", student_id)
            .execute()
        )
        return res.data[0] if res.data else None

    def list_by_assignment(self, assignment_id: str) -> List[Dict[str, Any]]:
        res = (
            self.client.table(self.table_name)
            .select("*, profiles:student_id(full_name, email), evaluations(*), draft_versions(raw_content)")
            .eq("assignment_id", assignment_id)
            .order("submitted_at", desc=True)
            .execute()
        )
        return res.data or []

    def update_evaluation_override(
        self,
        evaluation_id: str,
        overridden_score: float,
        teacher_id: str,
        override_reason: str
    ) -> Dict[str, Any]:
        payload = {
            "is_overridden": True,
            "overridden_score": overridden_score,
            "overridden_by": teacher_id,
            "override_reason": override_reason,
        }
        res = self.client.table("evaluations").update(payload).eq("id", evaluation_id).execute()
        return res.data[0] if res.data else {}

    def update_submission_score(
        self,
        submission_id: str,
        final_score: float,
        teacher_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        payload = {
            "final_score": final_score,
            "status": "GRADED_OVERRIDDEN",
            "teacher_notes": teacher_notes
        }
        res = self.client.table(self.table_name).update(payload).eq("id", submission_id).execute()
        return res.data[0] if res.data else {}