from typing import List
from app.ai.evaluation.models import EvaluationFinding
from app.ai.graph.skill_graph import SkillGraph
from app.core.constants import FindingCategory, FindingStatus
from app.db.repositories.skill_repository import SkillRepository


class SkillPipeline:
    """Updates student skill proficiencies across PostgreSQL and Neo4j based on evaluation evidence."""

    def __init__(self):
        self.skill_repo = SkillRepository()
        self.skill_graph = SkillGraph()

    def process_evaluation_skills(
        self,
        user_id: str,
        evaluation_id: str,
        findings: List[EvaluationFinding]
    ) -> None:
        for f in findings:
            if f.category in (FindingCategory.CLAUSE_COVERAGE, FindingCategory.STRUCTURE, FindingCategory.FORMATTING):
                # Retrieve matching skill entity
                skill = self.skill_repo.get_skill_by_name(f.criterion)
                if not skill:
                    continue

                skill_id = skill["id"]
                current_record = self.skill_repo.get_student_skill(user_id, skill_id)

                earned_ratio = (f.score / f.max_score) if f.max_score > 0 else 0.0
                score_points = round(earned_ratio * 100.0, 2)

                if current_record:
                    old_score = float(current_record["proficiency_score"])
                    # Moving average
                    new_score = round((old_score * 0.6) + (score_points * 0.4), 2)
                    delta = round(new_score - old_score, 2)
                    new_conf = min(1.0, float(current_record["confidence_level"]) + 0.15)
                else:
                    new_score = score_points
                    delta = score_points
                    new_conf = 0.50

                student_skill = self.skill_repo.upsert_student_skill(
                    user_id=user_id,
                    skill_id=skill_id,
                    proficiency_score=new_score,
                    confidence_level=new_conf
                )

                self.skill_repo.log_skill_history(
                    student_skill_id=student_skill["id"],
                    score_delta=delta,
                    reason=f"Evaluation {evaluation_id}: {f.explanation}",
                    evaluation_id=evaluation_id
                )

                # Update graph node connection in Neo4j Aura
                self.skill_graph.update_student_skill(user_id=user_id, skill_id=skill_id, score=new_score)