from typing import List, Optional
from app.core.constants import DocumentType
from app.core.exceptions import NotFoundError
from app.db.repositories.exercise_repository import ExerciseRepository
from app.models.schemas.exercise import (
    ExerciseAttemptResponse,
    ExerciseResponse,
    SubmitExerciseAttemptRequest,
)


class ExerciseService:
    def __init__(self):
        self.repo = ExerciseRepository()

    def list_exercises(self, doc_type: DocumentType, difficulty: Optional[str] = None) -> List[ExerciseResponse]:
        records = self.repo.list_by_document_type(doc_type, difficulty)
        return [ExerciseResponse(**r) for r in records]

    def get_exercise(self, exercise_id: str) -> ExerciseResponse:
        record = self.repo.get_exercise(exercise_id)
        if not record:
            raise NotFoundError("Exercise", exercise_id)
        return ExerciseResponse(**record)

    def submit_attempt(self, user_id: str, payload: SubmitExerciseAttemptRequest) -> ExerciseAttemptResponse:
        exercise = self.get_exercise(payload.exercise_id)

        # Keyword and length verification for deterministic evaluation
        submission = payload.student_submission
        matched_criteria = sum(1 for c in exercise.rubric_checklist if any(w.lower() in submission.lower() for w in c.split()[:2]))
        score = min(100.0, round((matched_criteria / max(len(exercise.rubric_checklist), 1)) * 100.0, 2))
        is_passed = score >= 60.0

        feedback = f"Matched {matched_criteria}/{len(exercise.rubric_checklist)} rubric elements. Model draft comparison available."

        attempt = self.repo.log_attempt(
            exercise_id=payload.exercise_id,
            user_id=user_id,
            submission=submission,
            feedback=feedback,
            score=score,
            is_passed=is_passed
        )

        return ExerciseAttemptResponse(**attempt)