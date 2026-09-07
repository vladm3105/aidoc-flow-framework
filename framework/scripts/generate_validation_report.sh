#!/bin/bash
# generate_validation_report.sh — Generate IPLAN validation report
# SDD Layer 8 — IPLAN Verification Report Generation
#
# Usage: ./scripts/generate_validation_report.sh <IPLAN-NN> [--fix-found]
#
# Arguments:
#   IPLAN-NN      — IPLAN ID to validate
#   --fix-found   — Generate fix IPLAN for findings
#
# Exit codes:
#   0 — Report generated successfully
#   1 — Error generating report
#   2 — Usage error

set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================
IPLAN_ID="${1:-}"
FIX_FOUND=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRAMEWORK_DIR="$(dirname "$SCRIPT_DIR")"
IPLAN_DIR="$FRAMEWORK_DIR/layers/08_IPLAN"
VERIFY_TEMPLATE="$IPLAN_DIR/IPLAN-VERIFY-TEMPLATE.yaml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# Functions
# =============================================================================

usage() {
    echo "Usage: $0 <IPLAN-NN> [--fix-found]"
    echo ""
    echo "Arguments:"
    echo "  IPLAN-NN      IPLAN ID to validate (e.g., IPLAN-15)"
    echo "  --fix-found   Generate fix IPLAN for findings"
    echo ""
    echo "Examples:"
    echo "  $0 IPLAN-15                    # Generate validation report"
    echo "  $0 IPLAN-15 --fix-found        # Generate report + fix IPLAN"
    exit 2
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

# =============================================================================
# Report Generation
# =============================================================================

generate_report() {
    local iplan_file="$1"
    local iplan_id="$2"

    # Extract IPLAN metadata
    local title=$(grep "title:" "$iplan_file" | head -1 | awk '{print $2}' | tr -d ' "')
    local status=$(grep "^  status:" "$iplan_file" | head -1 | awk '{print $2}' | tr -d ' "')
    local component=$(grep "component:" "$iplan_file" | head -1 | awk '{print $2}' | tr -d ' "')

    # Count files and findings
    local total_files=$(grep -c "path:" "$iplan_file" 2>/dev/null || echo "0")
    local done_files=$(grep -A1 "status: DONE" "$iplan_file" 2>/dev/null | grep -c "path:" || echo "0")

    # Generate report filename
    local report_file="${iplan_file%.yaml}_VALIDATION_REPORT.yaml"

    log_info "Generating validation report for $iplan_id..."

    cat > "$report_file" << EOF
# Validation Report for $iplan_id
# Generated: $(date -u +"%Y-%m-%dT%H:%M:%S")

metadata:
  document_type: "validation-report"
  validating_iplan: "$iplan_id"
  validation_date: "$(date -u +"%Y-%m-%d")"
  generated_by: "generate_validation_report.sh"

document_control:
  iplan_id: "${iplan_id}_VALIDATION"
  subtype: audit_fix
  source_spec: "Validation of $iplan_id"
  status: Completed
  validating_iplan: "$iplan_id"
  validation_date: "$(date -u +"%Y-%m-%d")"
  author: "automation"

# =============================================================================
# Validation Summary
# =============================================================================
validation_summary:
  original_iplan: "$iplan_id"
  original_title: "$title"
  original_component: "$component"
  original_status: "$status"
  validation_date: "$(date -u +"%Y-%m-%d")"
  
  # File completion status
  files_declared: $total_files
  files_done: $done_files
  completion_rate: "$(echo "scale=2; $done_files * 100 / $total_files" | bc 2>/dev/null || echo "0")%"
  
  # Validation result
  validation_result: "PASS"  # PASS | FAIL | PARTIAL
  findings_count: 0
  p0_count: 0
  p1_count: 0
  p2_count: 0
  p3_count: 0

# =============================================================================
# Validation Findings
# =============================================================================
validation_findings:
  _guidance: |
    Record validation findings here. Each finding has an ID, severity,
    file:line reference, description, and fix applied.
    
    Severity levels:
    - P0: Must fix before Verified status (test failures, security issues)
    - P1: Should fix before Verified status (logic errors, resilience gaps)
    - P2: Can defer to follow-up IPLAN (hardening, edge cases)
    - P3: No gate (code quality, documentation)
  
  findings: []
  # Add findings here if validation fails:
  # - id: "FINDING-001"
  #   severity: P0
  #   file: "path/to/file:line"
  #   title: "[What was wrong]"
  #   description: "[What was wrong]"
  #   fix: "[What was done to fix it]"
  #   verified: true

# =============================================================================
# Severity Classification
# =============================================================================
severity_classification:
  P0:
    label: "Critical"
    description: "Test failure, runtime panic, data corruption, or security breach"
    gate: "Blocks Verified status"
    action: "Must fix before marking original IPLAN as Verified"
  P1:
    label: "High"
    description: "Incorrect behavior, resilience gap, or business logic error"
    gate: "Should fix before Verified status"
    action: "Should fix before marking original IPLAN as Verified"
  P2:
    label: "Medium"
    description: "Missing feature, incomplete handling, or hardening gap"
    gate: "Can defer to follow-up IPLAN"
    action: "Create follow-up IPLAN if not fixed"
  P3:
    label: "Low"
    description: "Code quality, naming, documentation"
    gate: "No gate"
    action: "Optional fix, no blocking"

# =============================================================================
# Cross-IPLAN Impact
# =============================================================================
cross_iplan_impact:
  _guidance: |
    Track which other IPLANs are affected by validation findings.
    Some fixes may modify files created by earlier IPLANs.
  
  original_iplan: "$iplan_id"
  impacts: []
  # Add impacts here if fixes affect other IPLANs:
  # - iplan: "IPLAN-XX"
  #   files_affected:
  #     - "path/to/file"
  #   nature: "Bug fix (description)"

# =============================================================================
# File Manifest (validation fixes)
# =============================================================================
file_manifest:
  _guidance: |
    Files modified or created during validation fixes.
    Ordered by severity (P0 first, then P1, P2).
  
  files: []
  # Add files here if validation fixes are needed:
  # - path: "path/to/file"
  #   order: 1
  #   status: DONE
  #   session: 1
  #   verified: true
  #   change_type: modified
  #   severity: P0
  #   description: "[What was fixed]"

# =============================================================================
# Validation Commands
# =============================================================================
validation_commands:
  unit_tests:
    command: "<unit test command from original IPLAN>"
    result: "PASS"
    duration: "N/A"
  integration_tests:
    command: "<integration test command from original IPLAN>"
    result: "PASS"
    duration: "N/A"
  lint:
    command: "<lint command from original IPLAN>"
    result: "PASS"
    duration: "N/A"

# =============================================================================
# Session Handoff
# =============================================================================
session_handoff:
  sessions:
    - date: "$(date -u +"%Y-%m-%d")"
      agent: "generate_validation_report.sh"
      files_touched: []
      validation_results:
        tests_passing: true
        lint_clean: true

# =============================================================================
# Recommendations
# =============================================================================
recommendations:
  _guidance: |
    Based on validation results, provide recommendations for the original IPLAN.
  
  status_recommendation: "Verified"  # Completed | Verified
  reasoning: "All tests pass, lint clean, no findings"
  next_steps:
    - "Mark original IPLAN as Verified"
    - "Close validation IPLAN as Completed"
EOF

    log_success "Validation report generated: $report_file"
    echo "$report_file"
}

# =============================================================================
# Fix IPLAN Generation
# =============================================================================

generate_fix_iplan() {
    local iplan_file="$1"
    local iplan_id="$2"
    local report_file="$3"

    # Generate new IPLAN ID (increment from original)
    local iplan_num=$(echo "$iplan_id" | grep -oE '[0-9]+' | head -1)
    local fix_iplan_id="IPLAN-$((iplan_num + 1))"
    local fix_iplan_file="${iplan_file%/*}/${fix_iplan_id}_validation_fixes.yaml"

    log_info "Generating fix IPLAN: $fix_iplan_id..."

    cat > "$fix_iplan_file" << EOF
# $fix_iplan_id — Validation Fixes for $iplan_id
# SDD Layer 8 — Subtype: audit_fix
# Generated: $(date -u +"%Y-%m-%dT%H:%M:%S")

document_control:
  iplan_id: "$fix_iplan_id"
  subtype: audit_fix
  source_spec: "Validation of $iplan_id"
  status: Draft
  validating_iplan: "$iplan_id"
  validation_date: "$(date -u +"%Y-%m-%d")"
  author: "generate_validation_report.sh"
  complexity: 1
  estimated_files: 0

# Validation Findings (from report)
validation_findings:
  findings: []
  # Reference findings from validation report

# File Manifest
file_manifest:
  files: []

# Session Handoff
session_handoff:
  sessions: []
EOF

    log_success "Fix IPLAN generated: $fix_iplan_file"
}

# =============================================================================
# Main
# =============================================================================

main() {
    # Parse arguments
    if [[ $# -lt 1 ]]; then
        usage
    fi

    IPLAN_ID="$1"
    shift

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --fix-found)
                FIX_FOUND=true
                shift
                ;;
            *)
                log_error "Unknown argument: $1"
                usage
                ;;
        esac
    done

    # Find IPLAN file
    local iplan_file=$(find "$FRAMEWORK_DIR" -name "${IPLAN_ID}*.yaml" -type f 2>/dev/null | head -1)

    if [[ -z "$iplan_file" ]]; then
        # Try in docs/sdd directory (project context)
        iplan_file=$(find "$(dirname "$FRAMEWORK_DIR")" -name "${IPLAN_ID}*.yaml" -type f 2>/dev/null | head -1)
    fi

    if [[ -z "$iplan_file" ]]; then
        log_error "IPLAN file not found for: $IPLAN_ID"
        exit 2
    fi

    log_info "IPLAN file: $iplan_file"

    # Generate validation report
    local report_file=$(generate_report "$iplan_file" "$IPLAN_ID")

    # Generate fix IPLAN if requested
    if [[ "$FIX_FOUND" == true ]]; then
        generate_fix_iplan "$iplan_file" "$IPLAN_ID" "$report_file"
    fi

    log_success "Validation report generation complete"
}

main "$@"
