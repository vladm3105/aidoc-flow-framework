#!/usr/bin/env bash
# on_author trigger point (${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_REMEDIATION_FLOW.md).
#
# PostToolUse(Write|Edit) advisory hook: when an SDD instance document is
# written/edited, nudge the matching review skill (and, best-effort, surface
# deterministic structural findings if sdd_doc_lint is importable). Strictly
# ADVISORY — it never blocks the edit and always exits 0. The blocking
# deterministic gate is the pre_merge CI check (doc-review.yml), not this hook.

# Degrade silently if jq is unavailable (hooks parse stdin JSON with jq).
command -v jq >/dev/null 2>&1 || exit 0

input="$(cat)"
file_path="$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty' 2>/dev/null)"
[ -z "$file_path" ] && exit 0

base="$(basename "$file_path")"

# Detect the SDD layer: docs/0N_<ARTIFACT>/ path, or a <ARTIFACT>-NN filename.
artifact=""
if [[ "$file_path" =~ /docs/[0-9]{2}_([A-Za-z]+)/ ]]; then
  artifact="${BASH_REMATCH[1]}"
elif [[ "$base" =~ ^([A-Za-z]+)-[0-9] ]]; then
  artifact="${BASH_REMATCH[1]}"
fi
artifact="$(printf '%s' "$artifact" | tr '[:lower:]' '[:upper:]')"

case "$artifact" in
  BRD|PRD|EARS|BDD|ADR|SPEC|TDD|IPLAN) ;;
  *) exit 0 ;;  # not an SDD instance document — nothing to advise
esac

layer="$(printf '%s' "$artifact" | tr '[:upper:]' '[:lower:]')"
msg="Edited a ${artifact} document (${base}). Per the framework review→remediation→gate loop (on_author): run /aidoc-flow:doc-${layer}-audit to score readiness before promoting downstream; if it scores below the gate, /aidoc-flow:doc-${layer}-fixer remediates."

# Deterministic structural check via the vendored linter. The plugin ships
# sdd_doc_lint at its root, so derive the plugin root from this script's path
# and put it on PYTHONPATH (works regardless of the CLAUDE_PLUGIN_ROOT env var).
# Exit codes: 1 = structural findings (append); 0 = clean; 2 = registry not
# found (e.g. no framework/ in the project) → skip silently.
plugin_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." 2>/dev/null && pwd)"
if command -v python3 >/dev/null 2>&1 && [ -n "$plugin_root" ]; then
  findings="$(PYTHONPATH="${plugin_root}${PYTHONPATH:+:$PYTHONPATH}" python3 -m sdd_doc_lint "$file_path" 2>&1)"
  if [ "$?" -eq 1 ]; then
    msg="${msg}"$'\n\nStructural findings (sdd_doc_lint):\n'"${findings}"
  fi
fi

jq -n --arg ctx "$msg" \
  '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $ctx}}'
exit 0
