import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.ai.agents.tutor_agent import TutorAgent
from app.ai.embeddings.fastembed_provider import FastEmbedProvider
from app.config import get_settings
from app.core.logging import get_logger
from app.db.repositories.conversation_repository import ConversationRepository
from app.db.qdrant import get_qdrant_client

logger = get_logger("tutor_pipeline")
settings = get_settings()


class TutorPipeline:
    """End-to-end pipeline for grounding student queries with reference templates and generating Socratic tutoring guidance."""

    def __init__(self):
        self.tutor_agent = TutorAgent()
        self.embedder = FastEmbedProvider()
        self.repo = ConversationRepository()
        self.collection_name = settings.QDRANT_COLLECTION_NAME

    async def process_student_message(
        self,
        user_id: str,
        conversation_id: str,
        message_text: str,
        document_type: Optional[str] = "AFFIDAVIT_OF_CHARACTER"
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        # 1. Save user message to database
        user_msg_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        user_message_record = {
            "id": user_msg_id,
            "conversation_id": conversation_id,
            "user_id": user_id,
            "role": "user",
            "content": message_text,
            "retrieved_sources": [],
            "created_at": now
        }
        self.repo.save_message(user_message_record)

        # 2. Retrieve grounded reference evidence chunks from Qdrant
        retrieved_sources: List[Dict[str, Any]] = []
        try:
            client = get_qdrant_client()
            query_vector = self.embedder.embed_query(message_text)

            # Handle both qdrant-client v1.10+ (query_points) and older versions (search)
            if hasattr(client, "query_points"):
                response = client.query_points(
                    collection_name=self.collection_name,
                    query=query_vector,
                    limit=3
                )
                hits = response.points
            elif hasattr(client, "search"):
                hits = client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    limit=3
                )
            else:
                hits = []

            for hit in hits:
                payload = getattr(hit, "payload", {}) or {}
                retrieved_sources.append({
                    "source_document": payload.get("source_document", "Reference Corpus"),
                    "page_number": payload.get("page_number", 1),
                    "section": payload.get("section", "Standard Clauses"),
                    "content": payload.get("text", "")
                })
        except Exception as exc:
            logger.warning(f"Qdrant evidence retrieval safely bypassed: {exc}")

        # 3. Fetch past conversation history
        past_records = self.repo.get_messages(conversation_id) or []
        history = [{"role": m.get("role", "user"), "content": m.get("content", "")} for m in past_records[-6:]]

        # 4. Generate Socratic AI response
        ai_reply_text = await self.tutor_agent.answer_student_query(
            query=message_text,
            document_type=document_type,
            history=history,
            retrieved_sources=retrieved_sources
        )

        # 5. Save assistant message to database
        ai_msg_id = str(uuid.uuid4())
        ai_message_record = {
            "id": ai_msg_id,
            "conversation_id": conversation_id,
            "user_id": user_id,
            "role": "assistant",
            "content": ai_reply_text,
            "retrieved_sources": retrieved_sources,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        self.repo.save_message(ai_message_record)

        return user_message_record, ai_message_record