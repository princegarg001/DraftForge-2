from __future__ import annotations

from app.core.constants import UserRole
from app.core.exceptions import NotFoundError
from app.db.repositories.analytics_repository import AnalyticsRepository
from app.db.repositories.class_repository import ClassRepository, EnrollmentRepository
from app.models.database.models import UserProfileDB
from app.models.schemas.analytics import CohortAnalyticsResponse, WeakSkillStat


class AnalyticsService:
    def __init__(self):
        self.repo = AnalyticsRepository()
        self.enrollment_repo = EnrollmentRepository()
        self.class_repo = ClassRepository()

    def get_cohort_analytics(
        self, teacher: UserProfileDB, class_id: str | None = None
    ) -> CohortAnalyticsResponse:
        """Cohort metrics for the classes this teacher runs.

        With ``class_id``, narrows to that one class after confirming the
        caller owns it.
        """
        if class_id:
            classroom = self.class_repo.get_by_id(class_id)
            if not classroom or (
                classroom["teacher_id"] != teacher.id and teacher.role is not UserRole.ADMIN
            ):
                raise NotFoundError("class", class_id)
            student_ids = [
                row["student_id"]
                for row in self.enrollment_repo.list_roster(class_id)
                if row.get("student_id") and row.get("status") == "ACTIVE"
            ]
        else:
            student_ids = self.enrollment_repo.taught_student_ids(teacher.id)

        data = self.repo.get_cohort_overview(student_ids)
        return CohortAnalyticsResponse(
            total_students=data["total_students"],
            total_evaluations=data["total_evaluations"],
            cohort_average_score=data["cohort_average_score"],
            weak_skills_distribution=[
                WeakSkillStat(**item) for item in data["weak_skills_distribution"]
            ],
        )
