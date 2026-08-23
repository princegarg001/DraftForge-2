import json
import re
from typing import Any, Dict, List, Optional
from app.ai.llm.base import LLMMessage
from app.ai.llm.factory import get_llm
from app.core.logging import get_logger

logger = get_logger("roadmap_agent")


def extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    """Extracts and parses JSON object from text, handling reasoning tags and markdown blocks."""
    if not text:
        return None
    
    # 1. Strip reasoning / thinking tags
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    
    # 2. Try direct parse
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # 3. Extract within markdown ```json ... ``` blocks
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass

    # 4. Extract first outer curly brace pair
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(cleaned[start:end+1])
        except Exception:
            pass

    return None


class RoadmapAgent:
    """Synthesizes a 5-phase personalized learning roadmap grounded in student evaluation history."""

    def __init__(self):
        self.llm = get_llm()

    async def generate_roadmap(
        self,
        weak_skills: Optional[List[Dict[str, Any]]] = None,
        strong_skills: Optional[List[Dict[str, Any]]] = None,
        mastered_skills: Optional[List[Dict[str, Any]]] = None,
        avg_score: Optional[float] = 70.0,
        eval_count: Optional[int] = 1,
        target_doc_types: Optional[List[str]] = None,
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        weak = weak_skills or kwargs.get("weak", [])
        mastered = strong_skills or mastered_skills or kwargs.get("mastered", [])
        doc_types = target_doc_types or ["AFFIDAVIT_OF_CHARACTER", "EMPLOYMENT_AGREEMENT", "RENT_AGREEMENT"]

        system_prompt = (
            "You are an expert Indian Legal Education Consultant. "
            "Your output must be a valid JSON object containing exactly 5 phases. "
            "Do not include any conversational preamble or outro."
        )

        weak_str = "\n".join([f"- {s.get('name', 'Legal Skill')}" for s in weak]) or "- Foundation Legal Demarcation & Recitals"
        mastered_str = "\n".join([f"- {s.get('name', 'Legal Skill')}" for s in mastered]) or "- Basic Title Demarcation"
        docs_str = ", ".join(doc_types)

        user_prompt = f"""
Document Types: {docs_str}
Draft Score: {avg_score}/100

Weak Areas to Target:
{weak_str}

Mastered Areas:
{mastered_str}

Respond with only a valid JSON object matching this schema:
{{
  "phases": [
    {{"phase_number": 1, "title": "Phase 1 Title", "description": "Specific exercise targeting the weakest skill."}},
    {{"phase_number": 2, "title": "Phase 2 Title", "description": "Detailed practice task."}},
    {{"phase_number": 3, "title": "Phase 3 Title", "description": "Detailed practice task."}},
    {{"phase_number": 4, "title": "Phase 4 Title", "description": "Detailed practice task."}},
    {{"phase_number": 5, "title": "Phase 5 Title", "description": "Detailed practice task."}}
  ]
}}
"""

        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_prompt)
        ]

        try:
            # We omit response_format to avoid Groq validator conflicts with reasoning tokens
            response = await self.llm.generate(
                messages=messages,
                temperature=0.2,
                max_tokens=1500
            )
            data = extract_json_object(response.content)
            if data and "phases" in data and len(data["phases"]) == 5:
                return data["phases"]
        except Exception as exc:
            logger.warning(f"LLM roadmap generation parse fallback triggered: {exc}")

        # Standard 5-Phase Calibrated Fallback
        return [
            {"phase_number": 1, "title": "Parties & Jurisdiction Demarcation", "description": "Review Indian statutory title formats, jurats, and deponent details in standard affidavits."},
            {"phase_number": 2, "title": "Substantive Consideration & Remuneration", "description": "Practice drafting clear financial consideration, security deposits, and utility cost apportionment clauses."},
            {"phase_number": 3, "title": "Termination Notice & Cause Mechanics", "description": "Incorporate mutual notice periods and statutory standing orders into employment agreements."},
            {"phase_number": 4, "title": "Restrictive Covenants & Section 27 Restraints", "description": "Align post-termination non-solicitation and trade secret clauses with Section 27 Indian Contract Act."},
            {"phase_number": 5, "title": "Verification Jurats & Stamping Requirements", "description": "Master oath verification clauses, perjury declarations, and state stamp duty admissibility."}
        ]