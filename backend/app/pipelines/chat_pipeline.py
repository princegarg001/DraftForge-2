from typing import Any, Dict, List, Optional
from app.ai.llm.base import BaseLLM, LLMMessage
from app.ai.llm.factory import LLMFactory
from app.ai.memory.memory_manager import MemoryManager
from app.ai.memory.models import ConversationContext
from app.ai.rag.context.context_builder import ContextBuilder
from app.ai.rag.pipeline import RAGPipeline
from app.core.constants import DocumentType
from app.core.logging import get_logger

logger = get_logger("chat_pipeline")


class ChatPipeline:
    """Orchestrates multi-tier context assembly, RAG retrieval, and LLM chat generation."""

    def __init__(self, llm: Optional[BaseLLM] = None):
        self.memory_manager = MemoryManager()
        self.rag_pipeline = RAGPipeline()
        self.llm = llm or LLMFactory.get_llm()

    async def execute_turn(
        self,
        user_id: str,
        conversation_id: str,
        user_message: str,
        document_type: Optional[DocumentType] = None,
        draft_id: Optional[str] = None,
        section_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        # 1. Assemble memory tiers
        context: ConversationContext = self.memory_manager.build_context(
            user_id=user_id,
            conversation_id=conversation_id,
            draft_id=draft_id
        )

        # 2. RAG Retrieval if doc_type is known or query has legal terms
        retrieved_sources: List[Dict[str, Any]] = []
        rag_context_str = ""
        if document_type:
            retrieved_sources = self.rag_pipeline.retrieve_reference_evidence(
                query=user_message,
                document_type=document_type,
                section_hint=section_hint,
                top_k=3
            )
            rag_context_str = ContextBuilder.build_evidence_context(retrieved_sources)

        # 3. Construct System Prompt with Assembled Memory
        system_prompt = self._build_system_prompt(context, rag_context_str)

        # 4. Assemble LLM Message Chain
        messages: List[LLMMessage] = [LLMMessage(role="system", content=system_prompt)]

        for msg in context.recent_messages:
            messages.append(LLMMessage(role=msg.role, content=msg.content))

        messages.append(LLMMessage(role="user", content=user_message))

        # 5. Generate LLM response
        res = await self.llm.generate(messages=messages, temperature=0.3, max_tokens=2048)

        # 6. Background check to update summary
        await self.memory_manager.summary_memory.update_summary_if_needed(conversation_id)

        return {
            "response": res.content,
            "model": res.model,
            "retrieved_sources": retrieved_sources,
            "summary_used": bool(context.summary)
        }

    def _build_system_prompt(self, ctx: ConversationContext, rag_context: str) -> str:
        sections = [
            "You are an interactive, Socratic Indian Legal Drafting Tutor.",
            "Ground your feedback in the provided Reference Corpus and avoid legal hallucination.",
            "Use clear, educational explanations, citing specific requirements where applicable."
        ]

        if ctx.summary:
            sections.append(f"\n[CONVERSATION BACKGROUND SUMMARY]:\n{ctx.summary}")

        if ctx.user_memory_notes or ctx.frequent_mistakes:
            mistakes_str = ", ".join(ctx.frequent_mistakes) if ctx.frequent_mistakes else "None recorded"
            sections.append(f"\n[STUDENT LEARNING PROFILE]:\nNotes: {ctx.user_memory_notes}\nKnown Weaknesses: {mistakes_str}")

        if ctx.document_memory_notes:
            sections.append(f"\n[ACTIVE DRAFT STATUS]:\n{ctx.document_memory_notes}")

        if rag_context:
            sections.append(f"\n[RETRIEVED REFERENCE EVIDENCE]:\n{rag_context}")

        return "\n".join(sections)