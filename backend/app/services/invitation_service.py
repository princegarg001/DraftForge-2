"""Teacher-driven roster invitations.

Replaces open self-registration. A student account now comes into existence
only because an instructor put that address on a class roster, which makes the
invitation itself the proof of email ownership - so the created account is
email-confirmed on arrival rather than requiring a second verification round
trip.
"""

from __future__ import annotations

from typing import Any

from fastapi import BackgroundTasks

from app.config import get_settings
from app.core import audit
from app.core.authorization import assert_owns_assignment  # noqa: F401 - re-exported for callers
from app.core.constants import UserRole
from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    ValidationFailedError,
)
from app.core.logging import get_logger
from app.core.tokens import expiry_from_now, hash_token, is_expired, generate_token
from app.db.repositories.class_repository import ClassRepository, EnrollmentRepository
from app.db.repositories.invitation_repository import InvitationRepository
from app.db.repositories.user_repository import UserRepository
from app.db.supabase import get_supabase_admin_client
from app.models.database.models import UserProfileDB
from app.models.schemas.classroom import (
    AcceptInvitationRequest,
    BulkInviteResponse,
    InvitationPreviewResponse,
    InviteOutcome,
    StudentInvite,
)
from app.services.email import EmailMessage, dispatch, render_student_invitation

logger = get_logger("invitation_service")
settings = get_settings()

# Returned for every unusable token - unknown, expired, revoked or already
# accepted. Distinguishing them would let a caller probe which tokens exist.
_GENERIC_TOKEN_ERROR = "This invitation link is no longer valid. Ask your instructor to resend it."


class InvitationService:
    def __init__(self) -> None:
        self.class_repo = ClassRepository()
        self.enrollment_repo = EnrollmentRepository()
        self.invite_repo = InvitationRepository()
        self.user_repo = UserRepository()

    # ------------------------------------------------------------------
    # Issuing
    # ------------------------------------------------------------------
    def _load_owned_class(self, class_id: str, teacher: UserProfileDB) -> dict[str, Any]:
        classroom = self.class_repo.get_by_id(class_id)
        if not classroom:
            raise NotFoundError("class", class_id)
        if classroom["teacher_id"] != teacher.id and teacher.role is not UserRole.ADMIN:
            # 404 rather than 403: a 403 confirms the class exists.
            raise NotFoundError("class", class_id)
        if classroom.get("is_archived"):
            raise ConflictError("This class is archived. Restore it before inviting students.")
        return classroom

    def invite_students(
        self,
        class_id: str,
        teacher: UserProfileDB,
        students: list[StudentInvite],
        background_tasks: BackgroundTasks,
    ) -> BulkInviteResponse:
        classroom = self._load_owned_class(class_id, teacher)
        results: list[InviteOutcome] = []

        for student in students:
            try:
                results.append(self._invite_one(classroom, teacher, student, background_tasks))
            except Exception as exc:  # noqa: BLE001 - one bad row must not abort the batch
                logger.error(
                    f"Invite failed for {student.email} in class {class_id}: "
                    f"{exc.__class__.__name__}: {exc}"
                )
                results.append(
                    InviteOutcome(email=student.email, status="failed", detail="Could not be invited.")
                )

        invited = sum(1 for r in results if r.status in ("invited", "resent"))
        skipped = sum(1 for r in results if r.status == "already_enrolled")
        failed = sum(1 for r in results if r.status == "failed")

        audit.record(
            action=audit.AuditAction.INVITE_ISSUED,
            resource="class",
            actor_id=teacher.id,
            actor_role=teacher.role.value,
            resource_id=class_id,
            details={"submitted": len(students), "invited": invited, "skipped": skipped, "failed": failed},
        )

        return BulkInviteResponse(
            class_id=class_id,
            total_submitted=len(students),
            invited=invited,
            skipped=skipped,
            failed=failed,
            results=results,
        )

    def _invite_one(
        self,
        classroom: dict[str, Any],
        teacher: UserProfileDB,
        student: StudentInvite,
        background_tasks: BackgroundTasks,
    ) -> InviteOutcome:
        class_id = classroom["id"]

        enrollment = self.enrollment_repo.upsert_invited(
            class_id=class_id,
            email=student.email,
            full_name=student.full_name,
            invited_by=teacher.id,
        )

        if enrollment["status"] == "ACTIVE":
            return InviteOutcome(
                email=student.email, status="already_enrolled", detail="Already in this class."
            )

        # Any previous live token for this address is invalidated first, so a
        # resend replaces rather than accumulates valid credentials.
        self.invite_repo.revoke_pending_for(class_id, student.email)

        raw_token, token_hash = generate_token()
        expires_at = expiry_from_now(settings.INVITE_TOKEN_TTL_HOURS)

        invitation = self.invite_repo.create_invitation(
            class_id=class_id,
            enrollment_id=enrollment["id"],
            email=student.email,
            token_hash=token_hash,
            expires_at=expires_at.isoformat(),
            issued_by=teacher.id,
        )

        self._queue_invitation_email(
            raw_token=raw_token,
            invitation_id=invitation["id"],
            classroom=classroom,
            teacher=teacher,
            student=student,
            background_tasks=background_tasks,
        )

        return InviteOutcome(email=student.email, status="invited")

    def _queue_invitation_email(
        self,
        *,
        raw_token: str,
        invitation_id: str,
        classroom: dict[str, Any],
        teacher: UserProfileDB,
        student: StudentInvite,
        background_tasks: BackgroundTasks,
    ) -> None:
        invite_url = f"{settings.APP_PUBLIC_URL.rstrip('/')}/invite/accept?token={raw_token}"

        rendered = render_student_invitation(
            email=student.email,
            full_name=student.full_name,
            teacher_name=teacher.full_name or "Your instructor",
            class_name=classroom["name"],
            institution=classroom.get("institution"),
            invite_url=invite_url,
            expires_in_days=max(1, settings.INVITE_TOKEN_TTL_HOURS // 24),
        )

        # Sent out of band: a slow provider must not hold the teacher's request
        # open, and a 200-student batch would otherwise time out.
        background_tasks.add_task(
            dispatch,
            EmailMessage(
                to=student.email,
                subject=rendered.subject,
                html=rendered.html,
                text=rendered.text,
            ),
            "student_invitation",
            "invitation",
            invitation_id,
        )

    def resend_invitation(
        self,
        class_id: str,
        email: str,
        teacher: UserProfileDB,
        background_tasks: BackgroundTasks,
    ) -> InviteOutcome:
        classroom = self._load_owned_class(class_id, teacher)
        normalized = email.strip().lower()

        enrollment = self.enrollment_repo.get_by_class_and_email(class_id, normalized)
        if not enrollment:
            raise NotFoundError("roster entry", normalized)
        if enrollment["status"] == "ACTIVE":
            raise ConflictError("This student has already joined the class.")

        outcome = self._invite_one(
            classroom,
            teacher,
            StudentInvite(email=normalized, full_name=enrollment.get("full_name")),
            background_tasks,
        )
        return InviteOutcome(email=normalized, status="resent", detail=outcome.detail)

    def revoke_invitation(self, invitation_id: str, teacher: UserProfileDB) -> None:
        invitation = self.invite_repo.get_by_id(invitation_id)
        if not invitation:
            raise NotFoundError("invitation", invitation_id)

        classroom = self.class_repo.get_by_id(invitation["class_id"])
        if not classroom or (
            classroom["teacher_id"] != teacher.id and teacher.role is not UserRole.ADMIN
        ):
            raise NotFoundError("invitation", invitation_id)

        self.invite_repo.revoke(invitation_id)
        audit.record(
            action=audit.AuditAction.INVITE_REVOKED,
            resource="invitation",
            actor_id=teacher.id,
            actor_role=teacher.role.value,
            resource_id=invitation_id,
            details={"email": invitation["email"], "class_id": invitation["class_id"]},
        )

    # ------------------------------------------------------------------
    # Acceptance (unauthenticated)
    # ------------------------------------------------------------------
    def _resolve_valid_invitation(self, raw_token: str) -> dict[str, Any]:
        invitation = self.invite_repo.find_by_token_hash(hash_token(raw_token))

        if not invitation:
            raise ValidationFailedError(_GENERIC_TOKEN_ERROR)
        if invitation["status"] != "PENDING":
            raise ValidationFailedError(_GENERIC_TOKEN_ERROR)
        if is_expired(invitation["expires_at"]):
            self.invite_repo.mark_expired(invitation["id"])
            raise ValidationFailedError(_GENERIC_TOKEN_ERROR)

        return invitation

    def preview_invitation(self, raw_token: str) -> InvitationPreviewResponse:
        invitation = self._resolve_valid_invitation(raw_token)
        classroom = invitation.get("classes") or {}

        teacher_name = None
        if classroom.get("teacher_id"):
            teacher = self.user_repo.get_by_id(classroom["teacher_id"])
            teacher_name = (teacher or {}).get("full_name")

        enrollment = self.enrollment_repo.get_by_id(invitation["enrollment_id"]) or {}

        return InvitationPreviewResponse(
            email=invitation["email"],
            class_name=classroom.get("name", "your class"),
            institution=classroom.get("institution"),
            teacher_name=teacher_name,
            full_name=enrollment.get("full_name"),
            expires_at=invitation["expires_at"],
        )

    def accept_invitation(
        self, payload: AcceptInvitationRequest, background_tasks: BackgroundTasks
    ) -> dict[str, Any]:
        """Create the student's account and activate their enrollment.

        The email address comes from the invitation record, never from the
        request - otherwise a valid token could be redeemed against an arbitrary
        address, which would turn one leaked invitation into account creation
        for any email the attacker chose.
        """
        invitation = self._resolve_valid_invitation(payload.token)
        email = invitation["email"]
        admin = get_supabase_admin_client()

        existing_profile = self.user_repo.get_by_email(email)
        if existing_profile:
            # The account already exists; attach it to the class rather than
            # attempting to reset its password from an invitation token.
            self.enrollment_repo.mark_active(invitation["enrollment_id"], existing_profile["id"])
            self.invite_repo.mark_accepted(invitation["id"], existing_profile["id"])
            return {"user_id": existing_profile["id"], "email": email, "account_created": False}

        try:
            created = admin.auth.admin.create_user(
                {
                    "email": email,
                    "password": payload.password,
                    # The invitation was delivered to this address, which is
                    # itself proof of control; a second confirmation round trip
                    # would add friction without adding assurance.
                    "email_confirm": True,
                    "user_metadata": {"full_name": payload.full_name or ""},
                }
            )
        except Exception as exc:
            logger.error(f"Account creation failed for invited user: {exc.__class__.__name__}: {exc}")
            raise ConflictError("Could not complete sign-up. Ask your instructor to resend the invitation.") from exc

        if not created or not created.user:
            raise ConflictError("Could not complete sign-up. Ask your instructor to resend the invitation.")

        user_id = str(created.user.id)

        # STUDENT is hardcoded. The invitation's intended_role is constrained to
        # exclude ADMIN at the database level, and elevation never happens here.
        self.user_repo.ensure_profile(
            user_id=user_id,
            email=email,
            role=UserRole.STUDENT.value,
            full_name=payload.full_name,
        )

        self.enrollment_repo.mark_active(invitation["enrollment_id"], user_id)
        self.invite_repo.mark_accepted(invitation["id"], user_id)

        audit.record(
            action=audit.AuditAction.INVITE_ACCEPTED,
            resource="invitation",
            actor_id=user_id,
            actor_role=UserRole.STUDENT.value,
            resource_id=invitation["id"],
            subject_id=user_id,
            details={"class_id": invitation["class_id"]},
        )

        logger.info(f"Invited student {user_id} joined class {invitation['class_id']}")
        return {"user_id": user_id, "email": email, "account_created": True}
