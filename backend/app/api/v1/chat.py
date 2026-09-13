from fastapi import APIRouter, Depends
from app.core.rate_limit import LimitScope, RateLimit
from app.dependencies import get_current_user
from app.models.database.models import UserProfileDB
from app.models.schemas.chat import ChatMessageRequest, ChatTurnResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Multi-Tier Memory Chat"])
chat_service = ChatService()


@router.post(
    "/send",
    response_model=ChatTurnResponse,
    # Each call reaches Groq, so an unthrottled loop here is an unbounded
    # inference bill.
    dependencies=[Depends(RateLimit(LimitScope.LLM))],
)
async def send_chat_message(
    payload: ChatMessageRequest,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Sends a message to the Socratic AI Tutor, utilizing multi-tier conversation memory,
    user learning history, and contextual RAG reference citations.
    """
    return await chat_service.send_message(user_id=current_user.id, payload=payload)