from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict


class RoadmapItemResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    roadmap_id: str
    phase_number: int
    title: str
    description: Optional[str] = None
    skill_id: Optional[str] = None
    is_completed: bool = False
    completed_at: Optional[Any] = None


class RoadmapResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    user_id: str
    title: str
    is_active: bool = True
    created_at: Optional[Any] = None
    updated_at: Optional[Any] = None
    roadmap_items: List[RoadmapItemResponse] = []