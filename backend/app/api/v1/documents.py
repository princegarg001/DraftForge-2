from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from app.core.constants import DocumentType
from app.core.rate_limit import LimitScope, RateLimit
from app.dependencies import get_current_user, require_teacher
from app.models.database.models import UserProfileDB
from app.models.schemas.document import DocumentClassificationResult, ReferenceDocumentResponse
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Reference Documents (Teacher/RAG)"])
doc_service = DocumentService()


@router.post(
    "/reference/upload",
    response_model=ReferenceDocumentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_teacher), Depends(RateLimit(LimitScope.UPLOAD))],
)
async def upload_reference_document(
    file: UploadFile = File(...),
    document_type: Optional[DocumentType] = Form(None),
    jurisdiction: str = Form("India"),
    current_user: UserProfileDB = Depends(get_current_user),
):
    """
    Upload and parse official reference documents (Teacher/Admin only).
    """
    return await doc_service.ingest_reference_document(
        file=file,
        uploaded_by=current_user.id,
        explicit_doc_type=document_type,
        jurisdiction=jurisdiction
    )


@router.get("/reference", response_model=List[ReferenceDocumentResponse])
async def list_reference_documents(
    document_type: Optional[DocumentType] = None,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """
    List available reference corpus documents.
    """
    return doc_service.list_reference_documents(doc_type=document_type)


@router.post(
    "/classify",
    response_model=DocumentClassificationResult,
    # Was fully unauthenticated and accepted arbitrary text, giving anyone an
    # unbounded compute endpoint. Now authenticated and rate limited.
    dependencies=[Depends(RateLimit(LimitScope.DEFAULT))],
)
async def classify_raw_text(
    text: str = Form(..., max_length=200_000),
    current_user: UserProfileDB = Depends(get_current_user),
):
    """
    Run rule-based classification against legal text.
    """
    return doc_service.classify_text(text)