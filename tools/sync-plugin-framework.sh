#!/usr/bin/env bash
# Re-sync the Claude Code plugin's vendored framework bundle from the canonical
# framework/ spec. The monorepo framework/ is the single source of truth
# (D-0013); the plugin ships a byte-identical, GENERATED copy of the spec
# subtrees it consumes so that an installed plugin can resolve its own
# references from the Claude Code cache (D-0022 — the shippability exception).
#
# The plugin repoints every framework/ reference to
#   ${CLAUDE_PLUGIN_ROOT}/framework/...
# which resolves to this bundle once installed. Never hand-edit the bundle;
# edit the canonical framework/ and re-run this script. A conformance drift
# guard (tests/conformance/platforms/test_plugin_framework_bundle.py) fails CI
# if the bundle and the canonical spec diverge.
#
# Run from anywhere in the repo.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$here/.." && pwd)"
canonical="$repo_root/framework"
dest="$repo_root/platforms/claude-code-plugin/framework"

# The consumed subtrees + the single root doc the plugin's skills cite directly.
SUBTREES=(layers governance registry)
ROOT_FILES=(SPEC_DRIVEN_DEVELOPMENT_GUIDE.md)

# Safety: dest must be the plugin's framework bundle, nothing else.
case "$dest" in
  */platforms/claude-code-plugin/framework) ;;
  *) echo "refusing to sync: unexpected dest '$dest'" >&2; exit 1 ;;
esac

# Regenerate from scratch so upstream deletions propagate to the bundle.
rm -rf "$dest"
mkdir -p "$dest"
for sub in "${SUBTREES[@]}"; do
  cp -R "$canonical/$sub" "$dest/$sub"
done
for f in "${ROOT_FILES[@]}"; do
  cp "$canonical/$f" "$dest/$f"
done

count="$(find "$dest" -type f | wc -l | tr -d ' ')"
echo "synced framework bundle -> ${dest#"$repo_root"/} (${count} files)"
