#!/usr/bin/env bash
# read-pin-currency-log.sh — parse a completed `standards-drift` run log and
# emit the pin-currency verdict as GITHUB_OUTPUT-style key=value lines.
#
# WHY A LOG PARSER AND NOT AN API READ. The pin-currency signal exists on
# exactly one surface. Canon's reusable declares `inputs:` only and no
# `outputs:`, so a caller job receives nothing; the drift script writes nothing
# to $GITHUB_STEP_SUMMARY; and the check-run annotations API caps at 10 warnings
# per level, which on the measured run dropped all ten pin-currency lines
# (they are emitted at the script's tail). The run log is the only complete
# surface. See plans/PIN-CURRENCY-READER-PLAN.md §"What the measurements
# changed" for the four-surface table and its measurements.
#
# This script is deliberately pure: a file path in, key=value out. No network,
# no `gh`, no GitHub context — so it is unit-testable against checked-in
# fixtures before the workflow that calls it can ever run (both `workflow_run`
# and `workflow_dispatch` require the file on the default branch).
#
# Usage: bash scripts/read-pin-currency-log.sh <path-to-run-log>
#
# Emits: verdict, stale_count, canon, stale_files, drift_summary
#
# Verdicts (exit 0):
#   stale       N stale pin(s), N > 0, with a well-formed canon token
#   clean       all pins current, with a well-formed canon token
#   unresolved  canon's `curl` of main's VERSION failed; the pin script exits 0
#               before it ever audits, so there is no verdict to honour
#   skipped     no verdict line at all — canon's documented `::notice::` skip,
#               or `stop_uncheckable` exiting before the pin-currency tail
#
# Exits NON-ZERO on: a missing/unreadable log, a log with no evidence the drift
# script ran at all (truncated, empty, or from the wrong run), a verdict line
# whose canon token is malformed, or two contradictory verdict lines.
#
# The malformed-token check is load-bearing, not defensive tidiness. If canon's
# VERSION fetch returns an error page rather than failing, `ver_cmp` compares
# non-numeric fields under `2>/dev/null`, every comparison falls through to
# equal, and the script prints `all pins current ✅` — a false clean. Honouring
# it would CLOSE the tracking issue on a transient. Filed upstream; guarded here.
set -uo pipefail

die() { echo "::error::read-pin-currency-log: $*" >&2; exit 1; }

[ $# -eq 1 ] || die "usage: $0 <path-to-run-log>"
LOG="$1"
[ -f "$LOG" ] || die "log not found: $LOG"
[ -s "$LOG" ] || die "log is empty: $LOG"

# `gh run view --log` prefixes every line with "job<TAB>step<TAB>timestamp ".
# Strip it, then drop the runner's command echoes — those replay the workflow's
# own `run:` block, comments included, and its comments mention pin-currency.
#
# Echoes are identifiable by their colour sequence, which `gh` renders as the
# two literal characters `^` `[` — NOT as a raw ESC byte. A real download
# contains zero 0x1b; matching on `$'\x1b'` here would silently filter nothing.
# Measured against run 30257877863: 0 raw ESC, 68 literal `^[`.
#
# Anchoring every match to the start of the stripped message is the second half
# of the guard: real output begins with `pin-currency:` or a `##[...]` marker.
MSGS="$(cut -f3- -- "$LOG" | sed -e 's/^[0-9][0-9-]*T[0-9:.]*Z //' | grep -v '\^\[' || true)"

# --- positive evidence that the drift script RAN TO COMPLETION ---------------
# Without this, a truncated or wrong-run log has no verdict line and would parse
# as a benign `skipped` — exit 0, no signal — which is precisely the silent
# failure this whole workflow exists to remove.
#
# It must be a TERMINAL marker. The bare `check-standards-drift:` prefix is NOT
# one: the script emits an opening `repo=… tier=…` header under the same prefix
# before auditing anything, plus a `cannot check <family>` warning per unreadable
# control family. In the measured run the first of those lands 24 lines ahead of
# the pin-currency section, so a log truncated anywhere in between would satisfy
# a prefix test and report `skipped` while ten stale pins sat in the real run.
# That window is reachable: `workflow_run: completed` fires while the log
# archive is still assembling, and a partial archive is non-empty.
#
# Both markers below are emitted only at the end: the summary line closes every
# completed run, and `coverage —` is emitted by `emit_coverage`, which runs both
# at normal termination and from every `stop_uncheckable` early exit.
grep -qE '^(##\[[a-z]*\])?check-standards-drift: ([0-9]+ drift,|coverage —)' <<<"$MSGS" \
  || die "no terminal 'check-standards-drift:' line in $LOG (no summary and no coverage) — truncated, empty, or the wrong run"

drift_summary="$(sed -n 's/^check-standards-drift: \(.*drift,.*\)$/\1/p' <<<"$MSGS" | tail -1)"

# The canon token comes from the audit header, which the pin script prints only
# once it has resolved a token. An `unresolved` run exits before that line.
canon="$(sed -n 's/^pin-currency: auditing .* against canon \(.*\)$/\1/p' <<<"$MSGS" | tail -1)"

emit() {
  printf 'verdict=%s\n'       "$1"
  printf 'stale_count=%s\n'   "$2"
  printf 'canon=%s\n'         "$3"
  printf 'stale_files=%s\n'   "$4"
  printf 'drift_summary=%s\n' "$drift_summary"
  exit 0
}

# --- unresolved, tested BEFORE the no-verdict-line fallback ------------------
# An `unresolved` log satisfies `skipped`'s definition (it has no verdict line),
# so checking `skipped` first would swallow it. Order is load-bearing.
if grep -q '^##\[warning\]pin-currency: could not resolve canon VERSION' <<<"$MSGS"; then
  emit unresolved 0 "" ""
fi

stale_line="$(grep -m1 '^pin-currency: [0-9][0-9]* stale pin(s)' <<<"$MSGS" || true)"
clean_line="$(grep -m1 '^pin-currency: all pins current' <<<"$MSGS" || true)"

[ -n "$stale_line" ] && [ -n "$clean_line" ] \
  && die "contradictory verdicts in $LOG — both a stale count and 'all pins current'"

# --- no verdict line: canon's documented skip paths --------------------------
if [ -z "$stale_line" ] && [ -z "$clean_line" ]; then
  emit skipped 0 "" ""
fi

# A verdict is only honoured behind a well-formed canon token — see the header.
[[ "$canon" =~ ^ci/v[0-9]+\.[0-9]+\.[0-9]+$ ]] \
  || die "verdict line present but canon token is malformed: '${canon}' (expected ci/vX.Y.Z)"

if [ -n "$clean_line" ]; then
  emit clean 0 "$canon" ""
fi

stale_count="$(sed -n 's/^pin-currency: \([0-9][0-9]*\) stale pin(s).*/\1/p' <<<"$stale_line")"
[ "${stale_count:-0}" -gt 0 ] 2>/dev/null \
  || die "stale verdict line reports ${stale_count:-<unparseable>} stale pins — expected > 0"

# One entry per stale caller, as `<file>@<pinned-tag>`, sorted. Sorted because
# the reconcile compares this set against the one stored in the issue body to
# decide whether to comment; an unstable order would comment every run — and
# `LC_ALL=C` because that comparison spans runs, so a locale difference between
# two runners would reorder the set and look like a change.
stale_files="$(
  sed -n 's/^##\[warning\]pin-currency: \([^ ]*\) pinned @\([^ ]*\) .*/\1@\2/p' <<<"$MSGS" \
    | LC_ALL=C sort -u | paste -sd, -
)"

emit stale "$stale_count" "$canon" "$stale_files"
