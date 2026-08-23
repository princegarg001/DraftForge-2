from typing import Any, Dict
from app.ai.rag.chunking.models import LegalChunk
from app.core.constants import DocumentType


class MetadataBuilder:
    @staticmethod
    def build_payload(
        chunk: LegalChunk,
        document_id: str,
        document_type: DocumentType,
        source_document: str,
        jurisdiction: str = "India",
        source_type: str = "reference"
    ) -> Dict[str, Any]:
        """Constructs Qdrant vector payload conforming to evaluation schema."""
        return {
            "chunk_id": chunk.chunk_id,
            "document_id": document_id,
            "document_type": document_type.value if hasattr(document_type, "value") else str(document_type),
            "jurisdiction": jurisdiction.lower(),
            "source_document": source_document,
            "section": chunk.section,
            "subsection": chunk.subsection or "",
            "clause_id": chunk.clause_id or "",
            "chunk_type": chunk.chunk_type,
            "source_type": source_type,
            "page_number": chunk.page_number or 1,
            "content": chunk.content,
        }