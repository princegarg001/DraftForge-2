from typing import List
from fastapi import APIRouter, Depends, status
from app.dependencies import get_current_user
from app.models.database.models import UserProfileDB
from app.models.schemas.chat import MessageResponse
from app.models.schemas.conversation import ConversationCreateRequest, ConversationResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/conversations", tags=["Chat Conversations"])
chat_service = ChatService()


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreateRequest,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Creates a new persistent tutoring conversation thread.
    """
    return chat_service.create_conversation(user_id=current_user.id, payload=payload)


@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Lists all persistent conversation threads belonging to the authenticated user.
    """
    return chat_service.list_user_conversations(user_id=current_user.id)


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Retrieves full chronological message history for a conversation.
    """
    return chat_service.get_conversation_messages(conversation_id=conversation_id, user_id=current_user.id)