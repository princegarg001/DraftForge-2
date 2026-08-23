from app.core.exceptions import BaseAppException
from app.services.parsing.base_parser import BaseParser
from app.services.parsing.docx_parser import DocxParser
from app.services.parsing.pdf_parser import PDFParser
from app.services.parsing.txt_parser import TxtParser
from app.utils.file_utils import extract_filename_and_ext


class ParserFactory:
    @staticmethod
    def get_parser_for_file(filename: str) -> BaseParser:
        _, ext = extract_filename_and_ext(filename)
        if ext == "pdf":
            return PDFParser()
        elif ext == "docx":
            return DocxParser()
        elif ext == "txt":
            return TxtParser()
        else:
            raise BaseAppException(
                status_code=415,
                detail=f"No parser available for extension '{ext}'. Supported: pdf, docx, txt"
            )