from typing import Any, Dict, List, Optional
from app.db.supabase import get_supabase_admin_client


class DocumentMemory:
    """Stores draft-specific context, clause status, and persistent evaluation findings."""

    def __init__(self):
        self.client = get_supabase_admin_client()
        self.table = "document_memory"

    def get_document_memory(self, draft_id: str) -> Optional[Dict[str, Any]]:
        res = self.client.table(self.table).select("*").eq("draft_id", draft_id).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
        return None

    def upsert_document_memory(
        self,
        draft_id: str,
        summary: str,
        clauses_present: List[str],
        gaps: List[str]
    ) -> Dict[str, Any]:
        from datetime import datetime, timezone
        payload = {
            "draft_id": draft_id,
            "document_summary": summary,
            "key_clauses_present": clauses_present,
            "identified_gaps": gaps,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        res = self.client.table(self.table).upsert(payload).execute()
        return res.data[0] if res.data else {}