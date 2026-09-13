from typing import Optional
from fastapi import APIRouter, Depends, status
from app.core.rate_limit import LimitScope, RateLimit
from app.dependencies import get_current_user, require_student
from app.models.database.models import UserProfileDB
from app.models.schemas.roadmap import RoadmapItemResponse, RoadmapResponse
from app.services.roadmap_service import RoadmapService

router = APIRouter(prefix="/roadmap", tags=["Personalized Learning Roadmaps"])
roadmap_service = RoadmapService()


@router.get("", response_model=Optional[RoadmapResponse])
async def get_active_roadmap(
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Retrieves the student's active 5-phase personalized learning roadmap, or null if none created yet.
    """
    return roadmap_service.get_active_roadmap(user_id=current_user.id)


@router.post(
    "/generate",
    response_model=RoadmapResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_student), Depends(RateLimit(LimitScope.LLM))],
)
async def generate_new_roadmap(
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Regenerates a 5-phase learning roadmap based on recent evaluation gaps and skill proficiencies.
    """
    return await roadmap_service.generate_roadmap(user_id=current_user.id)


@router.patch("/items/{item_id}/complete", response_model=RoadmapItemResponse)
async def complete_roadmap_item(
    item_id: str,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Marks a milestone item within a learning roadmap as completed.
    """
    return roadmap_service.complete_item(item_id=item_id, user_id=current_user.id)