from typing import Any, Dict, List, Optional
from app.db.repositories.base_repository import BaseRepository


class RoadmapRepository(BaseRepository):
    def __init__(self):
        super().__init__(table_name="roadmaps")

    def get_active_roadmap(self, user_id: str) -> Optional[Dict[str, Any]]:
        res = (
            self.client.table(self.table_name)
            .select("*, roadmap_items(*)")
            .eq("user_id", user_id)
            .eq("is_active", True)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

    def deactivate_user_roadmaps(self, user_id: str) -> None:
        self.client.table(self.table_name).update({"is_active": False}).eq("user_id", user_id).execute()

    def create_roadmap_item(
        self,
        roadmap_id: str,
        phase_number: int,
        title: str,
        description: str,
        skill_id: Optional[str] = None
    ) -> Dict[str, Any]:
        payload = {
            "roadmap_id": roadmap_id,
            "phase_number": phase_number,
            "title": title,
            "description": description,
            "skill_id": skill_id,
            "is_completed": False
        }
        res = self.client.table("roadmap_items").insert(payload).execute()
        return res.data[0] if res.data else {}

    def mark_item_completed(self, item_id: str) -> Dict[str, Any]:
        from datetime import datetime, timezone
        payload = {
            "is_completed": True,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
        res = self.client.table("roadmap_items").update(payload).eq("id", item_id).execute()
        return res.data[0] if res.data else {}