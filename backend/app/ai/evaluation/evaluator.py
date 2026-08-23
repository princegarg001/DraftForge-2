from app.ai.evaluation.document_types.affidavit import AffidavitEvaluator
from app.ai.evaluation.document_types.employment_agreement import EmploymentAgreementEvaluator
from app.ai.evaluation.document_types.legal_notice import LegalNoticeEvaluator
from app.ai.evaluation.document_types.rent_agreement import RentAgreementEvaluator
from app.ai.evaluation.models import EvaluationResult
from app.ai.rag.pipeline import RAGPipeline
from app.core.constants import DocumentType
from app.core.exceptions import BaseAppException


class EvaluationEngine:
    def __init__(self):
        self.rag_pipeline = RAGPipeline()
        self.evaluators = {
            DocumentType.AFFIDAVIT_OF_CHARACTER: AffidavitEvaluator(self.rag_pipeline),
            DocumentType.EMPLOYMENT_AGREEMENT: EmploymentAgreementEvaluator(self.rag_pipeline),
            DocumentType.RENT_AGREEMENT: RentAgreementEvaluator(self.rag_pipeline),
            DocumentType.LEGAL_NOTICE: LegalNoticeEvaluator(self.rag_pipeline),
        }

    def evaluate_draft(self, raw_content: str, doc_type: DocumentType) -> EvaluationResult:
        evaluator = self.evaluators.get(doc_type)
        if not evaluator:
            raise BaseAppException(
                status_code=400,
                detail=f"No evaluator registered for document type: {doc_type}"
            )
        return evaluator.evaluate(raw_content)