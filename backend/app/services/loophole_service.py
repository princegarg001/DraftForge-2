from app.ai.evaluation.models import EvaluationFinding
from app.core.constants import DocumentType, FindingCategory, FindingStatus
from app.core.exceptions import NotFoundError
from app.db.repositories.draft_repository import DraftRepository
from app.db.repositories.evaluation_repository import EvaluationRepository
from app.models.schemas.loophole import LoopholeAnalysisResponse, LoopholeFindingResponse
from app.pipelines.loophole_pipeline import LoopholePipeline


class LoopholeService:
    def __init__(self):
        self.eval_repo = EvaluationRepository()
        self.draft_repo = DraftRepository()
        self.pipeline = LoopholePipeline()

    def analyze_evaluation_loopholes(self, evaluation_id: str) -> LoopholeAnalysisResponse:
        evaluation = self.eval_repo.get_with_evidence(evaluation_id)
        if not evaluation:
            raise NotFoundError("Evaluation", evaluation_id)

        # Retrieve parent draft to inspect document type
        version_id = evaluation["draft_version_id"]
        res = self.eval_repo.client.table("draft_versions").select("draft_id").eq("id", version_id).execute()
        if not res.data:
            raise NotFoundError("DraftVersion", version_id)

        draft = self.draft_repo.get_by_id(res.data[0]["draft_id"])
        doc_type = DocumentType(draft["document_type"])

        # Convert DB evidence records to EvaluationFinding objects
        raw_evidence = evaluation.get("evaluation_evidence") or []
        findings: list[EvaluationFinding] = []
        for e in raw_evidence:
            findings.append(
                EvaluationFinding(
                    category=FindingCategory(e["category"]),
                    criterion=e["criterion"],
                    status=FindingStatus(e["status"]),
                    score=float(e["score"]),
                    max_score=float(e["max_score"]),
                    student_evidence=e.get("student_evidence"),
                    reference_evidence=e.get("reference_evidence"),
                    source_document=e.get("source_document"),
                    source_page=e.get("source_page"),
                    source_section=e.get("source_section"),
                    explanation=e["explanation"],
                    metadata={"clause_id": e.get("criterion")}
                )
            )

        # Run GraphRAG loophole reasoner
        raw_loopholes = self.pipeline.run(doc_type=doc_type, findings=findings)
        loophole_dtos = [LoopholeFindingResponse(**lh.model_dump()) for lh in raw_loopholes]
        high_count = sum(1 for lh in loophole_dtos if lh.severity == "HIGH")

        return LoopholeAnalysisResponse(
            evaluation_id=evaluation_id,
            document_type=doc_type.value,
            total_loopholes=len(loophole_dtos),
            high_severity_count=high_count,
            loopholes=loophole_dtos
        )