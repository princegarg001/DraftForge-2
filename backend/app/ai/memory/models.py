from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MemoryMessage(BaseModel):
    id: str
    conversation_id: str
    user_id: str
    role: str  # "user" or "assistant"
    content: str
    model: Optional[str] = None
    retrieved_sources: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime


class ConversationContext(BaseModel):
    conversation_id: str
    summary: Optional[str] = None
    recent_messages: List[MemoryMessage] = Field(default_factory=list)
    user_memory_notes: Optional[str] = None
    frequent_mistakes: List[str] = Field(default_factory=list)
    document_memory_notes: Optional[str] = None
    rag_context: Optional[str] = None
    graph_context: Optional[str] = None