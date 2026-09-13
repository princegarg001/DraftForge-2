from typing import Any, Dict, List

from app.db.supabase import get_supabase_admin_client


class AnalyticsRepository:
    """Cohort intelligence and weak-skill distribution, scoped to a roster."""

    def __init__(self):
        self.client = get_supabase_admin_client()

    def get_cohort_overview(self, student_ids: List[str]) -> Dict[str, Any]:
        """Aggregate performance across the given students only.

        ``student_ids`` is required rather than optional. This previously
        counted every STUDENT profile, averaged every evaluation and pooled
        every skill record in the database, so each instructor's "cohort"
        dashboard actually described the entire platform - other institutions
        included.
        """
        empty: Dict[str, Any] = {
            "total_students": 0,
            "total_evaluations": 0,
            "cohort_average_score": 0.0,
            "weak_skills_distribution": [],
        }
        if not student_ids:
            return empty

        # Evaluations reachable from these students' drafts. evaluations has no
        # user column, so ownership runs through draft_versions -> drafts.
        draft_res = (
            self.client.table("drafts")
            .select("id, draft_versions(evaluations(overall_score, is_overridden, overridden_score))")
            .in_("user_id", student_ids)
            .execute()
        )

        scores: List[float] = []
        evaluation_count = 0
        for draft in draft_res.data or []:
            for version in draft.get("draft_versions") or []:
                for evaluation in version.get("evaluations") or []:
                    evaluation_count += 1
                    # A teacher's override is the authoritative mark.
                    if evaluation.get("is_overridden") and evaluation.get("overridden_score") is not None:
                        scores.append(float(evaluation["overridden_score"]))
                    elif evaluation.get("overall_score") is not None:
                        scores.append(float(evaluation["overall_score"]))

        cohort_avg = round(sum(scores) / len(scores), 2) if scores else 0.0

        skills_res = (
            self.client.table("student_skills")
            .select("proficiency_score, skills(name, category)")
            .in_("user_id", student_ids)
            .execute()
        )

        skill_aggregates: Dict[str, List[float]] = {}
        for row in skills_res.data or []:
            skill_info = row.get("skills")
            if not isinstance(skill_info, dict):
                continue
            name = skill_info.get("name") or "Unknown Skill"
            if row.get("proficiency_score") is not None:
                skill_aggregates.setdefault(name, []).append(float(row["proficiency_score"]))

        weak_skills = [
            {
                "skill_name": name,
                "average_proficiency": round(sum(values) / len(values), 2),
                "struggling_students_count": sum(1 for value in values if value < 60.0),
            }
            for name, values in skill_aggregates.items()
        ]
        weak_skills.sort(key=lambda item: item["average_proficiency"])

        return {
            "total_students": len(student_ids),
            "total_evaluations": evaluation_count,
            "cohort_average_score": cohort_avg,
            "weak_skills_distribution": weak_skills[:8],
        }
