#!/usr/bin/env bash
# Muse adaptation of the canon installer test: the skill + gate install from
# .agents/skills/verified-planning/ into <repo>/.agents/skills/verified-planning/.
set -euo pipefail
SRC="$(cd "$(dirname "$0")/.." && pwd)"   # the master skill dir
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/repoA/.git"
base="$tmp/repoA/.agents/skills/verified-planning"

# seed the repo as an OLDER installer left it, so the run below exercises the
# self-heal path and not just a clean install
mkdir -p "$base"
printf 'stale installer\n' > "$base/install.sh"

bash "$SRC/install.sh" "$tmp/repoA"

# the skill + gate belong in the repo — CI and the hook run from the checkout,
# and the method travels with the gate so they stay in sync
for f in SKILL.md check_plan.py PLAN.md DESIGN.md PLAN-TEMPLATE.snippet.md README.md; do
  test -f "$base/$f" || { echo "FAIL: missing $f"; exit 1; }
done
test -f "$base/tests/test_check_plan.py" || { echo "FAIL: tests not copied"; exit 1; }
test -f "$base/tests/test_install.sh" || { echo "FAIL: installer test not copied"; exit 1; }
test -f "$tmp/repoA/.github/workflows/plan-gate.yml" || { echo "FAIL: ci"; exit 1; }

# install.sh must not travel: a repo carrying its own copy can re-infect itself
# with a stale copy list.
test ! -e "$base/install.sh" \
  || { echo "FAIL: install.sh installed — re-infection path"; exit 1; }

# and the README that says what the directory is
# Literal backticks are intentional.
# shellcheck disable=SC2016
grep -q 'live Muse project skill' "$base/README.md" \
  || { echo "FAIL: README missing the live-skill note"; exit 1; }
grep -q '`SKILL.md`' "$base/README.md" \
  || { echo "FAIL: README missing the skill reference"; exit 1; }
echo "PASS"
