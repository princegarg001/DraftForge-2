"""Email provider interface.

Providers are kept behind this protocol so the choice of vendor stays a
configuration decision. Nothing above this layer imports Resend.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class EmailMessage:
    to: str
    subject: str
    html: str
    text: str
    reply_to: str | None = None


@dataclass(frozen=True)
class SendResult:
    success: bool
    provider_id: str | None = None
    error: str | None = None
    # False for permanent failures - an invalid address or a rejected domain
    # will not succeed on the tenth attempt any more than the first, and
    # retrying it burns the provider's reputation.
    retryable: bool = True


class EmailProvider(Protocol):
    name: str

    async def send(self, message: EmailMessage) -> SendResult: ...
