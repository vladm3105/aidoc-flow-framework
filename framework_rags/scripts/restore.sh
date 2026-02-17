#!/bin/bash
# =============================================================================
# RAG Services Restore Script
# Restores PostgreSQL, Neo4j, and LightRAG data from backup
# =============================================================================
#
# Backups are in: ${PROJECT_ROOT}/tools/data/backups/
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
BACKUPS_DIR="${DATA_DIR}/backups"
NEO4J_PASS="${NEO4J_PASSWORD:-neo4jpass}"

# List available backups
echo "Available backups in ${BACKUPS_DIR}:"
echo "======================================"
ls -la "${BACKUPS_DIR}" 2>/dev/null || echo "No backups found"
echo ""

# Get backup directory from argument or prompt
if [ -n "$1" ]; then
    BACKUP_DIR="$1"
else
    read -p "Enter backup directory name (e.g., backup_20260216_120000): " BACKUP_NAME
    BACKUP_DIR="${BACKUPS_DIR}/${BACKUP_NAME}"
fi

if [ ! -d "${BACKUP_DIR}" ]; then
    echo "Error: Backup directory not found: ${BACKUP_DIR}"
    exit 1
fi

echo ""
echo "Restoring from: ${BACKUP_DIR}"
echo "WARNING: This will overwrite current data!"
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Cancelled."
    exit 0
fi

# =============================================================================
# PostgreSQL Restore
# =============================================================================
if [ -f "${BACKUP_DIR}/postgres.sql" ]; then
    echo ""
    echo "Restoring PostgreSQL..."

    # Drop and recreate database
    docker-compose -f "${FRAMEWORK_DIR}/docker-compose.yml" exec -T postgres \
        psql -U raguser -d postgres -c "DROP DATABASE IF EXISTS ragdb;"
    docker-compose -f "${FRAMEWORK_DIR}/docker-compose.yml" exec -T postgres \
        psql -U raguser -d postgres -c "CREATE DATABASE ragdb;"

    # Restore data
    cat "${BACKUP_DIR}/postgres.sql" | docker-compose -f "${FRAMEWORK_DIR}/docker-compose.yml" exec -T postgres \
        psql -U raguser -d ragdb

    echo "  ✓ PostgreSQL restored"
else
    echo "  ⚠ No PostgreSQL backup found, skipping"
fi

# =============================================================================
# Neo4j Restore
# =============================================================================
if [ -f "${BACKUP_DIR}/neo4j.json" ]; then
    echo ""
    echo "Restoring Neo4j from JSON export..."

    # Copy backup file to container
    docker cp "${BACKUP_DIR}/neo4j.json" rag-neo4j:/var/lib/neo4j/import/backup.json

    # Clear existing data and import
    docker-compose -f "${FRAMEWORK_DIR}/docker-compose.yml" exec -T neo4j \
        cypher-shell -u neo4j -p "${NEO4J_PASS}" \
        "MATCH (n) DETACH DELETE n" || true

    docker-compose -f "${FRAMEWORK_DIR}/docker-compose.yml" exec -T neo4j \
        cypher-shell -u neo4j -p "${NEO4J_PASS}" \
        "CALL apoc.import.json('backup.json')" || true

    echo "  ✓ Neo4j restored (if APOC available)"
elif [ -f "${BACKUP_DIR}/neo4j_data.tar.gz" ]; then
    echo ""
    echo "Restoring Neo4j from data backup..."

    # Stop Neo4j
    docker-compose -f "${FRAMEWORK_DIR}/docker-compose.yml" stop neo4j

    # Restore data directory
    rm -rf "${DATA_DIR}/neo4j/data"/*
    tar xzf "${BACKUP_DIR}/neo4j_data.tar.gz" -C "${DATA_DIR}/neo4j"

    # Restart Neo4j
    docker-compose -f "${FRAMEWORK_DIR}/docker-compose.yml" start neo4j

    echo "  ✓ Neo4j data restored"
else
    echo "  ⚠ No Neo4j backup found, skipping"
fi

# =============================================================================
# LightRAG Data Restore
# =============================================================================
if [ -f "${BACKUP_DIR}/lightrag_data.tar.gz" ]; then
    echo ""
    echo "Restoring LightRAG data..."

    # Stop LightRAG to safely restore
    docker-compose -f "${FRAMEWORK_DIR}/docker-compose.yml" stop lightrag

    # Restore data
    rm -rf "${DATA_DIR}/lightrag/data"/*
    tar xzf "${BACKUP_DIR}/lightrag_data.tar.gz" -C "${DATA_DIR}/lightrag"

    # Restart LightRAG
    docker-compose -f "${FRAMEWORK_DIR}/docker-compose.yml" start lightrag

    echo "  ✓ LightRAG data restored"
else
    echo "  ⚠ No LightRAG backup found, skipping"
fi

# =============================================================================
# Haystack Data Restore
# =============================================================================
if [ -f "${BACKUP_DIR}/haystack_data.tar.gz" ]; then
    echo ""
    echo "Restoring Haystack data..."

    # Stop Haystack to safely restore
    docker-compose -f "${FRAMEWORK_DIR}/docker-compose.yml" stop haystack

    # Restore data
    rm -rf "${DATA_DIR}/haystack/data"/*
    rm -rf "${DATA_DIR}/haystack/pipelines"/*
    tar xzf "${BACKUP_DIR}/haystack_data.tar.gz" -C "${DATA_DIR}/haystack"

    # Restart Haystack
    docker-compose -f "${FRAMEWORK_DIR}/docker-compose.yml" start haystack

    echo "  ✓ Haystack data restored"
else
    echo "  ⚠ No Haystack backup found, skipping"
fi

# =============================================================================
# Summary
# =============================================================================
echo ""
echo "=============================================="
echo "Restore complete!"
echo "=============================================="
echo ""
echo "Data directory: ${DATA_DIR}"
echo "Run 'make rag-verify' to check service health"
