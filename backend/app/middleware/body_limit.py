"""Reject oversized request bodies before they are buffered.

File-size validation previously happened only after the entire upload had been
read into memory, so a large body consumed the memory it was meant to be
rejected for. Enforcing the ceiling at the transport layer means an oversized
body is refused as it streams, before the route ever runs.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger("body_limit")
settings = get_settings()

_BODYLESS_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "DELETE"})


def _too_large() -> JSONResponse:
    return JSONResponse(
        status_code=413,
        content={
            "code": "payload_too_large",
            "detail": (
                "Request body exceeds the maximum permitted size of "
                f"{settings.MAX_REQUEST_BYTES // (1024 * 1024)} MB."
            ),
        },
    )


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_bytes: int | None = None) -> None:  # noqa: ANN001
        super().__init__(app)
        self.max_bytes = max_bytes or settings.MAX_REQUEST_BYTES

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method in _BODYLESS_METHODS:
            return await call_next(request)

        # Fast path: trust a declared Content-Length to reject early, but never
        # to *accept* - it is client-supplied and may understate the real body.
        declared = request.headers.get("content-length")
        if declared is not None:
            try:
                if int(declared) > self.max_bytes:
                    logger.warning(f"Rejected oversized body: declared={declared} path={request.url.path}")
                    return _too_large()
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={"code": "bad_request", "detail": "Malformed Content-Length header."},
                )

        # Chunked or understated bodies are caught here, by counting bytes as
        # they arrive and aborting the moment the ceiling is crossed.
        body_size = 0
        overflowed = False

        async def counting_receive() -> dict:
            nonlocal body_size, overflowed
            message = await original_receive()
            if message["type"] == "http.request":
                body_size += len(message.get("body", b""))
                if body_size > self.max_bytes:
                    overflowed = True
                    return {"type": "http.disconnect"}
            return message

        original_receive = request.receive
        request._receive = counting_receive  # noqa: SLF001 - the supported Starlette hook

        response = await call_next(request)
        if overflowed:
            logger.warning(f"Rejected oversized streamed body on {request.url.path}")
            return _too_large()
        return response
