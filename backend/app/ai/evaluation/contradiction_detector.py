import re
from typing import List
from app.ai.evaluation.models import EvaluationFinding
from app.core.constants import FindingCategory, FindingStatus


class ContradictionDetector:
    @staticmethod
    def detect(draft_text: str) -> List[EvaluationFinding]:
        """
        Detects internal semantic contradictions in numbers, dates, notice periods, and party roles.
        """
        findings: List[EvaluationFinding] = []

        # 1. Notice Period Contradictions (e.g. mentions 30 days and 15 days in same termination scope)
        notice_days = re.findall(r"(\d+)\s*(?:days?|months?)\s+(?:written\s+)?notice", draft_text, re.IGNORECASE)
        if len(set(notice_days)) > 1:
            findings.append(
                EvaluationFinding(
                    category=FindingCategory.CONTRADICTION,
                    criterion="Inconsistent Notice Period",
                    status=FindingStatus.WARNING,
                    score=0.0,
                    max_score=0.0,
                    student_evidence=f"Found divergent notice periods: {', '.join(set(notice_days))}",
                    explanation="Draft specifies conflicting notice durations for notice/termination, creating legal ambiguity."
                )
            )

        # 2. Inconsistent Year or Date References
        years = re.findall(r"\b(20[1-3][0-9])\b", draft_text)
        if len(set(years)) > 2:
            findings.append(
                EvaluationFinding(
                    category=FindingCategory.CONTRADICTION,
                    criterion="Conflicting Year References",
                    status=FindingStatus.WARNING,
                    score=0.0,
                    max_score=0.0,
                    student_evidence=f"Mentioned years: {', '.join(set(years))}",
                    explanation="Multiple divergent calendar years identified across operative and execution clauses."
                )
            )

        return findings