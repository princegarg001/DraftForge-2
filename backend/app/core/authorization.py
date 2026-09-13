"""Resource-level authorization checks.

Role gates (``require_student``, ``require_teacher``) answer "may this kind of
user call this endpoint". They do not answer "may *this* user touch *this*
row" - and several endpoints were relying on the role gate alone, matching
records on a bare id supplied by the caller.

The checks here close that gap. They are the application-layer half of the
defence; the row-level security policies added in migration 005 are the
database-layer backstop for the same rules.
"""

from __future__ import annotations

from functools import lru_cache

from app.core.constants import UserRole
from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.core.logging import get_logger
from app.db.repositories.evaluation_repository import EvaluationRepository
from app.models.database.models import UserProfileDB

logger = get_logger("authorization")


@lru_cache
def _eval_repo() -> EvaluationRepository:
    # Built on first use: constructing it at import time would open a Supabase
    # client before settings validation has run.
    return EvaluationRepository()


def assert_can_access_evaluation(evaluation_id: str, user: UserProfileDB) -> str:
    """Authorize reading an evaluation. Returns the owning student's id.

    Permitted for the student who produced it, an admin, or a teacher on whose
    assignment it was submitted. A teacher has no standing claim on evaluations
    outside their own coursework.
    """
    repo = _eval_repo()
    owner_id = repo.get_owner_id(evaluation_id)
    if owner_id is None:
        raise NotFoundError("evaluation", evaluation_id)

    if user.role is UserRole.ADMIN or owner_id == user.id:
        return owner_id

    if user.role is UserRole.TEACHER and repo.is_visible_to_teacher(evaluation_id, user.id):
        return owner_id

    logger.warning(
        f"Blocked cross-tenant evaluation access: user={user.id} role={user.role.value} "
        f"evaluation={evaluation_id}"
    )
    # Reported as 404, not 403: confirming the row exists would let a caller
    # enumerate valid evaluation ids.
    raise NotFoundError("evaluation", evaluation_id)


def assert_owns_draft(draft: dict | None, user: UserProfileDB, draft_id: str) -> None:
    """Authorize acting on a draft the caller claims to own."""
    if not draft:
        raise NotFoundError("draft", draft_id)
    if draft.get("user_id") != user.id and user.role is not UserRole.ADMIN:
        logger.warning(f"Blocked cross-tenant draft access: user={user.id} draft={draft_id}")
        raise NotFoundError("draft", draft_id)


def assert_owns_assignment(assignment: dict | None, teacher_id: str, assignment_id: str) -> None:
    if not assignment:
        raise NotFoundError("assignment", assignment_id)
    if assignment.get("teacher_id") != teacher_id:
        logger.warning(
            f"Blocked cross-instructor assignment access: teacher={teacher_id} assignment={assignment_id}"
        )
        raise PermissionDeniedError("You do not have permission to manage this assignment.")
