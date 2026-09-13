"""Local verification of Supabase-issued access tokens.

The previous implementation called ``supabase.auth.get_user(token)`` on every
authenticated request. That added a network round-trip to the hot path of every
endpoint and made Supabase Auth a hard availability dependency: if it was slow
or down, the entire API was too.

Tokens are JWTs, so they can be verified locally from their signature. This
module does that, supporting both key types a Supabase project may issue:

* **Asymmetric (ES256/RS256)** - the project's public keys are fetched from its
  JWKS endpoint and cached. This is the preferred path.
* **Symmetric (HS256)** - verified with ``SUPABASE_JWT_SECRET``.

Algorithm confusion is the main hazard when supporting both. If the permitted
algorithms were taken from the token's own header, an attacker could take a
public RSA key from the JWKS, sign a token with it as an HMAC secret, set
``alg: HS256``, and have it verify. This module therefore derives the permitted
algorithm from the *key that was selected*, never from attacker-controlled
header input.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Final

import httpx
import jwt
from jwt import PyJWK, PyJWKSet
from pydantic import BaseModel, ConfigDict, Field

from app.config import get_settings
from app.core.constants import UserRole
from app.core.exceptions import AuthenticationError
from app.core.logging import get_logger

logger = get_logger("security")
settings = get_settings()

# Algorithms permitted per key type. "none" is absent by construction, and the
# symmetric and asymmetric sets are disjoint so a key can never be used with an
# algorithm of the wrong family.
_ASYMMETRIC_ALGORITHMS: Final[frozenset[str]] = frozenset({"RS256", "RS384", "RS512", "ES256", "ES384", "ES512"})
_SYMMETRIC_ALGORITHMS: Final[frozenset[str]] = frozenset({"HS256", "HS384", "HS512"})
_SUPPORTED_ALGORITHMS: Final[frozenset[str]] = _ASYMMETRIC_ALGORITHMS | _SYMMETRIC_ALGORITHMS


class TokenClaims(BaseModel):
    """Validated claims extracted from a Supabase access token.

    ``app_metadata`` is written only by trusted server-side code; ``user_metadata``
    is writable by the user at sign-up and is therefore never a source of
    authorization decisions.
    """

    model_config = ConfigDict(extra="ignore", frozen=True)

    sub: str
    email: str | None = None
    session_id: str | None = None
    app_metadata: dict[str, Any] = Field(default_factory=dict)
    user_metadata: dict[str, Any] = Field(default_factory=dict)
    expires_at: int | None = None

    @property
    def claimed_role(self) -> str | None:
        """Role asserted by ``app_metadata``, if any.

        This is a *hint* used only when provisioning a profile that does not yet
        exist. The authoritative role always comes from the ``profiles`` table -
        see ``app.dependencies.get_current_user``.
        """
        value = self.app_metadata.get("role")
        return str(value).upper() if value else None


class _JWKSCache:
    """Caches the project's JWKS with a TTL and a forced-refresh cooldown.

    An unknown ``kid`` triggers a refresh so that key rotation is picked up
    without a redeploy. The cooldown prevents that from becoming an
    amplification vector: without it, a client sending tokens with random
    ``kid`` values would drive one outbound JWKS request per inbound request.
    """

    def __init__(self) -> None:
        self._keys: dict[str, PyJWK] = {}
        self._fetched_at: float = 0.0
        self._last_forced_refresh: float = 0.0
        self._lock = asyncio.Lock()

    def _is_stale(self) -> bool:
        return (time.monotonic() - self._fetched_at) > settings.JWKS_CACHE_TTL_SECONDS

    async def _fetch(self) -> None:
        url = settings.jwks_url
        try:
            async with httpx.AsyncClient(timeout=settings.JWKS_REQUEST_TIMEOUT_SECONDS) as client:
                response = await client.get(url, headers={"apikey": settings.SUPABASE_ANON_KEY})
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            # A fetch failure must not invalidate keys already cached - serving
            # stale-but-valid keys is preferable to failing every request while
            # the JWKS endpoint is briefly unavailable.
            logger.warning(f"JWKS fetch failed for {url}: {exc.__class__.__name__}")
            if not self._keys:
                raise AuthenticationError("Unable to verify credentials at this time.") from exc
            return

        keys: dict[str, PyJWK] = {}
        for jwk in PyJWKSet.from_dict(payload).keys:
            if jwk.key_id:
                keys[jwk.key_id] = jwk

        if keys:
            self._keys = keys
            self._fetched_at = time.monotonic()
            logger.info(f"JWKS refreshed: {len(keys)} key(s) cached.")

    async def get(self, kid: str) -> PyJWK | None:
        if self._is_stale() or not self._keys:
            async with self._lock:
                if self._is_stale() or not self._keys:
                    await self._fetch()

        key = self._keys.get(kid)
        if key is not None:
            return key

        # Unknown kid: refresh once, subject to the cooldown.
        now = time.monotonic()
        if (now - self._last_forced_refresh) < settings.JWKS_REFRESH_COOLDOWN_SECONDS:
            return None

        async with self._lock:
            if (time.monotonic() - self._last_forced_refresh) < settings.JWKS_REFRESH_COOLDOWN_SECONDS:
                return self._keys.get(kid)
            self._last_forced_refresh = time.monotonic()
            await self._fetch()

        return self._keys.get(kid)

    def clear(self) -> None:
        self._keys.clear()
        self._fetched_at = 0.0


_jwks_cache = _JWKSCache()


def _read_unverified_header(token: str) -> dict[str, Any]:
    try:
        return jwt.get_unverified_header(token)
    except jwt.PyJWTError as exc:
        raise AuthenticationError("Malformed authentication token.") from exc


def _decode(token: str, key: Any, algorithms: list[str]) -> dict[str, Any]:
    """Decode with full claim validation.

    ``algorithms`` is derived from the selected key, never from the token
    header, which is what closes the algorithm-confusion hole.
    """
    return jwt.decode(
        token,
        key,
        algorithms=algorithms,
        audience=settings.JWT_AUDIENCE,
        issuer=settings.jwt_issuer,
        leeway=settings.JWT_LEEWAY_SECONDS,
        options={
            "verify_signature": True,
            "verify_exp": True,
            "verify_nbf": True,
            "verify_iat": True,
            "verify_aud": True,
            "verify_iss": True,
            "require": ["exp", "iat", "sub"],
        },
    )


async def verify_supabase_jwt(token: str) -> TokenClaims:
    """Verify a Supabase access token and return its validated claims.

    Raises ``AuthenticationError`` for any invalid token. The message returned
    to the client is deliberately generic; the specific reason is logged but
    never disclosed, since precise failure reasons help an attacker distinguish
    an expired token from a forged one.
    """
    if not token or not token.strip():
        raise AuthenticationError("Bearer token is missing.")

    header = _read_unverified_header(token)
    algorithm = str(header.get("alg", "")).upper()

    if algorithm not in _SUPPORTED_ALGORITHMS:
        logger.warning(f"Rejected token with unsupported alg={algorithm!r}")
        raise AuthenticationError("Invalid authentication token.")

    kid = header.get("kid")

    try:
        if kid:
            jwk = await _jwks_cache.get(str(kid))
            if jwk is None:
                logger.warning(f"No JWKS key matched kid={kid!r}")
                raise AuthenticationError("Invalid authentication token.")
            # Permitted algorithms come from the key's own family.
            permitted = sorted(_ASYMMETRIC_ALGORITHMS & {jwk.algorithm_name or algorithm})
            if not permitted:
                permitted = sorted(_ASYMMETRIC_ALGORITHMS)
            payload = _decode(token, jwk.key, permitted)
        else:
            if algorithm not in _SYMMETRIC_ALGORITHMS:
                # An asymmetric alg with no kid cannot select a key.
                raise AuthenticationError("Invalid authentication token.")
            payload = _decode(token, settings.SUPABASE_JWT_SECRET, ["HS256"])
    except AuthenticationError:
        raise
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationError("Session expired. Please sign in again.") from exc
    except jwt.PyJWTError as exc:
        logger.warning(f"Token verification failed: {exc.__class__.__name__}: {exc}")
        raise AuthenticationError("Invalid authentication token.") from exc

    subject = payload.get("sub")
    if not subject:
        raise AuthenticationError("Invalid authentication token.")

    return TokenClaims(
        sub=str(subject),
        email=payload.get("email"),
        session_id=payload.get("session_id"),
        app_metadata=payload.get("app_metadata") or {},
        user_metadata=payload.get("user_metadata") or {},
        expires_at=payload.get("exp"),
    )


def normalize_role(value: Any, default: UserRole = UserRole.STUDENT) -> UserRole:
    """Coerce an arbitrary role value to a known role, defaulting on anything unrecognised."""
    try:
        return UserRole(str(value).strip().upper())
    except (ValueError, AttributeError):
        return default
