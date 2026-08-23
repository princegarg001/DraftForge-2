import sys
from pathlib import Path

# Ensure root backend directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from app.ai.graph.schema_init import initialize_graph_constraints
from app.ai.graph.seed_knowledge import seed_knowledge_graph
from app.core.logging import get_logger

logger = get_logger("seed_script")

if __name__ == "__main__":
    logger.info("Initializing Neo4j Aura Graph Schema...")
    initialize_graph_constraints()
    logger.info("Seeding Initial Knowledge Graph...")
    seed_knowledge_graph()
    logger.info("Seeding completed successfully.")