#!/bin/bash
# validate_all_tspec.sh
# Batch validation for all TSPEC documents
# Usage: ./validate_all_tspec.sh <docs_path>

set -e

DOCS_PATH="${1:-docs/10_TSPEC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================="
echo "TSPEC Batch Validation"
echo "========================================="
echo "Path: $DOCS_PATH"
echo "Date: $(date)"
echo ""

# Track results
declare -a failed_files=()
total_files=0
passed_files=0

# Function to validate files
validate_type() {
    local type="$1"
    local validator="$2"
    local pattern="$3"

    echo "--- $type Validation ---"

    if ls "$DOCS_PATH/$type/$pattern" &>/dev/null; then
        for file in "$DOCS_PATH/$type/$pattern"; do
            ((total_files++)) || true
            if python3 "$SCRIPT_DIR/$validator" "$file" --quality-gates; then
                ((passed_files++)) || true
            else
                failed_files+=("$file")
            fi
            echo ""
        done
    else
        echo "No $type files found"
    fi
    echo ""
}

# Validate each type
validate_type "UTEST" "validate_utest.py" "UTEST-*.md"
validate_type "ITEST" "validate_itest.py" "ITEST-*.md"
validate_type "STEST" "validate_stest.py" "STEST-*.md"
validate_type "FTEST" "validate_ftest.py" "FTEST-*.md"

# Summary
echo "========================================="
echo "Validation Summary"
echo "========================================="
echo "Total files: $total_files"
echo "Passed: $passed_files"
echo "Failed: $((total_files - passed_files))"

if [ ${#failed_files[@]} -gt 0 ]; then
    echo ""
    echo "Failed files:"
    for file in "${failed_files[@]}"; do
        echo "  - $file"
    done
    echo ""
    echo "Status: ❌ FAIL"
    exit 1
else
    echo ""
    echo "Status: ✅ ALL PASSED"
    exit 0
fi
