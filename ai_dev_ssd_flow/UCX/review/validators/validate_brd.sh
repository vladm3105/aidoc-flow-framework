#!/usr/bin/env bash
# =============================================================================
# validate_brd.sh — BRD Schema and Structure Validator
# =============================================================================
# Validates BRD documents for structural compliance.
#
# Usage:
#   ./validate_brd.sh <brd_path>
#
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/validate_common.sh"

BRD_PATH="${1:-}"

if [[ -z "$BRD_PATH" ]]; then
    echo "Usage: ./validate_brd.sh <brd_path>"
    exit 1
fi

if [[ ! -e "$BRD_PATH" ]]; then
    echo "Error: BRD path not found: $BRD_PATH"
    exit 1
fi

log_info "Validating BRD: $BRD_PATH"

# =============================================================================
# Collect files to validate
# =============================================================================
files=()
if [[ -d "$BRD_PATH" ]]; then
    while IFS= read -r -d '' f; do
        files+=("$f")
    done < <(find "$BRD_PATH" -name "*.md" -not -name "*REVIEW*" -not -name "*REPORT*" -print0)
else
    files=("$BRD_PATH")
fi

# =============================================================================
# Validate each file
# =============================================================================
for file in "${files[@]}"; do
    log_info "Checking: $(basename "$file")"

    # Check YAML frontmatter
    check_yaml_frontmatter "$file" "title,doc_id,version,status"

    # Check for BRD element IDs
    check_element_ids "$file" "BRD\.[0-9]+\.[0-9]+\.[0-9]+"

    # Check for required tags
    if grep -q "custom_fields:" "$file"; then
        if ! grep -q "artifact_type:\s*BRD" "$file"; then
            log_warning "Missing artifact_type: BRD in custom_fields"
        fi
    fi
done

# =============================================================================
# Check for required sections (in index or main file)
# =============================================================================
required_sections=(
    "Executive Summary"
    "Business Context"
    "Requirements"
    "Constraints"
)

# Find index file or main file
index_file=""
for file in "${files[@]}"; do
    if [[ "$(basename "$file")" == *"index"* || "$(basename "$file")" == *"0_"* ]]; then
        index_file="$file"
        break
    fi
done

if [[ -n "$index_file" ]]; then
    check_required_sections "$index_file" "${required_sections[@]}"
elif [[ ${#files[@]} -eq 1 ]]; then
    check_required_sections "${files[0]}" "${required_sections[@]}"
fi

# =============================================================================
# Check traceability
# =============================================================================
for file in "${files[@]}"; do
    check_trace_references "$file" "@(ref|prd):\s*\S+"
done

# =============================================================================
# Output
# =============================================================================
output_validation_summary "brd" "$BRD_PATH"
