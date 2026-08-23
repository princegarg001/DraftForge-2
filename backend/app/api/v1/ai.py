from fastapi import APIRouter, Depends, status
from app.dependencies import get_current_user
from app.models.database.models import UserProfileDB
from app.models.schemas.ai import (
    AssistDraftingRequest,
    AssistDraftingResponse,
    ExplainEvaluationRequest,
    ExplainEvaluationResponse,
    TutorChatRequest,
    TutorChatResponse,
)
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI Assistance & Reasoning"])
ai_service = AIService()


@router.post("/assist-drafting", response_model=AssistDraftingResponse, status_code=status.HTTP_200_OK)
async def assist_drafting(
    payload: AssistDraftingRequest,
    current_user: UserProfileDB = Depends(get_current_user)
):
    return await ai_service.assist_drafting(payload)


@router.post("/explain-evaluation", response_model=ExplainEvaluationResponse, status_code=status.HTTP_200_OK)
async def explain_evaluation(
    payload: ExplainEvaluationRequest,
    current_user: UserProfileDB = Depends(get_current_user)
):
    return await ai_service.explain_evaluation(payload)