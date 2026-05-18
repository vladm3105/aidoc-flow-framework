#!/usr/bin/env bash
# =============================================================================
# run_ucx_autopilot.sh — UCX Autopilot (Unified Context Orchestration)
# =============================================================================
# Full autopilot that orchestrates UCC → UCR → UCRem cycles with:
# - Smart document detection (auto-select create vs review)
# - Drift monitoring (.drift_cache.json)
# - Full autopilot cycle (max 3 iterations)
# - IPLAN input support
# - Multi-document batch processing
# - PRD-Ready scoring and exit conditions
#
# Usage:
#   ./run_ucx_autopilot.sh <doc_type> <target> [options]
#
# Examples:
#   # Generate from reference docs
#   ./run_ucx_autopilot.sh brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/
#
#   # Review existing document
#   ./run_ucx_autopilot.sh brd docs/01_BRD/BRD-01
#
#   # Generate from IPLAN
#   ./run_ucx_autopilot.sh brd docs/01_BRD/BRD-02 --from-iplan IPLAN-001
#
#   # Batch process multiple documents
#   ./run_ucx_autopilot.sh brd docs/01_BRD/BRD-01 docs/01_BRD/BRD-02 --batch
#
# Options:
#   --from-ref <dir>       - Generate from reference documents
#   --from-upstream <file> - Generate from upstream artifact
#   --from-iplan <file>    - Generate from implementation plan
#   --batch                - Process multiple targets
#   --max-iterations <n>   - Max review/fix cycles (default: 3)
#   --min-score <n>        - Minimum PRD-Ready score (default: 90)
#   --skip-drift           - Skip drift monitoring
#   --dry-run              - Show what would be done without executing
#
# Environment:
#   UCX_MODEL        - Claude model to use (default: opus)
#   UCX_MAX_ITER     - Max iterations (default: 3)
#   UCX_MIN_SCORE    - Min PRD-Ready score (default: 90)
#
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Phase scripts
UCC_SCRIPT="$SCRIPT_DIR/creation/run_ucc.sh"
UCR_SCRIPT="$SCRIPT_DIR/review/run_ucr.sh"
UCREM_SCRIPT="$SCRIPT_DIR/remediation/run_ucrem.sh"

# =============================================================================
# Configuration
# =============================================================================
UCX_MODEL="${UCX_MODEL:-opus}"
UCX_MAX_ITER="${UCX_MAX_ITER:-3}"
UCX_MIN_SCORE="${UCX_MIN_SCORE:-90}"
SKIP_DRIFT="${UCX_SKIP_DRIFT:-false}"
DRY_RUN="false"
BATCH_MODE="false"

# =============================================================================
# Parse arguments
# =============================================================================
DOC_TYPE="${1:-}"
shift || true

TARGETS=()
FROM_REF=""
FROM_UPSTREAM=""
FROM_IPLAN=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --from-ref)
            FROM_REF="$2"
            shift 2
            ;;
        --from-upstream)
            FROM_UPSTREAM="$2"
            shift 2
            ;;
        --from-iplan)
            FROM_IPLAN="$2"
            shift 2
            ;;
        --batch)
            BATCH_MODE="true"
            shift
            ;;
        --max-iterations)
            UCX_MAX_ITER="$2"
            shift 2
            ;;
        --min-score)
            UCX_MIN_SCORE="$2"
            shift 2
            ;;
        --skip-drift)
            SKIP_DRIFT="true"
            shift
            ;;
        --dry-run)
            DRY_RUN="true"
            shift
            ;;
        -*)
            echo "Unknown option: $1"
            exit 1
            ;;
        *)
            TARGETS+=("$1")
            shift
            ;;
    esac
done

# =============================================================================
# Usage
# =============================================================================
if [[ -z "$DOC_TYPE" || ${#TARGETS[@]} -eq 0 ]]; then
    echo "Usage: ./run_ucx_autopilot.sh <doc_type> <target> [options]"
    echo ""
    echo "Document types: brd, prd, ears, bdd, adr, sys, req, ctr, spec, tspec"
    echo ""
    echo "Options:"
    echo "  --from-ref <dir>       Generate from reference documents"
    echo "  --from-upstream <file> Generate from upstream artifact"
    echo "  --from-iplan <file>    Generate from implementation plan"
    echo "  --batch                Process multiple targets"
    echo "  --max-iterations <n>   Max review/fix cycles (default: 3)"
    echo "  --min-score <n>        Minimum PRD-Ready score (default: 90)"
    echo "  --skip-drift           Skip drift monitoring"
    echo "  --dry-run              Show actions without executing"
    echo ""
    echo "Examples:"
    echo "  ./run_ucx_autopilot.sh brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/"
    echo "  ./run_ucx_autopilot.sh prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01"
    echo ""
    exit 1
fi

# Normalize doc type
DOC_TYPE=$(echo "$DOC_TYPE" | tr '[:upper:]' '[:lower:]')

# =============================================================================
# Utility Functions
# =============================================================================

log_phase() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║  $1"
    echo "╚════════════════════════════════════════════════════════════╝"
}

log_step() {
    echo "  → $1"
}

log_success() {
    echo "  ✓ $1"
}

log_warning() {
    echo "  ⚠ $1"
}

log_error() {
    echo "  ✗ $1" >&2
}

# =============================================================================
# Drift Cache Functions
# =============================================================================

compute_hash() {
    local file="$1"
    if [[ -f "$file" ]]; then
        sha256sum "$file" | cut -d' ' -f1
    else
        echo ""
    fi
}

get_drift_cache_path() {
    local doc_path="$1"
    if [[ -d "$doc_path" ]]; then
        echo "$doc_path/.drift_cache.json"
    else
        echo "$(dirname "$doc_path")/.drift_cache.json"
    fi
}

create_drift_cache() {
    local doc_path="$1"
    local upstream_path="${2:-}"
    local cache_file=$(get_drift_cache_path "$doc_path")
    local doc_id
    local upstream_mode="none"
    local upstream_docs="{}"

    # Extract doc ID from path
    doc_id=$(basename "$doc_path" | grep -oP '(BRD|PRD|EARS|BDD|ADR|SYS|REQ|CTR|SPEC|TSPEC)-[0-9]+' || echo "UNKNOWN")

    # Compute upstream hashes if provided
    if [[ -n "$upstream_path" ]]; then
        upstream_mode="ref"
        if [[ -d "$upstream_path" ]]; then
            local docs=""
            for f in "$upstream_path"/*.md "$upstream_path"/*.txt; do
                if [[ -f "$f" ]]; then
                    local fname=$(basename "$f")
                    local hash=$(compute_hash "$f")
                    if [[ -n "$docs" ]]; then docs+=","; fi
                    docs+="\"$fname\":{\"hash\":\"sha256:$hash\",\"last_checked\":\"$(date -Iseconds)\"}"
                fi
            done
            upstream_docs="{$docs}"
        elif [[ -f "$upstream_path" ]]; then
            local fname=$(basename "$upstream_path")
            local hash=$(compute_hash "$upstream_path")
            upstream_docs="{\"$fname\":{\"hash\":\"sha256:$hash\",\"last_checked\":\"$(date -Iseconds)\"}}"
        fi
    fi

    # Create drift cache JSON
    cat > "$cache_file" << EOF
{
  "schema_version": "1.1",
  "document_id": "$doc_id",
  "document_version": "1.0",
  "upstream_mode": "$upstream_mode",
  "drift_detection_skipped": $([ "$SKIP_DRIFT" == "true" ] && echo "true" || echo "false"),
  "last_reviewed": "$(date -Iseconds)",
  "reviewer_version": "UCX-1.0",
  "upstream_documents": $upstream_docs,
  "review_history": [
    {
      "date": "$(date -Iseconds)",
      "score": 0,
      "drift_detected": false,
      "status": "INITIAL"
    }
  ]
}
EOF
    log_success "Created drift cache: $cache_file"
}

update_drift_cache() {
    local cache_file="$1"
    local score="$2"
    local status="$3"
    local drift_detected="${4:-false}"

    if [[ ! -f "$cache_file" ]]; then
        log_warning "Drift cache not found: $cache_file"
        return
    fi

    # Update last_reviewed and add to review_history
    local tmp_file=$(mktemp)
    local new_entry="{\"date\":\"$(date -Iseconds)\",\"score\":$score,\"drift_detected\":$drift_detected,\"status\":\"$status\"}"

    # Use jq if available, otherwise use sed
    if command -v jq &> /dev/null; then
        jq ".last_reviewed = \"$(date -Iseconds)\" | .review_history += [$new_entry]" "$cache_file" > "$tmp_file"
        mv "$tmp_file" "$cache_file"
    else
        # Fallback: append to review_history array manually
        sed -i "s/\"last_reviewed\": \"[^\"]*\"/\"last_reviewed\": \"$(date -Iseconds)\"/" "$cache_file"
        log_warning "jq not installed - drift cache update is partial"
    fi

    log_step "Updated drift cache: score=$score, status=$status"
}

check_drift() {
    local cache_file="$1"
    local upstream_path="${2:-}"

    if [[ ! -f "$cache_file" || -z "$upstream_path" ]]; then
        echo "false"
        return
    fi

    # Check if upstream files have changed
    local drift_detected="false"

    if [[ -d "$upstream_path" ]]; then
        for f in "$upstream_path"/*.md "$upstream_path"/*.txt; do
            if [[ -f "$f" ]]; then
                local fname=$(basename "$f")
                local current_hash=$(compute_hash "$f")
                local cached_hash=$(grep -oP "\"$fname\":\{\"hash\":\"sha256:\K[0-9a-f]{64}" "$cache_file" 2>/dev/null || echo "")

                if [[ -n "$cached_hash" && "$current_hash" != "$cached_hash" ]]; then
                    drift_detected="true"
                    log_warning "Drift detected in: $fname"
                fi
            fi
        done
    fi

    echo "$drift_detected"
}

# =============================================================================
# IPLAN Resolution
# =============================================================================

resolve_iplan() {
    local iplan_input="$1"

    # Check if it's a direct path
    if [[ -f "$iplan_input" ]]; then
        echo "$iplan_input"
        return
    fi

    # Check if it matches IPLAN-NNN pattern
    if [[ "$iplan_input" =~ ^IPLAN-[0-9]+$ ]]; then
        # Search in work_plans/
        local found=$(find work_plans/ -name "${iplan_input}*.md" 2>/dev/null | head -1)
        if [[ -n "$found" ]]; then
            echo "$found"
            return
        fi

        # Search in governance/plans/
        found=$(find governance/plans/ -name "${iplan_input}*.md" 2>/dev/null | head -1)
        if [[ -n "$found" ]]; then
            echo "$found"
            return
        fi
    fi

    # Not found
    echo ""
}

# =============================================================================
# Score Extraction
# =============================================================================

extract_score() {
    local report_file="$1"
    local score=0

    if [[ -f "$report_file" ]]; then
        # Try to extract PRD-Ready score from review report
        score=$(grep -oP '(?:PRD-Ready|Quality|Score)[:\s]+(\d+)' "$report_file" | grep -oP '\d+' | tail -1 || echo "0")

        # Fallback: count P0/P1/P2 findings
        if [[ "$score" == "0" || -z "$score" ]]; then
            local p0=$(grep -c "P0-" "$report_file" 2>/dev/null || echo "0")
            local p1=$(grep -c "P1-" "$report_file" 2>/dev/null || echo "0")
            local p2=$(grep -c "P2-" "$report_file" 2>/dev/null || echo "0")

            # Simple scoring: 100 - (P0*20 + P1*10 + P2*5)
            score=$((100 - p0*20 - p1*10 - p2*5))
            if [[ $score -lt 0 ]]; then score=0; fi
        fi
    fi

    echo "$score"
}

has_manual_required() {
    local report_file="$1"

    if [[ -f "$report_file" ]]; then
        if grep -q "confidence: manual-required" "$report_file" 2>/dev/null; then
            echo "true"
        else
            echo "false"
        fi
    else
        echo "false"
    fi
}

# =============================================================================
# Smart Document Detection
# =============================================================================

detect_action() {
    local target="$1"

    # Check if target exists
    if [[ -e "$target" ]]; then
        # Document exists: Review mode
        if [[ -d "$target" ]]; then
            # Directory: check for main document files
            if ls "$target"/*.md &> /dev/null; then
                echo "review"
            else
                echo "generate"
            fi
        else
            # File exists
            echo "review"
        fi
    else
        # Document doesn't exist: Generate mode
        echo "generate"
    fi
}

# =============================================================================
# Process Single Document
# =============================================================================

process_document() {
    local target="$1"
    local action
    local iteration=0
    local score=0
    local status="PENDING"

    log_phase "Processing: $target"

    # Smart document detection
    action=$(detect_action "$target")
    log_step "Detected action: $action"

    # Get drift cache path
    local cache_file=$(get_drift_cache_path "$target")

    # ==========================================================================
    # PHASE 1: Generate (if needed)
    # ==========================================================================
    if [[ "$action" == "generate" ]]; then
        log_phase "Phase 1: Document Generation (UCC)"

        if [[ "$DRY_RUN" == "true" ]]; then
            log_step "[DRY-RUN] Would run: $UCC_SCRIPT $DOC_TYPE $target"
        else
            # Build UCC command
            local ucc_cmd="$UCC_SCRIPT $DOC_TYPE $target"

            if [[ -n "$FROM_REF" ]]; then
                ucc_cmd+=" --from-ref $FROM_REF"
            fi

            if [[ -n "$FROM_UPSTREAM" ]]; then
                ucc_cmd+=" --from-upstream $FROM_UPSTREAM"
            fi

            if [[ -n "$FROM_IPLAN" ]]; then
                local resolved=$(resolve_iplan "$FROM_IPLAN")
                if [[ -z "$resolved" ]]; then
                    log_error "IPLAN not found: $FROM_IPLAN"
                    return 1
                fi
                ucc_cmd+=" --from-upstream $resolved"
            fi

            log_step "Running: $ucc_cmd"
            bash -c "$ucc_cmd"

            # Create initial drift cache
            if [[ "$SKIP_DRIFT" != "true" ]]; then
                local upstream_ref="${FROM_REF:-$FROM_UPSTREAM}"
                create_drift_cache "$target" "$upstream_ref"
            fi
        fi
    fi

    # ==========================================================================
    # PHASE 2-5: Review → Fix → Re-Review Loop
    # ==========================================================================
    while [[ $iteration -lt $UCX_MAX_ITER ]]; do
        iteration=$((iteration + 1))
        log_phase "Phase 2-5: Review/Fix Cycle (Iteration $iteration/$UCX_MAX_ITER)"

        # Check for drift
        if [[ "$SKIP_DRIFT" != "true" && -f "$cache_file" ]]; then
            local drift=$(check_drift "$cache_file" "$FROM_REF")
            if [[ "$drift" == "true" ]]; then
                log_warning "Upstream drift detected - document may need regeneration"
            fi
        fi

        # Review report path
        local review_dir
        if [[ -d "$target" ]]; then
            review_dir="$target"
        else
            review_dir=$(dirname "$target")
        fi
        local review_report="$review_dir/${DOC_TYPE^^}_UCR_REVIEW.md"
        local fix_report="$review_dir/${DOC_TYPE^^}_UCRem_REPORT.md"

        # ======================================================================
        # UCR: Review
        # ======================================================================
        log_step "Running UCR review..."

        if [[ "$DRY_RUN" == "true" ]]; then
            log_step "[DRY-RUN] Would run: $UCR_SCRIPT $DOC_TYPE $target"
        else
            bash "$UCR_SCRIPT" "$DOC_TYPE" "$target" "$review_report"
        fi

        # Extract score
        if [[ "$DRY_RUN" != "true" ]]; then
            score=$(extract_score "$review_report")
            log_step "Review score: $score (target: $UCX_MIN_SCORE)"

            # Update drift cache
            if [[ "$SKIP_DRIFT" != "true" ]]; then
                local drift_status=$(check_drift "$cache_file" "$FROM_REF")
                update_drift_cache "$cache_file" "$score" "REVIEWED" "$drift_status"
            fi

            # Check if we've reached target score
            if [[ $score -ge $UCX_MIN_SCORE ]]; then
                log_success "Target score achieved: $score >= $UCX_MIN_SCORE"
                status="PASS"
                break
            fi
        fi

        # ======================================================================
        # UCRem: Fix
        # ======================================================================
        log_step "Running UCRem remediation..."

        if [[ "$DRY_RUN" == "true" ]]; then
            log_step "[DRY-RUN] Would run: $UCREM_SCRIPT $review_report $target"
        else
            bash "$UCREM_SCRIPT" "$review_report" "$target" "$fix_report"

            # Check for manual-required fixes
            local has_manual=$(has_manual_required "$fix_report")
            if [[ "$has_manual" == "true" ]]; then
                log_warning "Manual fixes required - cannot auto-complete"
                status="NEEDS_MANUAL"
            fi
        fi
    done

    # ==========================================================================
    # Final Status
    # ==========================================================================
    log_phase "Autopilot Complete: $target"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_step "[DRY-RUN] Would complete with unknown status"
    else
        log_step "Final Score: $score"
        log_step "Iterations: $iteration"
        log_step "Status: $status"

        if [[ $score -ge $UCX_MIN_SCORE ]]; then
            log_success "Document ready for downstream processing"
        else
            log_warning "Document needs additional attention"
        fi

        # Final drift cache update
        if [[ "$SKIP_DRIFT" != "true" && -f "$cache_file" ]]; then
            update_drift_cache "$cache_file" "$score" "$status" "false"
        fi
    fi

    return 0
}

# =============================================================================
# Main Execution
# =============================================================================

log_phase "UCX Autopilot"
echo "  Document Type:   ${DOC_TYPE^^}"
echo "  Targets:         ${#TARGETS[@]}"
echo "  Max Iterations:  $UCX_MAX_ITER"
echo "  Min Score:       $UCX_MIN_SCORE"
echo "  Drift Tracking:  $([[ "$SKIP_DRIFT" == "true" ]] && echo "disabled" || echo "enabled")"
echo "  Dry Run:         $DRY_RUN"

if [[ -n "$FROM_REF" ]]; then
    echo "  Reference:       $FROM_REF"
fi
if [[ -n "$FROM_UPSTREAM" ]]; then
    echo "  Upstream:        $FROM_UPSTREAM"
fi
if [[ -n "$FROM_IPLAN" ]]; then
    echo "  IPLAN:           $FROM_IPLAN"
fi

# Process targets
if [[ "$BATCH_MODE" == "true" ]]; then
    # Batch mode: process in chunks of 3
    log_step "Batch mode: processing ${#TARGETS[@]} targets in chunks of 3"

    for ((i=0; i<${#TARGETS[@]}; i+=3)); do
        chunk=("${TARGETS[@]:i:3}")
        log_step "Processing chunk: ${chunk[*]}"

        for target in "${chunk[@]}"; do
            process_document "$target"
        done
    done
else
    # Single mode: process first target
    process_document "${TARGETS[0]}"
fi

log_phase "UCX Autopilot Complete"
