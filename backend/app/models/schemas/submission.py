from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel
from app.models.schemas.evaluation import EvaluationResponse


class CreateSubmissionRequest(BaseModel):
    assignment_id: str
    draft_id: str
    draft_version_id: str


class ScoreOverrideRequest(BaseModel):
    overridden_score: float
    override_reason: str
    teacher_notes: Optional[str] = None


class SubmissionResponse(BaseModel):
    id: str
    assignment_id: str
    student_id: str
    draft_id: str
    draft_version_id: str
    evaluation_id: Optional[str] = None
    status: str
    final_score: Optional[float] = None
    teacher_notes: Optional[str] = None
    submitted_at: datetime
    student_name: Optional[str] = None
    student_email: Optional[str] = None
    evaluation: Optional[EvaluationResponse] = None