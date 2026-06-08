#!/usr/bin/env bash
# Unit tests for AUTO-REMEDIATE-001 helper functions in test-acceptance.sh.
# Sources test-acceptance.sh, calls helpers, asserts via [[ ]].

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

# Define test helpers inline (copied from test-acceptance.sh to avoid sourcing
# main entry-point code that requires arguments and environment setup).
has_STY03_only() {
  local output="$1"
  # Count ERROR-level lines that are NOT STY03
  local other_errors
  other_errors="$(printf '%s\n' "$output" | grep -cE '\[ERROR (STRUCT|AS|CSC|STY0[12]|STY[4-9])' || true)"
  # Count STY03 ERROR lines
  local sty03_errors
  sty03_errors="$(printf '%s\n' "$output" | grep -cE '\[ERROR STY03\]' || true)"
  # STY03-only iff at least one STY03 and zero other errors
  [[ "$sty03_errors" -gt 0 && "$other_errors" -eq 0 ]]
}

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

# ─── extract_path / extract_layer_dir / extract_artifact_id (inline) ────────

extract_path() {
  local output="$1"
  printf '%s\n' "$output" | grep -oE '^[^:]+:[0-9]+: \[ERROR STY03\]' \
    | head -1 \
    | sed -E 's/^([^:]+):[0-9]+: \[ERROR STY03\]$/\1/'
}

extract_layer_dir() {
  local path="$1"
  printf '%s' "$path" | grep -oE '/[0-9]{2}_[A-Z]+/' | head -1 | tr -d /
}

extract_artifact_id() {
  local path="$1"
  basename "$path" | grep -oE '^[A-Z]+-[0-9]+' | head -1
}

# ─── extract_path tests ──────────────────────────────────────────────────────

test_extract_path() {
  local input
  input="$(cat "$FIXTURES/lint-sty03-only.txt")"
  local actual
  actual="$(extract_path "$input")"
  assert_eq "$actual" "examples/url-shortener/docs/03_EARS/EARS-01.md" \
    "extract_path returns the STY03-failing file path"
}

echo ""
echo "=== extract_path ==="
test_extract_path

# ─── extract_layer_dir tests ─────────────────────────────────────────────────

test_extract_layer_dir() {
  local actual
  actual="$(extract_layer_dir 'examples/url-shortener/docs/03_EARS/EARS-01.md')"
  assert_eq "$actual" "03_EARS" "extract_layer_dir returns the 0N_LAYER segment"

  actual="$(extract_layer_dir 'examples/url-shortener/docs/02_PRD/PRD-01.md')"
  assert_eq "$actual" "02_PRD" "extract_layer_dir works for PRD"

  actual="$(extract_layer_dir 'examples/url-shortener/docs/08_IPLAN/IPLAN-01.md')"
  assert_eq "$actual" "08_IPLAN" "extract_layer_dir works for IPLAN"
}

echo ""
echo "=== extract_layer_dir ==="
test_extract_layer_dir

# ─── extract_artifact_id tests ───────────────────────────────────────────────

test_extract_artifact_id() {
  local actual
  actual="$(extract_artifact_id 'examples/url-shortener/docs/03_EARS/EARS-01.md')"
  assert_eq "$actual" "EARS-01" "extract_artifact_id returns the LAYER-NN prefix"

  actual="$(extract_artifact_id 'examples/url-shortener/docs/02_PRD/PRD-01.md')"
  assert_eq "$actual" "PRD-01" "extract_artifact_id works for PRD"
}

echo ""
echo "=== extract_artifact_id ==="
test_extract_artifact_id

echo ""
echo "All tests passed."
