from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class LegalChunk(BaseModel):
    chunk_id: str
    content: str
    section: str = "General"
    subsection: Optional[str] = None
    clause_id: Optional[str] = None
    page_number: Optional[int] = 1
    chunk_type: str = "clause"  # 'preamble', 'section', 'clause', 'verification'
    metadata: Dict[str, str] = Field(default_factory=dict)