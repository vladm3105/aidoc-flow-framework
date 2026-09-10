#!/usr/bin/env bash
# ch-gate-check.sh — Pre-commit hook enforcing CHG gate
# Blocks commits that modify code files without an active CHG.
# Exempts: bug fixes on active IPLANs, docs, configs, tests, migrations.

set -uo pipefail

toplevel="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
cd "$toplevel" || exit 0

# Get staged files (excluding deletes)
STAGED=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null)
[ -z "$STAGED" ] && exit 0

# Only enforce on code files
CODE_FILES=""
for f in $STAGED; do
  case "$f" in
    *.go|*.js|*.ts|*.tsx|*.jsx|*.py)
      # Exclude test files, docs, configs, migrations
      case "$f" in
        *_test.go|*_test.*|test_*|tests/*|docs/*|.mimocode/*|migrations/*) ;;
        *) CODE_FILES="$CODE_FILES $f" ;;
      esac
      ;;
  esac
done

[ -z "$CODE_FILES" ] && exit 0

# Check for active CHG in docs/sdd/09-CHG/
CHG_DIR="docs/sdd/09-CHG"
if [ ! -d "$CHG_DIR" ]; then
  echo "::error::GOVERNANCE GATE: No CHG directory found ($CHG_DIR)."
  echo "Create a CHG document before committing code changes."
  echo "See CLAUDE.md → MANDATORY: Governance Gate"
  exit 1
fi

# Look for CHG with status In-Progress or Approved
ACTIVE_CHG=""
for chg in "$CHG_DIR"/CHG-*.yaml; do
  [ -f "$chg" ] || continue
  status=$(grep -E '^\s*status:' "$chg" 2>/dev/null | head -1 | sed 's/.*status:\s*//' | tr -d '"' | tr -d "'")
  case "$status" in
    In-Progress|Approved)
      ACTIVE_CHG="$chg"
      break
      ;;
  esac
done

if [ -z "$ACTIVE_CHG" ]; then
  echo "::error::GOVERNANCE GATE: No active CHG found in $CHG_DIR/."
  echo "Code files being committed: $CODE_FILES"
  echo ""
  echo "Before committing code, you MUST:"
  echo "  1. Create a CHG document (docs/sdd/09-CHG/CHG-XX_*.yaml)"
  echo "  2. Set status to 'In-Progress' or 'Approved'"
  echo "  3. Complete §3.4 checklist"
  echo "  4. Run §3.4.1 validation"
  echo ""
  echo "See CLAUDE.md → MANDATORY: Governance Gate"
  echo "Exception: bug fixes on active IPLANs (add 'Bug fix on IPLAN-XX' to commit message)"
  exit 1
fi

echo "✅ GOVERNANCE GATE: Active CHG found — $(basename "$ACTIVE_CHG")"
exit 0
