from abc import ABC, abstractmethod
from typing import List
from app.ai.rag.chunking.models import LegalChunk
from app.services.parsing.base_parser import ParsedDocument


class BaseLegalChunker(ABC):
    @abstractmethod
    def chunk(self, parsed_doc: ParsedDocument, document_id: str) -> List[LegalChunk]:
        """Divides parsed document text into semantically cohesive legal chunks."""
        pass