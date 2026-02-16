#!/bin/bash
# =============================================================================
# Emergency Bypass Validation Script
# Validates emergency CHG documents and post-mortem completion
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
ERRORS=0
WARNINGS=0
INFO=0

# Configuration
CHG_DIR="${1:-}"
CHECK_POSTMORTEM="${2:-}"

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

print_header() {
  echo "=========================================="
  echo "Emergency Bypass Validation"
  echo "=========================================="
  echo "Directory: $CHG_DIR"
  echo "Date: $(TZ=America/New_York date '+%Y-%m-%d %H:%M:%S %Z')"
  echo ""
}

usage() {
  echo "Usage: $0 <CHG_DIR> [--check-postmortem]"
  echo ""
  echo "Validates emergency CHG documents and post-incident requirements."
  echo ""
  echo "Options:"
  echo "  --check-postmortem  Check post-mortem completion (72h requirement)"
  echo ""
  echo "Exit codes:"
  echo "  0 = Pass (no errors, no warnings)"
  echo "  1 = Pass with warnings (non-blocking)"
  echo "  2 = Fail (blocking errors)"
  echo "  3 = Invalid input"
  exit 3
}

# -----------------------------------------------------------------------------
# Find CHG file
# -----------------------------------------------------------------------------

find_chg_file() {
  local chg_file=""

  if [[ -f "$CHG_DIR" ]]; then
    # Direct file path
    chg_file="$CHG_DIR"
    CHG_DIR=$(dirname "$chg_file")
  else
    # Directory - find CHG file
    chg_file=$(find "$CHG_DIR" -maxdepth 1 -name "CHG-EMG-*.md" -o -name "CHG-*.md" | head -1)
  fi

  echo "$chg_file"
}

# -----------------------------------------------------------------------------
# Validation Checks
# -----------------------------------------------------------------------------

check_emergency_authorization() {
  local chg_file="$1"
  echo "--- EMG-E001: Emergency Authorization ---"

  # Check for incident commander authorization
  if grep -qiE "incident.commander|authorized.by|bypass.authorized" "$chg_file" 2>/dev/null; then
    echo -e "${GREEN}  ✓ Emergency authorization documented${NC}"
  else
    echo -e "${RED}EMG-E001: Emergency not authorized by incident commander${NC}"
    echo "  → Document 'Bypass Authorized By' field"
    ((ERRORS++)) || true
  fi
}

check_emergency_criteria() {
  local chg_file="$1"
  echo ""
  echo "--- EMG-E002: Emergency Criteria ---"

  local is_emergency=0

  # Check for P1 incident
  if grep -qiE "P1|production.down|critical.security|CVSS.*(9\.[0-9]|10\.0)|data.breach" "$chg_file" 2>/dev/null; then
    is_emergency=1
  fi

  if [[ $is_emergency -eq 1 ]]; then
    echo -e "${GREEN}  ✓ Valid emergency criteria met${NC}"
  else
    echo -e "${RED}EMG-E002: Non-critical issue using emergency bypass${NC}"
    echo "  → Use standard gate process for non-emergency changes"
    ((ERRORS++)) || true
  fi
}

check_emergency_stub() {
  local chg_file="$1"
  echo ""
  echo "--- EMG-E003: Emergency Stub Created ---"

  if [[ -f "$chg_file" ]]; then
    # Check for minimal required content
    local has_summary has_incident_ref
    has_summary=$(grep -ciE "incident.summary|problem.statement" "$chg_file" 2>/dev/null || echo 0)
    has_incident_ref=$(grep -ciE "INC-[0-9]|incident.ticket" "$chg_file" 2>/dev/null || echo 0)

    if [[ $has_summary -gt 0 ]]; then
      echo -e "${GREEN}  ✓ Emergency stub created with summary${NC}"
    else
      echo -e "${YELLOW}  ℹ Consider adding incident summary to stub${NC}"
      ((INFO++)) || true
    fi
  else
    echo -e "${RED}EMG-E003: Emergency stub not found${NC}"
    echo "  → Create CHG-EMG-{timestamp}.md with minimal details"
    ((ERRORS++)) || true
  fi
}

check_postmortem() {
  local chg_dir="$1"
  local chg_file="$2"
  echo ""
  echo "--- EMG-E004: Post-Mortem (72h requirement) ---"

  # Look for post-mortem file
  local postmortem_file
  postmortem_file=$(find "$chg_dir" -name "POST_MORTEM*.md" -o -name "post_mortem*.md" -o -name "postmortem*.md" 2>/dev/null | head -1 || true)

  if [[ -n "$postmortem_file" && -f "$postmortem_file" ]]; then
    echo -e "${GREEN}  ✓ Post-mortem document found: $(basename "$postmortem_file")${NC}"

    # Check for RCA
    if grep -qiE "5.why|root.cause|rca" "$postmortem_file" 2>/dev/null; then
      echo -e "${GREEN}  ✓ Root cause analysis present${NC}"
    else
      echo -e "${YELLOW}EMG-W003: Post-mortem may be missing root cause analysis${NC}"
      echo "  → Complete 5-Whys analysis"
      ((WARNINGS++)) || true
    fi

    # Check for action items
    if grep -qiE "action.item|follow.up|preventive" "$postmortem_file" 2>/dev/null; then
      echo -e "${GREEN}  ✓ Action items documented${NC}"
    else
      echo -e "${YELLOW}  ℹ Consider adding action items to post-mortem${NC}"
      ((INFO++)) || true
    fi
  else
    # Check if post-mortem is required (based on file creation time)
    if [[ -f "$chg_file" ]]; then
      local file_age
      file_age=$(( ( $(date +%s) - $(stat -c %Y "$chg_file" 2>/dev/null || stat -f %m "$chg_file" 2>/dev/null) ) / 3600 ))

      if [[ $file_age -gt 72 ]]; then
        echo -e "${RED}EMG-E004: Post-mortem not completed within 72 hours${NC}"
        echo "  → Emergency CHG created ${file_age}h ago, post-mortem overdue"
        ((ERRORS++)) || true
      else
        echo -e "${YELLOW}  ℹ Post-mortem due within 72h (${file_age}h elapsed)${NC}"
        ((INFO++)) || true
      fi
    else
      echo -e "${YELLOW}  ℹ Post-mortem file not found (may not be required yet)${NC}"
      ((INFO++)) || true
    fi
  fi
}

check_emergency_closure() {
  local chg_file="$1"
  echo ""
  echo "--- EMG-E005: Emergency CHG Closure ---"

  # Check for completion status
  if grep -qiE "status.*completed|completed.*status" "$chg_file" 2>/dev/null; then
    # Verify closure requirements
    local closure_items=0

    if grep -qiE "post.mortem.*complete|post-mortem.*complete" "$chg_file" 2>/dev/null; then
      ((closure_items++)) || true
    fi

    if grep -qiE "gate.*valid|retroactive.*valid" "$chg_file" 2>/dev/null; then
      ((closure_items++)) || true
    fi

    if grep -qiE "follow.up.*CHG|preventive.*CHG" "$chg_file" 2>/dev/null; then
      ((closure_items++)) || true
    fi

    if [[ $closure_items -ge 2 ]]; then
      echo -e "${GREEN}  ✓ Emergency CHG properly closed${NC}"
    else
      echo -e "${YELLOW}EMG-E005: Emergency CHG may have incomplete closure${NC}"
      echo "  → Verify: post-mortem, gate validation, follow-up CHGs"
      ((WARNINGS++)) || true
    fi
  else
    echo -e "${BLUE}  ℹ Emergency CHG not yet marked completed${NC}"
    ((INFO++)) || true
  fi
}

check_incident_reference() {
  local chg_file="$1"
  echo ""
  echo "--- EMG-W001: Incident Reference ---"

  if grep -qE "INC-[0-9]+|incident_ticket|incident.number" "$chg_file" 2>/dev/null; then
    local inc_ref
    inc_ref=$(grep -oE "INC-[0-9]+" "$chg_file" 2>/dev/null | head -1 || echo "")
    if [[ -n "$inc_ref" ]]; then
      echo -e "${GREEN}  ✓ Incident reference: $inc_ref${NC}"
    else
      echo -e "${GREEN}  ✓ Incident reference field present${NC}"
    fi
  else
    echo -e "${YELLOW}EMG-W001: Missing incident ticket reference${NC}"
    echo "  → Add INC-XXX incident reference"
    ((WARNINGS++)) || true
  fi
}

check_followup_chg() {
  local chg_dir="$1"
  local chg_file="$2"
  echo ""
  echo "--- EMG-W002: Follow-Up CHG ---"

  # Check if follow-up CHG is mentioned
  if grep -qiE "follow.up.*CHG|preventive.*measure.*CHG|CHG-[0-9]" "$chg_file" 2>/dev/null; then
    echo -e "${GREEN}  ✓ Follow-up CHG referenced${NC}"
  else
    # Only warn if post-mortem exists (follow-up should come from post-mortem)
    local postmortem_file
    postmortem_file=$(find "$chg_dir" -name "POST_MORTEM*.md" -o -name "post_mortem*.md" 2>/dev/null | head -1 || true)

    if [[ -n "$postmortem_file" && -f "$postmortem_file" ]]; then
      echo -e "${YELLOW}EMG-W002: Preventive measure CHG not documented${NC}"
      echo "  → Create follow-up CHG for preventive measures from post-mortem"
      ((WARNINGS++)) || true
    else
      echo -e "${BLUE}  ℹ Follow-up CHG pending post-mortem completion${NC}"
      ((INFO++)) || true
    fi
  fi
}

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------

print_summary() {
  echo ""
  echo "=========================================="
  echo "Emergency Bypass Validation Summary"
  echo "=========================================="
  echo -e "Errors:   ${RED}$ERRORS${NC}"
  echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
  echo -e "Info:     ${BLUE}$INFO${NC}"
  echo ""

  if [[ $ERRORS -gt 0 ]]; then
    echo -e "${RED}EMERGENCY VALIDATION FAILED: $ERRORS error(s) must be fixed${NC}"
    exit 2
  elif [[ $WARNINGS -gt 0 ]]; then
    echo -e "${YELLOW}EMERGENCY VALIDATION PASSED with $WARNINGS warning(s)${NC}"
    exit 1
  else
    echo -e "${GREEN}EMERGENCY VALIDATION PASSED: All checks passed${NC}"
    exit 0
  fi
}

# -----------------------------------------------------------------------------
# Main Execution
# -----------------------------------------------------------------------------

main() {
  # Validate input
  if [[ -z "$CHG_DIR" ]]; then
    usage
  fi

  if [[ ! -d "$CHG_DIR" && ! -f "$CHG_DIR" ]]; then
    echo -e "${RED}ERROR: Path not found: $CHG_DIR${NC}"
    exit 3
  fi

  print_header

  # Find CHG file
  local chg_file
  chg_file=$(find_chg_file)

  if [[ -z "$chg_file" || ! -f "$chg_file" ]]; then
    echo -e "${RED}ERROR: No CHG file found in $CHG_DIR${NC}"
    exit 3
  fi

  echo "CHG File: $chg_file"
  echo ""

  # Determine CHG directory
  local chg_dir
  chg_dir=$(dirname "$chg_file")

  # Run all checks
  check_emergency_authorization "$chg_file"
  check_emergency_criteria "$chg_file"
  check_emergency_stub "$chg_file"
  check_postmortem "$chg_dir" "$chg_file"
  check_emergency_closure "$chg_file"
  check_incident_reference "$chg_file"
  check_followup_chg "$chg_dir" "$chg_file"

  print_summary
}

# Run main function
main "$@"
