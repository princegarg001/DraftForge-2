from typing import List
from app.ai.graph.models import ClauseDependency
from app.ai.graph.queries.clause_queries import (
    GET_CLAUSE_DEPENDENCIES_BY_DOCTYPE,
    GET_PREREQUISITES_FOR_CLAUSE,
)
from app.core.constants import DocumentType
from app.db.neo4j import execute_cypher_read


class ClauseGraph:
    """Manages clause relationship and dependency traversals in Neo4j."""

    @staticmethod
    def get_dependencies_for_doctype(doc_type: DocumentType) -> List[ClauseDependency]:
        records = execute_cypher_read(
            GET_CLAUSE_DEPENDENCIES_BY_DOCTYPE,
            {"document_type": doc_type.value}
        )
        dependencies: List[ClauseDependency] = []
        for r in records:
            if r.get("target_id"):
                dependencies.append(
                    ClauseDependency(
                        source_clause_id=r["source_id"],
                        source_clause_name=r["source_name"],
                        target_clause_id=r["target_id"],
                        target_clause_name=r["target_name"],
                        reason=r.get("reason") or "Prerequisite relationship"
                    )
                )
        return dependencies

    @staticmethod
    def get_prerequisites(clause_id: str) -> List[dict]:
        return execute_cypher_read(GET_PREREQUISITES_FOR_CLAUSE, {"clause_id": clause_id})