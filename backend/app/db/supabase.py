from supabase import Client, create_client
from app.config import get_settings
from app.core.exceptions import DatabaseConnectionError
from app.core.logging import get_logger

logger = get_logger("supabase_client")
settings = get_settings()

_supabase_admin_client: Client = None
_supabase_anon_client: Client = None


def get_supabase_admin_client() -> Client:
    """
    Returns the Supabase client initialized with the SERVICE_ROLE key.
    Used exclusively in backend operations requiring elevated administrative privileges.
    """
    global _supabase_admin_client
    if _supabase_admin_client is None:
        try:
            _supabase_admin_client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_ROLE_KEY,
            )
            logger.info("Initialized Supabase Admin Client.")
        except Exception as exc:
            logger.error(f"Failed to initialize Supabase Admin Client: {exc}")
            raise DatabaseConnectionError("Supabase Admin", str(exc)) from exc
    return _supabase_admin_client


def get_supabase_anon_client() -> Client:
    """
    Returns the public Supabase client initialized with the ANON key.
    """
    global _supabase_anon_client
    if _supabase_anon_client is None:
        try:
            _supabase_anon_client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_ANON_KEY,
            )
            logger.info("Initialized Supabase Anon Client.")
        except Exception as exc:
            logger.error(f"Failed to initialize Supabase Anon Client: {exc}")
            raise DatabaseConnectionError("Supabase Anon", str(exc)) from exc
    return _supabase_anon_client


def check_supabase_health() -> bool:
    """
    Verifies that the Supabase client can contact the database.
    """
    try:
        client = get_supabase_admin_client()
        # Query the profiles table with limit 1
        response = client.table("profiles").select("id").limit(1).execute()
        return response is not None
    except Exception as exc:
        logger.error(f"Supabase health check failed: {exc}")
        return False