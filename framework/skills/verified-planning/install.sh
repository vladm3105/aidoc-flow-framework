#!/usr/bin/env bash
# Install the verified-planning GATE from framework/skills into a consumer repo.
# Framework adaptation of the canon installer: the master is this directory
# under framework/skills/verified-planning/.
#
# What gets committed into a consumer repo, and what deliberately does NOT:
#
#   YES — check_plan.py, plan-gate.yml, the pre-commit snippet, the plan
#         template, tests. CI and the hook run inside the repo, so the gate has
#         to be in the tree they check out.
#
#   NO  — skill file. The live skill ships with the framework tree; a consumer
#         pins the gate files below, not a second skill copy that can drift.
#
#   NO  — install.sh itself. A repo carrying its own installer can re-infect
#         itself with a stale copy list, which is how the above would come back.
#
# Usage: install.sh <repo-dir> [<repo-dir> ...]
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"   # the master skill dir

install_into() {  # $1 = repo dir
  local repo="$1"
  local dst="$repo/framework-skills/verified-planning"
  mkdir -p "$dst/tests" "$repo/.github/workflows"
  # guard: never copy the master onto itself (a repo running its own copy)
  if [ "$dst" -ef "$SRC" ]; then echo "skip: $repo is the master"; return; fi
  for f in check_plan.py PLAN-TEMPLATE.snippet.md \
           precommit-hook.snippet.txt plan-gate.yml; do
    cp "$SRC/$f" "$dst/$f"
  done
  cp -r "$SRC/tests/." "$dst/tests/"
  # framework adaptation: consumer keeps its own skill copy — the framework
  # tree is the master, the consumer copy is a pinned snapshot. Do not delete it.
  cat > "$dst/README.md" <<'README'
# verified-planning — committed gate only (framework adaptation)

This directory holds the **gate**, not the live skill. `check_plan.py` and
`plan-gate.yml` live here because CI and the pre-commit hook run inside this
repo and need them in the checked-out tree.

The live skill is `framework/skills/verified-planning/SKILL.md` in
aidoc-flow-framework. Refresh this directory with
`framework/skills/verified-planning/install.sh <repo>`.
README
  cp "$SRC/plan-gate.yml" "$repo/.github/workflows/plan-gate.yml"
  # framework adaptation: no engine-config gitignore dance — the gate lives under
  # framework-skills/, which repos commit directly.
  echo "installed into $repo"
}

[ "$#" -ge 1 ] || { echo "usage: install.sh <repo-dir>..." >&2; exit 2; }
for repo in "$@"; do install_into "$repo"; done
