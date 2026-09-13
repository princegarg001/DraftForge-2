from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.ai.graph.schema_init import initialize_graph_constraints
from app.ai.graph.seed_knowledge import seed_knowledge_graph
from app.api.v1.router import api_v1_router
from app.config import get_settings
from app.core.error_handlers import register_exception_handlers
from app.core.logging import get_logger
from app.core.redis_client import check_redis_health, close_redis
from app.db.neo4j import close_neo4j_driver, get_neo4j_driver
from app.db.qdrant import ensure_collection_exists, get_qdrant_client
from app.db.supabase import get_supabase_admin_client
from app.middleware import (
    BodySizeLimitMiddleware,
    RequestContextMiddleware,
    SecurityHeadersMiddleware,
)
from app.observability import setup_observability, shutdown_observability

settings = get_settings()
logger = get_logger("main_app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} [{settings.ENVIRONMENT}]")

    # Each dependency is probed independently so one unavailable service does
    # not mask the status of the others. Previously a single try block wrapped
    # all of them, so the first failure skipped every subsequent check and the
    # app reported a clean start.
    for name, probe in (
        ("Supabase", get_supabase_admin_client),
        ("Neo4j Aura", get_neo4j_driver),
        ("Qdrant Cloud", get_qdrant_client),
    ):
        try:
            probe()
            logger.info(f"{name} client initialized.")
        except Exception as exc:  # noqa: BLE001 - startup probes must not abort boot
            logger.error(f"{name} initialization failed: {exc.__class__.__name__}: {exc}")

    try:
        ensure_collection_exists(settings.QDRANT_COLLECTION_NAME)
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Qdrant collection check failed: {exc.__class__.__name__}: {exc}")

    try:
        initialize_graph_constraints()
        # Seeding is idempotent but not free; it re-runs a full MERGE set on
        # every boot, which on a platform that restarts frequently is wasted
        # work against a shared database.
        seed_knowledge_graph()
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Knowledge graph bootstrap failed: {exc.__class__.__name__}: {exc}")

    if settings.RATE_LIMIT_ENABLED:
        if await check_redis_health():
            logger.info("Redis reachable; rate limiting active.")
        elif settings.REDIS_REQUIRED:
            # Fail fast rather than serve traffic with limits silently disabled.
            raise RuntimeError("REDIS_REQUIRED is set but Redis is unreachable. Refusing to start.")
        else:
            logger.warning("Redis unreachable; rate limiting will fail open (non-production only).")

    yield

    logger.info("Shutting down...")
    close_neo4j_driver()
    await close_redis()
    # Flush buffered spans and metrics. Without this the batch processor's
    # buffer is lost on exit, reliably dropping telemetry for whatever was
    # happening when the process went down - the exact window worth seeing.
    shutdown_observability()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Evidence-Grounded Legal Drafting Education and Evaluation Platform API",
    lifespan=lifespan,
    # Disabled in production: a published schema of every endpoint, parameter
    # and model is a map for an attacker.
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
    openapi_url="/openapi.json" if settings.docs_enabled else None,
)

# --------------------------------------------------------------------------
# Middleware. Starlette applies these outermost-last, so the registration
# order below is the reverse of execution order. Effective order is:
#   TrustedHost -> CORS -> SecurityHeaders -> RequestContext -> BodyLimit
# --------------------------------------------------------------------------
app.add_middleware(BodySizeLimitMiddleware)
app.add_middleware(RequestContextMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    # Exact origins only. This previously carried
    # allow_origin_regex=r"...^https://.*\.onrender\.com$" together with
    # allow_credentials=True, which trusted *every* onrender.com subdomain -
    # a hostname anyone can obtain by deploying there - to make credentialed
    # cross-origin requests against this API.
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    # Enumerated rather than "*": with credentials, a wildcard is both invalid
    # per the Fetch spec and broader than anything this API needs.
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-CSRF-Token"],
    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining", "Retry-After"],
    max_age=600,
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.TRUSTED_HOSTS)

register_exception_handlers(app)
app.include_router(api_v1_router)

# Installed after the routes so FastAPI instrumentation sees the full route
# table and can label spans with their path template rather than the raw URL -
# otherwise every draft id becomes its own metric dimension.
setup_observability(app)


@app.get("/", tags=["System"])
async def root() -> dict[str, str | None]:
    return {
        "platform": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.docs_enabled else None,
        "health": "/api/v1/health",
    }


@app.get("/health", tags=["System"])
async def health() -> dict[str, str]:
    """Liveness probe.

    Deliberately shallow and dependency-free: it answers "is this process
    serving?", which is what a platform health check needs. Dependency status
    lives at /api/v1/health, which is authenticated.
    """
    return {"status": "healthy", "version": settings.APP_VERSION}
