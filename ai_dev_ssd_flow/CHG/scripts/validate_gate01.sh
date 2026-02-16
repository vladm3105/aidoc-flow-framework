#!/bin/bash
# =============================================================================
# GATE-01 Validation Script
# Validates Business/Product Gate requirements (L1-L4)
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
CHG_FILE="${1:-}"
VERBOSE="${2:-}"

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

print_header() {
  echo "=========================================="
  echo "GATE-01 Validation (Business/Product)"
  echo "Layers: L1-L4 (BRD, PRD, EARS, BDD)"
  echo "=========================================="
  echo "File: $CHG_FILE"
  echo "Date: $(TZ=America/New_York date '+%Y-%m-%d %H:%M:%S %Z')"
  echo ""
}

usage() {
  echo "Usage: $0 <CHG_FILE> [--verbose]"
  echo ""
  echo "Validates CHG document against GATE-01 requirements."
  echo ""
  echo "Exit codes:"
  echo "  0 = Pass (no errors, no warnings)"
  echo "  1 = Pass with warnings (non-blocking)"
  echo "  2 = Fail (blocking errors)"
  echo "  3 = Invalid input"
  exit 3
}

# -----------------------------------------------------------------------------
# Validation Checks
# -----------------------------------------------------------------------------

check_business_justification() {
  echo "--- GATE-01-E001: Business Justification ---"

  local has_justification=0

  # Check for business justification section or content
  if grep -qiE "(business justification|business rationale|business need|business impact)" "$CHG_FILE" 2>/dev/null; then
    has_justification=1
  fi

  # Also check for reason section with business content
  if grep -qiE "reason for change" "$CHG_FILE" 2>/dev/null; then
    has_justification=1
  fi

  if [[ $has_justification -eq 0 ]]; then
    echo -e "${RED}GATE-01-E001: Missing business justification${NC}"
    echo "  → Add 'Business Justification' section with measurable impact"
    ((ERRORS++)) || true
  else
    echo -e "${GREEN}  ✓ Business justification present${NC}"
  fi
}

check_prd_brd_linkage() {
  echo ""
  echo "--- GATE-01-E002: PRD-BRD Linkage ---"

  # Check if this is a PRD-related change
  if grep -qiE "PRD|product requirement" "$CHG_FILE" 2>/dev/null; then
    # Must have @brd tag
    if ! grep -qE "@brd:" "$CHG_FILE" 2>/dev/null; then
      echo -e "${RED}GATE-01-E002: PRD change missing @brd traceability${NC}"
      echo "  → Add @brd: BRD-XXX tag linking to business requirement"
      ((ERRORS++)) || true
    else
      echo -e "${GREEN}  ✓ PRD-BRD linkage present${NC}"
    fi
  else
    echo -e "${GREEN}  ✓ N/A (not a PRD change)${NC}"
  fi
}

check_ears_syntax() {
  echo ""
  echo "--- GATE-01-E003: EARS Syntax ---"

  # Check if EARS artifacts are mentioned
  if grep -qiE "EARS|EARS-[0-9]" "$CHG_FILE" 2>/dev/null; then
    # Check for WHEN-THE-SHALL pattern in related files
    local ears_file
    ears_file=$(grep -oE "EARS-[0-9]+\.[0-9]+\.[0-9]+" "$CHG_FILE" 2>/dev/null | head -1 || true)

    if [[ -n "$ears_file" ]]; then
      # This is a reference check - actual EARS validation would check the EARS file
      echo -e "${BLUE}  ℹ EARS reference found: $ears_file${NC}"
      echo "  → Verify EARS follows WHEN-THE-SHALL-WITHIN syntax"
      ((INFO++)) || true
    fi
  else
    echo -e "${GREEN}  ✓ N/A (no EARS changes)${NC}"
  fi
}

check_bdd_format() {
  echo ""
  echo "--- GATE-01-E004: BDD Format ---"

  # Check if BDD artifacts are mentioned
  if grep -qiE "BDD|SCEN-|feature file|given.*when.*then" "$CHG_FILE" 2>/dev/null; then
    local bdd_ref
    bdd_ref=$(grep -oE "SCEN-[0-9]+" "$CHG_FILE" 2>/dev/null | head -1 || true)

    if [[ -n "$bdd_ref" ]]; then
      echo -e "${BLUE}  ℹ BDD reference found: $bdd_ref${NC}"
      echo "  → Verify BDD follows Given-When-Then format"
      ((INFO++)) || true
    fi
  else
    echo -e "${GREEN}  ✓ N/A (no BDD changes)${NC}"
  fi
}

check_breaking_change_classification() {
  echo ""
  echo "--- GATE-01-E005: Breaking Change Classification ---"

  # Check if change is marked as breaking
  local is_breaking=0
  if grep -qiE "breaking.*(change|api|compatibility)|backward.*incompatible" "$CHG_FILE" 2>/dev/null; then
    is_breaking=1
  fi

  if [[ $is_breaking -eq 1 ]]; then
    # Must be L3
    if ! grep -qE "change_level:.*L3|Change Level.*L3|L3.*Major" "$CHG_FILE" 2>/dev/null; then
      echo -e "${RED}GATE-01-E005: Breaking change not classified as L3${NC}"
      echo "  → Breaking changes MUST be classified as L3 (Major)"
      ((ERRORS++)) || true
    else
      echo -e "${GREEN}  ✓ Breaking change correctly classified as L3${NC}"
    fi
  else
    echo -e "${GREEN}  ✓ No breaking changes detected${NC}"
  fi
}

check_stakeholder_approval() {
  echo ""
  echo "--- GATE-01-E006: Stakeholder Approval (L3) ---"

  # Check if L3 change
  if grep -qE "change_level:.*L3|Change Level.*L3|L3.*Major" "$CHG_FILE" 2>/dev/null; then
    # Must have stakeholder approval
    if ! grep -qiE "stakeholder.*(approval|sign|approved)|approved.*stakeholder" "$CHG_FILE" 2>/dev/null; then
      echo -e "${RED}GATE-01-E006: L3 change missing stakeholder approval${NC}"
      echo "  → L3 changes require stakeholder sign-off"
      ((ERRORS++)) || true
    else
      echo -e "${GREEN}  ✓ Stakeholder approval documented${NC}"
    fi
  else
    echo -e "${GREEN}  ✓ N/A (not L3 change)${NC}"
  fi
}

check_scope_warning() {
  echo ""
  echo "--- GATE-01-W001: Scope Assessment ---"

  # Count layers mentioned
  local layer_count=0
  for layer in L1 L2 L3 L4 L5 L6 L7 L8 L9 L10 L11 L12 L13 L14; do
    if grep -qE "Layer.*$layer|$layer[^0-9]|L$(echo $layer | sed 's/L//')" "$CHG_FILE" 2>/dev/null; then
      ((layer_count++)) || true
    fi
  done

  if [[ $layer_count -gt 5 ]]; then
    if ! grep -qE "change_level:.*L3|Change Level.*L3" "$CHG_FILE" 2>/dev/null; then
      echo -e "${YELLOW}GATE-01-W001: Large scope ($layer_count layers) without L3 classification${NC}"
      echo "  → Consider elevating to L3 or phased implementation"
      ((WARNINGS++)) || true
    fi
  else
    echo -e "${GREEN}  ✓ Scope acceptable ($layer_count layers affected)${NC}"
  fi
}

check_l2_approval() {
  echo ""
  echo "--- GATE-01-W002: L2 Approval ---"

  # Check if L2 change
  if grep -qE "change_level:.*L2|Change Level.*L2|L2.*Minor" "$CHG_FILE" 2>/dev/null; then
    # Check for PO approval
    if ! grep -qiE "(product owner|PO).*(approval|approved|sign)" "$CHG_FILE" 2>/dev/null; then
      echo -e "${YELLOW}GATE-01-W002: L2 change may need Product Owner approval${NC}"
      echo "  → Recommend obtaining PO sign-off"
      ((WARNINGS++)) || true
    else
      echo -e "${GREEN}  ✓ L2 approval documented${NC}"
    fi
  else
    echo -e "${GREEN}  ✓ N/A (not L2 change)${NC}"
  fi
}

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------

print_summary() {
  echo ""
  echo "=========================================="
  echo "GATE-01 Validation Summary"
  echo "=========================================="
  echo -e "Errors:   ${RED}$ERRORS${NC}"
  echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
  echo -e "Info:     ${BLUE}$INFO${NC}"
  echo ""

  if [[ $ERRORS -gt 0 ]]; then
    echo -e "${RED}GATE-01 FAILED: $ERRORS error(s) must be fixed${NC}"
    exit 2
  elif [[ $WARNINGS -gt 0 ]]; then
    echo -e "${YELLOW}GATE-01 PASSED with $WARNINGS warning(s)${NC}"
    exit 1
  else
    echo -e "${GREEN}GATE-01 PASSED: All validation checks passed${NC}"
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

  # Run all checks
  check_business_justification
  check_prd_brd_linkage
  check_ears_syntax
  check_bdd_format
  check_breaking_change_classification
  check_stakeholder_approval
  check_scope_warning
  check_l2_approval

  print_summary
}

# Run main function
main "$@"
