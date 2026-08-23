from fastapi import APIRouter, Depends
from app.dependencies import require_teacher
from app.models.schemas.analytics import CohortAnalyticsResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Cohort Analytics"])
analytics_service = AnalyticsService()


@router.get("/cohort", response_model=CohortAnalyticsResponse, dependencies=[Depends(require_teacher)])
async def get_cohort_intelligence():
    """
    Returns aggregated class-wide performance metrics and weak-skill distributions.
    """
    return analytics_service.get_cohort_analytics()