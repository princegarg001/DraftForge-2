from app.ai.evaluation.models import EvaluationFinding, RubricConfig
from app.ai.evaluation.scoring_engine import ScoringEngine
from app.core.constants import FindingCategory, FindingStatus


def test_deterministic_scoring_calculation():
    rubric = RubricConfig(
        document_type="AFFIDAVIT_OF_CHARACTER",
        jurisdiction="India",
        max_score=100.0,
        weights={"structure": 25.0, "clause_coverage": 50.0, "formatting": 25.0},
        penalties={"contradiction": 10.0, "missing_mandatory_clause": 10.0},
        required_sections=[],
        mandatory_clauses=[]
    )
    
    findings = [
        EvaluationFinding(
            category=FindingCategory.CONTRADICTION,
            criterion="Inconsistent Dates",
            status=FindingStatus.WARNING,
            score=0.0,
            max_score=0.0,
            explanation="Date clash found"
        )
    ]

    result = ScoringEngine.calculate_score(
        structure_score=25.0,
        clause_score=40.0,
        formatting_score=20.0,
        findings=findings,
        rubric=rubric
    )

    # 25 + 40 + 20 = 85 - 10 (contradiction penalty) = 75.0
    assert result.overall_score == 75.0
    assert result.gap_penalty == 10.0