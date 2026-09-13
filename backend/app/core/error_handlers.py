"""Uniform error responses.

Every error leaves the API in the same shape::

    {"code": "...", "detail": "...", "request_id": "..."}

The ``request_id`` lets a user quote one value that pins down the exact log
line, without the response having to carry any diagnostic detail itself.

Unhandled exceptions return a generic message. A stack trace or exception
string in a response body is a reconnaissance gift - it reveals library
versions, file paths and query structure.
"""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import BaseAppException
from app.core.logging import get_logger
from app.middleware.request_context import request_id_ctx

logger = get_logger("errors")


def _payload(code: str, detail: str, **extra: object) -> dict[str, object]:
    return {"code": code, "detail": detail, "request_id": request_id_ctx.get(), **extra}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BaseAppException)
    async def handle_app_exception(_: Request, exc: BaseAppException) -> JSONResponse:
        # exc.extra holds internal context (service names, upstream reasons)
        # and is deliberately logged rather than serialized.
        if exc.extra:
            logger.warning(f"{exc.code}: {exc.detail} | context={exc.extra}")
        return JSONResponse(
            status_code=exc.status_code,
            content=_payload(exc.code, exc.detail),
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        # Field-level errors are safe and genuinely useful to the caller, but
        # the submitted input is stripped: echoing it back reflects attacker
        # payloads and can disclose another user's data in a shared context.
        errors = [
            {
                "field": ".".join(str(part) for part in err.get("loc", ()) if part != "body"),
                "message": err.get("msg", "Invalid value."),
                "type": err.get("type", "value_error"),
            }
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=jsonable_encoder(
                _payload("validation_failed", "The request payload failed validation.", errors=errors)
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = {
            401: "authentication_failed",
            403: "permission_denied",
            404: "not_found",
            405: "method_not_allowed",
            409: "conflict",
            413: "payload_too_large",
            415: "unsupported_media_type",
            429: "rate_limit_exceeded",
        }.get(exc.status_code, "error")
        return JSONResponse(
            status_code=exc.status_code,
            content=_payload(code, str(exc.detail)),
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        logger.opt(exception=exc).error(
            f"Unhandled {exc.__class__.__name__} on {request.method} {request.url.path}"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_payload(
                "internal_error",
                "An unexpected error occurred. Quote the request_id if you contact support.",
            ),
        )
