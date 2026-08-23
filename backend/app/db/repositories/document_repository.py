from typing import Any, Dict, List, Optional
from app.core.constants import DocumentType
from app.db.repositories.base_repository import BaseRepository


class DocumentRepository(BaseRepository):
    def __init__(self):
        super().__init__(table_name="reference_documents")

    def get_by_hash(self, file_hash: str) -> Optional[Dict[str, Any]]:
        response = self.client.table(self.table_name).select("*").eq("file_hash", file_hash).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None

    def list_by_type(self, doc_type: DocumentType) -> List[Dict[str, Any]]:
        response = self.client.table(self.table_name).select("*").eq("document_type", doc_type.value).execute()
        return response.data or []