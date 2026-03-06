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
ptest_score=0
sectest_score=0

# Validate UTEST files
echo "--- UTEST Validation ---"
# Find files excluding templates, reserved IDs, and report files
utest_files=$(find "$DOCS_PATH/UTEST" -type f -name "UTEST-[0-9]*_*.md" \
    ! -name "UTEST-00_*" \
    ! -name "*TEMPLATE*" \
    ! -name "*FIX_PLAN*" \
    ! -name "*.A_audit_report*" \
    ! -name "*.R_review_report*" \
    ! -name "*.F_fix_report*" \
    ! -name "*.V_validation_report*" \
    2>/dev/null || true)
if [ -n "$utest_files" ]; then
    result=$(python3 "$SCRIPT_DIR/validate_utest.py" $utest_files 2>&1 || true)
    echo "$result"
    utest_score=$(echo "$result" | grep -oP '\d+(\.\d+)?(?=%)' | head -1 || echo "0")
    ((total_count++)) || true
else
    echo "No UTEST files found"
fi
echo ""

# Validate ITEST files
echo "--- ITEST Validation ---"
# Find files excluding templates, reserved IDs, and report files
itest_files=$(find "$DOCS_PATH/ITEST" -type f -name "ITEST-[0-9]*_*.md" \
    ! -name "ITEST-00_*" \
    ! -name "*TEMPLATE*" \
    ! -name "*FIX_PLAN*" \
    ! -name "*.A_audit_report*" \
    ! -name "*.R_review_report*" \
    ! -name "*.F_fix_report*" \
    ! -name "*.V_validation_report*" \
    2>/dev/null || true)
if [ -n "$itest_files" ]; then
    result=$(python3 "$SCRIPT_DIR/validate_itest.py" $itest_files 2>&1 || true)
    echo "$result"
    itest_score=$(echo "$result" | grep -oP '\d+(\.\d+)?(?=%)' | head -1 || echo "0")
    ((total_count++)) || true
else
    echo "No ITEST files found"
fi
echo ""

# Validate STEST files
echo "--- STEST Validation ---"
# Find files excluding templates, reserved IDs, and report files
stest_files=$(find "$DOCS_PATH/STEST" -type f -name "STEST-[0-9]*_*.md" \
    ! -name "STEST-00_*" \
    ! -name "*TEMPLATE*" \
    ! -name "*FIX_PLAN*" \
    ! -name "*.A_audit_report*" \
    ! -name "*.R_review_report*" \
    ! -name "*.F_fix_report*" \
    ! -name "*.V_validation_report*" \
    2>/dev/null || true)
if [ -n "$stest_files" ]; then
    result=$(python3 "$SCRIPT_DIR/validate_stest.py" $stest_files 2>&1 || true)
    echo "$result"
    stest_score=$(echo "$result" | grep -oP '\d+(\.\d+)?(?=%)' | head -1 || echo "0")
    ((total_count++)) || true
else
    echo "No STEST files found"
fi
echo ""

# Validate FTEST files
echo "--- FTEST Validation ---"
# Find files excluding templates, reserved IDs, and report files
ftest_files=$(find "$DOCS_PATH/FTEST" -type f -name "FTEST-[0-9]*_*.md" \
    ! -name "FTEST-00_*" \
    ! -name "*TEMPLATE*" \
    ! -name "*FIX_PLAN*" \
    ! -name "*.A_audit_report*" \
    ! -name "*.R_review_report*" \
    ! -name "*.F_fix_report*" \
    ! -name "*.V_validation_report*" \
    2>/dev/null || true)
if [ -n "$ftest_files" ]; then
    result=$(python3 "$SCRIPT_DIR/validate_ftest.py" $ftest_files 2>&1 || true)
    echo "$result"
    ftest_score=$(echo "$result" | grep -oP '\d+(\.\d+)?(?=%)' | head -1 || echo "0")
    ((total_count++)) || true
else
    echo "No FTEST files found"
fi
echo ""

# Validate PTEST files
echo "--- PTEST Validation ---"
# Find files excluding templates, reserved IDs, and report files
ptest_files=$(find "$DOCS_PATH/PTEST" -type f -name "PTEST-[0-9]*_*.md" \
    ! -name "PTEST-00_*" \
    ! -name "*TEMPLATE*" \
    ! -name "*FIX_PLAN*" \
    ! -name "*.A_audit_report*" \
    ! -name "*.R_review_report*" \
    ! -name "*.F_fix_report*" \
    ! -name "*.V_validation_report*" \
    2>/dev/null || true)
if [ -n "$ptest_files" ]; then
    result=$(python3 "$SCRIPT_DIR/validate_ptest.py" $ptest_files 2>&1 || true)
    echo "$result"
    ptest_score=$(echo "$result" | grep -oP '\d+(\.\d+)?(?=%)' | head -1 || echo "0")
    ((total_count++)) || true
else
    echo "No PTEST files found"
fi
echo ""

# Validate SECTEST files
echo "--- SECTEST Validation ---"
# Find files excluding templates, reserved IDs, and report files
sectest_files=$(find "$DOCS_PATH/SECTEST" -type f -name "SECTEST-[0-9]*_*.md" \
    ! -name "SECTEST-00_*" \
    ! -name "*TEMPLATE*" \
    ! -name "*FIX_PLAN*" \
    ! -name "*.A_audit_report*" \
    ! -name "*.R_review_report*" \
    ! -name "*.F_fix_report*" \
    ! -name "*.V_validation_report*" \
    2>/dev/null || true)
if [ -n "$sectest_files" ]; then
    result=$(python3 "$SCRIPT_DIR/validate_sectest.py" $sectest_files 2>&1 || true)
    echo "$result"
    sectest_score=$(echo "$result" | grep -oP '\d+(\.\d+)?(?=%)' | head -1 || echo "0")
    ((total_count++)) || true
else
    echo "No SECTEST files found"
fi
echo ""

# Calculate combined score
if [ "$total_count" -gt 0 ]; then
    # Sum scores (handle empty values)
    utest_score=${utest_score:-0}
    itest_score=${itest_score:-0}
    stest_score=${stest_score:-0}
    ftest_score=${ftest_score:-0}
    ptest_score=${ptest_score:-0}
    sectest_score=${sectest_score:-0}

    combined=$(echo "scale=1; ($utest_score + $itest_score + $stest_score + $ftest_score + $ptest_score + $sectest_score) / $total_count" | bc)

    echo "========================================="
    echo "Combined Quality Score Summary"
    echo "========================================="
    echo "UTEST:   ${utest_score}%"
    echo "ITEST:   ${itest_score}%"
    echo "STEST:   ${stest_score}%"
    echo "FTEST:   ${ftest_score}%"
    echo "PTEST:   ${ptest_score}%"
    echo "SECTEST: ${sectest_score}%"
    echo "-----------------------------------------"
    echo "Combined: ${combined}%"
    echo "========================================="

    # Determine overall status
    if (( $(echo "$combined >= 85" | bc -l) )); then
        echo "Status: [PASS] PASS"
        exit 0
    else
        echo "Status: [FAIL] FAIL (target: ≥85%)"
        exit 1
    fi
else
    echo "No TSPEC files found to validate"
    echo "Status: [PASS] SKIP (no files to validate)"
    exit 0
fi
