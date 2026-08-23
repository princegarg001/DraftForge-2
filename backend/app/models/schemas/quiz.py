from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from app.core.constants import DocumentType


class QuizOption(BaseModel):
    key: str
    text: str


class QuizQuestionResponse(BaseModel):
    id: str
    quiz_id: str
    question_text: str
    options: List[QuizOption]
    order_index: int


class QuizResponse(BaseModel):
    id: str
    skill_id: Optional[str] = None
    document_type: DocumentType
    title: str
    description: Optional[str] = None
    difficulty: str
    created_at: datetime
    questions: List[QuizQuestionResponse] = []


class SubmitQuizAttemptRequest(BaseModel):
    quiz_id: str
    answers: Dict[str, str]  # {question_id: "A"}


class QuizAttemptResponse(BaseModel):
    id: str
    quiz_id: str
    user_id: str
    score: float
    total_questions: int
    passed: bool
    breakdown: List[Dict[str, Any]] = []
    created_at: datetime