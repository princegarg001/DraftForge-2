import pytest
from app.ai.evaluation.evaluator import EvaluationEngine
from app.core.constants import DocumentType, FindingStatus


def test_affidavit_evaluation_deterministic_flow(sample_affidavit_text):
    engine = EvaluationEngine()
    result = engine.evaluate_draft(sample_affidavit_text, DocumentType.AFFIDAVIT_OF_CHARACTER)

    assert result.overall_score > 60.0
    assert result.structure_score > 0.0
    assert result.clause_score > 0.0
    assert result.formatting_score > 0.0
    
    # Assert verification clause was identified
    criteria_names = [f.criterion for f in result.findings]
    assert any("Verification" in c for c in criteria_names)


def test_employment_evaluation_deterministic_flow(sample_employment_text):
    engine = EvaluationEngine()
    result = engine.evaluate_draft(sample_employment_text, DocumentType.EMPLOYMENT_AGREEMENT)

    assert result.overall_score >= 70.0
    statuses = {f.criterion: f.status for f in result.findings}
    assert any("Termination" in k for k in statuses)