from typing import Any, Dict, List
from app.ai.graph.queries.skill_queries import (
    GET_SKILLS_FOR_CLAUSES,
    UPSERT_STUDENT_SKILL_HISTORY,
)
from app.db.neo4j import execute_cypher_read, execute_cypher_write


class SkillGraph:
    """Manages student skill progression, weakness mappings, and skill links."""

    @staticmethod
    def get_skills_for_clauses(clause_ids: List[str]) -> List[Dict[str, Any]]:
        if not clause_ids:
            return []
        return execute_cypher_read(GET_SKILLS_FOR_CLAUSES, {"clause_ids": clause_ids})

    @staticmethod
    def update_student_skill(user_id: str, skill_id: str, score: float) -> None:
        execute_cypher_write(
            UPSERT_STUDENT_SKILL_HISTORY,
            {"user_id": user_id, "skill_id": skill_id, "score": score}
        )