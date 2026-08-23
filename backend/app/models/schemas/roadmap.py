from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class RoadmapItemResponse(BaseModel):
    id: str
    roadmap_id: str
    phase_number: int
    title: str
    description: Optional[str] = None
    skill_id: Optional[str] = None
    is_completed: bool
    completed_at: Optional[datetime] = None


class RoadmapResponse(BaseModel):
    id: str
    user_id: str
    title: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    roadmap_items: List[RoadmapItemResponse] = []