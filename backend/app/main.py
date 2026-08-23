from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.ai.graph.schema_init import initialize_graph_constraints
from app.ai.graph.seed_knowledge import seed_knowledge_graph
from app.api.v1.router import api_v1_router
from app.config import get_settings
from app.core.logging import get_logger
from app.db.neo4j import close_neo4j_driver, get_neo4j_driver
from app.db.qdrant import ensure_collection_exists, get_qdrant_client
from app.db.supabase import get_supabase_admin_client

settings = get_settings()
logger = get_logger("main_app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Sequence
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} [{settings.ENVIRONMENT}]")
    try:
        get_supabase_admin_client()
        get_neo4j_driver()
        get_qdrant_client()
        ensure_collection_exists(settings.QDRANT_COLLECTION_NAME)
        # Ensure Graph Constraints & Seed Topology
        initialize_graph_constraints()
        seed_knowledge_graph()
        logger.info("All managed cloud services (Supabase, Neo4j Aura, Qdrant Cloud) initialized.")
    except Exception as exc:
        logger.error(f"Startup check failed: {exc}")
    yield
    # Shutdown Sequence
    logger.info("Shutting down application...")
    close_neo4j_driver()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Evidence-Grounded Legal Drafting Education and Evaluation Platform API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$|^https://.*\.onrender\.com$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(api_v1_router)


@app.get("/")
async def root():
    return {
        "platform": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/v1/health"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }