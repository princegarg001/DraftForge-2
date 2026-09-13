"""Logging configuration.

Two sinks, selected by ``LOG_FORMAT``: a colourized human-readable one for
local work, and single-line JSON for deployed environments, where logs are
shipped to Loki and need to be queryable by field rather than grep-able by eye.

Every record carries the current ``request_id``, and - once tracing is enabled -
the active ``trace_id`` and ``span_id``, so a log line in Loki links directly to
its trace in Tempo.

Sensitive values are redacted at the sink. Relying on every call site to
remember not to log a token is a losing strategy; enforcing it in one place is
not.
"""

from __future__ import annotations

import json
import logging
import re
import sys
from typing import Any

from loguru import logger

from app.config import get_settings

settings = get_settings()

# Patterns redacted from every emitted message.
_REDACTIONS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"), "<jwt:redacted>"),
    (re.compile(r"\bgsk_[A-Za-z0-9]{20,}"), "<groq-key:redacted>"),
    (re.compile(r"\bre_[A-Za-z0-9_-]{20,}"), "<resend-key:redacted>"),
    (re.compile(r"\bglc_[A-Za-z0-9+/=]{20,}"), "<grafana-token:redacted>"),
    (re.compile(r"(?i)(authorization|api[-_]?key|password|secret|token)([\"']?\s*[:=]\s*[\"']?)[^\s\"',}]+"),
     r"\1\2<redacted>"),
    (re.compile(r"://[^:/@\s]+:[^@/\s]+@"), "://<credentials:redacted>@"),
)


def _redact(text: str) -> str:
    for pattern, replacement in _REDACTIONS:
        text = pattern.sub(replacement, text)
    return text


def _context() -> dict[str, str]:
    # Imported lazily: this module is imported by config-time code, and the
    # middleware module imports logging in turn.
    from app.middleware.request_context import request_id_ctx

    ctx: dict[str, str] = {"request_id": request_id_ctx.get()}

    try:
        from opentelemetry import trace

        span = trace.get_current_span()
        span_context = span.get_span_context()
        if span_context.is_valid:
            ctx["trace_id"] = format(span_context.trace_id, "032x")
            ctx["span_id"] = format(span_context.span_id, "016x")
    except Exception:  # noqa: BLE001 - tracing is optional
        pass

    return ctx


def _json_sink(message: Any) -> None:
    record = message.record
    payload = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "logger": record["extra"].get("name", record["name"]),
        "message": _redact(record["message"]),
        "module": record["module"],
        "function": record["function"],
        "line": record["line"],
        **_context(),
    }

    if record["exception"] is not None:
        exc = record["exception"]
        payload["exception"] = {
            "type": exc.type.__name__ if exc.type else None,
            "value": _redact(str(exc.value)) if exc.value else None,
        }

    extra = {k: v for k, v in record["extra"].items() if k != "name"}
    if extra:
        payload["extra"] = extra

    sys.stdout.write(json.dumps(payload, default=str) + "\n")


def _console_format(record: Any) -> str:
    record["extra"]["request_id"] = _context()["request_id"]
    return (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<magenta>{extra[request_id]}</magenta> | "
        "<cyan>{extra[name]}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>\n{exception}"
    )


def _patch_message(record: Any) -> None:
    record["message"] = _redact(record["message"])


class _InterceptHandler(logging.Handler):
    """Routes stdlib logging (uvicorn, httpx, neo4j) through loguru.

    Without this, library logs bypass the JSON sink entirely and arrive in Loki
    unstructured and unredacted.
    """

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.bind(name=record.name).opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def configure_logging() -> None:
    logger.remove()
    level = "DEBUG" if settings.DEBUG else settings.LOG_LEVEL.upper()

    if settings.LOG_FORMAT == "json":
        logger.add(_json_sink, level=level, enqueue=True)
    else:
        logger.add(
            sys.stdout,
            level=level,
            format=_console_format,
            colorize=True,
            enqueue=True,
            backtrace=True,
            diagnose=not settings.is_production,  # never expose locals in production
        )

    logger.configure(patcher=_patch_message)

    logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "httpx", "httpcore", "neo4j", "hpack"):
        stdlib_logger = logging.getLogger(name)
        stdlib_logger.handlers = [_InterceptHandler()]
        stdlib_logger.propagate = False


configure_logging()


def get_logger(name: str):  # noqa: ANN201 - loguru's bound logger type is not public
    return logger.bind(name=name)
