#!/usr/bin/env bash
# PreToolUse(git commit) — warn (non-blocking) if a staged plan file carries
# fewer than two review passes in its ## Review log (see CLAUDE.md workflow).
set -u

cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

short=""
while IFS= read -r f; do
  case "$f" in
    plans/PLAN-TEMPLATE.md) continue ;;
    plans/*PLAN*.md|plans/*plan*.md) ;;
    *) continue ;;
  esac
  passes=$(git show ":$f" 2>/dev/null | grep -cE '^### Pass ' || true)
  if [ "${passes:-0}" -lt 2 ]; then
    short="${short}  - ${f}: ${passes:-0} review pass(es)\n"
  fi
done < <(git diff --cached --name-only --diff-filter=AM)

[ -z "$short" ] && exit 0

msg="Plan review gate: staged plan file(s) have fewer than 2 review passes in their ## Review log:\n${short}Per CLAUDE.md, a plan needs >=2 ISO-stamped passes before it is implemented."
jq -n --arg m "$(printf '%b' "$msg")" '{systemMessage: $m}'
exit 0
