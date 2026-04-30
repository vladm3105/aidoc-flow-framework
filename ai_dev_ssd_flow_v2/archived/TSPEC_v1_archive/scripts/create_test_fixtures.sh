#!/bin/bash
# =============================================================================
# Create TSPEC Test Fixtures
# Creates comprehensive test data for validation
# =============================================================================

set -e

FIXTURES_DIR="/opt/data/docs_flow_framework/ucx_flow_v3/10_TSPEC/scripts/tests/fixtures"

echo "========================================="
echo "Creating TSPEC Test Fixtures"
echo "========================================="

# Create directory structure
mkdir -p "$FIXTURES_DIR"/{valid,invalid,edge_cases}/{UTEST,ITEST,STEST,FTEST,PTEST,SECTEST}

# Function to create fixture file
create_fixture() {
    local type="$1"
    local id="$2"
    local category="$3"  # valid, invalid, edge_cases
    local score="$4"
    local score_format="$5"  # percent, fraction, bracket

    local dir="$FIXTURES_DIR/$category/$type/${type}-${id}_test"
    local file="$dir/${type}-${id}_test.md"

    mkdir -p "$dir"

    # Format score based on requested format
    local score_display=""
    case $score_format in
        percent)
            score_display="${score}%"
            ;;
        fraction)
            score_display="${score}/100"
            ;;
        bracket)
            score_display="[${score}]"
            ;;
    esac

    cat > "$file" << EOF
---
document_id: "${type}-${id}"
version: "1.0.0"
type: "$type"
created: "$(date -I)"
status: "test_fixture"
---

# ${type}-${id}: Test Fixture

## 1. Document Control

| Field | Value |
|-------|-------|
| Document ID | ${type}-${id} |
| Version | 1.0.0 |
| Type | $type |
| Status | Test Fixture |

## 2. Test Scope

Test fixture for validation testing.

## 3. Test Case Index

| ID | Name | Priority |
|----|------|----------|
| ${type}.${id}.01.01 | Test Case 1 | P1 |

## 4. Test Case Details

### ${type}.${id}.01.01: Test Case 1

**Description**: Sample test case for fixture

**Test Steps**:
1. Execute test
2. Verify result

**Expected Result**: Pass

## 5. Coverage Matrix

| Upstream ID | Covered |
|-------------|---------|
| REQ-01 | ✓ |

## 6. Traceability

**Upstream References**:
- @brd: BRD-01
- @prd: PRD-01
- @ears: EARS-01
- @bdd: BDD-01
- @adr: ADR-01
- @sys: SYS-01
- @req: REQ-01
- @spec: SPEC-01

## 7. TASKS-Ready Assessment

**TASKS-Ready Score**: $score_display

**Completeness Factors**:
- Test coverage: ${score}%
- Documentation: Complete
- Traceability: Complete
EOF

    echo "  Created: $file (score: $score_display)"
}

# Create VALID fixtures (all test types, different score formats)
echo "--- Creating Valid Fixtures ---"
create_fixture "UTEST" "01" "valid" "95" "percent"
create_fixture "ITEST" "01" "valid" "92" "fraction"
create_fixture "STEST" "01" "valid" "100" "bracket"
create_fixture "FTEST" "01" "valid" "91" "percent"
create_fixture "PTEST" "01" "valid" "88" "percent"
create_fixture "SECTEST" "01" "valid" "93" "percent"
echo ""

# Create INVALID fixtures (below thresholds)
echo "--- Creating Invalid Fixtures ---"
create_fixture "UTEST" "02" "invalid" "75" "percent"
create_fixture "ITEST" "02" "invalid" "70" "percent"
create_fixture "STEST" "02" "invalid" "85" "percent"  # STEST requires 100%
create_fixture "FTEST" "02" "invalid" "80" "percent"
create_fixture "PTEST" "02" "invalid" "60" "percent"
create_fixture "SECTEST" "02" "invalid" "75" "percent"
echo ""

# Create EDGE CASE fixtures
echo "--- Creating Edge Case Fixtures ---"

# Reserved IDs (TYPE-00_*)
for TYPE in UTEST ITEST STEST FTEST PTEST SECTEST; do
    mkdir -p "$FIXTURES_DIR/edge_cases/$TYPE/${TYPE}-00_index"
    cat > "$FIXTURES_DIR/edge_cases/$TYPE/${TYPE}-00_index/${TYPE}-00_index.md" << EOF
# ${TYPE}-00: Index (Reserved ID)
This file should be excluded from validation.
EOF
    echo "  Created: ${TYPE}-00_index (reserved ID)"
done
echo ""

# Report files
for TYPE in UTEST ITEST STEST FTEST PTEST SECTEST; do
    mkdir -p "$FIXTURES_DIR/edge_cases/$TYPE/${TYPE}-03_test"

    # Audit report
    cat > "$FIXTURES_DIR/edge_cases/$TYPE/${TYPE}-03_test.A_audit_report_v001.md" << EOF
# ${TYPE}-03: Audit Report
This file should be excluded from validation.
EOF

    # Review report
    cat > "$FIXTURES_DIR/edge_cases/$TYPE/${TYPE}-03_test.R_review_report_v001.md" << EOF
# ${TYPE}-03: Review Report
This file should be excluded from validation.
EOF

    # Fix report
    cat > "$FIXTURES_DIR/edge_cases/$TYPE/${TYPE}-03_test.F_fix_report_v001.md" << EOF
# ${TYPE}-03: Fix Report
This file should be excluded from validation.
EOF

    # Validation report
    cat > "$FIXTURES_DIR/edge_cases/$TYPE/${TYPE}-03_test.V_validation_report_v001.md" << EOF
# ${TYPE}-03: Validation Report
This file should be excluded from validation.
EOF

    echo "  Created: ${TYPE}-03 report files (4 report types)"
done
echo ""

echo "========================================="
echo "Test Fixtures Created Successfully"
echo "========================================="
echo "Location: $FIXTURES_DIR"
echo ""
echo "Fixture Counts:"
find "$FIXTURES_DIR" -type f -name "*.md" | wc -l | xargs echo "  Total files:"
find "$FIXTURES_DIR/valid" -type f -name "*.md" | wc -l | xargs echo "  Valid fixtures:"
find "$FIXTURES_DIR/invalid" -type f -name "*.md" | wc -l | xargs echo "  Invalid fixtures:"
find "$FIXTURES_DIR/edge_cases" -type f -name "*.md" | wc -l | xargs echo "  Edge case fixtures:"
