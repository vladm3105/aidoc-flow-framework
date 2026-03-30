#!/usr/bin/env bash
# =============================================================================
# run_generate.sh — Doc Review Pipeline Generation Orchestrator
# =============================================================================
# Purpose: Orchestrates multi-agent AI Expert teams to generate documents
# matching the SDD framework rules.
#
# Process:
# 1. Individual Experts: Draft specific sections based on their domain context.
# 2. Chairperson (Assembler): Assembles the sections into a V1 Draft.
# 3. LLM Judge: Critiques the V1 Draft against template/validation standards.
# 4. Chairperson (Editor): Applies the critique to output the Final Document.
#
# Usage:
#   run_generate.sh --type <doc_type> --outdir <output_dir> [options]
#
# Options:
#   --type         Document type (e.g., brd, prd, adr, bdd, ears)
#   --outdir       Directory to save the generated document
#   --upstream     Upstream document to load into context (e.g., parent BRD path for PRD)
#   --topic        Text file containing initial requirements or topic description
#   --dry-run      Preview actions, don't execute AI logic
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CORE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")/core"

source "$CORE_DIR/config.sh"
source "$CORE_DIR/utils.sh"

DOC_TYPE=""
OUT_DIR=""
UPSTREAM_FILE=""
TOPIC_FILE=""
DRY_RUN="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --type) DOC_TYPE="$2"; shift 2 ;;
    --outdir) OUT_DIR="$2"; shift 2 ;;
    --upstream) UPSTREAM_FILE="$2"; shift 2 ;;
    --topic) TOPIC_FILE="$2"; shift 2 ;;
    --dry-run) DRY_RUN="true"; shift ;;
    -*)
      log_error "Unknown option: $1"
      echo "Usage: run_generate.sh --type <type> --outdir <dir> [--upstream <doc.md>] [--topic <topic.md>] [--dry-run]" >&2
      exit 2 ;;
    *)
      log_error "Unexpected argument: $1"
      exit 2 ;;
  esac
done

if [[ -z "$DOC_TYPE" || -z "$OUT_DIR" ]]; then
    die "Usage: run_generate.sh --type <type> --outdir <dir> [--upstream <doc.md>] [--topic <topic.md>] [--dry-run]"
fi

# Normalize DOC_TYPE
DOC_TYPE=$(echo "$DOC_TYPE" | tr '[:upper:]' '[:lower:]')

# Ensure OUT_DIR exists
mkdir -p "$OUT_DIR"

GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "")

# Locate generate.<type>.yaml
EXPERTS_YAML=""
if [[ -n "$GIT_ROOT" && -f "$GIT_ROOT/docs/AI_EXPERTS/generate.${DOC_TYPE}.yaml" ]]; then
    EXPERTS_YAML="$GIT_ROOT/docs/AI_EXPERTS/generate.${DOC_TYPE}.yaml"
elif [[ -f "/opt/data/docs_flow_framework/ai_dev_ssd_flow/AI_EXPERTS/generate.${DOC_TYPE}.yaml" ]]; then
    EXPERTS_YAML="/opt/data/docs_flow_framework/ai_dev_ssd_flow/AI_EXPERTS/generate.${DOC_TYPE}.yaml"
else
    # Fallback to generic generate template if it exists
    if [[ -n "$GIT_ROOT" && -f "$GIT_ROOT/docs/AI_EXPERTS/generate.template.yaml" ]]; then
        EXPERTS_YAML="$GIT_ROOT/docs/AI_EXPERTS/generate.template.yaml"
    elif [[ -f "/opt/data/docs_flow_framework/ai_dev_ssd_flow/AI_EXPERTS/generate.template.yaml" ]]; then
        EXPERTS_YAML="/opt/data/docs_flow_framework/ai_dev_ssd_flow/AI_EXPERTS/generate.template.yaml"
    else
        die "Could not find a generation board (generate.${DOC_TYPE}.yaml or generate.template.yaml)"
    fi
    log_warn "Exact type board not found. Falling back to generate.template.yaml"
fi
require_file "$EXPERTS_YAML"

RUN_DIR="${OUT_DIR}/.generation_memory"
mkdir -p "$RUN_DIR"
rm -f "$RUN_DIR"/prompt_*.txt "$RUN_DIR"/response_*.txt "$RUN_DIR"/shared_context.txt "$RUN_DIR"/*.md 2>/dev/null || true

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  DOC REVIEW PIPELINE — Document Generation ($DOC_TYPE)"
echo "════════════════════════════════════════════════════════════"
echo "  Output Dir: $OUT_DIR"
echo "  Upstream:   ${UPSTREAM_FILE:-None}"
echo "  Topic Context: ${TOPIC_FILE:-None}"
echo "  Board config: $EXPERTS_YAML"
echo "  Dry run:    $DRY_RUN"
echo "════════════════════════════════════════════════════════════"
echo ""

log_step "Step 1/5 — Building Shared Context"

SHARED_CONTEXT_FILE="$RUN_DIR/shared_context.txt"
echo "=== SHARED FRAMEWORK STANDARDS & CONTEXT ===" > "$SHARED_CONTEXT_FILE"

# Inject core framework standards
FRAMEWORK_DOCS=(
    "ai_dev_ssd_flow/ID_NAMING_STANDARDS.md"
    "ai_dev_ssd_flow/VALIDATION_STANDARDS.md"
    "ai_dev_ssd_flow/LAYER_REGISTRY.yaml"
    "ai_dev_ssd_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md"
)

for fdoc in "${FRAMEWORK_DOCS[@]}"; do
    path="/opt/data/docs_flow_framework/$fdoc"
    if [[ -f "$path" ]]; then
        echo "--- FRAMEWORK DOCUMENT: $(basename "$path") ---" >> "$SHARED_CONTEXT_FILE"
        cat "$path" >> "$SHARED_CONTEXT_FILE"
        echo "" >> "$SHARED_CONTEXT_FILE"
    fi
done

# Inject target doc-type SKILL rules
DOC_SKILL_FILE=""
if [[ -n "$GIT_ROOT" && -f "$GIT_ROOT/.claude/skills/doc-${DOC_TYPE}/SKILL.md" ]]; then
    DOC_SKILL_FILE="$GIT_ROOT/.claude/skills/doc-${DOC_TYPE}/SKILL.md"
elif [[ -f "/opt/data/docs_flow_framework/.claude/skills/doc-${DOC_TYPE}/SKILL.md" ]]; then
    DOC_SKILL_FILE="/opt/data/docs_flow_framework/.claude/skills/doc-${DOC_TYPE}/SKILL.md"
fi

if [[ -n "$DOC_SKILL_FILE" && -f "$DOC_SKILL_FILE" ]]; then
    echo "--- GENERATION RULES FOR ${DOC_TYPE} (Crucial) ---" >> "$SHARED_CONTEXT_FILE"
    cat "$DOC_SKILL_FILE" >> "$SHARED_CONTEXT_FILE"
    echo "" >> "$SHARED_CONTEXT_FILE"
else
    log_warn "doc-${DOC_TYPE} SKILL file not found! Output may not match strict schema requirements."
fi

# Inject upstream document if provided
if [[ -n "$UPSTREAM_FILE" ]]; then
    require_file "$UPSTREAM_FILE"
    echo "--- UPSTREAM DOCUMENT REFERENCE ---" >> "$SHARED_CONTEXT_FILE"
    cat "$UPSTREAM_FILE" >> "$SHARED_CONTEXT_FILE"
    
    # Check for linked files (like in run_review)
    UP_DIR=$(dirname "$UPSTREAM_FILE")
    LINKED_FILES=$(grep -oP '\]\(\K[^)]+\.md' "$UPSTREAM_FILE" | grep -v "^http" | grep -v "/" | sort -u || true)
    for linked_file in $LINKED_FILES; do
        local_path="$UP_DIR/$linked_file"
        if [[ -f "$local_path" && "$local_path" != "$UPSTREAM_FILE" ]]; then
            echo "--- UPSTREAM LINKED FILE: $linked_file ---" >> "$SHARED_CONTEXT_FILE"
            cat "$local_path" >> "$SHARED_CONTEXT_FILE"
            echo "" >> "$SHARED_CONTEXT_FILE"
        fi
    done
    echo "" >> "$SHARED_CONTEXT_FILE"
fi

# Inject topic file if provided
if [[ -n "$TOPIC_FILE" ]]; then
    require_file "$TOPIC_FILE"
    echo "--- TOPIC / INITIAL REQUIREMENTS ---" >> "$SHARED_CONTEXT_FILE"
    cat "$TOPIC_FILE" >> "$SHARED_CONTEXT_FILE"
    echo "" >> "$SHARED_CONTEXT_FILE"
fi

echo "=== END SHARED CONTEXT ===" >> "$SHARED_CONTEXT_FILE"

# Get persona list directly from YAML, excluding internal roles
PERSONAS=$(python3 -c "
import yaml, sys
try:
    with open(sys.argv[1], 'r') as f:
        d = yaml.safe_load(f)
    print(' '.join(k for k in d.get('personas', {}).keys() if k not in ['chairperson', 'judge']))
except Exception:
    print('')
" "$EXPERTS_YAML")

log_step "Step 2/5 — Run AI Expert Drafters"

for persona in $PERSONAS; do
    log_info "Summoning drafter: $persona..."
    
    eval "$(python3 -c "
import yaml, sys, shlex
with open(sys.argv[1], 'r') as f: d = yaml.safe_load(f)
p = d.get('personas', {}).get(sys.argv[2], {})
print(f\"P_NAME={shlex.quote(str(p.get('name', '')))}\")
print(f\"P_PROMPT={shlex.quote(str(p.get('prompt', '')))}\")
print(f\"P_SKILL={shlex.quote(str(p.get('skill_file') or ''))}\")
agent = p.get('agent', {})
print(f\"P_CMD={shlex.quote(str(agent.get('cmd') or ''))}\")
print(f\"P_ENGINE={shlex.quote(str(agent.get('engine') or ''))}\")
print(f\"P_MODEL={shlex.quote(str(agent.get('model') or ''))}\")
print(f\"P_TEMP={shlex.quote(str(agent.get('temperature') or ''))}\")
print(f\"P_MAX_TOKENS={shlex.quote(str(agent.get('max_tokens') or ''))}\")
" "$EXPERTS_YAML" "$persona")"

    PROMPT_FILE="$RUN_DIR/prompt_$persona.txt"
    RESPONSE_FILE="$RUN_DIR/response_$persona.txt"
    
    cp "$SHARED_CONTEXT_FILE" "$PROMPT_FILE"

    # Inject Domain Knowledge
    SKILL_FILE="$P_SKILL"
    if [[ -z "$SKILL_FILE" ]]; then
        if [[ -n "$GIT_ROOT" && -f "$GIT_ROOT/docs/AI_EXPERTS/skills/${persona}.md" ]]; then
            SKILL_FILE="$GIT_ROOT/docs/AI_EXPERTS/skills/${persona}.md"
        else
            SKILL_FILE="/opt/data/docs_flow_framework/ai_dev_ssd_flow/AI_EXPERTS/skills/${persona}.md"
        fi
    fi
    if [[ "$SKILL_FILE" != /* && -n "$GIT_ROOT" ]]; then SKILL_FILE="$GIT_ROOT/$SKILL_FILE"; fi

    if [[ -f "$SKILL_FILE" ]]; then
        echo "=== YOUR DOMAIN KNOWLEDGE ===" >> "$PROMPT_FILE"
        cat "$SKILL_FILE" >> "$PROMPT_FILE"
        echo "=== END DOMAIN KNOWLEDGE ===" >> "$PROMPT_FILE"
        echo "" >> "$PROMPT_FILE"
    fi

    # Inject previous drafters' output
    PREV_FINDINGS=$(find "$RUN_DIR" -maxdepth 1 -name "response_*.txt" -type f 2>/dev/null || true)
    if [[ -n "$PREV_FINDINGS" ]]; then
        echo "=== PREVIOUS EXPERT SECTIONS ===" >> "$PROMPT_FILE"
        for prev in $PREV_FINDINGS; do
            echo "--- Section by $(basename "$prev" | sed 's/response_//;s/\.txt//') ---" >> "$PROMPT_FILE"
            cat "$prev" >> "$PROMPT_FILE"
            echo "" >> "$PROMPT_FILE"
        done
        echo "=== END PREVIOUS EXPERT SECTIONS ===" >> "$PROMPT_FILE"
    fi

    # Add their specific prompt
    cat << EOF >> "$PROMPT_FILE"
==============
EXPERT INSTRUCTIONS:
You are $P_NAME.
$P_PROMPT
EOF

    AI_PARAMS=("$PROMPT_FILE")
    [[ -n "$P_CMD" ]] && AI_PARAMS+=("--cmd" "$P_CMD") || {
        [[ -n "$P_MODEL" ]]       && AI_PARAMS+=("--model"       "$P_MODEL")
        [[ -n "$P_TEMP" ]]        && AI_PARAMS+=("--temperature" "$P_TEMP")
        [[ -n "$P_MAX_TOKENS" ]]  && AI_PARAMS+=("--max-tokens"  "$P_MAX_TOKENS")
    }

    if [[ "$DRY_RUN" == "true" ]]; then
        echo "Dry run output for $persona: [Draft section]" > "$RESPONSE_FILE"
        log_dry "Skipping $persona generation."
    else
        P_MODEL="$P_MODEL" P_TEMP="$P_TEMP" P_MAX_TOKENS="$P_MAX_TOKENS" \
        AI_AGENT="${P_ENGINE:-claude}" bash "$AI_EXEC_SH" "${AI_PARAMS[@]}" > "$RESPONSE_FILE"
        log_ok "$persona generated their section."
    fi
done

log_step "Step 3/5 — Chairperson (Assembler) builds V1 Draft"

eval "$(python3 -c "
import yaml, sys, shlex
with open(sys.argv[1], 'r') as f: d = yaml.safe_load(f)
c = d.get('chairperson', {})
print(f\"C_NAME={shlex.quote(str(c.get('name', '')))}\")
print(f\"C_PROMPT={shlex.quote(str(c.get('prompt', '')))}\")
agent = c.get('agent', {})
print(f\"C_CMD={shlex.quote(str(agent.get('cmd') or ''))}\")
print(f\"C_ENGINE={shlex.quote(str(agent.get('engine') or ''))}\")
print(f\"C_MODEL={shlex.quote(str(agent.get('model') or ''))}\")
print(f\"C_TEMP={shlex.quote(str(agent.get('temperature') or ''))}\")
print(f\"C_MAX_TOKENS={shlex.quote(str(agent.get('max_tokens') or ''))}\")
" "$EXPERTS_YAML")"

PROMPT_FILE="$RUN_DIR/prompt_chairperson_v1.txt"
V1_FILE="$RUN_DIR/draft_v1.md"

cp "$SHARED_CONTEXT_FILE" "$PROMPT_FILE"

cat << EOF >> "$PROMPT_FILE"
$C_PROMPT

You must now assemble the V1 Document Draft from the expert outputs below. 
You MUST adhere strictly to the exact generation framework rules provided in the SHARED CONTEXT for this document type.
Generate the complete markdown document content.

=== EXPERT DRAFTS ===
$(for p in $PERSONAS; do echo "--- $p ---"; cat "$RUN_DIR/response_$p.txt" || true; echo ""; done)
=== END EXPERT DRAFTS ===

Please output the V1 Draft now.
EOF

if [[ "$DRY_RUN" == "true" ]]; then
    echo "Dry run output: V1 Draft" > "$V1_FILE"
    log_dry "Would assemble V1 via Chairperson."
else
    log_info "Summoning Chairperson (Assembler)..."
    C_PARAMS=("$PROMPT_FILE")
    [[ -n "$C_CMD" ]] && C_PARAMS+=("--cmd" "$C_CMD") || {
        [[ -n "$C_MODEL" ]] && C_PARAMS+=("--model" "$C_MODEL")
        [[ -n "$C_TEMP" ]] && C_PARAMS+=("--temperature" "$C_TEMP")
        [[ -n "$C_MAX_TOKENS" ]] && C_PARAMS+=("--max-tokens" "$C_MAX_TOKENS")
    }

    P_MODEL="$C_MODEL" P_TEMP="$C_TEMP" P_MAX_TOKENS="$C_MAX_TOKENS" \
    AI_AGENT="${C_ENGINE:-claude}" bash "$AI_EXEC_SH" "${C_PARAMS[@]}" > "$V1_FILE"
    log_ok "V1 Draft assembled."
fi

log_step "Step 4/5 — LLM Judge evaluates V1 Draft"

eval "$(python3 -c "
import yaml, sys, shlex
with open(sys.argv[1], 'r') as f: d = yaml.safe_load(f)
c = d.get('judge', {})
print(f\"J_NAME={shlex.quote(str(c.get('name', '')))}\")
print(f\"J_PROMPT={shlex.quote(str(c.get('prompt', '')))}\")
agent = c.get('agent', {})
print(f\"J_CMD={shlex.quote(str(agent.get('cmd') or ''))}\")
print(f\"J_ENGINE={shlex.quote(str(agent.get('engine') or ''))}\")
print(f\"J_MODEL={shlex.quote(str(agent.get('model') or ''))}\")
print(f\"J_TEMP={shlex.quote(str(agent.get('temperature') or ''))}\")
print(f\"J_MAX_TOKENS={shlex.quote(str(agent.get('max_tokens') or ''))}\")
" "$EXPERTS_YAML")"

if [[ -z "$J_NAME" ]]; then
    # No judge configured in YAML, we must fallback or skip
    log_warn "No 'judge' defined in YAML! Skipping Judge step."
    CRITIQUE_FILE="$RUN_DIR/critique.txt"
    echo "No judge configured. Skipping evaluation." > "$CRITIQUE_FILE"
else
    PROMPT_FILE="$RUN_DIR/prompt_judge.txt"
    CRITIQUE_FILE="$RUN_DIR/critique.txt"

    cp "$SHARED_CONTEXT_FILE" "$PROMPT_FILE"
    cat << EOF >> "$PROMPT_FILE"
$J_PROMPT

Evaluate the following V1 Draft for the strictly required schema and structure.
Identify any missing sections, malformed IDs, absent Traceability tags, or deviations from the provided template.

=== V1 DRAFT ===
$(cat "$V1_FILE")
=== END V1 DRAFT ===

Provide an Audit Critique detailing what MUST be fixed.
EOF

    if [[ "$DRY_RUN" == "true" ]]; then
        echo "Dry run output: Judge Critique" > "$CRITIQUE_FILE"
        log_dry "Would evaluate V1 via Judge."
    else
        log_info "Summoning Judge ($J_MODEL)..."
        J_PARAMS=("$PROMPT_FILE")
        [[ -n "$J_CMD" ]] && J_PARAMS+=("--cmd" "$J_CMD") || {
            [[ -n "$J_MODEL" ]] && J_PARAMS+=("--model" "$J_MODEL")
            [[ -n "$J_TEMP" ]] && J_PARAMS+=("--temperature" "$J_TEMP")
            [[ -n "$J_MAX_TOKENS" ]] && J_PARAMS+=("--max-tokens" "$J_MAX_TOKENS")
        }

        P_MODEL="$J_MODEL" P_TEMP="$J_TEMP" P_MAX_TOKENS="$J_MAX_TOKENS" \
        AI_AGENT="${J_ENGINE:-claude}" bash "$AI_EXEC_SH" "${J_PARAMS[@]}" > "$CRITIQUE_FILE"
        log_ok "Judge critique complete."
    fi
fi

log_step "Step 5/5 — Chairperson (Editor) builds Final Document"

eval "$(python3 -c "
import yaml, sys, shlex
with open(sys.argv[1], 'r') as f: d = yaml.safe_load(f)
c = d.get('editor', {})
print(f\"E_NAME={shlex.quote(str(c.get('name', '')))}\")
print(f\"E_PROMPT={shlex.quote(str(c.get('prompt', '')))}\")
agent = c.get('agent', {})
print(f\"E_CMD={shlex.quote(str(agent.get('cmd') or ''))}\")
print(f\"E_ENGINE={shlex.quote(str(agent.get('engine') or ''))}\")
print(f\"E_MODEL={shlex.quote(str(agent.get('model') or ''))}\")
print(f\"E_TEMP={shlex.quote(str(agent.get('temperature') or ''))}\")
print(f\"E_MAX_TOKENS={shlex.quote(str(agent.get('max_tokens') or ''))}\")
" "$EXPERTS_YAML")"

PROMPT_FILE="$RUN_DIR/prompt_editor.txt"
FINAL_FILE="$OUT_DIR/GENERATED_${DOC_TYPE}.md"

cp "$SHARED_CONTEXT_FILE" "$PROMPT_FILE"

cat << EOF >> "$PROMPT_FILE"
$E_PROMPT

=== V1 DRAFT ===
$(cat "$V1_FILE")
=== END V1 DRAFT ===

=== JUDGE CRITIQUE ===
$(cat "$CRITIQUE_FILE")
=== END JUDGE CRITIQUE ===

INSTRUCTIONS:
Using the Judge's feedback, correct the V1 draft.
Output the FINAL, fully compliant Markdown document. 
Ensure you wrap the final output cleanly.
EOF

if [[ "$DRY_RUN" == "true" ]]; then
    echo "Dry run output: Final Document" > "$FINAL_FILE"
    log_dry "Would create Final Document."
else
    log_info "Summoning Chairperson (Editor)..."
    E_PARAMS=("$PROMPT_FILE")
    [[ -n "$E_CMD" ]] && E_PARAMS+=("--cmd" "$E_CMD") || {
        [[ -n "$E_MODEL" ]] && E_PARAMS+=("--model" "$E_MODEL")
        [[ -n "$E_TEMP" ]] && E_PARAMS+=("--temperature" "$E_TEMP")
        [[ -n "$E_MAX_TOKENS" ]] && E_PARAMS+=("--max-tokens" "$E_MAX_TOKENS")
    }

    P_MODEL="$E_MODEL" P_TEMP="$E_TEMP" P_MAX_TOKENS="$E_MAX_TOKENS" \
    AI_AGENT="${E_ENGINE:-claude}" bash "$AI_EXEC_SH" "${E_PARAMS[@]}" > "$FINAL_FILE"
    log_ok "Generation Pipeline complete. Document saved to: $FINAL_FILE"
fi

echo "════════════════════════════════════════════════════════════"
echo "  DOC REVIEW PIPELINE GENERATION — Complete"
echo "════════════════════════════════════════════════════════════"
