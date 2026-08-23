from typing import Any, Dict, List, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from app.config import get_settings
from app.core.exceptions import DatabaseConnectionError
from app.core.logging import get_logger

logger = get_logger("qdrant_cloud")
settings = get_settings()

_qdrant_client: Optional[QdrantClient] = None


def get_qdrant_client() -> QdrantClient:
    """
    Returns the singleton QdrantClient initialized for Qdrant Cloud.
    """
    global _qdrant_client
    if _qdrant_client is None:
        try:
            _qdrant_client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
                timeout=20,
            )
            logger.info("Initialized Qdrant Cloud Client.")
        except Exception as exc:
            logger.error(f"Failed to connect to Qdrant Cloud: {exc}")
            raise DatabaseConnectionError("Qdrant Cloud", str(exc)) from exc
    return _qdrant_client


def ensure_collection_exists(
    collection_name: str,
    vector_size: int = 384,
    distance: qmodels.Distance = qmodels.Distance.COSINE
) -> None:
    """
    Checks if a Qdrant collection exists; if not, creates it with specified dimensions.
    """
    client = get_qdrant_client()
    collections_response = client.get_collections()
    existing = [col.name for col in collections_response.collections]
    
    if collection_name not in existing:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=qmodels.VectorParams(
                size=vector_size,
                distance=distance,
            ),
        )
        logger.info(f"Created Qdrant Collection '{collection_name}' with dimension {vector_size}.")


def check_qdrant_health() -> bool:
    """
    Health check query for Qdrant Cloud.
    """
    try:
        client = get_qdrant_client()
        res = client.get_collections()
        return res is not None
    except Exception as exc:
        logger.error(f"Qdrant health check failed: {exc}")
        return False