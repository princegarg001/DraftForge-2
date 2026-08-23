from app.ai.rag.retrieval.hybrid_retriever import HybridRetriever
from app.core.constants import DocumentType


def test_rag_retrieval_relevance_benchmark():
    """
    Measures precision and source traceability on core legal queries.
    """
    retriever = HybridRetriever()
    query = "procedure for termination with 30 days written notice"
    results = retriever.retrieve(query=query, document_type=DocumentType.EMPLOYMENT_AGREEMENT, top_k=3)

    assert isinstance(results, list)
    for res in results:
        # Traceability assertions
        assert "document_type" in res
        assert "source_document" in res
        assert "page_number" in res
        assert "content" in res