import json
from typing import Any, Dict
from app.ai.agents.base_agent import BaseAgent
from app.ai.llm.base import LLMMessage
from app.ai.llm.prompts.exercise_prompts import (
    EXERCISE_GENERATOR_SYSTEM_PROMPT,
    EXERCISE_GENERATOR_USER_PROMPT,
)


class ExerciseAgent(BaseAgent):
    """Generates personalized practice exercises tailored to student skill gaps."""

    async def generate_exercise(
        self,
        skill_name: str,
        skill_category: str,
        document_type: str,
        weakness_description: str,
        difficulty: str = "INTERMEDIATE"
    ) -> Dict[str, Any]:
        user_content = EXERCISE_GENERATOR_USER_PROMPT.format(
            skill_name=skill_name,
            skill_category=skill_category,
            document_type=document_type,
            weakness_description=weakness_description,
            difficulty=difficulty
        )

        messages = [
            LLMMessage(role="system", content=EXERCISE_GENERATOR_SYSTEM_PROMPT),
            LLMMessage(role="user", content=user_content),
        ]

        response = await self.llm.generate(
            messages=messages,
            temperature=0.4,
            max_tokens=2048,
            response_format={"type": "json_object"}
        )

        try:
            return json.loads(response.content)
        except Exception:
            # Fallback if raw markdown wrapped
            cleaned = response.content.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)