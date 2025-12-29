#!/bin/bash
# IMPL (Implementation Plan) Template Validator v1.0
# Validates IMPL documents against:
# - IMPL-TEMPLATE.md (authoritative template)
# - AI Dev Flow SDD framework standards
# - Layer 8 artifact requirements
# - Project management focus (WHO/WHAT/WHEN, not HOW)
# Usage: ./scripts/validate_impl.sh <IMPL_FILE>

set -e

IMPL_FILE=$1
ERRORS=0
WARNINGS=0
SCRIPT_VERSION="1.0.0"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

if [ -z "$IMPL_FILE" ]; then
  echo "Usage: $0 <IMPL_FILE>"
  echo "Example: $0 /opt/data/project/docs/IMPL/IMPL-01_risk_management_system.md"
  exit 1
fi

if [ ! -f "$IMPL_FILE" ]; then
  echo -e "${RED}ERROR: File not found: $IMPL_FILE${NC}"
  exit 1
fi

echo "========================================="
echo "IMPL Template Validator v${SCRIPT_VERSION}"
echo "========================================="
echo "File: $IMPL_FILE"
echo "Artifact Type: IMPL (Implementation Plan) - Layer 8"
echo ""

# ============================================
# CHECK 1: Filename Format
# ============================================
echo "CHECK 1: Filename Format"
echo "-----------------------------------------"

filename=$(basename "$IMPL_FILE")

# Pattern: IMPL-NNN_descriptive_slug.md
if [[ $filename =~ ^IMPL-[0-9]{2,}_[a-z0-9_]+\.md$ ]]; then
  echo -e "  ${GREEN}✅ Filename format valid: $filename${NC}"

  # Extract IMPL ID
  IMPL_ID=$(echo "$filename" | grep -oE "IMPL-[0-9]+" | head -1)
  echo "  IMPL ID: $IMPL_ID"
else
  echo -e "  ${RED}❌ ERROR: Invalid filename format: $filename${NC}"
  echo "           Expected: IMPL-NNN_descriptive_slug.md"
  echo "           Pattern: ^IMPL-[0-9]{2,}_[a-z0-9_]+\\.md$"
  ((ERRORS++))
fi

echo ""

# ============================================
# CHECK 2: Frontmatter Validation
# ============================================
echo "CHECK 2: Frontmatter Validation"
echo "-----------------------------------------"

# Check for YAML frontmatter (--- delimiters)
if grep -q "^---" "$IMPL_FILE"; then
  echo -e "  ${GREEN}✅ YAML frontmatter present${NC}"

  # Check for required fields
  if grep -q "artifact_type: IMPL" "$IMPL_FILE"; then
    echo -e "  ${GREEN}✅ artifact_type: IMPL${NC}"
  else
    echo -e "  ${RED}❌ ERROR: Missing or invalid artifact_type (must be IMPL)${NC}"
    ((ERRORS++))
  fi

  if grep -q "layer: 8" "$IMPL_FILE"; then
    echo -e "  ${GREEN}✅ layer: 8${NC}"
  else
    echo -e "  ${RED}❌ ERROR: Missing or invalid layer (must be 8)${NC}"
    ((ERRORS++))
  fi

  if grep -q "layer-8-artifact" "$IMPL_FILE"; then
    echo -e "  ${GREEN}✅ layer-8-artifact tag present${NC}"
  else
    echo -e "  ${YELLOW}⚠️  WARNING: Missing layer-8-artifact tag${NC}"
    ((WARNINGS++))
  fi

  # Check related_reqs
  if grep -q "related_reqs:" "$IMPL_FILE"; then
    echo -e "  ${GREEN}✅ related_reqs field present${NC}"
  else
    echo -e "  ${YELLOW}⚠️  WARNING: Missing related_reqs field${NC}"
    ((WARNINGS++))
  fi
else
  echo -e "  ${RED}❌ ERROR: Missing YAML frontmatter (--- delimiters)${NC}"
  ((ERRORS++))
fi

echo ""

# ============================================
# CHECK 3: Document Control Table
# ============================================
echo "CHECK 3: Document Control Table"
echo "-----------------------------------------"

required_dc_fields=(
  "IMPL ID"
  "Title"
  "Status"
  "Version"
  "Created"
  "Author"
  "Owner"
  "Last Updated"
  "Related REQs"
  "Deliverables"
)

for field in "${required_dc_fields[@]}"; do
  if grep -qi "$field" "$IMPL_FILE"; then
    echo -e "  ${GREEN}✅ Found: $field${NC}"
  else
    echo -e "  ${RED}❌ MISSING: $field${NC}"
    ((ERRORS++))
  fi
done

# Check status value
if grep -qE "Status.*\|.*(Draft|Planned|In Progress|On Hold|Completed|Cancelled)" "$IMPL_FILE"; then
  echo -e "  ${GREEN}✅ Status has valid enum value${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: Status should be Draft, Planned, In Progress, On Hold, Completed, or Cancelled${NC}"
  ((WARNINGS++))
fi

echo ""

# ============================================
# CHECK 4: Required Parts
# ============================================
echo "CHECK 4: Required Parts (4 PARTS structure)"
echo "-----------------------------------------"

required_parts=(
  "## PART 1"
  "## PART 2"
  "## PART 3"
  "## PART 4"
  "## Traceability"
)

for part in "${required_parts[@]}"; do
  if grep -q "$part" "$IMPL_FILE"; then
    echo -e "  ${GREEN}✅ Found: $part${NC}"
  else
    echo -e "  ${RED}❌ MISSING: $part${NC}"
    ((ERRORS++))
  fi
done

echo ""

# ============================================
# CHECK 5: PART 1 Validation
# ============================================
echo "CHECK 5: PART 1 - Project Context Validation"
echo "-----------------------------------------"

part1_subsections=(
  "### 1.1"
  "### 1.2"
  "### 1.3"
  "### 1.4"
)

for section in "${part1_subsections[@]}"; do
  if grep -q "$section" "$IMPL_FILE"; then
    echo -e "  ${GREEN}✅ Found: $section${NC}"
  else
    echo -e "  ${YELLOW}⚠️  WARNING: Missing Part 1 subsection: $section${NC}"
    ((WARNINGS++))
  fi
done

# Check for scope definitions
if grep -qi "in scope\|out of scope" "$IMPL_FILE"; then
  echo -e "  ${GREEN}✅ Scope definitions present${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: Define in-scope and out-of-scope items${NC}"
  ((WARNINGS++))
fi

echo ""

# ============================================
# CHECK 6: PART 2 - Phases Validation
# ============================================
echo "CHECK 6: PART 2 - Phased Implementation Validation"
echo "-----------------------------------------"

# Count phases
phase_count=$(grep -cE "^### Phase [0-9]+" "$IMPL_FILE" 2>/dev/null || echo "0")

if [ "$phase_count" -ge 1 ]; then
  echo -e "  ${GREEN}✅ Found $phase_count phase(s)${NC}"
else
  echo -e "  ${RED}❌ ERROR: No phases defined in PART 2${NC}"
  ((ERRORS++))
fi

# Check for deliverables in phases
deliverable_count=$(grep -cE "(CTR-[0-9]+|SPEC-[0-9]+|TASKS-[0-9]+)" "$IMPL_FILE" 2>/dev/null || echo "0")
if [ "$deliverable_count" -gt 0 ]; then
  echo -e "  ${GREEN}✅ Found $deliverable_count deliverable reference(s)${NC}"
else
  echo -e "  ${RED}❌ ERROR: No deliverables (CTR/SPEC/TASKS) referenced${NC}"
  ((ERRORS++))
fi

# Check for phase ownership
if grep -qi "owner\|team\|responsible" "$IMPL_FILE"; then
  echo -e "  ${GREEN}✅ Phase ownership documented${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: Document phase owners/teams${NC}"
  ((WARNINGS++))
fi

# Check for timeline
if grep -qiE "timeline|sprint|week|date" "$IMPL_FILE"; then
  echo -e "  ${GREEN}✅ Timeline information present${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: Include timeline/sprint information${NC}"
  ((WARNINGS++))
fi

echo ""

# ============================================
# CHECK 7: Deliverables Validation
# ============================================
echo "CHECK 7: Deliverables Validation"
echo "-----------------------------------------"

# Check for deliverables checklist format
if grep -q "\[ \]" "$IMPL_FILE"; then
  checkbox_count=$(grep -c "\[ \]" "$IMPL_FILE" 2>/dev/null || echo "0")
  echo -e "  ${GREEN}✅ Found $checkbox_count deliverables checklist item(s)${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: No deliverables checklist found (use [ ] format)${NC}"
  ((WARNINGS++))
fi

# Check for CTR references
ctr_count=$(grep -cE "CTR-[0-9]+" "$IMPL_FILE" 2>/dev/null || echo "0")
spec_count=$(grep -cE "SPEC-[0-9]+" "$IMPL_FILE" 2>/dev/null || echo "0")
tasks_count=$(grep -cE "TASKS-[0-9]+" "$IMPL_FILE" 2>/dev/null || echo "0")

echo "  Deliverable references:"
echo "    CTR: $ctr_count"
echo "    SPEC: $spec_count"
echo "    TASKS: $tasks_count"

total_deliverables=$((ctr_count + spec_count + tasks_count))
if [ "$total_deliverables" -lt 1 ]; then
  echo -e "  ${RED}❌ ERROR: No deliverables referenced${NC}"
  ((ERRORS++))
fi

echo ""

# ============================================
# CHECK 8: PART 3 - Project Management Validation
# ============================================
echo "CHECK 8: PART 3 - Project Management Validation"
echo "-----------------------------------------"

# Check for resources section
if grep -qi "resources\|team\|allocation" "$IMPL_FILE"; then
  echo -e "  ${GREEN}✅ Resources section present${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: Document resource allocation${NC}"
  ((WARNINGS++))
fi

# Check for risk register
if grep -qE "R-[0-9]+" "$IMPL_FILE"; then
  risk_count=$(grep -cE "R-[0-9]+" "$IMPL_FILE" 2>/dev/null || echo "0")
  echo -e "  ${GREEN}✅ Found $risk_count risk(s) in risk register${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: No risk IDs found (use R-001 format)${NC}"
  ((WARNINGS++))
fi

echo ""

# ============================================
# CHECK 9: PART 4 - Tracking Validation
# ============================================
echo "CHECK 9: PART 4 - Tracking Validation"
echo "-----------------------------------------"

# Check for sign-off section
if grep -qi "sign-off\|signoff" "$IMPL_FILE"; then
  echo -e "  ${GREEN}✅ Sign-off section present${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: No sign-off section found${NC}"
  ((WARNINGS++))
fi

# Check for completion criteria
if grep -qi "completion criteria\|project complete" "$IMPL_FILE"; then
  echo -e "  ${GREEN}✅ Completion criteria defined${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: No completion criteria defined${NC}"
  ((WARNINGS++))
fi

echo ""

# ============================================
# CHECK 10: Scope Boundary Validation
# ============================================
echo "CHECK 10: Scope Boundary Validation (PM vs Technical)"
echo "-----------------------------------------"

# Check for technical content that belongs in SPEC
technical_patterns=(
  "class [A-Z]"
  "def [a-z]"
  "import "
  "function "
)

technical_content_count=0
for pattern in "${technical_patterns[@]}"; do
  count=$(grep -cE "$pattern" "$IMPL_FILE" 2>/dev/null || echo "0")
  if [ "$count" -gt 5 ]; then
    echo -e "  ${YELLOW}⚠️  WARNING: Technical pattern found $count times: $pattern${NC}"
    technical_content_count=$((technical_content_count + count))
  fi
done

if [ "$technical_content_count" -gt 10 ]; then
  echo -e "  ${YELLOW}⚠️  WARNING: Heavy technical content detected${NC}"
  echo "           IMPL focuses on WHO/WHAT/WHEN, not HOW (technical details go in SPEC)"
  ((WARNINGS++))
else
  echo -e "  ${GREEN}✅ Project management focus maintained${NC}"
fi

# Check for required PM content
pm_patterns=(
  "Phase"
  "Timeline"
  "Owner"
  "Deliverable"
  "Team"
)

pm_found=0
for pattern in "${pm_patterns[@]}"; do
  if grep -qi "$pattern" "$IMPL_FILE"; then
    ((pm_found++))
  fi
done

if [ "$pm_found" -lt 3 ]; then
  echo -e "  ${YELLOW}⚠️  WARNING: Insufficient project management content${NC}"
  ((WARNINGS++))
else
  echo -e "  ${GREEN}✅ Project management content present ($pm_found/5 patterns)${NC}"
fi

echo ""

# ============================================
# CHECK 11: Element ID Format Validation
# ============================================
echo "CHECK 11: Element ID Format Validation"
echo "-----------------------------------------"

# Check for deprecated element ID formats
# Old formats: TYPE-NN-YY, FR-001, AC-001, QA-001, BC-001, BO-001
deprecated_patterns=(
  "^### (FR|QA|AC|BC|BO)-[0-9]{3}:"
  "IMPL-[0-9]{3}-[0-9]{2}"
)

deprecated_found=0
for pattern in "${deprecated_patterns[@]}"; do
  matches=$(grep -cE "$pattern" "$IMPL_FILE" 2>/dev/null || echo "0")
  if [ "$matches" -gt 0 ]; then
    echo -e "  ${RED}❌ ERROR: Deprecated element ID format found ($matches occurrences)${NC}"
    echo "           Pattern: $pattern"
    echo "           Use unified format: IMPL.NN.TT.SS"
    deprecated_found=$((deprecated_found + matches))
  fi
done

if [ "$deprecated_found" -eq 0 ]; then
  echo -e "  ${GREEN}✅ No deprecated element ID formats found${NC}"
fi

# Validate unified format element IDs (TYPE.NN.TT.SS)
unified_pattern="IMPL\.[0-9]{2,9}\.[0-9]{2,9}\.[0-9]{2,9}"
unified_count=$(grep -cE "$unified_pattern" "$IMPL_FILE" 2>/dev/null || echo "0")
echo "  Unified format element IDs found: $unified_count"

if [ "$deprecated_found" -gt 0 ]; then
  ((ERRORS++))
fi

echo ""

# ============================================
# CHECK 12: Traceability Tags (Layer 8)
# ============================================
echo "CHECK 12: Traceability Tags (Layer 8)"
echo "-----------------------------------------"

required_tags=("@brd" "@prd" "@ears" "@bdd" "@adr" "@sys" "@req")

tag_count=0
for tag in "${required_tags[@]}"; do
  if grep -qE "^${tag}:|^\- \`${tag}:" "$IMPL_FILE"; then
    echo -e "  ${GREEN}✅ Found: $tag${NC}"
    ((tag_count++))
  else
    echo -e "  ${RED}❌ MISSING: $tag${NC}"
    ((ERRORS++))
  fi
done

echo "  Total traceability tags: $tag_count"
if [ $tag_count -lt 7 ]; then
  echo -e "  ${RED}❌ ERROR: Minimum 7 tags required for Layer 8${NC}"
fi

# Check for empty tags
if grep -qE "@[a-z]+:\s*$" "$IMPL_FILE"; then
  echo -e "  ${RED}❌ ERROR: Empty tag value found${NC}"
  ((ERRORS++))
fi

echo ""

# ============================================
# CHECK 12: Cross-Reference Validation
# ============================================
echo "CHECK 12: Cross-Reference Validation"
echo "-----------------------------------------"

base_dir="$(dirname "$IMPL_FILE")"

# Check REQ references
req_refs=$(grep -oE "REQ-[0-9]+" "$IMPL_FILE" 2>/dev/null | sort -u || echo "")
if [ -n "$req_refs" ]; then
  req_count=$(echo "$req_refs" | wc -l)
  echo "  Found $req_count REQ reference(s)"

  echo "$req_refs" | while read -r req_ref; do
    req_file=$(find "$base_dir/../REQ" -name "${req_ref}*.md" 2>/dev/null | head -1)
    if [ -n "$req_file" ]; then
      echo -e "    ${GREEN}✅ $req_ref exists${NC}"
    else
      echo -e "    ${YELLOW}⚠️  WARNING: $req_ref not found${NC}"
    fi
  done
else
  echo -e "  ${YELLOW}⚠️  WARNING: No REQ references found${NC}"
  ((WARNINGS++))
fi

# Check ADR references
adr_refs=$(grep -oE "ADR-[0-9]+" "$IMPL_FILE" 2>/dev/null | sort -u || echo "")
if [ -n "$adr_refs" ]; then
  adr_count=$(echo "$adr_refs" | wc -l)
  echo "  Found $adr_count ADR reference(s)"
fi

echo ""

# ============================================
# SUMMARY
# ============================================
echo "========================================="
echo "VALIDATION SUMMARY"
echo "========================================="
echo "File: $IMPL_FILE"
echo "Script Version: ${SCRIPT_VERSION}"
echo "IMPL ID: ${IMPL_ID:-unknown}"
echo "Phases: ${phase_count:-0}"
echo "Deliverables: ${total_deliverables:-0}"
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
  echo -e "${GREEN}✅ PASSED: All validation checks passed${NC}"
  echo ""
  echo "Document complies with:"
  echo "  - IMPL-TEMPLATE.md structure"
  echo "  - AI Dev Flow SDD framework requirements"
  echo "  - Layer 8 artifact standards"
  echo "  - Project management scope boundaries"
  exit 0
elif [ $ERRORS -eq 0 ]; then
  echo -e "${YELLOW}⚠️  PASSED WITH WARNINGS: Document valid but has $WARNINGS warnings${NC}"
  echo ""
  echo "Recommendations:"
  echo "  - Review warnings for quality improvements"
  echo "  - See IMPL-TEMPLATE.md for best practices"
  echo "  - Ensure technical details are in SPEC, not IMPL"
  exit 0
else
  echo -e "${RED}❌ FAILED: $ERRORS critical errors found${NC}"
  echo ""
  echo "Action Required:"
  echo "  1. Fix all errors listed above"
  echo "  2. Review IMPL-TEMPLATE.md for requirements"
  echo "  3. Check IMPL_CREATION_RULES.md for standards"
  echo "  4. Re-run validation: ./scripts/validate_impl.sh $IMPL_FILE"
  exit 1
fi
