from typing import Any, Dict, List
from app.ai.agents.roadmap_agent import RoadmapAgent
from app.db.repositories.progress_repository import ProgressRepository
from app.db.repositories.roadmap_repository import RoadmapRepository
from app.db.repositories.skill_repository import SkillRepository


class RoadmapPipeline:
    """Orchestrates dynamic roadmap generation based on empirical student weak points."""

    def __init__(self):
        self.skill_repo = SkillRepository()
        self.roadmap_repo = RoadmapRepository()
        self.progress_repo = ProgressRepository()
        self.agent = RoadmapAgent()

    async def generate_personalized_roadmap(self, user_id: str) -> Dict[str, Any]:
        # 1. Fetch skill proficiencies
        student_skills = self.skill_repo.get_student_skills(user_id)
        weak_skills = [
            s["skills"]["name"] for s in student_skills if float(s["proficiency_score"]) < 60.0
        ]
        strong_skills = [
            s["skills"]["name"] for s in student_skills if float(s["proficiency_score"]) >= 75.0
        ]

        # 2. Fetch evaluation stats
        stats = self.progress_repo.get_student_evaluation_stats(user_id)
        avg_score = stats["average_score"]
        doc_types = list(stats["document_type_averages"].keys()) or ["AFFIDAVIT_OF_CHARACTER", "EMPLOYMENT_AGREEMENT"]

        # 3. Generate 5-phase learning trajectory via LLM
        phases = await self.agent.generate_roadmap(
            weak_skills=weak_skills,
            strong_skills=strong_skills,
            average_score=avg_score,
            target_doc_types=doc_types
        )

        # 4. Deactivate old roadmaps and save new active roadmap
        self.roadmap_repo.deactivate_user_roadmaps(user_id)
        roadmap = self.roadmap_repo.create({
            "user_id": user_id,
            "title": f"Targeted Legal Drafting Mastery ({len(weak_skills)} Priority Areas)",
            "is_active": True
        })

        items = []
        for p in phases:
            it = self.roadmap_repo.create_roadmap_item(
                roadmap_id=roadmap["id"],
                phase_number=p.get("phase_number", 1),
                title=p.get("title", "Drafting Phase"),
                description=p.get("description", "")
            )
            items.append(it)

        roadmap["roadmap_items"] = items
        return roadmap