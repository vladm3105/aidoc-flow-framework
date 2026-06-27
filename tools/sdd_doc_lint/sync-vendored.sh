#!/usr/bin/env bash
# Re-sync the vendored sdd_doc_lint copies from the canonical tools/sdd_doc_lint.
# The canonical copy is the single source of truth; each platform ships a
# byte-identical copy so its runtime can import the linter independently
# (PLATFORM-ALIGN Part A). Run from anywhere in the repo.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$here/../.." && pwd)"
canonical="$repo_root/tools/sdd_doc_lint"

for dest in \
  "$repo_root/platforms/claude-code-plugin/sdd_doc_lint" \
  "$repo_root/platforms/hermes/sdd_doc_lint"; do
  mkdir -p "$dest"
  cp "$canonical/__init__.py" "$dest/__init__.py"
  cp "$canonical/__main__.py" "$dest/__main__.py"
  cp "$canonical/trace_graph.py" "$dest/trace_graph.py"
  echo "synced -> ${dest#"$repo_root"/}"
done
