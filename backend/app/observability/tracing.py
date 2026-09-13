"""OpenTelemetry tracing and metrics, exported over OTLP to Grafana Cloud.

Auto-instrumentation covers the boundaries (HTTP in, HTTP out, Redis). What it
cannot see is the part of this system that actually costs money and time: which
stage of the RAG pipeline was slow, how many tokens a tutor turn burned, and
whether the deterministic scorer or the graph traversal dominated an
evaluation. Those are instrumented by hand in ``app.observability.spans``.

Everything here degrades to a no-op when ``OTEL_ENABLED`` is false, so local
development needs no collector running.
"""

from __future__ import annotations

from typing import Any

from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger("observability")
settings = get_settings()

_initialized = False


def _parse_headers(raw: str) -> dict[str, str]:
    """Parse ``key=value,key2=value2`` as used by OTEL_EXPORTER_OTLP_HEADERS."""
    headers: dict[str, str] = {}
    for pair in raw.split(","):
        if "=" in pair:
            key, _, value = pair.partition("=")
            headers[key.strip()] = value.strip()
    return headers


def setup_observability(app: Any) -> None:
    """Install tracing, metrics and auto-instrumentation.

    Safe to call more than once; subsequent calls are ignored.
    """
    global _initialized

    if not settings.OTEL_ENABLED:
        logger.info("OpenTelemetry disabled (OTEL_ENABLED=False).")
        return
    if _initialized:
        return

    try:
        from opentelemetry import metrics, trace
        from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased
    except ImportError as exc:
        logger.warning(f"OpenTelemetry packages unavailable, tracing disabled: {exc}")
        return

    endpoint = settings.OTEL_EXPORTER_OTLP_ENDPOINT.rstrip("/")
    if not endpoint:
        logger.warning("OTEL_ENABLED is set but OTEL_EXPORTER_OTLP_ENDPOINT is empty; tracing disabled.")
        return

    headers = _parse_headers(settings.OTEL_EXPORTER_OTLP_HEADERS)

    resource = Resource.create(
        {
            "service.name": settings.OTEL_SERVICE_NAME,
            "service.version": settings.APP_VERSION,
            "deployment.environment": settings.ENVIRONMENT,
        }
    )

    # ParentBased so a sampling decision made upstream is honoured; otherwise a
    # sampled frontend trace can lose its backend half and appear broken.
    tracer_provider = TracerProvider(
        resource=resource,
        sampler=ParentBased(root=TraceIdRatioBased(settings.OTEL_TRACES_SAMPLER_RATIO)),
    )
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces", headers=headers))
    )
    trace.set_tracer_provider(tracer_provider)

    metrics.set_meter_provider(
        MeterProvider(
            resource=resource,
            metric_readers=[
                PeriodicExportingMetricReader(
                    OTLPMetricExporter(endpoint=f"{endpoint}/v1/metrics", headers=headers),
                    export_interval_millis=30_000,
                )
            ],
        )
    )

    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=tracer_provider,
        # Health probes fire constantly and would dominate the trace volume
        # without telling anyone anything.
        excluded_urls="health,metrics",
    )
    HTTPXClientInstrumentor().instrument(tracer_provider=tracer_provider)

    try:
        from opentelemetry.instrumentation.redis import RedisInstrumentor

        RedisInstrumentor().instrument(tracer_provider=tracer_provider)
    except ImportError:
        pass

    _initialized = True
    logger.info(
        f"OpenTelemetry active: service={settings.OTEL_SERVICE_NAME} "
        f"endpoint={endpoint} sample_ratio={settings.OTEL_TRACES_SAMPLER_RATIO}"
    )


def shutdown_observability() -> None:
    """Flush pending spans and metrics on shutdown.

    Without this, the batch processor's buffer is lost on exit - which reliably
    drops the traces for whatever was happening when the process went down, the
    exact window someone will want to look at.
    """
    if not _initialized:
        return
    try:
        from opentelemetry import metrics, trace

        provider = trace.get_tracer_provider()
        if hasattr(provider, "shutdown"):
            provider.shutdown()

        meter_provider = metrics.get_meter_provider()
        if hasattr(meter_provider, "shutdown"):
            meter_provider.shutdown()

        logger.info("OpenTelemetry exporters flushed.")
    except Exception as exc:  # noqa: BLE001 - shutdown must not raise
        logger.warning(f"Error flushing telemetry: {exc.__class__.__name__}")
