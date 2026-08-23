from typing import List, Optional
from fastapi import APIRouter, Depends
from app.core.constants import DocumentType
from app.dependencies import get_current_user
from app.models.database.models import UserProfileDB
from app.models.schemas.quiz import (
    QuizAttemptResponse,
    QuizResponse,
    SubmitQuizAttemptRequest,
)
from app.services.quiz_service import QuizService

router = APIRouter(prefix="/quizzes", tags=["Interactive Legal Quizzes"])
quiz_service = QuizService()


@router.get("", response_model=List[QuizResponse])
async def list_quizzes(
    document_type: Optional[DocumentType] = None,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Lists available interactive quizzes filtered by document type.
    """
    return quiz_service.list_quizzes(doc_type=document_type)


@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: str,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Retrieves quiz questions and options.
    """
    return quiz_service.get_quiz(quiz_id=quiz_id)


@router.post("/submit", response_model=QuizAttemptResponse)
async def submit_quiz(
    payload: SubmitQuizAttemptRequest,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Evaluates quiz submissions, calculates the score, and returns detailed question explanations.
    """
    return quiz_service.submit_quiz(user_id=current_user.id, payload=payload)