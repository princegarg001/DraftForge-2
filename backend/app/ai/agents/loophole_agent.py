from typing import List
from app.ai.agents.base_agent import BaseAgent
from app.ai.graph.models import LoopholeFinding
from app.ai.llm.base import LLMMessage


class LoopholeAgent(BaseAgent):
    """Explains graph-detected loopholes, unmitigated risks, and provides practical mitigations."""

    async def explain_loopholes(self, document_type: str, loopholes: List[LoopholeFinding]) -> str:
        if not loopholes:
            return "No critical structural loopholes or unmitigated risks were detected in this submission."

        loopholes_text = []
        for idx, lh in enumerate(loopholes, start=1):
            lh_str = (
                f"Loophole {idx}: [{lh.severity}] {lh.title}\n"
                f"- Type: {lh.gap_type}\n"
                f"- Clause: {lh.related_clause_name or 'N/A'}\n"
                f"- Observation: {lh.educational_observation}\n"
                f"- Recommendation: {lh.reference_recommendation}"
            )
            loopholes_text.append(lh_str)

        system_prompt = (
            "You are an Indian contract and legal risk specialist. "
            "Synthesize the following graph-detected legal loopholes and explain their real-world consequences to a law student."
        )

        user_prompt = (
            f"DOCUMENT TYPE: {document_type}\n\n"
            f"DETECTED GRAPH LOOPHOLES:\n"
            f"{'\n\n'.join(loopholes_text)}\n\n"
            "Provide an educational risk briefing explaining why these omissions create liability and how to draft protective terms."
        )

        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_prompt),
        ]

        response = await self.llm.generate(messages=messages, temperature=0.2, max_tokens=2048)
        return response.content