"""Distributed sliding-window rate limiting.

The API previously had no limits at all. That mattered most on the endpoints
that call Groq - ``/chat/send``, ``/ai/assist-drafting``, ``/roadmap/generate`` -
where an unauthenticated loop translates directly into an unbounded inference
bill, and on ``/auth/login``, where it left credential stuffing unthrottled.

Two independent controls are enforced:

* **Request rate** - a sliding-window counter, evaluated atomically in Redis.
* **Token budget** - a per-user daily ceiling on LLM tokens, which request-rate
  limits alone cannot express (one request can consume a hundred times another).

The sliding-window counter weights the previous window by how far the current
one has advanced. That avoids the burst-at-the-boundary flaw of fixed windows -
where a client can spend a full quota at 0:59 and another at 1:00 - while
costing O(1) memory per key, unlike a full request log.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum

from fastapi import Request

from app.config import get_settings
from app.core.exceptions import QuotaExceededError, RateLimitExceededError
from app.core.logging import get_logger
from app.core.redis_client import get_redis
from app.observability import record_rate_limit

logger = get_logger("rate_limit")
settings = get_settings()

# Evaluated server-side so the read-decide-increment sequence cannot interleave
# between competing workers.
_SLIDING_WINDOW_LUA = """
local cur_key   = KEYS[1]
local prev_key  = KEYS[2]
local limit     = tonumber(ARGV[1])
local window    = tonumber(ARGV[2])
local elapsed   = tonumber(ARGV[3])

local cur  = tonumber(redis.call('GET', cur_key) or '0')
local prev = tonumber(redis.call('GET', prev_key) or '0')

local weight    = (window - elapsed) / window
local estimated = (prev * weight) + cur

if estimated >= limit then
    return {0, limit, 0, window - elapsed}
end

cur = redis.call('INCR', cur_key)
if cur == 1 then
    redis.call('EXPIRE', cur_key, window * 2)
end

local used      = (prev * weight) + cur
local remaining = limit - used
if remaining < 0 then remaining = 0 end

return {1, limit, math.floor(remaining), 0}
"""

_TOKEN_BUDGET_LUA = """
local key    = KEYS[1]
local budget = tonumber(ARGV[1])
local cost   = tonumber(ARGV[2])
local ttl    = tonumber(ARGV[3])

local used = tonumber(redis.call('GET', key) or '0')
if used + cost > budget then
    return {0, budget, budget - used}
end

local total = redis.call('INCRBY', key, cost)
if total == cost then
    redis.call('EXPIRE', key, ttl)
end

return {1, budget, budget - total}
"""


class LimitScope(str, Enum):
    DEFAULT = "default"
    AUTH = "auth"
    LLM = "llm"
    UPLOAD = "upload"
    INVITE = "invite"


@dataclass(frozen=True)
class LimitRule:
    limit: int
    window_seconds: int

    @property
    def label(self) -> str:
        return f"{self.limit}/{self.window_seconds}s"


@dataclass(frozen=True)
class LimitResult:
    allowed: bool
    limit: int
    remaining: int
    retry_after_seconds: int


def rules_for(scope: LimitScope) -> tuple[LimitRule, ...]:
    if scope is LimitScope.AUTH:
        return (
            LimitRule(settings.RATE_LIMIT_AUTH_PER_MINUTE, 60),
            LimitRule(settings.RATE_LIMIT_AUTH_PER_HOUR, 3600),
        )
    if scope is LimitScope.LLM:
        return (
            LimitRule(settings.RATE_LIMIT_LLM_PER_MINUTE, 60),
            LimitRule(settings.RATE_LIMIT_LLM_PER_DAY, 86_400),
        )
    if scope is LimitScope.UPLOAD:
        return (LimitRule(settings.RATE_LIMIT_UPLOAD_PER_HOUR, 3600),)
    if scope is LimitScope.INVITE:
        return (LimitRule(settings.RATE_LIMIT_INVITE_PER_HOUR, 3600),)
    return (LimitRule(settings.RATE_LIMIT_DEFAULT_PER_MINUTE, 60),)


def client_identity(request: Request) -> str:
    """Identify the caller for limiting purposes.

    An authenticated user id is preferred: it survives NAT, where thousands of
    students behind one institutional IP would otherwise share a bucket.
    Anonymous callers fall back to peer IP, which uvicorn resolves from proxy
    headers when started with ``--proxy-headers``.
    """
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return f"user:{user_id}"
    client = request.client
    return f"ip:{client.host}" if client else "ip:unknown"


async def check_rate_limit(identity: str, scope: LimitScope) -> LimitResult:
    """Consume one unit against every rule for ``scope``."""
    if not settings.RATE_LIMIT_ENABLED:
        return LimitResult(True, 0, 0, 0)

    try:
        client = get_redis()
        tightest = LimitResult(True, 0, 2**31 - 1, 0)

        for rule in rules_for(scope):
            now = time.time()
            window_index = int(now // rule.window_seconds)
            elapsed = now - (window_index * rule.window_seconds)

            raw = await client.eval(
                _SLIDING_WINDOW_LUA,
                2,
                f"rl:{scope.value}:{identity}:{window_index}",
                f"rl:{scope.value}:{identity}:{window_index - 1}",
                str(rule.limit),
                str(rule.window_seconds),
                str(elapsed),
            )
            allowed, limit, remaining, retry_after = (int(v) for v in raw)

            if not allowed:
                logger.warning(f"Rate limit hit: identity={identity} scope={scope.value} rule={rule.label}")
                record_rate_limit(scope=scope.value, allowed=False)
                return LimitResult(False, limit, 0, max(1, retry_after))
            if remaining < tightest.remaining:
                tightest = LimitResult(True, limit, remaining, 0)

        return tightest

    except Exception as exc:  # noqa: BLE001 - Redis failure policy is configurable
        if settings.REDIS_REQUIRED:
            # Fail closed: an unavailable limiter must not become an open door.
            logger.error(f"Rate limiter unavailable, failing closed: {exc.__class__.__name__}")
            raise RateLimitExceededError(
                retry_after_seconds=5,
                detail="Service is temporarily unable to process requests. Please retry shortly.",
            ) from exc
        logger.warning(f"Rate limiter unavailable, failing open (dev): {exc.__class__.__name__}")
        return LimitResult(True, 0, 0, 0)


async def enforce_rate_limit(request: Request, scope: LimitScope) -> LimitResult:
    result = await check_rate_limit(client_identity(request), scope)
    if not result.allowed:
        raise RateLimitExceededError(retry_after_seconds=result.retry_after_seconds)
    return result


async def consume_token_budget(user_id: str, tokens: int) -> None:
    """Charge ``tokens`` against the caller's daily LLM allowance.

    Request-rate limits cannot bound spend on their own, because a single
    long-context request may cost orders of magnitude more than a short one.
    """
    budget = settings.LLM_TOKEN_BUDGET_PER_DAY
    if budget <= 0 or tokens <= 0:
        return

    day = time.strftime("%Y%m%d", time.gmtime())
    try:
        raw = await get_redis().eval(
            _TOKEN_BUDGET_LUA,
            1,
            f"budget:llm:{user_id}:{day}",
            str(budget),
            str(tokens),
            "172800",
        )
        allowed, _limit, remaining = (int(v) for v in raw)
    except Exception as exc:  # noqa: BLE001
        if settings.REDIS_REQUIRED:
            logger.error(f"Token budget check unavailable, failing closed: {exc.__class__.__name__}")
            raise QuotaExceededError("Usage metering is temporarily unavailable.") from exc
        logger.warning(f"Token budget check skipped (dev): {exc.__class__.__name__}")
        return

    if not allowed:
        logger.warning(f"LLM token budget exhausted for user={user_id}")
        raise QuotaExceededError(
            "You have reached your daily AI usage allowance. It resets at midnight UTC."
        )
    if remaining < budget * 0.1:
        logger.info(f"User {user_id} has {remaining} LLM tokens remaining today.")


class RateLimit:
    """FastAPI dependency applying a named limit scope.

    Usage::

        @router.post("/send", dependencies=[Depends(RateLimit(LimitScope.LLM))])
    """

    def __init__(self, scope: LimitScope = LimitScope.DEFAULT) -> None:
        self.scope = scope

    async def __call__(self, request: Request) -> None:
        result = await enforce_rate_limit(request, self.scope)
        # Surfaced as response headers by RateLimitHeaderMiddleware.
        request.state.rate_limit = result
