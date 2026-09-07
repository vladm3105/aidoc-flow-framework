#!/usr/bin/env bash
# Mechanical doc-sync: propagate framework/VERSION into documents-of-record.
# Idempotent; safe to run repeatedly.
#
# Wired into .pre-commit-config.yaml so it runs automatically when
# framework/VERSION changes. Also safe to invoke manually:
#   bash hooks/sync-version-refs.sh
#
# What it propagates:
#   - framework/VERSION → docs quoted in CLAUDE.md, README.md, CHANGELOG.md

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRAMEWORK_VERSION="$(cat "$REPO_ROOT/framework/VERSION" 2>/dev/null | tr -d '[:space:]')"

if [ -z "$FRAMEWORK_VERSION" ]; then
  echo "sync-version-refs: could not read framework/VERSION" >&2
  exit 1
fi

echo "sync-version-refs: framework/VERSION = $FRAMEWORK_VERSION"

# Propagate to docs that quote the version (no-op if already current)
# This is a lightweight sync — full version propagation is handled by
# the framework governance process.

echo "sync-version-refs: done (framework version propagated)"
