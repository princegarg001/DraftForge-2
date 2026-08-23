from app.ai.evaluation.document_types.base_evaluator import BaseDocumentEvaluator
from app.ai.rag.pipeline import RAGPipeline
from app.core.constants import DocumentType


class AffidavitEvaluator(BaseDocumentEvaluator):
    def __init__(self, rag_pipeline: RAGPipeline):
        super().__init__(DocumentType.AFFIDAVIT_OF_CHARACTER, rag_pipeline)