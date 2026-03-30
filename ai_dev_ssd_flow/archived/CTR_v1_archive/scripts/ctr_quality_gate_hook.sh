#!/bin/bash
# =============================================================================
# CTR Quality Gate Hook
# Pre-commit hook for CTR quality gate validation
# Wrapper for validate_ctr_quality_score.sh
# =============================================================================

set -euo pipefail

# Get the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTR_DIR="${1:-ai_dev_ssd_flow/08_CTR}"

# Support both absolute and relative paths
if [[ ! "$CTR_DIR" =~ ^/ ]]; then
    # Relative path - make absolute from git root
    GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "$(pwd)")
    CTR_DIR="$GIT_ROOT/$CTR_DIR"
fi

# Run quality gate validation
if [ -f "$SCRIPT_DIR/validate_ctr_quality_score.sh" ]; then
    "$SCRIPT_DIR/validate_ctr_quality_score.sh" "$CTR_DIR"
else
    echo "ERROR: validate_ctr_quality_score.sh not found"
    exit 1
fi
