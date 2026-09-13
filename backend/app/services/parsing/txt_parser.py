from app.core.exceptions import ValidationFailedError
from app.services.parsing.base_parser import BaseParser, ParsedDocument, ParsedPage
from app.utils.text_utils import clean_extracted_text


class TxtParser(BaseParser):
    def parse(self, content: bytes, original_filename: str) -> ParsedDocument:
        try:
            # Attempt UTF-8 decode, fallback to latin-1
            try:
                decoded = content.decode("utf-8")
            except UnicodeDecodeError:
                decoded = content.decode("latin-1")

            cleaned = clean_extracted_text(decoded)
            pages = [ParsedPage(page_number=1, text=cleaned)]
            return ParsedDocument(
                raw_text=cleaned,
                pages=pages,
                total_pages=1,
                metadata={"source_format": "txt"}
            )
        except Exception as exc:
            raise ValidationFailedError(
                "This text file could not be decoded. Save it as UTF-8 and try again."
            ) from exc