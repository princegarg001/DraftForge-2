from typing import Any, Dict, List


class RRFReranker:
    """
    Reciprocal Rank Fusion (RRF) reranking to combine dense vector rankings
    with keyword matches deterministically.
    """
    @staticmethod
    def rerank(
        vector_results: List[Dict[str, Any]],
        keyword_results: List[Dict[str, Any]],
        k: int = 60,
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        scores: Dict[str, float] = {}
        doc_map: Dict[str, Dict[str, Any]] = {}

        # Process vector ranks
        for rank, item in enumerate(vector_results, start=1):
            chunk_id = item["chunk_id"]
            doc_map[chunk_id] = item
            scores[chunk_id] = scores.get(chunk_id, 0.0) + (1.0 / (k + rank))

        # Process keyword ranks
        for rank, item in enumerate(keyword_results, start=1):
            chunk_id = item.get("chunk_id")
            if not chunk_id:
                continue
            doc_map[chunk_id] = item
            scores[chunk_id] = scores.get(chunk_id, 0.0) + (1.0 / (k + rank))

        # Sort by merged reciprocal rank
        sorted_ids = sorted(scores.keys(), key=lambda cid: scores[cid], reverse=True)
        reranked: List[Dict[str, Any]] = []
        for cid in sorted_ids[:top_n]:
            entry = dict(doc_map[cid])
            entry["rrf_score"] = round(scores[cid], 5)
            reranked.append(entry)

        return reranked