#!/usr/bin/env bash
# =============================================================================
# validate_generic.sh — Generic Document Validator
# =============================================================================
# Generic validator for document types without specific validators.
# Performs basic structural and metadata checks.
#
# Usage:
#   ./validate_generic.sh <doc_type> <doc_path>
#
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/validate_common.sh"

DOC_TYPE="${1:-}"
DOC_PATH="${2:-}"

if [[ -z "$DOC_TYPE" || -z "$DOC_PATH" ]]; then
    echo "Usage: ./validate_generic.sh <doc_type> <doc_path>"
    exit 1
fi

if [[ ! -e "$DOC_PATH" ]]; then
    echo "Error: Document path not found: $DOC_PATH"
    exit 1
fi

DOC_TYPE_UPPER=$(echo "$DOC_TYPE" | tr '[:lower:]' '[:upper:]')

log_info "Validating ${DOC_TYPE_UPPER}: $DOC_PATH"

# =============================================================================
# Collect files to validate
# =============================================================================
files=()
if [[ -d "$DOC_PATH" ]]; then
    while IFS= read -r -d '' f; do
        files+=("$f")
    done < <(find "$DOC_PATH" -name "*.md" -not -name "*REVIEW*" -not -name "*REPORT*" -print0)
else
    files=("$DOC_PATH")
fi

# =============================================================================
# Validate each file
# =============================================================================
for file in "${files[@]}"; do
    log_info "Checking: $(basename "$file")"

    # Check YAML frontmatter
    check_yaml_frontmatter "$file" "title,doc_id,version,status"

    # Check for element IDs matching the doc type
    check_element_ids "$file" "${DOC_TYPE_UPPER}\.[0-9]+\.[A-Z0-9]+\.[0-9]+"

    # Check for any trace references
    check_trace_references "$file"
done

# =============================================================================
# Output
# =============================================================================
output_validation_summary "$DOC_TYPE" "$DOC_PATH"
