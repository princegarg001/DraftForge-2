from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.core.constants import DocumentType


class ConversationCreate(BaseModel):
    title: str = Field(..., max_length=255)


class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: Any
    updated_at: Any
    summary: Optional[str] = None


class ChatMessageRequest(BaseModel):
    conversation_id: str
    message: str
    document_type: Optional[DocumentType] = None
    draft_id: Optional[str] = None
    section_hint: Optional[str] = None


class SendMessageRequest(BaseModel):
    conversation_id: str
    message: str
    document_type: Optional[DocumentType] = None
    draft_id: Optional[str] = None
    section_hint: Optional[str] = None


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    user_id: Optional[str] = None
    role: str
    content: str
    model: Optional[str] = None
    retrieved_sources: Optional[List[Dict[str, Any]]] = []
    created_at: Any


class ChatTurnResponse(BaseModel):
    user_message: MessageResponse
    ai_message: MessageResponse


# Alias for ChatTurnResponse to support both naming conventions
SendMessageResponse = ChatTurnResponse


class ConversationSummaryResponse(BaseModel):
    id: str
    conversation_id: str
    summary_text: str
    created_at: Any