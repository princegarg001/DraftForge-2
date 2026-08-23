from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict


class SkillDetail(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: Optional[str] = None
    name: str
    category: str
    description: Optional[str] = None


class StudentSkillResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    user_id: str
    skill_id: str
    proficiency_score: float
    confidence_level: float
    updated_at: Optional[Any] = None
    skill: SkillDetail