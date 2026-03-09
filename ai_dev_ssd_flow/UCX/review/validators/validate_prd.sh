#!/usr/bin/env bash
# =============================================================================
# validate_prd.sh — PRD Schema and Structure Validator
# =============================================================================
# Validates PRD documents for structural compliance.
#
# Usage:
#   ./validate_prd.sh <prd_path>
#
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/validate_common.sh"

PRD_PATH="${1:-}"

if [[ -z "$PRD_PATH" ]]; then
    echo "Usage: ./validate_prd.sh <prd_path>"
    exit 1
fi

if [[ ! -e "$PRD_PATH" ]]; then
    echo "Error: PRD path not found: $PRD_PATH"
    exit 1
fi

log_info "Validating PRD: $PRD_PATH"

# =============================================================================
# Collect files to validate
# =============================================================================
files=()
if [[ -d "$PRD_PATH" ]]; then
    while IFS= read -r -d '' f; do
        files+=("$f")
    done < <(find "$PRD_PATH" -name "*.md" -not -name "*REVIEW*" -not -name "*REPORT*" -print0)
else
    files=("$PRD_PATH")
fi

# =============================================================================
# Validate each file
# =============================================================================
for file in "${files[@]}"; do
    log_info "Checking: $(basename "$file")"

    # Check YAML frontmatter
    check_yaml_frontmatter "$file" "title,doc_id,version,status"

    # Check for PRD element IDs
    check_element_ids "$file" "PRD\.[0-9]+\.(US|AC|NF|FT)\.[0-9]+"

    # Check for BRD traceability
    if ! grep -q "@brd:" "$file"; then
        log_warning "No BRD traceability (@brd: references) in $(basename "$file")"
    fi
done

# =============================================================================
# Check for required sections
# =============================================================================
required_sections=(
    "Overview"
    "User"
    "Stories"
    "Requirements"
)

for file in "${files[@]}"; do
    check_required_sections "$file" "${required_sections[@]}"
done

# =============================================================================
# Check for user story format
# =============================================================================
for file in "${files[@]}"; do
    if grep -q "As a\|I want\|So that" "$file"; then
        log_pass "User story format detected in $(basename "$file")"
    else
        log_warning "No user story format (As a/I want/So that) in $(basename "$file")"
    fi
done

# =============================================================================
# Output
# =============================================================================
output_validation_summary "prd" "$PRD_PATH"
