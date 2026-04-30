#!/bin/bash
# =============================================================================
# TSPEC Core Validator Hook (CORRECTED VERSION v2.0)
# Pre-commit hook for validating all TSPEC test types
# Handles nested folders, reserved IDs, and report file exclusion
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

# NEW (v2.0): Verify TSPEC directory exists
if [[ ! -d "$TSPEC_DIR" ]]; then
    echo "ERROR: TSPEC directory not found: $TSPEC_DIR" >&2
    echo "Please verify the path and try again." >&2
    exit 2
fi

# Validation counters
TOTAL_FILES=0
ERRORS=0
WARNINGS=0

echo "========================================="
echo "TSPEC Core Validator"
echo "========================================="
echo "Location: $TSPEC_DIR"
echo "Date: $(date)"
echo ""

# Function to validate files of a specific type
validate_test_type() {
    local TYPE="$1"
    local validator_script=$(echo "$TYPE" | tr '[:upper:]' '[:lower:]')

    echo "--- Validating $TYPE ---"

    # NEW (v2.0): Check if type directory exists
    if [[ ! -d "$TSPEC_DIR/$TYPE" ]]; then
        echo "  Type directory not found: $TSPEC_DIR/$TYPE"
        echo ""
        return 0
    fi

    # Find TSPEC files in nested folders, excluding:
    # - Reserved IDs (TYPE-00_*)
    # - Templates (*TEMPLATE*)
    # - Audit reports (*.A_audit_report*)
    # - Review reports (*.R_review_report*)
    # - Fix reports (*.F_fix_report*)
    # - Validation reports (*.V_validation_report*)
    local TYPE_FILES=$(find "$TSPEC_DIR/$TYPE" -type f -name "${TYPE}-[0-9]*_*.md" \
        ! -name "${TYPE}-00_*" \
        ! -name "*TEMPLATE*" \
        ! -name "*.A_audit_report*" \
        ! -name "*.R_review_report*" \
        ! -name "*.F_fix_report*" \
        ! -name "*.V_validation_report*" \
        2>/dev/null || true)

    if [ -z "$TYPE_FILES" ]; then
        echo "  No $TYPE files found (or all excluded)"
        echo ""
        return 0
    fi

    # Validate each file
    while IFS= read -r file; do
        if [ -f "$file" ]; then
            ((TOTAL_FILES++)) || true
            echo "  Validating: $(basename "$file")"

            # Run type-specific validator
            if python3 "$SCRIPT_DIR/validate_${validator_script}.py" "$file" 2>&1; then
                echo "    ✓ PASS"
            else
                local exit_code=$?
                if [ $exit_code -eq 1 ]; then
                    echo "    ⚠ WARNINGS"
                    ((WARNINGS++)) || true
                elif [ $exit_code -eq 2 ]; then
                    echo "    ✗ FAIL"
                    ((ERRORS++)) || true
                fi
            fi
            echo ""
        fi
    done <<< "$TYPE_FILES"
}

# Validate all test types
for TYPE in UTEST ITEST STEST FTEST PTEST SECTEST; do
    validate_test_type "$TYPE"
done

# Summary
echo "========================================="
echo "Validation Summary"
echo "========================================="
echo "Total files validated: $TOTAL_FILES"
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"
echo ""

if [ $ERRORS -gt 0 ]; then
    echo "❌ TSPEC core validation FAILED with $ERRORS errors"
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo "⚠️  TSPEC core validation passed with $WARNINGS warnings"
    exit 0
else
    echo "✅ TSPEC core validation PASSED"
    exit 0
fi
