#!/usr/bin/env bash
# sync-ucx-templates.sh — Sync Hermes SDD templates from UCX canonical v3 source
# Usage: ./sync-ucx-templates.sh [--dry-run] [--verify-only]
# Requires: bash 4+, rsync or cp, sed

set -euo pipefail

UCX_ROOT="/opt/data/ucx_framework/ucx_flow_v3"
DEST_DIR="${HOME}/.hermes/skills/spec-driven-development/sdd-orchestrator/templates"
DRY_RUN=0
VERIFY_ONLY=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run) DRY_RUN=1; shift ;;
        --verify-only) VERIFY_ONLY=1; shift ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

# 0. Verify source exists
if [[ ! -d "$UCX_ROOT" ]]; then
    echo "ERROR: UCX framework root not found: $UCX_ROOT"
    exit 1
fi

# 1. Verify-only mode
if [[ $VERIFY_ONLY -eq 1 ]]; then
    echo "=== Verification Mode ==="
    ERRORS=0
    for f in "$DEST_DIR"/*-TEMPLATE.yaml; do
        name=$(basename "$f")
        echo "Checking $name ..."

        # Check layer numbers
        if grep -q "Layer 9" "$f" || grep -q "Layer 10" "$f" || grep -q "Layer 11" "$f"; then
            echo "  FAIL: v2 layer numbers detected"
            ERRORS=$((ERRORS + 1))
        fi

        # Check cut layers
        if grep -iq "\bSYS\b.*Ready" "$f" || grep -iq "\bREQ\b.*Ready" "$f" || grep -iq "\bCTR\b.*Ready" "$f" || grep -iq "\bTSPEC\b.*Ready" "$f" || grep -iq "\bTASKS\b.*Ready" "$f"; then
            echo "  FAIL: cut layer readiness reference detected"
            ERRORS=$((ERRORS + 1))
        fi

        # Check server header
        if grep -q "server: mcp_ucx" "$f"; then
            echo "  FAIL: stale 'mcp_ucx' server header"
            ERRORS=$((ERRORS + 1))
        fi
        if ! grep -q "server: ucx_hermes" "$f"; then
            echo "  FAIL: missing 'ucx_hermes' server header"
            ERRORS=$((ERRORS + 1))
        fi

        if [[ $ERRORS -eq $(($ERRORS - 0)) ]]; then
            echo "  OK"
        fi
    done

    echo "=== $ERRORS error(s) found ==="
    exit $ERRORS
fi

# 2. Copy from canonical source
echo "=== Copying canonical v3 templates ==="
for src in "$UCX_ROOT"/*/*-TEMPLATE.yaml; do
    name=$(basename "$src")
    if [[ $DRY_RUN -eq 1 ]]; then
        echo "DRY-RUN: would copy $src -> $DEST_DIR/$name"
    else
        cp "$src" "$DEST_DIR/$name"
        echo "Copied $name"
    fi
done

# 3. Stamp server header
if [[ $DRY_RUN -eq 1 ]]; then
    echo "DRY-RUN: would sed 's/server: mcp_ucx/server: ucx_hermes/g' in $DEST_DIR/*.yaml"
else
    sed -i 's/server: mcp_ucx/server: ucx_hermes/g' "$DEST_DIR"/*-TEMPLATE.yaml
    echo "Stamped server headers to 'ucx_hermes'"
fi

# 4. Run verification after sync
if [[ $DRY_RUN -eq 0 ]]; then
    echo "=== Post-sync verification ==="
    $0 --verify-only
fi
