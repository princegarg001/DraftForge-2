import re
from typing import List, Tuple
from app.ai.evaluation.models import EvaluationFinding, RubricConfig
from app.core.constants import FindingCategory, FindingStatus


class StructureChecker:
    @staticmethod
    def evaluate(draft_text: str, rubric: RubricConfig) -> Tuple[float, List[EvaluationFinding]]:
        findings: List[EvaluationFinding] = []
        required_sections = rubric.required_sections
        total_sections = len(required_sections)
        max_structure_score = rubric.weights.get("structure", 25.0)

        if total_sections == 0:
            return max_structure_score, findings

        points_per_sec = max_structure_score / total_sections
        accumulated_score = 0.0
        lower_text = draft_text.lower()

        for sec in required_sections:
            sec_name = sec["name"]
            is_mandatory = sec.get("mandatory", True)
            keywords = [w.lower() for w in re.findall(r"\b\w{3,}\b", sec_name)]

            # Check if keywords from section title appear in draft
            matches = sum(1 for kw in keywords if kw in lower_text)
            coverage = matches / max(len(keywords), 1)

            if coverage >= 0.5:
                status = FindingStatus.PASS
                score = round(points_per_sec, 2)
                explanation = f"Section '{sec_name}' identified and structurally organized."
            elif coverage > 0.1:
                status = FindingStatus.PARTIAL
                score = round(points_per_sec * 0.5, 2)
                explanation = f"Section '{sec_name}' is partially presented but lacks clear demarcations or headers."
            else:
                status = FindingStatus.FAIL
                score = 0.0
                explanation = f"Required section '{sec_name}' appears completely missing from the draft."

            accumulated_score += score
            findings.append(
                EvaluationFinding(
                    category=FindingCategory.STRUCTURE,
                    criterion=sec_name,
                    status=status,
                    score=score,
                    max_score=round(points_per_sec, 2),
                    student_evidence=None,
                    reference_evidence=f"Reference requires section: {sec_name}",
                    explanation=explanation
                )
            )

        return round(accumulated_score, 2), findings