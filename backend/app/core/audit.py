"""Audit trail for privileged actions.

Grade overrides, role changes, reference-corpus uploads and account
deactivations previously left no durable record, so there was no way to answer
"who changed this mark, and when". Entries are append-only at the database
layer (migration 005 grants no UPDATE or DELETE), so a compromised session
cannot rewrite its own history.

Writes are best-effort: a failure to record an audit entry is logged loudly but
never fails the operation it describes. Blocking a teacher's grade override on
an audit-table hiccup trades a real feature for a bookkeeping one.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from fastapi import Request

from app.core.logging import get_logger
from app.db.supabase import get_supabase_admin_client

logger = get_logger("audit")


class AuditAction(str, Enum):
    ROLE_CHANGED = "role.changed"
    ACCOUNT_DEACTIVATED = "account.deactivated"
    ACCOUNT_REACTIVATED = "account.reactivated"
    GRADE_OVERRIDDEN = "grade.overridden"
    REFERENCE_UPLOADED = "reference.uploaded"
    REFERENCE_DELETED = "reference.deleted"
    ASSIGNMENT_CREATED = "assignment.created"
    INVITE_ISSUED = "invite.issued"
    INVITE_REVOKED = "invite.revoked"
    INVITE_ACCEPTED = "invite.accepted"
    AUTHZ_DENIED = "authz.denied"


def record(
    action: AuditAction,
    resource: str,
    actor_id: str | None = None,
    actor_role: str | None = None,
    resource_id: str | None = None,
    subject_id: str | None = None,
    details: dict[str, Any] | None = None,
    request: Request | None = None,
) -> None:
    """Append an audit entry. Never raises."""
    entry: dict[str, Any] = {
        "action": action.value,
        "resource": resource,
        "actor_id": actor_id,
        "actor_role": actor_role,
        "resource_id": resource_id,
        "subject_id": subject_id,
        # Values here are chosen by the caller and must stay free of
        # credentials; the logging sink redacts, but the database does not.
        "details": details or {},
    }

    if request is not None:
        entry["request_id"] = getattr(request.state, "request_id", None)
        if request.client:
            entry["ip_address"] = request.client.host

    try:
        get_supabase_admin_client().table("audit_log").insert(entry).execute()
    except Exception as exc:  # noqa: BLE001 - auditing must not break the action
        logger.error(
            f"AUDIT WRITE FAILED action={action.value} resource={resource} "
            f"actor={actor_id} resource_id={resource_id}: {exc.__class__.__name__}"
        )
