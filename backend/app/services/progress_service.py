from app.core.constants import UserRole
from app.db.repositories.class_repository import EnrollmentRepository
from app.db.repositories.progress_repository import ProgressRepository
from app.db.repositories.skill_repository import SkillRepository
from app.models.database.models import UserProfileDB
from app.models.schemas.leaderboard import LeaderboardEntry, LeaderboardResponse
from app.models.schemas.progress import StudentProgressResponse


class ProgressService:
    def __init__(self):
        self.repo = ProgressRepository()
        self.skill_repo = SkillRepository()
        self.enrollment_repo = EnrollmentRepository()

    def get_student_progress(self, user_id: str) -> StudentProgressResponse:
        stats = self.repo.get_student_evaluation_stats(user_id)
        skills = self.skill_repo.get_student_skills(user_id)

        mastered = sum(1 for s in skills if float(s["proficiency_score"]) >= 75.0)
        weak = sum(1 for s in skills if float(s["proficiency_score"]) < 60.0)

        return StudentProgressResponse(
            user_id=user_id,
            total_evaluations=stats["total_evaluations"],
            average_score=stats["average_score"],
            score_history=stats["score_history"],
            document_type_averages=stats["document_type_averages"],
            mastered_skills_count=mastered,
            weak_skills_count=weak
        )

    def get_leaderboard(self, user: UserProfileDB) -> LeaderboardResponse:
        """Rank the caller against their classmates only.

        A teacher sees the students they actually teach; a student sees peers
        from classes they share. Someone enrolled in nothing sees an empty
        board rather than the whole platform.
        """
        if user.role is UserRole.TEACHER:
            student_ids = self.enrollment_repo.taught_student_ids(user.id)
        else:
            student_ids = self.enrollment_repo.classmate_ids(user.id)

        entries = self.repo.get_leaderboard(student_ids)
        return LeaderboardResponse(entries=[LeaderboardEntry(**e) for e in entries])