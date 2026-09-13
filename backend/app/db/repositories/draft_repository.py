from typing import Any, Dict, List, Optional
from app.db.repositories.base_repository import BaseRepository


class DraftRepository(BaseRepository):
    def __init__(self):
        super().__init__(table_name="drafts")

    def list_user_drafts(self, user_id: str) -> List[Dict[str, Any]]:
        response = (
            self.client.table(self.table_name)
            .select("*, draft_versions(*)")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return response.data or []

    def get_draft_with_versions(self, draft_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        response = (
            self.client.table(self.table_name)
            .select("*, draft_versions(*)")
            .eq("id", draft_id)
            .eq("user_id", user_id)
            .execute()
        )
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None

    def create_version(self, draft_id: str, version_number: int, content: str, storage_path: Optional[str] = None, file_hash: Optional[str] = None) -> Dict[str, Any]:
        payload = {
            "draft_id": draft_id,
            "version_number": version_number,
            "raw_content": content,
            "storage_path": storage_path,
            "file_hash": file_hash,
        }
        res = self.client.table("draft_versions").insert(payload).execute()
        return res.data[0]

    def get_latest_version(self, draft_id: str) -> Optional[Dict[str, Any]]:
        res = (
            self.client.table("draft_versions")
            .select("*")
            .eq("draft_id", draft_id)
            .order("version_number", desc=True)
            .limit(1)
            .execute()
        )
        if res.data and len(res.data) > 0:
            return res.data[0]
        return None

    def get_version_by_id(self, version_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a draft version by its own id.

        Callers must check the returned ``draft_id`` against a draft they have
        already confirmed the user owns - this lookup is unscoped on its own.
        """
        res = (
            self.client.table("draft_versions")
            .select("*")
            .eq("id", version_id)
            .limit(1)
            .execute()
        )
        if res.data:
            return res.data[0]
        return None

    def get_version_by_number(self, draft_id: str, version_number: int) -> Optional[Dict[str, Any]]:
        res = (
            self.client.table("draft_versions")
            .select("*")
            .eq("draft_id", draft_id)
            .eq("version_number", version_number)
            .execute()
        )
        if res.data and len(res.data) > 0:
            return res.data[0]
        return None