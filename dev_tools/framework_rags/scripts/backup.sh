#!/bin/bash
# =============================================================================
# RAG Services Backup Script
# Backs up PostgreSQL, Neo4j, and LightRAG data
# =============================================================================
#
# Data is stored in: ${PROJECT_ROOT}/tools/data/
# Backups go to: ${PROJECT_ROOT}/tools/data/backups/
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRAMEWORK_DIR="$(dirname "$SCRIPT_DIR")"

# Load environment
if [ -f "${FRAMEWORK_DIR}/.env" ]; then
    source "${FRAMEWORK_DIR}/.env"
fi

# Verify PROJECT_ROOT is set
if [ -z "${PROJECT_ROOT}" ]; then
    echo "ERROR: PROJECT_ROOT not set. Please set it in .env"
    exit 1
fi

DATA_DIR="${PROJECT_ROOT}/tools/data"
BACKUP_DIR="${DATA_DIR}/backups/backup_$(date +%Y%m%d_%H%M%S)"

echo "Creating backup directory: ${BACKUP_DIR}"
mkdir -p "${BACKUP_DIR}"

# =============================================================================
# PostgreSQL Backup
# =============================================================================
echo ""
echo "Backing up PostgreSQL..."

if docker-compose -f "${FRAMEWORK_DIR}/docker-compose.yml" exec -T postgres pg_isready -U raguser -d ragdb > /dev/null 2>&1; then
    docker-compose -f "${FRAMEWORK_DIR}/docker-compose.yml" exec -T postgres \
        pg_dump -U raguser ragdb > "${BACKUP_DIR}/postgres.sql"
    echo "  ✓ PostgreSQL backup: ${BACKUP_DIR}/postgres.sql"
else
    echo "  ✗ PostgreSQL not running, skipping backup"
fi

# =============================================================================
# Neo4j Backup
# =============================================================================
echo ""
echo "Backing up Neo4j..."

if docker-compose -f "${FRAMEWORK_DIR}/docker-compose.yml" exec -T neo4j neo4j status > /dev/null 2>&1; then
    # Neo4j Community Edition doesn't support online backup
    # We'll export using Cypher instead
    NEO4J_PASS="${NEO4J_PASSWORD:-neo4jpass}"
    docker-compose -f "${FRAMEWORK_DIR}/docker-compose.yml" exec -T neo4j \
        cypher-shell -u neo4j -p "${NEO4J_PASS}" \
        "CALL apoc.export.json.all('backup.json', {useTypes: true})" > /dev/null 2>&1 || true

    # Copy the export file
    docker cp rag-neo4j:/var/lib/neo4j/backup.json "${BACKUP_DIR}/neo4j.json" 2>/dev/null || \
        echo "  ⚠ Neo4j APOC export not available, backing up data directory"

    # Also backup the data directory directly
    if [ -d "${DATA_DIR}/neo4j/data" ]; then
        tar czf "${BACKUP_DIR}/neo4j_data.tar.gz" -C "${DATA_DIR}/neo4j" data
        echo "  ✓ Neo4j data backup: ${BACKUP_DIR}/neo4j_data.tar.gz"
    fi
else
    echo "  ✗ Neo4j not running, skipping backup"
fi

# =============================================================================
# LightRAG Data Backup
# =============================================================================
echo ""
echo "Backing up LightRAG data..."

if [ -d "${DATA_DIR}/lightrag/data" ]; then
    tar czf "${BACKUP_DIR}/lightrag_data.tar.gz" -C "${DATA_DIR}/lightrag" data
    echo "  ✓ LightRAG data: ${BACKUP_DIR}/lightrag_data.tar.gz"
else
    echo "  ✗ LightRAG data directory not found, skipping backup"
fi

# =============================================================================
# Haystack Data Backup
# =============================================================================
echo ""
echo "Backing up Haystack data..."

if [ -d "${DATA_DIR}/haystack/data" ]; then
    tar czf "${BACKUP_DIR}/haystack_data.tar.gz" -C "${DATA_DIR}/haystack" data pipelines
    echo "  ✓ Haystack data: ${BACKUP_DIR}/haystack_data.tar.gz"
else
    echo "  ✗ Haystack data directory not found, skipping backup"
fi

# =============================================================================
# Summary
# =============================================================================
echo ""
echo "=============================================="
echo "Backup complete: ${BACKUP_DIR}"
echo "=============================================="
ls -lh "${BACKUP_DIR}"

# Calculate total size
TOTAL_SIZE=$(du -sh "${BACKUP_DIR}" | cut -f1)
echo ""
echo "Total backup size: ${TOTAL_SIZE}"
echo "Data directory: ${DATA_DIR}"
