from typing import Any, Dict, List


class ContextBuilder:
    @staticmethod
    def build_evidence_context(chunks: List[Dict[str, Any]]) -> str:
        """
        Formats retrieved reference chunks into traceable legal evidence blocks.
        """
        if not chunks:
            return "No matching reference evidence found in knowledge base."

        formatted_blocks = []
        for idx, chunk in enumerate(chunks, start=1):
            source_doc = chunk.get("source_document", "Reference Corpus")
            page = chunk.get("page_number", 1)
            section = chunk.get("section", "General")
            clause_id = chunk.get("clause_id") or "N/A"
            content = chunk.get("content", "").strip()

            block = (
                f"[REFERENCE EVIDENCE {idx}]\n"
                f"Source: {source_doc} (Page {page})\n"
                f"Section: {section} | Clause ID: {clause_id}\n"
                f"Text:\n{content}"
            )
            formatted_blocks.append(block)

        return "\n\n---\n\n".join(formatted_blocks)