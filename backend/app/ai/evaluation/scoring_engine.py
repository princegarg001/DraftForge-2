from typing import List
from app.ai.evaluation.models import EvaluationFinding, EvaluationResult, RubricConfig
from app.core.constants import FindingCategory, FindingStatus


class ScoringEngine:
    @staticmethod
    def calculate_score(
        structure_score: float,
        clause_score: float,
        formatting_score: float,
        findings: List[EvaluationFinding],
        rubric: RubricConfig
    ) -> EvaluationResult:
        """
        Deterministically calculates the overall score by applying rubric weights and deducting penalties.
        """
        # Calculate contradiction & severe gap penalties
        gap_penalty = 0.0
        contradiction_penalty_per_item = rubric.penalties.get("contradiction", 10.0)

        for f in findings:
            if f.category == FindingCategory.CONTRADICTION and f.status == FindingStatus.WARNING:
                gap_penalty += contradiction_penalty_per_item

        raw_total = structure_score + clause_score + formatting_score - gap_penalty
        final_score = max(0.0, min(raw_total, rubric.max_score))

        return EvaluationResult(
            overall_score=round(final_score, 2),
            max_score=rubric.max_score,
            structure_score=round(structure_score, 2),
            clause_score=round(clause_score, 2),
            formatting_score=round(formatting_score, 2),
            gap_penalty=round(gap_penalty, 2),
            rubric_version=f"{rubric.document_type}_v1.0",
            findings=findings
        )