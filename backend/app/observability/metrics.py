"""Domain metrics.

RED metrics for HTTP come from auto-instrumentation. These cover what is
specific to this system and cannot be inferred from request counts:

* **LLM cost and latency** - tokens are the unit that maps to money, and one
  request can cost a hundred times another, so request rate says nothing useful
  about spend.
* **Retrieval quality** - a RAG answer degrades silently. Score distribution
  and result counts are the signal that indexing or embedding has regressed.
* **Evaluation throughput** - the deterministic scorer is the product's core
  claim; a regression in its latency or score distribution matters more than
  any endpoint's p99.

All instruments are created lazily and are no-ops when telemetry is off.
"""

from __future__ import annotations

from typing import Any

from app.config import get_settings

settings = get_settings()

_meter: Any = None
_instruments: dict[str, Any] = {}


def _get_meter() -> Any:
    global _meter
    if _meter is None:
        try:
            from opentelemetry import metrics

            _meter = metrics.get_meter("draftforge.api", settings.APP_VERSION)
        except Exception:  # noqa: BLE001 - telemetry must never break a request
            _meter = False
    return _meter


def _counter(name: str, unit: str, description: str) -> Any:
    meter = _get_meter()
    if not meter:
        return None
    if name not in _instruments:
        _instruments[name] = meter.create_counter(name, unit=unit, description=description)
    return _instruments[name]


def _histogram(name: str, unit: str, description: str) -> Any:
    meter = _get_meter()
    if not meter:
        return None
    if name not in _instruments:
        _instruments[name] = meter.create_histogram(name, unit=unit, description=description)
    return _instruments[name]


def _record(instrument: Any, value: float, attributes: dict[str, Any], add: bool) -> None:
    if instrument is None:
        return
    try:
        if add:
            instrument.add(value, attributes)
        else:
            instrument.record(value, attributes)
    except Exception:  # noqa: BLE001 - never let a metric break the caller
        pass


# ---------------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------------
def record_llm_call(
    *,
    provider: str,
    model: str,
    operation: str,
    duration_seconds: float,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    success: bool = True,
) -> None:
    attributes = {
        "llm.provider": provider,
        "llm.model": model,
        "llm.operation": operation,
        "llm.success": success,
    }
    _record(
        _counter("draftforge.llm.calls", "1", "LLM invocations"), 1, attributes, add=True
    )
    _record(
        _histogram("draftforge.llm.duration", "s", "LLM call latency"),
        duration_seconds,
        attributes,
        add=False,
    )
    if prompt_tokens:
        _record(
            _counter("draftforge.llm.tokens", "1", "Tokens consumed"),
            prompt_tokens,
            {**attributes, "llm.token_kind": "prompt"},
            add=True,
        )
    if completion_tokens:
        _record(
            _counter("draftforge.llm.tokens", "1", "Tokens consumed"),
            completion_tokens,
            {**attributes, "llm.token_kind": "completion"},
            add=True,
        )


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------
def record_retrieval(
    *,
    stage: str,
    document_type: str,
    duration_seconds: float,
    result_count: int,
    top_score: float | None = None,
) -> None:
    attributes = {"rag.stage": stage, "rag.document_type": document_type}
    _record(
        _histogram("draftforge.rag.duration", "s", "Retrieval stage latency"),
        duration_seconds,
        attributes,
        add=False,
    )
    _record(
        _histogram("draftforge.rag.results", "1", "Results returned per retrieval"),
        result_count,
        attributes,
        add=False,
    )
    if top_score is not None:
        # A falling top score is the earliest sign that retrieval quality has
        # regressed, well before anyone reports a bad answer.
        _record(
            _histogram("draftforge.rag.top_score", "1", "Best similarity score"),
            top_score,
            attributes,
            add=False,
        )


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------
def record_evaluation(
    *, document_type: str, duration_seconds: float, overall_score: float, success: bool = True
) -> None:
    attributes = {"evaluation.document_type": document_type, "evaluation.success": success}
    _record(
        _counter("draftforge.evaluations", "1", "Evaluations run"), 1, attributes, add=True
    )
    _record(
        _histogram("draftforge.evaluation.duration", "s", "Evaluation latency"),
        duration_seconds,
        attributes,
        add=False,
    )
    if success:
        _record(
            _histogram("draftforge.evaluation.score", "1", "Score distribution"),
            overall_score,
            attributes,
            add=False,
        )


# ---------------------------------------------------------------------------
# Platform events
# ---------------------------------------------------------------------------
def record_invitation(*, outcome: str) -> None:
    _record(
        _counter("draftforge.invitations", "1", "Invitation outcomes"),
        1,
        {"invitation.outcome": outcome},
        add=True,
    )


def record_email(*, template: str, status: str, attempts: int) -> None:
    attributes = {"email.template": template, "email.status": status}
    _record(_counter("draftforge.emails", "1", "Email delivery outcomes"), 1, attributes, add=True)
    _record(
        _histogram("draftforge.email.attempts", "1", "Attempts before resolution"),
        attempts,
        attributes,
        add=False,
    )


def record_rate_limit(*, scope: str, allowed: bool) -> None:
    _record(
        _counter("draftforge.rate_limit.decisions", "1", "Rate limit decisions"),
        1,
        {"rate_limit.scope": scope, "rate_limit.allowed": allowed},
        add=True,
    )


def record_auth_event(*, event: str, success: bool) -> None:
    """Authentication outcomes. A spike in failures is the signal for
    credential stuffing, which is otherwise invisible in request counts."""
    _record(
        _counter("draftforge.auth.events", "1", "Authentication outcomes"),
        1,
        {"auth.event": event, "auth.success": success},
        add=True,
    )
