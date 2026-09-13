"""Per-request identity, timing and rate-limit headers.

Assigns every request a correlation id that is bound to the logging context and
returned to the client. When a user reports a failure, that id is the join key
between their screenshot, the log line and - once Phase 3 lands - the trace.
"""

from __future__ import annotations

import time
import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger

logger = get_logger("http")

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")

REQUEST_ID_HEADER = "X-Request-ID"

# Paths excluded from access logging to keep platform health probes from
# drowning the log stream.
_QUIET_PATHS = frozenset({"/health", "/metrics"})


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # An inbound id is honoured so a trace can span the frontend and API,
        # but it is length-capped and sanitized: it ends up in log output, and
        # unbounded client-controlled text there invites log injection.
        incoming = request.headers.get(REQUEST_ID_HEADER, "")
        request_id = (
            "".join(c for c in incoming if c.isalnum() or c in "-_")[:64] or uuid.uuid4().hex
        )

        token = request_id_ctx.set(request_id)
        request.state.request_id = request_id
        started = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - started) * 1000
            logger.exception(
                f"{request.method} {request.url.path} failed after {duration_ms:.1f}ms "
                f"[request_id={request_id}]"
            )
            raise
        finally:
            request_id_ctx.reset(token)

        duration_ms = (time.perf_counter() - started) * 1000
        response.headers[REQUEST_ID_HEADER] = request_id
        response.headers["Server-Timing"] = f"app;dur={duration_ms:.1f}"

        rate_limit = getattr(request.state, "rate_limit", None)
        if rate_limit is not None and rate_limit.limit:
            response.headers["X-RateLimit-Limit"] = str(rate_limit.limit)
            response.headers["X-RateLimit-Remaining"] = str(rate_limit.remaining)

        if request.url.path not in _QUIET_PATHS:
            logger.info(
                f"{request.method} {request.url.path} -> {response.status_code} "
                f"({duration_ms:.1f}ms) [request_id={request_id}]"
            )

        return response
