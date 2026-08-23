from typing import List
from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.db.repositories.assignment_repository import AssignmentRepository
from app.db.repositories.evaluation_repository import EvaluationRepository
from app.db.repositories.submission_repository import SubmissionRepository
from app.models.schemas.evaluation import EvaluationFindingResponse, EvaluationResponse
from app.models.schemas.submission import (
    CreateSubmissionRequest,
    ScoreOverrideRequest,
    SubmissionResponse,
)
from app.services.evaluation_service import EvaluationService


class SubmissionService:
    def __init__(self):
        self.sub_repo = SubmissionRepository()
        self.assign_repo = AssignmentRepository()
        self.eval_repo = EvaluationRepository()
        self.eval_service = EvaluationService()

    def submit_assignment(self, student_id: str, payload: CreateSubmissionRequest) -> SubmissionResponse:
        assignment = self.assign_repo.get_by_id(payload.assignment_id)
        if not assignment:
            raise NotFoundError("Assignment", payload.assignment_id)

        # 1. Trigger or link deterministic evaluation
        existing_eval = self.eval_repo.get_by_draft_version(payload.draft_version_id)
        if existing_eval:
            eval_id = existing_eval["id"]
            final_score = float(existing_eval["overall_score"])
        else:
            eval_res = self.eval_service.evaluate_draft(user_id=student_id, draft_id=payload.draft_id)
            eval_id = eval_res.id
            final_score = eval_res.overall_score

        # 2. Persist submission
        sub_record = self.sub_repo.create({
            "assignment_id": payload.assignment_id,
            "student_id": student_id,
            "draft_id": payload.draft_id,
            "draft_version_id": payload.draft_version_id,
            "evaluation_id": eval_id,
            "status": "EVALUATED",
            "final_score": final_score
        })

        return self._format_submission(sub_record)

    def list_assignment_submissions(self, assignment_id: str, teacher_id: str) -> List[SubmissionResponse]:
        assignment = self.assign_repo.get_by_id(assignment_id)
        if not assignment:
            raise NotFoundError("Assignment", assignment_id)
        if assignment["teacher_id"] != teacher_id:
            raise PermissionDeniedError("Unauthorized to view submissions for another instructor's assignment.")

        records = self.sub_repo.list_by_assignment(assignment_id)
        return [self._format_submission(r) for r in records]

    def override_submission_score(
        self,
        submission_id: str,
        teacher_id: str,
        payload: ScoreOverrideRequest
    ) -> SubmissionResponse:
        submission = self.sub_repo.get_by_id(submission_id)
        if not submission:
            raise NotFoundError("Submission", submission_id)

        eval_id = submission.get("evaluation_id")
        if eval_id:
            self.sub_repo.update_evaluation_override(
                evaluation_id=eval_id,
                overridden_score=payload.overridden_score,
                teacher_id=teacher_id,
                override_reason=payload.override_reason
            )

        updated_sub = self.sub_repo.update_submission_score(
            submission_id=submission_id,
            final_score=payload.overridden_score,
            teacher_notes=payload.teacher_notes
        )

        return self._format_submission(updated_sub)

    def _format_submission(self, record: dict) -> SubmissionResponse:
        eval_dto = None
        eval_data = record.get("evaluations")
        if eval_data:
            evidence_items = [
                EvaluationFindingResponse(**item)
                for item in eval_data.get("evaluation_evidence", [])
            ]
            eval_dto = EvaluationResponse(
                id=eval_data["id"],
                draft_version_id=eval_data["draft_version_id"],
                overall_score=eval_data["overall_score"],
                max_score=eval_data["max_score"],
                structure_score=eval_data["structure_score"],
                clause_score=eval_data["clause_score"],
                formatting_score=eval_data["formatting_score"],
                gap_penalty=eval_data["gap_penalty"],
                rubric_version=eval_data["rubric_version"],
                llm_explanation=eval_data.get("llm_explanation"),
                is_overridden=eval_data.get("is_overridden", False),
                overridden_score=eval_data.get("overridden_score"),
                created_at=eval_data["created_at"],
                evidence_items=evidence_items
            )

        profile = record.get("profiles") or {}
        return SubmissionResponse(
            id=record["id"],
            assignment_id=record["assignment_id"],
            student_id=record["student_id"],
            draft_id=record["draft_id"],
            draft_version_id=record["draft_version_id"],
            evaluation_id=record.get("evaluation_id"),
            status=record["status"],
            final_score=record.get("final_score"),
            teacher_notes=record.get("teacher_notes"),
            submitted_at=record["submitted_at"],
            student_name=profile.get("full_name"),
            student_email=profile.get("email"),
            evaluation=eval_dto
        )