# =============================================================================
# Haystack RAG Service Dockerfile
# Service 1: Technical & Project Documentation
# =============================================================================

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY pyproject.toml .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install \
    "haystack-ai>=2.0" \
    "pgvector-haystack>=0.3.0" \
    "hayhooks[mcp]>=0.1.0" \
    "cohere>=5.0" \
    "openai>=1.0" \
    "pyyaml>=6.0" \
    "psycopg2-binary>=2.9" \
    "python-dotenv>=1.0"

# Copy application code
COPY src/ /app/src/
COPY config/ /app/config/

# Create directories
RUN mkdir -p /app/data /app/pipelines /app/logs

# Set Python path
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:1416/health || exit 1

# Expose Hayhooks port
EXPOSE 1416

# Default command: Start Hayhooks MCP server
CMD ["python", "-m", "hayhooks", "--host", "0.0.0.0", "--port", "1416", "--pipelines-dir", "/app/pipelines"]
