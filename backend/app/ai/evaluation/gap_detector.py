from typing import List
from app.ai.evaluation.models import EvaluationFinding
from app.core.constants import FindingCategory, FindingStatus


class GapDetector:
    @staticmethod
    def detect_gaps(clause_findings: List[EvaluationFinding]) -> List[EvaluationFinding]:
        """
        Synthesizes identified clause deficiencies into actionable educational gaps.
        """
        gap_findings: List[EvaluationFinding] = []
        for finding in clause_findings:
            if finding.category == FindingCategory.CLAUSE_COVERAGE and finding.status in (FindingStatus.FAIL, FindingStatus.PARTIAL):
                gap_findings.append(
                    EvaluationFinding(
                        category=FindingCategory.GAP,
                        criterion=f"Omission / Weakness: {finding.criterion}",
                        status=FindingStatus.WARNING,
                        score=0.0,
                        max_score=0.0,
                        student_evidence=finding.student_evidence,
                        reference_evidence=finding.reference_evidence,
                        source_document=finding.source_document,
                        source_page=finding.source_page,
                        source_section=finding.source_section,
                        explanation=f"Educational observation: Missing or incomplete provision for '{finding.criterion}'. {finding.explanation}"
                    )
                )
        return gap_findings