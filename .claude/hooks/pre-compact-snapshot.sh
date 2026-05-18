#!/usr/bin/env bash
# PreCompact hook — snapshot uncommitted work before context compaction so
# nothing is lost if the ephemeral container is reclaimed afterwards.
# Acts only on the migration working branch; no-ops otherwise.
set -u

cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

WORKING_BRANCH="claude/multi-platform-migration-AamWB"
branch=$(git branch --show-current 2>/dev/null)
[ "$branch" = "$WORKING_BRANCH" ] || exit 0

# Nothing staged, unstaged, or untracked — nothing to snapshot.
[ -z "$(git status --porcelain)" ] && exit 0

ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
git add -A || exit 0
git commit -m "wip: pre-compact snapshot ${ts}" >/dev/null 2>&1 || exit 0

pushed="local-only (push failed)"
for delay in 0 2 4 8; do
  [ "$delay" -gt 0 ] && sleep "$delay"
  if git push origin "$branch" >/dev/null 2>&1; then
    pushed="pushed"
    break
  fi
done

jq -n --arg msg "PreCompact: WIP snapshot committed (${pushed}) at ${ts}" \
  '{systemMessage: $msg, suppressOutput: true}'
