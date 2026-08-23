from typing import Any, Dict
from app.core.exceptions import AuthenticationError
from app.db.supabase import get_supabase_anon_client
from app.core.logging import get_logger

logger = get_logger("security")


def verify_supabase_jwt(token: str) -> Dict[str, Any]:
    """
    Verifies the Supabase Auth access token using the Supabase client.
    Returns user claims if valid.
    """
    if not token or not token.strip():
        raise AuthenticationError("Bearer token is missing or empty.")

    try:
        supabase = get_supabase_anon_client()
        # Verify directly against Supabase Auth
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise AuthenticationError("Invalid or expired session token.")

        user = user_response.user
        return {
            "sub": str(user.id),
            "email": user.email,
            "user_metadata": user.user_metadata or {},
        }
    except Exception as exc:
        logger.error(f"Supabase JWT verification failed: {exc}")
        raise AuthenticationError(f"Authentication failed: {str(exc)}") from exc