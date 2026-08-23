from typing import Any, Dict, List
from app.db.supabase import get_supabase_admin_client


class ProgressRepository:
    """Aggregates multi-table analytics for student mastery, draft evaluations, and leaderboards."""

    def __init__(self):
        self.client = get_supabase_admin_client()

    def get_student_evaluation_stats(self, user_id: str) -> Dict[str, Any]:
        res = (
            self.client.table("drafts")
            .select("id, document_type, draft_versions(evaluations(overall_score, created_at))")
            .eq("user_id", user_id)
            .execute()
        )
        drafts = res.data or []
        scores: List[float] = []
        doc_performance: Dict[str, List[float]] = {}

        for d in drafts:
            dtype = d["document_type"]
            for v in d.get("draft_versions", []):
                for e in v.get("evaluations", []):
                    sc = float(e["overall_score"])
                    scores.append(sc)
                    doc_performance.setdefault(dtype, []).append(sc)

        avg_score = round(sum(scores) / len(scores), 2) if scores else 0.0
        doc_averages = {
            dtype: round(sum(s_list) / len(s_list), 2)
            for dtype, s_list in doc_performance.items()
        }

        return {
            "total_evaluations": len(scores),
            "average_score": avg_score,
            "score_history": scores[-10:],
            "document_type_averages": doc_averages
        }

    def get_global_leaderboard(self, limit: int = 20) -> List[Dict[str, Any]]:
        # Fetch students and their evaluations
        res = (
            self.client.table("profiles")
            .select("id, full_name, role, drafts(draft_versions(evaluations(overall_score)))")
            .eq("role", "STUDENT")
            .execute()
        )
        students = res.data or []
        leaderboard_data = []

        for st in students:
            scores = []
            for d in st.get("drafts", []):
                for v in d.get("draft_versions", []):
                    for e in v.get("evaluations", []):
                        scores.append(float(e["overall_score"]))

            if scores:
                avg = round(sum(scores) / len(scores), 2)
                leaderboard_data.append({
                    "user_id": st["id"],
                    "full_name": st.get("full_name") or "Anonymous Student",
                    "evaluations_completed": len(scores),
                    "average_score": avg
                })

        leaderboard_data.sort(key=lambda x: (x["average_score"], x["evaluations_completed"]), reverse=True)
        return leaderboard_data[:limit]