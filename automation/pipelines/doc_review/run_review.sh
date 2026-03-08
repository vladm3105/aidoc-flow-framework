#!/usr/bin/env bash
# =============================================================================
# run_review.sh — Doc Review Pipeline Review Orchestrator
# =============================================================================
# Purpose: AI Expert Board Automation Script
# Generates a PERSONA_REVIEW_REPORT acting as a formal framework audit gate.
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

# Extract Frontmatter Metadata from target file to determine Document Type / Layer
doc_id=$(grep -m 1 "^doc_id:" "$TARGET_FILE" | awk '{print $2}' | tr -d '\r' || echo "")
version=$(grep -m 1 "^version:" "$TARGET_FILE" | awk '{print $2}' | tr -d '\r' || echo "UNKNOWN")
artifact_type=$(grep -m 1 "^artifact_type:" "$TARGET_FILE" | awk '{print $2}' | tr -d '\r' | tr '[:upper:]' '[:lower:]' || echo "")
current_date=$(date -I)

if [[ -z "$doc_id" || "$doc_id" == "UNKNOWN" ]]; then
    log_warn "Target file lacks 'doc_id' YAML frontmatter. Using filename."
    doc_id="$TARGET_BASENAME"
fi

# Locate project_experts.yaml (Preferring layer-specific configs based on artifact_type)
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "")
EXPERTS_YAML=""

# 1. Target dir layer-specific config
if [[ -n "$artifact_type" && -f "$TARGET_DIR/project_experts.${artifact_type}.yaml" ]]; then
    EXPERTS_YAML="$TARGET_DIR/project_experts.${artifact_type}.yaml"
# 2. Global AI_EXPERTS layer-specific config
elif [[ -n "$artifact_type" && -n "$GIT_ROOT" && -f "$GIT_ROOT/docs/AI_EXPERTS/project_experts.${artifact_type}.yaml" ]]; then
    EXPERTS_YAML="$GIT_ROOT/docs/AI_EXPERTS/project_experts.${artifact_type}.yaml"
# 3. Target dir generic config
elif [[ -f "$TARGET_DIR/project_experts.yaml" ]]; then
    EXPERTS_YAML="$TARGET_DIR/project_experts.yaml"
# 4. Global AI_EXPERTS generic config
elif [[ -n "$GIT_ROOT" && -f "$GIT_ROOT/docs/AI_EXPERTS/project_experts.yaml" ]]; then
    EXPERTS_YAML="$GIT_ROOT/docs/AI_EXPERTS/project_experts.yaml"
# 5. Framework fallback
else
    log_warn "No project_experts.yaml found. Falling back to framework template."
    EXPERTS_YAML="$(dirname "$AUTOMATION_ROOT")/ai_dev_ssd_flow/AI_EXPERTS/project_experts.template.yaml"
fi
require_file "$EXPERTS_YAML"

# Set output path
OUTPUT_FILE="$TARGET_DIR/${doc_id}_PERSONA_REVIEW_REPORT.md"
TEMPLATE_FILE="$(dirname "$AUTOMATION_ROOT")/ai_dev_ssd_flow/AI_EXPERTS/PERSONA_REVIEW-MVP-TEMPLATE.md"

log_info "Target Document: $TARGET_BASENAME (ID: $doc_id, v$version)"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  DOC REVIEW PIPELINE — AI Board Review"
echo "════════════════════════════════════════════════════════════"
echo "  Target:     $TARGET_FILE"
echo "  Document:   $doc_id"
echo "  Agent:      $AI_AGENT"
echo "  Dry run:    ${DRY_RUN:-false}"
echo "════════════════════════════════════════════════════════════"
echo ""

# Internal Workspace for the AI agent shared memory
RUN_DIR="${TARGET_DIR}/.doc_review_memory"
mkdir -p "$RUN_DIR"
# Clear previous run artifacts to prevent staleness on re-runs
rm -f "$RUN_DIR"/prompt_*.txt "$RUN_DIR"/response_*.txt "$RUN_DIR"/shared_context.txt "$RUN_DIR"/final_body.md 2>/dev/null || true
log_info "DEBUG: Workspace memory is $RUN_DIR"

PERSONAS=("architect" "auditor" "tech_lead" "product_owner" "strategist" "qa_lead" "operator" "integration_expert")

# =============================================================================
# Build Shared Document Context (For API Prompt Caching)
# =============================================================================
SHARED_CONTEXT_FILE="$RUN_DIR/shared_context.txt"
echo "=== SHARED DOCUMENT CONTEXT ===" > "$SHARED_CONTEXT_FILE"

# Dynamically locate structural template rules in parent directory
CREATION_RULES=$(find "$(dirname "$TARGET_DIR")" -maxdepth 1 -name "*_CREATION_RULES.md" -o -name "*_TEMPLATE.md" -print -quit 2>/dev/null || true)
if [[ -n "$CREATION_RULES" && -f "$CREATION_RULES" ]]; then
    echo "=== DOCUMENT CREATION RULES / TEMPLATE START ===" >> "$SHARED_CONTEXT_FILE"
    cat "$CREATION_RULES" >> "$SHARED_CONTEXT_FILE"
    echo "=== DOCUMENT CREATION RULES / TEMPLATE END ===" >> "$SHARED_CONTEXT_FILE"
    echo "" >> "$SHARED_CONTEXT_FILE"
fi

cat << EOF >> "$SHARED_CONTEXT_FILE"
=== TARGET DOCUMENT START ===
EOF
# Extract explicitly linked markdown files from the target file
# Using grep -v "/" to ensure we don't accidentally import cross-referenced other BRDs (e.g. ../BRD-02)
LINKED_FILES=$(grep -oP '\]\(\K[^)]+\.md' "$TARGET_FILE" | grep -v "^http" | grep -v "/" | sort -u || true)

if [[ -n "$LINKED_FILES" ]]; then
    # Sectioned Layout
    # Add the index file itself first
    echo "--- FILE: $(basename "$TARGET_FILE") ---" >> "$SHARED_CONTEXT_FILE"
    cat "$TARGET_FILE" >> "$SHARED_CONTEXT_FILE"
    echo "" >> "$SHARED_CONTEXT_FILE"
    
    # Add all linked sub-files
    for linked_file in $LINKED_FILES; do
        local_path="$TARGET_DIR/$linked_file"
        if [[ -f "$local_path" && "$local_path" != "$TARGET_FILE" ]]; then
            echo "--- FILE: $linked_file ---" >> "$SHARED_CONTEXT_FILE"
            cat "$local_path" >> "$SHARED_CONTEXT_FILE"
            echo "" >> "$SHARED_CONTEXT_FILE"
        fi
    done
else
    # Monolithic Layout (no internal sibling links found)
    echo "--- FILE: $(basename "$TARGET_FILE") ---" >> "$SHARED_CONTEXT_FILE"
    cat "$TARGET_FILE" >> "$SHARED_CONTEXT_FILE"
    echo "" >> "$SHARED_CONTEXT_FILE"
fi
echo "=== TARGET DOCUMENT END ===" >> "$SHARED_CONTEXT_FILE"
echo "" >> "$SHARED_CONTEXT_FILE"

log_step "Step 1 / 3 — Phase 2 Blind Audits"

for persona in "${PERSONAS[@]}"; do
    log_info "Summoning $persona..."
    
    # Extract details using an inline Python parser for robust YAML multiline and nested object support
    eval "$(python3 -c "
import yaml, sys, shlex
with open(sys.argv[1], 'r') as f:
    d = yaml.safe_load(f)
p = d.get('personas', {}).get(sys.argv[2], {}) if sys.argv[2] != 'chairperson' else d.get('chairperson', {})
print(f\"P_NAME={shlex.quote(str(p.get('name', '')))}\")
print(f\"P_PROMPT={shlex.quote(str(p.get('prompt', '')))}\")
print(f\"P_SKILL={shlex.quote(str(p.get('skill_file') or ''))}\")
agent = p.get('agent', {})
print(f\"P_CMD={shlex.quote(str(agent.get('cmd') or ''))}\")
print(f\"P_ENGINE={shlex.quote(str(agent.get('engine') or ''))}\")
print(f\"P_MODEL={shlex.quote(str(agent.get('model') or ''))}\")
print(f\"P_TEMP={shlex.quote(str(agent.get('temperature') or ''))}\")
print(f\"P_TOP_K={shlex.quote(str(agent.get('top_k') or ''))}\")
print(f\"P_MAX_TOKENS={shlex.quote(str(agent.get('max_tokens') or ''))}\")
print(f\"P_API_BASE={shlex.quote(str(agent.get('api_base') or ''))}\")
print(f\"P_API_KEY_ENV={shlex.quote(str(agent.get('api_key_env') or ''))}\")
" "$EXPERTS_YAML" "$persona")"

    
    # Build Prompt
    PROMPT_FILE="$RUN_DIR/prompt_$persona.txt"
    RESPONSE_FILE="$RUN_DIR/response_$persona.txt"
    
    # 1. Start with the identical shared context to trigger AI API Prefix Caching (e.g. Claude)
    cp "$SHARED_CONTEXT_FILE" "$PROMPT_FILE"

    # 1a. Inject Domain Knowledge (Skill File) if present
    SKILL_FILE="$P_SKILL"
    if [[ -z "$SKILL_FILE" ]]; then
        if [[ -f "$GIT_ROOT/docs/AI_EXPERTS/skills/${persona}.md" ]]; then
            SKILL_FILE="$GIT_ROOT/docs/AI_EXPERTS/skills/${persona}.md"
        else
            SKILL_FILE="/opt/data/docs_flow_framework/ai_dev_ssd_flow/AI_EXPERTS/skills/${persona}.md"
        fi
    fi
    
    # Resolve relative paths relative to GIT_ROOT if needed
    if [[ "$SKILL_FILE" != /* ]]; then
        SKILL_FILE="$GIT_ROOT/$SKILL_FILE"
    fi

    if [[ -f "$SKILL_FILE" ]]; then
        echo "=== YOUR DOMAIN KNOWLEDGE ===" >> "$PROMPT_FILE"
        cat "$SKILL_FILE" >> "$PROMPT_FILE"
        echo "=== END DOMAIN KNOWLEDGE ===" >> "$PROMPT_FILE"
        echo "" >> "$PROMPT_FILE"
    fi

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
            
            find "$LAYER_DIR" -maxdepth 1 -name "*.md" -type f ! -name "*_PERSONA_REVIEW_REPORT.md" 2>/dev/null | while read -r other_doc; do
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

    # 2. Inject previous experts' findings for shared cross-persona memory
    PREV_FINDINGS=$(find "$RUN_DIR" -maxdepth 1 -name "response_*.txt" -type f 2>/dev/null || true)
    if [[ -n "$PREV_FINDINGS" ]]; then
        cat << EOF >> "$PROMPT_FILE"
=== PREVIOUS EXPERT FINDINGS ===
The following are the findings from other experts who have already reviewed this document.
You may use their insights, agree with them, or fiercely disagree with them in your own report to the Chairperson:
EOF
        for prev in $PREV_FINDINGS; do
            prev_name=$(basename "$prev" | sed 's/response_//;s/\.txt//')
            echo "--- Report from $prev_name ---" >> "$PROMPT_FILE"
            cat "$prev" >> "$PROMPT_FILE"
            echo "" >> "$PROMPT_FILE"
        done
        echo "=== END PREVIOUS EXPERT FINDINGS ===" >> "$PROMPT_FILE"
        echo "" >> "$PROMPT_FILE"
    fi

    # 3. Append Persona specific instructions at the very end
    cat << EOF >> "$PROMPT_FILE"
==============
EXPERT INSTRUCTIONS:
You are $P_NAME.
$P_PROMPT
EOF

    # Prepare ai_exec arguments dynamically based on YAML config
    AI_PARAMS=("$PROMPT_FILE")
    if [[ -n "$P_CMD" ]]; then
        # CLI mode: pass the raw command directly — all flags embedded in the cmd string
        AI_PARAMS+=("--cmd" "$P_CMD")
    else
        # API mode: pass structured parameters
        [[ -n "$P_MODEL" ]]       && AI_PARAMS+=("--model"       "$P_MODEL")
        [[ -n "$P_TEMP" ]]        && AI_PARAMS+=("--temperature" "$P_TEMP")
        [[ -n "$P_TOP_K" ]]       && AI_PARAMS+=("--top-k"       "$P_TOP_K")
        [[ -n "$P_MAX_TOKENS" ]]  && AI_PARAMS+=("--max-tokens"  "$P_MAX_TOKENS")
        [[ -n "$P_API_BASE" ]]    && AI_PARAMS+=("--api-base"    "$P_API_BASE")
        [[ -n "$P_API_KEY_ENV" ]] && AI_PARAMS+=("--api-key-env" "$P_API_KEY_ENV")
    fi

    # Run AI Agent
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        if [[ -n "$P_CMD" ]]; then
            log_dry "Would call: bash -c \"$P_CMD\" (P_MODEL=$P_MODEL P_MAX_TOKENS=$P_MAX_TOKENS P_TEMP=$P_TEMP)"
        else
            log_dry "Would call: AI_AGENT=$P_ENGINE ai_exec.sh ${AI_PARAMS[*]}"
        fi
        echo "Dry run output for $persona: [Mocked response]" > "$RESPONSE_FILE"
    else
        # Export P_MODEL / P_TEMP / P_MAX_TOKENS so they are visible inside bash -c expansion of cmd:
        P_MODEL="$P_MODEL" P_TEMP="$P_TEMP" P_TOP_K="$P_TOP_K" P_MAX_TOKENS="$P_MAX_TOKENS" \
          AI_AGENT="${P_ENGINE:-claude}" bash "$AI_EXEC_SH" "${AI_PARAMS[@]}" > "$RESPONSE_FILE"
        log_ok "$persona completed review."
    fi
done

log_step "Step 2 / 3 — Summarizing via Chairperson"

# Extract Chairperson details using inline Python YAML
eval "$(python3 -c "
import yaml, sys, shlex
with open(sys.argv[1], 'r') as f:
    d = yaml.safe_load(f)
c = d.get('chairperson', {})
print(f\"C_NAME={shlex.quote(str(c.get('name', '')))}\")
print(f\"C_PROMPT={shlex.quote(str(c.get('prompt', '')))}\")
print(f\"C_SKILL={shlex.quote(str(c.get('skill_file') or ''))}\")
agent = c.get('agent', {})
print(f\"C_CMD={shlex.quote(str(agent.get('cmd') or ''))}\")
print(f\"C_ENGINE={shlex.quote(str(agent.get('engine') or ''))}\")
print(f\"C_MODEL={shlex.quote(str(agent.get('model') or ''))}\")
print(f\"C_TEMP={shlex.quote(str(agent.get('temperature') or ''))}\")
print(f\"C_TOP_K={shlex.quote(str(agent.get('top_k') or ''))}\")
print(f\"C_MAX_TOKENS={shlex.quote(str(agent.get('max_tokens') or ''))}\")
print(f\"C_API_BASE={shlex.quote(str(agent.get('api_base') or ''))}\")
print(f\"C_API_KEY_ENV={shlex.quote(str(agent.get('api_key_env') or ''))}\")
" "$EXPERTS_YAML" "chairperson")"

PROMPT_FILE="$RUN_DIR/prompt_chairperson.txt"
RESPONSE_FILE="$RUN_DIR/final_body.md"

cat "$SHARED_CONTEXT_FILE" > "$PROMPT_FILE"

# Inject Chairperson Domain Knowledge (Skill File)
SKILL_FILE="$C_SKILL"
if [[ -z "$SKILL_FILE" ]]; then
    if [[ -f "$GIT_ROOT/docs/AI_EXPERTS/skills/chairperson.md" ]]; then
        SKILL_FILE="$GIT_ROOT/docs/AI_EXPERTS/skills/chairperson.md"
    else
        SKILL_FILE="/opt/data/docs_flow_framework/ai_dev_ssd_flow/AI_EXPERTS/skills/chairperson.md"
    fi
fi

# Resolve relative paths relative to GIT_ROOT if needed
if [[ "$SKILL_FILE" != /* ]]; then
    SKILL_FILE="$GIT_ROOT/$SKILL_FILE"
fi

if [[ -f "$SKILL_FILE" ]]; then
    echo "=== YOUR DOMAIN KNOWLEDGE ===" >> "$PROMPT_FILE"
    cat "$SKILL_FILE" >> "$PROMPT_FILE"
    echo "=== END DOMAIN KNOWLEDGE ===" >> "$PROMPT_FILE"
    echo "" >> "$PROMPT_FILE"
fi

cat << EOF >> "$PROMPT_FILE"
$C_PROMPT

Read the following 8 conflicting expert reports regarding document $doc_id.

=== EXPERT REPORTS ===
$(for p in "${PERSONAS[@]}"; do echo "--- Report from $p ---"; cat "$RUN_DIR/response_$p.txt"; echo ""; done)
=== END EXPERT REPORTS ===

=== TEMPLATE FORMAT TO FOLLOW ===
$(cat "$TEMPLATE_FILE")
=== END TEMPLATE FORMAT ===

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
    if [[ -n "$C_CMD" ]]; then
        log_dry "Would call: bash -c \"$C_CMD\" < $PROMPT_FILE"
    else
        log_dry "Would call: AI_AGENT=$C_ENGINE ai_exec.sh $PROMPT_FILE"
    fi
    echo "# Expert Board Audit Report: $doc_id" > "$RESPONSE_FILE"
    echo "Dry run output for Chairperson: [Mocked synthesis]" >> "$RESPONSE_FILE"
else
    log_info "Summoning chairperson..."
    
    C_PARAMS=("$PROMPT_FILE")
    if [[ -n "$C_CMD" ]]; then
        C_PARAMS+=("--cmd" "$C_CMD")
    else
        [[ -n "$C_MODEL" ]]       && C_PARAMS+=("--model"       "$C_MODEL")
        [[ -n "$C_TEMP" ]]        && C_PARAMS+=("--temperature" "$C_TEMP")
        [[ -n "$C_TOP_K" ]]       && C_PARAMS+=("--top-k"       "$C_TOP_K")
        [[ -n "$C_MAX_TOKENS" ]]  && C_PARAMS+=("--max-tokens"  "$C_MAX_TOKENS")
        [[ -n "$C_API_BASE" ]]    && C_PARAMS+=("--api-base"    "$C_API_BASE")
        [[ -n "$C_API_KEY_ENV" ]] && C_PARAMS+=("--api-key-env" "$C_API_KEY_ENV")
    fi

    # Export C_ vars so they are visible for bash -c expansion in cmd:
    P_MODEL="$C_MODEL" P_TEMP="$C_TEMP" P_TOP_K="$C_TOP_K" P_MAX_TOKENS="$C_MAX_TOKENS" \
      AI_AGENT="${C_ENGINE:-claude}" bash "$AI_EXEC_SH" "${C_PARAMS[@]}" > "$RESPONSE_FILE"
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
    log_ok "EXPERTS Audit Report generated at:"
    echo "  $OUTPUT_FILE"
    echo ""
    log_info "Next steps: To apply remediation or create tasks, run:"
    echo "  bash automation/pipelines/doc_review/run_remediate.sh $OUTPUT_FILE --target-doc $TARGET_FILE"
fi

echo "════════════════════════════════════════════════════════════"
echo "  DOC REVIEW PIPELINE REVIEW — Complete"
echo "════════════════════════════════════════════════════════════"
