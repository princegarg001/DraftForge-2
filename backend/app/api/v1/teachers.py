from typing import List
from fastapi import APIRouter, Depends
from app.dependencies import get_current_user, require_teacher
from app.models.database.models import UserProfileDB
from app.models.schemas.analytics import CohortAnalyticsResponse
from app.models.schemas.assignment import AssignmentResponse
from app.services.analytics_service import AnalyticsService
from app.services.assignment_service import AssignmentService

router = APIRouter(prefix="/teachers", tags=["Teacher Portal"])
assignment_service = AssignmentService()
analytics_service = AnalyticsService()


@router.get("/assignments", response_model=List[AssignmentResponse], dependencies=[Depends(require_teacher)])
async def list_teacher_assignments(
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Retrieves all assignments managed by the authenticated teacher.
    """
    return assignment_service.list_teacher_assignments(teacher_id=current_user.id)


@router.get("/cohort-analytics", response_model=CohortAnalyticsResponse, dependencies=[Depends(require_teacher)])
async def get_cohort_analytics(
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Retrieves performance metrics, average scores, and weak-skill distributions
    across the classes this teacher runs.
    """
    return analytics_service.get_cohort_analytics(current_user)