from typing import List, Optional
from fastapi import UploadFile
from app.ai.rag.pipeline import RAGPipeline
from app.config import get_settings
from app.core.constants import DocumentType
from app.core.exceptions import BaseAppException, NotFoundError
from app.core import audit
from app.core.file_security import sanitize_filename, validate_uploaded_file
from app.db.repositories.document_repository import DocumentRepository
from app.models.schemas.document import DocumentClassificationResult, ReferenceDocumentResponse
from app.services.parsing.classifier import DocumentClassifier
from app.services.parsing.parser_factory import ParserFactory
from app.services.storage_service import StorageService
from app.utils.file_utils import compute_sha256

settings = get_settings()


class DocumentService:
    def __init__(self):
        self.repo = DocumentRepository()
        self.storage_service = StorageService()
        self.rag_pipeline = RAGPipeline()

    async def ingest_reference_document(
        self,
        file: UploadFile,
        uploaded_by: str,
        explicit_doc_type: Optional[DocumentType] = None,
        jurisdiction: str = "India"
    ) -> ReferenceDocumentResponse:
        content = await file.read()
        verified_type = validate_uploaded_file(file, content)
        safe_filename = sanitize_filename(file.filename or "upload")

        file_hash = compute_sha256(content)
        existing = self.repo.get_by_hash(file_hash)
        if existing:
            return ReferenceDocumentResponse(**existing)

        # 1. Parse document structure & extract pages
        parser = ParserFactory.get_parser_for_file(safe_filename)
        parsed_doc = parser.parse(content, safe_filename)

        if explicit_doc_type:
            doc_type = explicit_doc_type
        else:
            detected_type, _ = DocumentClassifier.classify(parsed_doc.raw_text)
            doc_type = detected_type

        # 2. Store original binary in Supabase Storage
        storage_path = self.storage_service.store_reference_document(
            filename=f"{file_hash}_{safe_filename}",
            content=content,
            content_type=verified_type,
        )

        # 3. Store document metadata record in PostgreSQL
        record = self.repo.create({
            "title": safe_filename,
            "document_type": doc_type.value,
            "jurisdiction": jurisdiction,
            "storage_path": storage_path,
            "file_size_bytes": len(content),
            "file_hash": file_hash,
            "mime_type": verified_type,
            "uploaded_by": uploaded_by
        })

        # 4. Ingest into RAG Vector Pipeline (Chunk, Embed, and Index into Qdrant)
        self.rag_pipeline.index_reference_document(
            parsed_doc=parsed_doc,
            document_id=record["id"],
            document_type=doc_type,
            source_document=safe_filename,
            jurisdiction=jurisdiction
        )

        audit.record(
            action=audit.AuditAction.REFERENCE_UPLOADED,
            resource="reference_document",
            actor_id=uploaded_by,
            actor_role="TEACHER",
            resource_id=record["id"],
            details={
                "filename": safe_filename,
                "document_type": doc_type.value,
                "size_bytes": len(content),
                "sha256": file_hash,
            },
        )

        return ReferenceDocumentResponse(**record)

    def list_reference_documents(self, doc_type: Optional[DocumentType] = None) -> List[ReferenceDocumentResponse]:
        if doc_type:
            records = self.repo.list_by_type(doc_type)
        else:
            records = self.repo.list_all()
        return [ReferenceDocumentResponse(**r) for r in records]

    def get_document_by_id(self, document_id: str) -> ReferenceDocumentResponse:
        record = self.repo.get_by_id(document_id)
        if not record:
            raise NotFoundError("ReferenceDocument", document_id)
        return ReferenceDocumentResponse(**record)

    def classify_text(self, text: str) -> DocumentClassificationResult:
        detected_type, confidence = DocumentClassifier.classify(text)
        return DocumentClassificationResult(
            detected_type=detected_type,
            confidence=confidence,
            summary=f"Detected {detected_type.value} with {int(confidence * 100)}% structural confidence."
        )