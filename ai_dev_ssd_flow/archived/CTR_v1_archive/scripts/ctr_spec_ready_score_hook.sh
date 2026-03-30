#!/bin/bash
# =============================================================================
# CTR SPEC-Ready Score Hook
# Pre-commit hook for validating CTR SPEC-Ready score (≥90% required)
# Wrapper for validate_ctr_spec_readiness.py
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

# Check for Python validator
if [ ! -f "$SCRIPT_DIR/validate_ctr_spec_readiness.py" ]; then
    echo "ERROR: validate_ctr_spec_readiness.py not found"
    exit 1
fi

# Get threshold from environment or use default
SPEC_READY_THRESHOLD="${CTR_SPEC_READY_THRESHOLD:-90}"

# Find all CTR markdown files (excluding index and templates)
CTR_FILES=$(find "$CTR_DIR" -name "CTR-[0-9]*_*.md" ! -name "*index*" ! -name "*TEMPLATE*" 2>/dev/null || true)

if [ -z "$CTR_FILES" ]; then
    echo "No CTR files found in $CTR_DIR"
    exit 0
fi

ERRORS=0

# Validate each CTR file's SPEC-Ready score
while IFS= read -r ctr_file; do
    if [ -f "$ctr_file" ]; then
        echo "Checking SPEC-Ready score: $(basename "$ctr_file")"

        # Run Python validator
        if ! python3 "$SCRIPT_DIR/validate_ctr_spec_readiness.py" --ctr-file "$ctr_file" --min-score "$SPEC_READY_THRESHOLD" 2>&1; then
            echo "ERROR: SPEC-Ready score below threshold ($SPEC_READY_THRESHOLD%)"
            ((ERRORS++))
        fi
    fi
done <<< "$CTR_FILES"

if [ $ERRORS -gt 0 ]; then
    echo "CTR SPEC-Ready score validation failed ($ERRORS files below threshold)"
    exit 1
fi

echo "CTR SPEC-Ready score validation passed (all files ≥${SPEC_READY_THRESHOLD}%)"
exit 0
