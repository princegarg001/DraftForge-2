from app.ai.evaluation.evaluator import EvaluationEngine
from app.core.constants import DocumentType


def test_scoring_consistency_benchmark(sample_affidavit_text):
    """
    Verifies deterministic scoring reproducibility across 5 identical evaluations.
    """
    engine = EvaluationEngine()
    scores = []
    for _ in range(5):
        res = engine.evaluate_draft(sample_affidavit_text, DocumentType.AFFIDAVIT_OF_CHARACTER)
        scores.append(res.overall_score)

    # Deterministic scoring must produce zero variance
    assert len(set(scores)) == 1