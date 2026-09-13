"""Shared async Redis connection pool.

Redis backs rate limiting, LLM token budgets and the email outbox. Whether an
outage should fail open or closed is a deployment decision, not a code one:
``REDIS_REQUIRED`` controls it, and production forces it on so limits cannot
silently stop being enforced.
"""

from __future__ import annotations

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool

from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger("redis")
settings = get_settings()

_pool: ConnectionPool | None = None
_client: redis.Redis | None = None


def get_redis() -> redis.Redis:
    global _pool, _client
    if _client is None:
        _pool = ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=50,
            decode_responses=True,
            socket_connect_timeout=2.0,
            socket_timeout=2.0,
            retry_on_timeout=True,
            health_check_interval=30,
        )
        _client = redis.Redis(connection_pool=_pool)
        logger.info("Redis connection pool initialized.")
    return _client


async def close_redis() -> None:
    global _pool, _client
    if _client is not None:
        await _client.aclose()
        _client = None
    if _pool is not None:
        await _pool.disconnect()
        _pool = None
    logger.info("Redis connection pool closed.")


async def check_redis_health() -> bool:
    try:
        return bool(await get_redis().ping())
    except Exception as exc:  # noqa: BLE001 - health probe must never raise
        logger.warning(f"Redis health check failed: {exc.__class__.__name__}")
        return False
