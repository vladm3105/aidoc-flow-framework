#!/bin/bash
# =============================================================================
# Haystack RAG Setup Script
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Setting up Haystack RAG service..."

# Install Python dependencies
echo "Installing dependencies..."
pip install -e "${PROJECT_DIR}[dev]"

# Create necessary directories
mkdir -p "${PROJECT_DIR}/data"
mkdir -p "${PROJECT_DIR}/pipelines"
mkdir -p "${PROJECT_DIR}/logs"

# Export pipelines to YAML for Hayhooks
echo "Exporting pipelines..."
python "${SCRIPT_DIR}/export_pipeline.py"

echo ""
echo "Setup complete!"
echo "Run 'make rag-up' from the framework_rags directory to start services."
