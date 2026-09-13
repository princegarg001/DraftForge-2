from typing import Optional
from app.config import get_settings
from app.core.exceptions import NotFoundError, UpstreamServiceError
from app.core.logging import get_logger
from app.db.supabase import get_supabase_admin_client

logger = get_logger("supabase_storage")
settings = get_settings()


class SupabaseStorageClient:
    """
    Manages direct interactions with Supabase Storage buckets.
    """
    def __init__(self):
        self.client = get_supabase_admin_client()

    def upload_file(self, bucket: str, path: str, file_bytes: bytes, content_type: str) -> str:
        """
        Uploads a binary file payload to a Supabase bucket and returns the storage path.
        """
        try:
            res = self.client.storage.from_(bucket).upload(
                path=path,
                file=file_bytes,
                file_options={"content-type": content_type, "upsert": "true"},
            )
            logger.info(f"File uploaded successfully to bucket '{bucket}' at path '{path}'")
            return path
        except Exception as exc:
            # Bucket names and provider errors describe internal storage
            # topology and stay out of the response.
            logger.error(f"Failed to upload file to bucket '{bucket}' at '{path}': {exc}")
            raise UpstreamServiceError("Supabase Storage", str(exc)) from exc

    def download_file(self, bucket: str, path: str) -> bytes:
        """
        Downloads a file payload from a Supabase bucket.
        """
        try:
            data = self.client.storage.from_(bucket).download(path)
            return data
        except Exception as exc:
            logger.error(f"Failed to download file from bucket '{bucket}' at '{path}': {exc}")
            raise NotFoundError("stored file") from exc

    def delete_file(self, bucket: str, path: str) -> bool:
        """
        Removes a file from a Supabase bucket.
        """
        try:
            self.client.storage.from_(bucket).remove([path])
            logger.info(f"Deleted file from bucket '{bucket}' at path '{path}'")
            return True
        except Exception as exc:
            logger.error(f"Failed to delete file from bucket '{bucket}' at '{path}': {exc}")
            return False

    def create_signed_url(self, bucket: str, path: str, expires_in: int = 3600) -> Optional[str]:
        """
        Generates a secure temporary signed URL for file access.
        """
        try:
            res = self.client.storage.from_(bucket).create_signed_url(path, expires_in)
            return res.get("signedURL") or res.get("signedUrl")
        except Exception as exc:
            logger.error(f"Failed to generate signed URL for '{bucket}/{path}': {exc}")
            return None