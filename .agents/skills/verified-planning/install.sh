#!/usr/bin/env bash
# Install the verified-planning skill + gate into one or more repos as a committed copy.
# The master is this script's own directory
# (.agents/skills/verified-planning in aidoc-flow-framework).
#
# What gets committed into a repo:
#
#   YES — SKILL.md, check_plan.py, plan-gate.yml, the pre-commit snippet, the plan
#         template, PLAN.md, DESIGN.md, tests. CI and the hook run inside the repo,
#         so the gate has to be in the tree they check out; the skill travels with
#         it so the method and the gate stay in sync. (In Muse there is no
#         user-skill masking, so the project SKILL.md is the live skill.)
#
#   NO  — install.sh itself. A repo carrying its own installer can re-infect
#         itself with a stale copy list, which is how the above would come back.
#
# Re-running this is the remedy as well as the install: it DELETES a stale
# install.sh left by an older version of this script.
#
# Usage: install.sh <repo-dir> [<repo-dir> ...]
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"   # the master skill dir

install_into() {  # $1 = repo dir
  local repo="$1"
  local dst="$repo/.agents/skills/verified-planning"
  mkdir -p "$dst/tests" "$repo/.github/workflows"
  # guard: never copy the master onto itself (a repo running its own copy)
  if [ "$dst" -ef "$SRC" ]; then echo "skip: $repo is the master"; return; fi
  for f in SKILL.md check_plan.py PLAN.md DESIGN.md PLAN-TEMPLATE.snippet.md \
           precommit-hook.snippet.txt plan-gate.yml; do
    cp "$SRC/$f" "$dst/$f"
  done
  cp -r "$SRC/tests/." "$dst/tests/"
  # self-heal: older versions of this script installed this file. It is a
  # defect — install.sh re-infects (a stale copy list).
  [ -f "$dst/install.sh" ] && { rm -f "$dst/install.sh"
    echo "removed $dst/install.sh — stale copy list, re-infection path"; }
  cat > "$dst/README.md" <<'README'
# verified-planning — live Muse project skill + gate

This directory holds the **live skill** (`SKILL.md`) and the **gate**
(`check_plan.py`, `plan-gate.yml`). CI and the pre-commit hook run inside this
repo and need the gate in the checked-out tree; the skill travels with it so
the method and the gate stay in sync.

Refresh this directory with
`<framework-checkout>/.agents/skills/verified-planning/install.sh <repo>`.
README
  cp "$SRC/plan-gate.yml" "$repo/.github/workflows/plan-gate.yml"
  echo "installed into $repo"
}

[ "$#" -ge 1 ] || { echo "usage: install.sh <repo-dir>..." >&2; exit 2; }
for repo in "$@"; do install_into "$repo"; done
