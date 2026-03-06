#!/usr/bin/env bash
# =============================================================================
# 02_index.sh — Step 2: Index Audit Report into Knowledge Base
# =============================================================================
# Usage: 02_index.sh <COUNCIL_AUDIT_REPORT.md>
# Indexes the report into RAG (pgvector) and Graph (Neo4j).
# GRACEFULLY SKIPS if KB_ENABLED=false or databases are not running.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CORE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")/core"

source "$CORE_DIR/config.sh"
source "$CORE_DIR/utils.sh"

REPORT_FILE="${1:-}"
[[ -z "$REPORT_FILE" ]] && die "Usage: 02_index.sh <REPORT.md>"
require_file "$REPORT_FILE"

log_step "Step 2: Indexing audit report into Knowledge Base"

# =============================================================================
# Graceful skip if KB not enabled
# =============================================================================
if [[ "${KB_ENABLED:-false}" != "true" ]]; then
  log_warn "KB_ENABLED=false — skipping Knowledge Base indexing (set KB_ENABLED=true to enable)"
  log_info "To enable: set KB_ENABLED=true in your .env and start KB services (project_knowledge/)"
  exit 0
fi

# =============================================================================
# Locate project_knowledge orchestrator
# =============================================================================
# Try relative to framework root, then common install paths
PK_ORCHESTRATOR=""
for candidate in \
  "$(git rev-parse --show-toplevel 2>/dev/null)/project_knowledge/orchestrator.py" \
  "/opt/data/docs_flow_framework/project_knowledge/orchestrator.py" \
  "$SCRIPT_DIR/../../../project_knowledge/orchestrator.py"; do
  [[ -f "$candidate" ]] && { PK_ORCHESTRATOR="$candidate"; break; }
done

if [[ -z "$PK_ORCHESTRATOR" ]]; then
  log_warn "project_knowledge/orchestrator.py not found — skipping KB indexing"
  exit 0
fi

log_info "Using orchestrator: $PK_ORCHESTRATOR"
log_info "Report:  $REPORT_FILE"

# =============================================================================
# RAG embedding (pgvector)
# =============================================================================
if [[ "${KB_RAG_ENABLED:-false}" == "true" ]]; then
  log_info "RAG: Embedding audit report chunks..."
  if [[ "${DRY_RUN:-false}" == "true" ]]; then
    log_dry "Would run: python3 $PK_ORCHESTRATOR rag_embed $REPORT_FILE"
  else
    if python3 "$PK_ORCHESTRATOR" rag_embed "$REPORT_FILE" 2>/dev/null; then
      log_ok "RAG: Audit report embedded into pgvector"
    else
      log_warn "RAG embedding failed (non-fatal) — KB may be unavailable"
    fi
  fi
else
  log_info "KB_RAG_ENABLED=false — skipping RAG embedding"
fi

# =============================================================================
# Graph extraction (Neo4j) — creates RemediationTask nodes
# =============================================================================
if [[ "${KB_GRAPH_ENABLED:-false}" == "true" ]]; then
  log_info "Graph: Extracting RemediationTask nodes..."
  if [[ "${DRY_RUN:-false}" == "true" ]]; then
    log_dry "Would run: python3 $PK_ORCHESTRATOR graph_extract $REPORT_FILE --type council_audit"
  else
    if python3 "$PK_ORCHESTRATOR" graph_extract "$REPORT_FILE" --type council_audit 2>/dev/null; then
      log_ok "Graph: RemediationTask nodes created in Neo4j"
    else
      log_warn "Graph extraction failed (non-fatal) — Neo4j may be unavailable"
    fi
  fi
else
  log_info "KB_GRAPH_ENABLED=false — skipping Graph extraction"
fi

log_ok "Step 2 complete"
