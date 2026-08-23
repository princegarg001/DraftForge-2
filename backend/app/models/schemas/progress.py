from typing import Dict, List
from pydantic import BaseModel


class StudentProgressResponse(BaseModel):
    user_id: str
    total_evaluations: int
    average_score: float
    score_history: List[float] = []
    document_type_averages: Dict[str, float] = {}
    mastered_skills_count: int
    weak_skills_count: int