import time
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
from app.observability import record_retrieval, set_attributes, span
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
        started = time.perf_counter()

        with span(
            "rag.retrieve",
            **{
                "rag.document_type": document_type.value,
                "rag.top_k": top_k,
                # Length only. The query is student-authored text and may quote
                # their draft, so it does not belong in a trace attribute.
                "rag.query_length": len(query),
                "rag.has_section_hint": bool(section_hint),
            },
        ):
            results = self.retriever.retrieve(
                query=query,
                document_type=document_type,
                section_hint=section_hint,
                top_k=top_k
            )

            # A falling top score is the earliest signal that retrieval quality
            # has regressed - visible here well before anyone reports a poor
            # answer from the tutor.
            top_score = None
            if results:
                scores = [float(r["score"]) for r in results if r.get("score") is not None]
                top_score = max(scores) if scores else None

            set_attributes(**{"rag.result_count": len(results), "rag.top_score": top_score})
            record_retrieval(
                stage="hybrid",
                document_type=document_type.value,
                duration_seconds=time.perf_counter() - started,
                result_count=len(results),
                top_score=top_score,
            )

        return results