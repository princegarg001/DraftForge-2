from app.db.repositories.analytics_repository import AnalyticsRepository
from app.models.schemas.analytics import CohortAnalyticsResponse, WeakSkillStat


class AnalyticsService:
    def __init__(self):
        self.repo = AnalyticsRepository()

    def get_cohort_analytics(self) -> CohortAnalyticsResponse:
        data = self.repo.get_cohort_overview()
        weak_stats = [WeakSkillStat(**item) for item in data["weak_skills_distribution"]]
        return CohortAnalyticsResponse(
            total_students=data["total_students"],
            total_evaluations=data["total_evaluations"],
            cohort_average_score=data["cohort_average_score"],
            weak_skills_distribution=weak_stats
        )