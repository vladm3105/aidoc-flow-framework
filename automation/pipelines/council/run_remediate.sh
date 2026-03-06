#!/usr/bin/env bash
# =============================================================================
# run.sh — Council Pipeline Main Orchestrator
# =============================================================================
# The standard pipeline entrypoint. Runs all 4 steps in sequence.
#
# Usage:
#   run.sh <COUNCIL_AUDIT_REPORT.md> [options]
#
# Options:
#   --target-doc <path>   Path to the document being remediated (for auto-apply)
#   --doc-id <BRD-01>     Document ID for GitHub Issue labels (default: inferred)
#   --dry-run             Preview all actions without making changes
#   --no-index            Skip Step 2 (KB indexing)
#   --no-apply            Skip Step 3 (auto-apply structural fixes)
#   --no-issues           Skip Step 4 (GitHub Issues creation)
#   --parse-only          Only run Step 1 (parse report to JSON)
#
# Exit codes: 0=success, 1=step failure, 2=config error
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CORE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")/core"

source "$CORE_DIR/config.sh"
source "$CORE_DIR/utils.sh"

# =============================================================================
# Parse arguments
# =============================================================================
REPORT_FILE=""
TARGET_DOC=""
DOC_ID=""
SKIP_INDEX=false
SKIP_APPLY=false
SKIP_ISSUES=false
PARSE_ONLY=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target-doc)  TARGET_DOC="$2";  shift 2 ;;
    --doc-id)      DOC_ID="$2";      shift 2 ;;
    --dry-run)     export DRY_RUN=true; shift ;;
    --no-index)    SKIP_INDEX=true;  shift ;;
    --no-apply)    SKIP_APPLY=true;  shift ;;
    --no-issues)   SKIP_ISSUES=true; shift ;;
    --parse-only)  PARSE_ONLY=true;  shift ;;
    -*)
      log_error "Unknown option: $1"
      echo "Usage: run.sh <REPORT.md> [--target-doc <doc>] [--doc-id <BRD-XX>] [--dry-run] [--no-index] [--no-apply] [--no-issues] [--parse-only]" >&2
      exit 2 ;;
    *)
      REPORT_FILE="$1"
      shift ;;
  esac
done

[[ -z "$REPORT_FILE" ]] && die "Usage: run.sh <COUNCIL_AUDIT_REPORT.md> [options]"
require_file "$REPORT_FILE"

# =============================================================================
# Infer DOC_ID from report filename if not provided
# =============================================================================
if [[ -z "$DOC_ID" ]]; then
  REPORT_BASENAME=$(basename "$REPORT_FILE")
  # Extract first BRD-XX / PRD-XX / etc. pattern from filename
  DOC_ID=$(echo "$REPORT_BASENAME" | grep -oP '[A-Z]+-\d+' | head -1 || echo "UNKNOWN")
fi

# =============================================================================
# Setup: working directory for this run
# =============================================================================
RUN_DIR=$(mktemp -d "/tmp/council_run_XXXXXX")
trap "rm -rf $RUN_DIR" EXIT

ACTIONS_JSON="$RUN_DIR/actions.json"
SUMMARY_FILE="$RUN_DIR/summary.txt"

# =============================================================================
# Banner
# =============================================================================
echo ""
echo "════════════════════════════════════════════════════════════"
echo "  COUNCIL PIPELINE — Automated Remediation"
echo "════════════════════════════════════════════════════════════"
echo "  Report:     $REPORT_FILE"
echo "  Document:   $DOC_ID"
echo "  Agent:      $AI_AGENT"
echo "  Dry run:    ${DRY_RUN:-false}"
if [[ -n "$TARGET_DOC" ]]; then
  echo "  Target doc: $TARGET_DOC"
fi
echo "════════════════════════════════════════════════════════════"
echo ""

# =============================================================================
# STEP 1: Parse report → JSON
# =============================================================================
log_step "Step 1 / 4 — Parse audit report into JSON"
bash "$SCRIPT_DIR/01_parse.sh" "$REPORT_FILE" "$ACTIONS_JSON"

TOTAL=$(jq 'length' "$ACTIONS_JSON")
P0_COUNT=$(jq '[.[] | select(.priority=="P0")] | length' "$ACTIONS_JSON")
P1_COUNT=$(jq '[.[] | select(.priority=="P1")] | length' "$ACTIONS_JSON")
P2_COUNT=$(jq '[.[] | select(.priority=="P2")] | length' "$ACTIONS_JSON")
log_ok "Parsed: $TOTAL actions (P0=$P0_COUNT P1=$P1_COUNT P2=$P2_COUNT)"

if [[ "$PARSE_ONLY" == "true" ]]; then
  log_info "Parse-only mode — writing actions to: actions.json"
  cp "$ACTIONS_JSON" "$(dirname "$REPORT_FILE")/council_actions.json"
  log_ok "Done (parse-only). Actions saved to: $(dirname "$REPORT_FILE")/council_actions.json"
  exit 0
fi

# =============================================================================
# STEP 2: Index into Knowledge Base (graceful skip)
# =============================================================================
if [[ "$SKIP_INDEX" == "true" ]]; then
  log_info "Step 2: Skipped (--no-index)"
else
  log_step "Step 2 / 4 — Index into Knowledge Base"
  bash "$SCRIPT_DIR/02_index.sh" "$REPORT_FILE"
fi

# =============================================================================
# STEP 3: Auto-apply structural fixes
# =============================================================================
if [[ "$SKIP_APPLY" == "true" ]]; then
  log_info "Step 3: Skipped (--no-apply)"
elif [[ "${AUTO_APPLY_ENABLED:-true}" != "true" ]]; then
  log_info "Step 3: Skipped (AUTO_APPLY_ENABLED=false)"
elif [[ -z "$TARGET_DOC" ]]; then
  log_warn "Step 3: Skipped — no --target-doc provided (auto-apply requires the source document)"
else
  log_step "Step 3 / 4 — Auto-apply structural fixes"
  bash "$SCRIPT_DIR/03_auto_apply.sh" "$ACTIONS_JSON" "$TARGET_DOC"
fi

# =============================================================================
# STEP 4: Create GitHub Issues
# =============================================================================
if [[ "$SKIP_ISSUES" == "true" ]]; then
  log_info "Step 4: Skipped (--no-issues)"
elif [[ -z "$GH_REPO" ]]; then
  log_warn "Step 4: Skipped — GH_REPO not set (set it in .env to enable GitHub Issues)"
else
  log_step "Step 4 / 4 — Create GitHub Issues"
  DRY_RUN="${DRY_RUN:-false}" python3 "$SCRIPT_DIR/04_create_issues.py" \
    --actions "$ACTIONS_JSON" \
    --report "$REPORT_FILE" \
    --doc-id "$DOC_ID" \
    $([ "${DRY_RUN:-false}" == "true" ] && echo "--dry-run" || true)
fi

# =============================================================================
# Final summary
# =============================================================================
echo ""
echo "════════════════════════════════════════════════════════════"
echo "  COUNCIL PIPELINE — Complete"
echo "════════════════════════════════════════════════════════════"
echo "  Report:   $REPORT_FILE"
echo "  Actions:  $TOTAL total (P0=$P0_COUNT, P1=$P1_COUNT, P2=$P2_COUNT)"
echo ""
echo "  Next steps:"
echo "  1. Review auto-applied commits: git log --oneline -10"
echo "  2. Review GitHub Issues: gh issue list --repo $GH_REPO --label council:remediation"
echo "  3. Address P0 issues before PR merge"
echo "════════════════════════════════════════════════════════════"
