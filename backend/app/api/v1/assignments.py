from typing import List, Optional
from fastapi import APIRouter, Depends, status
from app.core.constants import DocumentType
from app.dependencies import get_current_user, require_teacher
from app.models.database.models import UserProfileDB
from app.models.schemas.assignment import AssignmentCreateRequest, AssignmentResponse
from app.services.assignment_service import AssignmentService

router = APIRouter(prefix="/assignments", tags=["Assignments"])
assignment_service = AssignmentService()


@router.post("", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_teacher)])
async def create_assignment(
    payload: AssignmentCreateRequest,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Creates a new legal drafting assignment with instructions, deadlines, and rubrics (Teacher Only).
    """
    return assignment_service.create_assignment(teacher_id=current_user.id, payload=payload)


@router.get("", response_model=List[AssignmentResponse])
async def list_assignments(
    document_type: Optional[DocumentType] = None,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Lists published drafting assignments available for submission.
    """
    return assignment_service.list_student_assignments(doc_type=document_type)


@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    assignment_id: str,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Retrieves assignment parameters and instructions.
    """
    return assignment_service.get_assignment(assignment_id=assignment_id)