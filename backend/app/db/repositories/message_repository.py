from typing import Any, Dict, List
from app.db.repositories.base_repository import BaseRepository


class MessageRepository(BaseRepository):
    def __init__(self):
        super().__init__(table_name="messages")

    def get_recent_messages(self, conversation_id: str, limit: int = 6) -> List[Dict[str, Any]]:
        res = (
            self.client.table(self.table_name)
            .select("*")
            .eq("conversation_id", conversation_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        # Reverse to chronological order
        return list(reversed(res.data or []))

    def get_all_messages_for_summary(self, conversation_id: str) -> List[Dict[str, Any]]:
        res = (
            self.client.table(self.table_name)
            .select("*")
            .eq("conversation_id", conversation_id)
            .order("created_at", desc=False)
            .execute()
        )
        return res.data or []

    def count_messages(self, conversation_id: str) -> int:
        res = self.client.table(self.table_name).select("id", count="exact").eq("conversation_id", conversation_id).execute()
        return res.count or 0