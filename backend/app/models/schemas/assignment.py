from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict
from app.core.constants import DocumentType


class AssignmentCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    document_type: DocumentType
    instructions: str
    deadline: Optional[datetime] = None
    rubric_override: Optional[Dict[str, Any]] = None


class AssignmentResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    teacher_id: str
    title: str
    description: Optional[str] = None
    document_type: DocumentType
    instructions: str
    deadline: Optional[Any] = None
    status: str
    created_at: Optional[Any] = None
    updated_at: Optional[Any] = None
    submissions_count: Optional[int] = 0