#!/usr/bin/env bash
# tests/scripts/test-layer.sh — run one layer's deterministic acceptance suite
set -uo pipefail

LAYER="${1:-}"
if [[ -z "$LAYER" ]]; then
  echo "Usage: bash tests/scripts/test-layer.sh <brd|prd|ears|bdd|adr|spec|tdd|iplan>" >&2
  exit 2
fi

FRAMEWORK="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$FRAMEWORK"
exec python3 -m unittest "tests.acceptance.deterministic.test_layer_${LAYER}" -v
