"""Upload validation.

The previous checks were bypassable in two ways:

* ``if file.content_type and file.content_type in ALLOWED_MIME_TYPES`` - the
  guard was skipped entirely when the header was absent, and the header is
  client-supplied in any case.
* The extension check read the client-supplied filename, which is trivially
  renamed.

Content type is now decided by inspecting the leading bytes of the file, so the
declared type and filename are treated as hints to cross-check rather than as
the decision. Filenames are additionally sanitized before they are ever used to
build a storage path.
"""

from __future__ import annotations

import re
import unicodedata
import zipfile
from io import BytesIO
from typing import Final

import filetype
from fastapi import UploadFile

from app.config import get_settings
from app.core.exceptions import PayloadTooLargeError, UnsupportedMediaTypeError, ValidationFailedError
from app.core.logging import get_logger

logger = get_logger("file_security")
settings = get_settings()

ALLOWED_EXTENSIONS: Final[frozenset[str]] = frozenset({"pdf", "docx", "txt"})

ALLOWED_MIME_TYPES: Final[frozenset[str]] = frozenset(
    {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    }
)

# Leading-byte signatures. DOCX is a ZIP container, so it shares the PK header
# with every other OOXML format and is disambiguated separately below.
_PDF_MAGIC: Final[bytes] = b"%PDF-"
_ZIP_MAGIC: Final[tuple[bytes, ...]] = (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")

_UNSAFE_FILENAME_CHARS = re.compile(r"[^A-Za-z0-9._-]")
_MAX_FILENAME_LENGTH = 120

# A zip whose declared uncompressed size dwarfs its compressed size is a
# decompression bomb. Legitimate DOCX files sit far below this.
_MAX_DOCX_COMPRESSION_RATIO = 200
_MAX_DOCX_UNCOMPRESSED_BYTES = 300 * 1024 * 1024


def sanitize_filename(filename: str) -> str:
    """Reduce a client-supplied filename to something safe to store.

    Strips directory components, control characters and Unicode trickery.
    Without this, a name like ``../../etc/passwd`` or one containing a
    right-to-left override can escape or disguise its intended storage path.
    """
    if not filename:
        return "upload"

    # Take the basename under both separators - the client may send either.
    name = filename.replace("\\", "/").rsplit("/", 1)[-1]
    name = unicodedata.normalize("NFKC", name)
    name = "".join(ch for ch in name if ch.isprintable() and unicodedata.category(ch) != "Cf")
    name = _UNSAFE_FILENAME_CHARS.sub("_", name).lstrip(".") or "upload"

    if len(name) > _MAX_FILENAME_LENGTH:
        stem, _, ext = name.rpartition(".")
        keep = _MAX_FILENAME_LENGTH - len(ext) - 1
        name = f"{stem[:keep]}.{ext}" if ext and keep > 0 else name[:_MAX_FILENAME_LENGTH]

    return name


def _extension_of(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def _is_docx(content: bytes) -> bool:
    """Confirm a ZIP container is genuinely a WordprocessingML document."""
    try:
        with zipfile.ZipFile(BytesIO(content)) as archive:
            names = set(archive.namelist())
            if "[Content_Types].xml" not in names or "word/document.xml" not in names:
                return False

            total_uncompressed = 0
            for info in archive.infolist():
                total_uncompressed += info.file_size
                if total_uncompressed > _MAX_DOCX_UNCOMPRESSED_BYTES:
                    logger.warning("Rejected DOCX: uncompressed size exceeds ceiling.")
                    return False
                if info.compress_size > 0:
                    ratio = info.file_size / info.compress_size
                    if ratio > _MAX_DOCX_COMPRESSION_RATIO:
                        logger.warning(f"Rejected DOCX: compression ratio {ratio:.0f}:1 on {info.filename}")
                        return False
            return True
    except (zipfile.BadZipFile, OSError):
        return False


def _looks_like_text(content: bytes) -> bool:
    """Heuristic for plain text: decodable and free of NUL bytes."""
    if b"\x00" in content[:8192]:
        return False
    try:
        content[:8192].decode("utf-8")
        return True
    except UnicodeDecodeError:
        # Latin-1 always decodes, so fall back to a printable-ratio test.
        sample = content[:8192]
        printable = sum(1 for b in sample if 0x20 <= b < 0x7F or b in (0x09, 0x0A, 0x0D))
        return bool(sample) and (printable / len(sample)) > 0.85


def detect_content_type(content: bytes, declared_extension: str) -> str:
    """Determine the real media type from the file's own bytes."""
    if content.startswith(_PDF_MAGIC):
        return "application/pdf"

    if content.startswith(_ZIP_MAGIC):
        if _is_docx(content):
            return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        raise UnsupportedMediaTypeError(
            "This appears to be a ZIP archive rather than a Word document."
        )

    # filetype recognises a wide set of binary formats; anything it identifies
    # here is by definition not one of the three we accept.
    guess = filetype.guess(content)
    if guess is not None:
        raise UnsupportedMediaTypeError(
            f"Files of type '{guess.mime}' are not accepted. Upload a PDF, DOCX or TXT file."
        )

    if declared_extension == "txt" and _looks_like_text(content):
        return "text/plain"

    if _looks_like_text(content):
        return "text/plain"

    raise UnsupportedMediaTypeError("The file content is not a readable PDF, DOCX or TXT document.")


def validate_uploaded_file(file: UploadFile, content: bytes) -> str:
    """Validate an upload and return its verified media type.

    Raises on anything that is not a genuine PDF, DOCX or TXT file within the
    configured size limit.
    """
    if not content:
        raise ValidationFailedError("The uploaded file is empty.")

    if len(content) > settings.MAX_UPLOAD_BYTES:
        raise PayloadTooLargeError(settings.MAX_UPLOAD_BYTES)

    safe_name = sanitize_filename(file.filename or "")
    extension = _extension_of(safe_name)

    if extension not in ALLOWED_EXTENSIONS:
        raise UnsupportedMediaTypeError(
            f"Unsupported file extension. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}."
        )

    detected = detect_content_type(content, extension)

    # The extension must agree with what the bytes actually are, so a renamed
    # file is rejected rather than silently parsed as the wrong format.
    expected_for_extension = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "txt": "text/plain",
    }[extension]

    if detected != expected_for_extension:
        logger.warning(
            f"Upload rejected: extension '.{extension}' does not match detected type '{detected}'"
        )
        raise UnsupportedMediaTypeError(
            f"This file's contents do not match its .{extension} extension."
        )

    return detected
