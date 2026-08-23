from fastapi import APIRouter, Depends
from app.ai.rag.context.context_builder import ContextBuilder
from app.ai.rag.pipeline import RAGPipeline
from app.dependencies import get_current_user
from app.models.database.models import UserProfileDB
from app.models.schemas.rag import EvidenceChunkSchema, RAGQueryRequest, RAGQueryResponse

router = APIRouter(prefix="/rag", tags=["RAG & Evidence Retrieval"])
rag_pipeline = RAGPipeline()


@router.post("/retrieve", response_model=RAGQueryResponse)
async def query_reference_evidence(
    payload: RAGQueryRequest,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    Executes hybrid retrieval (dense vectors + keyword metadata) to retrieve traceable reference evidence.
    """
    raw_results = rag_pipeline.retrieve_reference_evidence(
        query=payload.query,
        document_type=payload.document_type,
        section_hint=payload.section_hint,
        top_k=payload.top_k
    )

    evidence_items = [EvidenceChunkSchema(**res) for res in raw_results]
    context_str = ContextBuilder.build_evidence_context(raw_results)

    return RAGQueryResponse(
        query=payload.query,
        document_type=payload.document_type,
        results_count=len(evidence_items),
        evidence=evidence_items,
        formatted_context=context_str
    )