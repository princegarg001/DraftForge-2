from typing import Any, Dict, List
from app.ai.graph.queries.risk_queries import (
    GET_ALL_RISKS_FOR_DOCTYPE,
    GET_RISKS_FOR_MISSING_CLAUSES,
)
from app.core.constants import DocumentType
from app.db.neo4j import execute_cypher_read


class RiskGraph:
    """Manages risk mappings and unmitigated exposure checks."""

    @staticmethod
    def get_risks_for_missing_clauses(missing_clause_ids: List[str]) -> List[Dict[str, Any]]:
        if not missing_clause_ids:
            return []
        return execute_cypher_read(
            GET_RISKS_FOR_MISSING_CLAUSES,
            {"missing_clause_ids": missing_clause_ids}
        )

    @staticmethod
    def get_all_risks(doc_type: DocumentType) -> List[Dict[str, Any]]:
        return execute_cypher_read(
            GET_ALL_RISKS_FOR_DOCTYPE,
            {"document_type": doc_type.value}
        )