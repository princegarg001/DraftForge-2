from abc import ABC
from app.ai.evaluation.clause_matcher import ClauseMatcher
from app.ai.evaluation.contradiction_detector import ContradictionDetector
from app.ai.evaluation.evidence_engine import EvidenceEngine
from app.ai.evaluation.formatting_checker import FormattingChecker
from app.ai.evaluation.gap_detector import GapDetector
from app.ai.evaluation.models import EvaluationResult
from app.ai.evaluation.rubric_loader import RubricLoader
from app.ai.evaluation.scoring_engine import ScoringEngine
from app.ai.evaluation.structure_checker import StructureChecker
from app.ai.rag.pipeline import RAGPipeline
from app.core.constants import DocumentType


class BaseDocumentEvaluator(ABC):
    def __init__(self, doc_type: DocumentType, rag_pipeline: RAGPipeline):
        self.doc_type = doc_type
        self.rag_pipeline = rag_pipeline
        self.clause_matcher = ClauseMatcher(rag_pipeline)

    def evaluate(self, draft_text: str) -> EvaluationResult:
        rubric = RubricLoader.load_rubric(self.doc_type)

        # 1. Structural evaluation
        struct_score, struct_findings = StructureChecker.evaluate(draft_text, rubric)

        # 2. Reference-grounded clause evaluation
        clause_score, clause_findings = self.clause_matcher.evaluate(draft_text, self.doc_type, rubric)

        # 3. Formatting evaluation
        fmt_score, fmt_findings = FormattingChecker.evaluate(draft_text, rubric)

        # 4. Semantic contradictions & gaps
        contradictions = ContradictionDetector.detect(draft_text)
        gaps = GapDetector.detect_gaps(clause_findings)

        # 5. Evidence aggregation
        all_findings = EvidenceEngine.aggregate(
            struct_findings,
            clause_findings,
            fmt_findings,
            contradictions,
            gaps
        )

        # 6. Deterministic scoring computation
        return ScoringEngine.calculate_score(
            structure_score=struct_score,
            clause_score=clause_score,
            formatting_score=fmt_score,
            findings=all_findings,
            rubric=rubric
        )