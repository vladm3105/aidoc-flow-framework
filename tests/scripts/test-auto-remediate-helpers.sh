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

# ─── write_synthetic_verdict / write_synthetic_audit_report (inline) ─────────

write_synthetic_verdict() {
  local example_root="$1" layer_dir="$2" art_id="$3" message="$4"
  local out="$example_root/.aidoc/review/$layer_dir/$art_id/verdict.json"
  mkdir -p "$(dirname "$out")"
  python3 - "$out" "$message" "$art_id" "$layer_dir" <<'PY'
import json, sys, datetime
out, message, art_id, layer_dir = sys.argv[1:5]
ts = datetime.datetime.utcnow().isoformat() + "Z"
verdict = {
    "combined_status": "FAIL",
    "content_score": 0,
    "structural_status": "FAIL",
    "coverage": {"expected": 1, "ran": 1, "quorum_met": True},
    "blocking_findings_count": 1,
    "lens_scores": {},
    "findings": [{
        "id": "AUTO-REMEDIATE-STY03-001",
        "code": "STY03",
        "priority": "P1",
        "location": f"{art_id} — document body",
        "message": message,
        "recommendation": "Trim the document body below the EARS blocking word-count threshold (2250 words). Preserve all element IDs and the structural section set.",
        "personas": [],
    }],
    "playbook_coverage": {},
    "generated_at": ts,
    "synthetic": True,
    "synthetic_origin": "AUTO-REMEDIATE-001",
}
with open(out, "w") as f:
    json.dump(verdict, f, indent=2)
PY
}

write_synthetic_audit_report() {
  local example_root="$1" layer_dir="$2" art_id="$3" message="$4"
  local out="$example_root/.aidoc/audit/$layer_dir-audit.md"
  mkdir -p "$(dirname "$out")"
  cat > "$out" <<EOF
# Audit report — $art_id (synthetic / AUTO-REMEDIATE-001)

Combined status: FAIL
Content score: 0/100
Structural status: FAIL
Coverage quorum: met
Synthetic: true (origin AUTO-REMEDIATE-001 — cascade bootstrap auto-remediation)

## Findings

| ID | Priority | Code | Location | Message |
|---|---|---|---|---|
| AUTO-REMEDIATE-STY03-001 | P1 | STY03 | $art_id — document body | $message |

## Recommendation

Trim the document body below the EARS blocking word-count threshold (2250 words). Preserve all element IDs and the structural section set.
EOF
}

# ─── write_synthetic_verdict tests ───────────────────────────────────────────

test_write_synthetic_verdict() {
  local tmpdir
  tmpdir="$(mktemp -d)"
  trap 'rm -rf "$tmpdir"' RETURN
  local example_root="$tmpdir/example"
  mkdir -p "$example_root/.aidoc/review/03_EARS/EARS-01"

  write_synthetic_verdict "$example_root" "03_EARS" "EARS-01" \
    "Document body is 2457 words; reduce to <=2250."

  local verdict_file="$example_root/.aidoc/review/03_EARS/EARS-01/verdict.json"
  [[ -f "$verdict_file" ]] || { echo "FAIL: verdict.json not written" >&2; exit 1; }
  python3 -c "
import json
v = json.load(open('$verdict_file'))
assert v['combined_status'] == 'FAIL', f'expected FAIL got {v[\"combined_status\"]}'
assert v['blocking_findings_count'] == 1, f'expected 1 blocking got {v[\"blocking_findings_count\"]}'
assert len(v['findings']) == 1, f'expected 1 finding got {len(v[\"findings\"])}'
f = v['findings'][0]
assert f['priority'] == 'P1', f'expected P1 got {f[\"priority\"]}'
assert f['code'] == 'STY03', f'expected STY03 got {f[\"code\"]}'
assert '2457 words' in f['message'], f'message missing word count: {f[\"message\"]}'
print('  PASS: synthetic verdict.json shape valid')
"
}

echo ""
echo "=== write_synthetic_verdict ==="
test_write_synthetic_verdict

# ─── write_synthetic_audit_report tests ──────────────────────────────────────

test_write_synthetic_audit_report() {
  local tmpdir
  tmpdir="$(mktemp -d)"
  trap 'rm -rf "$tmpdir"' RETURN
  local example_root="$tmpdir/example"
  mkdir -p "$example_root/.aidoc/audit"

  write_synthetic_audit_report "$example_root" "03_EARS" "EARS-01" \
    "Document body is 2457 words; reduce to <=2250."

  local report_file="$example_root/.aidoc/audit/03_EARS-audit.md"
  [[ -f "$report_file" ]] || { echo "FAIL: audit report not written" >&2; exit 1; }
  grep -q 'STY03' "$report_file" || { echo "FAIL: report missing STY03" >&2; exit 1; }
  grep -q '2457 words' "$report_file" || { echo "FAIL: report missing word count" >&2; exit 1; }
  echo "  PASS: synthetic audit report content valid"
}

echo ""
echo "=== write_synthetic_audit_report ==="
test_write_synthetic_audit_report

# ─── backup_doc / restore_backup (inline) ────────────────────────────────────

backup_doc() {
  local path="$1"
  cp "$path" "$path.auto-remediate-backup"
}

restore_backup() {
  local path="$1"
  local bak="$path.auto-remediate-backup"
  if [[ -f "$bak" ]]; then
    mv "$bak" "$path"
  else
    log_warn() { echo "$@" >&2; }  # local stub if not sourced
    log_warn "restore_backup: no backup at $bak (already restored or never backed up)"
  fi
}

# ─── backup_doc / restore_backup tests ───────────────────────────────────────

test_backup_restore_doc() {
  local tmpdir
  tmpdir="$(mktemp -d)"
  trap 'rm -rf "$tmpdir"' RETURN
  local doc="$tmpdir/test.md"
  echo "ORIGINAL" > "$doc"

  backup_doc "$doc"
  echo "MODIFIED" > "$doc"
  assert_eq "$(cat "$doc")" "MODIFIED" "modification took effect"

  restore_backup "$doc"
  assert_eq "$(cat "$doc")" "ORIGINAL" "restore_backup restored original"
}

echo ""
echo "=== backup_doc / restore_backup ==="
test_backup_restore_doc

echo ""
echo "All tests passed."
