from typing import Any, Dict, List, Optional
from app.core.constants import DocumentType
from app.db.repositories.base_repository import BaseRepository


class ExerciseRepository(BaseRepository):
    def __init__(self):
        super().__init__(table_name="exercises")

    def list_by_document_type(self, doc_type: DocumentType, difficulty: Optional[str] = None) -> List[Dict[str, Any]]:
        query = self.client.table(self.table_name).select("*, skills(*)").eq("document_type", doc_type.value)
        if difficulty:
            query = query.eq("difficulty", difficulty.upper())
        res = query.execute()
        return res.data or []

    def get_exercise(self, exercise_id: str) -> Optional[Dict[str, Any]]:
        res = self.client.table(self.table_name).select("*, skills(*)").eq("id", exercise_id).execute()
        return res.data[0] if res.data else None

    def log_attempt(
        self,
        exercise_id: str,
        user_id: str,
        submission: str,
        feedback: str,
        score: float,
        is_passed: bool
    ) -> Dict[str, Any]:
        payload = {
            "exercise_id": exercise_id,
            "user_id": user_id,
            "student_submission": submission,
            "feedback": feedback,
            "score": score,
            "is_passed": is_passed
        }
        res = self.client.table("exercise_attempts").insert(payload).execute()
        return res.data[0] if res.data else {}

    def get_user_attempts(self, user_id: str) -> List[Dict[str, Any]]:
        res = (
            self.client.table("exercise_attempts")
            .select("*, exercises(*)")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return res.data or []