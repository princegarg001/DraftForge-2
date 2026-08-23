from typing import Any, Dict, Optional
from app.db.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(table_name="profiles")

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        response = self.client.table(self.table_name).select("*").eq("email", email).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None

    def upsert_profile(self, user_id: str, email: str, role: str, full_name: Optional[str] = None) -> Dict[str, Any]:
        payload = {
            "id": user_id,
            "email": email,
            "role": role,
            "full_name": full_name,
        }
        response = self.client.table(self.table_name).upsert(payload).execute()
        return response.data[0]