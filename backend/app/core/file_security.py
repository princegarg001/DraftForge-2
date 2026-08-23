from typing import Set
from fastapi import UploadFile
from app.core.exceptions import BaseAppException

ALLOWED_MIME_TYPES: Set[str] = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}

ALLOWED_EXTENSIONS: Set[str] = {"pdf", "docx", "txt"}
MAX_FILE_SIZE_BYTES: int = 15 * 1024 * 1024  # 15 MB limit


def validate_uploaded_file(file: UploadFile, content: bytes) -> None:
    """
    Validates uploaded file size, MIME type, and extension for security compliance.
    """
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise BaseAppException(
            status_code=413,
            detail=f"File size ({len(content)} bytes) exceeds the maximum allowed limit of {MAX_FILE_SIZE_BYTES} bytes (15 MB)."
        )

    if not file.filename:
        raise BaseAppException(status_code=400, detail="Missing file name.")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise BaseAppException(
            status_code=415,
            detail=f"Unsupported file extension '.{ext}'. Allowed extensions: {list(ALLOWED_EXTENSIONS)}"
        )

    # Basic MIME validation
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        raise BaseAppException(
            status_code=415,
            detail=f"Unsupported MIME type '{file.content_type}'. Allowed types: {list(ALLOWED_MIME_TYPES)}"
        )