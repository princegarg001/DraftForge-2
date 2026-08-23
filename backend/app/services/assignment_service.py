from typing import List, Optional
from app.core.constants import DocumentType
from app.core.exceptions import NotFoundError
from app.db.repositories.assignment_repository import AssignmentRepository
from app.models.schemas.assignment import AssignmentCreateRequest, AssignmentResponse


class AssignmentService:
    def __init__(self):
        self.repo = AssignmentRepository()

    def create_assignment(self, teacher_id: str, payload: AssignmentCreateRequest) -> AssignmentResponse:
        record = self.repo.create({
            "teacher_id": teacher_id,
            "title": payload.title,
            "description": payload.description,
            "document_type": payload.document_type.value,
            "instructions": payload.instructions,
            "deadline": payload.deadline.isoformat() if payload.deadline else None,
            "rubric_override": payload.rubric_override,
            "status": "PUBLISHED"
        })
        return AssignmentResponse(**record, submissions_count=0)

    def list_teacher_assignments(self, teacher_id: str) -> List[AssignmentResponse]:
        records = self.repo.list_teacher_assignments(teacher_id)
        results = []
        for r in records:
            sub_count = 0
            if r.get("submissions") and len(r["submissions"]) > 0:
                sub_count = r["submissions"][0].get("count", 0)
            results.append(AssignmentResponse(**r, submissions_count=sub_count))
        return results

    def list_student_assignments(self, doc_type: Optional[DocumentType] = None) -> List[AssignmentResponse]:
        records = self.repo.list_active_assignments(doc_type)
        return [AssignmentResponse(**r, submissions_count=0) for r in records]

    def get_assignment(self, assignment_id: str) -> AssignmentResponse:
        record = self.repo.get_by_id(assignment_id)
        if not record:
            raise NotFoundError("Assignment", assignment_id)
        return AssignmentResponse(**record)