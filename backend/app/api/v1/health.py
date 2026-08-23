from fastapi import APIRouter
from app.config import get_settings
from app.db.neo4j import check_neo4j_health
from app.db.qdrant import check_qdrant_health
from app.db.supabase import check_supabase_health
from app.models.schemas.health import HealthCheckResponse, ServiceStatus

router = APIRouter(tags=["Health & Telemetry"])
settings = get_settings()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Validates end-to-end connectivity with Supabase Postgres, Qdrant Cloud, and Neo4j Aura.
    """
    supabase_ok = check_supabase_health()
    qdrant_ok = check_qdrant_health()
    neo4j_ok = check_neo4j_health()

    all_healthy = supabase_ok and qdrant_ok and neo4j_ok

    return HealthCheckResponse(
        status="healthy" if all_healthy else "degraded",
        app_version=settings.APP_VERSION,
        services={
            "supabase_postgresql": ServiceStatus(
                reachable=supabase_ok,
                details="Connected to PostgreSQL & Profiles table verified" if supabase_ok else "Failed to query database"
            ),
            "qdrant_cloud": ServiceStatus(
                reachable=qdrant_ok,
                details="Connected to Qdrant cluster & collections verified" if qdrant_ok else "Cluster unreachable or auth invalid"
            ),
            "neo4j_aura": ServiceStatus(
                reachable=neo4j_ok,
                details="Active connection to Neo4j Aura Graph verified" if neo4j_ok else "Session handshake or Cypher query failed"
            ),
        }
    )