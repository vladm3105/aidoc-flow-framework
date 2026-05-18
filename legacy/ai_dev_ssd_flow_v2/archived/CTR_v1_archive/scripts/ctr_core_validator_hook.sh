#!/bin/bash
# =============================================================================
# CTR Core Validator Hook
# Pre-commit hook for validating CTR (Contract) documents
# Wrapper for validate_ctr.sh with git-aware execution
# =============================================================================

set -euo pipefail

# Get the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTR_DIR="${1:-ucx_flow_v3/08_CTR}"

# Support both absolute and relative paths
if [[ ! "$CTR_DIR" =~ ^/ ]]; then
    # Relative path - make absolute from git root
    GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "$(pwd)")
    CTR_DIR="$GIT_ROOT/$CTR_DIR"
fi

# Find all CTR markdown files (excluding index and templates)
CTR_FILES=$(find "$CTR_DIR" -name "CTR-[0-9]*_*.md" ! -name "*index*" ! -name "*TEMPLATE*" 2>/dev/null || true)

if [ -z "$CTR_FILES" ]; then
    echo "No CTR files found in $CTR_DIR"
    exit 0
fi

ERRORS=0

# Validate each CTR file
while IFS= read -r ctr_file; do
    if [ -f "$ctr_file" ]; then
        echo "Validating: $(basename "$ctr_file")"
        if ! "$SCRIPT_DIR/validate_ctr.sh" "$ctr_file" --strict 2>&1; then
            ((ERRORS++))
        fi
    fi
done <<< "$CTR_FILES"

if [ $ERRORS -gt 0 ]; then
    echo "CTR core validation failed with $ERRORS errors"
    exit 1
fi

echo "CTR core validation passed"
exit 0
