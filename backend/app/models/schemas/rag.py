from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from app.core.constants import DocumentType


class EvidenceChunkSchema(BaseModel):
    chunk_id: str
    document_id: str
    document_type: str
    jurisdiction: str
    source_document: str
    section: str
    clause_id: Optional[str] = None
    page_number: int
    content: str
    similarity_score: Optional[float] = None
    rrf_score: Optional[float] = None


class RAGQueryRequest(BaseModel):
    query: str
    document_type: DocumentType
    section_hint: Optional[str] = None
    top_k: int = 4


class RAGQueryResponse(BaseModel):
    query: str
    document_type: DocumentType
    results_count: int
    evidence: List[EvidenceChunkSchema]
    formatted_context: str