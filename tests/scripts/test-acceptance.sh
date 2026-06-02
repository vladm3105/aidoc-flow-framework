#!/usr/bin/env bash
#
# tests/scripts/test-acceptance.sh — Pre-deployment acceptance test driver.
#
# Drives every active element of the Claude Code plugin (currently 50
# skills + 11 agents + 1 command + 1 hook = 63 elements) against a named
# example's seed. The chain produced is the release-gate evidence.
#
# Plan: examples/<NAME>/ACCEPTANCE_TEST_PLAN.md (the design reference).
# Schema: tests/scripts/test-acceptance.schema.json.
#
# This is the Impl-1 foundation: arg parsing, log layout, Phase 0
# preflight, Phase 1.1 happy-path cascade structure, --mock mode.
# Phases 1.2, 2, 3, 4 land in Impl-2 through Impl-5.
#
# Usage:
#   bash tests/scripts/test-acceptance.sh <example-name> [flags]
#
#   Flags:
#     --no-live              skip live LLM calls (Phase 0 only effectively)
#     --live                 enable live LLM calls (default ON)
#     --phase=<name>         run one phase: bootstrap | cascade | negative |
#                            chg | utilities | agents | command | hook
#     --element=<name>       run one element only (e.g. doc-flow,
#                            agent:requirements-analyst)
#     --skip-completed       reuse prior run's PASS outcomes, skip those elements
#     --mock=<run-dir>       replay a prior recorded run; no Claude calls
#     --promote              promote cascade output to examples/<NAME>/docs/
#                            (lands in Impl-5)
#     --push                 push the promote commit (only with --promote)
#     --fail-fast            halt on first failure
#     -h | --help            show this usage block
#
# Output:
#   examples/<NAME>/logs/<LOG_TIMESTAMP>/
#     plugin-test.log              # this driver's stdout/stderr
#     summary.txt                  # human-readable per-element table
#     summary.json                 # machine-readable; conforms to
#                                  # tests/scripts/test-acceptance.schema.json
#     skills/<NAME>.{log,meta.json}
#     agents/<NAME>.{log,meta.json}
#     command/save-plan.{log,meta.json}
#     hook/sdd-doc-review.{log,meta.json}
#     cascade/<NN>_<LAYER>/<TYPE>-01.<example>.md
#     negative/<FIXTURE>.audit.log

set -uo pipefail

# -----------------------------------------------------------------------------
# Constants & globals
# -----------------------------------------------------------------------------
FRAMEWORK="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$FRAMEWORK"

PLUGIN_DIR="$FRAMEWORK/platforms/claude-code-plugin"
LAYERS=("brd" "prd" "ears" "bdd" "adr" "spec" "tdd" "iplan")
LAYER_TYPES=("BRD" "PRD" "EARS" "BDD" "ADR" "SPEC" "TDD" "IPLAN")
NEGATIVE_FIXTURES_DIR="$FRAMEWORK/tests/acceptance/fixtures/negative"
MAX_RUNTIME_SEC=2700   # 45 minutes (plan §9 + §13)

LOG_TIMESTAMP="$(date +%Y-%m-%dT%H%M%S)"
START_EPOCH="$(date +%s)"

# -----------------------------------------------------------------------------
# Arg parsing
# -----------------------------------------------------------------------------
EXAMPLE=""
LIVE_FLAG=""
PHASE=""
ELEMENT=""
SKIP_COMPLETED=0
MOCK_SOURCE=""
PROMOTE=0
PUSH=0
FAIL_FAST=0

usage() {
  sed -n '2,42p' "$0"
  exit "${1:-0}"
}

# First positional: example name
if [[ $# -lt 1 ]]; then
  echo "ERROR: missing example name" >&2
  usage 2
fi
case "$1" in
  -h|--help) usage 0 ;;
  --*)
    echo "ERROR: first argument must be the example name (got '$1')" >&2
    usage 2
    ;;
esac
EXAMPLE="$1"
shift

for arg in "$@"; do
  case "$arg" in
    --no-live)         LIVE_FLAG="0" ;;
    --live)            LIVE_FLAG="1" ;;
    --phase=*)         PHASE="${arg#--phase=}" ;;
    --element=*)       ELEMENT="${arg#--element=}" ;;
    --skip-completed)  SKIP_COMPLETED=1 ;;
    --mock=*)          MOCK_SOURCE="${arg#--mock=}" ;;
    --promote)         PROMOTE=1 ;;
    --push)            PUSH=1 ;;
    --fail-fast)       FAIL_FAST=1 ;;
    -h|--help)         usage 0 ;;
    *) echo "ERROR: unknown flag: $arg" >&2; usage 2 ;;
  esac
done

# Resolve LIVE_FLAG default (ON; --mock implies non-live)
if [[ -n "$MOCK_SOURCE" ]]; then
  LIVE_FLAG="0"
elif [[ -z "$LIVE_FLAG" ]]; then
  LIVE_FLAG="1"
fi

# -----------------------------------------------------------------------------
# Path resolution per example
# -----------------------------------------------------------------------------
EXAMPLE_DIR="$FRAMEWORK/examples/$EXAMPLE"
if [[ ! -d "$EXAMPLE_DIR" ]]; then
  echo "ERROR: example directory does not exist: $EXAMPLE_DIR" >&2
  exit 2
fi
SEED_FILE="$EXAMPLE_DIR/seed/initial-requirements.md"
EXAMPLE_DOCS="$EXAMPLE_DIR/docs"
CHG_FILE="$EXAMPLE_DIR/chg/test-change.md"

LOG_DIR="$EXAMPLE_DIR/logs/$LOG_TIMESTAMP"
mkdir -p "$LOG_DIR"/{bootstrap,skills,agents,command,hook,cascade,negative}
DRIVER_LOG="$LOG_DIR/plugin-test.log"
SUMMARY_TXT="$LOG_DIR/summary.txt"
SUMMARY_JSON="$LOG_DIR/summary.json"

# Tee everything to driver log
exec > >(tee -a "$DRIVER_LOG") 2>&1

# -----------------------------------------------------------------------------
# Output helpers
# -----------------------------------------------------------------------------
section() {
  printf '\n=================================================================\n'
  printf '  %s\n' "$*"
  printf '=================================================================\n'
}

log_info() { printf 'INFO  %s\n' "$*"; }
log_warn() { printf 'WARN  %s\n' "$*"; }
log_err()  { printf 'ERROR %s\n' "$*" >&2; }

# Outcome counters (parallel arrays keyed by element name)
declare -A OUTCOME_BY_NAME=()
declare -A KIND_BY_NAME=()
declare -A PHASE_BY_NAME=()
declare -A DURATION_BY_NAME=()
declare -A AUDIT_SCORE_BY_NAME=()
declare -A AUDIT_AFTER_FIXER_BY_NAME=()
declare -A FIXER_INVOKED_BY_NAME=()
declare -A OUTPUT_PATH_BY_NAME=()
declare -A ERROR_BY_NAME=()
declare -a ELEMENT_ORDER=()

record_outcome() {
  # record_outcome <name> <kind> <phase> <outcome> <duration> [<audit_score>] [<audit_after_fixer>] [<fixer_invoked>] [<output_path>] [<error>]
  local name="$1" kind="$2" phase="$3" outcome="$4" duration="$5"
  local audit="${6:-}" audit_after="${7:-}" fixer_inv="${8:-false}" out_path="${9:-}" err="${10:-}"

  if [[ -z "${OUTCOME_BY_NAME[$name]:-}" ]]; then
    ELEMENT_ORDER+=("$name")
  fi
  OUTCOME_BY_NAME[$name]="$outcome"
  KIND_BY_NAME[$name]="$kind"
  PHASE_BY_NAME[$name]="$phase"
  DURATION_BY_NAME[$name]="$duration"
  AUDIT_SCORE_BY_NAME[$name]="$audit"
  AUDIT_AFTER_FIXER_BY_NAME[$name]="$audit_after"
  FIXER_INVOKED_BY_NAME[$name]="$fixer_inv"
  OUTPUT_PATH_BY_NAME[$name]="$out_path"
  ERROR_BY_NAME[$name]="$err"
}

write_meta_json() {
  # write_meta_json <subdir> <name>
  local subdir="$1" name="$2"
  local meta_path="$LOG_DIR/$subdir/$name.meta.json"
  local outcome="${OUTCOME_BY_NAME[$name]:-FAIL}"
  local kind="${KIND_BY_NAME[$name]:-skill}"
  local phase="${PHASE_BY_NAME[$name]:-cascade}"
  local duration="${DURATION_BY_NAME[$name]:-0}"
  local audit="${AUDIT_SCORE_BY_NAME[$name]:-}"
  local audit_after="${AUDIT_AFTER_FIXER_BY_NAME[$name]:-}"
  local fixer_inv="${FIXER_INVOKED_BY_NAME[$name]:-false}"
  local out_path="${OUTPUT_PATH_BY_NAME[$name]:-}"
  local err="${ERROR_BY_NAME[$name]:-}"

  # Convert bash boolean string to Python literal
  local fixer_inv_py="False"
  [[ "$fixer_inv" == "true" ]] && fixer_inv_py="True"

  NAME="$name" KIND="$kind" PHASE_LABEL="$phase" DURATION="$duration" \
  OUTCOME="$outcome" AUDIT="$audit" AUDIT_AFTER="$audit_after" \
  FIXER_INV_PY="$fixer_inv_py" OUT_PATH="$out_path" ERR="$err" \
  python3 - "$meta_path" <<'PY'
import json, os, sys
meta = {
  "schema_version": "1.0",
  "name": os.environ["NAME"],
  "kind": os.environ["KIND"],
  "phase": os.environ["PHASE_LABEL"],
  "duration_sec": float(os.environ["DURATION"]) if os.environ.get("DURATION") else 0,
  "outcome": os.environ["OUTCOME"],
  "audit_score": int(os.environ["AUDIT"]) if os.environ.get("AUDIT") else None,
  "audit_score_after_fixer": int(os.environ["AUDIT_AFTER"]) if os.environ.get("AUDIT_AFTER") else None,
  "fixer_invoked": os.environ["FIXER_INV_PY"] == "True",
  "output_path": os.environ.get("OUT_PATH") or None,
  "error": os.environ.get("ERR") or None,
}
with open(sys.argv[1], "w") as fh:
  json.dump(meta, fh, indent=2)
PY
}

# -----------------------------------------------------------------------------
# Mock-mode helpers
# -----------------------------------------------------------------------------
mock_replay_for() {
  # mock_replay_for <subdir> <name>
  # Returns 0 if mock data was found and replayed, 1 otherwise.
  [[ -z "$MOCK_SOURCE" ]] && return 1
  local subdir="$1" name="$2"
  local src="$MOCK_SOURCE/$subdir/$name.log"
  if [[ ! -f "$src" ]]; then
    log_warn "mock mode: no prior log at $src"
    return 1
  fi
  cp "$src" "$LOG_DIR/$subdir/$name.log"
  if [[ -f "$MOCK_SOURCE/$subdir/$name.meta.json" ]]; then
    cp "$MOCK_SOURCE/$subdir/$name.meta.json" "$LOG_DIR/$subdir/$name.meta.json"
  fi
  log_info "mock-replayed: $subdir/$name"
  return 0
}

# -----------------------------------------------------------------------------
# Phase 0 — Bootstrap & preflight
# -----------------------------------------------------------------------------
BOOTSTRAP_MODE="false"

phase_0_bootstrap() {
  section "Phase 0 — Bootstrap & preflight"

  # 0.1 Seed file presence
  if [[ ! -f "$SEED_FILE" ]]; then
    log_err "seed missing: $SEED_FILE"
    record_outcome "phase-0-seed" "fixture" "bootstrap" "FAIL" 0 "" "" "false" "" "seed file not found"
    return 1
  fi
  log_info "seed: $SEED_FILE"

  # 0.2 Manifest validate --strict
  if command -v claude >/dev/null 2>&1; then
    local out
    out="$(claude plugin validate "$PLUGIN_DIR" --strict 2>&1)"
    if [[ $? -eq 0 ]]; then
      log_info "manifest validate (--strict): PASS"
      record_outcome "manifest-validate-strict" "fixture" "bootstrap" "PASS" 0
      write_meta_json "bootstrap" "manifest-validate-strict"
    else
      log_err "manifest validate (--strict) failed:"
      printf '%s\n' "$out" | sed 's/^/  /'
      record_outcome "manifest-validate-strict" "fixture" "bootstrap" "FAIL" 0 "" "" "false" "" "manifest validate failed"
      return 1
    fi
  else
    log_warn "claude CLI not on PATH — skipping manifest validate"
    record_outcome "manifest-validate-strict" "fixture" "bootstrap" "SKIP" 0
  fi

  # 0.3 sdd_doc_lint smoke on existing docs/ (if non-empty)
  if [[ -d "$EXAMPLE_DOCS" ]] && [[ -n "$(find "$EXAMPLE_DOCS" -name '*.md' -print -quit 2>/dev/null)" ]]; then
    local lint_out
    lint_out="$(PYTHONPATH="$PLUGIN_DIR" python3 -m sdd_doc_lint "$EXAMPLE_DOCS" 2>&1)"
    if [[ $? -eq 0 ]]; then
      log_info "sdd_doc_lint smoke (existing docs/): PASS"
      record_outcome "lint-smoke" "fixture" "bootstrap" "PASS" 0
    else
      log_err "sdd_doc_lint smoke FAILED on existing docs/:"
      printf '%s\n' "$lint_out" | sed 's/^/  /'
      record_outcome "lint-smoke" "fixture" "bootstrap" "FAIL" 0 "" "" "false" "" "lint smoke failed"
      return 1
    fi
  else
    BOOTSTRAP_MODE="true"
    log_info "bootstrap mode: $EXAMPLE_DOCS is empty or missing"
    log_info "  → Phase 2 (CHG) will be skipped"
    log_info "  → Phases 3 + 4 utilities that need a chain will read from cascade/ instead"
    record_outcome "lint-smoke" "fixture" "bootstrap" "SKIP" 0
  fi

  # 0.4 Negative-fixture presence check
  if [[ "$PHASE" == "" ]] || [[ "$PHASE" == "negative" ]]; then
    if [[ ! -d "$NEGATIVE_FIXTURES_DIR" ]]; then
      log_warn "negative fixtures directory missing: $NEGATIVE_FIXTURES_DIR"
      log_warn "  → Phase 1.2 negative validation will be skipped (lands with Impl-2)"
      record_outcome "negative-fixtures-presence" "fixture" "bootstrap" "SKIP" 0
    else
      log_info "negative fixtures present at $NEGATIVE_FIXTURES_DIR"
      record_outcome "negative-fixtures-presence" "fixture" "bootstrap" "PASS" 0
    fi
  fi

  # 0.5 API auth check (live mode only).
  # The claude CLI can authenticate via either ANTHROPIC_API_KEY (headless CI)
  # or its own interactive login (local dev). Require the CLI present; require
  # at least one usable auth path.
  if [[ "$LIVE_FLAG" == "1" ]] && [[ -z "$MOCK_SOURCE" ]]; then
    if ! command -v claude >/dev/null 2>&1; then
      log_err "claude CLI not on PATH; required for --live mode"
      record_outcome "api-auth-check" "fixture" "bootstrap" "FAIL" 0 "" "" "false" "" "claude CLI missing"
      _write_bootstrap_metas
      return 1
    fi
    if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
      log_info "API auth check: ANTHROPIC_API_KEY set"
      record_outcome "api-auth-check" "fixture" "bootstrap" "PASS" 0
    elif claude -p "respond with the single word OK" 2>/dev/null | grep -qi 'OK'; then
      log_info "API auth check: claude CLI interactive login OK"
      record_outcome "api-auth-check" "fixture" "bootstrap" "PASS" 0
    else
      log_err "claude CLI returned non-OK on probe; ANTHROPIC_API_KEY unset and no interactive login"
      record_outcome "api-auth-check" "fixture" "bootstrap" "FAIL" 0 "" "" "false" "" "no usable auth path"
      _write_bootstrap_metas
      return 1
    fi
  else
    log_info "live mode disabled; skipping API auth check"
    record_outcome "api-auth-check" "fixture" "bootstrap" "SKIP" 0
  fi

  _write_bootstrap_metas
  return 0
}

# Write .meta.json files for all bootstrap-phase elements recorded so far.
# Called from phase_0_bootstrap on every exit path so summary.json captures
# bootstrap state alongside skill/agent invocations.
_write_bootstrap_metas() {
  local name
  for name in "${ELEMENT_ORDER[@]}"; do
    if [[ "${PHASE_BY_NAME[$name]:-}" == "bootstrap" ]]; then
      write_meta_json "bootstrap" "$name"
    fi
  done
}

# -----------------------------------------------------------------------------
# Phase 1.1 — Happy-path cascade
# -----------------------------------------------------------------------------
# Drives the seed through all 8 layers via doc-<layer>-autopilot. Each layer's
# output becomes the next layer's input. Audit + optional fixer + lint after
# each layer.

invoke_skill_live() {
  # invoke_skill_live <skill-name> <prompt> <output-log-path>
  # Returns 0 on success, non-zero on failure. Writes Claude's response to
  # the output-log-path.
  local skill="$1" prompt="$2" out_log="$3"
  claude \
    --plugin-dir "$PLUGIN_DIR" \
    --dangerously-skip-permissions \
    -p "/aidoc-flow:$skill $prompt" \
    > "$out_log" 2>&1
  return $?
}

invoke_skill() {
  # invoke_skill <skill-name> <prompt> <subdir> <kind> <phase>
  # Dispatches to mock or live based on $MOCK_SOURCE. Returns 0 on PASS.
  local skill="$1" prompt="$2" subdir="$3" kind="$4" phase_label="$5"
  local out_log="$LOG_DIR/$subdir/$skill.log"

  local t0 t1 duration
  t0="$(date +%s)"

  if [[ -n "$MOCK_SOURCE" ]]; then
    if mock_replay_for "$subdir" "$skill"; then
      t1="$(date +%s)"
      duration=$((t1 - t0))
      record_outcome "$skill" "$kind" "$phase_label" "PASS" "$duration"
      write_meta_json "$subdir" "$skill"
      return 0
    else
      t1="$(date +%s)"
      duration=$((t1 - t0))
      record_outcome "$skill" "$kind" "$phase_label" "SKIP" "$duration" "" "" "false" "" "no mock data"
      write_meta_json "$subdir" "$skill"
      return 1
    fi
  fi

  log_info "invoking /aidoc-flow:$skill"
  if invoke_skill_live "$skill" "$prompt" "$out_log"; then
    t1="$(date +%s)"
    duration=$((t1 - t0))
    record_outcome "$skill" "$kind" "$phase_label" "PASS" "$duration"
    write_meta_json "$subdir" "$skill"
    return 0
  else
    local rc=$?
    t1="$(date +%s)"
    duration=$((t1 - t0))
    log_err "$skill failed (exit $rc)"
    record_outcome "$skill" "$kind" "$phase_label" "FAIL" "$duration" "" "" "false" "" "claude -p exit $rc"
    write_meta_json "$subdir" "$skill"
    return 1
  fi
}

parse_audit_score() {
  # parse_audit_score <log-file>
  # Extracts an integer 0-100 from common audit-score patterns. Echoes the
  # score or 0 if not found.
  local log="$1"
  if [[ ! -f "$log" ]]; then
    echo "0"; return
  fi
  # Common patterns: "Score: 92", "Readiness: 87", "audit score: 95"
  local score
  score="$(grep -iE 'score|readiness' "$log" \
    | grep -oE '[0-9]+' \
    | head -1)"
  echo "${score:-0}"
}

phase_1_cascade() {
  section "Phase 1.1 — Happy-path cascade"

  if [[ "$LIVE_FLAG" != "1" ]] && [[ -z "$MOCK_SOURCE" ]]; then
    log_warn "cascade requires --live or --mock; skipping"
    for layer in "${LAYERS[@]}"; do
      record_outcome "doc-$layer-autopilot" "skill" "cascade" "SKIP" 0 "" "" "false" "" "live mode disabled"
      write_meta_json "skills" "doc-$layer-autopilot"
    done
    return 0
  fi

  local i=0 layer type prev_output
  prev_output="$SEED_FILE"

  for layer in "${LAYERS[@]}"; do
    type="${LAYER_TYPES[$i]}"
    local layer_num
    printf -v layer_num '%02d' $((i + 1))
    local out_dir="$LOG_DIR/cascade/${layer_num}_${type}"
    mkdir -p "$out_dir"
    local out_file="$out_dir/${type}-01.${EXAMPLE}.md"

    log_info ""
    log_info "── Layer $((i + 1))/8: $type ──"

    # autopilot
    local autopilot_prompt="From the seed/prior-layer document at $prev_output, produce the $type artifact for the $EXAMPLE example. Write the result to $out_file."
    invoke_skill "doc-$layer-autopilot" "$autopilot_prompt" "skills" "skill" "cascade" || {
      [[ $FAIL_FAST -eq 1 ]] && return 1
    }

    # audit
    local audit_prompt="Audit the $type artifact at $out_file. Report the readiness score."
    invoke_skill "doc-$layer-audit" "$audit_prompt" "skills" "skill" "cascade"
    local audit_log="$LOG_DIR/skills/doc-$layer-audit.log"
    local score
    score="$(parse_audit_score "$audit_log")"
    AUDIT_SCORE_BY_NAME["doc-$layer-audit"]="$score"
    log_info "  audit score: $score"

    # fixer if needed
    if (( score < 90 )); then
      log_info "  score < 90 → invoking fixer"
      local fixer_prompt="Fix the $type artifact at $out_file based on the audit findings in $audit_log."
      invoke_skill "doc-$layer-fixer" "$fixer_prompt" "skills" "skill" "cascade"
      FIXER_INVOKED_BY_NAME["doc-$layer-audit"]="true"

      # re-audit
      invoke_skill "doc-$layer-audit" "$audit_prompt" "skills" "skill" "cascade"
      score="$(parse_audit_score "$audit_log")"
      AUDIT_AFTER_FIXER_BY_NAME["doc-$layer-audit"]="$score"
      log_info "  audit score after fixer: $score"
    fi

    # sdd_doc_lint structural check
    if [[ -f "$out_file" ]]; then
      local lint_out
      lint_out="$(PYTHONPATH="$PLUGIN_DIR" python3 -m sdd_doc_lint "$out_dir" 2>&1)"
      local lint_rc=$?
      if [[ $lint_rc -eq 0 ]]; then
        log_info "  sdd_doc_lint: PASS"
      else
        log_err "  sdd_doc_lint FAIL:"
        printf '%s\n' "$lint_out" | sed 's/^/    /'
      fi
    else
      log_warn "  autopilot did not produce $out_file"
    fi

    # base skill cross-check (advisory)
    local base_prompt="Reference the $type template structure for $out_file."
    invoke_skill "doc-$layer" "$base_prompt" "skills" "skill" "cascade" || true

    prev_output="$out_file"
    i=$((i + 1))

    # Runtime guard
    local now_epoch elapsed
    now_epoch="$(date +%s)"
    elapsed=$((now_epoch - START_EPOCH))
    if (( elapsed > MAX_RUNTIME_SEC )); then
      log_err "Max runtime ${MAX_RUNTIME_SEC}s exceeded at layer $type; aborting"
      return 2
    fi
  done

  return 0
}

# -----------------------------------------------------------------------------
# Phase 1.2 — Negative-fixture validation
# -----------------------------------------------------------------------------
# Fixture format: <name>|<path>|<detector>|<expected-finding>
#   detector: "lint:<CODE>"     — deterministic; expect sdd_doc_lint to report <CODE>
#             "audit:<skill>"   — live LLM; expect skill output to contain the expected
#                                 finding pattern (regex)
#             "validator"       — live LLM doc-validator; expect "unresolved" in output
#
# Phase 1.2 logic:
#   for each fixture:
#     if detector starts with "lint:" → run sdd_doc_lint, assert code appears
#     if detector starts with "audit:" → invoke skill (or SKIP in --no-live)
#     if detector == "validator" → invoke doc-validator (or SKIP in --no-live)

NEGATIVE_FIXTURES=(
  "brd-broken-sections|brd-broken-sections.md|lint:STRUCT01"
  "brd-broken-tags|brd-broken-tags.md|lint:ID01"
  "prd-broken-upstream-ref|prd-broken-upstream-ref.md|validator"
  "ears-score-7|ears-score-7.md|audit:doc-ears-audit"
  "adr-missing-sequence-diagram|adr-missing-sequence-diagram.md|lint:STRUCT01"
  "chain-trace-broken|chain-trace-broken|validator"
)

assert_lint_finding() {
  # assert_lint_finding <fixture-path> <expected-code>
  # Returns 0 if expected code appears in the JSON output, 1 otherwise.
  local target="$1" expected="$2"
  local json_out
  json_out="$(PYTHONPATH="$PLUGIN_DIR" python3 -m sdd_doc_lint "$target" --format json 2>&1)"
  python3 - "$expected" <<PY
import json, sys
try:
    data = json.loads('''$json_out''')
except Exception:
    sys.exit(2)
codes = {f.get("code") for f in data}
sys.exit(0 if sys.argv[1] in codes else 1)
PY
}

phase_1_negative() {
  section "Phase 1.2 — Negative-fixture validation"

  if [[ ! -d "$NEGATIVE_FIXTURES_DIR" ]]; then
    log_warn "negative fixtures dir missing: $NEGATIVE_FIXTURES_DIR; skipping all"
    for entry in "${NEGATIVE_FIXTURES[@]}"; do
      local name="${entry%%|*}"
      record_outcome "neg:$name" "fixture" "negative" "SKIP" 0 "" "" "false" "" "fixtures dir missing"
      write_meta_json "skills" "neg:$name"
    done
    return 0
  fi

  local entry name rel detector
  for entry in "${NEGATIVE_FIXTURES[@]}"; do
    IFS='|' read -r name rel detector <<< "$entry"
    local fixture_path="$NEGATIVE_FIXTURES_DIR/$rel"

    if [[ ! -e "$fixture_path" ]]; then
      log_warn "fixture missing: $fixture_path"
      record_outcome "neg:$name" "fixture" "negative" "SKIP" 0 "" "" "false" "" "fixture not found"
      write_meta_json "skills" "neg:$name"
      continue
    fi

    log_info "── fixture: $name ($detector) ──"
    local t0 t1 duration
    t0="$(date +%s)"

    case "$detector" in
      lint:*)
        local expected_code="${detector#lint:}"
        if assert_lint_finding "$fixture_path" "$expected_code"; then
          t1="$(date +%s)"; duration=$((t1 - t0))
          log_info "  ✓ $expected_code reported as expected"
          record_outcome "neg:$name" "fixture" "negative" "PASS" "$duration"
        else
          t1="$(date +%s)"; duration=$((t1 - t0))
          log_err "  ✗ $expected_code NOT reported — regression in detection sensitivity"
          record_outcome "neg:$name" "fixture" "negative" "FAIL" "$duration" "" "" "false" "" "expected $expected_code not in lint output"
          [[ $FAIL_FAST -eq 1 ]] && return 1
        fi
        ;;
      audit:*)
        if [[ "$LIVE_FLAG" == "1" ]] || [[ -n "$MOCK_SOURCE" ]]; then
          local skill="${detector#audit:}"
          local audit_prompt="Audit the broken artifact at $fixture_path. Report findings and readiness score."
          invoke_skill "$skill" "$audit_prompt" "skills" "skill" "negative"
          local audit_log="$LOG_DIR/skills/$skill.log"
          local score
          score="$(parse_audit_score "$audit_log")"
          t1="$(date +%s)"; duration=$((t1 - t0))
          if (( score < 90 )); then
            log_info "  ✓ audit score $score < 90 (broken fixture flagged)"
            record_outcome "neg:$name" "fixture" "negative" "PASS" "$duration" "$score"
          else
            log_err "  ✗ audit score $score ≥ 90 (broken fixture NOT flagged)"
            record_outcome "neg:$name" "fixture" "negative" "FAIL" "$duration" "$score" "" "false" "" "broken fixture got audit score >= 90"
            [[ $FAIL_FAST -eq 1 ]] && return 1
          fi
        else
          t1="$(date +%s)"; duration=$((t1 - t0))
          log_info "  SKIP (audit-based check requires --live or --mock)"
          record_outcome "neg:$name" "fixture" "negative" "SKIP" "$duration" "" "" "false" "" "live mode disabled"
        fi
        ;;
      validator)
        if [[ "$LIVE_FLAG" == "1" ]] || [[ -n "$MOCK_SOURCE" ]]; then
          local val_prompt="Validate cross-doc references in $fixture_path. Report unresolved references."
          invoke_skill "doc-validator" "$val_prompt" "skills" "skill" "negative"
          local val_log="$LOG_DIR/skills/doc-validator.log"
          t1="$(date +%s)"; duration=$((t1 - t0))
          if [[ -f "$val_log" ]] && grep -qiE "unresolved|broken|not found|missing" "$val_log"; then
            log_info "  ✓ doc-validator reports unresolved/broken reference"
            record_outcome "neg:$name" "fixture" "negative" "PASS" "$duration"
          else
            log_err "  ✗ doc-validator did not flag the broken reference"
            record_outcome "neg:$name" "fixture" "negative" "FAIL" "$duration" "" "" "false" "" "doc-validator missed broken reference"
            [[ $FAIL_FAST -eq 1 ]] && return 1
          fi
        else
          t1="$(date +%s)"; duration=$((t1 - t0))
          log_info "  SKIP (validator-based check requires --live or --mock)"
          record_outcome "neg:$name" "fixture" "negative" "SKIP" "$duration" "" "" "false" "" "live mode disabled"
        fi
        ;;
      *)
        log_err "  unknown detector type: $detector"
        record_outcome "neg:$name" "fixture" "negative" "FAIL" 0 "" "" "false" "" "unknown detector type"
        ;;
    esac

    write_meta_json "skills" "neg:$name"
  done

  return 0
}

# -----------------------------------------------------------------------------
# Phase 2 — Change management
# -----------------------------------------------------------------------------
# Gated on: Phase 1 success + not bootstrap_mode. Applies the predefined
# change at examples/<NAME>/chg/test-change.md and drives the 4 CHG skills.

phase_2_chg() {
  section "Phase 2 — Change management"

  if [[ "$BOOTSTRAP_MODE" == "true" ]]; then
    log_info "bootstrap mode; Phase 2 skipped (no chain to mutate)"
    for skill in doc-chg doc-chg-autopilot doc-chg-audit doc-chg-fixer; do
      record_outcome "$skill" "skill" "chg" "SKIP" 0 "" "" "false" "" "bootstrap mode"
      write_meta_json "skills" "$skill"
    done
    return 0
  fi

  if [[ ! -f "$CHG_FILE" ]]; then
    log_err "CHG test-change file missing: $CHG_FILE"
    for skill in doc-chg doc-chg-autopilot doc-chg-audit doc-chg-fixer; do
      record_outcome "$skill" "skill" "chg" "FAIL" 0 "" "" "false" "" "chg/test-change.md missing"
      write_meta_json "skills" "$skill"
    done
    return 1
  fi

  if [[ "$LIVE_FLAG" != "1" ]] && [[ -z "$MOCK_SOURCE" ]]; then
    log_info "Phase 2 requires --live or --mock; recording SKIP for all 4 CHG skills"
    for skill in doc-chg doc-chg-autopilot doc-chg-audit doc-chg-fixer; do
      record_outcome "$skill" "skill" "chg" "SKIP" 0 "" "" "false" "" "live mode disabled"
      write_meta_json "skills" "$skill"
    done
    return 0
  fi

  log_info "Applying change request from $CHG_FILE"

  # doc-chg: register the change
  invoke_skill "doc-chg" "Register the change request described in $CHG_FILE against the existing chain at $EXAMPLE_DOCS." "skills" "skill" "chg"

  # doc-chg-autopilot: drive CHG-01 governance flow
  local chg_out_dir="$LOG_DIR/cascade/09_CHG"
  mkdir -p "$chg_out_dir"
  local chg_out="$chg_out_dir/CHG-01.${EXAMPLE}.md"
  invoke_skill "doc-chg-autopilot" "Drive the change request at $CHG_FILE through impact assessment, approval, and propagation. Write CHG-01 to $chg_out. The propagation report must enumerate each item in the 'Expected downstream impacts' section of $CHG_FILE." "skills" "skill" "chg"

  # doc-chg-audit: audit CHG-01
  invoke_skill "doc-chg-audit" "Audit the CHG-01 artifact at $chg_out. Verify it references each expected downstream impact from $CHG_FILE. Report readiness score." "skills" "skill" "chg"
  local chg_audit_log="$LOG_DIR/skills/doc-chg-audit.log"
  local chg_score
  chg_score="$(parse_audit_score "$chg_audit_log")"
  AUDIT_SCORE_BY_NAME["doc-chg-audit"]="$chg_score"
  log_info "CHG audit score: $chg_score"

  # doc-chg-fixer if score < 90
  if (( chg_score < 90 )); then
    log_info "CHG audit < 90 → invoking fixer"
    invoke_skill "doc-chg-fixer" "Fix CHG-01 at $chg_out based on audit findings in $chg_audit_log." "skills" "skill" "chg"
    FIXER_INVOKED_BY_NAME["doc-chg-audit"]="true"

    invoke_skill "doc-chg-audit" "Re-audit CHG-01 at $chg_out." "skills" "skill" "chg"
    chg_score="$(parse_audit_score "$chg_audit_log")"
    AUDIT_AFTER_FIXER_BY_NAME["doc-chg-audit"]="$chg_score"
    log_info "CHG audit score after fixer: $chg_score"
  else
    record_outcome "doc-chg-fixer" "skill" "chg" "SKIP" 0 "" "" "false" "" "fixer not needed (audit ≥ 90)"
    write_meta_json "skills" "doc-chg-fixer"
  fi

  return 0
}

# -----------------------------------------------------------------------------
# Phase 3 — Cross-cutting utilities (14 skills)
# -----------------------------------------------------------------------------
# Each utility has a minimum-coverage threshold (plan §7). Empty structured
# output counts as FAIL, not PASS.
#
# All 14 require --live or --mock; --no-live records SKIP for every probe.
#
# Path resolution: utilities operate against `examples/<NAME>/docs/` if
# present; in bootstrap mode they read from `logs/<TS>/cascade/` (the
# cascade just produced).

# Resolve which chain dir Phase 3 should target.
_resolve_chain_target() {
  if [[ "$BOOTSTRAP_MODE" == "true" ]]; then
    echo "$LOG_DIR/cascade"
  else
    echo "$EXAMPLE_DOCS"
  fi
}

# Count occurrences of a regex pattern in a file. Echoes the count.
_count_matches() {
  local pattern="$1" file="$2"
  if [[ ! -f "$file" ]]; then echo 0; return; fi
  grep -oiE "$pattern" "$file" 2>/dev/null | wc -l
}

# Generic threshold probe: invoke skill, count pattern occurrences in its
# output log, PASS if count ≥ threshold.
_probe_with_count_threshold() {
  # _probe_with_count_threshold <skill> <prompt> <pattern> <min-count> <description>
  local skill="$1" prompt="$2" pattern="$3" min="$4" desc="$5"

  if [[ "$LIVE_FLAG" != "1" ]] && [[ -z "$MOCK_SOURCE" ]]; then
    record_outcome "$skill" "skill" "utilities" "SKIP" 0 "" "" "false" "" "live mode disabled"
    write_meta_json "skills" "$skill"
    return 0
  fi

  invoke_skill "$skill" "$prompt" "skills" "skill" "utilities"
  local log_file="$LOG_DIR/skills/$skill.log"
  local count
  count="$(_count_matches "$pattern" "$log_file")"
  log_info "  $desc: counted $count match(es) (threshold ≥ $min)"

  if (( count >= min )); then
    OUTCOME_BY_NAME[$skill]="PASS"
    write_meta_json "skills" "$skill"
    return 0
  else
    OUTCOME_BY_NAME[$skill]="FAIL"
    ERROR_BY_NAME[$skill]="coverage threshold: counted $count, need $min"
    write_meta_json "skills" "$skill"
    [[ $FAIL_FAST -eq 1 ]] && return 1
    return 0
  fi
}

phase_3_utilities() {
  section "Phase 3 — Cross-cutting utilities (14 skills)"

  local chain_dir
  chain_dir="$(_resolve_chain_target)"

  if [[ ! -d "$chain_dir" ]] || [[ -z "$(find "$chain_dir" -name '*.md' -print -quit 2>/dev/null)" ]]; then
    log_warn "no chain found at $chain_dir; Phase 3 probes that need a chain will SKIP"
    # Continue — project-init runs against a tmp sandbox and doesn't need the chain.
  fi

  # Skip-all path for --no-live (no LLM available)
  if [[ "$LIVE_FLAG" != "1" ]] && [[ -z "$MOCK_SOURCE" ]]; then
    log_info "live mode disabled; recording SKIP for all 14 utility probes"
    for skill in doc-flow doc-validator doc-ref doc-naming gate-check \
                 quality-advisor security-audit review-team \
                 knowledge-extractor charts-flow adr-roadmap \
                 project-init project-adopt project-profile; do
      record_outcome "$skill" "skill" "utilities" "SKIP" 0 "" "" "false" "" "live mode disabled"
      write_meta_json "skills" "$skill"
    done
    return 0
  fi

  # 1. doc-flow — routing test ("given chain at layer N, what's next?")
  _probe_with_count_threshold "doc-flow" \
    "Scan the chain at $chain_dir and report which layer it currently rests at and what the next recommended skill is." \
    "next|layer|recommend" 1 "routing keywords"

  # 2. doc-validator — cumulative trace closure
  _probe_with_count_threshold "doc-validator" \
    "Validate cumulative @brd…@tdd traceability across the chain at $chain_dir. Enumerate every resolved tag." \
    "@(brd|prd|ears|bdd|adr|spec|tdd|iplan):" 50 "resolved trace tags"

  # 3. doc-ref — cross-reference resolution
  _probe_with_count_threshold "doc-ref" \
    "Resolve all cross-document references in $chain_dir. Enumerate each reference and target." \
    "(@(brd|prd|ears|bdd|adr|spec|tdd|iplan):|see |refer to)" 8 "cross-references"

  # 4. doc-naming — name compliance
  _probe_with_count_threshold "doc-naming" \
    "Check that every artifact ID in $chain_dir matches the standards in ID_NAMING_STANDARDS.md." \
    "[A-Z]+-[0-9]{2,}" 8 "compliant IDs"

  # 5. gate-check — readiness gate
  _probe_with_count_threshold "gate-check" \
    "Confirm every layer in $chain_dir has readiness score ≥ 90. Report per-layer scores." \
    "[0-9]{2,3}" 8 "per-layer scores"

  # 6. quality-advisor — improvement suggestions
  _probe_with_count_threshold "quality-advisor" \
    "Review the chain at $chain_dir and provide actionable improvement suggestions, one per layer at minimum." \
    "suggest|recommend|improve" 8 "actionable suggestions"

  # 7. security-audit — security review
  # Special case: pass if ≥1 finding OR explicit "no findings" block ≥ 100 words
  if [[ "$LIVE_FLAG" == "1" ]] || [[ -n "$MOCK_SOURCE" ]]; then
    invoke_skill "security-audit" \
      "Perform a security review of the chain at $chain_dir. Report findings with severity, or provide an explicit 'no findings' justification of at least 100 words." \
      "skills" "skill" "utilities"
    local sa_log="$LOG_DIR/skills/security-audit.log"
    local findings high
    findings="$(_count_matches '(severity|finding|risk):' "$sa_log")"
    high="$(_count_matches '(severity:[[:space:]]*high|critical)' "$sa_log")"
    local word_count
    word_count="$(wc -w < "$sa_log" 2>/dev/null || echo 0)"

    if (( findings > 0 )); then
      if (( high == 0 )); then
        log_info "  security-audit: $findings finding(s), 0 high-severity → PASS"
        OUTCOME_BY_NAME["security-audit"]="PASS"
      else
        log_err "  security-audit: $high high-severity finding(s) → FAIL"
        OUTCOME_BY_NAME["security-audit"]="FAIL"
        ERROR_BY_NAME["security-audit"]="high-severity findings"
      fi
    elif (( word_count >= 100 )); then
      log_info "  security-audit: no findings but justification ≥ 100 words → PASS"
      OUTCOME_BY_NAME["security-audit"]="PASS"
    else
      log_err "  security-audit: empty output (no findings + no justification) → FAIL"
      OUTCOME_BY_NAME["security-audit"]="FAIL"
      ERROR_BY_NAME["security-audit"]="empty output"
    fi
    write_meta_json "skills" "security-audit"
  fi

  # 8. review-team — multi-persona review (assert all configured personas present)
  if [[ "$LIVE_FLAG" == "1" ]] || [[ -n "$MOCK_SOURCE" ]]; then
    invoke_skill "review-team" \
      "Run the review-team crew against the chain at $chain_dir. Each configured persona in REVIEW_CREWS.yaml must produce non-empty output." \
      "skills" "skill" "utilities"
    local rt_log="$LOG_DIR/skills/review-team.log"
    # Get persona names from REVIEW_CREWS.yaml
    local missing=""
    if [[ -f "$FRAMEWORK/framework/governance/REVIEW_CREWS.yaml" ]]; then
      local personas
      personas="$(grep -oE 'persona:[[:space:]]*[a-z_]+' "$FRAMEWORK/framework/governance/REVIEW_CREWS.yaml" 2>/dev/null | awk '{print $NF}' | sort -u)"
      for p in $personas; do
        if ! grep -qi "$p" "$rt_log" 2>/dev/null; then
          missing="$missing $p"
        fi
      done
    fi
    if [[ -n "$missing" ]]; then
      log_err "  review-team: missing persona output for:$missing"
      OUTCOME_BY_NAME["review-team"]="FAIL"
      ERROR_BY_NAME["review-team"]="missing persona output for$missing"
    else
      log_info "  review-team: all configured personas present"
      OUTCOME_BY_NAME["review-team"]="PASS"
    fi
    write_meta_json "skills" "review-team"
  fi

  # 9. knowledge-extractor — graph with ≥20 nodes
  _probe_with_count_threshold "knowledge-extractor" \
    "Extract a domain knowledge graph from the chain at $chain_dir. List each node (entity) and its relationships." \
    "(node|entity|concept):" 20 "knowledge graph nodes"

  # 10. charts-flow — diagram contract per DIAGRAM_STANDARDS.md
  _probe_with_count_threshold "charts-flow" \
    "Validate diagram contract for the chain at $chain_dir. Each required diagram per DIAGRAM_STANDARDS.md must be present (BRD c4-l1+dfd-l1, PRD c4-l2+dfd-l2+sequence, ADR sequence, SPEC c4-l3+dfd-l3)." \
    "@diagram:[[:space:]]*(c4-l[123]|dfd-l[123]|sequence)" 8 "required diagram tags"

  # 11. adr-roadmap — 1:1 ADR coverage
  _probe_with_count_threshold "adr-roadmap" \
    "Aggregate every ADR in $chain_dir into a roadmap. Each ADR must appear in the roadmap exactly once." \
    "ADR-[0-9]{2,}" 1 "ADR references"

  # 12. project-init — scaffold in sandboxed tmp dir
  if [[ "$LIVE_FLAG" == "1" ]] || [[ -n "$MOCK_SOURCE" ]]; then
    local pi_sandbox="$LOG_DIR/sandbox/project-init"
    mkdir -p "$pi_sandbox"
    invoke_skill "project-init" \
      "Scaffold a new SDD project tree under $pi_sandbox. Produce the 8 layer directories (01_BRD..08_IPLAN) plus governance/ and registry/." \
      "skills" "skill" "utilities"
    # Count expected dirs
    local pi_layer_dirs pi_total
    pi_layer_dirs="$(find "$pi_sandbox" -maxdepth 2 -type d -name '0[1-8]_*' 2>/dev/null | wc -l)"
    pi_total="$(find "$pi_sandbox" -maxdepth 2 -type d 2>/dev/null | wc -l)"
    if (( pi_layer_dirs >= 8 )); then
      log_info "  project-init: $pi_layer_dirs/8 layer dirs produced, $pi_total total dirs"
      OUTCOME_BY_NAME["project-init"]="PASS"
    else
      log_err "  project-init: only $pi_layer_dirs/8 layer dirs produced"
      OUTCOME_BY_NAME["project-init"]="FAIL"
      ERROR_BY_NAME["project-init"]="only $pi_layer_dirs/8 layer dirs"
    fi
    write_meta_json "skills" "project-init"
  fi

  # 13. project-adopt — adopt existing tree, report ≥8 layers detected
  _probe_with_count_threshold "project-adopt" \
    "Adopt the existing project tree at $chain_dir. Report each detected layer." \
    "layer[[:space:]]*[0-9]|0[1-8]_(brd|prd|ears|bdd|adr|spec|tdd|iplan)" 8 "detected layers"

  # 14. project-profile — profile chain
  _probe_with_count_threshold "project-profile" \
    "Profile the chain at $chain_dir. Report plugin version, framework spec version, layer count, and overall readiness." \
    "(version|layer|readiness)" 3 "profile fields"

  return 0
}

# -----------------------------------------------------------------------------
# Phase 4 — Agents, command, hook (13 elements)
# -----------------------------------------------------------------------------
# Plan §8. Each invocation has a minimum-output threshold so empty-output
# passes are rejected. The hook is deterministic (synthetic JSON payload —
# no LLM cost); agents + command require --live or --mock.

# Agent table: <agent>|<target>|<task>|<min-output-words>
AGENTS=(
  "requirements-analyst|01_BRD|produce a structured requirements analysis|200"
  "pm-orchestrator|.|produce an orchestration plan referencing every layer (BRD..IPLAN)|150"
  "solutions-architect|06_SPEC|review the architecture; reference C4/DFD diagram tags|150"
  "test-architect|07_TDD|review the test strategy|100"
  "software-engineer|08_IPLAN|review the implementation plan|100"
  "devops-release-engineer|08_IPLAN|produce a deployment plan|100"
  "code-reviewer|08_IPLAN|review the code-block examples in the IPLAN|100"
  "security-engineer|.|produce a security review of the chain|100"
  "traceability-auditor|.|confirm every 4-segment element-ID resolves|100"
  "adversary|.|produce adversarial findings via the review-team crew|50"
  "synthesizer|.|produce a synthesis combining persona outputs via the review-team crew|50"
)

invoke_agent_live() {
  # invoke_agent_live <agent-name> <prompt> <output-log-path>
  # Asks Claude to delegate to the named agent. Returns exit code.
  local agent="$1" prompt="$2" out_log="$3"
  claude \
    --plugin-dir "$PLUGIN_DIR" \
    --dangerously-skip-permissions \
    -p "Use the $agent agent to: $prompt" \
    > "$out_log" 2>&1
  return $?
}

invoke_agent() {
  # invoke_agent <agent-name> <prompt> — dispatches mock vs live, records outcome.
  # Returns 0 on PASS.
  local agent="$1" prompt="$2"
  local out_log="$LOG_DIR/agents/$agent.log"

  local t0 t1 duration
  t0="$(date +%s)"

  if [[ -n "$MOCK_SOURCE" ]]; then
    if mock_replay_for "agents" "$agent"; then
      t1="$(date +%s)"; duration=$((t1 - t0))
      record_outcome "$agent" "agent" "agents" "PASS" "$duration"
      write_meta_json "agents" "$agent"
      return 0
    fi
    t1="$(date +%s)"; duration=$((t1 - t0))
    record_outcome "$agent" "agent" "agents" "SKIP" "$duration" "" "" "false" "" "no mock data"
    write_meta_json "agents" "$agent"
    return 1
  fi

  log_info "invoking agent: $agent"
  if invoke_agent_live "$agent" "$prompt" "$out_log"; then
    t1="$(date +%s)"; duration=$((t1 - t0))
    record_outcome "$agent" "agent" "agents" "PASS" "$duration"
    write_meta_json "agents" "$agent"
    return 0
  else
    local rc=$?
    t1="$(date +%s)"; duration=$((t1 - t0))
    log_err "agent $agent failed (exit $rc)"
    record_outcome "$agent" "agent" "agents" "FAIL" "$duration" "" "" "false" "" "claude -p exit $rc"
    write_meta_json "agents" "$agent"
    return 1
  fi
}

phase_4_agents() {
  section "Phase 4.1 — Agents (11)"

  local chain_dir
  chain_dir="$(_resolve_chain_target)"

  if [[ "$LIVE_FLAG" != "1" ]] && [[ -z "$MOCK_SOURCE" ]]; then
    log_info "live mode disabled; recording SKIP for all 11 agents"
    local entry agent
    for entry in "${AGENTS[@]}"; do
      agent="${entry%%|*}"
      record_outcome "$agent" "agent" "agents" "SKIP" 0 "" "" "false" "" "live mode disabled"
      write_meta_json "agents" "$agent"
    done
    return 0
  fi

  local entry agent target task min_words
  for entry in "${AGENTS[@]}"; do
    IFS='|' read -r agent target task min_words <<< "$entry"
    local target_path
    if [[ "$target" == "." ]]; then
      target_path="$chain_dir"
    else
      target_path="$chain_dir/$target"
    fi

    local prompt="Read $target_path and ${task}. Provide a structured response."
    invoke_agent "$agent" "$prompt"

    # Word-count threshold
    local agent_log="$LOG_DIR/agents/$agent.log"
    local words
    words="$(wc -w < "$agent_log" 2>/dev/null || echo 0)"
    if (( words < min_words )); then
      log_err "  $agent: only $words words (threshold ≥ $min_words) → FAIL"
      OUTCOME_BY_NAME[$agent]="FAIL"
      ERROR_BY_NAME[$agent]="output $words words < threshold $min_words"
      write_meta_json "agents" "$agent"
      [[ $FAIL_FAST -eq 1 ]] && return 1
    else
      log_info "  $agent: $words words (≥ $min_words) → PASS"
    fi
  done

  return 0
}

phase_4_command() {
  section "Phase 4.2 — Command (/aidoc-flow:save-plan)"

  if [[ "$LIVE_FLAG" != "1" ]] && [[ -z "$MOCK_SOURCE" ]]; then
    log_info "live mode disabled; SKIP"
    record_outcome "save-plan" "command" "command" "SKIP" 0 "" "" "false" "" "live mode disabled"
    write_meta_json "command" "save-plan"
    return 0
  fi

  local cmd_log="$LOG_DIR/command/save-plan.log"
  local cmd_sandbox="$LOG_DIR/sandbox/save-plan"
  mkdir -p "$cmd_sandbox"

  local t0 t1 duration
  t0="$(date +%s)"

  if [[ -n "$MOCK_SOURCE" ]]; then
    if mock_replay_for "command" "save-plan"; then
      t1="$(date +%s)"; duration=$((t1 - t0))
      record_outcome "save-plan" "command" "command" "PASS" "$duration"
      write_meta_json "command" "save-plan"
      return 0
    fi
  fi

  log_info "invoking /aidoc-flow:save-plan (sandbox: $cmd_sandbox)"
  ( cd "$cmd_sandbox" && \
    claude --plugin-dir "$PLUGIN_DIR" --dangerously-skip-permissions \
      -p "Draft a brief plan with two steps. Then invoke /aidoc-flow:save-plan to capture it to a file under plans/." \
      > "$cmd_log" 2>&1 )
  local rc=$?

  t1="$(date +%s)"; duration=$((t1 - t0))

  # Assert: a plan file was created under sandbox/plans/
  local plan_file
  plan_file="$(find "$cmd_sandbox/plans" -name '*.md' -print -quit 2>/dev/null)"
  if [[ $rc -eq 0 ]] && [[ -n "$plan_file" ]] && [[ -s "$plan_file" ]]; then
    log_info "  ✓ save-plan produced plan file at $plan_file"
    record_outcome "save-plan" "command" "command" "PASS" "$duration"
  else
    log_err "  ✗ save-plan did not produce a non-empty plan file under $cmd_sandbox/plans/"
    record_outcome "save-plan" "command" "command" "FAIL" "$duration" "" "" "false" "" "no plan file produced"
  fi
  write_meta_json "command" "save-plan"

  return 0
}

phase_4_hook() {
  section "Phase 4.3 — Hook (sdd-doc-review.sh)"

  local hook_path="$PLUGIN_DIR/hooks/sdd-doc-review.sh"
  local hook_cfg="$PLUGIN_DIR/hooks/hooks.json"
  local hook_log="$LOG_DIR/hook/sdd-doc-review.log"

  local t0 t1 duration
  t0="$(date +%s)"

  # 4.3.1 — hooks.json is valid JSON
  if ! python3 -m json.tool < "$hook_cfg" > /dev/null 2>&1; then
    log_err "  hooks.json is not valid JSON"
    record_outcome "sdd-doc-review" "hook" "hook" "FAIL" 0 "" "" "false" "" "hooks.json invalid"
    write_meta_json "hook" "sdd-doc-review"
    return 1
  fi

  # 4.3.2 — hooks.json references the correct event + matcher
  if ! grep -q '"PostToolUse"' "$hook_cfg" || \
     ! grep -q '"Write|Edit"' "$hook_cfg" || \
     ! grep -q 'sdd-doc-review.sh' "$hook_cfg"; then
    log_err "  hooks.json missing expected PostToolUse / Write|Edit / sdd-doc-review.sh references"
    record_outcome "sdd-doc-review" "hook" "hook" "FAIL" 0 "" "" "false" "" "hooks.json config mismatch"
    write_meta_json "hook" "sdd-doc-review"
    return 1
  fi
  log_info "  ✓ hooks.json valid; references PostToolUse + Write|Edit + sdd-doc-review.sh"

  # 4.3.3 — hook script exists and is executable
  if [[ ! -x "$hook_path" ]]; then
    log_err "  hook script missing or not executable: $hook_path"
    record_outcome "sdd-doc-review" "hook" "hook" "FAIL" 0 "" "" "false" "" "hook script not executable"
    write_meta_json "hook" "sdd-doc-review"
    return 1
  fi

  # 4.3.4 — synthetic invocation against a broken fixture.
  # The hook detects SDD instance documents by path pattern: either
  # `/docs/0N_<TYPE>/...` or a filename matching `<TYPE>-NN`. Our raw
  # fixture (`brd-broken-sections.md`) is named for human readability and
  # doesn't match either pattern. Stage it at an SDD-style path so the
  # hook's layer-detection logic fires.
  local fixture="$NEGATIVE_FIXTURES_DIR/brd-broken-sections.md"
  if [[ ! -f "$fixture" ]]; then
    log_warn "  brd-broken-sections fixture missing; cannot synthetically test hook"
    record_outcome "sdd-doc-review" "hook" "hook" "SKIP" 0 "" "" "false" "" "fixture missing"
    write_meta_json "hook" "sdd-doc-review"
    return 0
  fi

  if ! command -v jq >/dev/null 2>&1; then
    log_warn "  jq not on PATH; hook check skipped (hook itself degrades silently without jq)"
    record_outcome "sdd-doc-review" "hook" "hook" "SKIP" 0 "" "" "false" "" "jq missing"
    write_meta_json "hook" "sdd-doc-review"
    return 0
  fi

  local hook_sandbox="$LOG_DIR/sandbox/hook/docs/01_BRD"
  mkdir -p "$hook_sandbox"
  local staged="$hook_sandbox/BRD-01.md"
  cp "$fixture" "$staged"

  local payload
  payload="$(jq -n --arg path "$staged" '{tool_input: {file_path: $path}}')"
  local hook_out
  hook_out="$(printf '%s' "$payload" | bash "$hook_path" 2>&1)"
  local hook_rc=$?

  t1="$(date +%s)"; duration=$((t1 - t0))

  # Assert: exit 0 (advisory — must never block)
  if [[ $hook_rc -ne 0 ]]; then
    log_err "  hook exited $hook_rc (must be 0 — advisory only)"
    record_outcome "sdd-doc-review" "hook" "hook" "FAIL" "$duration" "" "" "false" "" "hook exit $hook_rc"
    write_meta_json "hook" "sdd-doc-review"
    return 1
  fi

  # Assert: valid JSON output
  if ! printf '%s' "$hook_out" | jq . > /dev/null 2>&1; then
    log_err "  hook output is not valid JSON"
    printf '%s' "$hook_out" > "$hook_log"
    record_outcome "sdd-doc-review" "hook" "hook" "FAIL" "$duration" "" "" "false" "" "hook output invalid JSON"
    write_meta_json "hook" "sdd-doc-review"
    return 1
  fi

  # Assert: contains BRD-layer audit nudge
  if ! printf '%s' "$hook_out" | grep -q "doc-brd-audit"; then
    log_err "  hook output missing doc-brd-audit nudge"
    printf '%s' "$hook_out" > "$hook_log"
    record_outcome "sdd-doc-review" "hook" "hook" "FAIL" "$duration" "" "" "false" "" "missing audit nudge"
    write_meta_json "hook" "sdd-doc-review"
    return 1
  fi

  # Assert: includes structural findings (fixture has STRUCT01)
  if ! printf '%s' "$hook_out" | grep -qiE "STRUCT01|structural findings"; then
    log_err "  hook output missing STRUCT01 / structural findings (fixture is known-broken)"
    printf '%s' "$hook_out" > "$hook_log"
    record_outcome "sdd-doc-review" "hook" "hook" "FAIL" "$duration" "" "" "false" "" "missing structural findings"
    write_meta_json "hook" "sdd-doc-review"
    return 1
  fi

  log_info "  ✓ hook exits 0, valid JSON, includes audit nudge + STRUCT01"
  printf '%s' "$hook_out" > "$hook_log"
  record_outcome "sdd-doc-review" "hook" "hook" "PASS" "$duration"
  write_meta_json "hook" "sdd-doc-review"
  return 0
}

# -----------------------------------------------------------------------------
# --promote algorithm
# -----------------------------------------------------------------------------
# Per plan §3.2. Promotes logs/<TS>/cascade/ to examples/<NAME>/docs/ when
# all phases passed.
#
# Steps:
#   1. Resolve version from platforms/claude-code-plugin/VERSION
#   2. Refuse if working tree has uncommitted changes
#   3. Refuse if examples/<NAME>/docs/ has uncommitted changes
#   4. Archive existing docs/ to docs-archive/v<previous-version>/ (if non-empty)
#   5. rsync -a --delete logs/<TS>/cascade/ → examples/<NAME>/docs/
#   6. Commit: chore(examples): promote <example> cascade for v<X.Y.Z>
#   7. Push only if --push was also passed

_overall_outcome() {
  # Echo PASS|FAIL|SKIP based on in-memory outcome state
  local name fail_n=0 pass_n=0
  for name in "${ELEMENT_ORDER[@]}"; do
    case "${OUTCOME_BY_NAME[$name]}" in
      PASS) pass_n=$((pass_n + 1)) ;;
      FAIL) fail_n=$((fail_n + 1)) ;;
    esac
  done
  if (( fail_n > 0 )); then
    echo "FAIL"
  elif (( pass_n == 0 )); then
    echo "SKIP"
  else
    echo "PASS"
  fi
}

promote_cascade() {
  section "Promote — cascade → examples/<NAME>/docs/"

  local outcome
  outcome="$(_overall_outcome)"
  if [[ "$outcome" != "PASS" ]]; then
    log_err "overall outcome is $outcome; refusing to promote a non-PASS run"
    return 1
  fi

  local cascade_src="$LOG_DIR/cascade"
  if [[ ! -d "$cascade_src" ]] || [[ -z "$(find "$cascade_src" -name '*.md' -print -quit 2>/dev/null)" ]]; then
    log_err "no cascade output to promote: $cascade_src"
    return 1
  fi

  # Step 1 — version
  local plugin_version_file="$PLUGIN_DIR/VERSION"
  if [[ ! -f "$plugin_version_file" ]]; then
    log_err "VERSION file missing: $plugin_version_file"
    return 1
  fi
  local plugin_version
  plugin_version="$(cat "$plugin_version_file" | tr -d '[:space:]')"
  log_info "plugin version: $plugin_version"

  # Step 2 — working tree clean
  if ! git -C "$FRAMEWORK" diff-index --quiet HEAD 2>/dev/null; then
    log_err "framework working tree has uncommitted changes; refusing to promote"
    log_err "  (commit or stash, then re-run with --promote)"
    return 1
  fi
  log_info "✓ working tree clean"

  # Step 3 — docs/ has no uncommitted changes (redundant with step 2 but explicit)
  if ! git -C "$FRAMEWORK" diff-index --quiet HEAD -- "examples/$EXAMPLE/docs" 2>/dev/null; then
    log_err "examples/$EXAMPLE/docs has uncommitted changes; refusing to promote"
    return 1
  fi

  # Step 4 — archive existing docs/ (if non-empty)
  local archive_root="$EXAMPLE_DIR/docs-archive"
  if [[ -d "$EXAMPLE_DOCS" ]] && [[ -n "$(find "$EXAMPLE_DOCS" -name '*.md' -print -quit 2>/dev/null)" ]]; then
    # Previous version: read the last committed VERSION at the time the
    # docs/ was promoted. For first-time we cannot know exactly, so use
    # the current plugin_version as the archive key — but only if it
    # differs from the run's version. If they match, skip archive (the
    # docs/ already represents this version's cascade).
    #
    # Heuristic: if a marker file exists at examples/<NAME>/docs/.version,
    # use it. Otherwise use plugin_version.
    local prev_version="$plugin_version"
    if [[ -f "$EXAMPLE_DOCS/.version" ]]; then
      prev_version="$(cat "$EXAMPLE_DOCS/.version" | tr -d '[:space:]')"
    fi
    local archive_dir="$archive_root/v$prev_version"
    if [[ -d "$archive_dir" ]]; then
      log_err "archive dir already exists: $archive_dir (refusing to overwrite history)"
      return 1
    fi
    mkdir -p "$archive_dir"
    log_info "archiving existing docs/ → $archive_dir"
    rsync -a "$EXAMPLE_DOCS/" "$archive_dir/"
  else
    log_info "first-time bootstrap: no existing docs/ to archive"
  fi

  # Step 5 — copy cascade into docs/
  log_info "promoting cascade → $EXAMPLE_DOCS"
  rm -rf "$EXAMPLE_DOCS"
  mkdir -p "$EXAMPLE_DOCS"
  rsync -a --delete "$cascade_src/" "$EXAMPLE_DOCS/"
  echo "$plugin_version" > "$EXAMPLE_DOCS/.version"

  # Step 6 — commit
  log_info "committing promoted chain"
  git -C "$FRAMEWORK" add "examples/$EXAMPLE/docs" "examples/$EXAMPLE/docs-archive" 2>/dev/null || true
  if git -C "$FRAMEWORK" diff --cached --quiet; then
    log_info "no changes to commit (promoted content identical to previous)"
  else
    git -C "$FRAMEWORK" commit -m "chore(examples): promote $EXAMPLE cascade for v$plugin_version release

Run: $LOG_TIMESTAMP
Outcome: $outcome
Source: $cascade_src" || {
      log_err "commit failed"
      return 1
    }
    log_info "✓ committed promoted chain"
  fi

  # Step 7 — push if requested
  if (( PUSH == 1 )); then
    log_info "pushing to origin"
    git -C "$FRAMEWORK" push || {
      log_err "push failed"
      return 1
    }
    log_info "✓ pushed"
  else
    log_info "skipping push (use --push to push)"
  fi

  return 0
}

# -----------------------------------------------------------------------------
# Summary writers
# -----------------------------------------------------------------------------
write_summary() {
  section "Writing summary"

  local pass_n=0 fail_n=0 skip_n=0
  local name
  for name in "${ELEMENT_ORDER[@]}"; do
    case "${OUTCOME_BY_NAME[$name]}" in
      PASS) pass_n=$((pass_n + 1)) ;;
      FAIL) fail_n=$((fail_n + 1)) ;;
      SKIP) skip_n=$((skip_n + 1)) ;;
    esac
  done

  local total=$((pass_n + fail_n + skip_n))
  local overall="PASS"
  if (( fail_n > 0 )); then
    overall="FAIL"
  elif (( pass_n == 0 )); then
    overall="SKIP"
  fi

  # Human-readable
  {
    echo "Acceptance run: $EXAMPLE @ $LOG_TIMESTAMP"
    echo "Outcome: $overall  ($pass_n PASS, $fail_n FAIL, $skip_n SKIP, $total total)"
    echo "Bootstrap mode: $BOOTSTRAP_MODE"
    echo "Live: $([[ $LIVE_FLAG == 1 ]] && echo true || echo false)"
    echo "Mock source: ${MOCK_SOURCE:-(none)}"
    echo
    printf '  %-50s %-6s %-10s %s\n' "Element" "Phase" "Outcome" "Notes"
    printf '  %-50s %-6s %-10s %s\n' "$(printf -- '-%.0s' {1..50})" "------" "----------" "----------------------"
    for name in "${ELEMENT_ORDER[@]}"; do
      local notes=""
      local audit="${AUDIT_SCORE_BY_NAME[$name]:-}"
      local audit_after="${AUDIT_AFTER_FIXER_BY_NAME[$name]:-}"
      if [[ -n "$audit_after" ]]; then
        notes="audit: $audit → $audit_after (after fixer)"
      elif [[ -n "$audit" ]]; then
        notes="audit: $audit"
      fi
      printf '  %-50s %-6s %-10s %s\n' \
        "$name" \
        "${PHASE_BY_NAME[$name]}" \
        "${OUTCOME_BY_NAME[$name]}" \
        "$notes"
    done
  } > "$SUMMARY_TXT"
  cat "$SUMMARY_TXT"

  # Machine-readable JSON — built by reading per-element .meta.json files
  python3 - "$LOG_DIR" "$SUMMARY_JSON" <<'PY'
import json, os, sys, glob, time
log_dir, out_path = sys.argv[1], sys.argv[2]
elements = []
for subdir in ("bootstrap", "skills", "agents", "command", "hook"):
    for meta_path in sorted(glob.glob(os.path.join(log_dir, subdir, "*.meta.json"))):
        try:
            with open(meta_path) as fh:
                elements.append(json.load(fh))
        except Exception as e:
            sys.stderr.write(f"warn: failed reading {meta_path}: {e}\n")
counts = {"PASS": 0, "FAIL": 0, "SKIP": 0}
for e in elements:
    counts[e.get("outcome", "SKIP")] = counts.get(e.get("outcome", "SKIP"), 0) + 1
overall = "PASS"
if counts["FAIL"] > 0:
    overall = "FAIL"
elif counts["PASS"] == 0:
    overall = "SKIP"

# Read VERSION files if present
def _read(path):
    try:
        with open(path) as fh:
            return fh.read().strip()
    except Exception:
        return None

framework = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(log_dir))))  # framework root
plugin_version = _read(os.path.join(framework, "platforms", "claude-code-plugin", "VERSION"))
spec_version = _read(os.path.join(framework, "framework", "VERSION"))

summary = {
    "schema_version": "1.0",
    "run_id": os.path.basename(log_dir),
    "example": os.path.basename(os.path.dirname(os.path.dirname(log_dir))),
    "plugin_version": plugin_version,
    "framework_spec_version": spec_version,
    "outcome": overall,
    "counts": counts,
    "elements": elements,
}
with open(out_path, "w") as fh:
    json.dump(summary, fh, indent=2)
print(f"wrote {out_path}: {len(elements)} elements, outcome={overall}")
PY

  echo
  echo "Logs: $LOG_DIR"
  echo "Summary: $SUMMARY_TXT"
  echo "Summary JSON: $SUMMARY_JSON"

  if [[ "$overall" == "FAIL" ]]; then
    return 1
  fi
  return 0
}

# -----------------------------------------------------------------------------
# Main dispatch
# -----------------------------------------------------------------------------
echo "aidoc-flow acceptance run"
echo "Example:    $EXAMPLE"
echo "Plan:       $EXAMPLE_DIR/ACCEPTANCE_TEST_PLAN.md"
echo "Log dir:    $LOG_DIR"
echo "Live:       $([[ $LIVE_FLAG == 1 ]] && echo enabled || echo disabled)"
echo "Mock:       ${MOCK_SOURCE:-(none)}"
echo "Phase:      ${PHASE:-all}"
echo "Element:    ${ELEMENT:-all}"
echo

# Phase 0 always runs
phase_0_bootstrap || {
  log_err "Phase 0 failure — aborting"
  write_summary
  exit 1
}

# Phase dispatch
# Default: cascade → negative → chg → utilities → agents → command → hook.
PHASES_TO_RUN=("cascade" "negative" "chg" "utilities" "agents" "command" "hook")
if [[ -n "$PHASE" ]]; then
  case "$PHASE" in
    bootstrap)  PHASES_TO_RUN=() ;;  # only Phase 0 ran
    cascade)    PHASES_TO_RUN=("cascade") ;;
    negative)   PHASES_TO_RUN=("negative") ;;
    chg)        PHASES_TO_RUN=("chg") ;;
    utilities)  PHASES_TO_RUN=("utilities") ;;
    agents)     PHASES_TO_RUN=("agents") ;;
    command)    PHASES_TO_RUN=("command") ;;
    hook)       PHASES_TO_RUN=("hook") ;;
    *) log_err "unknown phase: $PHASE"; exit 2 ;;
  esac
fi

for phase_name in "${PHASES_TO_RUN[@]}"; do
  case "$phase_name" in
    cascade)   phase_1_cascade ;;
    negative)  phase_1_negative ;;
    chg)       phase_2_chg ;;
    utilities) phase_3_utilities ;;
    agents)    phase_4_agents ;;
    command)   phase_4_command ;;
    hook)      phase_4_hook ;;
  esac
done

# Final summary
write_summary
RC=$?

# Promote (if requested and run passed)
if (( PROMOTE == 1 )); then
  if (( RC != 0 )); then
    log_err "--promote requested but overall run is FAIL; skipping promote"
  else
    promote_cascade || {
      log_err "promote failed"
      RC=1
    }
  fi
fi

# Cleanup: log final runtime
END_EPOCH="$(date +%s)"
log_info "Total runtime: $((END_EPOCH - START_EPOCH))s"

exit $RC
