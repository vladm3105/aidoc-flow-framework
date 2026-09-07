#!/usr/bin/env bash
# Warning hook: when a commit changes code/spec/skills but does NOT touch
# any of the semantic documents-of-record, print a checklist of likely-stale
# docs the contributor should consider updating. Does NOT fail the commit
# (warning-only, false-positive friendly).
#
# Wired into .pre-commit-config.yaml. Also safe to invoke manually:
#   bash hooks/check-docs-updated.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Collect staged files
STAGED=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || true)
[ -z "$STAGED" ] && exit 0

# Documents of record
DOCS_OF_RECORD=(
  "CHANGELOG.md"
  "README.md"
  "CLAUDE.md"
  "framework/governance/DECISIONS.md"
)

# Check if any doc-of-record was touched
doc_touched=0
for doc in "${DOCS_OF_RECORD[@]}"; do
  if echo "$STAGED" | grep -q "^${doc}$"; then
    doc_touched=1
    break
  fi
done

if [ "$doc_touched" -eq 1 ]; then
  exit 0
fi

# Check if any code/spec was changed
code_changed=0
while IFS= read -r f; do
  case "$f" in
    framework/*|sdd_doc_lint/*|hooks/*|tests/*|examples/*)
      code_changed=1
      break
      ;;
  esac
done <<< "$STAGED"

if [ "$code_changed" -eq 1 ]; then
  echo ""
  echo "⚠️  Code/spec files changed but no document-of-record was updated."
  echo "   Consider updating:"
  for doc in "${DOCS_OF_RECORD[@]}"; do
    echo "   - $doc"
  done
  echo ""
fi
