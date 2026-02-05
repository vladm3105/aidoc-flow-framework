#!/bin/bash
# =============================================================================
# GATE-09 Validation Script
# Validates Design/Test Gate requirements (L9-L11)
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
  echo "GATE-09 Validation (Design/Test)"
  echo "Layers: L9-L11 (SPEC, TSPEC, TASKS)"
  echo "=========================================="
  echo "File: $CHG_FILE"
  echo "Date: $(TZ=America/New_York date '+%Y-%m-%d %H:%M:%S %Z')"
  echo ""
}

usage() {
  echo "Usage: $0 <CHG_FILE> [--verbose]"
  echo ""
  echo "Validates CHG document against GATE-09 requirements."
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

check_spec_readiness() {
  echo "--- GATE-09-E001: SPEC Implementation Readiness ---"

  # Check if SPEC is mentioned
  if grep -qiE "SPEC-|technical specification" "$CHG_FILE" 2>/dev/null; then
    # Look for implementation readiness score
    local score
    score=$(grep -oE "(SPEC-Ready|Implementation.Ready|Readiness).*Score[^0-9]*[0-9]+" "$CHG_FILE" 2>/dev/null | grep -oE "[0-9]+" | head -1 || echo "")

    if [[ -n "$score" ]]; then
      if [[ $score -lt 90 ]]; then
        echo -e "${RED}GATE-09-E001: SPEC readiness score $score% (required: >= 90%)${NC}"
        echo "  → Improve SPEC completeness before proceeding"
        ((ERRORS++)) || true
      else
        echo -e "${GREEN}  ✓ SPEC readiness score: $score%${NC}"
      fi
    else
      echo -e "${YELLOW}  ℹ SPEC referenced - verify readiness score >= 90% in SPEC file${NC}"
      ((INFO++)) || true
    fi
  else
    echo -e "${GREEN}  ✓ N/A (no SPEC changes)${NC}"
  fi
}

check_tspec_coverage() {
  echo ""
  echo "--- GATE-09-E002: TSPEC Interface Coverage ---"

  # Check if TSPEC is mentioned
  if grep -qiE "TSPEC|test specification|UTEST|ITEST|STEST|FTEST" "$CHG_FILE" 2>/dev/null; then
    # Check for test type coverage
    local test_types=0
    for tt in UTEST ITEST STEST FTEST; do
      if grep -qE "$tt" "$CHG_FILE" 2>/dev/null; then
        ((test_types++)) || true
      fi
    done

    if [[ $test_types -gt 0 ]]; then
      echo -e "${GREEN}  ✓ TSPEC test types referenced: $test_types types${NC}"
    else
      echo -e "${YELLOW}  ℹ TSPEC referenced - verify interface coverage in TSPEC file${NC}"
      ((INFO++)) || true
    fi
  else
    echo -e "${GREEN}  ✓ N/A (no TSPEC changes)${NC}"
  fi
}

check_tasks_linkage() {
  echo ""
  echo "--- GATE-09-E003: TASKS Traceability ---"

  # Check if TASKS is mentioned
  if grep -qiE "TASKS-|task breakdown" "$CHG_FILE" 2>/dev/null; then
    # Check for @spec and @tspec tags
    local has_spec has_tspec
    has_spec=$(grep -c "@spec:" "$CHG_FILE" 2>/dev/null || echo 0)
    has_tspec=$(grep -c "@tspec:" "$CHG_FILE" 2>/dev/null || echo 0)

    if [[ $has_spec -eq 0 && $has_tspec -eq 0 ]]; then
      echo -e "${YELLOW}  ℹ TASKS referenced - verify @spec and @tspec tags in TASKS file${NC}"
      ((INFO++)) || true
    else
      echo -e "${GREEN}  ✓ TASKS traceability present (@spec: $has_spec, @tspec: $has_tspec)${NC}"
    fi
  else
    echo -e "${GREEN}  ✓ N/A (no TASKS changes)${NC}"
  fi
}

check_tspec_spec_alignment() {
  echo ""
  echo "--- GATE-09-E004: TSPEC-SPEC Alignment ---"

  # Check for both TSPEC and SPEC changes
  if grep -qiE "TSPEC" "$CHG_FILE" 2>/dev/null && grep -qiE "SPEC-" "$CHG_FILE" 2>/dev/null; then
    echo -e "${GREEN}  ✓ Both TSPEC and SPEC mentioned - verify alignment${NC}"
  elif grep -qiE "SPEC-" "$CHG_FILE" 2>/dev/null && ! grep -qiE "TSPEC" "$CHG_FILE" 2>/dev/null; then
    echo -e "${YELLOW}GATE-09-E004: SPEC change without TSPEC mention${NC}"
    echo "  → Verify TSPEC is aligned with SPEC changes (TDD compliance)"
    ((WARNINGS++)) || true
  else
    echo -e "${GREEN}  ✓ Alignment check N/A${NC}"
  fi
}

check_tdd_compliance() {
  echo ""
  echo "--- GATE-09-E005: TDD Compliance ---"

  # Check for evidence of TDD order (TSPEC before SPEC)
  if grep -qiE "SPEC" "$CHG_FILE" 2>/dev/null; then
    # Look for TDD indicators
    if grep -qiE "TDD|test.first|TSPEC.*before|update.*TSPEC.*then.*SPEC" "$CHG_FILE" 2>/dev/null; then
      echo -e "${GREEN}  ✓ TDD workflow indicated${NC}"
    else
      echo -e "${BLUE}  ℹ Reminder: Follow TDD order (TSPEC → SPEC → TASKS)${NC}"
      ((INFO++)) || true
    fi
  else
    echo -e "${GREEN}  ✓ N/A (no SPEC changes)${NC}"
  fi
}

check_tasks_dependencies() {
  echo ""
  echo "--- GATE-09-E006: TASKS Dependencies ---"

  # Check for dependency-related content
  if grep -qiE "TASKS|task" "$CHG_FILE" 2>/dev/null; then
    if grep -qiE "circular|cycle|depend" "$CHG_FILE" 2>/dev/null; then
      if grep -qiE "no.*circular|resolved.*cycle|valid.*depend" "$CHG_FILE" 2>/dev/null; then
        echo -e "${GREEN}  ✓ Dependencies addressed${NC}"
      else
        echo -e "${YELLOW}  ℹ Dependency mentioned - verify no circular dependencies${NC}"
        ((INFO++)) || true
      fi
    else
      echo -e "${GREEN}  ✓ No dependency issues detected${NC}"
    fi
  else
    echo -e "${GREEN}  ✓ N/A (no TASKS changes)${NC}"
  fi
}

check_performance_baseline() {
  echo ""
  echo "--- GATE-09-W001: Performance Baseline ---"

  # Check for algorithm/performance changes
  if grep -qiE "algorithm|performance|optimization|benchmark" "$CHG_FILE" 2>/dev/null; then
    if ! grep -qE "[0-9]+\s*(ms|s|ops|req/s|MB|GB)" "$CHG_FILE" 2>/dev/null; then
      echo -e "${YELLOW}GATE-09-W001: Algorithm/performance change without baseline metrics${NC}"
      echo "  → Document current performance baseline before changes"
      ((WARNINGS++)) || true
    else
      echo -e "${GREEN}  ✓ Performance metrics present${NC}"
    fi
  else
    echo -e "${GREEN}  ✓ N/A (not performance-related)${NC}"
  fi
}

check_edge_case_coverage() {
  echo ""
  echo "--- GATE-09-W002: Edge Case Coverage ---"

  # Check for TSPEC without edge case mention
  if grep -qiE "TSPEC|test" "$CHG_FILE" 2>/dev/null; then
    if ! grep -qiE "edge.case|boundary|corner.case|negative.test|error.case" "$CHG_FILE" 2>/dev/null; then
      echo -e "${YELLOW}GATE-09-W002: TSPEC may lack edge case coverage${NC}"
      echo "  → Consider adding boundary condition tests"
      ((WARNINGS++)) || true
    else
      echo -e "${GREEN}  ✓ Edge case coverage mentioned${NC}"
    fi
  else
    echo -e "${GREEN}  ✓ N/A (no test changes)${NC}"
  fi
}

check_complexity() {
  echo ""
  echo "--- GATE-09-W003: Implementation Complexity ---"

  # Check for complexity score
  local complexity
  complexity=$(grep -oE "(complexity|impl.complexity)[^0-9]*[0-9]" "$CHG_FILE" 2>/dev/null | grep -oE "[0-9]" | head -1 || echo "")

  if [[ -n "$complexity" && $complexity -gt 4 ]]; then
    echo -e "${YELLOW}GATE-09-W003: High complexity score: $complexity${NC}"
    echo "  → Consider decomposing into smaller SPECs"
    ((WARNINGS++)) || true
  else
    echo -e "${GREEN}  ✓ Complexity acceptable${NC}"
  fi
}

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------

print_summary() {
  echo ""
  echo "=========================================="
  echo "GATE-09 Validation Summary"
  echo "=========================================="
  echo -e "Errors:   ${RED}$ERRORS${NC}"
  echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
  echo -e "Info:     ${BLUE}$INFO${NC}"
  echo ""

  if [[ $ERRORS -gt 0 ]]; then
    echo -e "${RED}GATE-09 FAILED: $ERRORS error(s) must be fixed${NC}"
    exit 2
  elif [[ $WARNINGS -gt 0 ]]; then
    echo -e "${YELLOW}GATE-09 PASSED with $WARNINGS warning(s)${NC}"
    exit 1
  else
    echo -e "${GREEN}GATE-09 PASSED: All validation checks passed${NC}"
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
  check_spec_readiness
  check_tspec_coverage
  check_tasks_linkage
  check_tspec_spec_alignment
  check_tdd_compliance
  check_tasks_dependencies
  check_performance_baseline
  check_edge_case_coverage
  check_complexity

  print_summary
}

# Run main function
main "$@"
