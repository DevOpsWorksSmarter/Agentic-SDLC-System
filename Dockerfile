# ── Stage 1: Build dependencies ───────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: Runtime image ────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

ARG BUILD_DATE
ARG GIT_SHA

LABEL org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${GIT_SHA}" \
      org.opencontainers.image.title="Agentic SDLC System" \
      org.opencontainers.image.description="Multi-agent SDLC workflow orchestrator"

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser

# Copy application source
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser main.py ./
COPY --chown=appuser:appuser requirements.txt ./

# Create outputs directory with correct permissions
RUN mkdir -p /app/outputs && chown appuser:appuser /app/outputs

USER appuser

# Health check — verifies the Python environment is intact
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from src.models.state import WorkflowState; print('ok')" || exit 1

EXPOSE 8080

# Default: run the orchestrator in auto mode with the mandatory use case
CMD ["python", "main.py", "--auto", \
     "--requirement", "Build a scalable URL shortener service with APIs, persistence, and analytics.", \
     "--output-dir", "/app/outputs"]
