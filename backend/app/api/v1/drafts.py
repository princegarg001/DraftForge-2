from typing import List
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from app.core.rate_limit import LimitScope, RateLimit
from app.dependencies import get_current_user, require_student
from app.models.database.models import UserProfileDB
from app.models.schemas.draft import DraftCreateRequest, DraftResponse, DraftVersionResponse, VersionCompareResponse
from app.services.draft_service import DraftService

router = APIRouter(prefix="/drafts", tags=["Student Drafts"])
draft_service = DraftService()


@router.post("", response_model=DraftResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_student)])
async def create_draft(
    payload: DraftCreateRequest,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Create a new student draft directly from raw text.
    """
    return draft_service.create_draft(user_id=current_user.id, payload=payload)


@router.post(
    "/upload",
    response_model=DraftResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_student), Depends(RateLimit(LimitScope.UPLOAD))],
)
async def upload_draft_file(
    file: UploadFile = File(...),
    title: str = Form(None),
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Upload a student draft (PDF, DOCX, TXT) and automatically parse into Version 1.
    """
    return await draft_service.create_draft_from_file(user_id=current_user.id, file=file, title=title)


@router.get("", response_model=List[DraftResponse])
async def list_student_drafts(
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    List all drafts belonging to the authenticated student.
    """
    return draft_service.get_user_drafts(user_id=current_user.id)


@router.get("/{draft_id}", response_model=DraftResponse)
async def get_draft_details(
    draft_id: str,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Retrieve full draft details including all previous versions.
    """
    return draft_service.get_draft(draft_id=draft_id, user_id=current_user.id)


@router.post("/{draft_id}/versions", response_model=DraftVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_next_draft_version(
    draft_id: str,
    content: str = Form(...),
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Append an updated revision as the next sequential version (e.g. v2, v3).
    """
    return draft_service.add_draft_version(user_id=current_user.id, draft_id=draft_id, new_content=content)


@router.get("/{draft_id}/compare", response_model=VersionCompareResponse)
async def compare_draft_versions(
    draft_id: str,
    v1: int = 1,
    v2: int = 2,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Generate additions/deletions diff between two specific versions of a draft.
    """
    return draft_service.compare_versions(draft_id=draft_id, user_id=current_user.id, v1_num=v1, v2_num=v2)