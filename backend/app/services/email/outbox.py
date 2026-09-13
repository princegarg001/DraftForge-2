"""Email dispatch and delivery records.

**Why the outbox stores no token.** The obvious design queues the template plus
its context and lets a worker render and send later. That cannot be used for
invitations: the context would contain the raw invitation token, which would
then sit in a database row, in backups, and in anything that reads the table -
defeating the point of storing only its hash.

So invitations are rendered in-process and dispatched as a background task, and
the outbox row records only *metadata*: recipient, template name, status,
attempt count and error. The token exists in memory and in the delivered
message, nowhere else.

A permanently failed invitation is therefore not replayable, which is correct:
the teacher resends, and that mints a fresh token with a fresh expiry rather
than resurrecting an old one.
"""

from __future__ import annotations

import asyncio
from typing import Any

from app.config import get_settings
from app.core.logging import get_logger
from app.db.supabase import get_supabase_admin_client
from app.services.email.base import EmailMessage
from app.services.email.providers import get_email_provider

logger = get_logger("email_outbox")
settings = get_settings()

# Exponential backoff between in-process retries, in seconds.
_BACKOFF_SCHEDULE = (1, 4, 15, 60)


def _record(
    recipient: str,
    subject: str,
    template: str,
    related_type: str | None,
    related_id: str | None,
) -> str | None:
    """Create the delivery record. Returns its id, or None if recording failed."""
    try:
        result = (
            get_supabase_admin_client()
            .table("email_outbox")
            .insert(
                {
                    "recipient": recipient,
                    "subject": subject,
                    "template": template,
                    # Empty by design - see the module docstring.
                    "context": {},
                    "status": "SENDING",
                    "related_type": related_type,
                    "related_id": related_id,
                    "max_attempts": settings.EMAIL_MAX_RETRIES,
                }
            )
            .execute()
        )
        return result.data[0]["id"] if result.data else None
    except Exception as exc:  # noqa: BLE001 - bookkeeping must not block sending
        logger.error(f"Could not create outbox record for {recipient}: {exc.__class__.__name__}")
        return None


def _finalize(record_id: str | None, status: str, attempts: int, error: str | None, provider_id: str | None) -> None:
    if record_id is None:
        return
    patch: dict[str, Any] = {"status": status, "attempts": attempts}
    if error:
        patch["last_error"] = error[:500]
    if provider_id:
        patch["provider_id"] = provider_id
    if status == "SENT":
        patch["sent_at"] = "now()"
    try:
        get_supabase_admin_client().table("email_outbox").update(patch).eq("id", record_id).execute()
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Could not finalize outbox record {record_id}: {exc.__class__.__name__}")


async def dispatch(
    message: EmailMessage,
    template: str,
    related_type: str | None = None,
    related_id: str | None = None,
) -> bool:
    """Send a message, retrying transient failures, and record the outcome.

    Intended to run as a background task so a slow provider never holds up the
    request that triggered it. Returns True when delivery succeeded.
    """
    provider = get_email_provider()
    record_id = _record(message.to, message.subject, template, related_type, related_id)

    attempts = 0
    last_error: str | None = None

    for delay in (0, *_BACKOFF_SCHEDULE[: settings.EMAIL_MAX_RETRIES - 1]):
        if delay:
            await asyncio.sleep(delay)
        attempts += 1

        result = await provider.send(message)
        if result.success:
            logger.info(f"Email '{template}' delivered to {message.to} on attempt {attempts}")
            _finalize(record_id, "SENT", attempts, None, result.provider_id)
            return True

        last_error = result.error
        if not result.retryable:
            # A rejected address or unverified domain will not start working.
            logger.warning(
                f"Email '{template}' to {message.to} permanently rejected: {result.error}"
            )
            _finalize(record_id, "BOUNCED", attempts, result.error, None)
            return False

        logger.warning(
            f"Email '{template}' to {message.to} failed (attempt {attempts}): {result.error}"
        )

    logger.error(f"Email '{template}' to {message.to} exhausted {attempts} attempts")
    _finalize(record_id, "FAILED", attempts, last_error, None)
    return False
