"""Authentication endpoints.

Two properties are load-bearing here:

1. **The client never chooses its role.** ``register`` hardcodes STUDENT.
   Faculty accounts come from the gated invitation flow, not this endpoint.
2. **Upstream errors are never echoed to the caller.** The previous
   implementation returned ``f"Registration failed: {exc}"``, leaking Supabase
   internals - and, through the differing text for "user exists" versus other
   failures, a user-enumeration oracle.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request, status

from app.core import audit
from app.core.constants import UserRole
from app.core.exceptions import AuthenticationError, ConflictError, PermissionDeniedError
from app.core.logging import get_logger
from app.core.rate_limit import LimitScope, RateLimit
from app.core.tokens import hash_token, is_expired
from app.db.repositories.invitation_repository import FacultyCodeRepository
from app.db.repositories.user_repository import UserRepository
from app.db.supabase import get_supabase_anon_client
from app.dependencies import get_current_user
from app.models.database.models import UserProfileDB
from app.models.schemas.auth import (
    AuthenticatedUserResponse,
    AuthTokenResponse,
    RefreshTokenRequest,
    UserLoginRequest,
    UserRegisterRequest,
)
from app.models.schemas.classroom import FacultyRegisterRequest

logger = get_logger("auth_router")
router = APIRouter(prefix="/auth", tags=["Authentication"])
user_repo = UserRepository()

# Credential endpoints are throttled per IP. Without this, password guessing
# and account enumeration are bounded only by network speed.
_auth_limit = Depends(RateLimit(LimitScope.AUTH))

# Returned for every failed credential check so that a wrong password and an
# unknown account are indistinguishable.
_GENERIC_AUTH_FAILURE = "Invalid email or password."


def _session_payload(auth_response: Any) -> tuple[str, str | None, int | None]:
    session = auth_response.session
    return (
        session.access_token,
        getattr(session, "refresh_token", None),
        getattr(session, "expires_in", None),
    )


@router.post(
    "/register",
    response_model=AuthTokenResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[_auth_limit],
)
async def register(payload: UserRegisterRequest, request: Request) -> AuthTokenResponse:
    """Register a student account.

    The role is fixed server-side. Supplying a ``role`` field is rejected by the
    schema (``extra="forbid"``) rather than silently ignored, so an integration
    still sending one fails loudly instead of believing it worked.
    """
    supabase = get_supabase_anon_client()

    try:
        auth_response = supabase.auth.sign_up(
            {
                "email": payload.email,
                "password": payload.password,
                "options": {
                    # user_metadata is user-controlled and is never read for
                    # authorization. Only the display name lives here.
                    "data": {"full_name": payload.full_name},
                },
            }
        )
    except Exception as exc:
        logger.warning(f"Registration rejected for {payload.email}: {exc.__class__.__name__}: {exc}")
        raise ConflictError("Unable to complete registration with the details provided.") from exc

    if not auth_response.user:
        raise ConflictError("Unable to complete registration with the details provided.")

    user_id = str(auth_response.user.id)

    # Role is assigned here, by the server, and cannot be influenced by input.
    profile = user_repo.ensure_profile(
        user_id=user_id,
        email=payload.email,
        role=UserRole.STUDENT.value,
        full_name=payload.full_name,
    )

    if not auth_response.session:
        # Email confirmation is enabled on the project: the account exists but
        # no session is issued until the address is verified.
        raise AuthenticationError(
            "Account created. Check your email to confirm your address before signing in."
        )

    access_token, refresh_token, expires_in = _session_payload(auth_response)
    logger.info(f"Registered student {user_id} from {request.client.host if request.client else 'unknown'}")

    return AuthTokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        user_id=user_id,
        email=profile["email"],
        role=UserRole(profile["role"]),
        full_name=profile.get("full_name"),
    )


@router.post(
    "/register-faculty",
    response_model=AuthTokenResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[_auth_limit],
)
async def register_faculty(payload: FacultyRegisterRequest) -> AuthTokenResponse:
    """Register an instructor account, gated by an institution-issued code.

    Faculty accounts cannot be self-service. Without this gate the
    role-escalation hole closed in Phase 1 reopens as an open teacher signup:
    the role would still not come from the request body, but anyone could
    obtain one anyway.
    """
    code_repo = FacultyCodeRepository()
    code = code_repo.find_usable(hash_token(payload.registration_code))

    # One generic message for every rejection - wrong code, exhausted code,
    # expired code - so the endpoint cannot be used to probe which codes exist.
    invalid = PermissionDeniedError("That registration code is not valid.")

    if not code:
        logger.warning(f"Faculty registration attempted with an unrecognised code for {payload.email}")
        raise invalid
    if code["use_count"] >= code["max_uses"]:
        raise invalid
    if code.get("expires_at") and is_expired(code["expires_at"]):
        raise invalid

    supabase = get_supabase_anon_client()
    try:
        auth_response = supabase.auth.sign_up(
            {
                "email": payload.email,
                "password": payload.password,
                "options": {"data": {"full_name": payload.full_name}},
            }
        )
    except Exception as exc:
        logger.warning(f"Faculty registration rejected for {payload.email}: {exc.__class__.__name__}")
        raise ConflictError("Unable to complete registration with the details provided.") from exc

    if not auth_response.user:
        raise ConflictError("Unable to complete registration with the details provided.")

    user_id = str(auth_response.user.id)

    # TEACHER is assigned here, by the server, only because a valid code was
    # presented. It is never read from the request.
    profile = user_repo.ensure_profile(
        user_id=user_id,
        email=payload.email,
        role=UserRole.TEACHER.value,
        full_name=payload.full_name,
    )
    code_repo.consume(code["id"], code["use_count"], code["max_uses"])

    audit.record(
        action=audit.AuditAction.ROLE_CHANGED,
        resource="profile",
        actor_id=user_id,
        actor_role=UserRole.TEACHER.value,
        resource_id=user_id,
        subject_id=user_id,
        details={"granted_role": "TEACHER", "via": "faculty_registration_code", "code_id": code["id"]},
    )

    if not auth_response.session:
        raise AuthenticationError(
            "Account created. Check your email to confirm your address before signing in."
        )

    access_token, refresh_token, expires_in = _session_payload(auth_response)
    return AuthTokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        user_id=user_id,
        email=profile["email"],
        role=UserRole(profile["role"]),
        full_name=profile.get("full_name"),
    )


@router.post("/login", response_model=AuthTokenResponse, dependencies=[_auth_limit])
async def login(payload: UserLoginRequest) -> AuthTokenResponse:
    supabase = get_supabase_anon_client()

    try:
        auth_response = supabase.auth.sign_in_with_password(
            {"email": payload.email, "password": payload.password}
        )
    except Exception as exc:
        logger.info(f"Failed login for {payload.email}: {exc.__class__.__name__}")
        raise AuthenticationError(_GENERIC_AUTH_FAILURE) from exc

    if not auth_response.user or not auth_response.session:
        raise AuthenticationError(_GENERIC_AUTH_FAILURE)

    user_id = str(auth_response.user.id)

    # The profile row is authoritative for role. ensure_profile creates a
    # least-privileged row if one is somehow missing, but never rewrites the
    # role of an existing one - otherwise a login could silently downgrade a
    # teacher, or be used to reset a role.
    profile = user_repo.ensure_profile(
        user_id=user_id,
        email=payload.email,
        role=UserRole.STUDENT.value,
        full_name=(auth_response.user.user_metadata or {}).get("full_name"),
    )

    if not profile.get("is_active", True):
        raise AuthenticationError("This account has been deactivated.")

    access_token, refresh_token, expires_in = _session_payload(auth_response)

    return AuthTokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        user_id=user_id,
        email=profile["email"],
        role=UserRole(profile["role"]),
        full_name=profile.get("full_name"),
    )


@router.post("/refresh", response_model=AuthTokenResponse, dependencies=[_auth_limit])
async def refresh_session(payload: RefreshTokenRequest) -> AuthTokenResponse:
    """Exchange a refresh token for a new access token.

    Supabase rotates the refresh token on each use and invalidates the whole
    family if a consumed token is replayed, which is what makes token theft
    detectable rather than silently persistent.
    """
    supabase = get_supabase_anon_client()

    try:
        auth_response = supabase.auth.refresh_session(payload.refresh_token)
    except Exception as exc:
        logger.info(f"Refresh rejected: {exc.__class__.__name__}")
        raise AuthenticationError("Session expired. Please sign in again.") from exc

    if not auth_response.user or not auth_response.session:
        raise AuthenticationError("Session expired. Please sign in again.")

    user_id = str(auth_response.user.id)
    profile = user_repo.get_by_id(user_id)
    if not profile:
        raise AuthenticationError("Session expired. Please sign in again.")
    if not profile.get("is_active", True):
        raise AuthenticationError("This account has been deactivated.")

    access_token, refresh_token, expires_in = _session_payload(auth_response)

    return AuthTokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        user_id=user_id,
        email=profile["email"],
        role=UserRole(profile["role"]),
        full_name=profile.get("full_name"),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: RefreshTokenRequest) -> None:
    """Revoke the supplied refresh token.

    Always returns 204: whether the token was already invalid is not useful to
    the caller and confirming it would leak token validity.
    """
    supabase = get_supabase_anon_client()
    try:
        supabase.auth.admin.sign_out(payload.refresh_token)
    except Exception as exc:  # noqa: BLE001 - revocation is best-effort
        logger.info(f"Logout revocation no-op: {exc.__class__.__name__}")


@router.get("/me", response_model=AuthenticatedUserResponse)
async def get_me(current_user: UserProfileDB = Depends(get_current_user)) -> AuthenticatedUserResponse:
    """Return the caller's server-resolved identity and role.

    The frontend must use this rather than trusting a role cached at login -
    a role changed or revoked server-side takes effect on the next call.
    """
    return AuthenticatedUserResponse(
        user_id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
    )
