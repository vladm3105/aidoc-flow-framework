#!/bin/bash
# =============================================================================
# TSPEC TASKS-Ready Hook (CORRECTED VERSION v2.0)
# Validates TASKS-Ready scores with type-specific thresholds
# Handles multiple score formats and provides detailed feedback
# =============================================================================

set -euo pipefail

# Get the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TSPEC_DIR="${1:-ai_dev_ssd_flow/10_TSPEC}"
OVERRIDE_THRESHOLD="${2:-}"  # NEW v2.0: Optional threshold override

# Support both absolute and relative paths
if [[ ! "$TSPEC_DIR" =~ ^/ ]]; then
    GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "$(pwd)")
    TSPEC_DIR="$GIT_ROOT/$TSPEC_DIR"
fi

# Type-specific TASKS-Ready thresholds
declare -A MIN_SCORES=(
    ["UTEST"]=90
    ["ITEST"]=90
    ["STEST"]=100
    ["FTEST"]=90
    ["PTEST"]=85
    ["SECTEST"]=90
)

echo "========================================="
echo "TSPEC TASKS-Ready Validator"
echo "========================================="
echo "Location: $TSPEC_DIR"
if [[ -n "$OVERRIDE_THRESHOLD" ]]; then
    echo "Threshold Override: ${OVERRIDE_THRESHOLD}% (all types)"
fi
echo ""

TOTAL_FILES=0
PASSED_FILES=0
FAILED_FILES=0

# Function to extract TASKS-Ready score from file
extract_score() {
    local file="$1"

    # Try multiple patterns to handle different score formats:
    # - "TASKS-Ready Score: 95%"
    # - "TASKS-Ready Score: [95%]"
    # - "TASKS-Ready Score: 95/100"
    # - "TASKS-Ready Score [95]"

    local score=""

    # Pattern 1: XX% format
    score=$(grep -i "TASKS-Ready Score" "$file" | \
            grep -oE '[0-9]{1,3}%' | \
            head -1 | \
            tr -d '%' 2>/dev/null || echo "")

    if [ -n "$score" ]; then
        echo "$score"
        return 0
    fi

    # Pattern 2: XX/100 format
    score=$(grep -i "TASKS-Ready Score" "$file" | \
            grep -oE '[0-9]{1,3}/100' | \
            head -1 | \
            cut -d'/' -f1 2>/dev/null || echo "")

    if [ -n "$score" ]; then
        echo "$score"
        return 0
    fi

    # Pattern 3: [XX] format
    score=$(grep -i "TASKS-Ready Score" "$file" | \
            grep -oE '\[[0-9]{1,3}\]' | \
            head -1 | \
            tr -d '[]' 2>/dev/null || echo "")

    if [ -n "$score" ]; then
        echo "$score"
        return 0
    fi

    # No score found
    echo "0"
    return 1
}

# Validate each test type
for TYPE in "${!MIN_SCORES[@]}"; do
    # Use override threshold if provided, otherwise use type-specific
    if [[ -n "$OVERRIDE_THRESHOLD" ]]; then
        MIN_SCORE="$OVERRIDE_THRESHOLD"
    else
        MIN_SCORE="${MIN_SCORES[$TYPE]}"
    fi

    echo "--- Validating $TYPE (Threshold: ≥${MIN_SCORE}%) ---"

    # Find TSPEC files (excluding reserved IDs and reports)
    TYPE_FILES=$(find "$TSPEC_DIR/$TYPE" -type f -name "${TYPE}-[0-9]*_*.md" \
        ! -name "${TYPE}-00_*" \
        ! -name "*TEMPLATE*" \
        ! -name "*.A_audit_report*" \
        ! -name "*.R_review_report*" \
        ! -name "*.F_fix_report*" \
        ! -name "*.V_validation_report*" \
        2>/dev/null || true)

    if [ -z "$TYPE_FILES" ]; then
        echo "  No $TYPE files found"
        echo ""
        continue
    fi

    # Validate each file
    while IFS= read -r file; do
        ((TOTAL_FILES++)) || true

        filename=$(basename "$file")
        score=$(extract_score "$file")

        if [ "$score" = "0" ]; then
            echo "  ⚠️  $filename: TASKS-Ready score not found (defaulting to 0%)"
            ((FAILED_FILES++)) || true
        elif [ "$score" -lt "$MIN_SCORE" ]; then
            echo "  ❌ $filename: TASKS-Ready score ${score}% < ${MIN_SCORE}% (${TYPE} threshold)"
            ((FAILED_FILES++)) || true
        else
            echo "  ✅ $filename: TASKS-Ready score ${score}% ≥ ${MIN_SCORE}%"
            ((PASSED_FILES++)) || true
        fi
    done <<< "$TYPE_FILES"

    echo ""
done

# Summary
echo "========================================="
echo "TASKS-Ready Validation Summary"
echo "========================================="
echo "Total files validated: $TOTAL_FILES"
echo "Passed: $PASSED_FILES"
echo "Failed: $FAILED_FILES"
echo ""

if [ $FAILED_FILES -gt 0 ]; then
    echo "❌ TSPEC TASKS-Ready validation FAILED"
    echo ""
    echo "Action Required:"
    echo "- Update TSPEC documents to meet type-specific thresholds"
    echo "- Thresholds: UTEST/ITEST/FTEST/SECTEST ≥90%, STEST=100%, PTEST ≥85%"
    exit 1
else
    echo "✅ TSPEC TASKS-Ready validation PASSED"
    exit 0
fi
