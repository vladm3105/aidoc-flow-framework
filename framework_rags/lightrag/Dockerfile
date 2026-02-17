# =============================================================================
# LightRAG Service Dockerfile
# Service 2: Research & Analysis Knowledge Base
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
    "lightrag-hku>=0.1.0" \
    "neo4j>=5.0" \
    "psycopg2-binary>=2.9" \
    "cohere>=5.0" \
    "openai>=1.0" \
    "fastapi>=0.110" \
    "uvicorn>=0.27" \
    "python-dotenv>=1.0" \
    "httpx>=0.27"

# Copy application code
COPY src/ /app/src/
COPY config/ /app/config/

# Create directories
RUN mkdir -p /app/data /app/inputs /app/logs

# Set Python path
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:9621/health || exit 1

# Expose LightRAG port
EXPOSE 9621

# Default command: Start LightRAG server
CMD ["python", "-m", "lightrag.api", "--host", "0.0.0.0", "--port", "9621"]
