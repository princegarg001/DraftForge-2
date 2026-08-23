from typing import List
from app.ai.evaluation.models import EvaluationFinding


class EvidenceEngine:
    @staticmethod
    def aggregate(
        structure_findings: List[EvaluationFinding],
        clause_findings: List[EvaluationFinding],
        formatting_findings: List[EvaluationFinding],
        contradictions: List[EvaluationFinding],
        gaps: List[EvaluationFinding]
    ) -> List[EvaluationFinding]:
        """Combines all modular findings into a unified, traceable evidence list."""
        all_findings = []
        all_findings.extend(structure_findings)
        all_findings.extend(clause_findings)
        all_findings.extend(formatting_findings)
        all_findings.extend(contradictions)
        all_findings.extend(gaps)
        return all_findings