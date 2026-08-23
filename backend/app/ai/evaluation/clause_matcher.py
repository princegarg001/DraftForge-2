import re
from typing import List, Tuple
from app.ai.evaluation.models import EvaluationFinding, RubricConfig
from app.ai.rag.pipeline import RAGPipeline
from app.core.constants import DocumentType, FindingCategory, FindingStatus


class ClauseMatcher:
    def __init__(self, rag_pipeline: RAGPipeline):
        self.rag = rag_pipeline

    def evaluate(
        self,
        draft_text: str,
        doc_type: DocumentType,
        rubric: RubricConfig
    ) -> Tuple[float, List[EvaluationFinding]]:
        findings: List[EvaluationFinding] = []
        mandatory_clauses = rubric.mandatory_clauses
        total_clauses = len(mandatory_clauses)
        max_clause_score = rubric.weights.get("clause_coverage", 50.0)

        if total_clauses == 0:
            return max_clause_score, findings

        points_per_clause = max_clause_score / total_clauses
        accumulated_score = 0.0
        lower_draft = draft_text.lower()

        for clause_spec in mandatory_clauses:
            clause_id = clause_spec["id"]
            clause_name = clause_spec["name"]
            keywords = clause_spec.get("keywords", [])
            min_similarity = clause_spec.get("min_similarity", 0.60)

            # 1. Keyword overlap scoring
            matched_kws = [kw for kw in keywords if kw.lower() in lower_draft]
            kw_ratio = len(matched_kws) / max(len(keywords), 1)

            # 2. Retrieve authoritative reference evidence from Qdrant via RAG
            rag_evidence = self.rag.retrieve_reference_evidence(
                query=f"{clause_name} {' '.join(keywords)}",
                document_type=doc_type,
                top_k=1
            )

            ref_chunk = rag_evidence[0] if rag_evidence else {}
            ref_content = ref_chunk.get("content", "")
            ref_source = ref_chunk.get("source_document", "Reference Knowledge Base")
            ref_page = ref_chunk.get("page_number", 1)
            ref_section = ref_chunk.get("section", "Standard Clauses")

            # Extract student matching sentence if keyword found
            student_excerpt = None
            if matched_kws:
                pattern = re.compile(rf"([^.\n]*?({re.escape(matched_kws[0])})[^.\n]*)", re.IGNORECASE)
                m = pattern.search(draft_text)
                if m:
                    student_excerpt = m.group(1).strip()

            # 3. Deterministic threshold assignment
            if kw_ratio >= 0.70:
                status = FindingStatus.PASS
                score = round(points_per_clause, 2)
                explanation = f"Clause '{clause_name}' is adequately drafted and contains essential legal terms ({', '.join(matched_kws)})."
            elif kw_ratio >= 0.30:
                status = FindingStatus.PARTIAL
                score = round(points_per_clause * 0.5, 2)
                explanation = f"Clause '{clause_name}' is only partially covered. Expected elements: {', '.join(keywords)}."
            else:
                status = FindingStatus.FAIL
                score = 0.0
                explanation = f"Essential clause '{clause_name}' is missing or substantially omitted based on reference standards."

            accumulated_score += score
            findings.append(
                EvaluationFinding(
                    category=FindingCategory.CLAUSE_COVERAGE,
                    criterion=clause_name,
                    status=status,
                    score=score,
                    max_score=round(points_per_clause, 2),
                    student_evidence=student_excerpt,
                    reference_evidence=ref_content or f"Standard requirements for {clause_name}",
                    source_document=ref_source,
                    source_page=ref_page,
                    source_section=ref_section,
                    explanation=explanation,
                    metadata={"clause_id": clause_id, "matched_keywords": matched_kws}
                )
            )

        return round(accumulated_score, 2), findings