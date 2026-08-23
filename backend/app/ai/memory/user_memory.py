from typing import Any, Dict, List, Optional
from app.db.supabase import get_supabase_admin_client


class UserLearningMemory:
    """Tracks cumulative student learning traits, frequent mistakes, and mastered concepts."""

    def __init__(self):
        self.client = get_supabase_admin_client()
        self.table = "user_learning_memory"

    def get_user_memory(self, user_id: str) -> Dict[str, Any]:
        res = self.client.table(self.table).select("*").eq("user_id", user_id).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
        return {
            "learning_notes": "Student beginning legal drafting curriculum.",
            "frequent_mistakes": [],
            "mastered_concepts": []
        }

    def record_weakness(self, user_id: str, mistake_tag: str, note_addition: Optional[str] = None) -> None:
        current = self.get_user_memory(user_id)
        mistakes = list(set(current.get("frequent_mistakes", []) + [mistake_tag]))
        notes = current.get("learning_notes", "")
        if note_addition and note_addition not in notes:
            notes += f" {note_addition}"

        payload = {
            "user_id": user_id,
            "learning_notes": notes,
            "frequent_mistakes": mistakes,
            "mastered_concepts": current.get("mastered_concepts", []),
            "updated_at": "now()"
        }
        self.client.table(self.table).upsert(payload).execute()