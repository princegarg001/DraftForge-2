from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel
from app.db.supabase import get_supabase_admin_client

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.client = get_supabase_admin_client()

    def get_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        response = self.client.table(self.table_name).select("*").eq("id", entity_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None

    def list_all(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        response = self.client.table(self.table_name).select("*").range(offset, offset + limit - 1).execute()
        return response.data or []

    def create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = self.client.table(self.table_name).insert(payload).execute()
        return response.data[0]

    def update(self, entity_id: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        response = self.client.table(self.table_name).update(payload).eq("id", entity_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None

    def delete(self, entity_id: str) -> bool:
        response = self.client.table(self.table_name).delete().eq("id", entity_id).execute()
        return len(response.data) > 0