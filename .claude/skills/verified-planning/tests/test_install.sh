#!/usr/bin/env bash
set -euo pipefail
SRC="$(cd "$(dirname "$0")/.." && pwd)"   # the master skill dir
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/repoA/.git"
printf '.claude/\n' > "$tmp/repoA/.gitignore"   # a repo that ignores .claude/
bash "$SRC/install.sh" "$tmp/repoA"
base="$tmp/repoA/.claude/skills/verified-planning"
for f in SKILL.md check_plan.py PLAN.md DESIGN.md PLAN-TEMPLATE.snippet.md; do
  test -f "$base/$f" || { echo "FAIL: missing $f"; exit 1; }
done
test -f "$base/tests/test_check_plan.py" || { echo "FAIL: tests not copied"; exit 1; }
test -f "$tmp/repoA/.github/workflows/plan-gate.yml" || { echo "FAIL: ci"; exit 1; }
grep -q 'verified-planning skill must be committed' "$tmp/repoA/.gitignore" \
  || { echo "FAIL: gitignore not un-ignored"; exit 1; }
echo "PASS"
