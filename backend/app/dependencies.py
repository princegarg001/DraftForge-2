"""Authentication and authorization dependencies.

The central rule enforced here: **a caller's role is read from the ``profiles``
table and nowhere else.**

Previously the role travelled with the token. ``user_metadata`` is populated
from the ``options.data`` block of a sign-up request, so it is attacker-
controlled - registering with ``role: "TEACHER"`` was enough to obtain
reference-document upload, cohort analytics and grade-override access. The
token is now trusted only to answer *who* the caller is (``sub``); *what they
may do* is resolved server-side on every request.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import lru_cache

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.constants import UserRole
from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.core.logging import get_logger
from app.core.security import TokenClaims, normalize_role, verify_supabase_jwt
from app.db.repositories.user_repository import UserRepository
from app.models.database.models import UserProfileDB

logger = get_logger("dependencies")

security_bearer = HTTPBearer(auto_error=True)
optional_bearer = HTTPBearer(auto_error=False)


@lru_cache
def _user_repo() -> UserRepository:
    # Constructed lazily: building it at import time forces a Supabase client
    # to be created before settings validation has necessarily run.
    return UserRepository()


async def get_token_claims(
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
) -> TokenClaims:
    return await verify_supabase_jwt(credentials.credentials)


async def get_current_user(
    request: Request,
    claims: TokenClaims = Depends(get_token_claims),
) -> UserProfileDB:
    repo = _user_repo()
    profile_data = repo.get_by_id(claims.sub)

    if not profile_data:
        # No profile yet. Provision a minimal one pinned to the least-privileged
        # role. app_metadata is writable only with the service-role key, so it
        # is the sole trusted elevation hint; user_metadata is ignored entirely.
        role = normalize_role(claims.claimed_role, default=UserRole.STUDENT)
        if role is UserRole.ADMIN:
            # Admin is never granted implicitly, even from app_metadata.
            role = UserRole.STUDENT
        logger.info(f"Provisioning profile for user {claims.sub} with role {role.value}")
        profile_data = repo.ensure_profile(
            user_id=claims.sub,
            email=claims.email or "",
            role=role.value,
            full_name=None,
        )

    profile = UserProfileDB(**profile_data)

    if not profile.is_active:
        raise PermissionDeniedError("This account has been deactivated.")

    # Expose identity to downstream middleware (audit logging, tracing) without
    # threading it through every call signature.
    request.state.user_id = profile.id
    request.state.user_role = profile.role.value
    return profile


async def get_optional_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_bearer),
) -> UserProfileDB | None:
    """Resolve the caller when a token is supplied, else ``None``.

    Used by endpoints that serve both authenticated and anonymous callers.
    An invalid token is still rejected - it is not silently downgraded to
    anonymous, which would let a caller with a revoked token keep partial access.
    """
    if credentials is None:
        return None
    claims = await verify_supabase_jwt(credentials.credentials)
    return await get_current_user(request=request, claims=claims)


def require_role(*allowed_roles: UserRole) -> Callable[..., UserProfileDB]:
    allowed = {role.value for role in allowed_roles}

    def role_checker(current_user: UserProfileDB = Depends(get_current_user)) -> UserProfileDB:
        if current_user.role.value not in allowed:
            logger.warning(
                f"Authorization denied: user={current_user.id} role={current_user.role.value} "
                f"required={sorted(allowed)}"
            )
            # The response does not name the required role - that detail only
            # helps an attacker map the permission model.
            raise PermissionDeniedError("You do not have permission to perform this action.")
        return current_user

    return role_checker


require_student = require_role(UserRole.STUDENT, UserRole.ADMIN)
require_teacher = require_role(UserRole.TEACHER, UserRole.ADMIN)
require_admin = require_role(UserRole.ADMIN)


def require_self_or_roles(*allowed_roles: UserRole) -> Callable[..., UserProfileDB]:
    """Permit access to one's own resources, or to holders of an elevated role."""
    allowed = {role.value for role in allowed_roles}

    def checker(
        user_id: str,
        current_user: UserProfileDB = Depends(get_current_user),
    ) -> UserProfileDB:
        if current_user.id != user_id and current_user.role.value not in allowed:
            raise PermissionDeniedError("You do not have permission to access this resource.")
        return current_user

    return checker


def require_bearer_subject(credentials: HTTPAuthorizationCredentials = Depends(security_bearer)) -> str:
    if not credentials.credentials:
        raise AuthenticationError("Bearer token is missing.")
    return credentials.credentials
