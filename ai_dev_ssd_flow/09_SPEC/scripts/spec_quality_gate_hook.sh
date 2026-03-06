#!/bin/bash
# =============================================================================
# SPEC Quality Gate Hook
# Pre-commit hook for SPEC quality gate validation
# Wrapper for validate_spec_quality_score.sh
# =============================================================================

set -euo pipefail

# Get the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPEC_DIR="${1:-ai_dev_ssd_flow/09_SPEC}"

# Support both absolute and relative paths
if [[ ! "$SPEC_DIR" =~ ^/ ]]; then
    # Relative path - make absolute from git root
    GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "$(pwd)")
    SPEC_DIR="$GIT_ROOT/$SPEC_DIR"
fi

# Run quality gate validation
if [ -f "$SCRIPT_DIR/validate_spec_quality_score.sh" ]; then
    "$SCRIPT_DIR/validate_spec_quality_score.sh" "$SPEC_DIR"
else
    echo "ERROR: validate_spec_quality_score.sh not found"
    exit 1
fi
