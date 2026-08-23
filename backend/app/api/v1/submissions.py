from typing import List
from fastapi import APIRouter, Depends, status
from app.dependencies import get_current_user, require_student, require_teacher
from app.models.database.models import UserProfileDB
from app.models.schemas.submission import (
    CreateSubmissionRequest,
    ScoreOverrideRequest,
    SubmissionResponse,
)
from app.services.submission_service import SubmissionService

router = APIRouter(prefix="/submissions", tags=["Assignment Submissions"])
submission_service = SubmissionService()


@router.post("", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_student)])
async def submit_assignment_draft(
    payload: CreateSubmissionRequest,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Submits a completed draft for an assignment and links deterministic evaluation scoring.
    """
    return submission_service.submit_assignment(student_id=current_user.id, payload=payload)


@router.get("/assignment/{assignment_id}", response_model=List[SubmissionResponse], dependencies=[Depends(require_teacher)])
async def get_assignment_submissions(
    assignment_id: str,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Lists student submissions for an assignment with full evaluation reports (Teacher Only).
    """
    return submission_service.list_assignment_submissions(assignment_id=assignment_id, teacher_id=current_user.id)


@router.post("/{submission_id}/override", response_model=SubmissionResponse, dependencies=[Depends(require_teacher)])
async def override_submission_score(
    submission_id: str,
    payload: ScoreOverrideRequest,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Allows a teacher to audit and override an automated evaluation score with custom notes.
    """
    return submission_service.override_submission_score(
        submission_id=submission_id,
        teacher_id=current_user.id,
        payload=payload
    )