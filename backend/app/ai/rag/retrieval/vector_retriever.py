from typing import Any, Dict, List, Optional
from qdrant_client.http import models as qmodels
from app.ai.embeddings.embedding_service import EmbeddingService
from app.config import get_settings
from app.core.constants import DocumentType
from app.db.qdrant import get_qdrant_client

settings = get_settings()


class VectorRetriever:
    def __init__(self):
        self.client = get_qdrant_client()
        self.collection_name = settings.QDRANT_COLLECTION_NAME

    def retrieve(
        self,
        query: str,
        document_type: Optional[DocumentType] = None,
        jurisdiction: str = "india",
        top_k: int = 5,
        score_threshold: float = 0.40
    ) -> List[Dict[str, Any]]:
        query_vector = EmbeddingService.embed_query(query)

        # Build Qdrant metadata filters
        must_filters = [
            qmodels.FieldCondition(
                key="jurisdiction",
                match=qmodels.MatchValue(value=jurisdiction.lower())
            )
        ]
        if document_type:
            doc_type_val = document_type.value if hasattr(document_type, "value") else str(document_type)
            must_filters.append(
                qmodels.FieldCondition(
                    key="document_type",
                    match=qmodels.MatchValue(value=doc_type_val)
                )
            )

        query_filter = qmodels.Filter(must=must_filters)

        results: List[Dict[str, Any]] = []

        try:
            # Modern Qdrant API (1.10.0+)
            if hasattr(self.client, "query_points"):
                response = self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_vector,
                    query_filter=query_filter,
                    limit=top_k,
                    score_threshold=score_threshold,
                    with_payload=True
                )
                hits = response.points
            else:
                # Legacy Qdrant API (<1.10.0)
                hits = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    query_filter=query_filter,
                    limit=top_k,
                    score_threshold=score_threshold,
                )

            for hit in hits:
                payload = dict(hit.payload or {})
                payload["similarity_score"] = round(float(hit.score), 4)
                results.append(payload)

        except Exception:
            # Fallback to local deterministic execution if cloud collection has no points yet
            return []

        return results