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
        weak_skills: Optional[List[Any]] = None,
        strong_skills: Optional[List[Any]] = None,
        mastered_skills: Optional[List[Any]] = None,
        avg_score: Optional[float] = 70.0,
        eval_count: Optional[int] = 1,
        target_doc_types: Optional[List[str]] = None,
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        weak = weak_skills if weak_skills is not None else kwargs.get("weak", [])
        mastered = strong_skills if strong_skills is not None else (mastered_skills if mastered_skills is not None else kwargs.get("mastered", []))
        doc_types = target_doc_types or ["AFFIDAVIT_OF_CHARACTER", "EMPLOYMENT_AGREEMENT", "RENT_AGREEMENT"]

        weak_items = []
        for s in weak:
            if isinstance(s, str) and s.strip():
                weak_items.append(s.strip())
            elif isinstance(s, dict):
                val = s.get("name") or s.get("title") or s.get("criterion")
                if val:
                    weak_items.append(str(val).strip())
            elif hasattr(s, "name"):
                weak_items.append(str(s.name).strip())

        mastered_items = []
        for s in mastered:
            if isinstance(s, str) and s.strip():
                mastered_items.append(s.strip())
            elif isinstance(s, dict):
                val = s.get("name") or s.get("title") or s.get("criterion")
                if val:
                    mastered_items.append(str(val).strip())
            elif hasattr(s, "name"):
                mastered_items.append(str(s.name).strip())

        weak_str = "\n".join([f"- {item}" for item in weak_items]) or "- Statutory Jurat, Recitals & Deponent Verification"
        mastered_str = "\n".join([f"- {item}" for item in mastered_items]) or "- Document Title Demarcation"
        docs_str = ", ".join(doc_types)

        system_prompt = (
            "You are an expert Indian Legal Education Consultant and Curriculum Architect. "
            "Your task is to generate a comprehensive, pedagogical 5-phase personalized learning roadmap "
            "for a law student to master Indian legal drafting. "
            "Each phase MUST have a specific, professional title (e.g. 'Mastering Statutory Jurat & Verification Clauses', 'Structuring Commercial Restrictive Covenants', etc.) "
            "and an actionable, practical description outlining drafting exercises and statutory review tasks. "
            "Your output MUST be a valid JSON object containing exactly 5 phases with keys 'phase_number', 'title', and 'description'."
        )

        user_prompt = f"""
Target Legal Document Types: {docs_str}
Current Draft Average Score: {avg_score}/100

Weak Areas to Target and Remediate:
{weak_str}

Mastered Areas:
{mastered_str}

Generate a 5-phase customized learning trajectory with specific titles and comprehensive descriptions for each phase. Return only a valid JSON object:
{{
  "phases": [
    {{
      "phase_number": 1,
      "title": "<Specific Phase 1 Title>",
      "description": "<Detailed learning objective and practical drafting task>"
    }},
    {{
      "phase_number": 2,
      "title": "<Specific Phase 2 Title>",
      "description": "<Detailed learning objective and practical drafting task>"
    }},
    {{
      "phase_number": 3,
      "title": "<Specific Phase 3 Title>",
      "description": "<Detailed learning objective and practical drafting task>"
    }},
    {{
      "phase_number": 4,
      "title": "<Specific Phase 4 Title>",
      "description": "<Detailed learning objective and practical drafting task>"
    }},
    {{
      "phase_number": 5,
      "title": "<Specific Phase 5 Title>",
      "description": "<Detailed learning objective and practical drafting task>"
    }}
  ]
}}
"""

        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_prompt)
        ]

        try:
            response = await self.llm.generate(
                messages=messages,
                temperature=0.3,
                max_tokens=1500
            )
            data = extract_json_object(response.content)
            if data and "phases" in data and isinstance(data["phases"], list) and len(data["phases"]) == 5:
                # Sanitize and ensure valid titles
                sanitized_phases = []
                for i, p in enumerate(data["phases"], start=1):
                    p_title = p.get("title", "").strip()
                    p_desc = p.get("description", "").strip()
                    if not p_title or "phase" in p_title.lower() and "title" in p_title.lower():
                        p_title = f"Phase {i}: Advanced Legal Drafting Mastery"
                    sanitized_phases.append({
                        "phase_number": i,
                        "title": p_title,
                        "description": p_desc or "Practice drafting and statutory alignment exercises."
                    })
                return sanitized_phases
        except Exception as exc:
            logger.warning(f"LLM roadmap generation parse fallback triggered: {exc}")

        # Standard 5-Phase Calibrated Fallback with Professional Titles
        return [
            {"phase_number": 1, "title": "Parties & Statutory Jurisdiction Demarcation", "description": "Review Indian statutory title formats, jurats, and deponent details in standard affidavits."},
            {"phase_number": 2, "title": "Substantive Consideration & Remuneration Architecture", "description": "Practice drafting clear financial consideration, security deposits, and utility cost apportionment clauses."},
            {"phase_number": 3, "title": "Termination Notice & Cause Mechanics", "description": "Incorporate mutual notice periods and statutory standing orders into employment agreements."},
            {"phase_number": 4, "title": "Restrictive Covenants & Section 27 Alignment", "description": "Align post-termination non-solicitation and trade secret clauses with Section 27 of the Indian Contract Act."},
            {"phase_number": 5, "title": "Verification Jurats & Stamping Requirements", "description": "Master oath verification clauses, perjury declarations, and state stamp duty admissibility."}
        ]