#!/bin/bash
# IPLAN (Implementation Work Plan) Template Validator v1.0
# Validates IPLAN documents against:
# - IPLAN-TEMPLATE.md (authoritative template)
# - AI Dev Flow SDD framework standards
# - Layer 12 artifact requirements
# - Session-based execution requirements
# Usage: ./scripts/validate_iplan.sh <IPLAN_FILE>

# Note: NOT using 'set -e' because ((ERRORS++)) returns false when ERRORS=0

IPLAN_FILE=$1
ERRORS=0
WARNINGS=0
SCRIPT_VERSION="1.0.0"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

if [ -z "$IPLAN_FILE" ]; then
  echo "Usage: $0 <IPLAN_FILE>"
  echo "Example: $0 /opt/data/project/docs/IPLAN/IPLAN-01_gateway_connection.md"
  exit 1
fi

if [ ! -f "$IPLAN_FILE" ]; then
  echo -e "${RED}ERROR: File not found: $IPLAN_FILE${NC}"
  exit 1
fi

echo "========================================="
echo "IPLAN Template Validator v${SCRIPT_VERSION}"
echo "========================================="
echo "File: $IPLAN_FILE"
echo "Artifact Type: IPLAN (Implementation Work Plan) - Layer 12"
echo ""

# ============================================
# CHECK 1: Filename Format
# ============================================
echo "CHECK 1: Filename Format"
echo "-----------------------------------------"

filename=$(basename "$IPLAN_FILE")

# Pattern: IPLAN-NN_descriptive_slug.md (mandatory format, no timestamps)
# Per IPLAN_VALIDATION_RULES.md: ^IPLAN-[0-9]{2,}_[a-z0-9_]+\.md$
if [[ $filename =~ ^IPLAN-[0-9]{2,}_[a-z0-9_]+\.md$ ]]; then
  echo -e "  ${GREEN}✅ Filename format valid: $filename${NC}"

  # Extract IPLAN ID
  IPLAN_ID=$(echo "$filename" | grep -oE "IPLAN-[0-9]+" | head -1)
  echo "  IPLAN ID: $IPLAN_ID"
  # Disallow timestamp-like suffixes in slug (e.g., _YYYYMMDD or _YYYYMMDD_HHMMSS)
  if [[ $filename =~ _[0-9]{8}(_[0-9]{6})?\.md$ ]]; then
    echo -e "  ${RED}❌ ERROR: Timestamp-like suffix detected in filename (timestamps are not allowed)${NC}"
    ERRORS=$((ERRORS + 1))
  fi
else
  echo -e "  ${RED}❌ ERROR: Invalid filename format: $filename${NC}"
  echo "           Expected: IPLAN-NN_descriptive_slug.md"
  echo "           Pattern: ^IPLAN-[0-9]{2,}_[a-z0-9_]+\\.md$"
  echo "           Rules: lowercase, underscores only, no hyphens in slug, NO timestamps"
  ERRORS=$((ERRORS + 1))
fi

echo ""

# ============================================
# CHECK 2: Frontmatter Validation
# ============================================
echo "CHECK 2: Frontmatter Validation"
echo "-----------------------------------------"

# Check for YAML frontmatter (--- delimiters)
if grep -q "^---" "$IPLAN_FILE"; then
  echo -e "  ${GREEN}✅ YAML frontmatter present${NC}"

  # Check for required fields
  if grep -q "artifact_type: IPLAN" "$IPLAN_FILE"; then
    echo -e "  ${GREEN}✅ artifact_type: IPLAN${NC}"
  else
    echo -e "  ${RED}❌ ERROR: Missing or invalid artifact_type (must be IPLAN)${NC}"
    ERRORS=$((ERRORS + 1))
  fi

  if grep -q "layer: 12" "$IPLAN_FILE"; then
    echo -e "  ${GREEN}✅ layer: 12${NC}"
  else
    echo -e "  ${RED}❌ ERROR: Missing or invalid layer (must be 12)${NC}"
    ERRORS=$((ERRORS + 1))
  fi

  if grep -q "layer-12-artifact" "$IPLAN_FILE"; then
    echo -e "  ${GREEN}✅ layer-12-artifact tag present${NC}"
  else
    echo -e "  ${YELLOW}⚠️  WARNING: Missing layer-12-artifact tag${NC}"
    WARNINGS=$((WARNINGS + 1))
  fi

  # Check parent_tasks
  if grep -q "parent_tasks: TASKS-" "$IPLAN_FILE"; then
    parent_tasks=$(grep -oE "parent_tasks: TASKS-[0-9]+" "$IPLAN_FILE" | head -1 | cut -d':' -f2 | tr -d ' ')
    echo -e "  ${GREEN}✅ parent_tasks: $parent_tasks${NC}"
  else
    echo -e "  ${RED}❌ ERROR: Missing parent_tasks field${NC}"
    ERRORS=$((ERRORS + 1))
  fi

  # Check complexity
  if grep -qE "complexity: [1-5]" "$IPLAN_FILE"; then
    complexity=$(grep -oE "complexity: [1-5]" "$IPLAN_FILE" | head -1 | cut -d':' -f2 | tr -d ' ')
    echo -e "  ${GREEN}✅ complexity: $complexity${NC}"
  else
    echo -e "  ${YELLOW}⚠️  WARNING: Missing or invalid complexity (1-5)${NC}"
    WARNINGS=$((WARNINGS + 1))
  fi
else
  echo -e "  ${RED}❌ ERROR: Missing YAML frontmatter (--- delimiters)${NC}"
  ERRORS=$((ERRORS + 1))
fi

echo ""

# ============================================
# CHECK 3: Document Control Table
# ============================================
echo "CHECK 3: Document Control Table"
echo "-----------------------------------------"

required_dc_fields=(
  "ID"
  "Status"
  "Version"
  "Created"
  "Last Updated"
  "Author"
  "Estimated Effort"
  "Complexity"
  "Parent TASKS"
)

for field in "${required_dc_fields[@]}"; do
  if grep -qi "$field" "$IPLAN_FILE"; then
    echo -e "  ${GREEN}✅ Found: $field${NC}"
  else
    echo -e "  ${RED}❌ MISSING: $field${NC}"
    ERRORS=$((ERRORS + 1))
  fi
done

# Check status value
if grep -qE "Status.*\|.*(Draft|Ready|In Progress|Completed|Blocked)" "$IPLAN_FILE"; then
  echo -e "  ${GREEN}✅ Status has valid enum value${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: Status should be Draft, Ready, In Progress, Completed, or Blocked${NC}"
  WARNINGS=$((WARNINGS + 1))
fi

echo ""

# ============================================
# CHECK 4: Required Sections
# ============================================
echo "CHECK 4: Required Sections"
echo "-----------------------------------------"

required_sections=(
  "## Position in"
  "## Objective"
  "## Context"
  "## Task List"
  "## Implementation Guide"
  "## Traceability Tags"
  "## Traceability"
  "## Risk"
  "## Success Criteria"
)

for section in "${required_sections[@]}"; do
  if grep -q "$section" "$IPLAN_FILE"; then
    echo -e "  ${GREEN}✅ Found: $section${NC}"
  else
    echo -e "  ${RED}❌ MISSING: $section${NC}"
    ERRORS=$((ERRORS + 1))
  fi
done

echo ""

# ============================================
# CHECK 5: Task List Validation
# ============================================
echo "CHECK 5: Task List Validation"
echo "-----------------------------------------"

# Count phases
phase_count=$(grep -cE "^### Phase [0-9]+" "$IPLAN_FILE" 2>/dev/null) || phase_count=0

if [ "$phase_count" -ge 1 ]; then
  echo -e "  ${GREEN}✅ Found $phase_count phase(s)${NC}"
else
  echo -e "  ${RED}❌ ERROR: No phases defined in Task List${NC}"
  ERRORS=$((ERRORS + 1))
fi

# Check for checkboxes
checkbox_count=$(grep -c "\[[ x]\]" "$IPLAN_FILE" 2>/dev/null) || checkbox_count=0

if [ "$checkbox_count" -ge 1 ]; then
  echo -e "  ${GREEN}✅ Found $checkbox_count task checkbox(es)${NC}"
else
  echo -e "  ${RED}❌ ERROR: No task checkboxes found${NC}"
  ERRORS=$((ERRORS + 1))
fi

# Check for time estimates
if grep -qE "[0-9]+ hours?" "$IPLAN_FILE"; then
  echo -e "  ${GREEN}✅ Time estimates present${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: No time estimates found${NC}"
  WARNINGS=$((WARNINGS + 1))
fi

# Check for status markers
if grep -qE "(COMPLETED|PENDING|IN PROGRESS)" "$IPLAN_FILE"; then
  echo -e "  ${GREEN}✅ Phase status markers present${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: No phase status markers found${NC}"
  WARNINGS=$((WARNINGS + 1))
fi

echo ""

# ============================================
# CHECK 6: Implementation Guide Validation
# ============================================
echo "CHECK 6: Implementation Guide (Bash Commands)"
echo "-----------------------------------------"

# Count bash code blocks
bash_count=$(grep -c '```bash' "$IPLAN_FILE" 2>/dev/null) || bash_count=0

if [ "$bash_count" -ge 1 ]; then
  echo -e "  ${GREEN}✅ Found $bash_count bash code block(s)${NC}"

  if [ "$bash_count" -lt 3 ]; then
    echo -e "  ${YELLOW}⚠️  WARNING: Only $bash_count bash blocks (recommend 3+)${NC}"
    WARNINGS=$((WARNINGS + 1))
  fi
else
  echo -e "  ${RED}❌ ERROR: No bash code blocks found${NC}"
  ERRORS=$((ERRORS + 1))
fi

# Check for verification sections
if grep -qi "verification\|verify\|expected" "$IPLAN_FILE"; then
  echo -e "  ${GREEN}✅ Verification steps present${NC}"
else
  echo -e "  ${RED}❌ ERROR: No verification steps found${NC}"
  ERRORS=$((ERRORS + 1))
fi

# Check for relative paths (should be absolute)
if grep -qE '(cd|touch|mkdir) \.\.' "$IPLAN_FILE"; then
  echo -e "  ${RED}❌ ERROR: Relative paths found - use absolute paths${NC}"
  ERRORS=$((ERRORS + 1))
else
  echo -e "  ${GREEN}✅ No relative paths detected${NC}"
fi

# Additional check for paths that don't start with / ~ or $
potential_relative=$(grep -E '(cd|touch|mkdir) [^/~$]' "$IPLAN_FILE" 2>/dev/null | grep -v "cd \$" | head -3 || echo "")
if [ -n "$potential_relative" ]; then
  echo -e "  ${YELLOW}⚠️  WARNING: Potential relative paths - prefer absolute paths${NC}"
  WARNINGS=$((WARNINGS + 1))
fi

echo ""

# ============================================
# CHECK 7: Element ID Format Validation
# ============================================
echo "CHECK 7: Element ID Format Validation"
echo "-----------------------------------------"

# Check for deprecated element ID formats
# Old formats: TYPE-NN-YY, FR-001, AC-001, QA-001, BC-001, BO-001
deprecated_patterns=(
  "^### (FR|QA|AC|BC|BO)-[0-9]{3}:"
  "IPLAN-[0-9]{3}-[0-9]{2}"
)

deprecated_found=0
for pattern in "${deprecated_patterns[@]}"; do
  matches=$(grep -cE "$pattern" "$IPLAN_FILE" 2>/dev/null || echo "0")
  if [ "$matches" -gt 0 ]; then
    echo -e "  ${RED}❌ ERROR: Deprecated element ID format found ($matches occurrences)${NC}"
    echo "           Pattern: $pattern"
    echo "           Use unified format: IPLAN.NN.TT.SS"
    deprecated_found=$((deprecated_found + matches))
  fi
done

if [ "$deprecated_found" -eq 0 ]; then
  echo -e "  ${GREEN}✅ No deprecated element ID formats found${NC}"
fi

# Validate unified format element IDs (TYPE.NN.TT.SS)
unified_pattern="IPLAN\.[0-9]{2,9}\.[0-9]{2,9}\.[0-9]{2,9}"
unified_count=$(grep -cE "$unified_pattern" "$IPLAN_FILE" 2>/dev/null || echo "0")
echo "  Unified format element IDs found: $unified_count"

if [ "$deprecated_found" -gt 0 ]; then
  ERRORS=$((ERRORS + 1))
fi

echo ""

# ============================================
# CHECK 8: Traceability Tags (Layer 12 - All 9)
# ============================================
echo "CHECK 8: Traceability Tags (Layer 12 - All 9 Mandatory)"
echo "-----------------------------------------"

required_tags=("@brd" "@prd" "@ears" "@bdd" "@adr" "@sys" "@req" "@spec" "@tasks")

tag_count=0
for tag in "${required_tags[@]}"; do
  if grep -qE "^${tag}:|^\- \`${tag}:" "$IPLAN_FILE"; then
    echo -e "  ${GREEN}✅ Found: $tag${NC}"
    tag_count=$((tag_count + 1))
  else
    echo -e "  ${RED}❌ MISSING: $tag${NC}"
    ERRORS=$((ERRORS + 1))
  fi
done

# Check optional tags
optional_tags=("@impl" "@ctr")
for tag in "${optional_tags[@]}"; do
  if grep -qE "^${tag}:|^\- \`${tag}:" "$IPLAN_FILE"; then
    echo -e "  ${GREEN}✅ Optional tag present: $tag${NC}"
    tag_count=$((tag_count + 1))
  fi
done

echo "  Total traceability tags: $tag_count"
if [ $tag_count -lt 9 ]; then
  echo -e "  ${RED}❌ ERROR: Minimum 9 tags required for Layer 12${NC}"
fi

# Check for empty tags
if grep -qE "@[a-z]+:\s*$" "$IPLAN_FILE"; then
  echo -e "  ${RED}❌ ERROR: Empty tag value found${NC}"
  ERRORS=$((ERRORS + 1))
fi

echo ""

# ============================================
# CHECK 8: Prerequisites Validation
# ============================================
echo "CHECK 8: Prerequisites Validation"
echo "-----------------------------------------"

# Check for prerequisites section
if grep -qi "prerequisites" "$IPLAN_FILE"; then
  echo -e "  ${GREEN}✅ Prerequisites section present${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: No Prerequisites section found${NC}"
  WARNINGS=$((WARNINGS + 1))
fi

# Check for tools documentation
if grep -qi "required tools\|tools:" "$IPLAN_FILE"; then
  echo -e "  ${GREEN}✅ Required tools documented${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: Required tools not documented${NC}"
  WARNINGS=$((WARNINGS + 1))
fi

# Check for file access documentation
if grep -qi "file.* access\|required files" "$IPLAN_FILE"; then
  echo -e "  ${GREEN}✅ Required file access documented${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: Required file access not documented${NC}"
  WARNINGS=$((WARNINGS + 1))
fi

echo ""

# ============================================
# CHECK 9: Cross-Reference Validation
# ============================================
echo "CHECK 9: Cross-Reference Validation"
echo "-----------------------------------------"

base_dir="$(dirname "$IPLAN_FILE")"
tasks_dir="$base_dir/../TASKS"

# Validate parent TASKS reference
parent_tasks=$(grep -oE "TASKS-[0-9]+" "$IPLAN_FILE" | head -1 || echo "")
if [ -n "$parent_tasks" ]; then
  echo "  Parent TASKS: $parent_tasks"

  tasks_file=$(find "$tasks_dir" -name "${parent_tasks}*.md" 2>/dev/null | head -1)
  if [ -n "$tasks_file" ]; then
    echo -e "  ${GREEN}✅ Parent TASKS file exists${NC}"
  else
    echo -e "  ${RED}❌ ERROR: Parent TASKS file not found: $parent_tasks${NC}"
    ERRORS=$((ERRORS + 1))
  fi
else
  echo -e "  ${RED}❌ ERROR: No parent TASKS reference found${NC}"
  ERRORS=$((ERRORS + 1))
fi

# Validate SPEC references
spec_refs=$(grep -oE "SPEC-[0-9]+" "$IPLAN_FILE" 2>/dev/null | sort -u || echo "")
if [ -n "$spec_refs" ]; then
  spec_count=$(echo "$spec_refs" | wc -l)
  echo "  Found $spec_count SPEC reference(s)"

  echo "$spec_refs" | while read -r spec_ref; do
    spec_file=$(find "$base_dir/../SPEC" -name "${spec_ref}*.yaml" 2>/dev/null | head -1)
    if [ -n "$spec_file" ]; then
      echo -e "    ${GREEN}✅ $spec_ref exists${NC}"
    else
      echo -e "    ${YELLOW}⚠️  WARNING: $spec_ref not found${NC}"
    fi
  done
fi

# Validate BDD references
bdd_refs=$(grep -oE "BDD-[0-9]+" "$IPLAN_FILE" 2>/dev/null | sort -u || echo "")
if [ -n "$bdd_refs" ]; then
  bdd_count=$(echo "$bdd_refs" | wc -l)
  echo "  Found $bdd_count BDD reference(s)"
fi

echo ""

# ============================================
# CHECK 10: Token Size Validation
# ============================================
echo "CHECK 10: Token Size Validation"
echo "-----------------------------------------"

# Get file size
file_size=$(wc -c < "$IPLAN_FILE")
file_kb=$((file_size / 1024))

echo "  File size: ${file_kb}KB"

if [ "$file_kb" -gt 400 ]; then
  echo -e "  ${RED}❌ ERROR: File size ${file_kb}KB exceeds 400KB maximum${NC}"
  ERRORS=$((ERRORS + 1))
elif [ "$file_kb" -gt 200 ]; then
  echo -e "  ${YELLOW}⚠️  WARNING: File size ${file_kb}KB exceeds 200KB optimal${NC}"
  WARNINGS=$((WARNINGS + 1))
elif [ "$file_kb" -gt 100 ]; then
  echo -e "  ${BLUE}ℹ️  INFO: File size ${file_kb}KB - consider optimization${NC}"
else
  echo -e "  ${GREEN}✅ File size within optimal range${NC}"
fi

# Estimate token count
char_count=$(wc -c < "$IPLAN_FILE")
token_estimate=$((char_count / 4))
echo "  Estimated tokens: ~$token_estimate"

echo ""

# ============================================
# CHECK 11: Verification Checklist Validation
# ============================================
echo "CHECK 11: Verification Checklist"
echo "-----------------------------------------"

if grep -qi "verification checklist" "$IPLAN_FILE"; then
  echo -e "  ${GREEN}✅ Verification Checklist section found${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: No Verification Checklist section found${NC}"
  WARNINGS=$((WARNINGS + 1))
fi

# Check for coverage metrics
if grep -qE "[0-9]+%" "$IPLAN_FILE"; then
  echo -e "  ${GREEN}✅ Coverage percentages present${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: No coverage percentages found${NC}"
  WARNINGS=$((WARNINGS + 1))
fi

# Check for phase verification
if grep -qi "after phase" "$IPLAN_FILE"; then
  echo -e "  ${GREEN}✅ Phase-based verification present${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: No phase-based verification found${NC}"
  WARNINGS=$((WARNINGS + 1))
fi

echo ""

# ============================================
# SUMMARY
# ============================================
echo "========================================="
echo "VALIDATION SUMMARY"
echo "========================================="
echo "File: $IPLAN_FILE"
echo "Script Version: ${SCRIPT_VERSION}"
echo "IPLAN ID: ${IPLAN_ID:-unknown}"
echo "Phases: ${phase_count:-0}"
echo "Tasks: ${checkbox_count:-0}"
echo "Bash Blocks: ${bash_count:-0}"
echo "Tags: ${tag_count:-0}"
echo "File Size: ${file_kb:-0}KB"
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
  echo -e "${GREEN}✅ PASSED: All validation checks passed${NC}"
  echo ""
  echo "Document complies with:"
  echo "  - IPLAN-TEMPLATE.md structure"
  echo "  - AI Dev Flow SDD framework requirements"
  echo "  - Layer 12 artifact standards"
  echo "  - Session-based execution requirements"
  exit 0
elif [ $ERRORS -eq 0 ]; then
  echo -e "${YELLOW}⚠️  PASSED WITH WARNINGS: Document valid but has $WARNINGS warnings${NC}"
  echo ""
  echo "Recommendations:"
  echo "  - Review warnings for quality improvements"
  echo "  - See IPLAN-TEMPLATE.md for best practices"
  echo "  - Ensure bash commands use absolute paths"
  exit 0
else
  echo -e "${RED}❌ FAILED: $ERRORS critical errors found${NC}"
  echo ""
  echo "Action Required:"
  echo "  1. Fix all errors listed above"
  echo "  2. Review IPLAN-TEMPLATE.md for requirements"
  echo "  3. Check IPLAN_CREATION_RULES.md for standards"
  echo "  4. Ensure all 9 mandatory traceability tags present"
  echo "  5. Re-run validation: ./scripts/validate_iplan.sh $IPLAN_FILE"
  exit 1
fi
