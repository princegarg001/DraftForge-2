from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel


class ParsedPage(BaseModel):
    page_number: int
    text: str


class ParsedDocument(BaseModel):
    raw_text: str
    pages: List[ParsedPage]
    total_pages: int
    metadata: dict = {}


class BaseParser(ABC):
    @abstractmethod
    def parse(self, content: bytes, original_filename: str) -> ParsedDocument:
        """Parses raw document bytes and returns a standardized ParsedDocument structure."""
        pass