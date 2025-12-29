#!/usr/bin/env bash
set -euo pipefail

EXAMPLES_DIR="BRD/examples"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VALIDATOR="$SCRIPT_DIR/validate_brd_template.sh"

if [ ! -x "$VALIDATOR" ]; then
  echo "❌ Validator not found or not executable: $VALIDATOR" >&2
  exit 1
fi

if [ ! -d "$EXAMPLES_DIR" ]; then
  echo "❌ Examples directory not found: $EXAMPLES_DIR" >&2
  exit 1
fi

status=0
for f in "$EXAMPLES_DIR"/BRD-*.md; do
  [ -e "$f" ] || continue
  echo "\n== Validating: $f ==\n"
  bash "$VALIDATOR" "$f" || status=1
done

exit $status

