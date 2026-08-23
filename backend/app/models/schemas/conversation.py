from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ConversationCreateRequest(BaseModel):
    title: Optional[str] = "Legal Drafting Tutoring"


class ConversationSummaryResponse(BaseModel):
    summary_text: str
    updated_at: datetime


class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    summary: Optional[str] = None