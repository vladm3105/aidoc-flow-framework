#!/usr/bin/env bash
# tests/smoke/install-from-marketplace.sh
# Install the published plugin into a clean workspace dir for smoke testing.
#
# Verified syntax (see tests/smoke/COMMANDS.md, verification log 2026-05-31):
#   claude plugin marketplace add <path-or-url>
#   claude plugin install <plugin>[@<marketplace-name>] [--scope ...]
#
# The CLI expects a *plugin name* (optionally @marketplace), not a URL —
# the marketplace must be added first.
set -uo pipefail

MARKETPLACE="${MARKETPLACE:-${MARKETPLACE_URL:-}}"   # path or URL to the marketplace
PLUGIN="${PLUGIN:-}"                                  # plugin name or name@marketplace
SCOPE="${SCOPE:-user}"                                # user | project | local
WORKSPACE="${1:-}"

if [[ -z "$MARKETPLACE" || -z "$PLUGIN" || -z "$WORKSPACE" ]]; then
  echo "Usage: MARKETPLACE=<path-or-url> PLUGIN=<name[@marketplace]> [SCOPE=user|project|local] $0 <workspace-dir>" >&2
  exit 2
fi

mkdir -p "$WORKSPACE"
cd "$WORKSPACE"

# See tests/smoke/COMMANDS.md for verified syntax.
claude plugin marketplace add "$MARKETPLACE"
claude plugin install "$PLUGIN" --scope "$SCOPE"
