#!/usr/bin/env bash
# =============================================================================
# run_review.sh — Council Pipeline Review Orchestrator
# =============================================================================
# Purpose: AI Expert Board Automation Script
# Generates a COUNCIL_AUDIT_REPORT acting as a formal framework audit gate.
# Uses the agent-agnostic core framework (`ai_exec.sh`).
#
# Usage:
#   run_review.sh <target_document.md> [options]
#
# Options:
#   --dry-run             Preview actions, don't execute AI logic
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CORE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")/core"

source "$CORE_DIR/config.sh"
source "$CORE_DIR/utils.sh"

TARGET_FILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) export DRY_RUN=true; shift ;;
    -*)
      log_error "Unknown option: $1"
      echo "Usage: run_review.sh <TARGET.md> [--dry-run]" >&2
      exit 2 ;;
    *)
      TARGET_FILE="$1"
      shift ;;
  esac
done

[[ -z "$TARGET_FILE" ]] && die "Usage: run_review.sh <target_document.md> [--dry-run]"
require_file "$TARGET_FILE"

TARGET_DIR=$(dirname "$TARGET_FILE")
TARGET_FILENAME=$(basename "$TARGET_FILE")
TARGET_BASENAME="${TARGET_FILENAME%.*}" # e.g., BRD-01

# Locate project_experts.yaml
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "")
EXPERTS_YAML=""
if [ -f "$TARGET_DIR/project_experts.yaml" ]; then
    EXPERTS_YAML="$TARGET_DIR/project_experts.yaml"
elif [ -n "$GIT_ROOT" ] && [ -f "$GIT_ROOT/docs/AI_EXPERTS/project_experts.yaml" ]; then
    EXPERTS_YAML="$GIT_ROOT/docs/AI_EXPERTS/project_experts.yaml"
else
    log_warn "No project_experts.yaml found. Falling back to framework template."
    # The SSD flow is 3 levels up from core
    EXPERTS_YAML="$(dirname "$(dirname "$AUTOMATION_ROOT")")/ai_dev_ssd_flow/AI_EXPERTS/project_experts.template.yaml"
fi
require_file "$EXPERTS_YAML"

log_info "Using Expert Profile: $EXPERTS_YAML"

# Extract Frontmatter Metadata from target file
doc_id=$(grep -m 1 "^doc_id:" "$TARGET_FILE" | awk '{print $2}' || echo "")
version=$(grep -m 1 "^version:" "$TARGET_FILE" | awk '{print $2}' || echo "UNKNOWN")
current_date=$(date -I)

if [[ -z "$doc_id" || "$doc_id" == "UNKNOWN" ]]; then
    log_warn "Target file lacks 'doc_id' YAML frontmatter. Using filename."
    doc_id="$TARGET_BASENAME"
fi

# Set output path
OUTPUT_FILE="$TARGET_DIR/${doc_id}_COUNCIL_AUDIT_REPORT.md"
TEMPLATE_FILE="$(dirname "$(dirname "$AUTOMATION_ROOT")")/ai_dev_ssd_flow/AI_EXPERTS/COUNCIL-MVP-TEMPLATE.md"

log_info "Target Document: $TARGET_BASENAME (ID: $doc_id, v$version)"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  COUNCIL PIPELINE — AI Board Review"
echo "════════════════════════════════════════════════════════════"
echo "  Target:     $TARGET_FILE"
echo "  Document:   $doc_id"
echo "  Agent:      $AI_AGENT"
echo "  Dry run:    ${DRY_RUN:-false}"
echo "════════════════════════════════════════════════════════════"
echo ""

# Internal Temp Files for the 7 persona responses
RUN_DIR=$(mktemp -d "/tmp/council_review_XXXXXX")
trap "rm -rf $RUN_DIR" EXIT

PERSONAS=("architect" "auditor" "domain_specialist" "strategist" "qa_lead" "operator" "integration_expert")

log_step "Step 1 / 3 — Phase 2 Blind Audits"

for persona in "${PERSONAS[@]}"; do
    log_info "Summoning $persona..."
    
    # Extract details using grep (assuming standard yaml format)
    P_NAME=$(grep -A 5 "$persona:" "$EXPERTS_YAML" | grep "name:" | cut -d'"' -f2 | head -1)
    P_FOCUS=$(grep -A 5 "$persona:" "$EXPERTS_YAML" | grep "focus:" | cut -d'"' -f2 | head -1)
    P_BIAS=$(grep -A 5 "$persona:" "$EXPERTS_YAML" | grep "anti_bias_directive:" | cut -d'"' -f2 | head -1)
    
    # Build Prompt
    PROMPT_FILE="$RUN_DIR/prompt_$persona.txt"
    RESPONSE_FILE="$RUN_DIR/response_$persona.txt"
    
    cat << EOF > "$PROMPT_FILE"
You are $P_NAME. Your operational focus is: $P_FOCUS.
CRITICAL CONSTRAINT: $P_BIAS

Review the following technical document strictly from your persona's perspective. Do not sugarcoat. Do not be polite. Find the flaws.
Output your findings in EXACTLY three sections:
- 1. Major Risks
- 2. Unhandled Edge Cases
- 3. Alternative Approach

EOF

    # If the persona is integration_expert, append the integration matrix for context
    if [ "$persona" = "integration_expert" ]; then
        MATRIX_FILE=$(find "$GIT_ROOT/docs" -name "*INTEGRATION_MATRIX*.md" -print -quit 2>/dev/null || true)
        
        if [ -n "$MATRIX_FILE" ] && [ -f "$MATRIX_FILE" ]; then
            echo "=== SYSTEM INTEGRATION MATRIX ===" >> "$PROMPT_FILE"
            cat "$MATRIX_FILE" >> "$PROMPT_FILE"
            echo "=== END SYSTEM INTEGRATION MATRIX ===" >> "$PROMPT_FILE"
            echo "" >> "$PROMPT_FILE"
        else
            LAYER_DIR=$(dirname "$TARGET_FILE")
            log_warn "Integration matrix not found. Falling back to Layer Context scanning in $LAYER_DIR."
            echo "=== LAYER CONTEXT (Fallback) ===" >> "$PROMPT_FILE"
            echo "The formal integration matrix is missing. Here is the metadata of other documents currently in the same layer to help you identify overlap or dependencies:" >> "$PROMPT_FILE"
            
            find "$LAYER_DIR" -maxdepth 1 -name "*.md" -type f ! -name "*_COUNCIL_AUDIT_REPORT.md" 2>/dev/null | while read -r other_doc; do
                if [ "$other_doc" != "$TARGET_FILE" ]; then
                    other_title=$(grep -m 1 "^# " "$other_doc" || echo "# Unknown Title")
                    other_id=$(grep -m 1 "^doc_id:" "$other_doc" | awk '{print $2}' || echo "UNKNOWN_ID")
                    if [ "$other_id" != "UNKNOWN_ID" ]; then
                        echo "- Document: $other_id | Title: ${other_title### }" >> "$PROMPT_FILE"
                    fi
                fi
            done
            echo "=== END LAYER CONTEXT ===" >> "$PROMPT_FILE"
            echo "" >> "$PROMPT_FILE"
        fi
    fi

    # Dynamically locate structural template rules in parent directory
    CREATION_RULES=$(find "$(dirname "$TARGET_DIR")" -maxdepth 1 -name "*_CREATION_RULES.md" -o -name "*_TEMPLATE.md" -print -quit 2>/dev/null || true)
    if [[ -n "$CREATION_RULES" && -f "$CREATION_RULES" ]]; then
        echo "=== DOCUMENT CREATION RULES / TEMPLATE START ===" >> "$PROMPT_FILE"
        cat "$CREATION_RULES" >> "$PROMPT_FILE"
        echo "=== DOCUMENT CREATION RULES / TEMPLATE END ===" >> "$PROMPT_FILE"
        echo "" >> "$PROMPT_FILE"
    fi

    cat << EOF >> "$PROMPT_FILE"
=== TARGET DOCUMENT START ===
EOF
    # Append all markdown files in the target directory (except audit reports)
    # This handles both monolithic (1 file) and section-based (N files) structures natively
    find "$TARGET_DIR" -maxdepth 1 -type f -name "*.md" ! -name "*_COUNCIL_AUDIT_REPORT*.md" | sort | while read -r doc_file; do
        echo "--- FILE: $(basename "$doc_file") ---" >> "$PROMPT_FILE"
        cat "$doc_file" >> "$PROMPT_FILE"
        echo "" >> "$PROMPT_FILE"
    done
    echo "=== TARGET DOCUMENT END ===" >> "$PROMPT_FILE"

    # Run AI Agent
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        log_dry "Would call: ai_exec.sh $PROMPT_FILE"
        echo "Dry run output for $persona: [Mocked response]" > "$RESPONSE_FILE"
    else
        bash "$AI_EXEC_SH" "$PROMPT_FILE" > "$RESPONSE_FILE"
        log_ok "$persona completed review."
    fi
done

log_step "Step 2 / 3 — Summarizing via Chairperson"

C_NAME=$(grep -A 5 "chairperson:" "$EXPERTS_YAML" | grep "name:" | cut -d'"' -f2 | head -1)
C_BIAS=$(grep -A 5 "chairperson:" "$EXPERTS_YAML" | grep "anti_bias_directive:" | cut -d'"' -f2 | head -1)

PROMPT_FILE="$RUN_DIR/prompt_chairperson.txt"
RESPONSE_FILE="$RUN_DIR/final_body.md"

cat << EOF > "$PROMPT_FILE"
You are $C_NAME. 
$C_BIAS

Read the following 7 conflicting expert reports regarding document $doc_id.
Adjudicate and synthesize them into the final markdown structure provided in the template. Do not include the YAML block, just the markdown body starting from the H1 header.

=== EXPERT REPORTS ===
$(for p in "${PERSONAS[@]}"; do echo "--- Report from $p ---"; cat "$RUN_DIR/response_$p.txt"; echo ""; done)
=== END EXPERT REPORTS ===

=== REQUIRED OUTPUT STRUCTURE (Follow exactly) ===
# Expert Board Audit Report: $doc_id

> **Target Document**: $doc_id (Version $version)
> **Audit Date**: $current_date
> **Board Configuration**: project_experts.yaml

## 1. Executive Summary
*   **Consensus Recommendation**: (Proceed / Remediation Required / Fundamental Redesign)
*   *Chairperson's Synthesis*: [Your synthesized paragraph]

[... Fill out Sections 2 through 6 based on the template requirements]
EOF

if [[ "${DRY_RUN:-false}" == "true" ]]; then
    log_dry "Would call: ai_exec.sh $PROMPT_FILE"
    echo "# Expert Board Audit Report: $doc_id" > "$RESPONSE_FILE"
    echo "Dry run output for Chairperson: [Mocked synthesis]" >> "$RESPONSE_FILE"
else
    log_info "Summoning chairperson..."
    bash "$AI_EXEC_SH" "$PROMPT_FILE" > "$RESPONSE_FILE"
    log_ok "Chairperson synthesis complete."
fi

log_step "Step 3 / 3 — Assembling final audit report"

if [[ "${DRY_RUN:-false}" == "true" ]]; then
    log_dry "Would assemble $OUTPUT_FILE from template and chairperson response."
else
    # 1. Generate YAML Frontmatter from template
    cat "$TEMPLATE_FILE" | awk '/^---/{if(++c==2) {print; exit}} {print}' | \
        sed "s/{NN}/${doc_id//[!0-9]/}/g" | \
        sed "s/{TARGET_DOC_ID}/$doc_id/g" | \
        sed "s/{TARGET_DOC_VERSION}/$version/g" | \
        sed "s/{PASS_OR_FAIL}/PENDING_REVIEW/g" | \
        sed "s/{CURRENT_DATE}/$current_date/g" > "$OUTPUT_FILE"

    # 2. Append Chairperson Body
    cat "$RESPONSE_FILE" >> "$OUTPUT_FILE"

    echo ""
    log_ok "COUNCIL Audit Report generated at:"
    echo "  $OUTPUT_FILE"
    echo ""
    log_info "Next steps: To apply remediation or create tasks, run:"
    echo "  bash automation/pipelines/council/run_remediate.sh $OUTPUT_FILE --target-doc $TARGET_FILE"
fi

echo "════════════════════════════════════════════════════════════"
echo "  COUNCIL PIPELINE REVIEW — Complete"
echo "════════════════════════════════════════════════════════════"
