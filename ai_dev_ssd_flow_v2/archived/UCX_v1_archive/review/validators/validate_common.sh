#!/usr/bin/env bash
# =============================================================================
# validate_common.sh — Common validation functions for UCR validators
# =============================================================================
# Shared utilities used by all layer-specific validators.
#
# Usage:
#   source validate_common.sh
#
# =============================================================================

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Counters
VALIDATION_ERRORS=0
VALIDATION_WARNINGS=0
VALIDATION_PASSES=0

# =============================================================================
# Output Functions
# =============================================================================

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ((VALIDATION_ERRORS++))
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    ((VALIDATION_WARNINGS++))
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((VALIDATION_PASSES++))
}

log_info() {
    echo "[INFO] $1"
}

# =============================================================================
# YAML Validation
# =============================================================================

check_yaml_frontmatter() {
    local file="$1"
    local required_fields="${2:-title,doc_id,version,status}"

    if ! head -1 "$file" | grep -q "^---$"; then
        log_error "Missing YAML frontmatter in $(basename "$file")"
        return 1
    fi

    # Extract frontmatter
    local frontmatter
    frontmatter=$(sed -n '/^---$/,/^---$/p' "$file" | head -n -1 | tail -n +2)

    # Check required fields
    IFS=',' read -ra fields <<< "$required_fields"
    for field in "${fields[@]}"; do
        if ! echo "$frontmatter" | grep -q "^${field}:"; then
            log_warning "Missing frontmatter field: $field in $(basename "$file")"
        fi
    done

    log_pass "YAML frontmatter structure valid in $(basename "$file")"
}

# =============================================================================
# Traceability Validation
# =============================================================================

check_trace_references() {
    local file="$1"
    local trace_pattern="${2:-@(brd|prd|ears|bdd|adr|sys|req|ctr|spec|tspec):}"

    local traces
    traces=$(grep -oE "$trace_pattern\s*\S+" "$file" 2>/dev/null || true)

    if [[ -z "$traces" ]]; then
        log_warning "No trace references found in $(basename "$file")"
        return 0
    fi

    local count
    count=$(echo "$traces" | wc -l)
    log_pass "Found $count trace references in $(basename "$file")"
}

# =============================================================================
# Element ID Validation
# =============================================================================

check_element_ids() {
    local file="$1"
    local pattern="$2"

    local ids
    ids=$(grep -oE "$pattern" "$file" 2>/dev/null || true)

    if [[ -z "$ids" ]]; then
        log_warning "No element IDs matching pattern '$pattern' in $(basename "$file")"
        return 0
    fi

    local count
    count=$(echo "$ids" | wc -l)
    log_pass "Found $count element IDs in $(basename "$file")"
}

# =============================================================================
# Section Structure Validation
# =============================================================================

check_required_sections() {
    local file="$1"
    shift
    local sections=("$@")

    local missing=0
    for section in "${sections[@]}"; do
        if ! grep -qi "^#.*${section}" "$file"; then
            log_error "Missing required section: $section in $(basename "$file")"
            ((missing++))
        fi
    done

    if [[ $missing -eq 0 ]]; then
        log_pass "All required sections present in $(basename "$file")"
    fi
}

# =============================================================================
# Summary Output
# =============================================================================

output_validation_summary() {
    local doc_type="$1"
    local doc_path="$2"

    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "  Validation Summary: ${doc_type^^}"
    echo "════════════════════════════════════════════════════════════"
    echo "  Document:  $doc_path"
    echo "  Errors:    $VALIDATION_ERRORS"
    echo "  Warnings:  $VALIDATION_WARNINGS"
    echo "  Passes:    $VALIDATION_PASSES"
    echo "════════════════════════════════════════════════════════════"

    if [[ $VALIDATION_ERRORS -gt 0 ]]; then
        echo "  Status: FAILED"
        return 1
    elif [[ $VALIDATION_WARNINGS -gt 0 ]]; then
        echo "  Status: PASSED WITH WARNINGS"
        return 0
    else
        echo "  Status: PASSED"
        return 0
    fi
}

# =============================================================================
# JSON Output for Integration
# =============================================================================

output_validation_json() {
    local doc_type="$1"
    local doc_path="$2"

    cat <<EOF
{
  "validator": "ucr-${doc_type}-validator",
  "document": "$doc_path",
  "results": {
    "errors": $VALIDATION_ERRORS,
    "warnings": $VALIDATION_WARNINGS,
    "passes": $VALIDATION_PASSES
  },
  "status": "$([[ $VALIDATION_ERRORS -gt 0 ]] && echo "FAILED" || echo "PASSED")"
}
EOF
}
