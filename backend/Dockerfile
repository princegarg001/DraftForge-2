# =============================================================================
# Stage 1 - builder: compile wheels with the toolchain, then discard it.
# =============================================================================
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY requirements.txt .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip setuptools wheel \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# =============================================================================
# Stage 2 - runtime: no compiler, no package manager cache, unprivileged user.
# =============================================================================
FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8000

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system --gid 1001 draftforge \
    && useradd --system --uid 1001 --gid draftforge --create-home draftforge

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
COPY --chown=draftforge:draftforge . .

# FastEmbed downloads and caches the ONNX model at first use; give it a
# writable location owned by the unprivileged user so the image can stay
# read-only elsewhere.
ENV FASTEMBED_CACHE_PATH=/home/draftforge/.cache/fastembed
RUN mkdir -p "$FASTEMBED_CACHE_PATH" && chown -R draftforge:draftforge "$FASTEMBED_CACHE_PATH"

USER draftforge

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD curl -fsS "http://127.0.0.1:${PORT}/health" || exit 1

# Honour the platform-injected $PORT (Render, Fly, Cloud Run) instead of
# hardcoding 8000.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips='*'"]
