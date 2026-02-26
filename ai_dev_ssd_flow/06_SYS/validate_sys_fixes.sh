#!/bin/bash
# =============================================================================
# SYS-MVP-TEMPLATE Fix Validation Script
# Version: 2.0
# Purpose: Validate all fixes from SYS-MVP-TEMPLATE_FIX_PLAN.md v2.0
# =============================================================================

# Don't exit on error - we handle errors via pass/fail functions

SYS_DIR="/opt/data/docs_flow_framework/ai_dev_ssd_flow/06_SYS"
SKILLS_DIR="/opt/data/docs_flow_framework/.claude/skills"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASS_COUNT++))
}

fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAIL_COUNT++))
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    ((WARN_COUNT++))
}

echo "=============================================="
echo "SYS-MVP-TEMPLATE Fix Validation"
echo "=============================================="
echo ""

# -----------------------------------------------------------------------------
# Phase 1: MD Template Checks
# -----------------------------------------------------------------------------
echo "--- Phase 1: MD Template ---"

# Check schema_version
if grep -q 'schema_version: "2.1"' "$SYS_DIR/SYS-MVP-TEMPLATE.md"; then
    pass "MD template schema_version is 2.1"
else
    fail "MD template schema_version not updated to 2.1"
fi

# Check total_sections
if grep -q 'total_sections: 15' "$SYS_DIR/SYS-MVP-TEMPLATE.md"; then
    pass "MD template has total_sections: 15"
else
    fail "MD template missing total_sections: 15"
fi

# Check section count
SECTION_COUNT=$(grep -c "^## [0-9]" "$SYS_DIR/SYS-MVP-TEMPLATE.md" || echo "0")
if [ "$SECTION_COUNT" -eq 15 ]; then
    pass "MD template has 15 sections"
else
    fail "MD template has $SECTION_COUNT sections (expected 15)"
fi

# Check template footer
if grep -q "Template Version.* 2.1 (MVP - 15 sections)" "$SYS_DIR/SYS-MVP-TEMPLATE.md"; then
    pass "MD template has version footer"
else
    fail "MD template missing version footer"
fi

# -----------------------------------------------------------------------------
# Phase 3: Supporting Documents
# -----------------------------------------------------------------------------
echo ""
echo "--- Phase 3: Supporting Documents ---"

# Check Quality Gate thresholds
if grep -q "Tokens | 15,000 | 20,000" "$SYS_DIR/SYS_MVP_QUALITY_GATE_VALIDATION.md"; then
    pass "Quality Gate has correct token thresholds (15K/20K)"
else
    fail "Quality Gate token thresholds not updated"
fi

# Check README section count
if grep -q "15 sections" "$SYS_DIR/README.md"; then
    pass "README mentions 15 sections"
else
    fail "README doesn't mention 15 sections"
fi

# -----------------------------------------------------------------------------
# Phase 4: YAML Template
# -----------------------------------------------------------------------------
echo ""
echo "--- Phase 4: YAML Template ---"

# Check YAML syntax
if python3 -c "import yaml; yaml.safe_load(open('$SYS_DIR/SYS-MVP-TEMPLATE.yaml').read())" 2>/dev/null; then
    pass "YAML template syntax valid"
else
    fail "YAML template syntax invalid"
fi

# Check YAML schema_version
if grep -q 'schema_version: "2.1"' "$SYS_DIR/SYS-MVP-TEMPLATE.yaml"; then
    pass "YAML template schema_version is 2.1"
else
    fail "YAML template schema_version not updated"
fi

# Check YAML total_sections
if grep -q 'total_sections: 15' "$SYS_DIR/SYS-MVP-TEMPLATE.yaml"; then
    pass "YAML template has total_sections: 15"
else
    fail "YAML template missing total_sections"
fi

# Check YAML section count
YAML_SECTIONS=$(grep -c "^\s*- number:" "$SYS_DIR/SYS-MVP-TEMPLATE.yaml" || echo "0")
if [ "$YAML_SECTIONS" -eq 15 ]; then
    pass "YAML template has 15 sections array entries"
else
    fail "YAML template has $YAML_SECTIONS sections (expected 15)"
fi

# Check for legacy SYS-FN format (should NOT exist)
if grep -q "SYS-FN-" "$SYS_DIR/SYS-MVP-TEMPLATE.yaml"; then
    fail "YAML template still contains legacy SYS-FN-NNN format"
else
    pass "YAML template uses unified SYS.NN.TT.SS format"
fi

# -----------------------------------------------------------------------------
# Phase 5: Skills
# -----------------------------------------------------------------------------
echo ""
echo "--- Phase 5: Skills ---"

# Check doc-sys_quickref path
if grep -q "docs/06_SYS/SYS-NN" "$SKILLS_DIR/doc-sys_quickref.md"; then
    pass "doc-sys_quickref has correct path (docs/06_SYS/SYS-NN)"
else
    fail "doc-sys_quickref has wrong path"
fi

# Check doc-sys-validator format
if grep -q "SYS.NN.01.SS" "$SKILLS_DIR/doc-sys-validator/SKILL.md"; then
    pass "doc-sys-validator uses SYS.NN.01.SS format"
else
    fail "doc-sys-validator still uses FR-NNN format"
fi

# Check for legacy FR-NNN format in requirement pattern (should NOT exist)
# Note: FR-NNN may appear in warning descriptions (SYS-W001), which is OK
if grep -q "Pattern: \`FR-NNN\`" "$SKILLS_DIR/doc-sys-validator/SKILL.md"; then
    fail "doc-sys-validator still uses FR-NNN as required pattern"
else
    pass "doc-sys-validator no longer uses FR-NNN as required pattern"
fi

# Check doc-sys skill mentions 15 sections
if grep -q "15 Sections" "$SKILLS_DIR/doc-sys/SKILL.md"; then
    pass "doc-sys/SKILL.md mentions 15 sections"
else
    fail "doc-sys/SKILL.md doesn't mention 15 sections"
fi

# -----------------------------------------------------------------------------
# Phase 6: Sync Verification
# -----------------------------------------------------------------------------
echo ""
echo "--- Phase 6: Sync Verification ---"

# Compare section counts
MD_SECTIONS=$(grep -c "^## [0-9]" "$SYS_DIR/SYS-MVP-TEMPLATE.md" || echo "0")
YAML_SECTIONS=$(grep -c "^\s*- number:" "$SYS_DIR/SYS-MVP-TEMPLATE.yaml" || echo "0")

if [ "$MD_SECTIONS" -eq "$YAML_SECTIONS" ]; then
    pass "MD and YAML section counts match ($MD_SECTIONS)"
else
    fail "MD ($MD_SECTIONS) and YAML ($YAML_SECTIONS) section counts differ"
fi

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo ""
echo "=============================================="
echo "Validation Summary"
echo "=============================================="
echo -e "Passed: ${GREEN}$PASS_COUNT${NC}"
echo -e "Failed: ${RED}$FAIL_COUNT${NC}"
echo -e "Warnings: ${YELLOW}$WARN_COUNT${NC}"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}All validations passed!${NC}"
    exit 0
else
    echo -e "${RED}$FAIL_COUNT validation(s) failed. Review and fix before proceeding.${NC}"
    exit 1
fi
