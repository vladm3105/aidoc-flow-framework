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
# Personal namespace for now; override when the GitHub org exists (D-0023).
repo_slug="${MIRROR_REPO_SLUG:-vladm3105/aidoc-flow-plugin}"

# 1. Refresh the vendored framework bundle so the mirror is self-contained + current.
bash "$here/sync-plugin-framework.sh" >/dev/null

# 2. Reset the output tree (generated — safe to wipe).
rm -rf "$out"
mkdir -p "$out"

# 3. Copy the plugin contents (incl. the framework bundle + .claude-plugin/plugin.json)
#    to the mirror root.
cp -R "$plugin/." "$out/"

# 4. Write the mirror marketplace.json (plugin at repo root => source ".", owner is
#    the aidoc-flow.com identity) AND a standalone mirror README, overwriting the
#    copied monorepo README (whose ../../ links would dangle in a standalone repo).
#    Description/version are read from plugin.json so the manifests never drift.
python3 - "$plugin/.claude-plugin/plugin.json" "$out" "$repo_slug" <<'PY'
import json
import sys

plugin_json, out_dir, repo_slug = sys.argv[1], sys.argv[2], sys.argv[3]
p = json.load(open(plugin_json, encoding="utf-8"))
market_name = "aidoc-flow"
plugin_name = p["name"]

market = {
    "name": market_name,
    "owner": {
        "name": "AI Doc Flow",
        "email": "plugins@aidoc-flow.com",
        "url": "https://aidoc-flow.com",
    },
    "plugins": [
        {
            "name": plugin_name,
            "source": ".",
            "description": p.get("description", ""),
            "version": p.get("version", ""),
        }
    ],
}
with open(f"{out_dir}/.claude-plugin/marketplace.json", "w", encoding="utf-8") as fh:
    json.dump(market, fh, indent=2, ensure_ascii=False)
    fh.write("\n")

readme = f"""# {plugin_name} — Claude Code plugin

{p.get("description", "")}

> **One-way generated mirror.** This repository is a published mirror of the
> plugin, built from the source monorepo for marketplace install — do not edit it
> directly. Source of truth, issues, and contributions:
> <{p.get("repository", "")}>. Project home: <https://aidoc-flow.com/claude-code>.

## Install

```
/plugin marketplace add {repo_slug}
/plugin install {plugin_name}@{market_name}
```

## Quickstart

```
/{plugin_name}:doc-flow                # "which skill do I need?" — start here
/{plugin_name}:project-init            # scaffold the docs/ layer tree
/{plugin_name}:doc-brd-autopilot       # draft the first layer (BRD)
/{plugin_name}:doc-brd-audit           # score it against the layer gate
/{plugin_name}:trace-check             # verify traceability across artifacts
```

Work down the layers (`doc-prd` … `doc-iplan`), running each layer's `-audit`
before promoting. Full docs and guides: <https://aidoc-flow.com/claude-code>.

## License

{p.get("license", "MIT")} — see the source repository.
"""
with open(f"{out_dir}/README.md", "w", encoding="utf-8") as fh:
    fh.write(readme)
PY

count="$(find "$out" -type f | wc -l | tr -d ' ')"
version="$(cat "$plugin/VERSION")"
echo "mirror generated at ${out} (${count} files; plugin ${version})"
echo "next (user): create the public repo '${repo_slug}', copy this tree to its root,"
echo "             commit + push, then: /plugin marketplace add ${repo_slug}"
