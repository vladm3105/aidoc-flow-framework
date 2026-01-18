#!/bin/bash
# TASKS (Code Generation Plan) Template Validator v1.0
# Validates TASKS documents against:
# - TASKS-TEMPLATE.md (authoritative template)
# - AI Dev Flow SDD framework standards
# - Layer 10 artifact requirements
# - Code generation task structure
# Usage: ./scripts/validate_tasks.sh <TASKS_FILE>

set -e

TASKS_FILE=$1
ERRORS=0
WARNINGS=0
SCRIPT_VERSION="1.0.0"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

if [ -z "$TASKS_FILE" ]; then
  echo "Usage: $0 <TASKS_FILE>"
  echo "Example: $0 /opt/data/project/docs/TASKS/TASKS-001_gateway_service.md"
  exit 1
fi

if [ ! -f "$TASKS_FILE" ]; then
  echo -e "${RED}ERROR: File not found: $TASKS_FILE${NC}"
  exit 1
fi

echo "========================================="
echo "TASKS Template Validator v${SCRIPT_VERSION}"
echo "========================================="
echo "File: $TASKS_FILE"
echo "Artifact Type: TASKS (Code Generation Plan) - Layer 10"
echo ""

# ============================================
# CHECK 1: Filename Format
# ============================================
echo "CHECK 1: Filename Format"
echo "-----------------------------------------"

filename=$(basename "$TASKS_FILE")

# Pattern: TASKS-NNN_descriptive_slug.md
if [[ $filename =~ ^TASKS-[0-9]{2,}_[a-z0-9_]+\.md$ ]]; then
  echo -e "  ${GREEN}✅ Filename format valid: $filename${NC}"

  # Extract TASKS ID
  TASKS_ID=$(echo "$filename" | grep -oE "TASKS-[0-9]+" | head -1)
  echo "  TASKS ID: $TASKS_ID"
else
  echo -e "  ${RED}❌ ERROR: Invalid filename format: $filename${NC}"
  echo "           Expected: TASKS-NNN_descriptive_slug.md"
  echo "           Pattern: ^TASKS-[0-9]{2,}_[a-z0-9_]+\\.md$"
  ((ERRORS++))
fi

echo ""

# ============================================
# CHECK 2: Frontmatter Validation
# ============================================
echo "CHECK 2: Frontmatter Validation"
echo "-----------------------------------------"

# Check for YAML frontmatter (--- delimiters)
if grep -q "^---" "$TASKS_FILE"; then
  echo -e "  ${GREEN}✅ YAML frontmatter present${NC}"

  # Check for required fields
  if grep -q "artifact_type: TASKS" "$TASKS_FILE"; then
    echo -e "  ${GREEN}✅ artifact_type: TASKS${NC}"
  else
    echo -e "  ${RED}❌ ERROR: Missing or invalid artifact_type (must be TASKS)${NC}"
    ((ERRORS++))
  fi

  if grep -q "layer: 10" "$TASKS_FILE"; then
    echo -e "  ${GREEN}✅ layer: 10${NC}"
  else
    echo -e "  ${RED}❌ ERROR: Missing or invalid layer (must be 10)${NC}"
    ((ERRORS++))
  fi

  if grep -q "layer-10-artifact" "$TASKS_FILE"; then
    echo -e "  ${GREEN}✅ layer-10-artifact tag present${NC}"
  else
    echo -e "  ${YELLOW}⚠️  WARNING: Missing layer-10-artifact tag${NC}"
    ((WARNINGS++))
  fi

  # Check parent_spec
  if grep -q "parent_spec: SPEC-" "$TASKS_FILE"; then
    parent_spec=$(grep -oE "parent_spec: SPEC-[0-9]+" "$TASKS_FILE" | head -1 | cut -d':' -f2 | tr -d ' ')
    echo -e "  ${GREEN}✅ parent_spec: $parent_spec${NC}"
  else
    echo -e "  ${RED}❌ ERROR: Missing parent_spec field${NC}"
    ((ERRORS++))
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
  "TASKS ID"
  "Title"
  "Status"
  "Version"
  "Created"
  "Last Updated"
  "Author"
  "Parent SPEC"
  "Complexity"
)

for field in "${required_dc_fields[@]}"; do
  if grep -qi "$field" "$TASKS_FILE"; then
    echo -e "  ${GREEN}✅ Found: $field${NC}"
  else
    echo -e "  ${RED}❌ MISSING: $field${NC}"
    ((ERRORS++))
  fi
done

# Check status value
if grep -qE "Status.*\|.*(Draft|Ready|In Progress|Completed|Blocked)" "$TASKS_FILE"; then
  echo -e "  ${GREEN}✅ Status has valid enum value${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: Status should be Draft, Ready, In Progress, Completed, or Blocked${NC}"
  ((WARNINGS++))
fi

echo ""

# ============================================
# CHECK 4: Required Sections
# ============================================
echo "CHECK 4: Required Sections"
echo "-----------------------------------------"

required_sections=(
  "## 1. Overview"
  "## 2. Phase"
  "## 3. Dependencies"
  "## 4. Acceptance Criteria"
  "## Traceability"
)

for section in "${required_sections[@]}"; do
  if grep -q "$section" "$TASKS_FILE"; then
    echo -e "  ${GREEN}✅ Found: $section${NC}"
  else
    echo -e "  ${RED}❌ MISSING: $section${NC}"
    ((ERRORS++))
  fi
done

echo ""

# ============================================
# CHECK 5: Phase Structure Validation
# ============================================
echo "CHECK 5: Phase Structure Validation"
echo "-----------------------------------------"

# Count phases
phase_count=$(grep -cE "^### Phase [0-9]+" "$TASKS_FILE" 2>/dev/null | tr -d '\n' || echo "0")
[[ -z "$phase_count" || ! "$phase_count" =~ ^[0-9]+$ ]] && phase_count=0

if [ "$phase_count" -ge 1 ]; then
  echo -e "  ${GREEN}✅ Found $phase_count phase(s)${NC}"
else
  echo -e "  ${RED}❌ ERROR: No phases defined${NC}"
  ((ERRORS++))
fi

# Check for task structure within phases
task_count=$(grep -cE "^#### TASK-[0-9]+" "$TASKS_FILE" 2>/dev/null | tr -d '\n' || echo "0")
[[ -z "$task_count" || ! "$task_count" =~ ^[0-9]+$ ]] && task_count=0
if [ "$task_count" -ge 1 ]; then
  echo -e "  ${GREEN}✅ Found $task_count task(s)${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: No TASK-NNN items found${NC}"
  ((WARNINGS++))
fi

# Check for checkboxes
checkbox_count=$(grep -c "\[[ x]\]" "$TASKS_FILE" 2>/dev/null | tr -d '\n' || echo "0")
[[ -z "$checkbox_count" || ! "$checkbox_count" =~ ^[0-9]+$ ]] && checkbox_count=0
if [ "$checkbox_count" -ge 1 ]; then
  echo -e "  ${GREEN}✅ Found $checkbox_count checkbox(es)${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: No task checkboxes found${NC}"
  ((WARNINGS++))
fi

echo ""

# ============================================
# CHECK 6: Task Detail Validation
# ============================================
echo "CHECK 6: Task Detail Validation"
echo "-----------------------------------------"

# Check for required task fields
task_fields=(
  "Input:"
  "Output:"
  "Acceptance:"
)

for field in "${task_fields[@]}"; do
  field_count=$(grep -ci "$field" "$TASKS_FILE" 2>/dev/null | tr -d '\n' || echo "0")
  [[ -z "$field_count" || ! "$field_count" =~ ^[0-9]+$ ]] && field_count=0
  if [ "$field_count" -ge 1 ]; then
    echo -e "  ${GREEN}✅ Found $field_count \"$field\" field(s)${NC}"
  else
    echo -e "  ${YELLOW}⚠️  WARNING: No \"$field\" fields found in tasks${NC}"
    ((WARNINGS++))
  fi
done

# Check for file references
if grep -qE "\`[a-z_/]+\.(py|ts|js|yaml|json|md)\`" "$TASKS_FILE"; then
  file_refs=$(grep -cE "\`[a-z_/]+\.(py|ts|js|yaml|json|md)\`" "$TASKS_FILE" 2>/dev/null | tr -d '\n' || echo "0")
  [[ -z "$file_refs" || ! "$file_refs" =~ ^[0-9]+$ ]] && file_refs=0
  echo -e "  ${GREEN}✅ Found $file_refs file reference(s)${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: No file references found${NC}"
  ((WARNINGS++))
fi

echo ""

# ============================================
# CHECK 7: Dependencies Validation
# ============================================
echo "CHECK 7: Dependencies Validation"
echo "-----------------------------------------"

# Check for upstream dependencies
if grep -qi "upstream" "$TASKS_FILE"; then
  echo -e "  ${GREEN}✅ Upstream dependencies section present${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: Document upstream dependencies${NC}"
  ((WARNINGS++))
fi

# Check for downstream dependencies
if grep -qi "downstream" "$TASKS_FILE"; then
  echo -e "  ${GREEN}✅ Downstream dependencies section present${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: Document downstream dependencies${NC}"
  ((WARNINGS++))
fi

# Check for blocking relationships
if grep -qi "blocks\|blocked by\|depends on" "$TASKS_FILE"; then
  echo -e "  ${GREEN}✅ Dependency relationships documented${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: No blocking relationships documented${NC}"
  ((WARNINGS++))
fi

echo ""

# ============================================
# CHECK 8: Acceptance Criteria Validation
# ============================================
echo "CHECK 8: Acceptance Criteria Validation"
echo "-----------------------------------------"

# Check for test coverage targets
if grep -qE "(unit|integration|e2e|coverage).*[0-9]+%" "$TASKS_FILE"; then
  echo -e "  ${GREEN}✅ Test coverage targets defined${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: No test coverage targets found${NC}"
  ((WARNINGS++))
fi

# Check for BDD scenario references
bdd_refs=$(grep -oE "BDD-[0-9]+" "$TASKS_FILE" 2>/dev/null | sort -u || echo "")
if [ -n "$bdd_refs" ]; then
  bdd_count=$(echo "$bdd_refs" | wc -l)
  echo -e "  ${GREEN}✅ Found $bdd_count BDD reference(s)${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: No BDD scenario references found${NC}"
  ((WARNINGS++))
fi

# Check for completion criteria
if grep -qi "definition of done\|completion criteria\|done when" "$TASKS_FILE"; then
  echo -e "  ${GREEN}✅ Completion criteria documented${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: No completion criteria documented${NC}"
  ((WARNINGS++))
fi

echo ""

# ============================================
# CHECK 9: Implementation Contracts (Section 7-8)
# ============================================
echo "CHECK 9: Implementation Contracts (Section 7-8)"
echo "-----------------------------------------"

# Check for embedded contracts in Section 7-8
if grep -qE "(Protocol|TypedDict|BaseModel|dataclass)" "$TASKS_FILE"; then
  echo -e "  ${GREEN}✅ Embedded contract definitions found${NC}"

  # Check for type hints
  if grep -qE "-> [A-Za-z\[\]|]+:" "$TASKS_FILE"; then
    echo -e "  ${GREEN}✅ Type hints present in contracts${NC}"
  else
    echo -e "  ${YELLOW}⚠️  WARNING: Add return type hints to contract methods${NC}"
    ((WARNINGS++))
  fi
else
  echo -e "  ${BLUE}ℹ️  INFO: No embedded contracts (may not be needed)${NC}"
fi

echo ""

# ============================================
# CHECK 10: Element ID Format Validation
# ============================================
echo "CHECK 10: Element ID Format Validation"
echo "-----------------------------------------"

# Check for deprecated element ID formats
# Old formats: TYPE-NN-YY, FR-001, AC-001, QA-001, BC-001, BO-001
deprecated_patterns=(
  "^### (FR|QA|AC|BC|BO)-[0-9]{3}:"
  "TASKS-[0-9]{3}-[0-9]{2}"
)

deprecated_found=0
for pattern in "${deprecated_patterns[@]}"; do
  matches=$(grep -cE "$pattern" "$TASKS_FILE" 2>/dev/null | tr -d '\n' || echo "0")
  [[ -z "$matches" || ! "$matches" =~ ^[0-9]+$ ]] && matches=0
  if [ "$matches" -gt 0 ]; then
    echo -e "  ${RED}❌ ERROR: Deprecated element ID format found ($matches occurrences)${NC}"
    echo "           Pattern: $pattern"
    echo "           Use unified format: TASKS.NN.TT.SS"
    deprecated_found=$((deprecated_found + matches))
  fi
done

if [ "$deprecated_found" -eq 0 ]; then
  echo -e "  ${GREEN}✅ No deprecated element ID formats found${NC}"
fi

# Validate unified format element IDs (TYPE.NN.TT.SS)
unified_pattern="TASKS\.[0-9]{2,9}\.[0-9]{2,9}\.[0-9]{2,9}"
unified_count=$(grep -cE "$unified_pattern" "$TASKS_FILE" 2>/dev/null | tr -d '\n' || echo "0")
[[ -z "$unified_count" || ! "$unified_count" =~ ^[0-9]+$ ]] && unified_count=0
echo "  Unified format element IDs found: $unified_count"

if [ "$deprecated_found" -gt 0 ]; then
  ((ERRORS++))
fi

echo ""

# ============================================
# CHECK 11: Traceability Tags (Layer 10)
echo "CHECK 11: Traceability Tags (Layer 10)"

echo "-----------------------------------------"

required_tags=("@brd" "@prd" "@ears" "@bdd" "@adr" "@sys" "@req" "@spec")

tag_count=0
for tag in "${required_tags[@]}"; do
  if grep -qE "^${tag}:|^\- \`${tag}:" "$TASKS_FILE"; then
    echo -e "  ${GREEN}✅ Found: $tag${NC}"
    ((tag_count++))
  else
    echo -e "  ${RED}❌ MISSING: $tag${NC}"
    ((ERRORS++))
  fi
done

# Check optional tags
optional_tags=("@ctr")
for tag in "${optional_tags[@]}"; do
  if grep -qE "^${tag}:|^\- \`${tag}:" "$TASKS_FILE"; then
    echo -e "  ${GREEN}✅ Optional tag present: $tag${NC}"
    ((tag_count++))
  fi
done

echo "  Total traceability tags: $tag_count"
if [ $tag_count -lt 8 ]; then
  echo -e "  ${RED}❌ ERROR: Minimum 8 tags required for Layer 10${NC}"
fi

# Check for empty tags
if grep -qE "@[a-z]+:\s*$" "$TASKS_FILE"; then
  echo -e "  ${RED}❌ ERROR: Empty tag value found${NC}"
  ((ERRORS++))
fi

echo ""

# ============================================
# CHECK 11: Cross-Reference Validation
# ============================================
echo "CHECK 11: Cross-Reference Validation"
echo "-----------------------------------------"

base_dir="$(dirname "$TASKS_FILE")"
spec_dir="$base_dir/../09_SPEC"

# Validate parent SPEC reference
parent_spec=$(grep -oE "SPEC-[0-9]+" "$TASKS_FILE" | head -1 || echo "")
if [ -n "$parent_spec" ]; then
  echo "  Parent SPEC: $parent_spec"

  spec_file=$(find "$spec_dir" -name "${parent_spec}*.yaml" 2>/dev/null | head -1)
  if [ -n "$spec_file" ]; then
    echo -e "  ${GREEN}✅ Parent SPEC file exists${NC}"
  else
    echo -e "  ${RED}❌ ERROR: Parent SPEC file not found: $parent_spec${NC}"
    ((ERRORS++))
  fi
else
  echo -e "  ${RED}❌ ERROR: No parent SPEC reference found${NC}"
  ((ERRORS++))
fi

# Check REQ references
req_refs=$(grep -oE "REQ-[0-9]+" "$TASKS_FILE" 2>/dev/null | sort -u || echo "")
if [ -n "$req_refs" ]; then
  req_count=$(echo "$req_refs" | wc -l)
  echo "  Found $req_count REQ reference(s)"
fi

# Check ADR references
adr_refs=$(grep -oE "ADR-[0-9]+" "$TASKS_FILE" 2>/dev/null | sort -u || echo "")
if [ -n "$adr_refs" ]; then
  adr_count=$(echo "$adr_refs" | wc -l)
  echo "  Found $adr_count ADR reference(s)"
fi

echo ""

# ============================================
# CHECK 12: Code Generation Readiness
# ============================================
echo "CHECK 12: Code Generation Readiness"
echo "-----------------------------------------"

# Check for module/file structure
if grep -qE "module|file|class|function" "$TASKS_FILE"; then
  echo -e "  ${GREEN}✅ Code structure elements documented${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: Document module/file/class structure${NC}"
  ((WARNINGS++))
fi

# Check for import/dependency information
if grep -qiE "import|dependency|require" "$TASKS_FILE"; then
  echo -e "  ${GREEN}✅ Import/dependency information present${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: Document import dependencies${NC}"
  ((WARNINGS++))
fi

# Check for error handling
if grep -qiE "error|exception|handle" "$TASKS_FILE"; then
  echo -e "  ${GREEN}✅ Error handling documented${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: Document error handling approach${NC}"
  ((WARNINGS++))
fi

echo ""

# ============================================
# CHECK 13: Token Size Validation
# ============================================
echo "CHECK 13: Token Size Validation"
echo "-----------------------------------------"

# Get file size
file_size=$(wc -c < "$TASKS_FILE")
file_kb=$((file_size / 1024))

echo "  File size: ${file_kb}KB"

if [ "$file_kb" -gt 200 ]; then
  echo -e "  ${YELLOW}⚠️  WARNING: File size ${file_kb}KB exceeds 200KB optimal${NC}"
  echo "           Consider splitting into multiple TASKS files"
  ((WARNINGS++))
elif [ "$file_kb" -gt 100 ]; then
  echo -e "  ${BLUE}ℹ️  INFO: File size ${file_kb}KB - consider optimization${NC}"
else
  echo -e "  ${GREEN}✅ File size within optimal range${NC}"
fi

echo ""

# ============================================
# SUMMARY
# ============================================
echo "========================================="
echo "VALIDATION SUMMARY"
echo "========================================="
echo "File: $TASKS_FILE"
echo "Script Version: ${SCRIPT_VERSION}"
echo "TASKS ID: ${TASKS_ID:-unknown}"
echo "Phases: ${phase_count:-0}"
echo "Tasks: ${task_count:-0}"
echo "Tags: ${tag_count:-0}"
echo "File Size: ${file_kb:-0}KB"
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
  echo -e "${GREEN}✅ PASSED: All validation checks passed${NC}"
  echo ""
  echo "Document complies with:"
  echo "  - TASKS-TEMPLATE.md structure"
  echo "  - AI Dev Flow SDD framework requirements"
  echo "  - Layer 10 artifact standards"
  echo "  - Code generation readiness requirements"
  exit 0
elif [ $ERRORS -eq 0 ]; then
  echo -e "${YELLOW}⚠️  PASSED WITH WARNINGS: Document valid but has $WARNINGS warnings${NC}"
  echo ""
  echo "Recommendations:"
  echo "  - Review warnings for quality improvements"
  echo "  - See TASKS-TEMPLATE.md for best practices"
  echo "  - Ensure all task details are complete"
  exit 0
else
  echo -e "${RED}❌ FAILED: $ERRORS critical errors found${NC}"
  echo ""
  echo "Action Required:"
  echo "  1. Fix all errors listed above"
  echo "  2. Review TASKS-TEMPLATE.md for requirements"
  echo "  3. Check TASKS_CREATION_RULES.md for standards"
  echo "  4. Ensure all 8 mandatory traceability tags present"
  echo "  5. Re-run validation: ./scripts/validate_tasks.sh $TASKS_FILE"
  exit 1
fi
