"""Regression tests for upload validation.

Each test pins a bypass that the previous implementation allowed.
"""

from __future__ import annotations

import io
import zipfile

import pytest
from fastapi import UploadFile

from app.core.exceptions import PayloadTooLargeError, UnsupportedMediaTypeError, ValidationFailedError
from app.core.file_security import detect_content_type, sanitize_filename, validate_uploaded_file

pytestmark = pytest.mark.security

MINIMAL_PDF = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n"
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def make_docx(extra_size: int = 0) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", "<Types/>")
        archive.writestr("word/document.xml", "<document/>" + ("x" * extra_size))
    return buffer.getvalue()


class TestFilenameSanitization:
    @pytest.mark.parametrize(
        "raw,forbidden",
        [
            ("../../../etc/passwd", "/"),
            ("..\\..\\windows\\system32\\config", "\\"),
            ("/absolute/path/doc.pdf", "/"),
        ],
    )
    def test_strips_directory_traversal(self, raw: str, forbidden: str) -> None:
        result = sanitize_filename(raw)
        assert forbidden not in result
        assert ".." not in result

    def test_strips_bidi_override(self) -> None:
        # U+202E disguises "exe.pdf" as "fdp.exe" in a file listing.
        assert "‮" not in sanitize_filename("invoice‮gpj.exe")

    def test_strips_control_characters(self) -> None:
        result = sanitize_filename("draft\x00\x0a\x0dname.pdf")
        assert "\x00" not in result and "\n" not in result

    def test_caps_length(self) -> None:
        assert len(sanitize_filename("a" * 500 + ".pdf")) <= 120

    def test_never_returns_empty(self) -> None:
        assert sanitize_filename("") == "upload"
        assert sanitize_filename("...") == "upload"


class TestContentTypeDetection:
    def test_detects_pdf_from_magic_bytes(self) -> None:
        assert detect_content_type(MINIMAL_PDF, "pdf") == "application/pdf"

    def test_detects_docx_from_container_structure(self) -> None:
        assert detect_content_type(make_docx(), "docx") == DOCX_MIME

    def test_rejects_plain_zip_masquerading_as_docx(self) -> None:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("payload.txt", "not a word document")
        with pytest.raises(UnsupportedMediaTypeError):
            detect_content_type(buffer.getvalue(), "docx")

    def test_rejects_executable_renamed_to_pdf(self) -> None:
        # An ELF binary named .pdf previously passed on extension alone.
        with pytest.raises(UnsupportedMediaTypeError):
            detect_content_type(b"\x7fELF\x02\x01\x01\x00" + b"\x00" * 64, "pdf")

    def test_rejects_decompression_bomb(self) -> None:
        # Highly compressible payload: a small archive declaring a huge
        # uncompressed size.
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("[Content_Types].xml", "<Types/>")
            archive.writestr("word/document.xml", "\0" * (80 * 1024 * 1024))
        with pytest.raises(UnsupportedMediaTypeError):
            detect_content_type(buffer.getvalue(), "docx")


class TestValidateUploadedFile:
    def test_accepts_genuine_pdf(self) -> None:
        file = UploadFile(filename="affidavit.pdf", file=io.BytesIO(MINIMAL_PDF))
        assert validate_uploaded_file(file, MINIMAL_PDF) == "application/pdf"

    def test_rejects_empty_file(self) -> None:
        file = UploadFile(filename="empty.pdf", file=io.BytesIO(b""))
        with pytest.raises(ValidationFailedError):
            validate_uploaded_file(file, b"")

    def test_rejects_extension_content_mismatch(self) -> None:
        # A real PDF named .txt must not be accepted as text.
        file = UploadFile(filename="notes.txt", file=io.BytesIO(MINIMAL_PDF))
        with pytest.raises(UnsupportedMediaTypeError):
            validate_uploaded_file(file, MINIMAL_PDF)

    def test_rejects_disallowed_extension(self) -> None:
        file = UploadFile(filename="script.exe", file=io.BytesIO(MINIMAL_PDF))
        with pytest.raises(UnsupportedMediaTypeError):
            validate_uploaded_file(file, MINIMAL_PDF)

    def test_rejects_oversized_file(self) -> None:
        from app.config import get_settings

        oversized = MINIMAL_PDF + b"\x00" * (get_settings().MAX_UPLOAD_BYTES + 1)
        file = UploadFile(filename="huge.pdf", file=io.BytesIO(oversized))
        with pytest.raises(PayloadTooLargeError):
            validate_uploaded_file(file, oversized)

    def test_missing_content_type_header_still_validates(self) -> None:
        """The old guard was `if file.content_type and ...`, so an absent
        header skipped MIME validation entirely."""
        evil = b"\x7fELF\x02\x01\x01\x00" + b"\x00" * 64
        file = UploadFile(filename="payload.pdf", file=io.BytesIO(evil))
        with pytest.raises(UnsupportedMediaTypeError):
            validate_uploaded_file(file, evil)
