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

  # 0.5 API auth check (live mode only)
  if [[ "$LIVE_FLAG" == "1" ]] && [[ -z "$MOCK_SOURCE" ]]; then
    if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
      log_err "ANTHROPIC_API_KEY is unset; required for --live mode"
      record_outcome "api-auth-check" "fixture" "bootstrap" "FAIL" 0 "" "" "false" "" "ANTHROPIC_API_KEY unset"
      _write_bootstrap_metas
      return 1
    fi
    if ! command -v claude >/dev/null 2>&1; then
      log_err "claude CLI not on PATH; required for --live mode"
      record_outcome "api-auth-check" "fixture" "bootstrap" "FAIL" 0 "" "" "false" "" "claude CLI missing"
      _write_bootstrap_metas
      return 1
    fi
    log_info "API auth check: PASS"
    record_outcome "api-auth-check" "fixture" "bootstrap" "PASS" 0
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
PHASES_TO_RUN=("cascade")  # Impl-1 only implements bootstrap + cascade
if [[ -n "$PHASE" ]]; then
  case "$PHASE" in
    bootstrap)  PHASES_TO_RUN=() ;;  # only Phase 0 ran
    cascade)    PHASES_TO_RUN=("cascade") ;;
    negative|chg|utilities|agents|command|hook)
      log_warn "phase=$PHASE not yet implemented (Impl-2+); running cascade if --live"
      PHASES_TO_RUN=("cascade")
      ;;
    *) log_err "unknown phase: $PHASE"; exit 2 ;;
  esac
fi

for phase_name in "${PHASES_TO_RUN[@]}"; do
  case "$phase_name" in
    cascade) phase_1_cascade ;;
  esac
done

# Final summary
write_summary
RC=$?

# Cleanup: log final runtime
END_EPOCH="$(date +%s)"
log_info "Total runtime: $((END_EPOCH - START_EPOCH))s"

exit $RC
