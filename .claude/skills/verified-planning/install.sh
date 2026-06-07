#!/usr/bin/env bash
# Install the verified-planning skill into one or more repos as a self-contained,
# committed copy. The master is this script's own directory.
# Usage: install.sh <repo-dir> [<repo-dir> ...]
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"   # the master skill dir

install_into() {  # $1 = repo dir
  local repo="$1"
  local dst="$repo/.claude/skills/verified-planning"
  mkdir -p "$dst/tests" "$repo/.github/workflows"
  # guard: never copy the master onto itself (a repo running its own copy)
  if [ "$dst" -ef "$SRC" ]; then echo "skip: $repo is the master"; return; fi
  for f in SKILL.md check_plan.py PLAN.md DESIGN.md PLAN-TEMPLATE.snippet.md \
           precommit-hook.snippet.yaml plan-gate.yml install.sh; do
    cp "$SRC/$f" "$dst/$f"
  done
  cp -r "$SRC/tests/." "$dst/tests/"
  cp "$SRC/plan-gate.yml" "$repo/.github/workflows/plan-gate.yml"
  # if the repo gitignores .claude/, add a negation so the skill is committable
  if [ -f "$repo/.gitignore" ] && grep -qE '^\.claude/?$' "$repo/.gitignore" \
     && ! grep -q 'verified-planning skill must be committed' "$repo/.gitignore"; then
    printf '\n# verified-planning skill must be committed (overrides .claude/ ignore)\n!.claude/skills/verified-planning/\n!.claude/skills/verified-planning/**\n' >> "$repo/.gitignore"
  fi
  echo "installed into $repo"
}

[ "$#" -ge 1 ] || { echo "usage: install.sh <repo-dir>..." >&2; exit 2; }
for repo in "$@"; do install_into "$repo"; done
