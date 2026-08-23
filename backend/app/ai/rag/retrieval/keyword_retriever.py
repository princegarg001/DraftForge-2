import re
from typing import Any, Dict, List, Optional
from qdrant_client.http import models as qmodels
from app.config import get_settings
from app.core.constants import DocumentType
from app.db.qdrant import get_qdrant_client

settings = get_settings()


class KeywordRetriever:
    """Keyword & metadata retriever utilizing Qdrant payload filters."""

    def __init__(self):
        self.client = get_qdrant_client()
        self.collection_name = settings.QDRANT_COLLECTION_NAME

    def retrieve_by_section(
        self,
        section_name: str,
        document_type: DocumentType,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        filter_conditions = [
            qmodels.FieldCondition(
                key="document_type",
                match=qmodels.MatchValue(value=document_type.value)
            ),
            qmodels.FieldCondition(
                key="section",
                match=qmodels.MatchText(text=section_name)
            )
        ]

        records, _ = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=qmodels.Filter(must=filter_conditions),
            limit=limit,
            with_payload=True,
        )

        return [r.payload for r in records if r.payload]