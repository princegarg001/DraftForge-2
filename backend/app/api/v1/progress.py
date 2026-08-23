from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.models.database.models import UserProfileDB
from app.models.schemas.progress import StudentProgressResponse
from app.services.progress_service import ProgressService

router = APIRouter(prefix="/progress", tags=["Student Progress & Analytics"])
progress_service = ProgressService()


@router.get("", response_model=StudentProgressResponse)
async def get_progress(
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Returns aggregated evaluation averages, score trends, and skill metrics for the current student.
    """
    return progress_service.get_student_progress(user_id=current_user.id)