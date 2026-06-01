#!/usr/bin/env bash
# tests/review/run-claude-review.sh
# Invoke a Claude Code code-reviewer agent on the current diff.
set -uo pipefail
BASE="${BASE_REF:-origin/main}"
MAX_BYTES="${MAX_DIFF_BYTES:-262144}"

FULL_DIFF="$(git diff "${BASE}"...HEAD 2>&1 || true)"
DIFF_BYTES=${#FULL_DIFF}

if (( DIFF_BYTES > MAX_BYTES )); then
  echo "::warning::diff is ${DIFF_BYTES} bytes (>${MAX_BYTES}); truncating per-file" >&2
  TRUNCATED=$(echo "$FULL_DIFF" | awk '
    /^diff --git/ { if (n>0) print "..."; n=0; print; next }
    { if (n<200) { print; n++ } }
  ')
  DIFF_FOR_REVIEW="$TRUNCATED"
else
  DIFF_FOR_REVIEW="$FULL_DIFF"
fi

PROMPT="$(cat <<EOF
Review the diff below for security, correctness, framework convention adherence,
and any silent failure patterns. Surface ONLY high-confidence findings. For each:
  SEVERITY: BLOCKER|CRITICAL|MAJOR|MINOR
  FILE: <path>:<line>
  FINDING: <one sentence>
  EVIDENCE: <quote>

Stop after 12 findings max. Prefer no findings over speculative ones.

--- DIFF ---
${DIFF_FOR_REVIEW}
EOF
)"
claude --dangerously-skip-permissions -p "$PROMPT"
