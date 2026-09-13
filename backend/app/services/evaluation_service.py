from app.ai.evaluation.evaluator import EvaluationEngine
from app.ai.evaluation.models import EvaluationFinding
from app.core.authorization import assert_can_access_evaluation
from app.core.constants import DocumentType, FindingCategory, FindingStatus
from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.db.repositories.draft_repository import DraftRepository
from app.db.repositories.evaluation_repository import EvaluationRepository
from app.db.repositories.evidence_repository import EvidenceRepository
from app.models.database.models import UserProfileDB
from app.models.schemas.evaluation import EvaluationFindingResponse, EvaluationResponse
from app.pipelines.skill_pipeline import SkillPipeline


class EvaluationService:
    def __init__(self):
        self.draft_repo = DraftRepository()
        self.eval_repo = EvaluationRepository()
        self.evidence_repo = EvidenceRepository()
        self.engine = EvaluationEngine()
        self.skill_pipeline = SkillPipeline()

    def evaluate_draft(self, user_id: str, draft_id: str, version_number: int = None) -> EvaluationResponse:
        draft = self.draft_repo.get_by_id(draft_id)
        if not draft:
            raise NotFoundError("Draft", draft_id)
        if str(draft.get("user_id", "")).strip() != str(user_id).strip():
            raise PermissionDeniedError("Cannot evaluate another student's draft.")

        if version_number:
            version = self.draft_repo.get_version_by_number(draft_id, version_number)
        else:
            version = self.draft_repo.get_latest_version(draft_id)

        if not version:
            raise NotFoundError("DraftVersion", f"for draft {draft_id}")

        raw_doc_type = draft.get("document_type")
        if isinstance(raw_doc_type, DocumentType):
            doc_type = raw_doc_type
        else:
            try:
                doc_type = DocumentType(str(raw_doc_type).upper())
            except (ValueError, KeyError):
                doc_type = DocumentType.AFFIDAVIT_OF_CHARACTER

        eval_result = self.engine.evaluate_draft(version.get("raw_content", ""), doc_type)

        # 1. Persist evaluation record
        eval_record = self.eval_repo.create({
            "draft_version_id": version["id"],
            "overall_score": eval_result.overall_score,
            "max_score": eval_result.max_score,
            "structure_score": eval_result.structure_score,
            "clause_score": eval_result.clause_score,
            "formatting_score": eval_result.formatting_score,
            "gap_penalty": eval_result.gap_penalty,
            "rubric_version": eval_result.rubric_version,
            "llm_explanation": None,
        })

        # 2. Persist granular evidence findings
        findings_payload = [f.model_dump(mode="json") for f in eval_result.findings]
        saved_findings = self.evidence_repo.create_batch(eval_record["id"], findings_payload)

        # 3. Update student skill graph in PostgreSQL and Neo4j Aura
        try:
            self.skill_pipeline.process_evaluation_skills(
                user_id=user_id,
                evaluation_id=eval_record["id"],
                findings=eval_result.findings
            )
        except Exception:
            pass

        # 4. Update draft status
        try:
            self.draft_repo.update(draft_id, {"status": "EVALUATED"})
        except Exception:
            pass

        evidence_items = [EvaluationFindingResponse(**sf) for sf in saved_findings]
        return EvaluationResponse(
            id=eval_record["id"],
            draft_version_id=eval_record["draft_version_id"],
            overall_score=eval_record["overall_score"],
            max_score=eval_record["max_score"],
            structure_score=eval_record["structure_score"],
            clause_score=eval_record["clause_score"],
            formatting_score=eval_record["formatting_score"],
            gap_penalty=eval_record["gap_penalty"],
            rubric_version=eval_record["rubric_version"],
            created_at=eval_record.get("created_at"),
            evidence_items=evidence_items,
        )

    def get_evaluation(self, evaluation_id: str, requester: UserProfileDB) -> EvaluationResponse:
        # Authorize before reading: the record contains the student's scores and
        # verbatim draft evidence, so a bare id lookup leaks coursework across
        # the whole cohort.
        assert_can_access_evaluation(evaluation_id, requester)

        record = self.eval_repo.get_with_evidence(evaluation_id)
        if not record:
            raise NotFoundError("Evaluation", evaluation_id)

        raw_evidence = record.get("evaluation_evidence") or []
        evidence_items = [EvaluationFindingResponse(**item) for item in raw_evidence]

        return EvaluationResponse(
            id=record["id"],
            draft_version_id=record["draft_version_id"],
            overall_score=record["overall_score"],
            max_score=record["max_score"],
            structure_score=record["structure_score"],
            clause_score=record["clause_score"],
            formatting_score=record["formatting_score"],
            gap_penalty=record["gap_penalty"],
            rubric_version=record["rubric_version"],
            llm_explanation=record.get("llm_explanation"),
            is_overridden=record["is_overridden"],
            overridden_score=record.get("overridden_score"),
            created_at=record["created_at"],
            evidence_items=evidence_items,
        )