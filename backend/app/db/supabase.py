from supabase import Client, create_client
from app.config import get_settings
from app.core.exceptions import DatabaseConnectionError
from app.core.logging import get_logger

logger = get_logger("supabase_client")
settings = get_settings()

_supabase_admin_client: Client | None = None
_supabase_anon_client: Client | None = None


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


def get_user_scoped_client(access_token: str) -> Client:
    """Return a client that acts *as the calling user*, so RLS applies.

    The admin client used by the repositories carries the service-role key,
    which is BYPASSRLS by design - every policy in migration 005 is inert on
    that connection. A client built from the anon key and the caller's own JWT
    is subject to those policies, making the database a real second line of
    defence rather than a decorative one.

    A fresh client is constructed per call rather than mutating a shared one's
    auth header: the header is connection-wide state, so reusing one instance
    across concurrent requests would let one user's token serve another's
    query.
    """
    if not access_token:
        raise ValueError("access_token is required to build a user-scoped client.")

    try:
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
        client.postgrest.auth(access_token)
        return client
    except Exception as exc:
        logger.error(f"Failed to build user-scoped Supabase client: {exc.__class__.__name__}")
        raise DatabaseConnectionError("Supabase", str(exc)) from exc


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