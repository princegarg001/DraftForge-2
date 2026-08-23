from typing import Any, Dict, List, Optional
from app.ai.rag.reranking.rrf_reranker import RRFReranker
from app.ai.rag.retrieval.keyword_retriever import KeywordRetriever
from app.ai.rag.retrieval.vector_retriever import VectorRetriever
from app.core.constants import DocumentType


class HybridRetriever:
    def __init__(self):
        self.vector_retriever = VectorRetriever()
        self.keyword_retriever = KeywordRetriever()
        self.reranker = RRFReranker()

    def retrieve(
        self,
        query: str,
        document_type: DocumentType,
        section_hint: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        # 1. Dense vector search
        vector_hits = self.vector_retriever.retrieve(
            query=query,
            document_type=document_type,
            top_k=top_k * 2
        )

        # 2. Section/Keyword matching if a section hint is available
        keyword_hits: List[Dict[str, Any]] = []
        if section_hint:
            keyword_hits = self.keyword_retriever.retrieve_by_section(
                section_name=section_hint,
                document_type=document_type,
                limit=top_k * 2
            )

        # 3. Merged RRF reranking
        if keyword_hits:
            return self.reranker.rerank(vector_hits, keyword_hits, top_n=top_k)
        
        return vector_hits[:top_k]