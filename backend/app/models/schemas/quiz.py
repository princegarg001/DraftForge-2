from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict
from app.core.constants import DocumentType


class QuizOption(BaseModel):
    model_config = ConfigDict(extra="ignore")

    key: str
    text: str


class QuizQuestionResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    quiz_id: str
    question_text: str
    options: List[QuizOption]
    order_index: int


class QuizResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    skill_id: Optional[str] = None
    document_type: DocumentType
    title: str
    description: Optional[str] = None
    difficulty: str
    created_at: Optional[Any] = None
    questions: List[QuizQuestionResponse] = []


class SubmitQuizAttemptRequest(BaseModel):
    quiz_id: str
    answers: Dict[str, str]  # {question_id: "A"}


class QuizAttemptResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    quiz_id: str
    user_id: str
    score: float
    total_questions: int
    passed: bool
    breakdown: List[Dict[str, Any]] = []
    created_at: Optional[Any] = None