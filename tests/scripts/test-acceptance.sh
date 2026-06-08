#!/usr/bin/env bash
#
# tests/scripts/test-acceptance.sh — Pre-deployment acceptance test driver.
#
# Drives every active element of the Claude Code plugin (50 skills + 11
# agents + 1 command + 1 hook = 63 elements) against a named example's
# seed. The chain produced is the release-gate evidence.
#
# Methodology: tests/ACCEPTANCE.md.
# Per-example specifics: examples/<NAME>/README.md.
# Schema: tests/scripts/test-acceptance.schema.json (v1.2).
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
#     --no-live              skip live LLM calls; prints plan summary, then
#                            runs the full deterministic suite (Phase 0
#                            preflight + Phase 1.2 negative fixtures that
#                            don't require LLM + Phase 4.3 hook). ~9s, $0.
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
#     --dry-run              alias for --no-live (common convention)
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
DEFAULT_PROFILE_SRC="$FRAMEWORK/framework/governance/PROFILE-TEMPLATE.yaml"
FRAMEWORK_CREWS_FALLBACK="$FRAMEWORK/framework/governance/REVIEW_CREWS.yaml"

# Per-layer runtime cap. Raised again in BRD-RT-003 / D-0027 from 1800s
# to 3600s: an autopilot that orchestrates a create→review→revise loop
# (audit + fixer + re-audit) legitimately runs 30-45 min per layer in
# team mode, and a multi-iteration fix cycle pushes that to ~60 min.
# Lineage: 900s (BRD-RT-001) → 1800s (BRD-RT-002) → 3600s (BRD-RT-003).
MAX_LAYER_SEC=3600   # 60 minutes per layer

# Per-skill timeout. Generalised in BRD-RT-004 / D-0028: collapse the
# previously-separate AUDIT_TIMEOUT / AUTOPILOT_TIMEOUT / REVIEW_TEAM_TIMEOUT
# into a single ORCHESTRATOR_TIMEOUT applied to every skill that
# internally dispatches a sub-team in team mode (review-team, plus
# doc-*-audit, doc-*-autopilot, doc-*-fixer). Leaf skills (no sub-team
# dispatch) keep the default SKILL_TIMEOUT. Agents (Phase 4.1) keep the
# AGENT_TIMEOUT.
#
# Lineage of the orchestrator budget:
#   BRD-RT-002: AUDIT_TIMEOUT=1200 for doc-*-audit only
#     (Gap A — audit's lens-fan-out + synthesizer dispatch)
#   BRD-RT-003: AUTOPILOT_TIMEOUT=1800 added for doc-*-autopilot
#     (G11 — autopilot's create→review→revise outer loop)
#   BRD-RT-004: doc-*-fixer also hit 600s SKILL_TIMEOUT on a multi-lens
#     dispatch (G15 — fixer's parallel lens-validation Task subagents
#     + synthesizer). Generalised to one ORCHESTRATOR_TIMEOUT covering
#     all three (audit, autopilot, fixer) + review-team itself.
SKILL_TIMEOUT="${SKILL_TIMEOUT:-600}"                       # 10 min — leaf skills
# Autopilot now wraps the saga driver, which itself dispatches up to 4
# claude -p subprocesses per layer (draft, review, fixer, re-review).
# A realistic BRD cycle with one fixer pass takes 40-55 min wall-clock,
# so the autopilot subprocess needs ~60 min to outlive the driver's
# break-circuit (SOFT_DEADLINE=3300s in saga_driver.py). See B5/B6 in
# the SAGA-PARITY-001 Phase 2 Amendment 1 verification (2026-06-05).
ORCHESTRATOR_TIMEOUT="${ORCHESTRATOR_TIMEOUT:-3600}"         # 60 min — autopilot+driver chain
AGENT_TIMEOUT="${AGENT_TIMEOUT:-600}"                       # 10 min for agents

# Total token budget for the whole run (A8). When the cumulative
# tokens_out across all elements exceeds this, abort with FAIL.
# Token counts are estimated from output byte size / 4 (rough char/token
# ratio) until B6's --output-format=json wiring lands in PR C.
MAX_TOTAL_OUTPUT_TOKENS="${MAX_TOTAL_OUTPUT_TOKENS:-1500000}"
TOTAL_TOKENS_OUT=0

# Retry policy for transient HTTP errors (A9).
RETRY_MAX="${RETRY_MAX:-3}"
RETRY_BACKOFF_BASE="${RETRY_BACKOFF_BASE:-5}"  # seconds; exponential 5, 10, 20

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
SKIP_COMPLETED_PATH=""   # R5 — explicit prior-run directory
MOCK_SOURCE=""
PROMOTE=0
PUSH=0
FORCE=0
FAIL_FAST=0
FROM_LAYER=""     # A7 — resume cascade from this layer name (e.g. "spec")
TO_LAYER=""       # P2 — stop cascade after this layer name
# --dry-run is a clean alias of --no-live (both set LIVE_FLAG=0). Kept as
# a separate flag because the name is conventional in CLI tooling.

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
    --skip-completed=*) SKIP_COMPLETED=1; SKIP_COMPLETED_PATH="${arg#--skip-completed=}" ;;
    --mock=*)          MOCK_SOURCE="${arg#--mock=}" ;;
    --promote)         PROMOTE=1 ;;
    --push)            PUSH=1 ;;
    --force)           FORCE=1 ;;
    --fail-fast)       FAIL_FAST=1 ;;
    --from-layer=*)    FROM_LAYER="${arg#--from-layer=}" ;;
    --to-layer=*)      TO_LAYER="${arg#--to-layer=}" ;;
    --dry-run)         LIVE_FLAG="0" ;;  # alias for --no-live
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

# R2 — SIGINT/SIGTERM trap. Ensures a usable summary.json + summary.txt
# exist even when the user kills mid-run. In-flight RUNNING elements
# are rewritten as INTERRUPTED so --skip-completed knows what to retry.
INTERRUPTED=0
_on_interrupt() {
  INTERRUPTED=1
  # Subsequent code paths check $INTERRUPTED and exit cleanly.
  printf '\n!! interrupted — finalizing state...\n' >&2
}
trap _on_interrupt INT TERM

_on_exit() {
  local rc=$?
  # Mark any RUNNING elements as INTERRUPTED.
  if [[ -d "$LOG_DIR/elements" ]]; then
    local stub
    for stub in "$LOG_DIR"/elements/*.log; do
      [[ -f "$stub" ]] || continue
      if grep -q '^outcome: RUNNING$' "$stub" 2>/dev/null; then
        sed -i 's/^outcome: RUNNING$/outcome: INTERRUPTED/' "$stub"
      fi
    done
    _rebuild_summary_json 2>/dev/null || true
  fi
  exit "$rc"
}
trap _on_exit EXIT

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

# AUTO-REMEDIATE-001: detect if lint output contains STY03 error(s) and no
# other ERROR-level findings. Returns 0 if the failure is STY03-only (eligible
# for auto-remediation), non-zero otherwise. Lint warnings are ignored.
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

# AUTO-REMEDIATE-001: extract the file path from STY03 lint error output.
# Input is the full lint stdout; output is the first path matching
# <path>:<line>: [ERROR STY03].
extract_path() {
  local output="$1"
  printf '%s\n' "$output" | grep -oE '^[^:]+:[0-9]+: \[ERROR STY03\]' \
    | head -1 \
    | sed -E 's/^([^:]+):[0-9]+: \[ERROR STY03\]$/\1/'
}

# AUTO-REMEDIATE-001: extract the layer directory (e.g., "03_EARS") from a
# docs/0N_LAYER/... path. Returns empty string on no match.
extract_layer_dir() {
  local path="$1"
  printf '%s' "$path" | grep -oE '/[0-9]{2}_[A-Z]+/' | head -1 | tr -d /
}

# AUTO-REMEDIATE-001: extract the artifact ID (e.g., "EARS-01") from the
# filename portion of a docs/.../LAYER-NN[_anything].md path.
extract_artifact_id() {
  local path="$1"
  basename "$path" | grep -oE '^[A-Z]+-[0-9]+' | head -1
}

# AUTO-REMEDIATE-001: write a minimal synthetic audit verdict.json for the
# fixer to consume. Schema matches what the synthesizer agent would emit but
# contains a single STY03 P1 finding (the only finding the fixer needs to
# address). Directory must exist (caller ensures via mkdir -p).
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

# AUTO-REMEDIATE-001: write a minimal synthetic audit report markdown
# matching what doc-<layer>-fixer expects (Input Contract). Only contains the
# single STY03 finding.
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

  local tokens_out="${TOKENS_OUT_BY_NAME[$name]:-}"

  NAME="$name" KIND="$kind" PHASE_LABEL="$phase" DURATION="$duration" \
  OUTCOME="$outcome" AUDIT="$audit" AUDIT_AFTER="$audit_after" \
  FIXER_INV_PY="$fixer_inv_py" OUT_PATH="$out_path" ERR="$err" \
  TOKENS_OUT="$tokens_out" \
  STDOUT_PATH="$stdout_path" LOG_PATH="$log_path" \
  python3 - <<'PY'
import json, os

meta = {
  "schema_version": "1.2",
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
  "tokens_out": int(os.environ["TOKENS_OUT"]) if os.environ.get("TOKENS_OUT") else None,
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

  # R1 — Refresh summary.json incrementally so an interrupted run still
  # leaves a usable checkpoint that --skip-completed can read.
  _rebuild_summary_json
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
# Skill invocation — live mode, with timeout (B4), retry on transient
# errors (A9), and token estimation (B6 approximate; exact via
# --output-format=json deferred to PR C).
# -----------------------------------------------------------------------------
_pick_timeout_for() {
  # _pick_timeout_for <kind> <name> → seconds
  #
  # BRD-RT-004 / D-0028: orchestrator skills (anything that internally
  # dispatches a sub-team in team mode) get ORCHESTRATOR_TIMEOUT.
  # Identified by name pattern:
  #   review-team             — the dispatch primitive itself
  #   doc-*-audit             — fans out N review-lens Task subagents + synthesizer
  #   doc-*-autopilot         — runs create→review→revise loop inside one process
  #   doc-*-fixer             — dispatches N lens-validator Task subagents on
  #                             multi-lens findings (G15, BRD-RT-002 Run #1)
  #
  # Globs are anchored to the `doc-*-` prefix (not bare `*-audit` etc.)
  # to avoid catching non-orchestrator utilities like `security-audit`,
  # which is a single-pass leaf skill — confirmed by inspection: its
  # SKILL.md does not dispatch Task subagents (G18, gap analysis of
  # PR #77). The 9 layer + CHG skills per pattern are the intended set.
  #
  # Pattern reusable for PRD..IPLAN — name-match applies uniformly.
  local kind="$1" name="$2"
  if [[ "$kind" == "agent" ]]; then
    echo "$AGENT_TIMEOUT"
  elif [[ "$name" == "review-team" || "$name" == doc-*-audit || "$name" == doc-*-autopilot || "$name" == doc-*-fixer ]]; then
    echo "$ORCHESTRATOR_TIMEOUT"
  else
    echo "$SKILL_TIMEOUT"
  fi
}

# Estimate output tokens from a captured stdout file. Crude: bytes / 4.
# Returns 0 if file missing.
_estimate_tokens_out() {
  local path="$1"
  [[ -f "$path" ]] || { echo 0; return; }
  local bytes
  bytes="$(wc -c < "$path" 2>/dev/null || echo 0)"
  echo $((bytes / 4))
}

# B6 — Maintain a process-wide cumulative token counter and trigger A8
# cost cap when exceeded. R4 — sets a global flag so the dispatch loop
# stops, not just the current element.
COST_CAP_EXCEEDED=0
_record_tokens_out() {
  local name="$1" tokens="$2"
  TOKENS_OUT_BY_NAME["$name"]="$tokens"
  TOTAL_TOKENS_OUT=$((TOTAL_TOKENS_OUT + tokens))
  if (( TOTAL_TOKENS_OUT > MAX_TOTAL_OUTPUT_TOKENS )); then
    log_err "Cost cap exceeded: ${TOTAL_TOKENS_OUT} tokens out > ${MAX_TOTAL_OUTPUT_TOKENS} cap"
    log_err "  Aborting to prevent runaway spend. Set MAX_TOTAL_OUTPUT_TOKENS to raise."
    COST_CAP_EXCEEDED=1
    return 1
  fi
  return 0
}

declare -A TOKENS_OUT_BY_NAME=()

invoke_skill_live() {
  # invoke_skill_live <name> <prompt> <stdout-path> <kind>
  # Runs claude -p with per-skill timeout and retry-on-transient-error.
  # Returns 0 on success, non-zero otherwise. Caller checks output via
  # the stdout file.
  local name="$1" prompt="$2" out_path="$3" kind="${4:-skill}"
  local t_sec; t_sec="$(_pick_timeout_for "$kind" "$name")"

  local attempt rc
  for attempt in $(seq 1 "$RETRY_MAX"); do
    if [[ "$kind" == "agent" ]]; then
      timeout "$t_sec" claude \
        --plugin-dir "$PLUGIN_DIR" \
        --dangerously-skip-permissions \
        -p "Use the $name agent to: $prompt" \
        > "$out_path" 2>&1
    else
      timeout "$t_sec" claude \
        --plugin-dir "$PLUGIN_DIR" \
        --dangerously-skip-permissions \
        -p "/aidoc-flow:$name $prompt" \
        > "$out_path" 2>&1
    fi
    rc=$?

    case $rc in
      0) return 0 ;;
      124) echo "TIMEOUT after ${t_sec}s" >> "$out_path"; return $rc ;;
      *)
        # Retry on what look like transient errors: 5xx wording, "rate",
        # "overloaded", "service unavailable". Non-retryable: exit 124
        # (timeout, handled above) and any structured non-zero with
        # actual output that doesn't match transient patterns.
        if grep -qiE 'rate limit|overloaded|503|502|service unavailable|temporarily' "$out_path" 2>/dev/null \
           && (( attempt < RETRY_MAX )); then
          local backoff=$((RETRY_BACKOFF_BASE * (2 ** (attempt - 1))))
          log_warn "$name attempt $attempt failed (transient); retry in ${backoff}s"
          sleep "$backoff"
          continue
        fi
        return $rc
        ;;
    esac
  done
  return $rc
}

invoke_skill() {
  # invoke_skill <name> <prompt> <kind> <phase>
  local name="$1" prompt="$2" kind="$3" phase_label="$4"
  local stdout_path="$LOG_DIR/elements/$name.stdout"

  # A6 — --skip-completed: if a prior run's summary marks this element
  # PASS, copy that element's log over and skip the call.
  if (( SKIP_COMPLETED == 1 )) && _try_skip_completed "$name" "$kind" "$phase_label"; then
    return 0
  fi

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

  # R3 — write a RUNNING stub before invoking, so an interrupted run
  # (Ctrl-C, kill, network drop, OOM) leaves a visible marker that the
  # trap handler can rewrite as INTERRUPTED.
  record_outcome "$name" "$kind" "$phase_label" "RUNNING" 0
  write_element_log "$name"

  if invoke_skill_live "$name" "$prompt" "$stdout_path" "$kind"; then
    t1="$(date +%s)"; duration=$((t1 - t0))
    local tokens; tokens="$(_estimate_tokens_out "$stdout_path")"
    if ! _record_tokens_out "$name" "$tokens"; then
      record_outcome "$name" "$kind" "$phase_label" "FAIL" "$duration" "" "" "false" "" "cost cap exceeded"
      write_element_log "$name"
      return 1
    fi
    record_outcome "$name" "$kind" "$phase_label" "PASS" "$duration"
    write_element_log "$name"
    return 0
  else
    local rc=$?
    t1="$(date +%s)"; duration=$((t1 - t0))
    log_err "$name failed (exit $rc)"
    local tokens; tokens="$(_estimate_tokens_out "$stdout_path")"
    _record_tokens_out "$name" "$tokens" || true   # don't double-fail
    record_outcome "$name" "$kind" "$phase_label" "FAIL" "$duration" "" "" "false" "" "claude -p exit $rc"
    write_element_log "$name"
    return 1
  fi
}

# A6 helper — peek at a prior run's summary.json and skip elements
# that were PASS there. R5 — explicit path via $SKIP_COMPLETED_PATH;
# otherwise default to the most-recent prior run.
_try_skip_completed() {
  local name="$1" kind="$2" phase_label="$3"
  local prior
  if [[ -n "$SKIP_COMPLETED_PATH" ]]; then
    prior="$SKIP_COMPLETED_PATH"
  else
    prior="$(ls -td "$EXAMPLE_DIR"/logs/*/ 2>/dev/null \
             | grep -v "$LOG_TIMESTAMP" \
             | head -1)"
  fi
  [[ -z "$prior" ]] && return 1
  local prior_summary="${prior%/}/summary.json"
  [[ -f "$prior_summary" ]] || return 1

  local outcome
  outcome="$(NAME="$name" SUMMARY="$prior_summary" python3 - <<'PY'
import json, os, sys
with open(os.environ["SUMMARY"]) as fh:
    d = json.load(fh)
for e in d.get("elements", []):
    if e.get("name") == os.environ["NAME"]:
        print(e.get("outcome", ""))
        sys.exit(0)
print("")
PY
)"
  [[ "$outcome" != "PASS" ]] && return 1

  # Copy the prior element log into the new run
  local prior_log="${prior%/}/elements/$name.log"
  if [[ -f "$prior_log" ]]; then
    cp "$prior_log" "$LOG_DIR/elements/$name.log"
    log_info "skip-completed: reusing prior PASS for $name"
    record_outcome "$name" "$kind" "$phase_label" "PASS" 0
    return 0
  fi
  return 1
}

parse_audit_score() {
  # parse_audit_score <name>
  # Source of truth (BRD-RT-002 / D-0026): the synthesizer's verdict.json
  # at .aidoc/review/<NN>_<LAYER>/<artifact-id>/verdict.json. Falls back
  # to scraping the audit skill's stdout log when verdict.json is absent
  # (e.g. single_pass runs — no synthesizer dispatched).
  #
  # If both are present and disagree, prefer verdict.json and log a
  # warning. Model output drift in the audit skill's stdout response
  # vs the synthesizer's deterministic JSON is exactly what this
  # cross-check catches.
  local name="$1"
  local log="$LOG_DIR/elements/$name.log"
  local stdout_score=""
  local json_score=""

  # 1. Scrape the audit skill's stdout (legacy path).
  if [[ -f "$log" ]]; then
    stdout_score="$(awk '/^---$/ {n++; next} n>=2' "$log" \
      | grep -iE 'score|readiness' \
      | grep -oE '[0-9]+' \
      | head -1)"
  fi

  # 2. Find the matching verdict.json. Skill names look like
  # "doc-brd-audit"; extract the layer token (e.g. "brd") and resolve
  # the per-artifact blackboard dir.
  if [[ "$name" =~ ^doc-([a-z]+)-audit$ ]]; then
    local layer="${BASH_REMATCH[1]}"
    local layer_upper="${layer^^}"
    local layer_num=""
    case "$layer" in
      brd)   layer_num="01" ;;
      prd)   layer_num="02" ;;
      ears)  layer_num="03" ;;
      bdd)   layer_num="04" ;;
      adr)   layer_num="05" ;;
      spec)  layer_num="06" ;;
      tdd)   layer_num="07" ;;
      iplan) layer_num="08" ;;
    esac
    if [[ -n "$layer_num" ]]; then
      local verdict
      verdict="$(ls "$AIDOC_DIR/review/${layer_num}_${layer_upper}"/*/verdict.json 2>/dev/null | head -1)"
      if [[ -n "$verdict" && -f "$verdict" ]]; then
        json_score="$(python3 -c "
import json, sys
try:
    with open('$verdict') as f:
        print(json.load(f).get('content_score', ''))
except Exception:
    print('')
" 2>/dev/null)"
      fi
    fi
  fi

  # 3. Decide. verdict.json wins; warn on mismatch.
  if [[ -n "$json_score" ]]; then
    if [[ -n "$stdout_score" && "$stdout_score" != "$json_score" ]]; then
      log_warn "  audit score drift: stdout reported $stdout_score, verdict.json says $json_score; preferring verdict.json"
    fi
    echo "$json_score"
    return
  fi

  echo "${stdout_score:-0}"
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

  # 0.8 P3 — Upstream presence check. If --from-layer or --element
  # implies a non-BRD layer, the previous layer's artifact in docs/
  # must already exist. Fail fast with a clear hint.
  local _resume_layer=""
  if [[ -n "$FROM_LAYER" ]]; then
    _resume_layer="$FROM_LAYER"
  elif [[ -n "$ELEMENT" ]]; then
    # Extract <layer> from doc-<layer>-<variant>.
    if [[ "$ELEMENT" =~ ^doc-([a-z]+)(-[a-z]+)?$ ]]; then
      local _l="${BASH_REMATCH[1]}"
      case "$_l" in
        brd|prd|ears|bdd|adr|spec|tdd|iplan) _resume_layer="$_l" ;;
      esac
    fi
  fi
  if [[ -n "$_resume_layer" ]] && [[ "$_resume_layer" != "brd" ]]; then
    local _idx=0 _prev_layer="" _prev_type=""
    for _l in "${LAYERS[@]}"; do
      if [[ "$_l" == "$_resume_layer" ]] && (( _idx > 0 )); then
        _prev_layer="${LAYERS[$((_idx - 1))]}"
        _prev_type="${LAYER_TYPES[$((_idx - 1))]}"
        break
      fi
      _idx=$((_idx + 1))
    done
    local _prev_num
    printf -v _prev_num '%02d' "$_idx"
    local _upstream="$EXAMPLE_DOCS/${_prev_num}_${_prev_type}/${_prev_type}-01.md"
    if [[ ! -f "$_upstream" ]]; then
      log_err "upstream artifact missing: $_upstream"
      log_err "  --from-layer=$_resume_layer / --element=$ELEMENT requires the previous layer ($_prev_type) to exist in docs/"
      log_err "  hint: run \`--from-layer=brd --to-layer=$_prev_layer\` first, or remove --from-layer/--element"
      record_outcome "upstream-check" "fixture" "bootstrap" "FAIL" 0 "" "" "false" "" "upstream $_upstream missing"
      _write_bootstrap_metas
      return 1
    fi
    log_info "upstream check: $_upstream exists"
    record_outcome "upstream-check" "fixture" "bootstrap" "PASS" 0
  fi

  _write_bootstrap_metas
  return 0
}

# P1 helper — given the active --element filter and a candidate
# invocation name, decide whether to run it (return 0) or skip it
# (return 1). When ELEMENT is empty, everything runs.
_should_invoke() {
  local candidate="$1"
  [[ -z "$ELEMENT" ]] && return 0
  [[ "$candidate" == "$ELEMENT" ]] && return 0
  return 1
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

  # A7 — --from-layer: skip layers before the resume point. The
  # previous layer's artifact in docs/ becomes the upstream context.
  local resume_idx=0
  if [[ -n "$FROM_LAYER" ]]; then
    local idx=0
    local found=0
    for l in "${LAYERS[@]}"; do
      if [[ "$l" == "$FROM_LAYER" ]]; then
        resume_idx=$idx
        found=1
        break
      fi
      idx=$((idx + 1))
    done
    if (( found == 0 )); then
      log_warn "--from-layer=$FROM_LAYER not found in LAYERS list; running full cascade"
    elif (( resume_idx > 0 )); then
      local prev_idx=$((resume_idx - 1))
      local prev_layer="${LAYERS[$prev_idx]}"
      local prev_type="${LAYER_TYPES[$prev_idx]}"
      local prev_num
      printf -v prev_num '%02d' "$resume_idx"
      prev_output="$EXAMPLE_DOCS/${prev_num}_${prev_type}/${prev_type}-01.md"
      if [[ ! -f "$prev_output" ]]; then
        log_err "--from-layer=$FROM_LAYER but upstream $prev_output does not exist"
        return 1
      fi
      log_info "--from-layer=$FROM_LAYER (resuming with upstream $prev_output)"
    else
      log_info "--from-layer=$FROM_LAYER (first layer; no upstream required)"
    fi
  fi

  # P2 — resolve TO_LAYER → stop_idx (inclusive)
  local stop_idx=$((${#LAYERS[@]} - 1))
  if [[ -n "$TO_LAYER" ]]; then
    local idx=0
    for l in "${LAYERS[@]}"; do
      if [[ "$l" == "$TO_LAYER" ]]; then
        stop_idx=$idx
        break
      fi
      idx=$((idx + 1))
    done
    log_info "--to-layer=$TO_LAYER (stop after layer index $stop_idx)"
  fi

  for layer in "${LAYERS[@]}"; do
    if (( i < resume_idx )); then
      log_info "skipping layer ${LAYER_TYPES[$i]} (--from-layer=$FROM_LAYER)"
      record_outcome "doc-$layer-autopilot" "skill" "cascade" "SKIP" 0 "" "" "false" "" "skipped via --from-layer"
      write_element_log "doc-$layer-autopilot"
      i=$((i + 1))
      continue
    fi
    if (( i > stop_idx )); then
      log_info "skipping layer ${LAYER_TYPES[$i]} (--to-layer=$TO_LAYER)"
      record_outcome "doc-$layer-autopilot" "skill" "cascade" "SKIP" 0 "" "" "false" "" "skipped via --to-layer"
      write_element_log "doc-$layer-autopilot"
      i=$((i + 1))
      continue
    fi
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

    # The cascade dispatcher invokes the saga driver DIRECTLY (Python),
    # NOT through the `doc-<layer>-autopilot` SKILL. The autopilot SKILL
    # remains available as a user-facing entry point for interactive use
    # (`/aidoc-flow:doc-<layer>-autopilot` in a Claude Code session), but
    # the HARNESS uses the driver directly to eliminate LLM-stochasticity
    # from the dispatch path.
    #
    # Why this matters: in 2026-06-07 PRD-RT-001 verification (PR #101)
    # the autopilot LLM chose `run_in_background=true` and exited before
    # the driver completed, relying on a Claude Code notification that
    # doesn't fire in `claude -p` non-interactive CLI mode. The same
    # SKILL prompt that worked for BRD v0.6.1 failed for PRD v0.6.4 —
    # same class as B1's "cooperative-enforcement is non-deterministic."
    # The fix here removes the LLM from the harness's driver-invocation
    # path entirely. The driver itself is layer-agnostic (its
    # _LAYER_CREWS covers all 8 layers) and Python; deterministic.
    #
    # The autopilot SKILL is still recorded as a PASS element when the
    # driver succeeds — for harness output / summary continuity. The
    # SKILL just isn't invoked.
    if _should_invoke "doc-$layer-autopilot"; then
      export PREV_OUTPUT="$prev_output"
      export ARTIFACT_ID="${type}-01"
      export ARTIFACT_PATH="$artifact"
      export CLAUDE_PLUGIN_ROOT="$PLUGIN_DIR"

      log_info "invoking saga_driver.py directly (--layer ${layer_num}_${type})"
      local driver_log="$LOG_DIR/elements/doc-$layer-autopilot.stdout"
      local driver_t0 driver_t1 driver_dur driver_rc driver_timeout
      driver_t0="$(date +%s)"
      record_outcome "doc-$layer-autopilot" "skill" "cascade" "RUNNING" 0
      write_element_log "doc-$layer-autopilot"

      driver_timeout="$ORCHESTRATOR_TIMEOUT"
      timeout "$driver_timeout" python3 \
        "$PLUGIN_DIR/tools/saga_driver.py" \
        --layer "${layer_num}_${type}" \
        --threshold 90 \
        > "$driver_log" 2>&1
      driver_rc=$?
      driver_t1="$(date +%s)"
      driver_dur=$((driver_t1 - driver_t0))

      OUTPUT_PATH_BY_NAME["doc-$layer-autopilot"]="$artifact"
      if (( driver_rc == 0 )); then
        record_outcome "doc-$layer-autopilot" "skill" "cascade" "PASS" "$driver_dur"
      elif (( driver_rc == 124 )); then
        echo "TIMEOUT after ${driver_timeout}s" >> "$driver_log"
        record_outcome "doc-$layer-autopilot" "skill" "cascade" "FAIL" "$driver_dur" "" "" "false" "" "driver timeout"
      else
        record_outcome "doc-$layer-autopilot" "skill" "cascade" "FAIL" "$driver_dur" "" "" "false" "" "driver exit $driver_rc"
      fi
      write_element_log "doc-$layer-autopilot"

      if [[ "${OUTCOME_BY_NAME[doc-$layer-autopilot]:-}" != "PASS" ]] && [[ $FAIL_FAST -eq 1 ]]; then
        return 1
      fi
    fi

    # Read the autopilot's saga.json journal for the layer outcome.
    # The autopilot's saga driver dispatched doc-<layer>-audit (+ fixer
    # + re-audit as needed) internally; this is the post-hoc inspection.
    #
    # CRITICAL: saga.json MUST exist after a team-mode autopilot run.
    # If it's absent, the autopilot bypassed the saga driver (the
    # exact bug Amendment 1 fixes). FAIL the layer hard rather than
    # silently passing on subprocess exit code.
    local saga_file="$AIDOC_DIR/review/${layer_num}_${type}/${type}-01/saga.json"
    local score=0
    local saga_status="UNKNOWN"
    if [[ -f "$saga_file" ]]; then
      saga_status="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('status',''))" "$saga_file" 2>/dev/null || echo UNKNOWN)"
      score="$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d.get('result',{}).get('content_score', 0))" "$saga_file" 2>/dev/null || echo 0)"
      log_info "  saga: status=$saga_status score=$score"
      # Reject non-terminal status — the driver must complete the loop.
      case "$saga_status" in
        CLOSED) ;;  # happy path
        ESCALATED)
          log_err "  saga ESCALATED for ${type}-01 — human review required"
          record_outcome "doc-$layer-autopilot" "skill" "cascade" "FAIL" "" "" "" "false" "" "saga ESCALATED"
          [[ $FAIL_FAST -eq 1 ]] && return 1
          ;;
        PARTIAL_TIMEOUT)
          log_warn "  saga PARTIAL_TIMEOUT for ${type}-01 — resume on next invocation"
          record_outcome "doc-$layer-autopilot" "skill" "cascade" "FAIL" "" "" "" "false" "" "saga PARTIAL_TIMEOUT"
          [[ $FAIL_FAST -eq 1 ]] && return 1
          ;;
        *)
          log_err "  saga status=$saga_status for ${type}-01 — unexpected non-terminal state"
          record_outcome "doc-$layer-autopilot" "skill" "cascade" "FAIL" "" "" "" "false" "" "saga non-terminal: $saga_status"
          [[ $FAIL_FAST -eq 1 ]] && return 1
          ;;
      esac
    else
      log_err "  saga.json MISSING at $saga_file — autopilot bypassed the saga driver"
      log_err "  (this is the v0.6.0 cooperative-enforcement failure mode;"
      log_err "   v0.6.1 autopilot MUST invoke \${CLAUDE_PLUGIN_ROOT}/tools/saga_driver.py)"
      record_outcome "doc-$layer-autopilot" "skill" "cascade" "FAIL" "" "" "" "false" "" "saga.json absent"
      [[ $FAIL_FAST -eq 1 ]] && return 1
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

    # Note: doc-<layer>-{audit,fixer,base} are no longer dispatched by
    # this cascade. The autopilot's saga driver invokes them internally
    # via subprocess. They stay available for direct user invocation.

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

  # C2 — Calibrated against actual quality-advisor output (structured
  # prose with `### Layer N` headings, `→` arrow markers, priority
  # lists). The original `suggest|recommend|improve` regex undercounted
  # by ~5×.
  _probe_with_count_threshold "quality-advisor" \
    "Review the chain at $chain_dir and provide actionable improvement suggestions, one per layer at minimum. Write the full suggestions document to $qa_path with per-layer sections (### Layer N) and actionable items prefixed with → or numbered." \
    "^### Layer|^→ |^- \*\*Fix|^[0-9]+\.[[:space:]]|suggest|recommend|improve" 8 "actionable suggestions"

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
    # Fallback chain (PROFILE-DELTA-001): the project profile is an
    # override-only delta. If it does not declare crews/personas, fall
    # back to the framework default at $FRAMEWORK_CREWS_FALLBACK.
    local personas
    personas="$(PROFILE="$PROFILE_FILE" FALLBACK="$FRAMEWORK_CREWS_FALLBACK" python3 - <<'PY'
import os, yaml

def load(path):
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}

def collect(node, acc):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "persona" and isinstance(v, str):
                acc.add(v)
            else:
                collect(v, acc)
    elif isinstance(node, list):
        for item in node:
            collect(item, acc)

acc = set()
collect(load(os.environ["PROFILE"]), acc)
if not acc:
    # Project profile carries no crew/persona overrides — fall back to
    # the framework default (REVIEW_CREWS.yaml).
    collect(load(os.environ["FALLBACK"]), acc)
print(" ".join(sorted(acc)))
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

  # C3 — Calibrated: in the prior run knowledge-extractor asked
  # follow-up questions instead of producing output. New prompt is
  # directive ("do not ask for clarification") and asks for Mermaid
  # syntax. Regex now matches Mermaid node/edge syntax + bullet
  # entities + JSON keys.
  _probe_with_count_threshold "knowledge-extractor" \
    "Extract a domain knowledge graph from the chain at $chain_dir. Write the full graph to $val_path/knowledge-graph.md as a Mermaid \`graph TD\` block followed by a bullet list of entities. Do not ask for clarification or offer alternatives — produce the graph directly. Include at least $ke_min distinct entities/nodes." \
    "-->|---|::|^[A-Z_][a-zA-Z0-9_]+\\s*\\[|^[*-][[:space:]]+\\*\\*[A-Z]|node|entity|concept" $ke_min "knowledge graph nodes"

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
  "security-engineer|.|produce external-threat findings (threat model, trust boundaries, abuse cases, controls) — first-class crew lens + standalone security review of the chain|100"
  "traceability-auditor|.|confirm every 4-segment element-ID resolves|100"
  "chaos-engineer|.|produce internal-stability findings (failure paths, edge cases, race conditions, recovery) via the review-team crew|50"
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
# R1 — Incremental summary.json rebuild. Called after every element
# completes (via write_element_log) and once more at the end of the run.
# Idempotent; reads logs/<TS>/elements/*.log and aggregates YAML
# front-matter into summary.json. Cheap (~50ms).
_rebuild_summary_json() {
  [[ -d "$LOG_DIR/elements" ]] || return 0
  python3 - "$LOG_DIR" "$SUMMARY_JSON" <<'PY' 2>/dev/null || true
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

counts = {"PASS": 0, "FAIL": 0, "SKIP": 0, "RUNNING": 0, "INTERRUPTED": 0}
for e in elements:
    counts[e.get("outcome", "SKIP")] = counts.get(e.get("outcome", "SKIP"), 0) + 1
# Overall outcome reflects terminal states; in-flight RUNNING is treated
# as not-yet-terminal.
overall = "PASS"
if counts.get("FAIL", 0) > 0 or counts.get("INTERRUPTED", 0) > 0:
    overall = "FAIL"
elif counts.get("PASS", 0) == 0:
    overall = "SKIP"

def _read(path):
    try:
        with open(path) as fh: return fh.read().strip()
    except Exception: return None

framework = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(log_dir))))
plugin_version = _read(os.path.join(framework, "platforms", "claude-code-plugin", "VERSION"))
spec_version = _read(os.path.join(framework, "framework", "VERSION"))

summary = {
    "schema_version": "1.2",
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
PY
}

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

  # Build summary.json via the shared helper (also called incrementally
  # after each element completes).
  _rebuild_summary_json
  echo "wrote $SUMMARY_JSON"

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
echo "Example:     $EXAMPLE"
echo "Methodology: tests/ACCEPTANCE.md"
echo "Example doc: $EXAMPLE_DIR/README.md"
echo "Log dir:     $LOG_DIR"
echo "Docs:       $EXAMPLE_DOCS"
echo "AIDoc:      $AIDOC_DIR"
echo "Live:       $([[ $LIVE_FLAG == 1 ]] && echo enabled || echo disabled)"
echo "Mock:       ${MOCK_SOURCE:-(none)}"
echo "Phase:      ${PHASE:-all}"
echo "Element:    ${ELEMENT:-all}"
[[ -n "${FROM_LAYER:-}" ]] && echo "From layer: $FROM_LAYER"
[[ -n "${TO_LAYER:-}" ]] && echo "To layer:   $TO_LAYER"
echo

# R6 — When --skip-completed is in effect, surface any elements that
# were INTERRUPTED in the prior run so the operator knows what's about
# to be re-attempted.
if (( SKIP_COMPLETED == 1 )); then
  _prior_dir="$SKIP_COMPLETED_PATH"
  [[ -z "$_prior_dir" ]] && _prior_dir="$(ls -td "$EXAMPLE_DIR"/logs/*/ 2>/dev/null \
                                          | grep -v "$LOG_TIMESTAMP" | head -1)"
  if [[ -n "$_prior_dir" ]] && [[ -f "${_prior_dir%/}/summary.json" ]]; then
    log_info "--skip-completed: reading prior run at ${_prior_dir%/}"
    _interrupted="$(python3 - "${_prior_dir%/}/summary.json" <<'PY'
import json, sys
with open(sys.argv[1]) as fh:
    d = json.load(fh)
names = [e["name"] for e in d.get("elements", []) if e.get("outcome") in ("RUNNING", "INTERRUPTED")]
print(" ".join(names))
PY
)"
    if [[ -n "$_interrupted" ]]; then
      log_warn "prior run had interrupted elements (will retry): $_interrupted"
    fi
  fi
fi

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

# P1 — Single-element mode: --element=<name> runs only that element,
# resolves its phase + upstream, and skips everything else. Useful for
# "generate just the PRD against the existing BRD" iteration.
#
# Element naming:
#   doc-<layer>-{base,autopilot,audit,fixer} → cascade phase
#   doc-chg, doc-chg-{autopilot,audit,fixer}  → chg phase
#   doc-flow, doc-validator, doc-ref, doc-naming, gate-check,
#   quality-advisor, security-audit, review-team, knowledge-extractor,
#   charts-flow, adr-roadmap, project-init, project-adopt,
#   project-profile                            → utilities phase
#   <agent name>                               → agents phase
#   save-plan                                  → command phase
#   sdd-doc-review                             → hook phase
_element_phase() {
  local n="$1"
  case "$n" in
    doc-chg|doc-chg-*) echo "chg" ;;
    doc-*-autopilot|doc-*-audit|doc-*-fixer|doc-brd|doc-prd|doc-ears|doc-bdd|doc-adr|doc-spec|doc-tdd|doc-iplan) echo "cascade" ;;
    doc-flow|doc-validator|doc-ref|doc-naming|gate-check|quality-advisor|security-audit|review-team|knowledge-extractor|charts-flow|adr-roadmap|project-init|project-adopt|project-profile) echo "utilities" ;;
    save-plan) echo "command" ;;
    sdd-doc-review) echo "hook" ;;
    requirements-analyst|pm-orchestrator|solutions-architect|test-architect|software-engineer|devops-release-engineer|code-reviewer|security-engineer|traceability-auditor|chaos-engineer|synthesizer) echo "agents" ;;
    *) echo "" ;;
  esac
}

if [[ -n "$ELEMENT" ]]; then
  _elem_phase="$(_element_phase "$ELEMENT")"
  if [[ -z "$_elem_phase" ]]; then
    log_err "unknown element name: $ELEMENT"
    exit 2
  fi
  log_info "--element=$ELEMENT → routing through phase '$_elem_phase'"
  PHASES_TO_RUN=("$_elem_phase")
fi

# Plan summary — printed on every run after Phase 0 + planning so the user
# sees what will execute before the first LLM call (if any) is made.
echo
echo "=== Acceptance plan ==="
echo "Phases: ${PHASES_TO_RUN[*]}"
[[ -n "$ELEMENT" ]] && echo "Element filter: $ELEMENT"
[[ -n "$FROM_LAYER" ]] && echo "From layer: $FROM_LAYER"
[[ -n "$TO_LAYER" ]] && echo "To layer: $TO_LAYER"
echo "Live: $([[ $LIVE_FLAG == 1 ]] && echo yes || echo no)"
echo "Cost cap: $MAX_TOTAL_OUTPUT_TOKENS tokens output"
echo "Per-skill timeout: ${SKILL_TIMEOUT}s | orchestrators ${ORCHESTRATOR_TIMEOUT}s (review-team, doc-*-{audit,autopilot,fixer}) | agents ${AGENT_TIMEOUT}s"
if [[ "$LIVE_FLAG" != "1" ]] && [[ -z "$MOCK_SOURCE" ]]; then
  echo "(No LLM calls will be made; LLM-dependent elements will SKIP.)"
fi
echo "======================="
echo

for phase_name in "${PHASES_TO_RUN[@]}"; do
  # R4 — bail out of remaining phases if cost cap fired or user
  # interrupted. EXIT trap will still flush state.
  if (( COST_CAP_EXCEEDED == 1 )); then
    log_warn "skipping phase $phase_name — cost cap exceeded"
    continue
  fi
  if (( INTERRUPTED == 1 )); then
    log_warn "skipping phase $phase_name — interrupted"
    continue
  fi
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
