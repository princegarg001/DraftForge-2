from typing import Optional
from app.ai.llm.base import LLMMessage
from app.ai.llm.factory import LLMFactory
from app.core.logging import get_logger
from app.db.repositories.conversation_repository import ConversationRepository
from app.db.repositories.message_repository import MessageRepository

logger = get_logger("summary_memory")


class SummaryMemory:
    """Progressive background summarizer for long-running tutoring conversations."""

    def __init__(self):
        self.conv_repo = ConversationRepository()
        self.msg_repo = MessageRepository()
        self.llm = LLMFactory.get_llm()

    def get_summary(self, conversation_id: str) -> Optional[str]:
        return self.conv_repo.get_summary(conversation_id)

    async def update_summary_if_needed(self, conversation_id: str, force: bool = False) -> Optional[str]:
        total_messages = self.msg_repo.count_messages(conversation_id)
        # Summarize every 8 messages or if forced
        if not force and (total_messages < 8 or total_messages % 8 != 0):
            return None

        all_msgs = self.msg_repo.get_all_messages_for_summary(conversation_id)
        if not all_msgs:
            return None

        transcript = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in all_msgs])
        current_summary = self.get_summary(conversation_id) or "None"

        prompt = (
            "You are a memory condensation assistant for a legal drafting tutor.\n"
            "Synthesize the ongoing conversation into a concise 1-2 paragraph memory brief.\n"
            "Capture: key drafting doubts raised, student strengths, specific document clauses discussed, and current status.\n\n"
            f"EXISTING SUMMARY: {current_summary}\n\n"
            f"NEW CONVERSATION TRANSCRIPT:\n{transcript}\n\n"
            "CONCISE UPDATED SUMMARY:"
        )

        messages = [LLMMessage(role="system", content="You create concise conversation memory summaries."), LLMMessage(role="user", content=prompt)]

        try:
            res = await self.llm.generate(messages=messages, temperature=0.1, max_tokens=500)
            new_summary = res.content.strip()
            self.conv_repo.upsert_summary(
                conversation_id=conversation_id,
                summary_text=new_summary,
                last_message_id=all_msgs[-1]["id"]
            )
            logger.info(f"Updated conversation summary for {conversation_id}")
            return new_summary
        except Exception as exc:
            logger.error(f"Failed to generate conversation summary: {exc}")
            return None