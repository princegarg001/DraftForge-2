from app.ai.graph.queries.clause_queries import INIT_CONSTRAINTS
from app.core.logging import get_logger
from app.db.neo4j import execute_cypher_write

logger = get_logger("graph_schema_init")


def initialize_graph_constraints() -> None:
    """Creates uniqueness constraints and indexes on Neo4j Aura."""
    logger.info("Initializing Neo4j Aura schema constraints...")
    statements = [stmt.strip() for stmt in INIT_CONSTRAINTS.split(";") if stmt.strip()]
    for stmt in statements:
        try:
            execute_cypher_write(stmt)
        except Exception as exc:
            logger.warning(f"Constraint setup notice (may already exist): {exc}")
    logger.info("Neo4j Aura schema constraints initialized.")