from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict
from app.core.constants import DocumentType


class DraftVersionResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    draft_id: str
    version_number: int
    raw_content: str
    storage_path: Optional[str] = None
    file_hash: Optional[str] = None
    created_at: Optional[Any] = None


class DraftCreateRequest(BaseModel):
    title: str
    document_type: Optional[DocumentType] = None
    raw_content: str


class DraftResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    user_id: str
    document_type: DocumentType
    title: str
    status: str
    created_at: Optional[Any] = None
    updated_at: Optional[Any] = None
    versions: List[DraftVersionResponse] = []


class VersionCompareResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    draft_id: str
    v1_number: int
    v2_number: int
    additions: int
    deletions: int
    diff_summary: str