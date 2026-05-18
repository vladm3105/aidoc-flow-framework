#!/usr/bin/env bash
# SessionStart hook — inject the migration handoff record into context so a
# fresh or post-compaction session resumes exactly where the last one stopped.
set -u

cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0
[ -f plans/HANDOFF.md ] || exit 0

content=$(cat plans/HANDOFF.md)
jq -n --arg c "$content" \
  '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: ("Migration handoff record (plans/HANDOFF.md) — read before starting work:\n\n" + $c)}}'
