"""Manual span helpers for the paths auto-instrumentation cannot see.

A trace that shows only "POST /chat/send took 4.2s" is not actionable. These
helpers break that into embedding, vector search, graph traversal, reranking
and inference, so the slow stage is visible rather than inferred.

Every helper is a no-op when telemetry is off, and none of them may raise:
instrumentation that can break a request is worse than no instrumentation.
"""

from __future__ import annotations

import time
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from app.config import get_settings

settings = get_settings()

_tracer: Any = None


def _get_tracer() -> Any:
    global _tracer
    if _tracer is None:
        try:
            from opentelemetry import trace

            _tracer = trace.get_tracer("draftforge.api", settings.APP_VERSION)
        except Exception:  # noqa: BLE001
            _tracer = False
    return _tracer


@contextmanager
def span(name: str, **attributes: Any) -> Iterator[Any]:
    """Open a span, recording duration and any exception raised inside it."""
    tracer = _get_tracer()
    if not tracer:
        yield None
        return

    try:
        from opentelemetry.trace import Status, StatusCode
    except Exception:  # noqa: BLE001
        yield None
        return

    with tracer.start_as_current_span(name) as current:
        started = time.perf_counter()
        try:
            for key, value in attributes.items():
                if value is not None:
                    current.set_attribute(key, value)
            yield current
        except Exception as exc:
            current.set_status(Status(StatusCode.ERROR, exc.__class__.__name__))
            current.record_exception(exc)
            raise
        finally:
            current.set_attribute("duration_ms", round((time.perf_counter() - started) * 1000, 2))


def set_attributes(**attributes: Any) -> None:
    """Annotate the active span. Useful for values known only after the work."""
    tracer = _get_tracer()
    if not tracer:
        return
    try:
        from opentelemetry import trace

        current = trace.get_current_span()
        if current and current.get_span_context().is_valid:
            for key, value in attributes.items():
                if value is not None:
                    current.set_attribute(key, value)
    except Exception:  # noqa: BLE001
        pass


def add_event(name: str, **attributes: Any) -> None:
    tracer = _get_tracer()
    if not tracer:
        return
    try:
        from opentelemetry import trace

        current = trace.get_current_span()
        if current and current.get_span_context().is_valid:
            current.add_event(name, {k: v for k, v in attributes.items() if v is not None})
    except Exception:  # noqa: BLE001
        pass


def current_trace_id() -> str | None:
    """Hex trace id of the active span, for correlating a log line or an error."""
    try:
        from opentelemetry import trace

        context = trace.get_current_span().get_span_context()
        return format(context.trace_id, "032x") if context.is_valid else None
    except Exception:  # noqa: BLE001
        return None
