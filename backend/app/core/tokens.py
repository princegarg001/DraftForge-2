"""Single-use token generation and verification.

Invitation tokens are bearer credentials: whoever holds one can create an
account bound to the invited address. They are therefore treated like
passwords - only a hash is stored, so a database read yields nothing usable.

A plain SHA-256 is correct here, unlike for passwords. These tokens carry 256
bits of entropy from ``secrets``, so there is no dictionary to attack and no
reason to pay the cost of a slow KDF on a lookup that happens on every
acceptance request.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

# 32 bytes -> 43 URL-safe characters.
_TOKEN_BYTES = 32

# Ambiguous characters removed: join codes are read aloud and retyped, and
# 0/O and 1/I/L account for most transcription errors.
_JOIN_CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
_JOIN_CODE_LENGTH = 8


def generate_token() -> tuple[str, str]:
    """Return ``(raw_token, token_hash)``.

    The raw token is returned once, to be embedded in an email. Only the hash
    is ever persisted.
    """
    raw = secrets.token_urlsafe(_TOKEN_BYTES)
    return raw, hash_token(raw)


def hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def verify_token(raw: str, expected_hash: str) -> bool:
    """Constant-time comparison, so timing cannot be used to recover a token."""
    return hmac.compare_digest(hash_token(raw), expected_hash)


def generate_join_code() -> str:
    return "".join(secrets.choice(_JOIN_CODE_ALPHABET) for _ in range(_JOIN_CODE_LENGTH))


def expiry_from_now(hours: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=hours)


def is_expired(expires_at: str | datetime) -> bool:
    if isinstance(expires_at, str):
        # Postgres renders +00:00; fromisoformat wants Z normalized.
        expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) >= expires_at
