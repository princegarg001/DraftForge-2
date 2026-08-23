from typing import Any, Dict, List
from pydantic import BaseModel


class WeakSkillStat(BaseModel):
    skill_name: str
    average_proficiency: float
    struggling_students_count: int


class CohortAnalyticsResponse(BaseModel):
    total_students: int
    total_evaluations: int
    cohort_average_score: float
    weak_skills_distribution: List[WeakSkillStat]