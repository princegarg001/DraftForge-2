import re
from typing import Any, Dict, List, Optional
from app.ai.llm.base import LLMMessage
from app.ai.llm.factory import get_llm
from app.core.logging import get_logger

logger = get_logger("tutor_agent")


def strip_reasoning_tags(text: str) -> str:
    """Removes <think>...</think> reasoning tags and trims trailing whitespace."""
    if not text:
        return ""
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned.strip()


class TutorAgent:
    """Interactive Socratic Indian Legal Drafting Tutor."""

    def __init__(self):
        self.llm = get_llm()

    async def guide_student(
        self,
        query: str,
        document_type: Optional[str] = "AFFIDAVIT_OF_CHARACTER",
        history: Optional[List[Dict[str, str]]] = None,
        retrieved_sources: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        sources_context = ""
        if retrieved_sources:
            sources_context = "\n\nReference Corpus Clauses:\n" + "\n---\n".join(
                [f"[{s.get('source_document', 'Doc')} - {s.get('section', 'Clause')}]:\n{s.get('content', '')}"
                 for s in retrieved_sources]
            )

        system_prompt = (
            "You are an interactive, Socratic Indian Legal Drafting Tutor specializing in Indian law "
            "(e.g., Indian Evidence Act, Bharatiya Sakshya Adhiniyam, Code of Civil Procedure, Indian Contract Act).\n"
            "Pedagogical Guidelines:\n"
            "1. Guide the student step-by-step using the Socratic method.\n"
            "2. Never give the complete finished legal document at once unless specifically requested.\n"
            "3. Ask targeted guiding questions to verify necessary elements (deponent details, verification clauses, non-compete enforceability under Section 27, etc.).\n"
            "4. Keep your explanations concise, encouraging, and clear."
        )

        messages = [LLMMessage(role="system", content=system_prompt + sources_context)]

        if history:
            for turn in history:
                messages.append(LLMMessage(role=turn.get("role", "user"), content=turn.get("content", "")))

        messages.append(LLMMessage(role="user", content=query))

        try:
            response = await self.llm.generate(
                messages=messages,
                temperature=0.3,
                max_tokens=1024
            )
            return strip_reasoning_tags(response.content)
        except Exception as exc:
            logger.error(f"TutorAgent inference failed: {exc}")
            return "I am here to guide you through your legal draft. What specific clause or document structure would you like to review first?"

    # Method Aliases
    async def answer_student_query(
        self,
        query: str,
        document_type: Optional[str] = "AFFIDAVIT_OF_CHARACTER",
        history: Optional[List[Dict[str, str]]] = None,
        retrieved_sources: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        return await self.guide_student(query, document_type, history, retrieved_sources)

    async def chat(self, *args, **kwargs) -> str:
        return await self.guide_student(*args, **kwargs)