"""Class and roster endpoints (instructor-facing)."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status

from app.core.rate_limit import LimitScope, RateLimit
from app.dependencies import get_current_user, require_student, require_teacher
from app.models.database.models import UserProfileDB
from app.models.schemas.classroom import (
    BulkInviteRequest,
    BulkInviteResponse,
    ClassCreateRequest,
    ClassResponse,
    ClassUpdateRequest,
    EnrollmentResponse,
    InviteOutcome,
    PendingInvitationResponse,
)
from app.services.class_service import ClassService
from app.services.invitation_service import InvitationService

router = APIRouter(prefix="/classes", tags=["Classes & Roster"])
class_service = ClassService()
invitation_service = InvitationService()

_teacher = Depends(require_teacher)


@router.post("", response_model=ClassResponse, status_code=status.HTTP_201_CREATED, dependencies=[_teacher])
async def create_class(
    payload: ClassCreateRequest,
    current_user: UserProfileDB = Depends(get_current_user),
) -> ClassResponse:
    """Create a class. The caller becomes its instructor."""
    return class_service.create_class(current_user, payload)


@router.get("", response_model=list[ClassResponse], dependencies=[_teacher])
async def list_my_classes(
    include_archived: bool = Query(False),
    current_user: UserProfileDB = Depends(get_current_user),
) -> list[ClassResponse]:
    return class_service.list_teacher_classes(current_user, include_archived)


@router.get("/enrolled", response_model=list[ClassResponse], dependencies=[Depends(require_student)])
async def list_enrolled_classes(
    current_user: UserProfileDB = Depends(get_current_user),
) -> list[ClassResponse]:
    """Classes the authenticated student belongs to."""
    return class_service.list_student_classes(current_user)


@router.get("/{class_id}", response_model=ClassResponse, dependencies=[_teacher])
async def get_class(
    class_id: str,
    current_user: UserProfileDB = Depends(get_current_user),
) -> ClassResponse:
    return class_service.get_class(class_id, current_user)


@router.patch("/{class_id}", response_model=ClassResponse, dependencies=[_teacher])
async def update_class(
    class_id: str,
    payload: ClassUpdateRequest,
    current_user: UserProfileDB = Depends(get_current_user),
) -> ClassResponse:
    return class_service.update_class(class_id, current_user, payload)


@router.post("/{class_id}/rotate-join-code", response_model=ClassResponse, dependencies=[_teacher])
async def rotate_join_code(
    class_id: str,
    current_user: UserProfileDB = Depends(get_current_user),
) -> ClassResponse:
    """Issue a fresh join code, invalidating the previous one."""
    return class_service.rotate_join_code(class_id, current_user)


@router.get("/{class_id}/roster", response_model=list[EnrollmentResponse], dependencies=[_teacher])
async def get_roster(
    class_id: str,
    current_user: UserProfileDB = Depends(get_current_user),
) -> list[EnrollmentResponse]:
    return class_service.get_roster(class_id, current_user)


@router.post(
    "/{class_id}/invitations",
    response_model=BulkInviteResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[_teacher, Depends(RateLimit(LimitScope.INVITE))],
)
async def invite_students(
    class_id: str,
    payload: BulkInviteRequest,
    background_tasks: BackgroundTasks,
    current_user: UserProfileDB = Depends(get_current_user),
) -> BulkInviteResponse:
    """Add students to the roster and email each an invitation.

    Returns 202: the roster is updated synchronously, but delivery happens out
    of band, so a slow provider cannot stall a large batch.
    """
    return invitation_service.invite_students(
        class_id=class_id,
        teacher=current_user,
        students=payload.students,
        background_tasks=background_tasks,
    )


@router.get(
    "/{class_id}/invitations",
    response_model=list[PendingInvitationResponse],
    dependencies=[_teacher],
)
async def list_pending_invitations(
    class_id: str,
    current_user: UserProfileDB = Depends(get_current_user),
) -> list[PendingInvitationResponse]:
    return class_service.list_pending_invitations(class_id, current_user)


@router.post(
    "/{class_id}/invitations/resend",
    response_model=InviteOutcome,
    dependencies=[_teacher, Depends(RateLimit(LimitScope.INVITE))],
)
async def resend_invitation(
    class_id: str,
    email: str,
    background_tasks: BackgroundTasks,
    current_user: UserProfileDB = Depends(get_current_user),
) -> InviteOutcome:
    """Reissue an invitation. The previous token is revoked."""
    return invitation_service.resend_invitation(
        class_id=class_id,
        email=email,
        teacher=current_user,
        background_tasks=background_tasks,
    )


@router.delete(
    "/{class_id}/invitations/{invitation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[_teacher],
)
async def revoke_invitation(
    class_id: str,  # noqa: ARG001 - scopes the route; ownership is checked on the invitation
    invitation_id: str,
    current_user: UserProfileDB = Depends(get_current_user),
) -> None:
    invitation_service.revoke_invitation(invitation_id, current_user)


@router.delete(
    "/{class_id}/roster/{enrollment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[_teacher],
)
async def remove_student(
    class_id: str,
    enrollment_id: str,
    current_user: UserProfileDB = Depends(get_current_user),
) -> None:
    """Remove a student from the roster.

    Their coursework is retained; only the enrollment is withdrawn.
    """
    class_service.remove_student(class_id, enrollment_id, current_user)
