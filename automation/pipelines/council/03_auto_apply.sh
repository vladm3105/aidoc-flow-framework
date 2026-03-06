#!/usr/bin/env bash
# =============================================================================
# 03_auto_apply.sh — Step 3: Auto-Apply Structural P0 Fixes
# =============================================================================
# Usage: 03_auto_apply.sh <actions.json> <target_doc_path>
#
# For each action in actions.json where:
#   - type is in AUTO_APPLY_TYPES (frontmatter_tag, section_add, matrix_row, etc.)
#   - target_document matches the source doc
#
# Calls the AI agent to apply the fix, writes the patched file, and optionally
# commits to git. Non-auto-applicable actions are skipped (handled by 04_create_issues.py).
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CORE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")/core"

source "$CORE_DIR/config.sh"
source "$CORE_DIR/utils.sh"

require_jq

ACTIONS_JSON="${1:-}"
TARGET_DOC="${2:-}"

[[ -z "$ACTIONS_JSON" ]] && die "Usage: 03_auto_apply.sh <actions.json> <target_doc_path>"
[[ -z "$TARGET_DOC"   ]] && die "Usage: 03_auto_apply.sh <actions.json> <target_doc_path>"
require_file "$ACTIONS_JSON"
require_file "$TARGET_DOC"

assert_valid_json_array "$ACTIONS_JSON"

log_step "Step 3: Auto-applying structural fixes"
log_info "Actions JSON: $ACTIONS_JSON"
log_info "Target doc:   $TARGET_DOC"

APPLY_PROMPT_TEMPLATE="$SCRIPT_DIR/prompts/apply_fix.txt"
require_file "$APPLY_PROMPT_TEMPLATE"

TARGET_DOC_ID=$(basename "$(dirname "$TARGET_DOC")")  # e.g. BRD-01_platform_architecture

APPLIED=0
SKIPPED=0

# Iterate through actions
while IFS= read -r action; do
  ACTION_ID=$(json_get "$action" '.id' 'unknown')
  PRIORITY=$(json_get "$action" '.priority' 'P2')
  ACTION_TYPE=$(json_get "$action" '.type' 'unknown')
  ACTION_TEXT=$(json_get "$action" '.action' '')
  TARGET_SECTION=$(json_get "$action" '.target_section' 'unknown')
  SOURCE_EXPERT=$(json_get "$action" '.source_expert' 'unknown')
  ACTION_TARGET_DOC=$(json_get "$action" '.target_document' '')
  ACTION_TARGET_FILE=$(json_get "$action" '.target_file' '')

  # Only process actions that target this document
  # Match loosely: "BRD-01" matches folders/files containing "BRD-01"
  if [[ -n "$ACTION_TARGET_DOC" ]] && ! echo "$TARGET_DOC_ID" | grep -qi "${ACTION_TARGET_DOC}"; then
    log_info "[$ACTION_ID] Skip — targets $ACTION_TARGET_DOC (not this doc)"
    ((SKIPPED++)) || true
    continue
  fi

  # Only auto-apply structural types
  if ! is_auto_applicable "$ACTION_TYPE"; then
    log_info "[$ACTION_ID] Skip — type '$ACTION_TYPE' requires human review (→ GitHub Issue)"
    ((SKIPPED++)) || true
    continue
  fi

  log_info "[$ACTION_ID] Applying: [$PRIORITY/$ACTION_TYPE] $ACTION_TEXT"

  # Resolve target file dynamically (support multi-file architectures)
  ACTUAL_TARGET="$TARGET_DOC"
  if [[ -n "$ACTION_TARGET_FILE" && "$ACTION_TARGET_FILE" != "null" ]]; then
    POTENTIAL_TARGET="$(dirname "$TARGET_DOC")/$ACTION_TARGET_FILE"
    if [[ -f "$POTENTIAL_TARGET" ]]; then
      ACTUAL_TARGET="$POTENTIAL_TARGET"
      log_info "[$ACTION_ID] Routing patch specifically to: $ACTION_TARGET_FILE"
    else
      log_warn "[$ACTION_ID] Target file '$ACTION_TARGET_FILE' not found. Falling back to targeted root $TARGET_DOC"
    fi
  fi

  # Build prompt from template, substituting placeholders
  PROMPT_TMP=$(tmp_file "council_apply_prompt_${ACTION_ID}")
  cleanup_on_exit "$PROMPT_TMP"

  sed \
    -e "s|{{ACTION_TYPE}}|$ACTION_TYPE|g" \
    -e "s|{{ACTION}}|$ACTION_TEXT|g" \
    -e "s|{{TARGET_SECTION}}|$TARGET_SECTION|g" \
    -e "s|{{SOURCE_EXPERT}}|$SOURCE_EXPERT|g" \
    -e "s|{{PRIORITY}}|$PRIORITY|g" \
    "$APPLY_PROMPT_TEMPLATE" > "$PROMPT_TMP"

  # Append the current document content
  echo "" >> "$PROMPT_TMP"
  cat "$ACTUAL_TARGET" >> "$PROMPT_TMP"

  if [[ "${DRY_RUN:-false}" == "true" ]]; then
    log_dry "[$ACTION_ID] Would apply fix to: $ACTUAL_TARGET"
    log_dry "[$ACTION_ID] Prompt: $(wc -l < "$PROMPT_TMP") lines"
    ((APPLIED++)) || true
    continue
  fi

  # Call AI agent to apply the fix
  PATCHED_TMP=$(tmp_file "council_patched_${ACTION_ID}")
  cleanup_on_exit "$PATCHED_TMP"

  if ! "$AI_EXEC_SH" "$PROMPT_TMP" > "$PATCHED_TMP" 2>/tmp/ai_exec_err.txt; then
    log_warn "[$ACTION_ID] AI agent failed — skipping this fix"
    cat /tmp/ai_exec_err.txt >&2
    ((SKIPPED++)) || true
    continue
  fi

  # Sanity check: patched file must be non-empty and larger than 100 chars
  PATCHED_SIZE=$(wc -c < "$PATCHED_TMP")
  if [[ "$PATCHED_SIZE" -lt 100 ]]; then
    log_warn "[$ACTION_ID] Patched output too small ($PATCHED_SIZE bytes) — skipping"
    ((SKIPPED++)) || true
    continue
  fi

  # Apply the patch
  cp "$PATCHED_TMP" "$ACTUAL_TARGET"
  log_ok "[$ACTION_ID] Fix applied to: $ACTUAL_TARGET"

  # Commit if enabled
  if [[ "${AUTO_APPLY_COMMIT:-true}" == "true" ]]; then
    COMMIT_MSG="auto-fix($ACTION_TARGET_DOC): [$PRIORITY] $ACTION_ID — $ACTION_TYPE by $SOURCE_EXPERT"
    git_commit_if_changes "$COMMIT_MSG" "$ACTUAL_TARGET"
  fi

  ((APPLIED++)) || true

done < <(jq -c '.[]' "$ACTIONS_JSON")

log_ok "Step 3 complete: $APPLIED fixes applied, $SKIPPED skipped (→ will become GitHub Issues)"
