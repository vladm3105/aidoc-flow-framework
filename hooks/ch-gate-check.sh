#!/usr/bin/env bash
# ch-gate-check.sh — Pre-commit hook enforcing CHG gate
# Warns on commits that modify code files without an active CHG.
# Exempts: bug fixes on active IPLANs, docs, configs, tests, migrations.
#
# Warn-only: every path exits 0 — the gate advises, never blocks. Wired into
# .pre-commit-config.yaml (local warn-only hook) and hooks/hooks.json (Claude
# path). See framework/governance/DOC_GOVERNANCE_CORE.md §3.4.

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
    *.go|*.js|*.ts|*.tsx|*.jsx|*.py|*.sh)
      # Exclude test files, docs, configs, migrations
      case "$f" in
        *_test.go|*_test.*|test_*|tests/*|docs/*|.mimocode/*|migrations/*) ;;
        *) CODE_FILES="$CODE_FILES $f" ;;
      esac
      ;;
  esac
done

[ -z "$CODE_FILES" ] && exit 0

# CHG instance locations, in precedence order. The framework-only repo has no
# instance dir by design (only the template at framework/layers/09_CHG/), so a
# missing dir is an advisory state, never a failure.
CHG_DIRS="docs/sdd/09-CHG framework/layers/09_CHG"
CHG_DIR=""
for d in $CHG_DIRS; do
  if [ -d "$d" ]; then
    CHG_DIR="$d"
    break
  fi
done

if [ -z "$CHG_DIR" ]; then
  echo "::warning::GOVERNANCE GATE: No CHG instance directory found ($CHG_DIRS)."
  echo "Code files being committed: $CODE_FILES"
  echo "Create a CHG document before committing code changes."
  echo "See AGENTS.md → MANDATORY: Governance Gate"
  exit 0
fi

# Look for CHG with status In-Progress or Approved
ACTIVE_CHG=""
for chg in "$CHG_DIR"/CHG-*.yaml; do
  [ -f "$chg" ] || continue
  # Templates are not instances — a future status-value edit on a template
  # must never arm the gate (#663).
  case "$chg" in
    *TEMPLATE*) continue ;;
  esac
  # NOTE: `[[:space:]]`, not `\s` — the latter is a GNU grep/sed extension
  # and silently never matches on BSD/macOS (#690).
  status=$(grep -E '^[[:space:]]*status:' "$chg" 2>/dev/null | head -1 | sed 's/.*status:[[:space:]]*//' | tr -d '"' | tr -d "'" | tr -d '[:space:]')
  case "$status" in
    In-Progress|Approved)
      ACTIVE_CHG="$chg"
      break
      ;;
  esac
done

if [ -z "$ACTIVE_CHG" ]; then
  echo "::warning::GOVERNANCE GATE: No active CHG found in $CHG_DIR/."
  echo "Code files being committed: $CODE_FILES"
  echo ""
  echo "Before committing code, you MUST:"
  echo "  1. Create a CHG document ($CHG_DIR/CHG-XX_*.yaml)"
  echo "  2. Set status to 'In-Progress' or 'Approved'"
  echo "  3. Complete §3.4 checklist"
  echo "  4. Run §3.4.1 validation"
  echo ""
  echo "See AGENTS.md → MANDATORY: Governance Gate"
  # At pre-commit time HEAD is the *previous* commit, never the one being
  # committed — so read the staged content instead (#690). A staged CHG that
  # names a bug-fix vehicle suggests the author is on the repair path.
  STAGED_BUGFIX=""
  for f in $STAGED; do
    case "$f" in
      *CHG-*.yaml)
        case "$f" in
          *TEMPLATE*) continue ;;
        esac
        if git show ":$f" 2>/dev/null | grep -qi "parent_iplan\|bugfix"; then
          STAGED_BUGFIX="$f"
          break
        fi
        ;;
    esac
  done
  if [ -n "$STAGED_BUGFIX" ]; then
    echo "Note: staged $STAGED_BUGFIX looks like a bug-fix vehicle — verify it names the right plan."
  else
    echo "Exception: bug fixes on active IPLANs (add 'Bug fix on IPLAN-XX' to commit message)"
  fi
  exit 0
fi

echo "✅ GOVERNANCE GATE: Active CHG found — $(basename "$ACTIVE_CHG")"
exit 0
