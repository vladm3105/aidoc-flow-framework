#!/usr/bin/env bash
# reconcile-pin-currency-issue.sh — reconcile exactly ONE tracking issue against
# a pin-currency verdict produced by scripts/read-pin-currency-log.sh.
#
# WHY THIS IS A SCRIPT AND NOT INLINE YAML. `workflow_run` and
# `workflow_dispatch` both require the workflow file on the DEFAULT BRANCH, so
# nothing end-to-end runs on the PR branch that introduces it. Extracting the
# branchy create/edit/reopen/close logic is what makes it testable before merge.
# This repo has no prior `gh issue create/list/edit/close` usage in any workflow
# or script, so none of this logic is load-bearing-by-precedent either.
#
# Usage:
#   bash scripts/read-pin-currency-log.sh run.log \
#     | bash scripts/reconcile-pin-currency-issue.sh --repo O/R --run-url URL
#
# Options:
#   --repo O/R        target repository (default: $GITHUB_REPOSITORY)
#   --run-url URL     the standards-drift run the verdict came from
#   --input FILE      read the verdict from FILE instead of stdin
#   --assignee USER   who to notify (default: $PIN_CURRENCY_ASSIGNEE, else none)
#   --dry-run         execute reads, PRINT writes instead of running them
#
# GH="${GH:-gh}" adopts canon's own injectable-binary pattern
# (aidoc-flow-ci/sync/check-pin-currency.sh:21). It is what makes the tests real:
# they substitute a stub that returns a canned `gh issue list` response, so
# create-vs-edit-vs-reopen is driven by a fixture rather than by a live
# authenticated read. Without it the test would need `gh`, auth and network —
# and the suite it registers into runs on EVERY commit via an `always_run`
# pre-commit hook, so that would fail an offline contributor's commit.
set -uo pipefail

GH="${GH:-gh}"

# The idempotence key. Do not change it without migrating the existing issue:
# lookup is an exact title compare, so a renamed title creates a second issue.
TITLE='CI canon drift — stale @ci/v* pins'
LABEL='ci'
STATE_FENCE='pin-currency-state'
STAMP_PREFIX='last verified '

REPO="${GITHUB_REPOSITORY:-}"
RUN_URL=""
INPUT=""
ASSIGNEE="${PIN_CURRENCY_ASSIGNEE:-}"
DRY_RUN=0

die() { echo "::error::reconcile-pin-currency-issue: $*" >&2; exit 1; }
warn() { echo "::warning::reconcile-pin-currency-issue: $*"; }
note() { echo "::notice::reconcile-pin-currency-issue: $*"; }

# `shift 2` with only one argument left FAILS WITHOUT SHIFTING, and there is no
# `set -e` here — so a value-less trailing option spins this loop forever. The
# explicit arity check is what stops a typo from hanging an unattended job.
need_value() { [ "$1" -ge 2 ] || die "$2 requires a value"; }
while [ $# -gt 0 ]; do
  case "$1" in
    --repo)     need_value $# --repo;     REPO="$2";     shift 2;;
    --run-url)  need_value $# --run-url;  RUN_URL="$2";  shift 2;;
    --input)    need_value $# --input;    INPUT="$2";    shift 2;;
    --assignee) need_value $# --assignee; ASSIGNEE="$2"; shift 2;;
    --dry-run) DRY_RUN=1; shift;;
    *) die "unknown arg: $1";;
  esac
done
[ -n "$REPO" ] || die "--repo is required (or set GITHUB_REPOSITORY)"

# --- read the verdict --------------------------------------------------------
verdict=""; stale_count=0; canon=""; stale_files=""; drift_summary=""
while IFS='=' read -r key value; do
  case "$key" in
    verdict) verdict="$value";;
    stale_count) stale_count="$value";;
    canon) canon="$value";;
    stale_files) stale_files="$value";;
    drift_summary) drift_summary="$value";;
  esac
done < <(if [ -n "$INPUT" ]; then cat -- "$INPUT"; else cat; fi)

case "$verdict" in
  stale|clean|unresolved|skipped) ;;
  *) die "unrecognized verdict: '${verdict}'";;
esac

NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# --- gh plumbing -------------------------------------------------------------
# Reads always execute. Writes are printed under --dry-run so the whole call
# sequence is assertable without a live API write.
gh_read() { "$GH" "$@"; }
gh_write() {
  if [ "$DRY_RUN" -eq 1 ]; then
    printf 'DRY-RUN gh %s\n' "$*"
    return 0
  fi
  "$GH" "$@"
}

# --- find the one issue ------------------------------------------------------
# NOT `--search`: that goes through a tokenized, eventually-consistent index, so
# a just-created issue can be invisible and the next run duplicates it. Exact
# `jq` compare on the title instead.
#
# `--state all` because a stale → clean → stale cycle recurs once per canon
# release (the drift script resolves canon from main's VERSION, which this repo
# does not control), so `--state open` would create one issue per release rather
# than reopening one.
#
# `--limit 200` is load-bearing: the default is 30 and this repo is past #382,
# so a long-closed tracking issue falls off the first page, the exact-title
# compare finds nothing, and the run creates a DUPLICATE. It does age out
# eventually; raising it is a one-token change when it does.
#
# `body` is in the field list because the body is the only persistent store of
# the previous verdict — the comment trigger compares against it.
list_err="$(mktemp)"
found="$(gh_read issue list --repo "$REPO" --state all --limit 200 \
  --json number,title,state,body \
  --jq "[.[] | select(.title == \"${TITLE}\")] | first // empty" 2>"$list_err")" \
  || die "could not list issues on ${REPO}: $(tr '\n' ' ' <"$list_err")"
rm -f "$list_err"

# Every extraction below is `|| die`, NOT best-effort. `gh --jq` uses gh's own
# built-in jq, so the guard above passes even when the external `jq` these lines
# call is broken — and an unchecked failure would leave `issue_number` empty,
# which is indistinguishable from "no issue has ever existed" and routes
# straight to CREATE. A read failure must never be able to open a duplicate.
issue_number=""; issue_state=""; issue_body=""
if [ -n "$found" ]; then
  issue_number="$(jq -r '.number' <<<"$found")" \
    || die "could not parse the issue number out of the list response"
  issue_state="$(jq -r '.state' <<<"$found" | tr '[:upper:]' '[:lower:]')" \
    || die "could not parse the issue state out of the list response"
  # `tr -d '\r'`: a body hand-edited through the GitHub web UI comes back with
  # CRLF endings (HTML textareas submit them), and the state-block reader below
  # compares whole lines exactly. Without this, one web edit blanks every
  # previous-verdict field and the reader comments on every run thereafter.
  issue_body="$(jq -r '.body // ""' <<<"$found" | tr -d '\r')" \
    || die "could not parse the issue body out of the list response"
  case "$issue_number" in
    ''|*[!0-9]*) die "unusable issue number from the list response: '${issue_number}'";;
  esac
fi

# --- the machine-readable state block ---------------------------------------
# The human-facing prose above it is free to change without affecting the
# comparison; only these four fields decide whether to comment.
prev_state() { # $1 = key
  awk -v k="$1" -v f="$STATE_FENCE" '
    $0 == "```" f {inside=1; next}
    inside && $0 == "```" {inside=0}
    inside && index($0, k "=") == 1 {print substr($0, length(k) + 2)}
  ' <<<"$issue_body"
}

render_state_block() {
  printf '```%s\n' "$STATE_FENCE"
  printf 'verdict=%s\nstale_count=%s\ncanon=%s\nstale_files=%s\n' \
    "$verdict" "$stale_count" "$canon" "$stale_files"
  printf '```\n'
}

render_table() {
  [ -n "$stale_files" ] || return 0
  printf '| Caller | Pinned |\n| --- | --- |\n'
  tr ',' '\n' <<<"$stale_files" | while IFS='@' read -r file tag; do
    [ -n "$file" ] && printf '| `%s` | `%s` |\n' "$file" "$tag"
  done
  # NO trailing blank line here. Command substitution strips trailing newlines,
  # so one emitted at this level cannot survive into the heredoc below — the
  # blank line that terminates the GFM table has to be a literal line THERE.
  # Without it the remedy paragraph is absorbed into the table as junk rows,
  # which is every issue this tool opens.
}

render_body() {
  cat <<EOF
## Stale \`@ci/v*\` pins

\`standards-drift\` found **${stale_count}** caller file(s) pinned below canon
**\`${canon}\`**.

$(render_table)

**Remedy** — re-pin only. Never \`--update\`: that replaces whole caller bodies
and would clobber this repo's local overrides.

\`\`\`sh
CI_TAG=${canon} bash install/install.sh ${REPO} --repin
\`\`\`

The count is per **file**, not per call site — canon's \`sort -u\` collapses two
same-tag pins in one file to one, so a fully-stale repo reports fewer files than
it has \`uses:\` lines.

Other drift dimensions this run: \`${drift_summary}\`

Source run: ${RUN_URL:-(not recorded)}

${STAMP_PREFIX}${NOW}

$(render_state_block)
<sub>Opened and maintained by \`.github/workflows/pin-currency-reader.yml\`.
Edited in place each run. Do not rename the title — it is the idempotence key.
Closing this by hand is fine; the next stale reading reopens it.</sub>
EOF
}

render_resolved_body() {
  cat <<EOF
## \`@ci/v*\` pins are current

Every caller is pinned at or above canon **\`${canon}\`**. Nothing to do.

This issue is reopened automatically the next time \`standards-drift\` reports a
stale pin — which recurs once per canon release, because the drift script
resolves canon from \`main\`'s \`VERSION\` rather than anything this repo pins.

Other drift dimensions this run: \`${drift_summary}\`

Source run: ${RUN_URL:-(not recorded)}

${STAMP_PREFIX}${NOW}

$(render_state_block)
<sub>Opened and maintained by \`.github/workflows/pin-currency-reader.yml\`.
Do not rename the title — it is the idempotence key.</sub>
EOF
}

body_file="$(mktemp)"
comment_file="$(mktemp)"
trap 'rm -f "$body_file" "$comment_file"' EXIT

# --- silent verdicts: stamp only --------------------------------------------
# `unresolved` and `skipped` produce no verdict to act on, but they are exactly
# the failure modes that made the original signal invisible — so they still
# write a `last verified` line, making the READER's own staleness visible in the
# artifact it maintains.
#
# The stamp must PRESERVE the state block verbatim. Regenerating the body from
# the template here would clear the stored stale set, so the next identical
# `stale` reading would look like clean → stale and emit a spurious comment.
if [ "$verdict" = unresolved ] || [ "$verdict" = skipped ]; then
  if [ -z "$issue_number" ]; then
    # The steady state: creation happens only on `stale`, so with no issue there
    # is nothing to stamp. Not an error.
    note "verdict=${verdict} and no tracking issue exists — nothing to stamp"
    exit 0
  fi
  # Replace the stamp in place if present; APPEND it if not. A body that has
  # been hand-edited may have lost the line, and an awk that only substitutes
  # would then rewrite the body byte-identically and still report success —
  # a stamp that silently does nothing, on the one artifact whose whole job is
  # to make silence visible.
  awk -v p="$STAMP_PREFIX" -v now="$NOW" '
    index($0, p) == 1 { print p now; hit = 1; next }
    { print }
    END { if (!hit) { print ""; print p now } }
  ' <<<"$issue_body" >"$body_file"
  gh_write issue edit "$issue_number" --repo "$REPO" --body-file "$body_file" \
    || die "could not stamp issue #${issue_number}"
  note "verdict=${verdict} — stamped issue #${issue_number}, state unchanged"
  exit 0
fi

# --- clean -------------------------------------------------------------------
if [ "$verdict" = clean ]; then
  if [ -z "$issue_number" ] || [ "$issue_state" != open ]; then
    note "all pins current — no open tracking issue to close"
    exit 0
  fi
  # NOT render_body — that renders the STALE template, so closing would leave
  # behind a body headed "Stale @ci/v* pins", reporting 0 stale files and
  # offering a --repin command, as the artifact's final persisted state.
  render_resolved_body >"$body_file"
  gh_write issue edit "$issue_number" --repo "$REPO" --body-file "$body_file" \
    || warn "could not update body of #${issue_number} before closing"
  printf 'All \`@ci/v*\` pins are current as of \`%s\` (canon \`%s\`). Closing.\n\nSource run: %s\n' \
    "$NOW" "$canon" "${RUN_URL:-(not recorded)}" >"$comment_file"
  gh_write issue comment "$issue_number" --repo "$REPO" --body-file "$comment_file" \
    || warn "could not comment on #${issue_number}"
  gh_write issue close "$issue_number" --repo "$REPO" \
    || die "could not close #${issue_number}"
  note "all pins current — closed issue #${issue_number}"
  exit 0
fi

# --- stale -------------------------------------------------------------------
render_body >"$body_file"

if [ -z "$issue_number" ]; then
  # No issue has ever carried this title — create one.
  #
  # The label is applied non-fatally BY RETRY, not by `|| true`. `gh issue
  # create --label ci … || true` would make the whole creation non-fatal,
  # reintroducing exactly the invisibility this workflow exists to close.
  # The retry drops ONLY the label. The assignee is not on the create call at
  # all — see below.
  if ! create_out="$(gh_write issue create --repo "$REPO" --title "$TITLE" \
        --label "$LABEL" --body-file "$body_file" 2>&1)"; then
    warn "create with --label ${LABEL} failed; retrying unlabelled"
    create_out="$(gh_write issue create --repo "$REPO" --title "$TITLE" \
      --body-file "$body_file" 2>&1)" \
      || die "could not create the tracking issue on ${REPO}: ${create_out}"
  fi
  printf '%s\n' "$create_out"

  # Assignee is set AFTER creation, never as `--assignee` on the create call:
  # that flag ERRORS on a non-assignable user, which would fail both the create
  # AND its unlabelled retry, producing no issue at all. Setting it here makes
  # the failure non-fatal by construction — the issue exists either way.
  #
  # It matters because a `github-actions[bot]` issue notifies only repo
  # watchers, and a GITHUB_TOKEN-authored event fires no `issues`-triggered
  # automation, so without an assignee the artifact has no reader — which is
  # the failure this whole workflow exists to remove, one level up.
  if [ -n "$ASSIGNEE" ]; then
    new_ref="$(grep -oE 'https://[^[:space:]]*/issues/[0-9]+' <<<"$create_out" | tail -1)"
    if [ "$DRY_RUN" -eq 1 ]; then
      printf 'DRY-RUN gh issue edit <new-issue> --repo %s --add-assignee %s\n' \
        "$REPO" "$ASSIGNEE"
    elif [ -n "$new_ref" ]; then
      gh_write issue edit "$new_ref" --repo "$REPO" --add-assignee "$ASSIGNEE" \
        || warn "could not assign ${ASSIGNEE}; the issue was created and stands"
    else
      warn "could not determine the new issue URL; ${ASSIGNEE} not assigned"
    fi
  fi
  note "opened the tracking issue (${stale_count} stale pin file(s), canon ${canon})"
  exit 0
fi

prev_verdict="$(prev_state verdict)"
prev_count="$(prev_state stale_count)"
prev_files="$(prev_state stale_files)"

gh_write issue edit "$issue_number" --repo "$REPO" --body-file "$body_file" \
  || die "could not update issue #${issue_number}"

if [ "$issue_state" != open ]; then
  # Reopen, never recreate — see the --state all rationale above.
  gh_write issue reopen "$issue_number" --repo "$REPO" \
    || die "could not reopen #${issue_number}"
  printf 'Stale pins are back: **%s** caller file(s) below canon `%s`. Reopening.\n\nSource run: %s\n' \
    "$stale_count" "$canon" "${RUN_URL:-(not recorded)}" >"$comment_file"
  gh_write issue comment "$issue_number" --repo "$REPO" --body-file "$comment_file" \
    || warn "could not comment on #${issue_number}"
  note "reopened issue #${issue_number}"
  exit 0
fi

# Already open. Comment ONLY when the verdict or the stale set actually moved.
#
# The trigger is the state block, NOT the body: the body embeds a run URL that
# changes every week, so body-diffing would comment on every single run. And
# without the count/set comparison a count going 10 → 15 would be a silent edit
# with no notification at all, which defeats the point of having an assignee.
if [ "$prev_count" != "$stale_count" ] || [ "$prev_files" != "$stale_files" ] \
   || [ "$prev_verdict" != stale ]; then
  printf 'Stale pin set changed: **%s** → **%s** caller file(s) (canon `%s`).\n\nSource run: %s\n' \
    "${prev_count:-unknown}" "$stale_count" "$canon" "${RUN_URL:-(not recorded)}" >"$comment_file"
  gh_write issue comment "$issue_number" --repo "$REPO" --body-file "$comment_file" \
    || warn "could not comment on #${issue_number}"
  note "issue #${issue_number} updated and commented (${prev_count:-unknown} → ${stale_count})"
else
  note "issue #${issue_number} updated silently (unchanged at ${stale_count} stale file(s))"
fi
