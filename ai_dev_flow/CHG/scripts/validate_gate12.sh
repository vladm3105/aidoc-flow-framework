#!/bin/bash
# =============================================================================
# GATE-12 Validation Script
# Validates Implementation Gate requirements (L12-L14)
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
  echo "GATE-12 Validation (Implementation)"
  echo "Layers: L12-L14 (Code, Tests, Validation)"
  echo "=========================================="
  echo "File: $CHG_FILE"
  echo "Date: $(TZ=America/New_York date '+%Y-%m-%d %H:%M:%S %Z')"
  echo ""
}

usage() {
  echo "Usage: $0 <CHG_FILE> [--verbose]"
  echo ""
  echo "Validates CHG document against GATE-12 requirements."
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

check_root_cause_analysis() {
  echo "--- GATE-12-E001: Root Cause Analysis ---"

  # Check for RCA content
  local has_rca=0

  if grep -qiE "root.cause|5.why|five.why|fishbone|rca" "$CHG_FILE" 2>/dev/null; then
    has_rca=1
  fi

  # Also check for "Why?" pattern
  local why_count
  why_count=$(grep -cE "^[0-9]+\.\s*Why\?" "$CHG_FILE" 2>/dev/null || echo 0)
  if [[ $why_count -ge 3 ]]; then
    has_rca=1
  fi

  # Check if this is a downstream/defect change that requires RCA
  if grep -qiE "change_source:.*downstream|defect|bug|fix|issue" "$CHG_FILE" 2>/dev/null; then
    if [[ $has_rca -eq 0 ]]; then
      echo -e "${RED}GATE-12-E001: Downstream change missing root cause analysis${NC}"
      echo "  → Add 'Root Cause Analysis' section with 5-Whys"
      ((ERRORS++)) || true
    else
      echo -e "${GREEN}  ✓ Root cause analysis present${NC}"
    fi
  else
    echo -e "${GREEN}  ✓ RCA not required (not downstream change)${NC}"
  fi
}

check_correct_layer_fix() {
  echo ""
  echo "--- GATE-12-E002: Fix at Correct Layer ---"

  # Check for layer justification
  if grep -qiE "root.cause.layer|fix.layer|correct.layer|layer.determination" "$CHG_FILE" 2>/dev/null; then
    echo -e "${GREEN}  ✓ Layer justification present${NC}"
  elif grep -qiE "change_source:.*downstream" "$CHG_FILE" 2>/dev/null; then
    echo -e "${YELLOW}  ℹ Verify fix is at correct layer (not symptom masking)${NC}"
    echo "  → Document: Why is L12-L14 the correct layer to fix?"
    ((INFO++)) || true
  else
    echo -e "${GREEN}  ✓ Layer check N/A (not defect fix)${NC}"
  fi
}

check_regression_tests() {
  echo ""
  echo "--- GATE-12-E003: Regression Tests ---"

  # Check for test-related content
  if grep -qiE "regression.test|test.added|test.included|test.cover" "$CHG_FILE" 2>/dev/null; then
    echo -e "${GREEN}  ✓ Regression tests mentioned${NC}"
  elif grep -qiE "code|implementation|fix" "$CHG_FILE" 2>/dev/null; then
    echo -e "${YELLOW}GATE-12-E003: Code change should include regression tests${NC}"
    echo "  → Document tests that cover the fix"
    ((WARNINGS++)) || true
  else
    echo -e "${GREEN}  ✓ N/A (no code changes)${NC}"
  fi
}

check_code_review() {
  echo ""
  echo "--- GATE-12-E004: Code Review ---"

  # Check for L2/L3 change
  if grep -qE "change_level:.*L[23]|Change Level.*L[23]" "$CHG_FILE" 2>/dev/null; then
    # Check for review mention
    if grep -qiE "code.review|review.approved|reviewed.by|PR.approved" "$CHG_FILE" 2>/dev/null; then
      echo -e "${GREEN}  ✓ Code review documented${NC}"
    else
      echo -e "${RED}GATE-12-E004: L2/L3 change requires code review${NC}"
      echo "  → Document code review approval"
      ((ERRORS++)) || true
    fi
  else
    echo -e "${GREEN}  ✓ Code review not required (L1 change)${NC}"
  fi
}

check_build_status() {
  echo ""
  echo "--- GATE-12-E005: Build Status ---"

  # Check for build/CI mention
  if grep -qiE "build.pass|CI.pass|pipeline.green|build.*success" "$CHG_FILE" 2>/dev/null; then
    echo -e "${GREEN}  ✓ Build status documented${NC}"
  else
    echo -e "${BLUE}  ℹ Reminder: Verify build passes before merge${NC}"
    ((INFO++)) || true
  fi
}

check_coverage() {
  echo ""
  echo "--- GATE-12-E006: Test Coverage ---"

  # Check for coverage mention
  if grep -qiE "coverage|test.*percent|coverage.*%" "$CHG_FILE" 2>/dev/null; then
    # Check for coverage numbers
    local coverage
    coverage=$(grep -oE "[0-9]+%" "$CHG_FILE" 2>/dev/null | head -1 || echo "")
    if [[ -n "$coverage" ]]; then
      echo -e "${GREEN}  ✓ Coverage documented: $coverage${NC}"
    else
      echo -e "${GREEN}  ✓ Coverage mentioned${NC}"
    fi
  else
    echo -e "${BLUE}  ℹ Reminder: Verify coverage is maintained or improved${NC}"
    ((INFO++)) || true
  fi
}

check_tspec_update_warning() {
  echo ""
  echo "--- GATE-12-W001: TSPEC Update ---"

  # Check if code change without TSPEC mention
  if grep -qiE "code|implementation|fix" "$CHG_FILE" 2>/dev/null; then
    if ! grep -qiE "TSPEC|test.spec" "$CHG_FILE" 2>/dev/null; then
      echo -e "${YELLOW}GATE-12-W001: Code change without TSPEC mention${NC}"
      echo "  → Consider updating TSPEC for TDD compliance"
      ((WARNINGS++)) || true
    else
      echo -e "${GREEN}  ✓ TSPEC referenced${NC}"
    fi
  else
    echo -e "${GREEN}  ✓ N/A (no code changes)${NC}"
  fi
}

check_change_level_appropriate() {
  echo ""
  echo "--- GATE-12-W002: Change Level Appropriateness ---"

  # Check for large changes marked as L1
  if grep -qE "change_level:.*L1|Change Level.*L1|L1.*Patch" "$CHG_FILE" 2>/dev/null; then
    # Count files or lines mentioned
    local file_count
    file_count=$(grep -ciE "file|\.py|\.ts|\.js|\.go|\.java" "$CHG_FILE" 2>/dev/null || echo 0)

    if [[ $file_count -gt 5 ]]; then
      echo -e "${YELLOW}GATE-12-W002: Large change ($file_count files) classified as L1${NC}"
      echo "  → Consider L2 classification for multi-file changes"
      ((WARNINGS++)) || true
    else
      echo -e "${GREEN}  ✓ Change level appears appropriate${NC}"
    fi
  else
    echo -e "${GREEN}  ✓ Not L1 change${NC}"
  fi
}

check_performance_benchmark() {
  echo ""
  echo "--- GATE-12-W003: Performance Benchmark ---"

  # Check for performance-critical code
  if grep -qiE "performance|algorithm|optimization|critical.path" "$CHG_FILE" 2>/dev/null; then
    if ! grep -qE "[0-9]+\s*(ms|s|ops|req/s)" "$CHG_FILE" 2>/dev/null; then
      echo -e "${YELLOW}GATE-12-W003: Performance-critical code without benchmark${NC}"
      echo "  → Add performance test to validate change"
      ((WARNINGS++)) || true
    else
      echo -e "${GREEN}  ✓ Performance metrics present${NC}"
    fi
  else
    echo -e "${GREEN}  ✓ N/A (not performance-related)${NC}"
  fi
}

check_security_review() {
  echo ""
  echo "--- GATE-12-W004: Security Review ---"

  # Check for security-sensitive code
  if grep -qiE "auth|password|token|secret|encrypt|credential|security" "$CHG_FILE" 2>/dev/null; then
    if ! grep -qiE "security.review|security.approved" "$CHG_FILE" 2>/dev/null; then
      echo -e "${YELLOW}GATE-12-W004: Security-sensitive code without review${NC}"
      echo "  → Request security review for auth/crypto changes"
      ((WARNINGS++)) || true
    else
      echo -e "${GREEN}  ✓ Security review mentioned${NC}"
    fi
  else
    echo -e "${GREEN}  ✓ N/A (not security-sensitive)${NC}"
  fi
}

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------

print_summary() {
  echo ""
  echo "=========================================="
  echo "GATE-12 Validation Summary"
  echo "=========================================="
  echo -e "Errors:   ${RED}$ERRORS${NC}"
  echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
  echo -e "Info:     ${BLUE}$INFO${NC}"
  echo ""

  if [[ $ERRORS -gt 0 ]]; then
    echo -e "${RED}GATE-12 FAILED: $ERRORS error(s) must be fixed${NC}"
    exit 2
  elif [[ $WARNINGS -gt 0 ]]; then
    echo -e "${YELLOW}GATE-12 PASSED with $WARNINGS warning(s)${NC}"
    exit 1
  else
    echo -e "${GREEN}GATE-12 PASSED: All validation checks passed${NC}"
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
  check_root_cause_analysis
  check_correct_layer_fix
  check_regression_tests
  check_code_review
  check_build_status
  check_coverage
  check_tspec_update_warning
  check_change_level_appropriate
  check_performance_benchmark
  check_security_review

  print_summary
}

# Run main function
main "$@"
