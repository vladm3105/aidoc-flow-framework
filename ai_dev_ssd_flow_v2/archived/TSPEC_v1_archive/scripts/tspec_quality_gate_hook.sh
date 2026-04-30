#!/bin/bash
# =============================================================================
# TSPEC Quality Gate Hook (CORRECTED VERSION v2.0)
# Pre-commit hook for TSPEC quality gate validation
# Wrapper for validate_tspec_quality_score.sh
# =============================================================================

set -euo pipefail

# Get the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TSPEC_DIR="${1:-ucx_flow_v3/10_TSPEC}"

# Support both absolute and relative paths
if [[ ! "$TSPEC_DIR" =~ ^/ ]]; then
    # Relative path - make absolute from git root
    GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "$(pwd)")
    TSPEC_DIR="$GIT_ROOT/$TSPEC_DIR"
fi

echo "========================================="
echo "TSPEC Quality Gate Validator"
echo "========================================="
echo "Location: $TSPEC_DIR"
echo ""

# Run quality gate validation
if [ -f "$SCRIPT_DIR/validate_tspec_quality_score.sh" ]; then
    if "$SCRIPT_DIR/validate_tspec_quality_score.sh" "$TSPEC_DIR"; then
        echo ""
        echo "✅ TSPEC quality gates PASSED"
        exit 0
    else
        echo ""
        echo "❌ TSPEC quality gates FAILED"
        exit 1
    fi
else
    echo "ERROR: validate_tspec_quality_score.sh not found at $SCRIPT_DIR"
    echo "Please ensure TSPEC quality score validator is installed"
    exit 1
fi
