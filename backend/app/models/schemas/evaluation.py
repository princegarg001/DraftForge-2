from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict
from app.core.constants import FindingCategory, FindingStatus


class EvaluationFindingResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: Optional[str] = None
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


class EvaluationResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    draft_version_id: str
    overall_score: float
    max_score: float = 100.0
    structure_score: float
    clause_score: float
    formatting_score: float
    gap_penalty: float = 0.0
    rubric_version: str
    llm_explanation: Optional[str] = None
    is_overridden: bool = False
    overridden_score: Optional[float] = None
    created_at: Optional[Any] = None
    evidence_items: List[EvaluationFindingResponse] = []


class EvaluateDraftRequest(BaseModel):
    draft_id: str
    version_number: Optional[int] = None