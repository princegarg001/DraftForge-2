from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.core.constants import DocumentType


class DraftVersionResponse(BaseModel):
    id: str
    draft_id: str
    version_number: int
    raw_content: str
    storage_path: Optional[str] = None
    file_hash: Optional[str] = None
    created_at: datetime


class DraftCreateRequest(BaseModel):
    title: str
    document_type: Optional[DocumentType] = None
    raw_content: str


class DraftResponse(BaseModel):
    id: str
    user_id: str
    document_type: DocumentType
    title: str
    status: str
    created_at: datetime
    updated_at: datetime
    versions: List[DraftVersionResponse] = []


class VersionCompareResponse(BaseModel):
    draft_id: str
    v1_number: int
    v2_number: int
    additions: int
    deletions: int
    diff_summary: str