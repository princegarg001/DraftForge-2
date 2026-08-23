import re
import uuid
from typing import List
from app.ai.rag.chunking.base_chunker import BaseLegalChunker
from app.ai.rag.chunking.models import LegalChunk
from app.services.parsing.base_parser import ParsedDocument


class LegalClauseChunker(BaseLegalChunker):
    """
    Legal-aware structural chunker. Preserves clause boundaries, section headers,
    and numbered provisions common in Indian legal documents (Affidavits, Agreements, Notices).
    """

    # Matches numbered clauses: "1.", "1.1", "(a)", "Clause 1:", "SECTION 2", "WHEREFORE", "VERIFICATION"
    CLAUSE_PATTERN = re.compile(
        r"(?=(?:^|\n)(?:\d+\.|\d+\.\d+|\([a-z0-9]\)|(?:Clause|Section|Article)\s+\d+|WHEREAS|NOW THEREFORE|VERIFICATION|IN WITNESS WHEREOF))",
        re.IGNORECASE | re.MULTILINE
    )

    SECTION_PATTERN = re.compile(
        r"^(?:(?:Clause|Section|Article)\s+\d+[:\.\-]?\s*([A-Za-z\s]+)|([A-Z\s]{4,}):?)",
        re.MULTILINE
    )

    def chunk(self, parsed_doc: ParsedDocument, document_id: str) -> List[LegalChunk]:
        chunks: List[LegalChunk] = []
        current_section = "Preamble"

        for page in parsed_doc.pages:
            page_text = page.text.strip()
            if not page_text:
                continue

            raw_splits = self.CLAUSE_PATTERN.split(page_text)
            for split in raw_splits:
                cleaned = split.strip()
                if len(cleaned) < 25:
                    continue  # Filter out noise fragments

                # Check if this chunk defines a section header
                sec_match = self.SECTION_PATTERN.search(cleaned)
                if sec_match:
                    found_sec = sec_match.group(1) or sec_match.group(2)
                    if found_sec:
                        current_section = found_sec.strip().title()

                # Infer clause identifier
                clause_id = None
                first_line = cleaned.splitlines()[0][:30]
                num_match = re.match(r"^(\d+(\.\d+)?|\([a-z0-9]\))", first_line)
                if num_match:
                    clause_id = num_match.group(1)

                chunk_type = "clause"
                if "verification" in cleaned.lower():
                    chunk_type = "verification"
                elif "whereas" in cleaned.lower() or "now therefore" in cleaned.lower():
                    chunk_type = "preamble"

                chunk_obj = LegalChunk(
                    chunk_id=f"{document_id}_{uuid.uuid4().hex[:8]}",
                    content=cleaned,
                    section=current_section,
                    clause_id=clause_id,
                    page_number=page.page_number,
                    chunk_type=chunk_type,
                    metadata={"document_id": document_id}
                )
                chunks.append(chunk_obj)

        if not chunks and parsed_doc.raw_text:
            # Fallback if no clause headers matched
            chunks.append(
                LegalChunk(
                    chunk_id=f"{document_id}_{uuid.uuid4().hex[:8]}",
                    content=parsed_doc.raw_text[:2000],
                    section="Main Body",
                    page_number=1,
                    chunk_type="section",
                    metadata={"document_id": document_id}
                )
            )

        return chunks