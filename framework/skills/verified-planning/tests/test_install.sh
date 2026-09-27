#!/usr/bin/env bash
# Framework adaptation of the canon installer test: the gate installs from
# framework/skills/verified-planning/ into <repo>/framework-skills/.
set -euo pipefail
SRC="$(cd "$(dirname "$0")/.." && pwd)"   # the master skill dir
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/repoA/.git"
base="$tmp/repoA/framework-skills/verified-planning"

bash "$SRC/install.sh" "$tmp/repoA"

# the gate belongs in the repo — CI and the hook run from the checkout
for f in check_plan.py PLAN-TEMPLATE.snippet.md README.md; do
  test -f "$base/$f" || { echo "FAIL: missing $f"; exit 1; }
done
test -f "$base/tests/test_check_plan.py" || { echo "FAIL: tests not copied"; exit 1; }
test -f "$tmp/repoA/.github/workflows/plan-gate.yml" || { echo "FAIL: ci"; exit 1; }

# the installer itself must not travel: a repo carrying its own copy can
# re-infect itself with a stale copy list.
test ! -e "$base/install.sh" \
  || { echo "FAIL: install.sh installed — re-infection path"; exit 1; }

grep -q 'committed gate only' "$base/README.md" \
  || { echo "FAIL: README missing gate-only note"; exit 1; }
echo "PASS"
