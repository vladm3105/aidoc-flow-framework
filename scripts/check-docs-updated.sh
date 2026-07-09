#!/usr/bin/env bash
# Warning hook: when a commit changes code / spec / skills but does not touch
# any of the semantic documents-of-record, print a checklist of likely-stale
# docs the contributor should consider updating. Does NOT fail the commit
# (warning-only, false-positive friendly).
#
# Wired into .pre-commit-config.yaml. Also safe to invoke manually:
#
#   bash scripts/check-docs-updated.sh
#
# The mechanical doc-sync (version-reference propagation) lives in a separate
# hook: scripts/sync-version-refs.sh.  This hook covers the semantic content
# that can't be auto-generated:
#
#   - root CHANGELOG.md entry under [Unreleased] (project-level)
#   - plugin CHANGELOG entry under [Unreleased]
#   - ROADMAP.md "Recently shipped" bullet
#   - plans/HANDOFF.md current-state header refresh
#   - plans/HERMES-BACKLOG.md new H-N entry (when the change creates Hermes
#     follow-on work)
#
# The hook reads staged changes only and produces output even when those docs
# WERE updated (a "summary of which docs were touched" line) — so the
# contributor gets affirmative feedback when they are doing the right thing.

set -euo pipefail

# Collect staged file paths (added, copied, modified, renamed).
mapfile -t staged < <(git diff --cached --name-only --diff-filter=ACMR)

if (( ${#staged[@]} == 0 )); then
  # No staged changes — nothing to check. (pre-commit shouldn't actually
  # invoke us here, but be defensive.)
  exit 0
fi

# Categorize the staged changes.
has_framework_change=0  # framework/** edits
has_platform_change=0   # platforms/**/{skills,agents,scripts,tools,*.py,VERSION,...}
has_tools_change=0      # repo-root tools/** (shared code, e.g. saga_driver.py)
has_test_change=0       # tests/**
has_doc_change=0        # any of the doc paths we track
docs_touched=()         # names of doc-of-record files that ARE in the staged set

for f in "${staged[@]}"; do
  case "$f" in
    framework/*) has_framework_change=1 ;;
    platforms/*/skills/*|platforms/*/agents/*|platforms/*/scripts/*|platforms/*/tools/*)
      has_platform_change=1 ;;
    platforms/*/VERSION|platforms/*/.claude-plugin/*) has_platform_change=1 ;;
    platforms/*.py|platforms/*/src/*) has_platform_change=1 ;;
    tools/*) has_tools_change=1 ;;
    tests/*) has_test_change=1 ;;
  esac

  case "$f" in
    CHANGELOG.md) has_doc_change=1; docs_touched+=("CHANGELOG.md") ;;
    README.md) has_doc_change=1; docs_touched+=("README.md") ;;
    ROADMAP.md) has_doc_change=1; docs_touched+=("ROADMAP.md") ;;
    CLAUDE.md) has_doc_change=1; docs_touched+=("CLAUDE.md") ;;
    CONTRIBUTING.md) has_doc_change=1; docs_touched+=("CONTRIBUTING.md") ;;
    plans/HANDOFF.md) has_doc_change=1; docs_touched+=("plans/HANDOFF.md") ;;
    plans/HERMES-BACKLOG.md) has_doc_change=1; docs_touched+=("plans/HERMES-BACKLOG.md") ;;
    docs/PARITY.md) has_doc_change=1; docs_touched+=("docs/PARITY.md") ;;
    docs/TAGGING.md) has_doc_change=1; docs_touched+=("docs/TAGGING.md") ;;
    docs/PROJECT.md) has_doc_change=1; docs_touched+=("docs/PROJECT.md") ;;
    docs/REPO_STRUCTURE.md) has_doc_change=1; docs_touched+=("docs/REPO_STRUCTURE.md") ;;
    platforms/*/CHANGELOG.md) has_doc_change=1; docs_touched+=("$f") ;;
    framework/governance/DECISIONS.md) has_doc_change=1; docs_touched+=("$f") ;;
  esac
done

substantive=$(( has_framework_change + has_platform_change + has_tools_change ))

# Affirmative summary when docs ARE touched.
if (( has_doc_change )); then
  printf '[check-docs-updated] OK — docs touched in this commit:\n' >&2
  for d in "${docs_touched[@]}"; do
    printf '  - %s\n' "$d" >&2
  done
fi

# Warning when substantive changes exist but no doc was touched.
if (( substantive > 0 && has_doc_change == 0 )); then
  cat >&2 <<'WARN'
[check-docs-updated] ⚠ This commit changes code/spec/skills but touches NONE
                       of the documents-of-record. Consider whether any of the
                       following need to be updated in THIS commit (not in a
                       follow-up doc-refresh PR):

                       Project-level:
                         - CHANGELOG.md          (entry under [Unreleased])
                         - ROADMAP.md            ("Recently shipped" bullet)
                         - README.md             (Status block, if user-visible)
                         - CLAUDE.md             ("Current state" line)
                         - plans/HANDOFF.md      (current-state header)

                       Platform / framework:
                         - platforms/<name>/CHANGELOG.md  (under [Unreleased])
                         - docs/PARITY.md                 (current-state row, on release)
                         - docs/TAGGING.md                (new release row, on release)
                         - framework/governance/DECISIONS.md (if a decision is recorded)

                       Hermes follow-on:
                         - plans/HERMES-BACKLOG.md  (new H-N entry, if this
                                                     plugin change creates
                                                     Hermes catch-up work)

                       This is a WARNING, not a failure. Commit proceeds. If
                       the change genuinely needs no doc update (typo fix,
                       internal refactor, test-only change), this warning is
                       a false positive and can be ignored.

                       Rule reference: CLAUDE.md §"Durable conventions"
                       "Update docs of record per PR".
WARN
fi

exit 0
