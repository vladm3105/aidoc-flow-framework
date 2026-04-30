#!/bin/bash
# =============================================================================
# SPEC Implementation-Ready Score Hook
# Pre-commit hook for validating SPEC Implementation-Ready score (≥90% required)
# Wrapper for validate_spec_implementation_readiness.py
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

# Check for Python validator
if [ ! -f "$SCRIPT_DIR/validate_spec_implementation_readiness.py" ]; then
    echo "ERROR: validate_spec_implementation_readiness.py not found"
    exit 1
fi

# Get threshold from environment or use default
IMPL_READY_THRESHOLD="${SPEC_IMPL_READY_THRESHOLD:-90}"

# Find all SPEC YAML files (excluding index and templates)
SPEC_FILES=$(find "$SPEC_DIR" -name "SPEC-[0-9]*_*.yaml" ! -name "*index*" ! -name "*TEMPLATE*" ! -path "*/examples/*" ! -path "*/archive/*" 2>/dev/null || true)

if [ -z "$SPEC_FILES" ]; then
    echo "No SPEC files found in $SPEC_DIR"
    exit 0
fi

ERRORS=0

# Validate each SPEC file's Implementation-Ready score
while IFS= read -r spec_file; do
    if [ -f "$spec_file" ]; then
        echo "Checking Implementation-Ready score: $(basename "$spec_file")"

        # Run Python validator
        if ! python3 "$SCRIPT_DIR/validate_spec_implementation_readiness.py" --spec-file "$spec_file" --min-score "$IMPL_READY_THRESHOLD" 2>&1; then
            echo "ERROR: Implementation-Ready score below threshold ($IMPL_READY_THRESHOLD%)"
            ((ERRORS++))
        fi
    fi
done <<< "$SPEC_FILES"

if [ $ERRORS -gt 0 ]; then
    echo "SPEC Implementation-Ready score validation failed ($ERRORS files below threshold)"
    exit 1
fi

echo "SPEC Implementation-Ready score validation passed (all files ≥${IMPL_READY_THRESHOLD}%)"
exit 0
