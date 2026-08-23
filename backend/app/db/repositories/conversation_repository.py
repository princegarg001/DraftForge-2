from typing import Any, Dict, List, Optional
from app.db.supabase import get_supabase_admin_client
from app.core.logging import get_logger

logger = get_logger("conversation_repo")


class ConversationRepository:
    def __init__(self):
        self.supabase = get_supabase_admin_client()
        self._messages_table = "messages"

    def create_conversation(self, user_id: str, title: str) -> Dict[str, Any]:
        payload = {"user_id": user_id, "title": title}
        res = self.supabase.table("conversations").insert(payload).execute()
        return res.data[0] if res.data else payload

    def list_conversations_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        try:
            res = (
                self.supabase.table("conversations")
                .select("*, conversation_summaries(*)")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .execute()
            )
            return res.data or []
        except Exception:
            res = (
                self.supabase.table("conversations")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .execute()
            )
            return res.data or []

    def get_user_conversations(self, user_id: str) -> List[Dict[str, Any]]:
        return self.list_conversations_by_user(user_id)

    def list_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        return self.list_conversations_by_user(user_id)

    def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        for tbl in [self._messages_table, "chat_messages"]:
            try:
                res = (
                    self.supabase.table(tbl)
                    .select("*")
                    .eq("conversation_id", conversation_id)
                    .order("created_at", desc=False)
                    .execute()
                )
                self._messages_table = tbl
                return res.data or []
            except Exception as exc:
                logger.debug(f"Table '{tbl}' query failed ({exc}), attempting fallback...")
        return []

    def save_message(self, message_record: Dict[str, Any]) -> Dict[str, Any]:
        for tbl in [self._messages_table, "chat_messages"]:
            try:
                res = self.supabase.table(tbl).insert(message_record).execute()
                self._messages_table = tbl
                return res.data[0] if res.data else message_record
            except Exception as exc:
                logger.debug(f"Save to '{tbl}' failed ({exc}), attempting fallback...")
        return message_record