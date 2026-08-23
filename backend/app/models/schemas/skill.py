from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SkillDetail(BaseModel):
    id: str
    name: str
    category: str
    description: Optional[str] = None


class StudentSkillResponse(BaseModel):
    id: str
    user_id: str
    skill_id: str
    proficiency_score: float
    confidence_level: float
    updated_at: datetime
    skill: SkillDetail