#!/bin/bash
# validate_tspec_quality_score.sh
# Calculate combined quality score for all TSPEC types
# Usage: ./validate_tspec_quality_score.sh <docs_path>

set -e

DOCS_PATH="${1:-docs/10_TSPEC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================="
echo "TSPEC Combined Quality Score Validation"
echo "========================================="
echo "Path: $DOCS_PATH"
echo ""

# Initialize counters
total_score=0
total_count=0
utest_score=0
itest_score=0
stest_score=0
ftest_score=0

# Validate UTEST files
echo "--- UTEST Validation ---"
if ls "$DOCS_PATH/UTEST/UTEST-"*.md &>/dev/null; then
    result=$(python3 "$SCRIPT_DIR/validate_utest.py" "$DOCS_PATH/UTEST/UTEST-"*.md 2>&1 || true)
    echo "$result"
    utest_score=$(echo "$result" | grep -oP '\d+(\.\d+)?(?=%)' | head -1 || echo "0")
    ((total_count++)) || true
else
    echo "No UTEST files found"
fi
echo ""

# Validate ITEST files
echo "--- ITEST Validation ---"
if ls "$DOCS_PATH/ITEST/ITEST-"*.md &>/dev/null; then
    result=$(python3 "$SCRIPT_DIR/validate_itest.py" "$DOCS_PATH/ITEST/ITEST-"*.md 2>&1 || true)
    echo "$result"
    itest_score=$(echo "$result" | grep -oP '\d+(\.\d+)?(?=%)' | head -1 || echo "0")
    ((total_count++)) || true
else
    echo "No ITEST files found"
fi
echo ""

# Validate STEST files
echo "--- STEST Validation ---"
if ls "$DOCS_PATH/STEST/STEST-"*.md &>/dev/null; then
    result=$(python3 "$SCRIPT_DIR/validate_stest.py" "$DOCS_PATH/STEST/STEST-"*.md 2>&1 || true)
    echo "$result"
    stest_score=$(echo "$result" | grep -oP '\d+(\.\d+)?(?=%)' | head -1 || echo "0")
    ((total_count++)) || true
else
    echo "No STEST files found"
fi
echo ""

# Validate FTEST files
echo "--- FTEST Validation ---"
if ls "$DOCS_PATH/FTEST/FTEST-"*.md &>/dev/null; then
    result=$(python3 "$SCRIPT_DIR/validate_ftest.py" "$DOCS_PATH/FTEST/FTEST-"*.md 2>&1 || true)
    echo "$result"
    ftest_score=$(echo "$result" | grep -oP '\d+(\.\d+)?(?=%)' | head -1 || echo "0")
    ((total_count++)) || true
else
    echo "No FTEST files found"
fi
echo ""

# Calculate combined score
if [ "$total_count" -gt 0 ]; then
    # Sum scores (handle empty values)
    utest_score=${utest_score:-0}
    itest_score=${itest_score:-0}
    stest_score=${stest_score:-0}
    ftest_score=${ftest_score:-0}

    combined=$(echo "scale=1; ($utest_score + $itest_score + $stest_score + $ftest_score) / $total_count" | bc)

    echo "========================================="
    echo "Combined Quality Score Summary"
    echo "========================================="
    echo "UTEST: ${utest_score}%"
    echo "ITEST: ${itest_score}%"
    echo "STEST: ${stest_score}%"
    echo "FTEST: ${ftest_score}%"
    echo "-----------------------------------------"
    echo "Combined: ${combined}%"
    echo "========================================="

    # Determine overall status
    if (( $(echo "$combined >= 85" | bc -l) )); then
        echo "Status: ✅ PASS"
        exit 0
    else
        echo "Status: ❌ FAIL (target: ≥85%)"
        exit 1
    fi
else
    echo "No TSPEC files found to validate"
    exit 2
fi
