from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.models.database.models import UserProfileDB
from app.models.schemas.leaderboard import LeaderboardResponse
from app.services.progress_service import ProgressService

router = APIRouter(prefix="/leaderboard", tags=["Student Leaderboard"])
progress_service = ProgressService()


@router.get("", response_model=LeaderboardResponse)
async def get_leaderboard(
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Retrieves global student leaderboard rankings based on average drafting scores.
    """
    return progress_service.get_leaderboard()