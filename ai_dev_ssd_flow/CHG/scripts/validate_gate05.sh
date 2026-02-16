#!/bin/bash
# =============================================================================
# GATE-05 Validation Script
# Validates Architecture/Contract Gate requirements (L5-L8)
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
  echo "GATE-05 Validation (Architecture/Contract)"
  echo "Layers: L5-L8 (ADR, SYS, REQ, CTR)"
  echo "=========================================="
  echo "File: $CHG_FILE"
  echo "Date: $(TZ=America/New_York date '+%Y-%m-%d %H:%M:%S %Z')"
  echo ""
}

usage() {
  echo "Usage: $0 <CHG_FILE> [--verbose]"
  echo ""
  echo "Validates CHG document against GATE-05 requirements."
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

check_adr_structure() {
  echo "--- GATE-05-E001: ADR Structure ---"

  # Check if ADR is mentioned
  if grep -qiE "ADR|architecture decision" "$CHG_FILE" 2>/dev/null; then
    # Check for Context-Decision-Consequences
    local has_context has_decision has_consequences
    has_context=$(grep -ciE "^#+.*context|context.*:" "$CHG_FILE" 2>/dev/null || echo 0)
    has_decision=$(grep -ciE "^#+.*decision|decision.*:" "$CHG_FILE" 2>/dev/null || echo 0)
    has_consequences=$(grep -ciE "^#+.*consequences|consequences.*:" "$CHG_FILE" 2>/dev/null || echo 0)

    if [[ $has_context -eq 0 || $has_decision -eq 0 || $has_consequences -eq 0 ]]; then
      echo -e "${YELLOW}  ℹ ADR referenced - verify Context-Decision-Consequences in ADR file${NC}"
      ((INFO++)) || true
    else
      echo -e "${GREEN}  ✓ ADR structure elements present${NC}"
    fi
  else
    echo -e "${GREEN}  ✓ N/A (no ADR changes)${NC}"
  fi
}

check_sys_measurable() {
  echo ""
  echo "--- GATE-05-E002: SYS Measurable Quality Attributes ---"

  # Check if SYS is mentioned
  if grep -qiE "SYS-|system requirement|quality attribute" "$CHG_FILE" 2>/dev/null; then
    # Check for measurable thresholds
    if grep -qE "[0-9]+\s*(ms|s|%|MB|GB|req/s|rps|qps)" "$CHG_FILE" 2>/dev/null; then
      echo -e "${GREEN}  ✓ Measurable thresholds present${NC}"
    else
      echo -e "${YELLOW}GATE-05-E002: Quality attributes may lack measurable thresholds${NC}"
      echo "  → Add quantified thresholds (e.g., '< 100ms', '>= 99.9%')"
      ((WARNINGS++)) || true
    fi
  else
    echo -e "${GREEN}  ✓ N/A (no SYS changes)${NC}"
  fi
}

check_req_traceability() {
  echo ""
  echo "--- GATE-05-E003: REQ Traceability Tags ---"

  # Check if REQ is mentioned
  if grep -qiE "REQ-[0-9]|atomic requirement" "$CHG_FILE" 2>/dev/null; then
    # Check for 6 upstream traceability tags
    local tags_found=0
    for tag in "@brd:" "@prd:" "@ears:" "@bdd:" "@adr:" "@sys:"; do
      if grep -q "$tag" "$CHG_FILE" 2>/dev/null; then
        ((tags_found++)) || true
      fi
    done

    if [[ $tags_found -lt 6 ]]; then
      echo -e "${YELLOW}  ℹ REQ referenced - verify 6 upstream traceability tags in REQ file${NC}"
      echo "  → Found $tags_found/6 tags in CHG. Verify REQ has: @brd, @prd, @ears, @bdd, @adr, @sys"
      ((INFO++)) || true
    else
      echo -e "${GREEN}  ✓ All 6 traceability tags present${NC}"
    fi
  else
    echo -e "${GREEN}  ✓ N/A (no REQ changes)${NC}"
  fi
}

check_ctr_validation() {
  echo ""
  echo "--- GATE-05-E004: CTR Schema Validation ---"

  # Check if CTR is mentioned
  if grep -qiE "CTR-|contract|API.*schema" "$CHG_FILE" 2>/dev/null; then
    echo -e "${BLUE}  ℹ CTR referenced - verify YAML + MD synchronization${NC}"
    echo "  → Run: python scripts/validate_ctr.py <CTR_FILE>"
    ((INFO++)) || true
  else
    echo -e "${GREEN}  ✓ N/A (no CTR changes)${NC}"
  fi
}

check_breaking_api_classification() {
  echo ""
  echo "--- GATE-05-E005: Breaking API Classification ---"

  # Check for breaking API changes
  if grep -qiE "breaking.*(api|contract|interface)|api.*breaking|backward.*incompatible" "$CHG_FILE" 2>/dev/null; then
    if ! grep -qE "change_level:.*L3|Change Level.*L3|L3.*Major" "$CHG_FILE" 2>/dev/null; then
      echo -e "${RED}GATE-05-E005: Breaking API change not classified as L3${NC}"
      echo "  → Breaking API changes MUST be classified as L3 (Major)"
      ((ERRORS++)) || true
    else
      echo -e "${GREEN}  ✓ Breaking API correctly classified as L3${NC}"
    fi
  else
    echo -e "${GREEN}  ✓ No breaking API changes detected${NC}"
  fi
}

check_security_review() {
  echo ""
  echo "--- GATE-05-E006: Security Review (External) ---"

  # Check if external security change
  if grep -qiE "external|security|CVE|vulnerability" "$CHG_FILE" 2>/dev/null; then
    if grep -qiE "change_source:.*external|security" "$CHG_FILE" 2>/dev/null; then
      if ! grep -qiE "security.*(review|assessment|approved)|CVE-[0-9]" "$CHG_FILE" 2>/dev/null; then
        echo -e "${RED}GATE-05-E006: External/security change missing security review${NC}"
        echo "  → Complete security assessment before proceeding"
        ((ERRORS++)) || true
      else
        echo -e "${GREEN}  ✓ Security review documented${NC}"
      fi
    fi
  else
    echo -e "${GREEN}  ✓ N/A (not external/security change)${NC}"
  fi
}

check_cve_reference() {
  echo ""
  echo "--- GATE-05-W001: CVE Reference ---"

  # Check for security-related content without CVE
  if grep -qiE "security|vulnerability|exploit" "$CHG_FILE" 2>/dev/null; then
    if ! grep -qE "CVE-[0-9]{4}-[0-9]+" "$CHG_FILE" 2>/dev/null; then
      echo -e "${YELLOW}GATE-05-W001: Security change without CVE reference${NC}"
      echo "  → Add CVE-YYYY-NNNNN reference if applicable"
      ((WARNINGS++)) || true
    else
      local cve
      cve=$(grep -oE "CVE-[0-9]{4}-[0-9]+" "$CHG_FILE" 2>/dev/null | head -1)
      echo -e "${GREEN}  ✓ CVE reference found: $cve${NC}"
    fi
  else
    echo -e "${GREEN}  ✓ N/A (not security-related)${NC}"
  fi
}

check_ctr_changelog() {
  echo ""
  echo "--- GATE-05-W002: CTR Changelog ---"

  # Check if CTR version change
  if grep -qiE "CTR.*version|API.*v[0-9]|contract.*update" "$CHG_FILE" 2>/dev/null; then
    if ! grep -qiE "changelog|version.*history|what.*changed" "$CHG_FILE" 2>/dev/null; then
      echo -e "${YELLOW}GATE-05-W002: CTR version change without changelog${NC}"
      echo "  → Document API changes in changelog section"
      ((WARNINGS++)) || true
    else
      echo -e "${GREEN}  ✓ CTR changelog documented${NC}"
    fi
  else
    echo -e "${GREEN}  ✓ N/A (no CTR version change)${NC}"
  fi
}

check_adr_alternatives() {
  echo ""
  echo "--- GATE-05-W003: ADR Alternatives ---"

  # Check for ADR without alternatives
  if grep -qiE "ADR|architecture decision" "$CHG_FILE" 2>/dev/null; then
    if ! grep -qiE "alternative|option|considered" "$CHG_FILE" 2>/dev/null; then
      echo -e "${YELLOW}GATE-05-W003: ADR may be missing alternatives section${NC}"
      echo "  → Document considered alternatives in ADR"
      ((WARNINGS++)) || true
    else
      echo -e "${GREEN}  ✓ Alternatives considered documented${NC}"
    fi
  else
    echo -e "${GREEN}  ✓ N/A (no ADR changes)${NC}"
  fi
}

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------

print_summary() {
  echo ""
  echo "=========================================="
  echo "GATE-05 Validation Summary"
  echo "=========================================="
  echo -e "Errors:   ${RED}$ERRORS${NC}"
  echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
  echo -e "Info:     ${BLUE}$INFO${NC}"
  echo ""

  if [[ $ERRORS -gt 0 ]]; then
    echo -e "${RED}GATE-05 FAILED: $ERRORS error(s) must be fixed${NC}"
    exit 2
  elif [[ $WARNINGS -gt 0 ]]; then
    echo -e "${YELLOW}GATE-05 PASSED with $WARNINGS warning(s)${NC}"
    exit 1
  else
    echo -e "${GREEN}GATE-05 PASSED: All validation checks passed${NC}"
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
  check_adr_structure
  check_sys_measurable
  check_req_traceability
  check_ctr_validation
  check_breaking_api_classification
  check_security_review
  check_cve_reference
  check_ctr_changelog
  check_adr_alternatives

  print_summary
}

# Run main function
main "$@"
