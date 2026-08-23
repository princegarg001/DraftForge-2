import json
from typing import Any, Dict, List
from app.ai.agents.base_agent import BaseAgent
from app.ai.llm.base import LLMMessage


class QuizAgent(BaseAgent):
    """Generates rigorous legal multiple-choice questions grounded in reference principles."""

    async def generate_quiz_questions(
        self,
        skill_name: str,
        document_type: str,
        count: int = 3,
        difficulty: str = "INTERMEDIATE"
    ) -> List[Dict[str, Any]]:
        system_prompt = (
            "You are an Indian Bar Exam & Legal Drafting Examiner.\n"
            "Generate multiple choice questions testing critical legal drafting errors, clause dependencies, and risks.\n"
            "Return STRICTLY as a JSON array of question objects."
        )

        user_prompt = (
            f"TARGET SKILL: {skill_name}\n"
            f"DOCUMENT TYPE: {document_type}\n"
            f"DIFFICULTY: {difficulty}\n"
            f"QUESTION COUNT: {count}\n\n"
            "JSON SCHEMA:\n"
            "[\n"
            "  {\n"
            "    \"question_text\": \"Scenario or drafting question...\",\n"
            "    \"options\": [\n"
            "      {\"key\": \"A\", \"text\": \"Option A text\"},\n"
            "      {\"key\": \"B\", \"text\": \"Option B text\"},\n"
            "      {\"key\": \"C\", \"text\": \"Option C text\"},\n"
            "      {\"key\": \"D\", \"text\": \"Option D text\"}\n"
            "    ],\n"
            "    \"correct_option\": \"A\",\n"
            "    \"explanation\": \"Detailed legal reasoning citing why A is legally sound and B/C/D create flaws.\"\n"
            "  }\n"
            "]"
        )

        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_prompt)
        ]

        response = await self.llm.generate(
            messages=messages,
            temperature=0.3,
            max_tokens=2500,
            response_format={"type": "json_object"}
        )

        try:
            parsed = json.loads(response.content)
            if isinstance(parsed, list):
                return parsed
            if isinstance(parsed, dict) and "questions" in parsed:
                return parsed["questions"]
            return list(parsed.values())[0] if parsed else []
        except Exception:
            cleaned = response.content.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)