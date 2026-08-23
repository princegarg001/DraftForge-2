from typing import List
from app.db.repositories.skill_repository import SkillRepository
from app.models.schemas.skill import SkillDetail, StudentSkillResponse


class SkillService:
    def __init__(self):
        self.repo = SkillRepository()

    def get_student_skills(self, user_id: str) -> List[StudentSkillResponse]:
        records = self.repo.get_student_skills(user_id) or []
        results = []
        for r in records:
            s_data = r.get("skills") or {"name": "Statutory Drafting", "category": "LEGAL", "description": "Legal drafting competency"}
            if not isinstance(s_data, dict):
                s_data = {"name": str(s_data), "category": "LEGAL", "description": ""}
            results.append(
                StudentSkillResponse(
                    id=r["id"],
                    user_id=r["user_id"],
                    skill_id=r["skill_id"],
                    proficiency_score=float(r.get("proficiency_score", 50.0)),
                    confidence_level=float(r.get("confidence_level", 0.5)),
                    updated_at=r.get("updated_at"),
                    skill=SkillDetail(**s_data)
                )
            )
        return results