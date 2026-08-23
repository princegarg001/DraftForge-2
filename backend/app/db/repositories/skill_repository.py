from typing import Any, Dict, List, Optional
from app.db.repositories.base_repository import BaseRepository


class SkillRepository(BaseRepository):
    def __init__(self):
        super().__init__(table_name="skills")

    def get_skill_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        res = self.client.table(self.table_name).select("*").eq("name", name).execute()
        return res.data[0] if res.data else None

    def get_student_skills(self, user_id: str) -> List[Dict[str, Any]]:
        res = (
            self.client.table("student_skills")
            .select("*, skills(*)")
            .eq("user_id", user_id)
            .execute()
        )
        return res.data or []

    def get_student_skill(self, user_id: str, skill_id: str) -> Optional[Dict[str, Any]]:
        res = (
            self.client.table("student_skills")
            .select("*, skills(*)")
            .eq("user_id", user_id)
            .eq("skill_id", skill_id)
            .execute()
        )
        return res.data[0] if res.data else None

    def upsert_student_skill(
        self,
        user_id: str,
        skill_id: str,
        proficiency_score: float,
        confidence_level: float
    ) -> Dict[str, Any]:
        from datetime import datetime, timezone
        payload = {
            "user_id": user_id,
            "skill_id": skill_id,
            "proficiency_score": proficiency_score,
            "confidence_level": confidence_level,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        res = self.client.table("student_skills").upsert(payload).execute()
        return res.data[0] if res.data else {}

    def log_skill_history(
        self,
        student_skill_id: str,
        score_delta: float,
        reason: str,
        evaluation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        payload = {
            "student_skill_id": student_skill_id,
            "score_delta": score_delta,
            "evaluation_id": evaluation_id,
            "reason": reason,
        }
        res = self.client.table("skill_history").insert(payload).execute()
        return res.data[0] if res.data else {}