from app.config import get_settings
from app.db.storage import SupabaseStorageClient

settings = get_settings()


class StorageService:
    def __init__(self):
        self.storage = SupabaseStorageClient()

    def store_reference_document(self, filename: str, content: bytes, content_type: str) -> str:
        path = f"references/{filename}"
        return self.storage.upload_file(
            bucket=settings.SUPABASE_REFERENCE_BUCKET,
            path=path,
            file_bytes=content,
            content_type=content_type
        )

    def store_student_draft(self, user_id: str, draft_id: str, version: int, filename: str, content: bytes, content_type: str) -> str:
        path = f"{user_id}/{draft_id}/v{version}_{filename}"
        return self.storage.upload_file(
            bucket=settings.SUPABASE_DRAFT_BUCKET,
            path=path,
            file_bytes=content,
            content_type=content_type
        )