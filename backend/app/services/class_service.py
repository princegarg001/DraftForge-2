"""Class and roster management."""

from __future__ import annotations

from typing import Any

from app.core import audit
from app.core.constants import UserRole
from app.core.exceptions import ConflictError, NotFoundError
from app.core.logging import get_logger
from app.core.tokens import generate_join_code
from app.db.repositories.class_repository import ClassRepository, EnrollmentRepository
from app.db.repositories.invitation_repository import InvitationRepository
from app.models.database.models import UserProfileDB
from app.models.schemas.classroom import (
    ClassCreateRequest,
    ClassResponse,
    ClassUpdateRequest,
    EnrollmentResponse,
    PendingInvitationResponse,
)

logger = get_logger("class_service")


class ClassService:
    def __init__(self) -> None:
        self.repo = ClassRepository()
        self.enrollment_repo = EnrollmentRepository()
        self.invite_repo = InvitationRepository()

    # ------------------------------------------------------------------
    def _owned(self, class_id: str, user: UserProfileDB) -> dict[str, Any]:
        classroom = self.repo.get_by_id(class_id)
        if not classroom:
            raise NotFoundError("class", class_id)
        if classroom["teacher_id"] != user.id and user.role is not UserRole.ADMIN:
            # 404 rather than 403 so class ids cannot be probed.
            raise NotFoundError("class", class_id)
        return classroom

    @staticmethod
    def _to_response(record: dict[str, Any]) -> ClassResponse:
        # PostgREST returns an aggregate as [{"count": n}].
        raw_count = record.get("class_enrollments") or []
        student_count = raw_count[0].get("count", 0) if isinstance(raw_count, list) and raw_count else 0
        return ClassResponse(**record, student_count=student_count)

    # ------------------------------------------------------------------
    def create_class(self, teacher: UserProfileDB, payload: ClassCreateRequest) -> ClassResponse:
        # Retry on the small chance of a join-code collision before surfacing
        # an error; the codes are short by design so they can be read aloud.
        for _ in range(5):
            try:
                record = self.repo.create(
                    {
                        "teacher_id": teacher.id,
                        "name": payload.name,
                        "description": payload.description,
                        "institution": payload.institution,
                        "academic_term": payload.academic_term,
                        "join_code": generate_join_code(),
                    }
                )
                logger.info(f"Teacher {teacher.id} created class {record['id']}")
                return self._to_response(record)
            except Exception as exc:  # noqa: BLE001
                if "join_code" not in str(exc).lower():
                    raise
        raise ConflictError("Could not allocate a unique join code. Please try again.")

    def list_teacher_classes(self, teacher: UserProfileDB, include_archived: bool = False) -> list[ClassResponse]:
        return [
            self._to_response(record)
            for record in self.repo.list_for_teacher(teacher.id, include_archived)
        ]

    def list_student_classes(self, student: UserProfileDB) -> list[ClassResponse]:
        return [self._to_response(record) for record in self.repo.list_for_student(student.id)]

    def get_class(self, class_id: str, user: UserProfileDB) -> ClassResponse:
        return self._to_response(self._owned(class_id, user))

    def update_class(
        self, class_id: str, user: UserProfileDB, payload: ClassUpdateRequest
    ) -> ClassResponse:
        self._owned(class_id, user)
        patch = payload.model_dump(exclude_none=True)
        if not patch:
            return self.get_class(class_id, user)
        updated = self.repo.update(class_id, patch)
        if not updated:
            raise NotFoundError("class", class_id)
        return self._to_response(updated)

    def rotate_join_code(self, class_id: str, user: UserProfileDB) -> ClassResponse:
        """Issue a fresh join code, invalidating the previous one.

        The remedy when a code has been shared beyond the intended cohort.
        """
        self._owned(class_id, user)
        updated = self.repo.update(class_id, {"join_code": generate_join_code()})
        if not updated:
            raise NotFoundError("class", class_id)
        return self._to_response(updated)

    # ------------------------------------------------------------------
    def get_roster(self, class_id: str, user: UserProfileDB) -> list[EnrollmentResponse]:
        self._owned(class_id, user)
        roster = []
        for row in self.enrollment_repo.list_roster(class_id):
            profile = row.get("profiles") or {}
            roster.append(
                EnrollmentResponse(
                    **{k: v for k, v in row.items() if k != "profiles"},
                    # Prefer the registered name once the student has joined.
                    full_name=profile.get("full_name") or row.get("full_name"),
                )
            )
        return roster

    def list_pending_invitations(
        self, class_id: str, user: UserProfileDB
    ) -> list[PendingInvitationResponse]:
        self._owned(class_id, user)
        return [
            PendingInvitationResponse(**row)
            for row in self.invite_repo.list_pending_for_class(class_id)
        ]

    def remove_student(self, class_id: str, enrollment_id: str, user: UserProfileDB) -> None:
        """Remove a student from the roster.

        A soft removal: their drafts, evaluations and submissions are course
        records and are not deleted along with the roster entry.
        """
        self._owned(class_id, user)
        enrollment = self.enrollment_repo.get_by_id(enrollment_id)
        if not enrollment or enrollment["class_id"] != class_id:
            raise NotFoundError("roster entry", enrollment_id)

        self.enrollment_repo.update(enrollment_id, {"status": "REMOVED"})
        self.invite_repo.revoke_pending_for(class_id, enrollment["email"])

        audit.record(
            action=audit.AuditAction.INVITE_REVOKED,
            resource="class_enrollment",
            actor_id=user.id,
            actor_role=user.role.value,
            resource_id=enrollment_id,
            subject_id=enrollment.get("student_id"),
            details={"class_id": class_id, "email": enrollment["email"]},
        )
