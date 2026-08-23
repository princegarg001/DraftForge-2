from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.core.constants import DocumentType


class ExerciseResponse(BaseModel):
    id: str
    skill_id: Optional[str] = None
    document_type: DocumentType
    title: str
    scenario: str
    instructions: str
    difficulty: str
    hints: List[str] = []
    model_solution: str
    rubric_checklist: List[str] = []
    created_at: datetime


class SubmitExerciseAttemptRequest(BaseModel):
    exercise_id: str
    student_submission: str


class ExerciseAttemptResponse(BaseModel):
    id: str
    exercise_id: str
    user_id: str
    student_submission: str
    feedback: Optional[str] = None
    score: Optional[float] = None
    is_passed: bool
    created_at: datetime