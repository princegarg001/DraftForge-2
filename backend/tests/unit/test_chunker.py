from app.ai.rag.chunking.legal_chunker import LegalClauseChunker
from app.services.parsing.base_parser import ParsedDocument, ParsedPage


def test_legal_chunker_section_and_clauses():
    text = (
        "EMPLOYMENT AGREEMENT\n\n"
        "1. APPOINTMENT AND DUTIES\n"
        "The Employee is appointed as Counsel.\n\n"
        "2. REMUNERATION\n"
        "Salary is INR 1,00,000 per month.\n\n"
        "VERIFICATION\n"
        "Verified true and correct."
    )
    pages = [ParsedPage(page_number=1, text=text)]
    doc = ParsedDocument(raw_text=text, pages=pages, total_pages=1)

    chunker = LegalClauseChunker()
    chunks = chunker.chunk(doc, "doc_123")

    assert len(chunks) >= 2
    sections = [c.section for c in chunks]
    assert any("Appointment" in s or "Preamble" in s or "Remuneration" in s for s in sections)