#!/bin/bash

# doc_flow Quality Gates Validation Script
# Ensures 16-layer SDD workflow progression with TRACEABILITY.md alignment
#
# TRACEABILITY RULES (REQUIRED vs OPTIONAL):
# +-----------------------+-----------------------+------------------------+
# | Document Type         | Upstream Traceability | Downstream Traceability|
# +-----------------------+-----------------------+------------------------+
# | BRD                   | OPTIONAL (to BRDs)    | OPTIONAL               |
# | All Other Documents   | REQUIRED              | OPTIONAL               |
# +-----------------------+-----------------------+------------------------+
#
# Key Rules:
# - Upstream REQUIRED (except BRD): Document MUST reference upstream sources
# - Downstream OPTIONAL: Only link to documents that already exist
# - No-TBD Rule: NEVER use placeholder IDs (TBD, XXX, NNN)

set -e

validate_quality_gates() {
    local file="$1"

    echo "🔍 Validating quality gates for: $file"

    # Determine validation based on file path and type
    case "$file" in
        docs/BRD/*.md)
            validate_ears_ready "$file"
            ;;
        docs/PRD/*.md)
            validate_bdd_ready "$file"
            ;;
        docs/EARS/*.md)
            validate_adr_ready "$file"
            ;;
        docs/BDD/*.feature)
            validate_sys_ready "$file"
            ;;
        docs/ADR/*.md)
            validate_req_ready "$file"
            ;;
        docs/SYS/*.md)
            validate_spec_ready "$file"
            ;;
        docs/REQ/*.md)
            validate_impl_ready "$file"
            ;;
        docs/SPEC/*.yaml)
            validate_tasks_ready "$file"
            ;;
        docs/TASKS/*.md)
            validate_iplan_ready "$file"
            ;;
        docs/CTR/*.md)
            validate_ctr_files "$file"
            ;;
        *)
            echo "ℹ️ No quality gate for: $file"
            return 0
            ;;
    esac

    # Validate cumulative tagging for all document types
    validate_cumulative_tags "$file"

    echo "✅ Quality gates passed for $file"
}

validate_ears_ready() {
    validate_ready_score "$1" "EARS-Ready Score" 90
}

validate_bdd_ready() {
    validate_ready_score "$1" "BDD-Ready Score" 90
}

validate_adr_ready() {
    validate_ready_score "$1" "ADR-Ready Score" 90
}

validate_sys_ready() {
    validate_ready_score "$1" "SYS-Ready Score" 90
}

validate_req_ready() {
    validate_ready_score "$1" "REQ-Ready Score" 90
}

validate_spec_ready() {
    validate_ready_score "$1" "SPEC-Ready Score" 90
}

validate_impl_ready() {
    validate_ready_score "$1" "IMPL-Ready Score" 90
}

validate_tasks_ready() {
    # SPEC uses YAML metadata format
    validate_yaml_meta_score "$1" "task_ready_score" 90
}

validate_iplan_ready() {
    validate_ready_score "$1" "IPLAN-Ready Score" 90
}

validate_ctr_files() {
    local file="$1"
    local basename=$(basename "$file" .md)
    local yaml_file="${file%.md}.yaml"

    if [[ ! -f "$yaml_file" ]]; then
        echo "❌ Missing CTR YAML file: $yaml_file"
        return 1
    fi

    echo "✅ CTR dual-file requirement satisfied"
    return 0
}

validate_ready_score() {
    local file="$1"
    local score_field="$2"
    local min_threshold="$3"

    # Extract ready score using grep and sed
    local score_line=$(grep "| $score_field" "$file" 2>/dev/null || echo "")

    if [[ -z "$score_line" ]]; then
        echo "❌ Missing $score_field in $file"
        echo "💡 Add to Document Control: | $score_field | ✅ NN% (Target: ≥${min_threshold}%) |"
        return 1
    fi

    local score=$(echo "$score_line" | sed 's/.*✅ \([0-9]*\)%.*/\1/' | tr -d ' ')

    if ! [[ "$score" =~ ^[0-9]+$ ]] || [ "$score" -lt "$min_threshold" ]; then
        echo "❌ $score_field too low: ${score}% (minimum: ${min_threshold}%)"
        echo "💡 Improve document completeness to reach ${min_threshold}%+ score"
        return 1
    fi

    echo "✅ $score_field: ${score}% ≥ ${min_threshold}%"
    return 0
}

validate_yaml_meta_score() {
    local file="$1"
    local meta_field="$2"
    local min_threshold="$3"

    local score_line=$(grep "task_ready_score:" "$file" 2>/dev/null || echo "")

    if [[ -z "$score_line" ]]; then
        echo "❌ Missing $meta_field in $file"
        echo "💡 Add to metadata section:"
        echo "  task_ready_score: \"✅ NN% (Target: ≥${min_threshold}%)\""
        return 1
    fi

    local score=$(echo "$score_line" | sed 's/.*✅ \([0-9]*\)%.*/\1/' | tr -d ' ')

    if ! [[ "$score" =~ ^[0-9]+$ ]] || [ "$score" -lt "$min_threshold" ]; then
        echo "❌ $meta_field too low: ${score}% (minimum: ${min_threshold}%)"
        echo "💡 Improve YAML spec completeness to reach ${min_threshold}%+ score"
        return 1
    fi

    echo "✅ $meta_field: ${score}% ≥ ${min_threshold}%"
    return 0
}

validate_cumulative_tags() {
    local file="$1"

    # Determine required tags based on file path (aligned with TRACEABILITY.md §4.3)
    case "$file" in
        docs/BRD/*.md) required_tags=() ;; # Root level, no upstream tags
        docs/PRD/*.md) required_tags=("brd") ;;
        docs/EARS/*.md) required_tags=("brd" "prd") ;;
        docs/BDD/*.feature) required_tags=("brd" "prd" "ears") ;;
        docs/ADR/*.md) required_tags=("brd" "prd" "ears" "bdd") ;;
        docs/SYS/*.md) required_tags=("brd" "prd" "ears" "bdd" "adr") ;;
        docs/REQ/*.md) required_tags=("brd" "prd" "ears" "bdd" "adr" "sys") ;;
        docs/IMPL/*.md) required_tags=("brd" "prd" "ears" "bdd" "adr" "sys" "req") ;;
        docs/CTR/*.md) required_tags=("brd" "prd" "ears" "bdd" "adr" "sys" "req") ;;
        docs/SPEC/*.yaml) required_tags=("brd" "prd" "ears" "bdd" "adr" "sys" "req") ;;
        docs/TASKS/*.md) required_tags=("brd" "prd" "ears" "bdd" "adr" "sys" "req" "spec") ;;
        docs/IPLAN/*.md) required_tags=("brd" "prd" "ears" "bdd" "adr" "sys" "req" "spec" "tasks") ;;
    esac

    validate_tags_presence "$file" "${required_tags[@]}"
}

validate_tags_presence() {
    local file="$1"
    shift
    local required_tags=("$@")

    for tag in "${required_tags[@]}"; do
        if ! grep -q "^@$tag:" "$file"; then
            echo "❌ Missing cumulative tag: @$tag (required for layer progression)"
            echo "💡 Add to Traceability section:"
            echo "  @$tag: DOCUMENT-ID:REQ-ID"
            return 1
        fi
    done

    if [ ${#required_tags[@]} -gt 0 ]; then
        echo "✅ Cumulative tagging valid (${#required_tags[@]} upstream tags present)"
    fi

    return 0
}

show_usage() {
    echo "Usage: $0 <file_path>"
    echo ""
    echo "Validates quality gates for doc_flow SDD artifacts:"
    echo "  docs/BRD/*.md        → EARS-ready score ≥90%"
    echo "  docs/PRD/*.md        → BDD-ready score ≥90%"
    echo "  docs/EARS/*.md       → ADR-ready score ≥90%"
    echo "  docs/BDD/*.feature   → SYS-ready score ≥90%"
    echo "  docs/ADR/*.md        → REQ-ready score ≥90%"
    echo "  docs/SYS/*.md        → SPEC-ready score ≥90%"
    echo "  docs/REQ/*.md        → IMPL-ready score ≥90%"
    echo "  docs/SPEC/*.yaml     → TASKS-ready score ≥90%"
    echo "  docs/TASKS/*.md      → IPLAN-ready score ≥90%"
    echo ""
    echo "Also validates cumulative tagging alignment with TRACEABILITY.md"
    echo ""
    echo "Exit codes:"
    echo "  0 = Quality gates passed"
    echo "  1 = Quality gates failed (blocking progression)"
}

# Main execution
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

validate_quality_gates "$1"
