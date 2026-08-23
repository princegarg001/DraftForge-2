import time
from typing import Any, Dict, List, Optional
from neo4j import GraphDatabase, Driver
from neo4j.exceptions import SessionExpired, ServiceUnavailable
from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger("neo4j_db")
settings = get_settings()

_neo4j_driver: Optional[Driver] = None


def get_neo4j_driver() -> Driver:
    global _neo4j_driver
    if _neo4j_driver is None:
        _neo4j_driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
            max_connection_lifetime=30 * 60,
            max_connection_pool_size=50,
            connection_acquisition_timeout=60,
            liveness_check_timeout=1.0,
            keep_alive=True
        )
        logger.info("Initialized Neo4j Driver with keep-alive & liveness checks.")
    return _neo4j_driver


def close_neo4j_driver():
    global _neo4j_driver
    if _neo4j_driver is not None:
        _neo4j_driver.close()
        _neo4j_driver = None
        logger.info("Closed Neo4j Driver.")


def check_neo4j_health() -> bool:
    """Checks the health and connectivity of the Neo4j instance."""
    try:
        driver = get_neo4j_driver()
        with driver.session() as session:
            result = session.run("RETURN 1 AS status")
            record = result.single()
            return record is not None and record["status"] == 1
    except Exception as exc:
        logger.error(f"Neo4j health check failed: {exc}")
        return False


def execute_cypher_read(query: str, parameters: Optional[Dict[str, Any]] = None, retries: int = 2) -> List[Dict[str, Any]]:
    """Executes a Cypher read query with automatic session retry on dropped/expired connections."""
    driver = get_neo4j_driver()
    last_exc = None

    for attempt in range(retries + 1):
        try:
            with driver.session() as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except (SessionExpired, ServiceUnavailable, ConnectionResetError) as exc:
            last_exc = exc
            logger.warning(f"Neo4j connection dropped on read attempt {attempt + 1}. Reconnecting... ({exc})")
            time.sleep(0.5)

    logger.error(f"Neo4j read query failed after {retries} retries: {last_exc}")
    return []


def execute_cypher_write(query: str, parameters: Optional[Dict[str, Any]] = None, retries: int = 2) -> List[Dict[str, Any]]:
    """Executes a Cypher write query with automatic session retry."""
    driver = get_neo4j_driver()
    last_exc = None

    for attempt in range(retries + 1):
        try:
            with driver.session() as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except (SessionExpired, ServiceUnavailable, ConnectionResetError) as exc:
            last_exc = exc
            logger.warning(f"Neo4j connection dropped on write attempt {attempt + 1}. Reconnecting... ({exc})")
            time.sleep(0.5)

    logger.error(f"Neo4j write query failed after {retries} retries: {last_exc}")
    return []