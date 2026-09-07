#!/usr/bin/env bash
#
# tests/scripts/test-plugin.sh — Automated end-to-end verification of the
# aidoc-flow Claude Code plugin.
#
# Runs from framework root (this script lives at framework/tests/scripts/).
#
# Log layout (per-run directory keyed by ISO timestamp):
#   - Example-driven suite (default — Phase 3 lint + Phase 4 live probe target
#     a specific example):
#       examples/<NAME>/logs/<LOG_TIMESTAMP>/plugin-test.log
#       examples/<NAME>/logs/<LOG_TIMESTAMP>/probe-doc-flow.txt
#   - Fixture-driven suites (unit / layer / fullpath / pre-deploy / packaging /
#     release / smoke / review — none of them touch examples/):
#       tests/logs/<LOG_TIMESTAMP>/plugin-test.log
#
# Default suite (legacy 4-phase harness, LIVE on by default):
#   1. Static plugin validation       — `claude plugin validate` (+ `--strict`)
#   2. Framework conformance suite    — `python3 -m unittest` (70+ tests)
#   3. sdd_doc_lint smoke             — structural lint of the demo example
#   4. Live skill probe               — `claude -p` invokes /aidoc-flow:doc-flow
#                                       (with --dangerously-skip-permissions so
#                                       the non-interactive run never prompts;
#                                       the probe is read-only — no mutations).
#                                       Output streams live, is captured to a
#                                       probe file, then grepped for banned
#                                       confabulation patterns ("compact
#                                       variant", "documented walkthrough",
#                                       "pinned to lint", "enterprise template").
#
# Usage:
#   bash tests/scripts/test-plugin.sh [--no-live]
#       — legacy 4-phase run (live ON by default; --no-live skips Phase 4)
#
#   bash tests/scripts/test-plugin.sh --suite=<name> [--layer=<x>] [--live|--no-live] [--review]
#       Suites:
#         default     same as legacy 4-phase (live ON unless --no-live)
#         unit        tests/unit
#         layer       tests/acceptance/deterministic/test_layer_<LAYER>
#                     (+ live counterpart if --live)
#         fullpath    tests/acceptance/deterministic/test_fullpath
#                     (+ live counterpart if --live)
#         pre-deploy  unit + acceptance/deterministic + packaging + release
#                     (+ live acceptance if --live)
#         smoke       tests/smoke
#         review      tests/review (REVIEW=1)
#         all         recursive `$0 --suite=pre-deploy --live`
#
# Output:  stdout (live) + per-run log directory (see "Log layout" above)
#          summary table of per-phase PASS/FAIL/SKIP at end

set -uo pipefail

FRAMEWORK="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$FRAMEWORK"

PLUGIN_DIR="$FRAMEWORK/platforms/claude-code-plugin"
EXAMPLE_DIR="$FRAMEWORK/examples/url-shortener"
EXAMPLE_DOCS="$EXAMPLE_DIR/docs"
LOG_TIMESTAMP="$(date +%Y-%m-%dT%H%M%S)"
# LOG_DIR + LOG are resolved per-suite after argument parsing below.
LOG_DIR=""
LOG=""

# -----------------------------------------------------------------------------
# Argument parsing (two-pass: --suite first so --live defaults can be resolved)
# -----------------------------------------------------------------------------
SUITE=""
LAYER=""
LIVE_FLAG=""   # "1", "0", or "" (unset → suite-specific default)
REVIEW=0
SKIP_LIVE=0    # legacy --no-live flag for default suite

for arg in "$@"; do
  case "$arg" in
    --suite=*) SUITE="${arg#--suite=}" ;;
    --layer=*) LAYER="${arg#--layer=}" ;;
    --live)    LIVE_FLAG="1" ;;
    --no-live) LIVE_FLAG="0"; SKIP_LIVE=1 ;;
    --review)  REVIEW=1 ;;
    -h|--help) sed -n '2,50p' "$0"; exit 0 ;;
    *) echo "unknown flag: $arg"; exit 2 ;;
  esac
done

# Default suite preserves legacy back-compat: live ON unless --no-live.
if [[ -z "$SUITE" ]]; then
  SUITE="default"
fi

# Resolve live default per suite if not explicitly set.
if [[ -z "$LIVE_FLAG" ]]; then
  case "$SUITE" in
    default) LIVE_FLAG="1" ;;   # legacy behavior
    *)       LIVE_FLAG="0" ;;   # all other suites default OFF
  esac
fi

# Resolve per-run log directory.
# The default suite is example-driven (Phase 3 lints examples/<NAME>/docs;
# Phase 4 probes against examples/<NAME>); its log goes under that example.
# All other suites operate on fixtures or shared spec — log under tests/logs/.
case "$SUITE" in
  default) LOG_DIR="$EXAMPLE_DIR/logs/$LOG_TIMESTAMP" ;;
  *)       LOG_DIR="$FRAMEWORK/tests/logs/$LOG_TIMESTAMP" ;;
esac
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/plugin-test.log"

# Banned confabulation patterns — the fix landed in framework PR #35 is
# specifically supposed to keep these out of doc-flow / doc-*-audit output.
BANNED='compact [0-9]+-section|documented[ -]walkthrough|pinned to (sdd_doc_)?lint|enterprise template|10-section markdown'

declare -i FAILED=0
declare -a PHASE_RESULTS=()

section() {
  printf '\n=================================================================\n'
  printf '  %s\n' "$*"
  printf '=================================================================\n'
}

run() {
  # run <label> <cmd...>
  local label="$1"; shift
  printf '\n▸ %s\n' "$label"
  printf '  $ %s\n' "$*"
  local out rc
  out="$("$@" 2>&1)"; rc=$?
  printf '%s\n' "$out" | sed 's/^/  /'
  if [[ $rc -eq 0 ]]; then
    printf '  PASS\n'
  else
    printf '  FAIL (exit %d)\n' "$rc"
    FAILED+=1
  fi
  return $rc
}

phase_record() {
  # phase_record <phase-name> <PASS|FAIL|SKIP>
  PHASE_RESULTS+=("$1|$2")
}

phase_check() {
  # phase_check <phase-name> <FAILED-counter-before-phase>
  local name="$1" pre="$2"
  if (( FAILED > pre )); then
    phase_record "$name" "FAIL"
  else
    phase_record "$name" "PASS"
  fi
}

# Tee everything to log
exec > >(tee -a "$LOG") 2>&1

echo "aidoc-flow plugin test run — $LOG_TIMESTAMP"
echo "Framework: $FRAMEWORK"
echo "Plugin:    $PLUGIN_DIR"
echo "Log dir:   $LOG_DIR"
echo "Suite:     $SUITE"
echo "Live:      $([[ "$LIVE_FLAG" == "1" ]] && echo 'enabled' || echo 'disabled')"
[[ -n "$LAYER" ]] && echo "Layer:     $LAYER"
[[ "$REVIEW" -eq 1 ]] && echo "Review:    enabled"

# -----------------------------------------------------------------------------
# run_phase_1_to_4: the legacy 4-phase harness, factored into a function so
# new suites can re-use it. Honors $LIVE_FLAG for phase 4 (1 = run; 0 = skip).
# -----------------------------------------------------------------------------
run_phase_1_to_4() {
  # Phase 1 — Static plugin validation
  section "Phase 1 — Static plugin validation"
  local PRE=$FAILED
  if ! command -v claude >/dev/null 2>&1; then
    echo "  WARN: 'claude' CLI not on PATH — skipping Phase 1"
    phase_record "Phase 1 — Static plugin validation" "SKIP"
  else
    run "claude plugin validate"               claude plugin validate "$PLUGIN_DIR" || true
    run "claude plugin validate --strict (R1)" claude plugin validate "$PLUGIN_DIR" --strict || true
    phase_check "Phase 1 — Static plugin validation" "$PRE"
  fi

  # Phase 2 — Framework conformance suite
  section "Phase 2 — Framework conformance suite"
  PRE=$FAILED
  run "python -m unittest discover tests/conformance" \
    bash -c "cd '$FRAMEWORK/tests/conformance' && python3 -m unittest discover -q" || true
  phase_check "Phase 2 — Framework conformance suite" "$PRE"

  # Phase 3 — sdd_doc_lint on demo example
  section "Phase 3 — sdd_doc_lint on demo example"
  PRE=$FAILED
  if [[ ! -d "$EXAMPLE_DOCS" ]] || [[ -z "$(find "$EXAMPLE_DOCS" -name '*.md' -print -quit 2>/dev/null)" ]]; then
    echo "  SKIPPED: $EXAMPLE_DOCS is missing or empty (demo corpus cleared pending regeneration)"
    phase_record "Phase 3 — sdd_doc_lint on demo example" "SKIP"
  else
    run "sdd_doc_lint $EXAMPLE_DOCS" \
      bash -c "PYTHONPATH='$PLUGIN_DIR' python3 -m sdd_doc_lint '$EXAMPLE_DOCS'" || true
    phase_check "Phase 3 — sdd_doc_lint on demo example" "$PRE"
  fi

  # Phase 4 — Live skill probe
  section "Phase 4 — Live skill probe (claude -p /aidoc-flow:doc-flow)"
  PRE=$FAILED
  if [[ "$LIVE_FLAG" != "1" ]]; then
    echo "  SKIPPED via --no-live"
    phase_record "Phase 4 — Live skill probe" "SKIP"
  elif ! command -v claude >/dev/null 2>&1; then
    echo "  WARN: 'claude' CLI not on PATH — skipping Phase 4"
    phase_record "Phase 4 — Live skill probe" "SKIP"
  else
    local PROBE="$LOG_DIR/probe-doc-flow.txt"
    echo
    echo "▸ /aidoc-flow:doc-flow against $EXAMPLE_DIR"
    echo "  $ (cd $EXAMPLE_DIR; claude --plugin-dir $PLUGIN_DIR -p '/aidoc-flow:doc-flow ...')"
    # Stream live: tee captures to $PROBE while sed indents output to stdout
    # (and through the top-level exec tee, into $LOG).
    (
      cd "$EXAMPLE_DIR"
      claude \
        --plugin-dir "$PLUGIN_DIR" \
        --dangerously-skip-permissions \
        -p "/aidoc-flow:doc-flow scan the corpus and report position plus any template-conformance drift findings" 2>&1
    ) | tee "$PROBE" | sed 's/^/  /'
    local rc=${PIPESTATUS[0]}
    if [[ $rc -ne 0 ]]; then
      printf '  FAIL: claude -p exited %d\n' "$rc"
      FAILED+=1
    fi

    echo
    echo "▸ Confabulation pattern check"
    echo "  Pattern: $BANNED"
    if grep -qiE "$BANNED" "$PROBE"; then
      echo "  FAIL: doc-flow output contains banned confabulation language:"
      grep -niE "$BANNED" "$PROBE" | sed 's/^/    /'
      FAILED+=1
    else
      echo "  PASS: no banned confabulation language in output"
    fi
    phase_check "Phase 4 — Live skill probe" "$PRE"
  fi
}

# -----------------------------------------------------------------------------
# Suite dispatch
# -----------------------------------------------------------------------------
case "$SUITE" in
  default)
    run_phase_1_to_4
    ;;

  unit)
    section "Suite: unit — tests/unit"
    PRE=$FAILED
    run "python3 -m unittest discover tests/unit" \
      bash -c "cd '$FRAMEWORK' && python3 -m unittest discover tests/unit -v" || true
    phase_check "Suite: unit" "$PRE"
    ;;

  layer)
    if [[ -z "$LAYER" ]]; then
      echo "  ERROR: --suite=layer requires --layer=<x>"
      exit 2
    fi
    section "Suite: layer — test_layer_${LAYER} (deterministic)"
    PRE=$FAILED
    run "deterministic test_layer_${LAYER}" \
      bash -c "cd '$FRAMEWORK' && python3 -m unittest tests.acceptance.deterministic.test_layer_${LAYER} -v" || true
    phase_check "Suite: layer (deterministic)" "$PRE"

    if [[ "$LIVE_FLAG" == "1" ]]; then
      section "Suite: layer — test_layer_${LAYER}_live (LIVE)"
      PRE=$FAILED
      run "live test_layer_${LAYER}_live" \
        bash -c "cd '$FRAMEWORK' && LIVE=1 python3 -m unittest tests.acceptance.live.test_layer_${LAYER}_live -v" || true
      phase_check "Suite: layer (live)" "$PRE"
    fi
    ;;

  fullpath)
    section "Suite: fullpath — test_fullpath (deterministic)"
    PRE=$FAILED
    run "deterministic test_fullpath" \
      bash -c "cd '$FRAMEWORK' && python3 -m unittest tests.acceptance.deterministic.test_fullpath -v" || true
    phase_check "Suite: fullpath (deterministic)" "$PRE"

    if [[ "$LIVE_FLAG" == "1" ]]; then
      section "Suite: fullpath — test_fullpath_live (LIVE)"
      PRE=$FAILED
      run "live test_fullpath_live" \
        bash -c "cd '$FRAMEWORK' && LIVE=1 python3 -m unittest tests.acceptance.live.test_fullpath_live -v" || true
      phase_check "Suite: fullpath (live)" "$PRE"
    fi
    ;;

  pre-deploy)
    section "Suite: pre-deploy — unit + acceptance/deterministic + packaging + release"
    PRE=$FAILED
    run "unit" \
      bash -c "cd '$FRAMEWORK' && python3 -m unittest discover tests/unit -v" || true
    phase_check "Suite: pre-deploy — unit" "$PRE"

    PRE=$FAILED
    run "acceptance/deterministic" \
      bash -c "cd '$FRAMEWORK' && python3 -m unittest discover tests/acceptance/deterministic -v" || true
    phase_check "Suite: pre-deploy — acceptance/deterministic" "$PRE"

    PRE=$FAILED
    run "packaging" \
      bash -c "cd '$FRAMEWORK' && python3 -m unittest discover tests/packaging -v" || true
    phase_check "Suite: pre-deploy — packaging" "$PRE"

    PRE=$FAILED
    run "release" \
      bash -c "cd '$FRAMEWORK' && python3 -m unittest discover tests/release -v" || true
    phase_check "Suite: pre-deploy — release" "$PRE"

    if [[ "$LIVE_FLAG" == "1" ]]; then
      PRE=$FAILED
      run "acceptance/live (LIVE)" \
        bash -c "cd '$FRAMEWORK' && LIVE=1 python3 -m unittest discover tests/acceptance/live -v" || true
      phase_check "Suite: pre-deploy — acceptance/live" "$PRE"
    fi
    ;;

  smoke)
    section "Suite: smoke — tests/smoke"
    PRE=$FAILED
    run "python3 -m unittest discover tests/smoke" \
      bash -c "cd '$FRAMEWORK' && python3 -m unittest discover tests/smoke -v" || true
    phase_check "Suite: smoke" "$PRE"
    ;;

  review)
    section "Suite: review — tests/review (REVIEW=1)"
    PRE=$FAILED
    run "REVIEW=1 python3 -m unittest discover tests/review" \
      bash -c "cd '$FRAMEWORK' && REVIEW=1 python3 -m unittest discover tests/review -v" || true
    phase_check "Suite: review" "$PRE"
    ;;

  all)
    section "Suite: all — recursive into --suite=pre-deploy --live"
    exec "$0" --suite=pre-deploy --live
    ;;

  *)
    echo "unknown suite: $SUITE"
    exit 2
    ;;
esac

# -----------------------------------------------------------------------------
section "Summary"
# -----------------------------------------------------------------------------
if (( ${#PHASE_RESULTS[@]} > 0 )); then
  printf '  %-55s %s\n' "Phase" "Result"
  printf '  %-55s %s\n' "-------------------------------------------------------" "------"
  for entry in "${PHASE_RESULTS[@]}"; do
    name="${entry%%|*}"
    status="${entry##*|}"
    printf '  %-55s %s\n' "$name" "$status"
  done
  echo
fi

if (( FAILED == 0 )); then
  echo "  ALL CHECKS PASSED"
  echo "  Log: $LOG"
  exit 0
else
  echo "  FAILED ($FAILED check$( ((FAILED==1)) || printf s ))"
  echo "  Log: $LOG"
  exit 1
fi
