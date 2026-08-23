from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class GraphClauseNode(BaseModel):
    clause_id: str
    name: str
    document_type: str
    description: str
    is_mandatory: bool = True


class GraphRiskNode(BaseModel):
    risk_id: str
    name: str
    severity: str  # HIGH, MEDIUM, LOW
    description: str


class GraphSkillNode(BaseModel):
    skill_id: str
    name: str
    category: str
    description: str


class ClauseDependency(BaseModel):
    source_clause_id: str
    source_clause_name: str
    target_clause_id: str
    target_clause_name: str
    relationship_type: str = "DEPENDS_ON"
    reason: str


class LoopholeFinding(BaseModel):
    finding_id: str
    title: str
    severity: str  # HIGH, MEDIUM, LOW
    gap_type: str  # "MISSING_DEPENDENCY", "UNMITIGATED_RISK", "STRUCTURAL_OMISSION"
    related_clause_id: Optional[str] = None
    related_clause_name: Optional[str] = None
    prerequisite_clause_id: Optional[str] = None
    prerequisite_clause_name: Optional[str] = None
    risk_name: Optional[str] = None
    skill_id: Optional[str] = None
    skill_name: Optional[str] = None
    educational_observation: str
    reference_recommendation: str