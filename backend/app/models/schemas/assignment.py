from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from app.core.constants import DocumentType


class AssignmentCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    document_type: DocumentType
    instructions: str
    deadline: Optional[datetime] = None
    rubric_override: Optional[Dict[str, Any]] = None


class AssignmentResponse(BaseModel):
    id: str
    teacher_id: str
    title: str
    description: Optional[str] = None
    document_type: DocumentType
    instructions: str
    deadline: Optional[datetime] = None
    status: str
    created_at: datetime
    updated_at: datetime
    submissions_count: Optional[int] = 0