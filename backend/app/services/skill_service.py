from typing import List
from app.db.repositories.skill_repository import SkillRepository
from app.models.schemas.skill import SkillDetail, StudentSkillResponse


class SkillService:
    def __init__(self):
        self.repo = SkillRepository()

    def get_student_skills(self, user_id: str) -> List[StudentSkillResponse]:
        records = self.repo.get_student_skills(user_id)
        results = []
        for r in records:
            s_data = r["skills"]
            results.append(
                StudentSkillResponse(
                    id=r["id"],
                    user_id=r["user_id"],
                    skill_id=r["skill_id"],
                    proficiency_score=float(r["proficiency_score"]),
                    confidence_level=float(r["confidence_level"]),
                    updated_at=r["updated_at"],
                    skill=SkillDetail(**s_data)
                )
            )
        return results