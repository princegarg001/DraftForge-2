from app.services.parsing.txt_parser import TxtParser
from app.services.parsing.parser_factory import ParserFactory


def test_txt_parser_clean_extraction():
    content = b"  AFFIDAVIT OF CHARACTER  \n\n\n\nI solemnly declare.  "
    parser = TxtParser()
    doc = parser.parse(content, "affidavit.txt")
    assert doc.total_pages == 1
    assert "AFFIDAVIT OF CHARACTER" in doc.raw_text
    assert "\n\n\n\n" not in doc.raw_text


def test_parser_factory_routing():
    pdf_p = ParserFactory.get_parser_for_file("doc.pdf")
    docx_p = ParserFactory.get_parser_for_file("doc.docx")
    txt_p = ParserFactory.get_parser_for_file("doc.txt")
    
    assert pdf_p.__class__.__name__ == "PDFParser"
    assert docx_p.__class__.__name__ == "DocxParser"
    assert txt_p.__class__.__name__ == "TxtParser"