import io
from pypdf import PdfReader
from app.core.exceptions import BaseAppException, ValidationFailedError
from app.core.logging import get_logger
from app.services.parsing.base_parser import BaseParser, ParsedDocument, ParsedPage
from app.utils.text_utils import clean_extracted_text

logger = get_logger("pdf_parser")

# A crafted PDF can declare enormous page counts to exhaust CPU and memory
# during extraction. No legitimate student draft approaches this.
MAX_PDF_PAGES = 500


class PDFParser(BaseParser):
    def parse(self, content: bytes, original_filename: str) -> ParsedDocument:
        try:
            reader = PdfReader(io.BytesIO(content))

            if reader.is_encrypted:
                raise ValidationFailedError(
                    "This PDF is password-protected. Remove the protection and upload it again."
                )

            page_count = len(reader.pages)
            if page_count > MAX_PDF_PAGES:
                raise ValidationFailedError(
                    f"This PDF has {page_count} pages, which exceeds the {MAX_PDF_PAGES}-page limit."
                )

            pages: list[ParsedPage] = []
            full_text_parts: list[str] = []

            for idx, page in enumerate(reader.pages, start=1):
                extracted = page.extract_text() or ""
                cleaned = clean_extracted_text(extracted)
                pages.append(ParsedPage(page_number=idx, text=cleaned))
                if cleaned:
                    full_text_parts.append(cleaned)

            combined_text = "\n\n".join(full_text_parts)
            return ParsedDocument(
                raw_text=combined_text,
                pages=pages,
                total_pages=len(reader.pages),
                metadata={"num_pages": len(reader.pages), "source_format": "pdf"}
            )
        except BaseAppException:
            raise
        except Exception as exc:
            # The underlying pypdf message can echo document internals back to
            # the uploader; it stays in the log only.
            logger.error(f"PDF extraction error on file '{original_filename}': {exc.__class__.__name__}: {exc}")
            raise ValidationFailedError(
                "This PDF could not be read. It may be corrupted or use an unsupported format."
            ) from exc