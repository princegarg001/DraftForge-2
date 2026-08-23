from typing import Any, Dict, List
from qdrant_client.http import models as qmodels
from app.ai.embeddings.embedding_service import EmbeddingService
from app.ai.rag.chunking.legal_chunker import LegalClauseChunker
from app.ai.rag.metadata.metadata_builder import MetadataBuilder
from app.ai.rag.retrieval.hybrid_retriever import HybridRetriever
from app.config import get_settings
from app.core.constants import DocumentType
from app.core.logging import get_logger
from app.db.qdrant import get_qdrant_client
from app.services.parsing.base_parser import ParsedDocument

logger = get_logger("rag_pipeline")
settings = get_settings()


class RAGPipeline:
    def __init__(self):
        self.chunker = LegalClauseChunker()
        self.retriever = HybridRetriever()
        self.qdrant = get_qdrant_client()
        self.collection_name = settings.QDRANT_COLLECTION_NAME

    def index_reference_document(
        self,
        parsed_doc: ParsedDocument,
        document_id: str,
        document_type: DocumentType,
        source_document: str,
        jurisdiction: str = "India"
    ) -> int:
        """
        Extracts chunks, embeds text, and indexes dense vectors into Qdrant Cloud.
        """
        chunks = self.chunker.chunk(parsed_doc, document_id)
        if not chunks:
            logger.warning(f"No chunks extracted for document {document_id}")
            return 0

        texts = [c.content for c in chunks]
        embeddings = EmbeddingService.embed_texts(texts)

        points = []
        for chunk, vector in zip(chunks, embeddings):
            payload = MetadataBuilder.build_payload(
                chunk=chunk,
                document_id=document_id,
                document_type=document_type,
                source_document=source_document,
                jurisdiction=jurisdiction,
                source_type="reference"
            )
            points.append(
                qmodels.PointStruct(
                    id=qmodels.PointId(chunk.chunk_id.replace("-", "")[:32]),
                    vector=vector,
                    payload=payload
                )
            )

        self.qdrant.upsert(
            collection_name=self.collection_name,
            points=points
        )
        logger.info(f"Indexed {len(points)} vector chunks for reference doc '{source_document}' ({document_type.value}).")
        return len(points)

    def retrieve_reference_evidence(
        self,
        query: str,
        document_type: DocumentType,
        section_hint: str = None,
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        return self.retriever.retrieve(
            query=query,
            document_type=document_type,
            section_hint=section_hint,
            top_k=top_k
        )