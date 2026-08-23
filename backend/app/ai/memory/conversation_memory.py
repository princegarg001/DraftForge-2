from typing import List
from app.ai.memory.models import MemoryMessage
from app.db.repositories.message_repository import MessageRepository


class ConversationMemory:
    """Sliding-window recent conversation history buffer."""

    def __init__(self):
        self.message_repo = MessageRepository()

    def get_recent_window(self, conversation_id: str, limit: int = 6) -> List[MemoryMessage]:
        records = self.message_repo.get_recent_messages(conversation_id=conversation_id, limit=limit)
        return [MemoryMessage(**r) for r in records]