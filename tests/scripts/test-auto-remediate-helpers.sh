#!/usr/bin/env bash
# Unit tests for AUTO-REMEDIATE-001 helper functions in test-acceptance.sh.
# Sources test-acceptance.sh, calls helpers, asserts via [[ ]].

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

# Source test-acceptance.sh in a way that defines functions without executing main.
# We strip from line 139 (arg parsing) through line 202 (path setup + traps),
# then skip to the function definitions and stop before phase_0_bootstrap entry point.
TMPF="$(mktemp)"
trap 'rm -f "$TMPF"' EXIT

# Strip the entry-point code and source the rest.
sed '/^phase_0_bootstrap || {/,$d' tests/scripts/test-acceptance.sh > "$TMPF"
# shellcheck source=/dev/null
source "$TMPF" 2>&1 | grep -v -E "ERROR.*example|sed.*can't read" || true

FIXTURES="$REPO_ROOT/tests/scripts/fixtures/auto-remediate"

assert_eq() {
  local actual="$1" expected="$2" label="$3"
  if [[ "$actual" != "$expected" ]]; then
    echo "FAIL: $label: expected='$expected' actual='$actual'" >&2
    exit 1
  fi
  echo "  PASS: $label"
}

# ─── has_STY03_only tests ────────────────────────────────────────────────────

test_has_STY03_only_sty03_only() {
  local input
  input="$(cat "$FIXTURES/lint-sty03-only.txt")"
  if has_STY03_only "$input"; then
    echo "  PASS: STY03-only input returns 0 (true)"
  else
    echo "FAIL: STY03-only input should return 0 (true)" >&2
    exit 1
  fi
}

test_has_STY03_only_mixed() {
  local input
  input="$(cat "$FIXTURES/lint-mixed.txt")"
  if has_STY03_only "$input"; then
    echo "FAIL: STY03+STRUCT01 input should return non-zero (false)" >&2
    exit 1
  fi
  echo "  PASS: STY03+other input returns non-zero (false)"
}

test_has_STY03_only_no_sty03() {
  local input
  input="$(cat "$FIXTURES/lint-no-sty03.txt")"
  if has_STY03_only "$input"; then
    echo "FAIL: STRUCT01-only input should return non-zero (false)" >&2
    exit 1
  fi
  echo "  PASS: non-STY03 input returns non-zero (false)"
}

echo "=== has_STY03_only ==="
test_has_STY03_only_sty03_only
test_has_STY03_only_mixed
test_has_STY03_only_no_sty03

echo ""
echo "All tests passed."
