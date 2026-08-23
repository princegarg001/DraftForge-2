import re
from typing import Dict, List, Tuple
from app.core.constants import DocumentType


class DocumentClassifier:
    """
    Deterministic rule-based legal document classifier for Indian jurisdiction corpus:
    1. Affidavit of Character
    2. Employment Agreement
    3. Rent Agreement
    4. Legal Notice
    """
    
    # Signature patterns and weighted legal signals
    PATTERNS: Dict[DocumentType, List[Tuple[str, int]]] = {
        DocumentType.AFFIDAVIT_OF_CHARACTER: [
            (r"\baffidavit\b", 4),
            (r"\bdeponent\b", 5),
            (r"\bsolemnly\s+(affirm|declare|state)\b", 5),
            (r"\bverification\b", 3),
            (r"\bcharacter\b", 4),
            (r"\bbear\s+good\s+moral\s+character\b", 6),
            (r"\bno\s+criminal\s+case\b", 4),
            (r"\boath\s+commissioner\b", 4),
        ],
        DocumentType.EMPLOYMENT_AGREEMENT: [
            (r"\bemployment\s+agreement\b", 6),
            (r"\bappointment\s+letter\b", 5),
            (r"\bemployer\b", 4),
            (r"\bemployee\b", 4),
            (r"\bprobation\s+period\b", 4),
            (r"\bcompensation\s+and\s+benefits\b", 4),
            (r"\bnon-compete\b", 4),
            (r"\bcode\s+of\s+conduct\b", 3),
            (r"\btermination\s+of\s+employment\b", 4),
        ],
        DocumentType.RENT_AGREEMENT: [
            (r"\brent\s+agreement\b", 6),
            (r"\blease\s+agreement\b", 6),
            (r"\bleave\s+and\s+license\b", 6),
            (r"\blandlord\b|\blessor\b", 4),
            (r"\btenant\b|\blessee\b|\blicensee\b", 4),
            (r"\bmonthly\s+rent\b", 5),
            (r"\bsecurity\s+deposit\b", 4),
            (r"\bdemised\s+premises\b", 5),
            (r"\bmaintenance\s+charges\b", 3),
        ],
        DocumentType.LEGAL_NOTICE: [
            (r"\blegal\s+notice\b", 6),
            (r"\badvocate\b", 4),
            (r"\bunder\s+instructions\s+from\s+my\s+client\b", 6),
            (r"\bhereby\s+call\s+upon\s+you\b", 5),
            (r"\bwithin\s+\d+\s+days\b", 4),
            (r"\bfailing\s+which\b", 4),
            (r"\blegal\s+proceedings\b", 4),
            (r"\bcivil\s+and\s+criminal\b", 4),
        ],
    }

    @classmethod
    def classify(cls, text: str) -> Tuple[DocumentType, float]:
        """
        Classifies document text based on matching score density.
        Returns the top DocumentType and confidence score (0.0 to 1.0).
        """
        if not text.strip():
            return DocumentType.AFFIDAVIT_OF_CHARACTER, 0.0

        scores: Dict[DocumentType, int] = {doc_type: 0 for doc_type in DocumentType}
        lower_text = text.lower()

        for doc_type, regex_rules in cls.PATTERNS.items():
            for pattern, weight in regex_rules:
                matches = len(re.findall(pattern, lower_text))
                if matches > 0:
                    scores[doc_type] += min(matches, 3) * weight

        best_doc_type = max(scores, key=scores.get)
        top_score = scores[best_doc_type]
        total_score = sum(scores.values())

        if total_score == 0:
            return DocumentType.AFFIDAVIT_OF_CHARACTER, 0.0

        confidence = round(min(top_score / max(total_score, 15), 1.0), 2)
        return best_doc_type, confidence