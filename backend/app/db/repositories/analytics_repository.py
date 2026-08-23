from typing import Any, Dict, List
from app.db.supabase import get_supabase_admin_client


class AnalyticsRepository:
    """Computes cross-sectional cohort intelligence and weak-skill distributions for teachers."""

    def __init__(self):
        self.client = get_supabase_admin_client()

    def get_cohort_overview(self) -> Dict[str, Any]:
        # 1. Total Student Count
        st_res = self.client.table("profiles").select("id", count="exact").eq("role", "STUDENT").execute()
        total_students = st_res.count or 0

        # 2. Total Evaluations and Average Score
        eval_res = self.client.table("evaluations").select("overall_score, is_overridden, overridden_score").execute()
        evals = eval_res.data or []
        scores = [
            float(e["overridden_score"]) if e["is_overridden"] and e["overridden_score"] is not None else float(e["overall_score"])
            for e in evals
        ]
        cohort_avg = round(sum(scores) / len(scores), 2) if scores else 0.0

        # 3. Weak-Skill Breakdown
        skills_res = (
            self.client.table("student_skills")
            .select("proficiency_score, skills(name, category)")
            .execute()
        )
        skill_aggregates: Dict[str, List[float]] = {}
        for s in skills_res.data or []:
            name = s["skills"]["name"]
            skill_aggregates.setdefault(name, []).append(float(s["proficiency_score"]))

        weak_skills = []
        for name, p_list in skill_aggregates.items():
            avg_prof = round(sum(p_list) / len(p_list), 2)
            weak_skills.append({
                "skill_name": name,
                "average_proficiency": avg_prof,
                "struggling_students_count": sum(1 for p in p_list if p < 60.0)
            })

        weak_skills.sort(key=lambda x: x["average_proficiency"])

        return {
            "total_students": total_students,
            "total_evaluations": len(evals),
            "cohort_average_score": cohort_avg,
            "weak_skills_distribution": weak_skills[:8]
        }