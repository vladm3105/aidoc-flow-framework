#!/bin/bash
# =============================================================================
# LightRAG Service Setup Script
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Setting up LightRAG service..."

# Install Python dependencies
echo "Installing dependencies..."
pip install -e "${PROJECT_DIR}[dev]"

# Create necessary directories
mkdir -p "${PROJECT_DIR}/data/rag_storage"
mkdir -p "${PROJECT_DIR}/data/inputs"
mkdir -p "${PROJECT_DIR}/logs"

# Install daniel-lightrag-mcp for MCP bridge
echo "Installing daniel-lightrag-mcp..."
if [ ! -d "/opt/daniel-lightrag-mcp" ]; then
    git clone https://github.com/desimpkins/daniel-lightrag-mcp.git /opt/daniel-lightrag-mcp
    cd /opt/daniel-lightrag-mcp && pip install -e .
else
    echo "daniel-lightrag-mcp already installed"
fi

echo ""
echo "Setup complete!"
echo "Run 'make rag-up' from the framework_rags directory to start services."
