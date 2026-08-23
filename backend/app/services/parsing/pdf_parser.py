import io
from pypdf import PdfReader
from app.core.exceptions import BaseAppException
from app.core.logging import get_logger
from app.services.parsing.base_parser import BaseParser, ParsedDocument, ParsedPage
from app.utils.text_utils import clean_extracted_text

logger = get_logger("pdf_parser")


class PDFParser(BaseParser):
    def parse(self, content: bytes, original_filename: str) -> ParsedDocument:
        try:
            reader = PdfReader(io.BytesIO(content))
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
        except Exception as exc:
            logger.error(f"PDF extraction error on file '{original_filename}': {exc}")
            raise BaseAppException(status_code=422, detail=f"PDF parsing failed: {str(exc)}") from exc