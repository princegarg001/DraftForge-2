from typing import List, Optional
from pydantic import BaseModel


class LoopholeFindingResponse(BaseModel):
    finding_id: str
    title: str
    severity: str
    gap_type: str
    related_clause_id: Optional[str] = None
    related_clause_name: Optional[str] = None
    prerequisite_clause_id: Optional[str] = None
    prerequisite_clause_name: Optional[str] = None
    risk_name: Optional[str] = None
    skill_id: Optional[str] = None
    skill_name: Optional[str] = None
    educational_observation: str
    reference_recommendation: str


class LoopholeAnalysisResponse(BaseModel):
    evaluation_id: str
    document_type: str
    total_loopholes: int
    high_severity_count: int
    loopholes: List[LoopholeFindingResponse]