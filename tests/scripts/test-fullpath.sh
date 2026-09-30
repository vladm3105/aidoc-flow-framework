#!/usr/bin/env bash
# tests/scripts/test-fullpath.sh — deterministic full-path acceptance
# (the --live variant died with tests/acceptance/live/; CHG-08 #670)
set -uo pipefail

for arg in "$@"; do
  case "$arg" in
    -h|--help) echo "Usage: $0"; exit 0 ;;
    *) echo "unknown flag: $arg (live runs retired)"; exit 2 ;;
  esac
done

FRAMEWORK="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$FRAMEWORK"

python3 -m unittest tests.acceptance.deterministic.test_fullpath -v
