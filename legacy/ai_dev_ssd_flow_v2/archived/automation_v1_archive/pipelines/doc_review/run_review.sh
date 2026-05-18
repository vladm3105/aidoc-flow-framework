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

# Locate review.yaml (Preferring layer-specific configs based on artifact_type)
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "")
EXPERTS_YAML=""

# 1. Target dir layer-specific config
if [[ -n "$artifact_type" && -f "$TARGET_DIR/review.${artifact_type}.yaml" ]]; then
    EXPERTS_YAML="$TARGET_DIR/review.${artifact_type}.yaml"
# 2. Global AI_EXPERTS layer-specific config
elif [[ -n "$artifact_type" && -n "$GIT_ROOT" && -f "$GIT_ROOT/docs/AI_EXPERTS/review.${artifact_type}.yaml" ]]; then
    EXPERTS_YAML="$GIT_ROOT/docs/AI_EXPERTS/review.${artifact_type}.yaml"
# 3. Target dir generic config
elif [[ -f "$TARGET_DIR/review.yaml" ]]; then
    EXPERTS_YAML="$TARGET_DIR/review.yaml"
# 4. Global AI_EXPERTS generic config
elif [[ -n "$GIT_ROOT" && -f "$GIT_ROOT/docs/AI_EXPERTS/review.yaml" ]]; then
    EXPERTS_YAML="$GIT_ROOT/docs/AI_EXPERTS/review.yaml"
# 5. Framework fallback
else
    log_warn "No review.yaml found. Falling back to framework template."
    EXPERTS_YAML="$(dirname "$AUTOMATION_ROOT")/ucx_flow_v3/AI_EXPERTS/review.template.yaml"
fi
require_file "$EXPERTS_YAML"
log_info "Using experts config: $EXPERTS_YAML"

# Set output path
OUTPUT_FILE="$TARGET_DIR/${doc_id}_PERSONA_REVIEW_REPORT.md"
TEMPLATE_FILE="$(dirname "$AUTOMATION_ROOT")/ucx_flow_v3/AI_EXPERTS/PERSONA_REVIEW-MVP-TEMPLATE.md"

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

# Dynamically extract personas from YAML file
PERSONAS=()
while IFS= read -r persona; do
    PERSONAS+=("$persona")
done < <(python3 -c "
import yaml
with open('$EXPERTS_YAML', 'r') as f:
    d = yaml.safe_load(f)
for p in d.get('personas', {}).keys():
    print(p)
")
log_info "Loaded ${#PERSONAS[@]} personas from YAML: ${PERSONAS[*]}"

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

    
    # Build Prompt (persona-specific only - shared context passed separately for caching)
    PROMPT_FILE="$RUN_DIR/prompt_$persona.txt"
    RESPONSE_FILE="$RUN_DIR/response_$persona.txt"

    # 1. Create empty persona prompt file (shared context passed via --system-prompt-file for API caching)
    > "$PROMPT_FILE"

    # 1a. Inject Domain Knowledge (Skill File) if present
    SKILL_FILE="$P_SKILL"
    if [[ -z "$SKILL_FILE" ]]; then
        if [[ -f "$GIT_ROOT/docs/AI_EXPERTS/skills/${persona}.md" ]]; then
            SKILL_FILE="$GIT_ROOT/docs/AI_EXPERTS/skills/${persona}.md"
        else
            SKILL_FILE="/opt/data/docs_flow_framework/ucx_flow_v3/AI_EXPERTS/skills/${persona}.md"
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
    # Add shared context as system prompt for API caching (reduces tokens by ~80%)
    AI_PARAMS+=("--system-prompt-file" "$SHARED_CONTEXT_FILE")
    # Add explicit engine flag if specified in YAML
    [[ -n "$P_ENGINE" ]] && AI_PARAMS+=("--engine" "$P_ENGINE")
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
            log_dry "Would call: ai_exec.sh ${AI_PARAMS[*]}"
        fi
        echo "Dry run output for $persona: [Mocked response]" > "$RESPONSE_FILE"
    else
        # Export P_MODEL / P_TEMP / P_MAX_TOKENS so they are visible inside bash -c expansion of cmd:
        P_MODEL="$P_MODEL" P_TEMP="$P_TEMP" P_TOP_K="$P_TOP_K" P_MAX_TOKENS="$P_MAX_TOKENS" \
          bash "$AI_EXEC_SH" "${AI_PARAMS[@]}" > "$RESPONSE_FILE"
        log_ok "$persona completed review."
    fi
done

log_step "Step 2 / 5 — Summarizing via Chairperson"

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

# Create empty prompt file (shared context passed via --system-prompt-file for API caching)
> "$PROMPT_FILE"

# Inject Chairperson Domain Knowledge (Skill File)
SKILL_FILE="$C_SKILL"
if [[ -z "$SKILL_FILE" ]]; then
    if [[ -f "$GIT_ROOT/docs/AI_EXPERTS/skills/chairperson.md" ]]; then
        SKILL_FILE="$GIT_ROOT/docs/AI_EXPERTS/skills/chairperson.md"
    else
        SKILL_FILE="/opt/data/docs_flow_framework/ucx_flow_v3/AI_EXPERTS/skills/chairperson.md"
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
> **Board Configuration**: review.yaml

## 1. Executive Summary
*   **Consensus Recommendation**: (Proceed / Remediation Required / Fundamental Redesign)
*   *Chairperson's Synthesis*: [Your synthesized paragraph]

[... Fill out Sections 2 through 6 based on the template requirements]
EOF

if [[ "${DRY_RUN:-false}" == "true" ]]; then
    if [[ -n "$C_CMD" ]]; then
        log_dry "Would call: bash -c \"$C_CMD\" < $PROMPT_FILE"
    else
        log_dry "Would call: ai_exec.sh --engine $C_ENGINE $PROMPT_FILE"
    fi
    echo "# Expert Board Audit Report: $doc_id" > "$RESPONSE_FILE"
    echo "Dry run output for Chairperson: [Mocked synthesis]" >> "$RESPONSE_FILE"
else
    log_info "Summoning chairperson..."

    C_PARAMS=("$PROMPT_FILE")
    # Add shared context as system prompt for API caching
    C_PARAMS+=("--system-prompt-file" "$SHARED_CONTEXT_FILE")
    # Add explicit engine flag if specified in YAML
    [[ -n "$C_ENGINE" ]] && C_PARAMS+=("--engine" "$C_ENGINE")
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
      bash "$AI_EXEC_SH" "${C_PARAMS[@]}" > "$RESPONSE_FILE"
    log_ok "Chairperson synthesis complete."
fi

log_step "Step 3 / 5 — Judge validation of synthesis"

# Extract Judge details using inline Python YAML
eval "$(python3 -c "
import yaml, sys, shlex
with open(sys.argv[1], 'r') as f:
    d = yaml.safe_load(f)
j = d.get('judge', {})
print(f\"J_NAME={shlex.quote(str(j.get('name', '')))}\")
print(f\"J_PROMPT={shlex.quote(str(j.get('prompt', '')))}\")
agent = j.get('agent', {})
print(f\"J_CMD={shlex.quote(str(agent.get('cmd') or ''))}\")
print(f\"J_ENGINE={shlex.quote(str(agent.get('engine') or ''))}\")
print(f\"J_MODEL={shlex.quote(str(agent.get('model') or ''))}\")
print(f\"J_TEMP={shlex.quote(str(agent.get('temperature') or ''))}\")
print(f\"J_TOP_K={shlex.quote(str(agent.get('top_k') or ''))}\")
print(f\"J_MAX_TOKENS={shlex.quote(str(agent.get('max_tokens') or ''))}\")
print(f\"J_API_BASE={shlex.quote(str(agent.get('api_base') or ''))}\")
print(f\"J_API_KEY_ENV={shlex.quote(str(agent.get('api_key_env') or ''))}\")
" "$EXPERTS_YAML")"

JUDGE_PROMPT_FILE="$RUN_DIR/prompt_judge.txt"
JUDGE_RESPONSE_FILE="$RUN_DIR/response_judge.txt"

# Only run Judge if configured in YAML
if [[ -n "$J_NAME" ]]; then
    cat << EOF > "$JUDGE_PROMPT_FILE"
$J_PROMPT

=== RAW EXPERT REPORTS ===
$(for p in "${PERSONAS[@]}"; do echo "--- Report from $p ---"; cat "$RUN_DIR/response_$p.txt" 2>/dev/null || echo "[No response]"; echo ""; done)
=== END RAW EXPERT REPORTS ===

=== CHAIRPERSON'S SYNTHESIS ===
$(cat "$RESPONSE_FILE")
=== END CHAIRPERSON'S SYNTHESIS ===

Validate the synthesis against the raw expert reports and provide your verdict.
EOF

    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        log_dry "Would call Judge to validate synthesis"
        echo "Verdict: PASS (dry run)" > "$JUDGE_RESPONSE_FILE"
    else
        log_info "Summoning judge..."

        J_PARAMS=("$JUDGE_PROMPT_FILE")
        # Add shared context so Judge can verify claims against the actual document
        J_PARAMS+=("--system-prompt-file" "$SHARED_CONTEXT_FILE")
        # Add explicit engine flag if specified in YAML
        [[ -n "$J_ENGINE" ]] && J_PARAMS+=("--engine" "$J_ENGINE")
        if [[ -n "$J_CMD" ]]; then
            J_PARAMS+=("--cmd" "$J_CMD")
        else
            [[ -n "$J_MODEL" ]]       && J_PARAMS+=("--model"       "$J_MODEL")
            [[ -n "$J_TEMP" ]]        && J_PARAMS+=("--temperature" "$J_TEMP")
            [[ -n "$J_TOP_K" ]]       && J_PARAMS+=("--top-k"       "$J_TOP_K")
            [[ -n "$J_MAX_TOKENS" ]]  && J_PARAMS+=("--max-tokens"  "$J_MAX_TOKENS")
            [[ -n "$J_API_BASE" ]]    && J_PARAMS+=("--api-base"    "$J_API_BASE")
            [[ -n "$J_API_KEY_ENV" ]] && J_PARAMS+=("--api-key-env" "$J_API_KEY_ENV")
        fi

        P_MODEL="$J_MODEL" P_TEMP="$J_TEMP" P_TOP_K="$J_TOP_K" P_MAX_TOKENS="$J_MAX_TOKENS" \
          bash "$AI_EXEC_SH" "${J_PARAMS[@]}" > "$JUDGE_RESPONSE_FILE"
        log_ok "Judge validation complete."
    fi

    # Check if revision is required
    if grep -qi "REVISION_REQUIRED" "$JUDGE_RESPONSE_FILE"; then
        log_step "Step 4 / 5 — Editor applying fixes from Judge"

        # Extract Editor details using inline Python YAML
        eval "$(python3 -c "
import yaml, sys, shlex
with open(sys.argv[1], 'r') as f:
    d = yaml.safe_load(f)
e = d.get('editor', {})
print(f\"E_NAME={shlex.quote(str(e.get('name', '')))}\")
print(f\"E_PROMPT={shlex.quote(str(e.get('prompt', '')))}\")
agent = e.get('agent', {})
print(f\"E_CMD={shlex.quote(str(agent.get('cmd') or ''))}\")
print(f\"E_ENGINE={shlex.quote(str(agent.get('engine') or ''))}\")
print(f\"E_MODEL={shlex.quote(str(agent.get('model') or ''))}\")
print(f\"E_TEMP={shlex.quote(str(agent.get('temperature') or ''))}\")
print(f\"E_TOP_K={shlex.quote(str(agent.get('top_k') or ''))}\")
print(f\"E_MAX_TOKENS={shlex.quote(str(agent.get('max_tokens') or ''))}\")
print(f\"E_API_BASE={shlex.quote(str(agent.get('api_base') or ''))}\")
print(f\"E_API_KEY_ENV={shlex.quote(str(agent.get('api_key_env') or ''))}\")
" "$EXPERTS_YAML")"

        EDITOR_PROMPT_FILE="$RUN_DIR/prompt_editor.txt"
        EDITOR_RESPONSE_FILE="$RUN_DIR/response_editor.txt"

        cat << EOF > "$EDITOR_PROMPT_FILE"
$E_PROMPT

=== ORIGINAL CHAIRPERSON SYNTHESIS ===
$(cat "$RESPONSE_FILE")
=== END ORIGINAL SYNTHESIS ===

=== JUDGE'S CRITIQUE ===
$(cat "$JUDGE_RESPONSE_FILE")
=== END JUDGE'S CRITIQUE ===

=== RAW EXPERT REPORTS (for reference) ===
$(for p in "${PERSONAS[@]}"; do echo "--- Report from $p ---"; cat "$RUN_DIR/response_$p.txt" 2>/dev/null || echo "[No response]"; echo ""; done)
=== END RAW EXPERT REPORTS ===

Apply all fixes and output the COMPLETE corrected PERSONA_REVIEW_REPORT.
EOF

        if [[ "${DRY_RUN:-false}" == "true" ]]; then
            log_dry "Would call Editor to apply fixes"
            cp "$RESPONSE_FILE" "$EDITOR_RESPONSE_FILE"
        else
            log_info "Summoning editor..."

            E_PARAMS=("$EDITOR_PROMPT_FILE")
            # Add explicit engine flag if specified in YAML
            [[ -n "$E_ENGINE" ]] && E_PARAMS+=("--engine" "$E_ENGINE")
            if [[ -n "$E_CMD" ]]; then
                E_PARAMS+=("--cmd" "$E_CMD")
            else
                [[ -n "$E_MODEL" ]]       && E_PARAMS+=("--model"       "$E_MODEL")
                [[ -n "$E_TEMP" ]]        && E_PARAMS+=("--temperature" "$E_TEMP")
                [[ -n "$E_TOP_K" ]]       && E_PARAMS+=("--top-k"       "$E_TOP_K")
                [[ -n "$E_MAX_TOKENS" ]]  && E_PARAMS+=("--max-tokens"  "$E_MAX_TOKENS")
                [[ -n "$E_API_BASE" ]]    && E_PARAMS+=("--api-base"    "$E_API_BASE")
                [[ -n "$E_API_KEY_ENV" ]] && E_PARAMS+=("--api-key-env" "$E_API_KEY_ENV")
            fi

            P_MODEL="$E_MODEL" P_TEMP="$E_TEMP" P_TOP_K="$E_TOP_K" P_MAX_TOKENS="$E_MAX_TOKENS" \
              bash "$AI_EXEC_SH" "${E_PARAMS[@]}" > "$EDITOR_RESPONSE_FILE"
            log_ok "Editor fixes applied."
        fi

        # Use editor's output as final body
        RESPONSE_FILE="$EDITOR_RESPONSE_FILE"
    else
        log_ok "Judge verdict: PASS — no revision needed."
    fi
else
    log_warn "No judge configured in YAML — skipping validation step."
fi

log_step "Step 5 / 5 — Assembling final audit report"

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
