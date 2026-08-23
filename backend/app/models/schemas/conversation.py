from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class ConversationCreateRequest(BaseModel):
    title: Optional[str] = "Legal Drafting Tutoring"


class ConversationSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    summary_text: str
    updated_at: Optional[Any] = None


class ConversationResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    user_id: str
    title: str
    created_at: Optional[Any] = None
    updated_at: Optional[Any] = None
    summary: Optional[str] = None