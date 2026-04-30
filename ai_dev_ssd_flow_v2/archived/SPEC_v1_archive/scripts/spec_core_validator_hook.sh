#!/bin/bash
# =============================================================================
# SPEC Core Validator Hook
# Pre-commit hook for validating SPEC (Technical Specification) documents
# Wrapper for validate_spec.py with git-aware execution
# =============================================================================

set -euo pipefail

# Get the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPEC_DIR="${1:-ucx_flow_v3/09_SPEC}"

# Support both absolute and relative paths
if [[ ! "$SPEC_DIR" =~ ^/ ]]; then
    # Relative path - make absolute from git root
    GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "$(pwd)")
    SPEC_DIR="$GIT_ROOT/$SPEC_DIR"
fi

# Find all SPEC YAML files (excluding index and templates)
SPEC_FILES=$(find "$SPEC_DIR" -name "SPEC-[0-9]*_*.yaml" ! -name "*index*" ! -name "*TEMPLATE*" ! -path "*/examples/*" ! -path "*/archive/*" 2>/dev/null || true)

if [ -z "$SPEC_FILES" ]; then
    echo "No SPEC files found in $SPEC_DIR"
    exit 0
fi

ERRORS=0

# Validate each SPEC file
while IFS= read -r spec_file; do
    if [ -f "$spec_file" ]; then
        echo "Validating: $(basename "$spec_file")"
        if ! python3 "$SCRIPT_DIR/validate_spec.py" --spec-file "$spec_file" 2>&1; then
            ((ERRORS++))
        fi
    fi
done <<< "$SPEC_FILES"

if [ $ERRORS -gt 0 ]; then
    echo "SPEC core validation failed with $ERRORS errors"
    exit 1
fi

echo "SPEC core validation passed"
exit 0
