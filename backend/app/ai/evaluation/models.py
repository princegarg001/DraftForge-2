from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.core.constants import FindingCategory, FindingStatus


class EvaluationFinding(BaseModel):
    category: FindingCategory
    criterion: str
    status: FindingStatus
    score: float
    max_score: float
    student_evidence: Optional[str] = None
    reference_evidence: Optional[str] = None
    source_document: Optional[str] = None
    source_page: Optional[int] = None
    source_section: Optional[str] = None
    explanation: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RubricConfig(BaseModel):
    document_type: str
    jurisdiction: str = "India"
    max_score: float = 100.0
    weights: Dict[str, float]
    penalties: Dict[str, float]
    required_sections: List[Dict[str, Any]]
    mandatory_clauses: List[Dict[str, Any]]


class EvaluationResult(BaseModel):
    overall_score: float
    max_score: float = 100.0
    structure_score: float
    clause_score: float
    formatting_score: float
    gap_penalty: float = 0.0
    rubric_version: str
    findings: List[EvaluationFinding] = Field(default_factory=list)