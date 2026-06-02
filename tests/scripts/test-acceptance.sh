#!/usr/bin/env bash
#
# tests/scripts/test-acceptance.sh — Pre-deployment acceptance test driver.
#
# Drives every active element of the Claude Code plugin (50 skills + 11
# agents + 1 command + 1 hook = 63 elements) against a named example's
# seed. The chain produced is the release-gate evidence.
#
# Plan: examples/<NAME>/ACCEPTANCE_TEST_PLAN.md.
# Schema: tests/scripts/test-acceptance.schema.json (v1.1).
#
# Three-tier output separation per example:
#   examples/<NAME>/seed/, chg/   — human inputs (committed)
#   examples/<NAME>/docs/         — AI outputs, the produced chain (committed)
#   examples/<NAME>/.aidoc/       — AI working notes — provenance (committed)
#     ├── audit/<NN>_<LAYER>-audit.md       (per-layer audit reports)
#     ├── remediation/<NN>_<LAYER>-fix.md   (per-layer fix reports)
#     ├── review/<layer>-consensus.md       (review-team consensus)
#     ├── validation/<report>.md            (doc-validator/doc-ref/gate-check)
#     ├── security/review.md                (security-audit)
#     ├── quality/suggestions.md            (quality-advisor)
#     └── profile.yaml                      (project profile; bootstrap from default)
#   examples/<NAME>/logs/<TS>/    — tool internals (gitignored)
#     ├── plugin-test.log                   (driver flow trace only)
#     ├── summary.{txt,json}                (final outcome)
#     └── elements/<name>.log               (one file per element; YAML front-matter
#                                            + raw skill output)
#
# Usage:
#   bash tests/scripts/test-acceptance.sh <example-name> [flags]
#
#   Flags:
#     --no-live              skip live LLM calls (Phase 0 only effectively)
#     --live                 enable live LLM calls (default ON)
#     --phase=<name>         run one phase: bootstrap | cascade | negative |
#                            chg | utilities | agents | command | hook
#     --element=<name>       run one element only
#     --skip-completed       reuse prior run's PASS outcomes
#     --mock=<run-dir>       replay a prior recorded run; no Claude calls
#     --promote              git commit the produced docs/ and .aidoc/ changes
#     --push                 push the promote commit (only with --promote)
#     --force                bypass the "docs/ or .aidoc/ have unstaged
#                            changes" safety belt
#     --fail-fast            halt on first failure
#     -h | --help            show this usage block

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
DEFAULT_PROFILE_SRC="$FRAMEWORK/framework/governance/REVIEW_CREWS.yaml"

# Per-layer runtime cap (replaces the old global 45-min cap, plan B2).
MAX_LAYER_SEC=900   # 15 minutes per layer

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
FORCE=0
FAIL_FAST=0

usage() {
  sed -n '2,48p' "$0"
  exit "${1:-0}"
}

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
    --force)           FORCE=1 ;;
    --fail-fast)       FAIL_FAST=1 ;;
    -h|--help)         usage 0 ;;
    *) echo "ERROR: unknown flag: $arg" >&2; usage 2 ;;
  esac
done

if [[ -n "$MOCK_SOURCE" ]]; then
  LIVE_FLAG="0"
elif [[ -z "$LIVE_FLAG" ]]; then
  LIVE_FLAG="1"
fi

# -----------------------------------------------------------------------------
# Path resolution per example (the three-tier layout)
# -----------------------------------------------------------------------------
EXAMPLE_DIR="$FRAMEWORK/examples/$EXAMPLE"
if [[ ! -d "$EXAMPLE_DIR" ]]; then
  echo "ERROR: example directory does not exist: $EXAMPLE_DIR" >&2
  exit 2
fi

SEED_FILE="$EXAMPLE_DIR/seed/initial-requirements.md"
CHG_FILE="$EXAMPLE_DIR/chg/test-change.md"
EXAMPLE_DOCS="$EXAMPLE_DIR/docs"               # tier 2: AI outputs (committed)
AIDOC_DIR="$EXAMPLE_DIR/.aidoc"                # tier 3: AI working notes (committed)
PROFILE_FILE="$AIDOC_DIR/profile.yaml"         # the project profile (A11)

# Ephemeral execution logs (tier 4, gitignored)
LOG_DIR="$EXAMPLE_DIR/logs/$LOG_TIMESTAMP"
mkdir -p "$LOG_DIR/elements"
DRIVER_LOG="$LOG_DIR/plugin-test.log"
SUMMARY_TXT="$LOG_DIR/summary.txt"
SUMMARY_JSON="$LOG_DIR/summary.json"

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

# In-memory outcome tracking (keyed by element name)
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
  # record_outcome <name> <kind> <phase> <outcome> <duration> [<audit>] [<audit_after>] [<fixer_inv>] [<output_path>] [<error>]
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

# Write per-element file at logs/<TS>/elements/<name>.log with YAML
# front-matter (metadata) followed by the raw skill output if captured
# in $LOG_DIR/elements/<name>.stdout.
write_element_log() {
  # write_element_log <name>
  local name="$1"
  local log_path="$LOG_DIR/elements/$name.log"
  local stdout_path="$LOG_DIR/elements/$name.stdout"
  local outcome="${OUTCOME_BY_NAME[$name]:-FAIL}"
  local kind="${KIND_BY_NAME[$name]:-skill}"
  local phase="${PHASE_BY_NAME[$name]:-cascade}"
  local duration="${DURATION_BY_NAME[$name]:-0}"
  local audit="${AUDIT_SCORE_BY_NAME[$name]:-}"
  local audit_after="${AUDIT_AFTER_FIXER_BY_NAME[$name]:-}"
  local fixer_inv="${FIXER_INVOKED_BY_NAME[$name]:-false}"
  local out_path="${OUTPUT_PATH_BY_NAME[$name]:-}"
  local err="${ERROR_BY_NAME[$name]:-}"

  local fixer_inv_py="False"
  [[ "$fixer_inv" == "true" ]] && fixer_inv_py="True"

  NAME="$name" KIND="$kind" PHASE_LABEL="$phase" DURATION="$duration" \
  OUTCOME="$outcome" AUDIT="$audit" AUDIT_AFTER="$audit_after" \
  FIXER_INV_PY="$fixer_inv_py" OUT_PATH="$out_path" ERR="$err" \
  STDOUT_PATH="$stdout_path" LOG_PATH="$log_path" \
  python3 - <<'PY'
import json, os

meta = {
  "schema_version": "1.1",
  "name": os.environ["NAME"],
  "kind": os.environ["KIND"],
  "phase": os.environ["PHASE_LABEL"],
  "duration_sec": float(os.environ["DURATION"]) if os.environ.get("DURATION") else 0,
  "outcome": os.environ["OUTCOME"],
  "audit_score": int(os.environ["AUDIT"]) if os.environ.get("AUDIT") else None,
  "audit_score_after_fixer": int(os.environ["AUDIT_AFTER"]) if os.environ.get("AUDIT_AFTER") else None,
  "fixer_invoked": os.environ["FIXER_INV_PY"] == "True",
  "output_path": os.environ.get("OUT_PATH") or None,
  "tokens_in": None,
  "tokens_out": None,
  "error": os.environ.get("ERR") or None,
}

import yaml
front = yaml.safe_dump(meta, default_flow_style=False, sort_keys=False).strip()

stdout_path = os.environ["STDOUT_PATH"]
body = ""
if os.path.exists(stdout_path):
    with open(stdout_path) as fh:
        body = fh.read()

with open(os.environ["LOG_PATH"], "w") as fh:
    fh.write("---\n" + front + "\n---\n")
    if body:
        fh.write("\n" + body)
PY

  # Clean up the staging stdout file once merged into .log.
  rm -f "$stdout_path"
}

# -----------------------------------------------------------------------------
# Mock-mode helpers — replay a prior run's elements/ dir.
# -----------------------------------------------------------------------------
mock_replay_for() {
  # mock_replay_for <name>
  [[ -z "$MOCK_SOURCE" ]] && return 1
  local name="$1"
  local src="$MOCK_SOURCE/elements/$name.log"
  if [[ ! -f "$src" ]]; then
    log_warn "mock mode: no prior log at $src"
    return 1
  fi
  cp "$src" "$LOG_DIR/elements/$name.log"
  log_info "mock-replayed: $name"
  return 0
}

# -----------------------------------------------------------------------------
# Skill invocation — live mode, with output streamed line-by-line to a
# per-element stdout file. The final .log file is built from this stdout
# plus YAML front-matter by write_element_log().
# -----------------------------------------------------------------------------
invoke_skill_live() {
  # invoke_skill_live <skill-name> <prompt> <stdout-path>
  local skill="$1" prompt="$2" out_path="$3"
  claude \
    --plugin-dir "$PLUGIN_DIR" \
    --dangerously-skip-permissions \
    -p "/aidoc-flow:$skill $prompt" \
    > "$out_path" 2>&1
  return $?
}

invoke_skill() {
  # invoke_skill <name> <prompt> <kind> <phase>
  local name="$1" prompt="$2" kind="$3" phase_label="$4"
  local stdout_path="$LOG_DIR/elements/$name.stdout"

  local t0 t1 duration
  t0="$(date +%s)"

  if [[ -n "$MOCK_SOURCE" ]]; then
    if mock_replay_for "$name"; then
      t1="$(date +%s)"; duration=$((t1 - t0))
      record_outcome "$name" "$kind" "$phase_label" "PASS" "$duration"
      return 0
    fi
    t1="$(date +%s)"; duration=$((t1 - t0))
    record_outcome "$name" "$kind" "$phase_label" "SKIP" "$duration" "" "" "false" "" "no mock data"
    write_element_log "$name"
    return 1
  fi

  log_info "invoking /aidoc-flow:$name"
  if invoke_skill_live "$name" "$prompt" "$stdout_path"; then
    t1="$(date +%s)"; duration=$((t1 - t0))
    record_outcome "$name" "$kind" "$phase_label" "PASS" "$duration"
    write_element_log "$name"
    return 0
  else
    local rc=$?
    t1="$(date +%s)"; duration=$((t1 - t0))
    log_err "$name failed (exit $rc)"
    record_outcome "$name" "$kind" "$phase_label" "FAIL" "$duration" "" "" "false" "" "claude -p exit $rc"
    write_element_log "$name"
    return 1
  fi
}

parse_audit_score() {
  # parse_audit_score <name>
  # The skill output file for $name was already merged into .log by
  # write_element_log(); the body sits below the front-matter delimiter.
  local name="$1"
  local log="$LOG_DIR/elements/$name.log"
  [[ -f "$log" ]] || { echo "0"; return; }
  local score
  score="$(awk '/^---$/ {n++; next} n>=2' "$log" \
    | grep -iE 'score|readiness' \
    | grep -oE '[0-9]+' \
    | head -1)"
  echo "${score:-0}"
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
    write_element_log "phase-0-seed"
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
    else
      log_err "manifest validate (--strict) failed:"
      printf '%s\n' "$out" | sed 's/^/  /'
      record_outcome "manifest-validate-strict" "fixture" "bootstrap" "FAIL" 0 "" "" "false" "" "manifest validate failed"
      write_element_log "manifest-validate-strict"
      return 1
    fi
  else
    log_warn "claude CLI not on PATH — skipping manifest validate"
    record_outcome "manifest-validate-strict" "fixture" "bootstrap" "SKIP" 0
  fi

  # 0.3 Three-tier safety belt (A12)
  # Refuse to run cascade if docs/ or .aidoc/ have uncommitted changes,
  # unless --force is passed. Prevents accidental overwrite of in-progress
  # human edits.
  if [[ "$LIVE_FLAG" == "1" ]] && [[ -z "$MOCK_SOURCE" ]]; then
    local dirty=""
    if ! git -C "$FRAMEWORK" diff-index --quiet HEAD -- \
         "examples/$EXAMPLE/docs" "examples/$EXAMPLE/.aidoc" 2>/dev/null; then
      dirty=1
    fi
    if [[ -n "$dirty" ]] && [[ $FORCE -ne 1 ]]; then
      log_err "examples/$EXAMPLE/{docs,.aidoc}/ have unstaged changes."
      log_err "  Commit or stash first, OR pass --force to overwrite."
      record_outcome "tree-safety" "fixture" "bootstrap" "FAIL" 0 "" "" "false" "" "uncommitted changes; --force required"
      write_element_log "tree-safety"
      return 1
    elif [[ -n "$dirty" ]]; then
      log_warn "examples/$EXAMPLE/{docs,.aidoc}/ have unstaged changes; proceeding via --force"
      record_outcome "tree-safety" "fixture" "bootstrap" "PASS" 0 "" "" "false" "" "--force bypass"
    else
      log_info "working tree clean for docs/ + .aidoc/"
      record_outcome "tree-safety" "fixture" "bootstrap" "PASS" 0
    fi
  else
    record_outcome "tree-safety" "fixture" "bootstrap" "SKIP" 0
  fi

  # 0.4 Project profile bootstrap (A11)
  # If examples/<NAME>/.aidoc/profile.yaml exists, use it; if not, copy
  # the framework default. The suite never authors a new profile.
  mkdir -p "$AIDOC_DIR"
  if [[ -f "$PROFILE_FILE" ]]; then
    log_info "project profile: $PROFILE_FILE (existing)"
    record_outcome "profile-check" "fixture" "bootstrap" "PASS" 0
  elif [[ -f "$DEFAULT_PROFILE_SRC" ]]; then
    cp "$DEFAULT_PROFILE_SRC" "$PROFILE_FILE"
    log_info "project profile bootstrapped from framework default → $PROFILE_FILE"
    record_outcome "profile-check" "fixture" "bootstrap" "PASS" 0
  else
    log_err "no profile.yaml and no framework default at $DEFAULT_PROFILE_SRC"
    record_outcome "profile-check" "fixture" "bootstrap" "FAIL" 0 "" "" "false" "" "no profile available"
    write_element_log "profile-check"
    return 1
  fi

  # 0.5 sdd_doc_lint smoke on existing docs/ (B1 — lint individual files)
  if [[ -d "$EXAMPLE_DOCS" ]] && [[ -n "$(find "$EXAMPLE_DOCS" -name '*.md' -print -quit 2>/dev/null)" ]]; then
    local lint_out lint_rc
    lint_out="$(PYTHONPATH="$PLUGIN_DIR" python3 -m sdd_doc_lint "$EXAMPLE_DOCS" 2>&1)"; lint_rc=$?
    if [[ $lint_rc -eq 0 ]]; then
      log_info "sdd_doc_lint smoke (existing docs/): PASS"
      record_outcome "lint-smoke" "fixture" "bootstrap" "PASS" 0
    else
      log_err "sdd_doc_lint smoke FAILED on existing docs/:"
      printf '%s\n' "$lint_out" | sed 's/^/  /'
      record_outcome "lint-smoke" "fixture" "bootstrap" "FAIL" 0 "" "" "false" "" "lint smoke failed"
      _write_bootstrap_metas
      return 1
    fi
  else
    BOOTSTRAP_MODE="true"
    log_info "bootstrap mode: $EXAMPLE_DOCS is empty or missing"
    log_info "  → Phase 2 (CHG) will be skipped"
    record_outcome "lint-smoke" "fixture" "bootstrap" "SKIP" 0
  fi

  # 0.6 Negative-fixture presence check
  if [[ -z "$PHASE" ]] || [[ "$PHASE" == "negative" ]]; then
    if [[ ! -d "$NEGATIVE_FIXTURES_DIR" ]]; then
      log_warn "negative fixtures directory missing: $NEGATIVE_FIXTURES_DIR"
      record_outcome "negative-fixtures-presence" "fixture" "bootstrap" "SKIP" 0
    else
      log_info "negative fixtures present at $NEGATIVE_FIXTURES_DIR"
      record_outcome "negative-fixtures-presence" "fixture" "bootstrap" "PASS" 0
    fi
  fi

  # 0.7 API auth check
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

_write_bootstrap_metas() {
  local name
  for name in "${ELEMENT_ORDER[@]}"; do
    if [[ "${PHASE_BY_NAME[$name]:-}" == "bootstrap" ]]; then
      write_element_log "$name"
    fi
  done
}

# -----------------------------------------------------------------------------
# Phase 1.1 — Happy-path cascade (writes to docs/ + .aidoc/ directly, A1+A2)
# -----------------------------------------------------------------------------
phase_1_cascade() {
  section "Phase 1.1 — Happy-path cascade"

  if [[ "$LIVE_FLAG" != "1" ]] && [[ -z "$MOCK_SOURCE" ]]; then
    log_warn "cascade requires --live or --mock; skipping"
    for layer in "${LAYERS[@]}"; do
      record_outcome "doc-$layer-autopilot" "skill" "cascade" "SKIP" 0 "" "" "false" "" "live mode disabled"
      write_element_log "doc-$layer-autopilot"
    done
    return 0
  fi

  mkdir -p "$EXAMPLE_DOCS" "$AIDOC_DIR/audit" "$AIDOC_DIR/remediation"

  local i=0 layer type prev_output
  prev_output="$SEED_FILE"

  for layer in "${LAYERS[@]}"; do
    type="${LAYER_TYPES[$i]}"
    local layer_num
    printf -v layer_num '%02d' $((i + 1))
    local layer_dir="$EXAMPLE_DOCS/${layer_num}_${type}"
    mkdir -p "$layer_dir"
    local artifact="$layer_dir/${type}-01.md"
    local audit_report="$AIDOC_DIR/audit/${layer_num}_${type}-audit.md"
    local fix_report="$AIDOC_DIR/remediation/${layer_num}_${type}-fix.md"
    local layer_start_epoch
    layer_start_epoch="$(date +%s)"

    log_info ""
    log_info "── Layer $((i + 1))/8: $type ──"

    # autopilot — writes the layer artifact under docs/
    local autopilot_prompt
    autopilot_prompt="From the seed/prior-layer document at $prev_output, produce the $type artifact for the $EXAMPLE example. Write the result to $artifact."
    invoke_skill "doc-$layer-autopilot" "$autopilot_prompt" "skill" "cascade"
    OUTPUT_PATH_BY_NAME["doc-$layer-autopilot"]="$artifact"
    if [[ "${OUTCOME_BY_NAME[doc-$layer-autopilot]:-}" == "PASS" ]]; then
      write_element_log "doc-$layer-autopilot"
    fi
    if [[ "${OUTCOME_BY_NAME[doc-$layer-autopilot]:-}" != "PASS" ]] && [[ $FAIL_FAST -eq 1 ]]; then
      return 1
    fi

    # audit — writes audit report under .aidoc/audit/
    local audit_prompt
    audit_prompt="Audit the $type artifact at $artifact. Write a detailed audit report to $audit_report including the readiness score."
    invoke_skill "doc-$layer-audit" "$audit_prompt" "skill" "cascade"
    OUTPUT_PATH_BY_NAME["doc-$layer-audit"]="$audit_report"
    local score
    score="$(parse_audit_score "doc-$layer-audit")"
    AUDIT_SCORE_BY_NAME["doc-$layer-audit"]="$score"
    write_element_log "doc-$layer-audit"
    log_info "  audit score: $score"

    # fixer + re-audit if needed
    if (( score < 90 )); then
      log_info "  score < 90 → invoking fixer"
      local fixer_prompt
      fixer_prompt="Fix the $type artifact at $artifact based on findings in $audit_report. Write a fix report to $fix_report."
      invoke_skill "doc-$layer-fixer" "$fixer_prompt" "skill" "cascade"
      OUTPUT_PATH_BY_NAME["doc-$layer-fixer"]="$fix_report"
      FIXER_INVOKED_BY_NAME["doc-$layer-audit"]="true"
      write_element_log "doc-$layer-fixer"

      invoke_skill "doc-$layer-audit" "$audit_prompt" "skill" "cascade"
      score="$(parse_audit_score "doc-$layer-audit")"
      AUDIT_AFTER_FIXER_BY_NAME["doc-$layer-audit"]="$score"
      write_element_log "doc-$layer-audit"
      log_info "  audit score after fixer: $score"
    fi

    # sdd_doc_lint structural check on the artifact only (B1)
    if [[ -f "$artifact" ]]; then
      local lint_out lint_rc
      lint_out="$(PYTHONPATH="$PLUGIN_DIR" python3 -m sdd_doc_lint "$artifact" 2>&1)"; lint_rc=$?
      if [[ $lint_rc -eq 0 ]]; then
        log_info "  sdd_doc_lint: PASS"
      else
        log_err "  sdd_doc_lint FAIL on $artifact:"
        printf '%s\n' "$lint_out" | sed 's/^/    /'
      fi
    else
      log_warn "  autopilot did not produce $artifact"
    fi

    # base/reference skill — output captured to logs/<TS>/elements/
    invoke_skill "doc-$layer" "Reference the $type template structure for $artifact." "skill" "cascade" || true

    prev_output="$artifact"
    i=$((i + 1))

    # Per-layer runtime cap (B2)
    local layer_elapsed
    layer_elapsed=$(( $(date +%s) - layer_start_epoch ))
    if (( layer_elapsed > MAX_LAYER_SEC )); then
      log_err "Layer $type took ${layer_elapsed}s > ${MAX_LAYER_SEC}s cap; aborting cascade"
      return 2
    fi
  done

  return 0
}

# -----------------------------------------------------------------------------
# Phase 1.2 — Negative-fixture validation (unchanged behavior, new file paths)
# -----------------------------------------------------------------------------
NEGATIVE_FIXTURES=(
  "brd-broken-sections|brd-broken-sections.md|lint:STRUCT01"
  "brd-broken-tags|brd-broken-tags.md|lint:ID01"
  "prd-broken-upstream-ref|prd-broken-upstream-ref.md|validator"
  "ears-score-7|ears-score-7.md|audit:doc-ears-audit"
  "adr-missing-sequence-diagram|adr-missing-sequence-diagram.md|lint:STRUCT01"
  "chain-trace-broken|chain-trace-broken|validator"
)

assert_lint_finding() {
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
    log_warn "negative fixtures dir missing; skipping all"
    for entry in "${NEGATIVE_FIXTURES[@]}"; do
      local name="${entry%%|*}"
      record_outcome "neg:$name" "fixture" "negative" "SKIP" 0 "" "" "false" "" "fixtures dir missing"
      write_element_log "neg:$name"
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
      write_element_log "neg:$name"
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
          log_err "  ✗ $expected_code NOT reported"
          record_outcome "neg:$name" "fixture" "negative" "FAIL" "$duration" "" "" "false" "" "expected $expected_code not in lint output"
          [[ $FAIL_FAST -eq 1 ]] && return 1
        fi
        ;;
      audit:*)
        if [[ "$LIVE_FLAG" == "1" ]] || [[ -n "$MOCK_SOURCE" ]]; then
          local skill="${detector#audit:}"
          local audit_prompt="Audit the broken artifact at $fixture_path. Report findings and readiness score."
          invoke_skill "$skill" "$audit_prompt" "skill" "negative"
          local score; score="$(parse_audit_score "$skill")"
          t1="$(date +%s)"; duration=$((t1 - t0))
          if (( score < 90 )); then
            log_info "  ✓ audit score $score < 90 (broken fixture flagged)"
            record_outcome "neg:$name" "fixture" "negative" "PASS" "$duration" "$score"
          else
            log_err "  ✗ audit score $score ≥ 90"
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
          invoke_skill "doc-validator" "$val_prompt" "skill" "negative"
          local val_log="$LOG_DIR/elements/doc-validator.log"
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

    write_element_log "neg:$name"
  done

  return 0
}

# -----------------------------------------------------------------------------
# Phase 2 — Change management
# -----------------------------------------------------------------------------
phase_2_chg() {
  section "Phase 2 — Change management"

  if [[ "$BOOTSTRAP_MODE" == "true" ]]; then
    log_info "bootstrap mode; Phase 2 skipped (no chain to mutate)"
    for skill in doc-chg doc-chg-autopilot doc-chg-audit doc-chg-fixer; do
      record_outcome "$skill" "skill" "chg" "SKIP" 0 "" "" "false" "" "bootstrap mode"
      write_element_log "$skill"
    done
    return 0
  fi

  if [[ ! -f "$CHG_FILE" ]]; then
    log_err "CHG test-change file missing: $CHG_FILE"
    for skill in doc-chg doc-chg-autopilot doc-chg-audit doc-chg-fixer; do
      record_outcome "$skill" "skill" "chg" "FAIL" 0 "" "" "false" "" "chg/test-change.md missing"
      write_element_log "$skill"
    done
    return 1
  fi

  if [[ "$LIVE_FLAG" != "1" ]] && [[ -z "$MOCK_SOURCE" ]]; then
    log_info "Phase 2 requires --live or --mock; SKIP"
    for skill in doc-chg doc-chg-autopilot doc-chg-audit doc-chg-fixer; do
      record_outcome "$skill" "skill" "chg" "SKIP" 0 "" "" "false" "" "live mode disabled"
      write_element_log "$skill"
    done
    return 0
  fi

  log_info "Applying change request from $CHG_FILE"

  mkdir -p "$EXAMPLE_DOCS/09_CHG"
  local chg_artifact="$EXAMPLE_DOCS/09_CHG/CHG-01.md"
  local chg_audit_report="$AIDOC_DIR/audit/09_CHG-audit.md"
  local chg_fix_report="$AIDOC_DIR/remediation/09_CHG-fix.md"

  invoke_skill "doc-chg" "Register the change request described in $CHG_FILE against the chain at $EXAMPLE_DOCS." "skill" "chg"
  write_element_log "doc-chg"

  invoke_skill "doc-chg-autopilot" "Drive the change request at $CHG_FILE through impact assessment, approval, and propagation. Write CHG-01 to $chg_artifact. The propagation report must enumerate each item in the 'Expected downstream impacts' section of $CHG_FILE." "skill" "chg"
  OUTPUT_PATH_BY_NAME["doc-chg-autopilot"]="$chg_artifact"
  write_element_log "doc-chg-autopilot"

  invoke_skill "doc-chg-audit" "Audit the CHG-01 artifact at $chg_artifact. Write the audit report to $chg_audit_report. Report readiness score." "skill" "chg"
  OUTPUT_PATH_BY_NAME["doc-chg-audit"]="$chg_audit_report"
  local chg_score; chg_score="$(parse_audit_score "doc-chg-audit")"
  AUDIT_SCORE_BY_NAME["doc-chg-audit"]="$chg_score"
  write_element_log "doc-chg-audit"
  log_info "CHG audit score: $chg_score"

  if (( chg_score < 90 )); then
    log_info "CHG audit < 90 → invoking fixer"
    invoke_skill "doc-chg-fixer" "Fix CHG-01 at $chg_artifact based on audit findings at $chg_audit_report. Write a fix report to $chg_fix_report." "skill" "chg"
    OUTPUT_PATH_BY_NAME["doc-chg-fixer"]="$chg_fix_report"
    FIXER_INVOKED_BY_NAME["doc-chg-audit"]="true"
    write_element_log "doc-chg-fixer"

    invoke_skill "doc-chg-audit" "Re-audit CHG-01 at $chg_artifact." "skill" "chg"
    chg_score="$(parse_audit_score "doc-chg-audit")"
    AUDIT_AFTER_FIXER_BY_NAME["doc-chg-audit"]="$chg_score"
    write_element_log "doc-chg-audit"
    log_info "CHG audit score after fixer: $chg_score"
  else
    record_outcome "doc-chg-fixer" "skill" "chg" "SKIP" 0 "" "" "false" "" "fixer not needed (audit ≥ 90)"
    write_element_log "doc-chg-fixer"
  fi

  return 0
}

# -----------------------------------------------------------------------------
# Phase 3 — Cross-cutting utilities (output routed to .aidoc/<category>/)
# -----------------------------------------------------------------------------
_resolve_chain_target() {
  echo "$EXAMPLE_DOCS"
}

_count_matches() {
  local pattern="$1" file="$2"
  if [[ ! -f "$file" ]]; then echo 0; return; fi
  grep -oiE "$pattern" "$file" 2>/dev/null | wc -l
}

_probe_with_count_threshold() {
  local skill="$1" prompt="$2" pattern="$3" min="$4" desc="$5"

  if [[ "$LIVE_FLAG" != "1" ]] && [[ -z "$MOCK_SOURCE" ]]; then
    record_outcome "$skill" "skill" "utilities" "SKIP" 0 "" "" "false" "" "live mode disabled"
    write_element_log "$skill"
    return 0
  fi

  invoke_skill "$skill" "$prompt" "skill" "utilities"
  local log_file="$LOG_DIR/elements/$skill.log"
  local count
  count="$(_count_matches "$pattern" "$log_file")"
  log_info "  $desc: counted $count match(es) (threshold ≥ $min)"

  if (( count >= min )); then
    OUTCOME_BY_NAME[$skill]="PASS"
  else
    OUTCOME_BY_NAME[$skill]="FAIL"
    ERROR_BY_NAME[$skill]="coverage threshold: counted $count, need $min"
    [[ $FAIL_FAST -eq 1 ]] && return 1
  fi
  write_element_log "$skill"
  return 0
}

phase_3_utilities() {
  section "Phase 3 — Cross-cutting utilities (14 skills)"

  local chain_dir
  chain_dir="$(_resolve_chain_target)"

  if [[ "$LIVE_FLAG" != "1" ]] && [[ -z "$MOCK_SOURCE" ]]; then
    log_info "live mode disabled; recording SKIP for all 14 utility probes"
    for skill in doc-flow doc-validator doc-ref doc-naming gate-check \
                 quality-advisor security-audit review-team \
                 knowledge-extractor charts-flow adr-roadmap \
                 project-init project-adopt project-profile; do
      record_outcome "$skill" "skill" "utilities" "SKIP" 0 "" "" "false" "" "live mode disabled"
      write_element_log "$skill"
    done
    return 0
  fi

  mkdir -p "$AIDOC_DIR/validation" "$AIDOC_DIR/security" "$AIDOC_DIR/quality" "$AIDOC_DIR/review"
  local val_path="$AIDOC_DIR/validation"
  local sec_path="$AIDOC_DIR/security/review.md"
  local qa_path="$AIDOC_DIR/quality/suggestions.md"
  local rt_path="$AIDOC_DIR/review"

  _probe_with_count_threshold "doc-flow" \
    "Scan the chain at $chain_dir and report which layer it currently rests at and what the next recommended skill is." \
    "next|layer|recommend" 1 "routing keywords"

  _probe_with_count_threshold "doc-validator" \
    "Validate cumulative @brd…@tdd traceability across the chain at $chain_dir. Write the trace-closure report to $val_path/traceability.md. Enumerate every resolved tag." \
    "@(brd|prd|ears|bdd|adr|spec|tdd|iplan):" 20 "resolved trace tags"

  _probe_with_count_threshold "doc-ref" \
    "Resolve all cross-document references in $chain_dir. Write the reference resolution report to $val_path/cross-references.md." \
    "(@(brd|prd|ears|bdd|adr|spec|tdd|iplan):|see |refer to)" 8 "cross-references"

  _probe_with_count_threshold "doc-naming" \
    "Check that every artifact ID in $chain_dir matches the standards in ID_NAMING_STANDARDS.md. Write the report to $val_path/naming.md." \
    "[A-Z]+-[0-9]{2,}" 8 "compliant IDs"

  _probe_with_count_threshold "gate-check" \
    "Confirm every layer in $chain_dir has readiness score ≥ 90. Write the gate-check report to $val_path/gate-check.md." \
    "[0-9]{2,3}" 8 "per-layer scores"

  _probe_with_count_threshold "quality-advisor" \
    "Review the chain at $chain_dir and provide actionable improvement suggestions, one per layer at minimum. Write suggestions to $qa_path." \
    "suggest|recommend|improve" 8 "actionable suggestions"

  if [[ "$LIVE_FLAG" == "1" ]] || [[ -n "$MOCK_SOURCE" ]]; then
    invoke_skill "security-audit" \
      "Perform a security review of the chain at $chain_dir. Write the report to $sec_path. Either ≥1 finding with severity (no high-severity), or an explicit 'no findings' justification of at least 100 words." \
      "skill" "utilities"
    local sa_log="$LOG_DIR/elements/security-audit.log"
    local findings high words
    findings="$(_count_matches '(severity|finding|risk):' "$sa_log")"
    high="$(_count_matches '(severity:[[:space:]]*high|critical)' "$sa_log")"
    words="$(wc -w < "$sa_log" 2>/dev/null || echo 0)"
    if (( findings > 0 )); then
      if (( high == 0 )); then
        OUTCOME_BY_NAME["security-audit"]="PASS"
      else
        OUTCOME_BY_NAME["security-audit"]="FAIL"
        ERROR_BY_NAME["security-audit"]="high-severity findings"
      fi
    elif (( words >= 100 )); then
      OUTCOME_BY_NAME["security-audit"]="PASS"
    else
      OUTCOME_BY_NAME["security-audit"]="FAIL"
      ERROR_BY_NAME["security-audit"]="empty output"
    fi
    OUTPUT_PATH_BY_NAME["security-audit"]="$sec_path"
    write_element_log "security-audit"
  fi

  if [[ "$LIVE_FLAG" == "1" ]] || [[ -n "$MOCK_SOURCE" ]]; then
    invoke_skill "review-team" \
      "Run the review-team crew against the chain at $chain_dir. For each layer, write per-layer consensus reports under $rt_path/<layer>-consensus.md. Each configured persona in $PROFILE_FILE must produce non-empty output." \
      "skill" "utilities"
    local rt_log="$LOG_DIR/elements/review-team.log"
    # Personas via Python YAML parse (B3 fix).
    local personas
    personas="$(PROFILE="$PROFILE_FILE" python3 - <<'PY'
import os, yaml
try:
    with open(os.environ["PROFILE"]) as f:
        data = yaml.safe_load(f) or {}
except Exception:
    print("")
    raise SystemExit(0)
personas = set()
def collect(node):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "persona" and isinstance(v, str):
                personas.add(v)
            else:
                collect(v)
    elif isinstance(node, list):
        for item in node:
            collect(item)
collect(data)
print(" ".join(sorted(personas)))
PY
)"
    local missing=""
    for p in $personas; do
      if ! grep -qi "$p" "$rt_log" 2>/dev/null; then
        missing="$missing $p"
      fi
    done
    if [[ -n "$missing" ]]; then
      OUTCOME_BY_NAME["review-team"]="FAIL"
      ERROR_BY_NAME["review-team"]="missing persona output for:$missing"
    else
      OUTCOME_BY_NAME["review-team"]="PASS"
    fi
    OUTPUT_PATH_BY_NAME["review-team"]="$rt_path"
    write_element_log "review-team"
  fi

  local n_layers
  n_layers="$(ls -1d "$chain_dir"/[0-9]*_*/ 2>/dev/null | wc -l)"
  local ke_min=$(( n_layers > 0 ? n_layers * 4 : 8 ))

  _probe_with_count_threshold "knowledge-extractor" \
    "Extract a domain knowledge graph from the chain at $chain_dir. Write to $val_path/knowledge-graph.md. List each node (entity) and its relationships." \
    "(node|entity|concept|::|->|--)" $ke_min "knowledge graph nodes"

  _probe_with_count_threshold "charts-flow" \
    "Validate diagram contract for the chain at $chain_dir. Each required diagram per DIAGRAM_STANDARDS.md must be present. Write the report to $val_path/diagrams.md." \
    "@diagram:[[:space:]]*(c4-l[123]|dfd-l[123]|sequence)" 8 "required diagram tags"

  _probe_with_count_threshold "adr-roadmap" \
    "Aggregate every ADR in $chain_dir into a roadmap. Each ADR must appear exactly once. Write to $val_path/adr-roadmap.md." \
    "ADR-[0-9]{2,}" 1 "ADR references"

  if [[ "$LIVE_FLAG" == "1" ]] || [[ -n "$MOCK_SOURCE" ]]; then
    local pi_sandbox="$LOG_DIR/sandbox/project-init"
    mkdir -p "$pi_sandbox"
    invoke_skill "project-init" \
      "Scaffold a new SDD project tree under $pi_sandbox. Produce the 8 layer directories (01_BRD..08_IPLAN) plus governance/ and registry/." \
      "skill" "utilities"
    local pi_layers
    pi_layers="$(find "$pi_sandbox" -maxdepth 2 -type d -name '0[1-8]_*' 2>/dev/null | wc -l)"
    if (( pi_layers >= 8 )); then
      OUTCOME_BY_NAME["project-init"]="PASS"
    else
      OUTCOME_BY_NAME["project-init"]="FAIL"
      ERROR_BY_NAME["project-init"]="only $pi_layers/8 layer dirs"
    fi
    OUTPUT_PATH_BY_NAME["project-init"]="$pi_sandbox"
    write_element_log "project-init"
  fi

  _probe_with_count_threshold "project-adopt" \
    "Adopt the existing project tree at $chain_dir. Report each detected layer." \
    "layer[[:space:]]*[0-9]|0[1-8]_(brd|prd|ears|bdd|adr|spec|tdd|iplan)" 8 "detected layers"

  _probe_with_count_threshold "project-profile" \
    "Profile the chain at $chain_dir. Report plugin version, framework spec version, layer count, and overall readiness." \
    "(version|layer|readiness)" 3 "profile fields"

  return 0
}

# -----------------------------------------------------------------------------
# Phase 4 — Agents, command, hook
# -----------------------------------------------------------------------------
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
  local agent="$1" prompt="$2" out_log="$3"
  claude \
    --plugin-dir "$PLUGIN_DIR" \
    --dangerously-skip-permissions \
    -p "Use the $agent agent to: $prompt" \
    > "$out_log" 2>&1
  return $?
}

phase_4_agents() {
  section "Phase 4.1 — Agents (11)"

  local chain_dir
  chain_dir="$(_resolve_chain_target)"

  if [[ "$LIVE_FLAG" != "1" ]] && [[ -z "$MOCK_SOURCE" ]]; then
    local entry agent
    for entry in "${AGENTS[@]}"; do
      agent="${entry%%|*}"
      record_outcome "$agent" "agent" "agents" "SKIP" 0 "" "" "false" "" "live mode disabled"
      write_element_log "$agent"
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
    local stdout_path="$LOG_DIR/elements/$agent.stdout"
    local t0 t1 duration; t0="$(date +%s)"

    if [[ -n "$MOCK_SOURCE" ]]; then
      if mock_replay_for "$agent"; then
        t1="$(date +%s)"; duration=$((t1 - t0))
        record_outcome "$agent" "agent" "agents" "PASS" "$duration"
        continue
      fi
      t1="$(date +%s)"; duration=$((t1 - t0))
      record_outcome "$agent" "agent" "agents" "SKIP" "$duration" "" "" "false" "" "no mock data"
      write_element_log "$agent"
      continue
    fi

    log_info "invoking agent: $agent"
    if invoke_agent_live "$agent" "$prompt" "$stdout_path"; then
      t1="$(date +%s)"; duration=$((t1 - t0))
      local words; words="$(wc -w < "$stdout_path" 2>/dev/null || echo 0)"
      if (( words >= min_words )); then
        record_outcome "$agent" "agent" "agents" "PASS" "$duration"
      else
        record_outcome "$agent" "agent" "agents" "FAIL" "$duration" "" "" "false" "" "output $words words < threshold $min_words"
        [[ $FAIL_FAST -eq 1 ]] && return 1
      fi
    else
      local rc=$?
      t1="$(date +%s)"; duration=$((t1 - t0))
      log_err "agent $agent failed (exit $rc)"
      record_outcome "$agent" "agent" "agents" "FAIL" "$duration" "" "" "false" "" "claude -p exit $rc"
    fi
    write_element_log "$agent"
  done

  return 0
}

phase_4_command() {
  section "Phase 4.2 — Command (/aidoc-flow:save-plan)"

  if [[ "$LIVE_FLAG" != "1" ]] && [[ -z "$MOCK_SOURCE" ]]; then
    record_outcome "save-plan" "command" "command" "SKIP" 0 "" "" "false" "" "live mode disabled"
    write_element_log "save-plan"
    return 0
  fi

  local cmd_sandbox="$LOG_DIR/sandbox/save-plan"
  mkdir -p "$cmd_sandbox"
  local stdout_path="$LOG_DIR/elements/save-plan.stdout"

  local t0 t1 duration; t0="$(date +%s)"
  log_info "invoking /aidoc-flow:save-plan (sandbox: $cmd_sandbox)"
  ( cd "$cmd_sandbox" && \
    claude --plugin-dir "$PLUGIN_DIR" --dangerously-skip-permissions \
      -p "Draft a brief plan with two steps. Then invoke /aidoc-flow:save-plan to capture it to a file under plans/." \
      > "$stdout_path" 2>&1 )
  local rc=$?
  t1="$(date +%s)"; duration=$((t1 - t0))

  local plan_file
  plan_file="$(find "$cmd_sandbox/plans" -name '*.md' -print -quit 2>/dev/null)"
  if [[ $rc -eq 0 ]] && [[ -n "$plan_file" ]] && [[ -s "$plan_file" ]]; then
    record_outcome "save-plan" "command" "command" "PASS" "$duration"
  else
    record_outcome "save-plan" "command" "command" "FAIL" "$duration" "" "" "false" "" "no plan file produced"
  fi
  write_element_log "save-plan"
}

phase_4_hook() {
  section "Phase 4.3 — Hook (sdd-doc-review.sh)"

  local hook_path="$PLUGIN_DIR/hooks/sdd-doc-review.sh"
  local hook_cfg="$PLUGIN_DIR/hooks/hooks.json"
  local stdout_path="$LOG_DIR/elements/sdd-doc-review.stdout"
  local t0 t1 duration; t0="$(date +%s)"

  if ! python3 -m json.tool < "$hook_cfg" > /dev/null 2>&1; then
    record_outcome "sdd-doc-review" "hook" "hook" "FAIL" 0 "" "" "false" "" "hooks.json invalid"
    write_element_log "sdd-doc-review"
    return 1
  fi

  if ! grep -q '"PostToolUse"' "$hook_cfg" || \
     ! grep -q '"Write|Edit"' "$hook_cfg" || \
     ! grep -q 'sdd-doc-review.sh' "$hook_cfg"; then
    record_outcome "sdd-doc-review" "hook" "hook" "FAIL" 0 "" "" "false" "" "hooks.json config mismatch"
    write_element_log "sdd-doc-review"
    return 1
  fi

  if [[ ! -x "$hook_path" ]]; then
    record_outcome "sdd-doc-review" "hook" "hook" "FAIL" 0 "" "" "false" "" "hook script not executable"
    write_element_log "sdd-doc-review"
    return 1
  fi

  local fixture="$NEGATIVE_FIXTURES_DIR/brd-broken-sections.md"
  if [[ ! -f "$fixture" ]] || ! command -v jq >/dev/null 2>&1; then
    record_outcome "sdd-doc-review" "hook" "hook" "SKIP" 0 "" "" "false" "" "fixture or jq missing"
    write_element_log "sdd-doc-review"
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
  printf '%s' "$hook_out" > "$stdout_path"

  t1="$(date +%s)"; duration=$((t1 - t0))

  if [[ $hook_rc -ne 0 ]]; then
    record_outcome "sdd-doc-review" "hook" "hook" "FAIL" "$duration" "" "" "false" "" "hook exit $hook_rc"
  elif ! printf '%s' "$hook_out" | jq . > /dev/null 2>&1; then
    record_outcome "sdd-doc-review" "hook" "hook" "FAIL" "$duration" "" "" "false" "" "hook output invalid JSON"
  elif ! printf '%s' "$hook_out" | grep -q "doc-brd-audit"; then
    record_outcome "sdd-doc-review" "hook" "hook" "FAIL" "$duration" "" "" "false" "" "missing audit nudge"
  elif ! printf '%s' "$hook_out" | grep -qiE "STRUCT01|structural findings"; then
    record_outcome "sdd-doc-review" "hook" "hook" "FAIL" "$duration" "" "" "false" "" "missing structural findings"
  else
    record_outcome "sdd-doc-review" "hook" "hook" "PASS" "$duration"
  fi
  write_element_log "sdd-doc-review"
}

# -----------------------------------------------------------------------------
# --promote algorithm (A5 redesigned: git add docs/ + .aidoc/ then commit)
# -----------------------------------------------------------------------------
_overall_outcome() {
  local name fail_n=0 pass_n=0
  for name in "${ELEMENT_ORDER[@]}"; do
    case "${OUTCOME_BY_NAME[$name]}" in
      PASS) pass_n=$((pass_n + 1)) ;;
      FAIL) fail_n=$((fail_n + 1)) ;;
    esac
  done
  if (( fail_n > 0 )); then echo "FAIL"
  elif (( pass_n == 0 )); then echo "SKIP"
  else echo "PASS"
  fi
}

promote_cascade() {
  section "Promote — git commit docs/ + .aidoc/ changes"

  local outcome; outcome="$(_overall_outcome)"
  if [[ "$outcome" != "PASS" ]]; then
    log_err "overall outcome is $outcome; refusing to promote a non-PASS run"
    return 1
  fi

  local plugin_version_file="$PLUGIN_DIR/VERSION"
  if [[ ! -f "$plugin_version_file" ]]; then
    log_err "VERSION file missing: $plugin_version_file"
    return 1
  fi
  local plugin_version
  plugin_version="$(cat "$plugin_version_file" | tr -d '[:space:]')"
  log_info "plugin version: $plugin_version"

  git -C "$FRAMEWORK" add "examples/$EXAMPLE/docs" "examples/$EXAMPLE/.aidoc" 2>/dev/null || true
  if git -C "$FRAMEWORK" diff --cached --quiet; then
    log_info "no docs/ or .aidoc/ changes to commit"
    return 0
  fi

  git -C "$FRAMEWORK" commit -m "chore(examples): promote $EXAMPLE cascade for v$plugin_version release

Run: $LOG_TIMESTAMP
Outcome: $outcome" || {
    log_err "commit failed"
    return 1
  }
  log_info "✓ committed docs/ + .aidoc/ updates"

  if (( PUSH == 1 )); then
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
  if (( fail_n > 0 )); then overall="FAIL"
  elif (( pass_n == 0 )); then overall="SKIP"
  fi

  {
    echo "Acceptance run: $EXAMPLE @ $LOG_TIMESTAMP"
    echo "Outcome: $overall  ($pass_n PASS, $fail_n FAIL, $skip_n SKIP, $total total)"
    echo "Bootstrap mode: $BOOTSTRAP_MODE"
    echo "Live: $([[ $LIVE_FLAG == 1 ]] && echo true || echo false)"
    echo "Mock source: ${MOCK_SOURCE:-(none)}"
    echo
    printf '  %-50s %-10s %-10s %s\n' "Element" "Phase" "Outcome" "Notes"
    printf '  %-50s %-10s %-10s %s\n' "$(printf -- '-%.0s' {1..50})" "----------" "----------" "----------------------"
    for name in "${ELEMENT_ORDER[@]}"; do
      local notes=""
      local audit="${AUDIT_SCORE_BY_NAME[$name]:-}"
      local audit_after="${AUDIT_AFTER_FIXER_BY_NAME[$name]:-}"
      if [[ -n "$audit_after" ]]; then
        notes="audit: $audit → $audit_after (after fixer)"
      elif [[ -n "$audit" ]]; then
        notes="audit: $audit"
      fi
      printf '  %-50s %-10s %-10s %s\n' \
        "$name" \
        "${PHASE_BY_NAME[$name]}" \
        "${OUTCOME_BY_NAME[$name]}" \
        "$notes"
    done
  } > "$SUMMARY_TXT"
  cat "$SUMMARY_TXT"

  # Build summary.json from per-element YAML front-matter.
  python3 - "$LOG_DIR" "$SUMMARY_JSON" <<'PY'
import json, os, sys, glob
import yaml
log_dir, out_path = sys.argv[1], sys.argv[2]
elements = []
for path in sorted(glob.glob(os.path.join(log_dir, "elements", "*.log"))):
    try:
        with open(path) as fh:
            content = fh.read()
        if not content.startswith("---\n"):
            continue
        end = content.find("\n---\n", 4)
        if end < 0:
            continue
        front = content[4:end]
        meta = yaml.safe_load(front)
        elements.append(meta)
    except Exception as e:
        sys.stderr.write(f"warn: failed reading {path}: {e}\n")

counts = {"PASS": 0, "FAIL": 0, "SKIP": 0}
for e in elements:
    counts[e.get("outcome", "SKIP")] = counts.get(e.get("outcome", "SKIP"), 0) + 1
overall = "PASS"
if counts["FAIL"] > 0: overall = "FAIL"
elif counts["PASS"] == 0: overall = "SKIP"

def _read(path):
    try:
        with open(path) as fh: return fh.read().strip()
    except Exception: return None

framework = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(log_dir))))
plugin_version = _read(os.path.join(framework, "platforms", "claude-code-plugin", "VERSION"))
spec_version = _read(os.path.join(framework, "framework", "VERSION"))

summary = {
    "schema_version": "1.1",
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
  echo "Logs:        $LOG_DIR"
  echo "Summary:     $SUMMARY_TXT"
  echo "Summary JSON: $SUMMARY_JSON"
  echo "Docs:        $EXAMPLE_DOCS"
  echo "AIDoc:       $AIDOC_DIR"

  [[ "$overall" == "FAIL" ]] && return 1 || return 0
}

# -----------------------------------------------------------------------------
# Main dispatch
# -----------------------------------------------------------------------------
echo "aidoc-flow acceptance run"
echo "Example:    $EXAMPLE"
echo "Plan:       $EXAMPLE_DIR/ACCEPTANCE_TEST_PLAN.md"
echo "Log dir:    $LOG_DIR"
echo "Docs:       $EXAMPLE_DOCS"
echo "AIDoc:      $AIDOC_DIR"
echo "Live:       $([[ $LIVE_FLAG == 1 ]] && echo enabled || echo disabled)"
echo "Mock:       ${MOCK_SOURCE:-(none)}"
echo "Phase:      ${PHASE:-all}"
echo "Element:    ${ELEMENT:-all}"
echo

phase_0_bootstrap || {
  log_err "Phase 0 failure — aborting"
  write_summary
  exit 1
}

PHASES_TO_RUN=("cascade" "negative" "chg" "utilities" "agents" "command" "hook")
if [[ -n "$PHASE" ]]; then
  case "$PHASE" in
    bootstrap)  PHASES_TO_RUN=() ;;
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

write_summary
RC=$?

if (( PROMOTE == 1 )); then
  if (( RC != 0 )); then
    log_err "--promote requested but overall run is FAIL; skipping promote"
  else
    promote_cascade || RC=1
  fi
fi

END_EPOCH="$(date +%s)"
log_info "Total runtime: $((END_EPOCH - START_EPOCH))s"

exit $RC
