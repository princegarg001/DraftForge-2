from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_current_user, require_teacher
from app.models.database.models import UserProfileDB
from app.models.schemas.analytics import CohortAnalyticsResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Cohort Analytics"])
analytics_service = AnalyticsService()


@router.get("/cohort", response_model=CohortAnalyticsResponse, dependencies=[Depends(require_teacher)])
async def get_cohort_intelligence(
    class_id: Optional[str] = Query(None, description="Narrow to a single class you own."),
    current_user: UserProfileDB = Depends(get_current_user),
) -> CohortAnalyticsResponse:
    """
    Aggregated performance metrics and weak-skill distribution for the
    caller's own classes.
    """
    return analytics_service.get_cohort_analytics(current_user, class_id)