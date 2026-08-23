from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.core.constants import DocumentType


class ReferenceDocumentResponse(BaseModel):
    id: str
    title: str
    document_type: DocumentType
    jurisdiction: str
    storage_path: str
    file_size_bytes: int
    file_hash: str
    mime_type: str
    uploaded_by: Optional[str] = None
    created_at: datetime


class DocumentClassificationResult(BaseModel):
    detected_type: DocumentType
    confidence: float
    summary: str