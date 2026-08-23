from typing import Any, List, Optional
from app.db.repositories.conversation_repository import ConversationRepository
from app.models.schemas.chat import (
    ConversationResponse,
    MessageResponse,
    SendMessageRequest,
    SendMessageResponse,
)
from app.pipelines.tutor_pipeline import TutorPipeline


class ChatService:
    def __init__(self):
        self.repo = ConversationRepository()
        self.pipeline = TutorPipeline()

    def create_conversation(self, user_id: str, title: str) -> ConversationResponse:
        rec = self.repo.create_conversation(user_id=user_id, title=title)
        return ConversationResponse(
            id=rec["id"],
            user_id=rec["user_id"],
            title=rec["title"],
            created_at=rec.get("created_at"),
            updated_at=rec.get("updated_at"),
            summary=None
        )

    def list_user_conversations(self, user_id: str) -> List[ConversationResponse]:
        records = self.repo.list_conversations_by_user(user_id) or []
        results = []
        for r in records:
            summaries = r.get("conversation_summaries")
            summary_text = None
            if isinstance(summaries, list) and len(summaries) > 0:
                summary_text = summaries[0].get("summary_text")
            elif isinstance(summaries, dict):
                summary_text = summaries.get("summary_text")

            results.append(
                ConversationResponse(
                    id=r["id"],
                    user_id=r["user_id"],
                    title=r["title"],
                    created_at=r.get("created_at"),
                    updated_at=r.get("updated_at"),
                    summary=summary_text
                )
            )
        return results

    def get_messages(self, conversation_id: str, user_id: Optional[str] = None) -> List[MessageResponse]:
        records = self.repo.get_messages(conversation_id) or []
        return [MessageResponse(**m) for m in records]

    def get_conversation_messages(self, conversation_id: str, user_id: Optional[str] = None) -> List[MessageResponse]:
        return self.get_messages(conversation_id=conversation_id, user_id=user_id)

    async def send_message(
        self,
        user_id: str,
        request: Optional[Any] = None,
        payload: Optional[Any] = None
    ) -> SendMessageResponse:
        data = payload or request
        conv_id = getattr(data, "conversation_id", None) or data.get("conversation_id")
        msg_text = getattr(data, "message", None) or data.get("message")
        doc_type = getattr(data, "document_type", None) or (data.get("document_type") if isinstance(data, dict) else "AFFIDAVIT_OF_CHARACTER")

        user_msg, ai_msg = await self.pipeline.process_student_message(
            user_id=user_id,
            conversation_id=conv_id,
            message_text=msg_text,
            document_type=doc_type
        )
        return SendMessageResponse(
            user_message=MessageResponse(**user_msg),
            ai_message=MessageResponse(**ai_msg)
        )