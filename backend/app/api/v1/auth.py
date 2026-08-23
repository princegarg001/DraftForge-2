from fastapi import APIRouter, status
from app.core.exceptions import AuthenticationError
from app.db.repositories.user_repository import UserRepository
from app.db.supabase import get_supabase_anon_client
from app.models.schemas.auth import AuthTokenResponse, UserLoginRequest, UserRegisterRequest
from app.core.logging import get_logger

logger = get_logger("auth_router")
router = APIRouter(prefix="/auth", tags=["Authentication"])
user_repo = UserRepository()


@router.post("/register", response_model=AuthTokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegisterRequest):
    """
    Registers a new student or teacher account via Supabase Auth and registers profile in PostgreSQL.
    """
    supabase = get_supabase_anon_client()
    try:
        auth_response = supabase.auth.sign_up({
            "email": payload.email,
            "password": payload.password,
            "options": {
                "data": {
                    "role": payload.role.value,
                    "full_name": payload.full_name,
                }
            }
        })
    except Exception as exc:
        logger.error(f"Supabase registration error: {exc}")
        raise AuthenticationError(f"Registration failed: {str(exc)}") from exc

    if not auth_response.user or not auth_response.session:
        raise AuthenticationError("User created but authentication session could not be established.")

    user_id = str(auth_response.user.id)
    profile = user_repo.upsert_profile(
        user_id=user_id,
        email=payload.email,
        role=payload.role.value,
        full_name=payload.full_name
    )

    return AuthTokenResponse(
        access_token=auth_response.session.access_token,
        user_id=user_id,
        email=profile["email"],
        role=profile["role"],
        full_name=profile.get("full_name"),
    )


@router.post("/login", response_model=AuthTokenResponse)
async def login(payload: UserLoginRequest):
    """
    Authenticates an existing user with Supabase Auth and returns JWT token.
    """
    supabase = get_supabase_anon_client()
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": payload.email,
            "password": payload.password,
        })
    except Exception as exc:
        logger.error(f"Supabase login error: {exc}")
        raise AuthenticationError("Invalid email or password.") from exc

    if not auth_response.user or not auth_response.session:
        raise AuthenticationError("Authentication failed.")

    user_id = str(auth_response.user.id)
    profile = user_repo.get_by_id(user_id)
    if not profile:
        profile = user_repo.upsert_profile(
            user_id=user_id,
            email=payload.email,
            role=auth_response.user.user_metadata.get("role", "STUDENT"),
            full_name=auth_response.user.user_metadata.get("full_name")
        )

    return AuthTokenResponse(
        access_token=auth_response.session.access_token,
        user_id=user_id,
        email=profile["email"],
        role=profile["role"],
        full_name=profile.get("full_name"),
    )