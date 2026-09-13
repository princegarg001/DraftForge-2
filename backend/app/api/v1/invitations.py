"""Invitation acceptance (unauthenticated).

These are the only unauthenticated write endpoints in the API, so they are
rate limited under the AUTH scope: possession of a token is the sole
credential, and unthrottled they would permit token guessing and let one leaked
link be replayed at speed.
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Body, Depends, Query, status

from app.core.rate_limit import LimitScope, RateLimit
from app.db.supabase import get_supabase_anon_client
from app.models.schemas.auth import AuthTokenResponse
from app.models.schemas.classroom import AcceptInvitationRequest, InvitationPreviewResponse
from app.core.constants import UserRole
from app.core.exceptions import AuthenticationError
from app.core.logging import get_logger
from app.services.invitation_service import InvitationService

logger = get_logger("invitations_router")
router = APIRouter(prefix="/invitations", tags=["Invitations"])
invitation_service = InvitationService()

_invite_limit = Depends(RateLimit(LimitScope.AUTH))


@router.get("/preview", response_model=InvitationPreviewResponse, dependencies=[_invite_limit])
async def preview_invitation(
    token: str = Query(min_length=16, max_length=256),
) -> InvitationPreviewResponse:
    """Describe a pending invitation so the acceptance page can render.

    Returns only what the page needs. In particular it does not reveal whether
    an account already exists for the address.
    """
    return invitation_service.preview_invitation(token)


@router.post(
    "/accept",
    response_model=AuthTokenResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[_invite_limit],
)
async def accept_invitation(
    background_tasks: BackgroundTasks,
    payload: AcceptInvitationRequest = Body(...),
) -> AuthTokenResponse:
    """Redeem an invitation: create the account and sign the student in.

    The address is taken from the invitation record, never from the request
    body - otherwise one leaked token would allow account creation against any
    address the caller chose.
    """
    result = invitation_service.accept_invitation(payload, background_tasks)

    # Sign in with the password just set, so the student lands authenticated
    # rather than being bounced to a login form.
    supabase = get_supabase_anon_client()
    try:
        auth_response = supabase.auth.sign_in_with_password(
            {"email": result["email"], "password": payload.password}
        )
    except Exception as exc:
        logger.error(f"Post-acceptance sign-in failed: {exc.__class__.__name__}")
        raise AuthenticationError("Your account is ready. Please sign in to continue.") from exc

    if not auth_response.session:
        raise AuthenticationError("Your account is ready. Please sign in to continue.")

    return AuthTokenResponse(
        access_token=auth_response.session.access_token,
        refresh_token=getattr(auth_response.session, "refresh_token", None),
        expires_in=getattr(auth_response.session, "expires_in", None),
        user_id=result["user_id"],
        email=result["email"],
        role=UserRole.STUDENT,
        full_name=payload.full_name,
    )
