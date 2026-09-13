from fastapi import APIRouter, Depends

from app.config import get_settings
from app.core.rate_limit import LimitScope, RateLimit
from app.core.redis_client import check_redis_health
from app.db.neo4j import check_neo4j_health
from app.db.qdrant import check_qdrant_health
from app.db.supabase import check_supabase_health
from app.dependencies import get_current_user
from app.models.schemas.health import HealthCheckResponse, ServiceStatus

router = APIRouter(tags=["Health & Telemetry"])
settings = get_settings()


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    # Authenticated: this probes four backing services on each call, so
    # unauthenticated access is both an amplification vector and a readout of
    # which dependencies are currently down. The unauthenticated liveness probe
    # is GET / health at the application root.
    dependencies=[Depends(get_current_user), Depends(RateLimit(LimitScope.DEFAULT))],
)
async def health_check() -> HealthCheckResponse:
    """Report connectivity to Supabase, Qdrant, Neo4j and Redis."""
    supabase_ok = check_supabase_health()
    qdrant_ok = check_qdrant_health()
    neo4j_ok = check_neo4j_health()
    redis_ok = await check_redis_health()

    return HealthCheckResponse(
        status="healthy" if all((supabase_ok, qdrant_ok, neo4j_ok, redis_ok)) else "degraded",
        app_version=settings.APP_VERSION,
        services={
            "supabase_postgresql": ServiceStatus(
                reachable=supabase_ok,
                details="Connected" if supabase_ok else "Unreachable",
            ),
            "qdrant_cloud": ServiceStatus(
                reachable=qdrant_ok,
                details="Connected" if qdrant_ok else "Unreachable",
            ),
            "neo4j_aura": ServiceStatus(
                reachable=neo4j_ok,
                details="Connected" if neo4j_ok else "Unreachable",
            ),
            "redis": ServiceStatus(
                reachable=redis_ok,
                details="Connected" if redis_ok else "Unreachable",
            ),
        },
    )
