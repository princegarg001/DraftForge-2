from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.core.constants import DocumentType, FindingCategory, FindingStatus, UserRole


class UserProfileDB(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    email: str
    role: UserRole = UserRole.STUDENT
    full_name: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[Any] = None
    updated_at: Optional[Any] = None


class ReferenceDocumentDB(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    title: str
    document_type: DocumentType
    jurisdiction: str = "India"
    storage_path: str
    file_size_bytes: int
    file_hash: str
    mime_type: str
    uploaded_by: Optional[str] = None
    created_at: Optional[Any] = None


class DraftDB(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    user_id: str
    document_type: DocumentType
    title: str
    status: str
    created_at: Optional[Any] = None
    updated_at: Optional[Any] = None


class DraftVersionDB(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    draft_id: str
    version_number: int
    raw_content: str
    storage_path: Optional[str] = None
    file_hash: Optional[str] = None
    created_at: Optional[Any] = None


class EvaluationEvidenceDB(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    evaluation_id: str
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
    created_at: Optional[Any] = None


class EvaluationDB(BaseModel):
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
    overridden_by: Optional[str] = None
    override_reason: Optional[str] = None
    created_at: Optional[Any] = None
    evidence_items: List[EvaluationEvidenceDB] = Field(default_factory=list)