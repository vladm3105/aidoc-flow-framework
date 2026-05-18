#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

if ! command -v python >/dev/null 2>&1; then
  echo "python is required" >&2
  exit 2
fi

mapfile -t changed_md < <(git diff --name-only -- '*.md')

if [ "${#changed_md[@]}" -eq 0 ]; then
  echo "No changed markdown files to validate."
  exit 0
fi

failures=0

for file in "${changed_md[@]}"; do
  if [[ "$file" == governance/templates/* ]]; then
    echo "SKIP template-context file: $file"
    continue
  fi

  echo "VALIDATE $file"
  if ! PYTHONPATH=ucx_hermes/src python -m mcp_server.cli.main validate-links --target "$file" >/tmp/opencode/validate-links.out 2>/tmp/opencode/validate-links.err; then
    failures=$((failures + 1))
    echo "FAILED $file"
    if [ -s /tmp/opencode/validate-links.out ]; then
      cat /tmp/opencode/validate-links.out
    fi
    if [ -s /tmp/opencode/validate-links.err ]; then
      cat /tmp/opencode/validate-links.err
    fi
  fi
done

if [ "$failures" -gt 0 ]; then
  echo "Link validation failed for $failures file(s)." >&2
  exit 1
fi

echo "Link validation passed for changed non-template markdown files."
