from functools import lru_cache
from pathlib import Path
import yaml
from app.ai.evaluation.models import RubricConfig
from app.core.constants import DocumentType
from app.core.exceptions import BaseAppException

RUBRIC_DIR = Path(__file__).resolve().parent.parent / "knowledge" / "rubrics"


class RubricLoader:
    _RUBRIC_FILE_MAP = {
        DocumentType.AFFIDAVIT_OF_CHARACTER: "affidavit.yaml",
        DocumentType.EMPLOYMENT_AGREEMENT: "employment_agreement.yaml",
        DocumentType.RENT_AGREEMENT: "rent_agreement.yaml",
        DocumentType.LEGAL_NOTICE: "legal_notice.yaml",
    }

    @classmethod
    @lru_cache(maxsize=16)
    def load_rubric(cls, doc_type: DocumentType) -> RubricConfig:
        filename = cls._RUBRIC_FILE_MAP.get(doc_type)
        if not filename:
            raise BaseAppException(status_code=400, detail=f"No rubric defined for {doc_type}")

        file_path = RUBRIC_DIR / filename
        if not file_path.exists():
            raise BaseAppException(status_code=500, detail=f"Rubric config missing at {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            return RubricConfig(**data)
        except Exception as exc:
            raise BaseAppException(status_code=500, detail=f"Failed to parse rubric YAML: {exc}") from exc