from typing import Any, Dict, List
from app.ai.graph.clause_graph import ClauseGraph
from app.ai.graph.risk_graph import RiskGraph
from app.ai.graph.skill_graph import SkillGraph
from app.core.constants import DocumentType


class GraphRetriever:
    """Unified access point for GraphRAG retrieval operations."""

    def __init__(self):
        self.clause_graph = ClauseGraph()
        self.risk_graph = RiskGraph()
        self.skill_graph = SkillGraph()

    def get_document_topology(self, doc_type: DocumentType) -> Dict[str, Any]:
        return {
            "dependencies": self.clause_graph.get_dependencies_for_doctype(doc_type),
            "risks": self.risk_graph.get_all_risks(doc_type),
        }

    def get_unmitigated_risks(self, missing_clause_ids: List[str]) -> List[Dict[str, Any]]:
        return self.risk_graph.get_risks_for_missing_clauses(missing_clause_ids)

    def get_skill_mappings(self, clause_ids: List[str]) -> List[Dict[str, Any]]:
        return self.skill_graph.get_skills_for_clauses(clause_ids)