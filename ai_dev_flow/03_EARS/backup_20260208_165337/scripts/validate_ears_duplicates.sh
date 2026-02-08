#!/bin/bash
###############################################################################
# EARS Duplicate Requirement ID Validator
#
# Purpose: Validates that EARS documents do not contain duplicate requirement
#          IDs within the same file. Complements validate_ears.py by focusing
#          on intra-file duplicate detection.
#
# Usage:
#   ./validate_ears_duplicates.sh [EARS_DIR]
#
# Arguments:
#   EARS_DIR    Optional. Path to EARS directory (default: docs/EARS/)
#
# Exit Codes:
#   0 - No duplicates found
#   1 - Duplicates detected
#   2 - Invalid arguments or directory not found
#
# Example:
#   ./validate_ears_duplicates.sh docs/EARS/
#   ./validate_ears_duplicates.sh  # Uses default docs/EARS/
#
# Created: 2025-12-21
# Part of: SDD Framework Validation Scripts
###############################################################################

set -euo pipefail

# Configuration
EARS_DIR="${1:-docs/EARS}"
SCRIPT_NAME=$(basename "$0")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
usage() {
    echo "Usage: $SCRIPT_NAME [EARS_DIR]"
    echo ""
    echo "Validates EARS documents for duplicate requirement IDs within files."
    echo ""
    echo "Arguments:"
    echo "  EARS_DIR    Path to EARS directory (default: docs/EARS/)"
    echo ""
    echo "Examples:"
    echo "  $SCRIPT_NAME"
    echo "  $SCRIPT_NAME /path/to/docs/EARS/"
    exit 2
}

error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
    exit 2
}

# Validate arguments
if [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]]; then
    usage
fi

# Validate EARS directory exists
if [[ ! -d "$EARS_DIR" ]]; then
    error "EARS directory not found: $EARS_DIR"
fi

# Main validation
echo "========================================"
echo "EARS Duplicate Requirement ID Check"
echo "========================================"
echo "Directory: $EARS_DIR"
echo ""

has_duplicates=0
files_checked=0

# Check each EARS file (EARS-NN range)
for file in "$EARS_DIR"/EARS-{01..99}_*.md; do
    # Skip if no files match pattern
    [[ -e "$file" ]] || continue

    filename=$(basename "$file")
    files_checked=$((files_checked + 1))

    # Extract requirement IDs (format: **EARS.NN.TT.SSS)
    # Use grep to find all EARS requirement IDs, sort them, and find duplicates
    duplicates=$(grep -oh "\*\*EARS\.[0-9][0-9]\.[0-9][0-9]\.[0-9][0-9][0-9]" "$file" 2>/dev/null | sort | uniq -d || true)

    if [[ -n "$duplicates" ]]; then
        echo -e "${RED}❌ $filename has duplicate requirement IDs:${NC}"
        echo "$duplicates" | sed 's/^/   /'
        echo ""
        has_duplicates=1
    fi
done

# Summary
echo "========================================"
if [[ $files_checked -eq 0 ]]; then
    echo -e "${YELLOW}⚠  No EARS files found in $EARS_DIR${NC}"
    exit 0
fi

if [[ $has_duplicates -eq 0 ]]; then
    echo -e "${GREEN}✅ No duplicate requirement IDs found${NC}"
    echo "Files checked: $files_checked"
    exit 0
else
    echo -e "${RED}❌ Duplicates found - review required${NC}"
    echo "Files checked: $files_checked"
    exit 1
fi
