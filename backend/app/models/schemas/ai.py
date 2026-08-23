from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from app.core.constants import DocumentType


# ---------------- Drafting Assistance Schemas ----------------
class AssistDraftingRequest(BaseModel):
    document_type: DocumentType
    target_clause: str
    user_instructions: Optional[str] = None
    context_draft_id: Optional[str] = None


class AssistDraftingResponse(BaseModel):
    document_type: Any
    target_clause: str
    generated_draft: Optional[str] = None
    drafted_clause: Optional[str] = None
    commentary: Optional[str] = None


# ---------------- Evaluation Explanation Schemas ----------------
class ExplainEvaluationRequest(BaseModel):
    evaluation_id: str
    clause_category: Optional[str] = None
    student_query: Optional[str] = None


class ExplainEvaluationResponse(BaseModel):
    evaluation_id: str
    explanation: str
    remedial_suggestions: List[str] = []
    statutory_context: Optional[str] = None


# ---------------- Tutor Chat Direct Schemas ----------------
class TutorChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str = Field(..., min_length=1)
    document_type: Optional[DocumentType] = None
    draft_id: Optional[str] = None
    section_hint: Optional[str] = None


class TutorChatResponse(BaseModel):
    response: str
    conversation_id: Optional[str] = None
    retrieved_sources: List[Dict[str, Any]] = []


# ---------------- Exercise Generation Schemas ----------------
class GenerateExerciseRequest(BaseModel):
    document_type: DocumentType
    skill_name: Optional[str] = None
    difficulty: Optional[str] = "INTERMEDIATE"


class GenerateExerciseResponse(BaseModel):
    document_type: Any
    task_prompt: str
    rubric_hints: List[str] = []
    model_draft: Optional[str] = None


# ---------------- Semantic Search Schemas ----------------
class SemanticSearchRequest(BaseModel):
    query: str
    document_type: Optional[DocumentType] = None
    limit: Optional[int] = 5


class SemanticSearchResponse(BaseModel):
    results: List[Dict[str, Any]] = []