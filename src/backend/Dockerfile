# =============================================================================
# SICO GRC Backend - Secure Multi-Stage Production Build
# =============================================================================
# Security improvements:
# - Multi-stage build separates build-time from runtime dependencies
# - Python 3.11 slim (minimal Debian base)
# - Non-root user execution
# - Production wheels built separately
# - No build tools in final image
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder (compile dependencies)
# -----------------------------------------------------------------------------
FROM python:3.11.10-slim-bookworm AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies to a local directory (for copying to runtime)
RUN pip install --user --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --user --no-cache-dir -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 2: Production Runtime (minimal image)
# -----------------------------------------------------------------------------
FROM python:3.11.10-slim-bookworm AS runtime

# Install only runtime dependencies (PostgreSQL client library)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Create non-root user for running application
RUN groupadd -r appuser --gid=1000 && \
    useradd -r -g appuser --uid=1000 --home-dir=/app --shell=/bin/bash appuser && \
    chown -R appuser:appuser /app

# Copy Python dependencies from builder
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser . .

# Set Python path to include user-installed packages
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER appuser

# Expose application port
EXPOSE 8000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
