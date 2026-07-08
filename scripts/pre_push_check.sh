#!/usr/bin/env bash
# aidoc-flow-ci canon pre_push_check.sh — run local validation before push
# so mechanical issues don't burn a long-running remote ai-review round.
# Wired via `.pre-commit-config.yaml` `default_install_hook_types:
# [pre-commit, pre-push]` per PLAN-002 §4.2; safe to run by hand:
# `scripts/pre_push_check.sh`
#
# CANONICAL SCOPE (per PLAN-002 §4.1):
#   1. markdownlint (skipped-with-notice if not installed)
#   2. yamllint (skipped-with-notice if not installed)
#   3. actionlint on .github/workflows/*.yml (skipped-with-notice if absent)
#   4. shellcheck (skipped-with-notice if not installed)
#   5. OPS-0069 audit-trail phrase check (mandatory; scans commit range)
#
# Repo-specific extra checks (e.g., verified-planning `check_plan.py`,
# operations classify-parity) live in a consumer-side wrapper
# `scripts/pre_push_check_<repo>.sh` that sources this canon + adds its
# own. Wrapper preserves this script's rc-accumulator pattern.
#
# OPS-0069 says: this hook does NOT — and cannot — perform the mandatory
# multi-agent SELF-REVIEW for you. That is an agent step (dispatch the
# diff-class-matched sub-agents and fold their findings). The hook
# requires a proof-of-dispatch AUDIT-TRAIL PHRASE in one of the pushed
# commits' messages — a paper trail, not a review substitute.
#
# NO env-var escape hatch (matches OPS-0069 removal of
# SKIP_LOCAL_AI_REVIEW). Only bypass path: `git push --no-verify` (git
# primitive; caught by CI belt-and-suspenders `audit-trail-check.yml`).
#
# `set -uo pipefail` (NOT -e) — the rc accumulator pattern below depends
# on per-check failures being non-fatal so all checks run per push.

set -uo pipefail

# M1 (code-review fold): fail-fast on bash <4. macOS ships bash 3.2 as
# /bin/bash (GPLv3 avoidance); mapfile requires bash 4+. Without this
# guard the script limps with empty arrays + silent audit-trail failure.
if (( BASH_VERSINFO[0] < 4 )); then
  echo "::error::pre_push_check.sh requires bash 4+ (found ${BASH_VERSION:-unknown})." >&2
  echo "::error::On macOS the default /bin/bash is 3.2. Install a newer bash (e.g., 'brew install bash') and ensure it precedes /bin/bash on PATH." >&2
  exit 2
fi

# M2 (code-review fold): script-branded error on non-git-repo invocation
# so the operator sees the source of the exit-2 (not a naked git error).
toplevel="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "::error::pre_push_check.sh must run inside a git working tree." >&2
  exit 2
}
cd "$toplevel" || exit 2

# --- changed-files calculation ---
# base = merge-base with origin/main (fall back to local main, then to
# the empty tree for a fresh repo).
BASE="$(git merge-base HEAD origin/main 2>/dev/null \
        || git merge-base HEAD main 2>/dev/null \
        || git rev-list --max-parents=0 HEAD | tail -1)"
mapfile -t CHANGED < <(git diff --name-only --diff-filter=ACMR "$BASE"...HEAD 2>/dev/null)
if [ "${#CHANGED[@]}" -eq 0 ]; then
  echo "pre_push_check: no changed files vs base — skipping mechanical linters."
  CHANGED=()
fi

rc=0
have() { command -v "$1" >/dev/null 2>&1; }
exists() { [ -f "$1" ]; }
filter() {
  local pat="$1" f
  for f in "${CHANGED[@]:-}"; do
    [ -n "$f" ] && [[ "$f" =~ $pat ]] && exists "$f" && printf '%s\n' "$f"
  done
}

run() {
  # $1 = label ; rest = command (only invoked when FILES non-empty)
  local label="$1"; shift
  [ "${#FILES[@]}" -gt 0 ] || return 0
  echo "── ${label} (${#FILES[@]} file(s)) ──"
  "$@" "${FILES[@]}" || { echo "::error::${label} found issues — fix before pushing."; rc=1; }
}

# --- 1. markdownlint ---
mapfile -t FILES < <(filter '\.md$')
if [ "${#FILES[@]}" -gt 0 ]; then
  if have markdownlint-cli2; then
    run "markdownlint" markdownlint-cli2
  elif have npx && npx --no-install markdownlint-cli2 --version >/dev/null 2>&1; then
    run "markdownlint (npx)" npx --no-install markdownlint-cli2
  else
    echo "ℹ️  markdownlint skipped (markdownlint-cli2 not resolvable) — CI enforces."
  fi
fi

# --- 2. yamllint ---
mapfile -t FILES < <(filter '\.ya?ml$')
if [ "${#FILES[@]}" -gt 0 ]; then
  if have yamllint; then
    if [ -f .yamllint.yaml ]; then
      run "yamllint" yamllint -c .yamllint.yaml
    else
      run "yamllint" yamllint
    fi
  else
    echo "ℹ️  yamllint skipped (not installed)."
  fi
fi

# --- 3. actionlint on .github/workflows/ ---
mapfile -t FILES < <(filter '^\.github/workflows/.*\.ya?ml$')
if [ "${#FILES[@]}" -gt 0 ]; then
  if have actionlint; then
    run "actionlint" actionlint
  else
    echo "ℹ️  actionlint skipped (not installed) — recommended for local workflow lint."
  fi
fi

# --- 4. shellcheck ---
mapfile -t FILES < <(filter '\.sh$')
if [ "${#FILES[@]}" -gt 0 ]; then
  if have shellcheck; then
    run "shellcheck" shellcheck -S warning
  else
    echo "ℹ️  shellcheck skipped (not installed)."
  fi
fi

# --- 5. OPS-0069 audit-trail phrase check ---
#
# Every push must carry an audit-trail line in the NEW commits' messages
# proving that either (a) the OPS-0065 diff-class sub-agents were
# dispatched and their verdict folded, or (b) the founder explicitly
# OK'd skipping.
#
# Scan ONLY the commits being newly pushed. Scope: `@{upstream}..HEAD`
# when upstream is configured (so each push carries a fresh phrase on
# its new commits); falls back to `origin/main..HEAD` on the very first
# push before upstream is set. The BASE..HEAD merge-base range does NOT
# advance between pushes — once a phrase-bearing commit was anywhere
# in that range, subsequent pushes of never-reviewed commits also
# passed. Broken; do not revert.
#
# Canonical audit-trail phrases:
#   "Multi-agent self-review per OPS-0065"  — standard case; commit body
#                                             must also name the agents
#                                             + verdict.
#   "Self-review skipped per founder OK"    — override case only when
#                                             the founder authorizes the
#                                             skip in-session; reason
#                                             MUST follow the phrase.
#
# The hook verifies the phrase, not the review itself. Falsifying the
# phrase is a governance-Rule-2 violation caught at the CI ai-review
# layer.
#
# shellcheck disable=SC1083  # @{upstream} is git ref-syntax, not shell brace expansion
upstream_ref="$(git rev-parse --abbrev-ref --symbolic-full-name @{upstream} 2>/dev/null || echo '')"
if [ -n "$upstream_ref" ] && git rev-parse --verify --quiet "$upstream_ref" >/dev/null; then
  commit_range="${upstream_ref}..HEAD"
else
  # First push (no upstream yet) — scan since main-divergence.
  commit_range="origin/main..HEAD"
fi
push_msgs="$(git log --format=%B "$commit_range" 2>/dev/null || echo '')"

# --- Exemption logic (mirrors PLAN-002 §4.6; CI side implements the same +
# the two-signal skip-audit-trail label which needs PR context) ---
#
# Exemption 1: bot-authored — if ALL commits in range are authored by
# dependabot[bot] / renovate[bot] / github-actions[bot], skip the phrase
# check. Local hook rarely sees these (bots push via API), but the
# check is here for parity with CI.
push_authors="$(git log --format=%an "$commit_range" 2>/dev/null | sort -u || echo '')"
bot_only=1
while IFS= read -r author; do
  [ -z "$author" ] && continue
  case "$author" in
    "dependabot[bot]"|"renovate[bot]"|"github-actions[bot]") ;;
    *) bot_only=0; break ;;
  esac
done <<< "$push_authors"
if [ "$bot_only" = 1 ] && [ -n "$push_authors" ]; then
  echo "  ℹ️  OPS-0069 audit-trail check SKIPPED (bot-authored range: $push_authors)."
  audit_ok=1
else
  # Exemption 2: revert commits — if EVERY commit in range starts with
  # 'Revert "', skip. Mixed ranges (some revert + some non-revert) still
  # require the phrase.
  revert_only=1
  non_revert_found=0
  while IFS= read -r subject; do
    [ -z "$subject" ] && continue
    non_revert_found=1
    case "$subject" in
      'Revert "'*) ;;
      *) revert_only=0; break ;;
    esac
  done < <(git log --format=%s "$commit_range" 2>/dev/null)
  if [ "$revert_only" = 1 ] && [ "$non_revert_found" = 1 ]; then
    echo "  ℹ️  OPS-0069 audit-trail check SKIPPED (revert-only range)."
    audit_ok=1
  else
    audit_ok=0
    for phrase in "Multi-agent self-review per OPS-0065" \
                  "Self-review skipped per founder OK"; do
      if echo "$push_msgs" | grep -qF "$phrase"; then
        audit_ok=1
        break
      fi
    done
  fi
fi
if [ "$audit_ok" -ne 1 ]; then
  echo "::error::no OPS-0069 audit-trail phrase found in any commit in the push range ($commit_range)."
  echo
  echo "Every push MUST carry one of these phrases in a commit message body:"
  echo
  echo "  Standard case (dispatch OPS-0065 diff-class agents pre-push, fold findings):"
  echo "    Multi-agent self-review per OPS-0065 (<agents>): <verdict summary>"
  echo
  echo "  Founder-OK skip case (only with in-session authorization):"
  echo "    Self-review skipped per founder OK <reason>"
  echo
  echo "Options to unblock this push:"
  echo "  (1) Dispatch the OPS-0065 diff-class-matched sub-agents by invoking"
  echo "      your AI-agent tool (Claude Code Agent() / Codex agents / etc.),"
  echo "      one call per matched agent-type (code-reviewer, documentation-"
  echo "      specialist, security-auditor, silent-failure-hunter, etc. — see"
  echo "      https://github.com/vladm3105/aidoc-flow-operations/blob/main/CLAUDE.md"
  echo "      § 'Multi-agent automated review' for the diff-class → agent map)."
  echo "      Fold their findings, THEN amend HEAD:"
  echo "        git commit --amend"
  echo "        # in the editor, append a line to the commit body:"
  echo "        #   Multi-agent self-review per OPS-0065 (<agents>): <verdict summary>"
  echo "  (2) Get founder authorization to skip AND amend HEAD to add the"
  echo "      'Self-review skipped per founder OK <reason>' line to the commit"
  echo "      body via 'git commit --amend'."
  echo
  echo "See https://github.com/vladm3105/aidoc-flow-operations/blob/main/ops/DECISIONS.md"
  echo "→ OPS-0069 for the full rule."
  rc=1
else
  echo "  ✅ OPS-0069 audit-trail present in push range."
fi

echo "════════════════════════════════════════════════════════════════════"
if [ "$rc" = 0 ]; then
  echo "✅ local pre-push checks passed (including OPS-0069 audit-trail check)."
else
  echo "❌ local pre-push checks FAILED — do not push until fixed."
fi
exit "$rc"
