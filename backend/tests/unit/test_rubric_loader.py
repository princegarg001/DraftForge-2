from app.ai.evaluation.rubric_loader import RubricLoader
from app.core.constants import DocumentType


def test_load_all_four_rubrics():
    for dt in DocumentType:
        rubric = RubricLoader.load_rubric(dt)
        assert rubric.max_score == 100.0
        assert "structure" in rubric.weights
        assert "clause_coverage" in rubric.weights
        assert "formatting" in rubric.weights
        assert len(rubric.mandatory_clauses) > 0