from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict
from app.core.constants import DocumentType


class ReferenceDocumentResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    title: str
    document_type: DocumentType
    jurisdiction: str
    storage_path: str
    file_size_bytes: int
    file_hash: str
    mime_type: str
    uploaded_by: Optional[str] = None
    created_at: Optional[Any] = None


class DocumentClassificationResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    detected_type: DocumentType
    confidence: float
    summary: str