from typing import Optional
from app.ai.memory.conversation_memory import ConversationMemory
from app.ai.memory.document_memory import DocumentMemory
from app.ai.memory.models import ConversationContext
from app.ai.memory.summary_memory import SummaryMemory
from app.ai.memory.user_memory import UserLearningMemory


class MemoryManager:
    """Central orchestrator for assembling multi-tier memory for LLM prompts."""

    def __init__(self):
        self.conv_memory = ConversationMemory()
        self.summary_memory = SummaryMemory()
        self.user_memory = UserLearningMemory()
        self.doc_memory = DocumentMemory()

    def build_context(
        self,
        user_id: str,
        conversation_id: str,
        draft_id: Optional[str] = None
    ) -> ConversationContext:
        # 1. Sliding window messages
        recent = self.conv_memory.get_recent_window(conversation_id=conversation_id, limit=6)

        # 2. Conversation summary
        summary = self.summary_memory.get_summary(conversation_id=conversation_id)

        # 3. User learning profile
        u_mem = self.user_memory.get_user_memory(user_id=user_id)

        # 4. Draft-level memory
        d_summary = None
        if draft_id:
            d_mem = self.doc_memory.get_document_memory(draft_id=draft_id)
            if d_mem:
                d_summary = (
                    f"Draft Summary: {d_mem['document_summary']}\n"
                    f"Clauses present: {', '.join(d_mem['key_clauses_present'])}\n"
                    f"Identified Gaps: {', '.join(d_mem['identified_gaps'])}"
                )

        return ConversationContext(
            conversation_id=conversation_id,
            summary=summary,
            recent_messages=recent,
            user_memory_notes=u_mem.get("learning_notes"),
            frequent_mistakes=u_mem.get("frequent_mistakes", []),
            document_memory_notes=d_summary
        )