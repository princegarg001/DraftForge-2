from typing import List
from pydantic import BaseModel


class LeaderboardEntry(BaseModel):
    user_id: str
    full_name: str
    evaluations_completed: int
    average_score: float


class LeaderboardResponse(BaseModel):
    entries: List[LeaderboardEntry]