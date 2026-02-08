#!/bin/bash
###############################################################################
# EARS Structural Consistency Validator
#
# Purpose: Validates that all EARS documents have required structural sections
#          for traceability and BDD progression. Complements validate_ears.py
#          by providing batch consistency checking across all EARS files.
#
# Required Sections:
#   - Document Control (metadata)
#   - BDD-Ready Score (quality gate metric)
#   - Document Revision History (change tracking)
#   - Traceability section (upstream/downstream links)
#   - @brd and @prd tags (cumulative tagging)
#   - References section (documentation standards)
#
# Usage:
#   ./validate_ears_consistency.sh [EARS_DIR] [--strict]
#
# Arguments:
#   EARS_DIR    Optional. Path to EARS directory (default: docs/EARS/)
#   --strict    Optional. Fail if References section missing (default: warning)
#
# Exit Codes:
#   0 - All checks passed or only non-critical warnings
#   1 - Critical validation failures detected
#   2 - Invalid arguments or directory not found
#
# Example:
#   ./validate_ears_consistency.sh
#   ./validate_ears_consistency.sh docs/EARS/ --strict
#
# Created: 2025-12-21
# Part of: SDD Framework Validation Scripts
###############################################################################

set -euo pipefail

# Configuration
EARS_DIR="${1:-docs/EARS}"
STRICT_MODE=false
SCRIPT_NAME=$(basename "$0")

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --strict)
            STRICT_MODE=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            EARS_DIR="$1"
            shift
            ;;
    esac
done

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
usage() {
    echo "Usage: $SCRIPT_NAME [EARS_DIR] [--strict]"
    echo ""
    echo "Validates EARS documents for structural consistency."
    echo ""
    echo "Arguments:"
    echo "  EARS_DIR    Path to EARS directory (default: docs/EARS/)"
    echo "  --strict    Fail if References section missing (default: warning)"
    echo ""
    echo "Examples:"
    echo "  $SCRIPT_NAME"
    echo "  $SCRIPT_NAME docs/EARS/ --strict"
    exit 2
}

error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
    exit 2
}

# Validate EARS directory exists
if [[ ! -d "$EARS_DIR" ]]; then
    error "EARS directory not found: $EARS_DIR"
fi

# Main validation
echo "========================================"
echo "EARS Structural Consistency Check"
echo "========================================"
echo "Directory: $EARS_DIR"
echo "Strict mode: $STRICT_MODE"
echo ""

total_files=0
pass_count=0
files_with_warnings=0

# Check each EARS file (EARS-NN range)
for file in "$EARS_DIR"/EARS-{01..99}_*.md; do
    # Skip if no files match pattern
    [[ -e "$file" ]] || continue

    filename=$(basename "$file")
    total_files=$((total_files + 1))

    echo "Checking $filename..."
    critical_issues=0
    warnings=0

    # Check for Document Control section (CRITICAL)
    if ! grep -q "^## Document Control" "$file"; then
        echo -e "  ${RED}❌ Missing Document Control section${NC}"
        critical_issues=$((critical_issues + 1))
    fi

    # Check for BDD-Ready Score (CRITICAL)
    if ! grep -q "BDD-Ready Score" "$file"; then
        echo -e "  ${RED}❌ Missing BDD-Ready Score${NC}"
        critical_issues=$((critical_issues + 1))
    fi

    # Check for Document Revision History (CRITICAL)
    if ! grep -q "Document Revision History" "$file"; then
        echo -e "  ${RED}❌ Missing Document Revision History${NC}"
        critical_issues=$((critical_issues + 1))
    fi

    # Check for Traceability section (CRITICAL)
    if ! grep -q "^## [0-9]\+\. Traceability" "$file"; then
        echo -e "  ${RED}❌ Missing Traceability section${NC}"
        critical_issues=$((critical_issues + 1))
    fi

    # Check for @brd tags (CRITICAL)
    if ! grep -q "^@brd:" "$file"; then
        echo -e "  ${RED}❌ Missing @brd tags${NC}"
        critical_issues=$((critical_issues + 1))
    fi

    # Check for @prd tags (CRITICAL)
    if ! grep -q "^@prd:" "$file"; then
        echo -e "  ${RED}❌ Missing @prd tags${NC}"
        critical_issues=$((critical_issues + 1))
    fi

    # Check for References section (WARNING in normal mode, ERROR in strict mode)
    if ! grep -q "^## [0-9]\+\. References" "$file"; then
        if [[ "$STRICT_MODE" == "true" ]]; then
            echo -e "  ${RED}❌ Missing References section (strict mode)${NC}"
            critical_issues=$((critical_issues + 1))
        else
            echo -e "  ${YELLOW}⚠  Missing References section (non-blocking)${NC}"
            warnings=$((warnings + 1))
        fi
    fi

    # Determine file status
    if [[ $critical_issues -eq 0 ]]; then
        if [[ $warnings -eq 0 ]]; then
            echo -e "  ${GREEN}✅ All checks passed${NC}"
            pass_count=$((pass_count + 1))
        else
            echo -e "  ${YELLOW}⚠  Passed with warnings${NC}"
            pass_count=$((pass_count + 1))
            files_with_warnings=$((files_with_warnings + 1))
        fi
    fi

    echo ""
done

# Summary
echo "========================================"
if [[ $total_files -eq 0 ]]; then
    echo -e "${YELLOW}⚠  No EARS files found in $EARS_DIR${NC}"
    exit 0
fi

echo "Files checked: $total_files"
echo "Files passed: $pass_count"
if [[ $files_with_warnings -gt 0 ]]; then
    echo -e "${YELLOW}Files with warnings: $files_with_warnings${NC}"
fi
echo "========================================"

if [[ $pass_count -eq $total_files ]]; then
    echo -e "${GREEN}✅ All structural consistency checks passed${NC}"
    if [[ $files_with_warnings -gt 0 ]]; then
        echo -e "${YELLOW}Note: $files_with_warnings file(s) have non-blocking warnings${NC}"
    fi
    exit 0
else
    failed=$((total_files - pass_count))
    echo -e "${RED}❌ $failed file(s) failed critical checks${NC}"
    exit 1
fi
