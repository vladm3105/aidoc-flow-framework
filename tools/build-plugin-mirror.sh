#!/usr/bin/env bash
# Generate the standalone PUBLIC MIRROR of the Claude Code plugin
# (PLUGIN-MARKETPLACE P2). The mirror is a ONE-WAY, GENERATED artifact: never edit
# it by hand — edit platforms/claude-code-plugin/ and re-run this. It lays the
# plugin out at the mirror REPO ROOT (so marketplace.json uses source ".") and adds
# its own .claude-plugin/marketplace.json carrying the aidoc-flow.com owner (D-0023).
#
# The dev source of truth stays the monorepo; the mirror is a release artifact the
# user pushes to the public plugin repo. The container's GitHub scope is the
# monorepo only, so creating/pushing the mirror repo is a user step.
#
# Usage:
#   bash tools/build-plugin-mirror.sh [--out <dir>]
#   MIRROR_REPO_SLUG=<org>/aidoc-flow-plugin bash tools/build-plugin-mirror.sh
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$here/.." && pwd)"
plugin="$repo_root/platforms/claude-code-plugin"

out="$repo_root/dist/plugin-mirror"
if [ "${1:-}" = "--out" ] && [ -n "${2:-}" ]; then
  out="$2"
fi
repo_slug="${MIRROR_REPO_SLUG:-<org>/aidoc-flow-plugin}"

# 1. Refresh the vendored framework bundle so the mirror is self-contained + current.
bash "$here/sync-plugin-framework.sh" >/dev/null

# 2. Reset the output tree (generated — safe to wipe).
rm -rf "$out"
mkdir -p "$out"

# 3. Copy the plugin contents (incl. the framework bundle + .claude-plugin/plugin.json)
#    to the mirror root.
cp -R "$plugin/." "$out/"

# 4. Write the mirror marketplace.json: plugin at repo root => source "."; owner is
#    the aidoc-flow.com identity. Description/version are read from plugin.json so the
#    two manifests never drift.
python3 - "$plugin/.claude-plugin/plugin.json" "$out/.claude-plugin/marketplace.json" <<'PY'
import json
import sys

plugin_json, out_path = sys.argv[1], sys.argv[2]
p = json.load(open(plugin_json, encoding="utf-8"))
market = {
    "name": "aidoc-flow",
    "owner": {
        "name": "AI Doc Flow",
        "email": "plugins@aidoc-flow.com",
        "url": "https://aidoc-flow.com",
    },
    "plugins": [
        {
            "name": p["name"],
            "source": ".",
            "description": p.get("description", ""),
            "version": p.get("version", ""),
        }
    ],
}
with open(out_path, "w", encoding="utf-8") as fh:
    json.dump(market, fh, indent=2, ensure_ascii=False)
    fh.write("\n")
PY

count="$(find "$out" -type f | wc -l | tr -d ' ')"
version="$(cat "$plugin/VERSION")"
echo "mirror generated at ${out} (${count} files; plugin ${version})"
echo "next (user): create the public repo '${repo_slug}', copy this tree to its root,"
echo "             commit + push, then: /plugin marketplace add ${repo_slug}"
