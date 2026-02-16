#!/bin/bash
# =============================================================================
# All Gates Validation Script
# Orchestrates validation across all applicable gates for a CHG document
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Counters
TOTAL_ERRORS=0
TOTAL_WARNINGS=0
GATES_PASSED=0
GATES_FAILED=0
GATES_SKIPPED=0

# Configuration
CHG_FILE="${1:-}"
VERBOSE=""
SOURCE=""
RETROACTIVE=""

# Parse arguments
shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --verbose|-v)
      VERBOSE="--verbose"
      shift
      ;;
    --source=*)
      SOURCE="${1#*=}"
      shift
      ;;
    --retroactive)
      RETROACTIVE="true"
      shift
      ;;
    --help|-h)
      usage
      ;;
    *)
      shift
      ;;
  esac
done

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

print_header() {
  echo ""
  echo "╔══════════════════════════════════════════════════════════════════════╗"
  echo "║              4-GATE CHANGE MANAGEMENT VALIDATION                     ║"
  echo "╠══════════════════════════════════════════════════════════════════════╣"
  echo "║  File: $(printf '%-60s' "$CHG_FILE") ║"
  echo "║  Date: $(printf '%-60s' "$(TZ=America/New_York date '+%Y-%m-%d %H:%M:%S %Z')") ║"
  if [[ -n "$SOURCE" ]]; then
    echo "║  Source: $(printf '%-58s' "$SOURCE") ║"
  fi
  if [[ -n "$RETROACTIVE" ]]; then
    echo "║  Mode: $(printf '%-60s' "RETROACTIVE (post-emergency)") ║"
  fi
  echo "╚══════════════════════════════════════════════════════════════════════╝"
  echo ""
}

usage() {
  echo "Usage: $0 <CHG_FILE> [OPTIONS]"
  echo ""
  echo "Validates CHG document against all applicable gates."
  echo ""
  echo "Options:"
  echo "  --verbose, -v       Verbose output"
  echo "  --source=<source>   Change source (upstream, midstream, downstream, external, feedback)"
  echo "  --retroactive       Retroactive validation (for emergency bypass)"
  echo "  --help, -h          Show this help message"
  echo ""
  echo "Exit codes:"
  echo "  0 = All gates pass (no errors, no warnings)"
  echo "  1 = All gates pass with warnings (non-blocking)"
  echo "  2 = One or more gates fail (blocking errors)"
  echo "  3 = Invalid input"
  exit 3
}

# Determine applicable gates based on change source and affected layers
determine_applicable_gates() {
  local chg_file="$1"
  local gates=()

  # Read file content
  local content
  content=$(cat "$chg_file")

  # Extract change source
  local source
  source=$(echo "$content" | grep -oE "change_source:\s*\w+" | head -1 | sed 's/change_source:\s*//' || echo "")

  if [[ -n "$SOURCE" ]]; then
    source="$SOURCE"
  fi

  # Determine gates based on source
  case "$source" in
    upstream)
      gates=("GATE-01" "GATE-05" "GATE-09" "GATE-12")
      ;;
    midstream)
      # Check if bubble-up to GATE-01 required
      if echo "$content" | grep -qiE "L[1-4]|BRD|PRD|EARS|BDD"; then
        gates=("GATE-01" "GATE-05" "GATE-09" "GATE-12")
      else
        gates=("GATE-05" "GATE-09" "GATE-12")
      fi
      ;;
    design-optimization)
      gates=("GATE-09" "GATE-12")
      ;;
    downstream|feedback)
      # Check if bubble-up required
      if echo "$content" | grep -qiE "bubble.up|root.cause.*L[1-9]"; then
        gates=("GATE-05" "GATE-09" "GATE-12")
      else
        gates=("GATE-12")
      fi
      ;;
    external)
      gates=("GATE-05" "GATE-09" "GATE-12")
      ;;
    emergency)
      gates=("EMERGENCY")
      ;;
    *)
      # Default: check all gates based on affected layers
      if echo "$content" | grep -qiE "L[1-4]|BRD|PRD|EARS|BDD"; then
        gates+=("GATE-01")
      fi
      if echo "$content" | grep -qiE "L[5-8]|ADR|SYS|REQ|CTR"; then
        gates+=("GATE-05")
      fi
      if echo "$content" | grep -qiE "L(9|10|11)|SPEC|TSPEC|TASKS"; then
        gates+=("GATE-09")
      fi
      if echo "$content" | grep -qiE "L1[2-4]|code|test|validation"; then
        gates+=("GATE-12")
      fi

      # If no gates detected, default to GATE-12
      if [[ ${#gates[@]} -eq 0 ]]; then
        gates=("GATE-12")
      fi
      ;;
  esac

  echo "${gates[@]}"
}

run_gate_validation() {
  local gate="$1"
  local chg_file="$2"
  local script=""

  echo ""
  echo "┌──────────────────────────────────────────────────────────────────────┐"
  echo "│  $gate VALIDATION"
  echo "└──────────────────────────────────────────────────────────────────────┘"

  case "$gate" in
    GATE-01)
      script="$SCRIPT_DIR/validate_gate01.sh"
      ;;
    GATE-05)
      script="$SCRIPT_DIR/validate_gate05.sh"
      ;;
    GATE-09)
      script="$SCRIPT_DIR/validate_gate09.sh"
      ;;
    GATE-12)
      script="$SCRIPT_DIR/validate_gate12.sh"
      ;;
    EMERGENCY)
      script="$SCRIPT_DIR/validate_emergency_bypass.sh"
      ;;
    *)
      echo -e "${YELLOW}  ⚠ Unknown gate: $gate (skipped)${NC}"
      ((GATES_SKIPPED++)) || true
      return 0
      ;;
  esac

  # Check if script exists
  if [[ ! -x "$script" ]]; then
    echo -e "${YELLOW}  ⚠ Script not found or not executable: $script${NC}"
    ((GATES_SKIPPED++)) || true
    return 0
  fi

  # Run validation script
  local exit_code=0
  "$script" "$chg_file" $VERBOSE || exit_code=$?

  # Track results
  case $exit_code in
    0)
      ((GATES_PASSED++)) || true
      ;;
    1)
      ((GATES_PASSED++)) || true
      ((TOTAL_WARNINGS++)) || true
      ;;
    2)
      ((GATES_FAILED++)) || true
      ((TOTAL_ERRORS++)) || true
      ;;
  esac

  return $exit_code
}

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------

print_summary() {
  echo ""
  echo "╔══════════════════════════════════════════════════════════════════════╗"
  echo "║                    VALIDATION SUMMARY                                 ║"
  echo "╠══════════════════════════════════════════════════════════════════════╣"
  printf "║  Gates Passed:  %-54s ║\n" "${GREEN}$GATES_PASSED${NC}"
  printf "║  Gates Failed:  %-54s ║\n" "${RED}$GATES_FAILED${NC}"
  printf "║  Gates Skipped: %-54s ║\n" "${YELLOW}$GATES_SKIPPED${NC}"
  echo "╠══════════════════════════════════════════════════════════════════════╣"
  printf "║  Total Errors:   %-53s ║\n" "${RED}$TOTAL_ERRORS${NC}"
  printf "║  Total Warnings: %-53s ║\n" "${YELLOW}$TOTAL_WARNINGS${NC}"
  echo "╚══════════════════════════════════════════════════════════════════════╝"
  echo ""

  if [[ $GATES_FAILED -gt 0 ]]; then
    echo -e "${RED}╔══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  VALIDATION FAILED: $GATES_FAILED gate(s) failed validation                      ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════════════╝${NC}"
    exit 2
  elif [[ $TOTAL_WARNINGS -gt 0 ]]; then
    echo -e "${YELLOW}╔══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║  VALIDATION PASSED with $TOTAL_WARNINGS warning(s)                               ║${NC}"
    echo -e "${YELLOW}╚══════════════════════════════════════════════════════════════════════╝${NC}"
    exit 1
  else
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ALL GATES PASSED                                                    ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════╝${NC}"
    exit 0
  fi
}

# -----------------------------------------------------------------------------
# Main Execution
# -----------------------------------------------------------------------------

main() {
  # Validate input
  if [[ -z "$CHG_FILE" ]]; then
    usage
  fi

  if [[ ! -f "$CHG_FILE" ]]; then
    echo -e "${RED}ERROR: File not found: $CHG_FILE${NC}"
    exit 3
  fi

  print_header

  # Determine applicable gates
  echo "Determining applicable gates..."
  local applicable_gates
  read -ra applicable_gates <<< "$(determine_applicable_gates "$CHG_FILE")"

  echo "Applicable gates: ${applicable_gates[*]}"

  # Run routing validation first
  echo ""
  echo "┌──────────────────────────────────────────────────────────────────────┐"
  echo "│  ROUTING VALIDATION"
  echo "└──────────────────────────────────────────────────────────────────────┘"

  if [[ -x "$SCRIPT_DIR/validate_chg_routing.py" ]]; then
    python3 "$SCRIPT_DIR/validate_chg_routing.py" "$CHG_FILE" $VERBOSE || true
  else
    echo -e "${YELLOW}  ⚠ Routing validation script not found${NC}"
  fi

  # Run gate validations
  for gate in "${applicable_gates[@]}"; do
    run_gate_validation "$gate" "$CHG_FILE" || true
  done

  print_summary
}

# Run main function
main "$@"
