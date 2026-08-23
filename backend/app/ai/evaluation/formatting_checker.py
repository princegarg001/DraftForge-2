import re
from typing import List, Tuple
from app.ai.evaluation.models import EvaluationFinding, RubricConfig
from app.core.constants import FindingCategory, FindingStatus


class FormattingChecker:
    @staticmethod
    def evaluate(draft_text: str, rubric: RubricConfig) -> Tuple[float, List[EvaluationFinding]]:
        findings: List[EvaluationFinding] = []
        max_fmt_score = rubric.weights.get("formatting", 25.0)
        accumulated_score = 0.0

        # Sub-criteria: Paragraphing, Numbering/List, Signature/Closing blocks
        tests = [
            ("Paragraph Structure and Line Breaks", r"\n\s*\n", 0.35, "Document contains readable paragraph segmentation."),
            ("Numbered Clauses or Lists", r"(?:\d+\.|\([a-z0-9]\))", 0.35, "Clauses are systematically indexed and numbered."),
            ("Execution / Signature / Jurat Block", r"(?:signature|deponent|in witness whereof|advocate|sd/-|verified)", 0.30, "Document includes formal execution, witness, or verification sign-off.")
        ]

        for criterion, regex, weight, pass_desc in tests:
            sub_max = round(max_fmt_score * weight, 2)
            matches = len(re.findall(regex, draft_text, re.IGNORECASE))

            if matches > 0:
                score = sub_max
                status = FindingStatus.PASS
                explanation = pass_desc
            else:
                score = 0.0
                status = FindingStatus.FAIL
                explanation = f"Formatting deficiency: failed requirement for '{criterion}'."

            accumulated_score += score
            findings.append(
                EvaluationFinding(
                    category=FindingCategory.FORMATTING,
                    criterion=criterion,
                    status=status,
                    score=score,
                    max_score=sub_max,
                    explanation=explanation
                )
            )

        return round(accumulated_score, 2), findings