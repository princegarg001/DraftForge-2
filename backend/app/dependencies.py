from typing import Dict, Any
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.constants import UserRole
from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.core.security import verify_supabase_jwt
from app.db.repositories.user_repository import UserRepository
from app.models.database.models import UserProfileDB

security_bearer = HTTPBearer(auto_error=True)
user_repo = UserRepository()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
) -> UserProfileDB:
    token = credentials.credentials
    payload = verify_supabase_jwt(token)
    
    user_id: str = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid JWT token: subject claim 'sub' missing")
    
    # Retrieve user from the PostgreSQL database
    profile_data = user_repo.get_by_id(user_id)
    if not profile_data:
        # If user registered in Supabase Auth but profile doesn't exist yet, construct profile from token
        email = payload.get("email", "")
        role_claim = payload.get("user_metadata", {}).get("role", UserRole.STUDENT.value)
        profile_data = user_repo.upsert_profile(
            user_id=user_id,
            email=email,
            role=role_claim,
            full_name=payload.get("user_metadata", {}).get("full_name")
        )

    return UserProfileDB(**profile_data)


def require_role(allowed_roles: list[UserRole]):
    def role_checker(current_user: UserProfileDB = Depends(get_current_user)) -> UserProfileDB:
        if current_user.role not in allowed_roles:
            raise PermissionDeniedError(
                f"Operation restricted to roles: {[r.value for r in allowed_roles]}. Current role: {current_user.role.value}"
            )
        return current_user
    return role_checker


require_student = require_role([UserRole.STUDENT, UserRole.ADMIN])
require_teacher = require_role([UserRole.TEACHER, UserRole.ADMIN])
require_admin = require_role([UserRole.ADMIN])