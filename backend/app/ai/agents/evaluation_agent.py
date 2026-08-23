import json
from app.ai.agents.base_agent import BaseAgent
from app.ai.llm.base import LLMMessage
from app.ai.llm.prompts.explanation_prompts import (
    EXPLANATION_SYSTEM_PROMPT,
    EXPLANATION_USER_PROMPT,
)


class EvaluationAgent(BaseAgent):
    """Generates comprehensive, evidence-grounded score explanations."""

    async def explain_evaluation(self, evaluation_data: dict, doc_type_str: str) -> str:
        findings_formatted = []
        for f in evaluation_data.get("evidence_items", []):
            item_str = (
                f"- [{f['category']}] {f['criterion']}: Status={f['status']} (Score {f['score']}/{f['max_score']})\n"
                f"  Explanation: {f['explanation']}\n"
                f"  Source: {f.get('source_document') or 'N/A'} (Page {f.get('source_page') or 'N/A'})\n"
                f"  Student Text: \"{f.get('student_evidence') or 'None'}\""
            )
            findings_formatted.append(item_str)

        user_content = EXPLANATION_USER_PROMPT.format(
            document_type=doc_type_str,
            overall_score=evaluation_data["overall_score"],
            max_score=evaluation_data["max_score"],
            structure_score=evaluation_data["structure_score"],
            clause_score=evaluation_data["clause_score"],
            formatting_score=evaluation_data["formatting_score"],
            gap_penalty=evaluation_data["gap_penalty"],
            evidence_findings="\n\n".join(findings_formatted)
        )

        messages = [
            LLMMessage(role="system", content=EXPLANATION_SYSTEM_PROMPT),
            LLMMessage(role="user", content=user_content),
        ]

        response = await self.llm.generate(messages=messages, temperature=0.2, max_tokens=2500)
        return response.content