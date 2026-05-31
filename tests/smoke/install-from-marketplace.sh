#!/usr/bin/env bash
# tests/smoke/install-from-marketplace.sh
# Install the published plugin into a clean workspace dir for smoke testing.
set -uo pipefail

MARKETPLACE_URL="${MARKETPLACE_URL:-}"
WORKSPACE="${1:-}"
if [[ -z "$MARKETPLACE_URL" || -z "$WORKSPACE" ]]; then
  echo "Usage: MARKETPLACE_URL=<url> $0 <workspace-dir>" >&2
  exit 2
fi

mkdir -p "$WORKSPACE"
cd "$WORKSPACE"
# See tests/smoke/COMMANDS.md for verified syntax.
claude plugin install "$MARKETPLACE_URL"
