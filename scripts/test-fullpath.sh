#!/usr/bin/env bash
# scripts/test-fullpath.sh — deterministic + optional live full-path acceptance
set -uo pipefail

LIVE_FLAG=0
for arg in "$@"; do
  case "$arg" in
    --live) LIVE_FLAG=1 ;;
    -h|--help) echo "Usage: $0 [--live]"; exit 0 ;;
    *) echo "unknown flag: $arg"; exit 2 ;;
  esac
done

FRAMEWORK="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$FRAMEWORK"

python3 -m unittest tests.acceptance.deterministic.test_fullpath -v
if [[ $LIVE_FLAG -eq 1 ]]; then
  LIVE=1 python3 -m unittest tests.acceptance.live.test_fullpath_live -v
fi
