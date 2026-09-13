"""Concrete email providers."""

from __future__ import annotations

import httpx

from app.config import get_settings
from app.core.logging import get_logger
from app.services.email.base import EmailMessage, EmailProvider, SendResult

logger = get_logger("email_provider")
settings = get_settings()

# 4xx responses other than 429 describe a problem with the request itself -
# a malformed address, an unverified sender domain, a revoked key. Retrying
# cannot fix any of them.
_PERMANENT_STATUSES = frozenset({400, 401, 403, 404, 409, 422})


class ResendProvider:
    name = "resend"

    async def send(self, message: EmailMessage) -> SendResult:
        payload: dict[str, object] = {
            "from": settings.EMAIL_FROM_ADDRESS,
            "to": [message.to],
            "subject": message.subject,
            "html": message.html,
            "text": message.text,
        }
        reply_to = message.reply_to or settings.EMAIL_REPLY_TO
        if reply_to:
            payload["reply_to"] = reply_to

        try:
            async with httpx.AsyncClient(timeout=settings.EMAIL_REQUEST_TIMEOUT_SECONDS) as client:
                response = await client.post(
                    settings.RESEND_API_URL,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                        "Content-Type": "application/json",
                    },
                )
        except httpx.TimeoutException:
            return SendResult(False, error="timeout", retryable=True)
        except httpx.HTTPError as exc:
            return SendResult(False, error=f"transport:{exc.__class__.__name__}", retryable=True)

        if response.status_code in (200, 201):
            provider_id = None
            try:
                provider_id = response.json().get("id")
            except ValueError:
                pass
            return SendResult(True, provider_id=provider_id)

        # The body may echo recipient addresses, so it is logged rather than
        # stored on the outbox row where it would be widely readable.
        logger.warning(f"Resend rejected message with status {response.status_code}")
        return SendResult(
            False,
            error=f"http_{response.status_code}",
            retryable=response.status_code not in _PERMANENT_STATUSES,
        )


class ConsoleProvider:
    """Prints messages instead of sending them.

    Local development default: the invitation flow can be exercised end to end
    without a verified sending domain, and without the risk of a test run
    mailing a real address.
    """

    name = "console"

    async def send(self, message: EmailMessage) -> SendResult:
        logger.info(
            "\n"
            "======================= EMAIL (not sent) =======================\n"
            f"To:      {message.to}\n"
            f"Subject: {message.subject}\n"
            "----------------------------------------------------------------\n"
            f"{message.text}\n"
            "================================================================"
        )
        return SendResult(True, provider_id="console")


def get_email_provider() -> EmailProvider:
    if settings.EMAIL_PROVIDER == "resend":
        return ResendProvider()
    return ConsoleProvider()
