#!/bin/bash
# REQ Template Validator v3.0
# Validates REQ documents against:
# - REQ-TEMPLATE-V3.md (primary template - authoritative)
# - AI Dev Flow SDD framework standards
# - Cumulative tagging hierarchy (Layer 7: 6 required tags)
# Usage: ./validate_req_template.sh <REQ_FILE>

# set -e (disabled to prevent exit on arithmetic ((VAR++)) when VAR=0)

REQ_FILE=$1
ERRORS=0
WARNINGS=0
SCRIPT_VERSION="3.0.1"

if [ -z "$REQ_FILE" ]; then
  echo "Usage: $0 <REQ_FILE>"
  echo "Example: $0 /opt/data/ibmcp/docs/REQ/api/ib/REQ-02_connection_heartbeat_monitoring.md"
  exit 1
fi

if [ ! -f "$REQ_FILE" ]; then
  echo "❌ File not found: $REQ_FILE"
  exit 1
fi

echo "========================================="
echo "REQ Template Validator v${SCRIPT_VERSION}"
echo "========================================="
echo "File: $REQ_FILE"
echo "Template: REQ-MVP-TEMPLATE (MVP-only profile)"
echo ""

# ============================================
# CHECK 1: Required Sections
# ============================================
echo "CHECK 1: Required Sections"
echo "-----------------------------------------"

required_sections=(
  "## 1. Document Control"
  "## 2. Requirement Description"
  "## 3. Functional Specification"
  "## 4. Interface Definition"
  "## 5. Error Handling"
  "## 6. Quality Attributes"
  "## 7. Configuration"
  "## 8. Testing Requirements"
  "## 9. Acceptance Criteria"
  "## 10. Traceability"
  "## 11. Implementation Notes"
)

for section in "${required_sections[@]}"; do
  if grep -q "^$section" "$REQ_FILE"; then
    echo "  ✅ Found: $section"
  else
    echo "  ❌ MISSING: $section"
    ((ERRORS++))
  fi
done

echo ""

# ============================================
# CHECK 2: Document Control Fields
# ============================================
echo "CHECK 2: Document Control Fields"
echo "-----------------------------------------"

required_fields=(
  "| \*\*Status\*\* |"
  "| \*\*Version\*\* |"
  "| \*\*Date Created\*\* |"
  "| \*\*Last Updated\*\* |"
  "| \*\*Author\*\* |"
  "| \*\*Priority\*\* |"
  "| \*\*Category\*\* |"
  "| \*\*Infrastructure Type\*\* |"
  "| \*\*Source Document\*\* |"
  "| \*\*Verification Method\*\* |"
  "| \*\*Assigned Team\*\* |"
  "| \*\*SPEC-Ready Score\*\* |"
)

optional_fields=(
  "| \*\*CTR-Ready Score\*\* |"
  "| \*\*Template Version\*\* |"
)

field_names=(
  "Status"
  "Version"
  "Date Created"
  "Last Updated"
  "Author"
  "Priority"
  "Category"
  "Infrastructure Type"
  "Source Document"
  "Verification Method"
  "Assigned Team"
  "SPEC-Ready Score"
)

for i in "${!required_fields[@]}"; do
  if grep -q "${required_fields[$i]}" "$REQ_FILE"; then
    echo "  ✅ Found: ${field_names[$i]}"
  else
    echo "  ❌ MISSING: ${field_names[$i]}"
    ((ERRORS++))
  fi
done

for opt in "${optional_fields[@]}"; do
  if grep -q "$opt" "$REQ_FILE"; then
    echo "  ℹ️  Found optional: $opt"
  fi
done

echo ""

# ============================================
# CHECK 3: Traceability Structure
# ============================================
echo "CHECK 3: Traceability Structure"
echo "-----------------------------------------"

if grep -q "### .*Upstream Sources" "$REQ_FILE"; then
  echo "  ✅ Found: Upstream Sources subsection"
else
  echo "  ❌ MISSING: Upstream Sources subsection in Section 11"
  ((ERRORS++))
fi

if grep -q "### .*Downstream Artifacts" "$REQ_FILE"; then
  echo "  ✅ Found: Downstream Artifacts subsection"
else
  echo "  ⚠️  WARNING: Downstream Artifacts subsection recommended"
  ((WARNINGS++))
fi

if grep -q "### .*Code Implementation Paths" "$REQ_FILE"; then
  echo "  ✅ Found: Code Implementation Paths subsection"
else
  echo "  ⚠️  WARNING: Code Implementation Paths subsection recommended"
  ((WARNINGS++))
fi

echo ""

# ============================================
# CHECK 4: Version Format Validation
# ============================================
echo "CHECK 4: Version Format Validation"
echo "-----------------------------------------"

# Extract version from document
version=$(grep "| \*\*Version\*\* |" "$REQ_FILE" | sed 's/.*| \([0-9.]*\) |.*/\1/')

if [[ $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "  ✅ Version format valid: $version (semver X.Y.Z)"
else
  echo "  ❌ INVALID version format: '$version' (expected X.Y.Z)"
  ((ERRORS++))
fi

echo ""

# ============================================
# CHECK 5: Date Format Validation
# ============================================
echo "CHECK 5: Date Format Validation"
echo "-----------------------------------------"

# Extract dates
date_created=$(grep "| \*\*Date Created\*\* |" "$REQ_FILE" | sed 's/.*| \([0-9-]*\) |.*/\1/')
date_updated=$(grep "| \*\*Last Updated\*\* |" "$REQ_FILE" | sed 's/.*| \([0-9-]*\) |.*/\1/')

if [[ $date_created =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  echo "  ✅ Date Created format valid: $date_created"
else
  echo "  ❌ INVALID Date Created format: '$date_created' (expected YYYY-MM-DD)"
  ((ERRORS++))
fi

if [[ $date_updated =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  echo "  ✅ Last Updated format valid: $date_updated"
else
  echo "  ❌ INVALID Last Updated format: '$date_updated' (expected YYYY-MM-DD)"
  ((ERRORS++))
fi

# Compare dates
if [[ "$date_updated" < "$date_created" ]]; then
  echo "  ❌ ERROR: Last Updated ($date_updated) is before Date Created ($date_created)"
  ((ERRORS++))
fi

echo ""

# ============================================
# CHECK 6: Priority Format Validation
# ============================================
echo "CHECK 6: Priority Format Validation"
echo "-----------------------------------------"

priority_line=$(grep "| \*\*Priority\*\* |" "$REQ_FILE")

if echo "$priority_line" | grep -qE "(Critical|High|Medium|Low) \(P[1-4]\)"; then
  echo "  ✅ Priority format valid (includes P-level)"
else
  echo "  ⚠️  WARNING: Priority should include P-level: Critical (P1), High (P2), Medium (P3), Low (P4)"
  ((WARNINGS++))
fi

echo ""

# ============================================
# CHECK 7: Source Document Format
# ============================================
echo "CHECK 7: Source Document Format"
echo "-----------------------------------------"

source_doc=$(grep "| \*\*Source Document\*\* |" "$REQ_FILE" | sed 's/.*| \(.*\) |.*/\1/')

if echo "$source_doc" | grep -qE "[A-Z]+-[0-9]+ Section [0-9]"; then
  echo "  ✅ Source Document format valid: $source_doc"
else
  echo "  ⚠️  WARNING: Source Document should include section number (e.g., 'SYS-02 Section 3.1.1')"
  ((WARNINGS++))
fi

echo ""

# ============================================
# CHECK 8: SPEC-Ready Score
# ============================================
echo "CHECK 8: SPEC-Ready Score"
echo "-----------------------------------------"

spec_ready_line=$(grep "| \*\*SPEC-Ready Score\*\* |" "$REQ_FILE")

if echo "$spec_ready_line" | grep -qE "✅.*[0-9]+%"; then
  score=$(echo "$spec_ready_line" | grep -oE "[0-9]+%" | head -1 | tr -d '%')
  if [ "$score" -ge 90 ]; then
    echo "  ✅ SPEC-Ready Score ≥ 90%: $score%"
  else
    echo "  ⚠️  WARNING: SPEC-Ready Score below 90%: $score%"
    ((WARNINGS++))
  fi
else
  echo "  ❌ MISSING: SPEC-Ready Score with ✅ emoji and percentage"
  ((ERRORS++))
fi

# ============================================
# CHECK 8b: CTR-Ready Score
# ============================================
echo "CHECK 8b: CTR-Ready Score"
echo "-----------------------------------------"

ctr_ready_line=$(grep "| \*\*CTR-Ready Score\*\* |" "$REQ_FILE")

if [ -n "$ctr_ready_line" ]; then
  if echo "$ctr_ready_line" | grep -qE "✅.*[0-9]+%"; then
    ctr_score=$(echo "$ctr_ready_line" | grep -oE "[0-9]+%" | head -1 | tr -d '%')
    if [ "$ctr_score" -ge 90 ]; then
      echo "  ✅ CTR-Ready Score ≥ 90%: $ctr_score%"
    else
      echo "  ⚠️  WARNING: CTR-Ready Score below 90%: $ctr_score%"
      ((WARNINGS++))
    fi
  else
    echo "  ⚠️  WARNING: CTR-Ready Score present but format invalid (expected ✅ XX%)"
    ((WARNINGS++))
  fi
else
  echo "  ℹ️  CTR-Ready Score not provided (optional for MVP)"
fi

echo ""

# ============================================
# CHECK 9: Template Version
# ============================================
echo "CHECK 9: Template Version"
echo "-----------------------------------------"

template_version=$(grep "| \*\*Template Version\*\* |" "$REQ_FILE" | sed 's/.*| \(.*\) |.*/\1/' | xargs)

if [ -n "$template_version" ]; then
  if [ "$template_version" = "1.1" ]; then
    echo "  ✅ Template Version is 1.1"
  else
    echo "  ⚠️  WARNING: Template Version is '$template_version' (expected 1.1 for MVP)"
    ((WARNINGS++))
  fi
else
  echo "  ℹ️  Template Version not provided (optional for MVP)"
fi

echo ""

# ============================================
# CHECK 10: Change History
# ============================================
echo "CHECK 10: Change History"
echo "-----------------------------------------"
echo "  ℹ️  Change History is not included in MVP 11-section format; skipping"

echo ""

# ============================================
# CHECK 11: Filename/ID Format Validation
# ============================================
echo "CHECK 11: Filename/ID Format Validation"
echo "-----------------------------------------"

filename=$(basename "$REQ_FILE")

# Pattern: REQ-NN or REQ-NN-YY_{slug}.md or REQ-NN.YY_{slug}.md
if [[ $filename =~ ^REQ-[0-9]{2,}([-.][0-9]{2,3})?_[a-z0-9_]+\.md$ ]]; then
  echo "  ✅ Filename format valid: $filename"

  # Extract ID from filename
  file_id=$(echo "$filename" | sed -E 's/^(REQ-[0-9]{2,}([-.][0-9]{2,3})?)_.*/\1/')

  # Check H1 header matches
  h1_header=$(grep -m1 "^# REQ-" "$REQ_FILE" || echo "")
  if echo "$h1_header" | grep -qE "^# ${file_id}:"; then
    echo "  ✅ H1 header ID matches filename: $file_id"
  else
    echo "  ❌ ERROR: H1 header ID doesn't match filename"
    echo "           Filename ID: $file_id"
    echo "           H1 Header: $h1_header"
    ((ERRORS++))
  fi
else
  echo "  ❌ ERROR: Invalid filename format: $filename"
  echo "           Expected: REQ-NN_{slug}.md or REQ-NN-YY_{slug}.md"
  echo "           Example: REQ-02_connection_heartbeat.md"
  ((ERRORS++))
fi

echo ""

# ============================================
# CHECK 12: Resource Tag Validation (Template 1.1)
# ============================================
echo "CHECK 12: Resource Tag Validation"
echo "-----------------------------------------"

if [ "$template_version" = "1.1" ]; then
  h1_line=$(grep -m1 "^# REQ-" "$REQ_FILE")

  # Check for resource tag pattern [TAG_NAME]
  if echo "$h1_line" | grep -q '\['; then
    # Extract resource tag using sed (pattern: [RESOURCE_INSTANCE])
    resource_tag=$(echo "$h1_line" | sed -n 's/.*\(\[[^]]*\]\).*/\1/p')
    if [ -n "$resource_tag" ]; then
      echo "  ✅ Resource tag found in H1 header: $resource_tag"
    else
      echo "  ❌ ERROR: Failed to extract resource tag from H1"
      echo "           Current H1: $h1_line"
      ((ERRORS++))
    fi
  else
    echo "  ❌ ERROR: Template 1.1 requires [RESOURCE_INSTANCE] tag in H1"
    echo "           Current H1: $h1_line"
    echo "           Expected: # REQ-NN: [TAG] Title"
    echo "           Valid tags: [EXTERNAL_SERVICE_GATEWAY], [HEALTH_CHECK_SERVICE], etc."
    ((ERRORS++))
  fi
else
  echo "  ℹ️  Resource tag check skipped (Template Version not 1.1)"
fi

echo ""

# ============================================
# CHECK 13: Cumulative Tagging Hierarchy (Layer 7)
# ============================================
echo "CHECK 13: Cumulative Tagging Hierarchy (Layer 7)"
echo "-----------------------------------------"

required_tags=("@brd" "@prd" "@ears" "@bdd" "@adr" "@sys")
missing_tags=()
tag_format_errors=0

# Check all 6 tags present (Layer 7 requirement)
for tag in "${required_tags[@]}"; do
  # Disable set -e for this grep (it's OK if no match found)
  set +e
  grep -qE "^${tag}:" "$REQ_FILE"
  found=$?
  set -e

  if [ $found -ne 0 ]; then
    missing_tags+=("$tag")
  fi
done

if [[ ${#missing_tags[@]} -gt 0 ]]; then
  echo "  ❌ ERROR: Missing cumulative tags (Layer 7 requires all 6):"
  echo "           Missing: ${missing_tags[*]}"
  echo "           Required: @brd, @prd, @ears, @bdd, @adr, @sys"
  echo "           Reference: doc-flow TRACEABILITY.md Section 2.5"
  ((ERRORS++))
else
  echo "  ✅ All 6 cumulative tags present"

  # Validate tag format: @artifact-type: DOCUMENT-ID:REQUIREMENT-ID (supports dot notation)
  while IFS= read -r tag_line; do
    if ! [[ $tag_line =~ ^@(brd|prd|ears|bdd|adr|sys):[[:space:]]([A-Z]+-[0-9]{2,}|[A-Z]+\.[0-9]{2,}(\.[0-9]+)*)(:[A-Z0-9_-]+)? ]]; then
      echo "  ❌ ERROR: Invalid tag format: $tag_line"
      echo "           Expected: @type: DOC-ID:REQ-ID"
      echo "           Example: @brd: BRD.09.01.15"
      ((tag_format_errors++)) || true
    fi
  done < <(grep -E '^@(brd|prd|ears|bdd|adr|sys):' "$REQ_FILE")

  if [[ $tag_format_errors -gt 0 ]]; then
    ((ERRORS += tag_format_errors)) || true
  else
    echo "  ✅ All tag formats valid (@type: DOC-ID:REQ-ID)"
  fi
fi

echo ""

# ============================================
# CHECK 14: Complete Upstream Chain (6 Layers)
# ============================================
echo "CHECK 14: Complete Upstream Chain (6 Layers)"
echo "-----------------------------------------"

required_upstream=("BRD" "PRD" "EARS" "BDD" "ADR" "SYS")
missing_upstream=()

for type in "${required_upstream[@]}"; do
  # Disable set -e for this grep (it's OK if no match found)
  set +e
  grep -qE "^\| ${type} \|" "$REQ_FILE"
  found=$?
  # set -e (disabled)

  if [ $found -eq 0 ]; then
    echo "  ✅ Found: $type upstream source"
  else
    missing_upstream+=("$type")
  fi
done

if [[ ${#missing_upstream[@]} -gt 0 ]]; then
  echo "  ❌ ERROR: Incomplete upstream chain - missing: ${missing_upstream[*]}"
  echo "           Complete chain required: BRD → PRD → EARS → BDD → ADR → SYS"
  echo "           Reference: REQ-MVP-TEMPLATE.md Section 15 (RULE 2)"
  ((ERRORS++)) || true
else
  echo "  ✅ Complete upstream traceability chain (all 6 layers)"
fi

echo "DEBUG: Check 14 completed, starting Check 15..."
echo ""

# ============================================
# CHECK 15: Markdown Link Resolution
# ============================================
echo "CHECK 15: Markdown Link Resolution"
echo "-----------------------------------------"

base_dir="$(dirname "$REQ_FILE")"
broken_links=0
checked_links=0

# Extract all markdown links: [text](path)
while IFS= read -r link; do
  # Extract path from link
  path=$(echo "$link" | sed -E 's/.*\(([^)]+)\).*/\1/')

  # Skip external URLs
  if [[ "$path" =~ ^https?:// ]]; then
    continue
  fi

  # Extract file and anchor parts
  file_part="${path%%#*}"
  anchor_part="${path#*#}"

  # Skip if no file part (just anchor or empty)
  if [ -z "$file_part" ]; then
    continue
  fi

  ((checked_links++))

  # Resolve relative path
  resolved_path="$(cd "$base_dir" && realpath -m "$file_part" 2>/dev/null || echo "INVALID")"

  if [ ! -f "$resolved_path" ]; then
    echo "  ❌ ERROR: Broken link - file not found"
    echo "           Link: $path"
    echo "           Resolved: $resolved_path"
    ((broken_links++))
  elif [ "$anchor_part" != "$path" ] && [ -n "$anchor_part" ]; then
    # Validate anchor exists (check for header with ID)
    if ! grep -qE "^#{1,6} ${anchor_part}:|^#{1,6} .*${anchor_part}" "$resolved_path"; then
      echo "  ⚠️  WARNING: Anchor possibly missing in $(basename "$file_part"): #$anchor_part"
      ((WARNINGS++))
    fi
  fi
done < <(grep -oE '\[.*?\]\([^)]+\)' "$REQ_FILE" || true)

if [ $broken_links -gt 0 ]; then
  echo "  ❌ Found $broken_links broken links (checked $checked_links links)"
  ((ERRORS += broken_links))
elif [ $checked_links -gt 0 ]; then
  echo "  ✅ All markdown links resolve correctly ($checked_links links checked)"
else
  echo "  ℹ️  No markdown links found in document"
fi

echo ""

# ============================================
# CHECK 16: Traceability Matrix (Complex REQs)
# ============================================
echo "CHECK 16: Traceability Matrix (Complex REQs)"
echo "-----------------------------------------"

# Count upstream sources
upstream_count=$(grep -E "^\| (BRD|PRD|EARS|BDD|ADR|SYS) \|" "$REQ_FILE" | wc -l)

# Check for complex requirement indicators
has_subcomponents=$(grep -qE "REQ-[0-9]{2,}:[A-Z]+-[0-9]+" "$REQ_FILE" && echo "yes" || echo "no")

if [ "$upstream_count" -ge 5 ] || [ "$has_subcomponents" = "yes" ]; then
if grep -q "### .*Traceability Matrix\|### 11.4\|## 11.4\|### 10.4\|## 10.4" "$REQ_FILE"; then
    echo "  ✅ Traceability Matrix section found (complex REQ)"
    echo "     Upstream sources: $upstream_count, Sub-components: $has_subcomponents"
  else
    echo "  ⚠️  WARNING: Complex REQ detected but Section 11.4 (Traceability Matrix) missing"
    echo "           Upstream sources: $upstream_count (≥5 suggests complexity)"
    echo "           Sub-components: $has_subcomponents"
    echo "           Recommendation: Add Section 11.4 or create separate REQ-NN_TRACEABILITY_MATRIX.md"
    echo "           Reference: REQ-MVP-TEMPLATE.md Section 11.4"
    ((WARNINGS++)) || true
  fi
else
  echo "  ℹ️  Simple REQ - Traceability Matrix optional"
  echo "     Upstream sources: $upstream_count, Sub-components: $has_subcomponents"
fi

echo ""

# ============================================
# CHECK 17: SPEC-Ready Content Validation
# ============================================
echo "CHECK 17: SPEC-Ready Content Validation"
echo "-----------------------------------------"

if [ -n "$score" ] && [ "$score" -ge 90 ]; then
  echo "  Validating SPEC-Ready content for score ${score}%..."

  content_warnings=0

  # Section 3.4: Interface Protocol
  if grep -qE "class.*Protocol|class.*ABC|from typing import Protocol|from abc import.*ABC" "$REQ_FILE"; then
    echo "  ✅ Section 3.4: Protocol/ABC class found"
  else
    echo "  ❌ ERROR: SPEC-Ready ≥90% but no Protocol/ABC class in Section 3.4"
    ((content_warnings++))
  fi

  # Section 4: Data Schemas
  if grep -qE "BaseModel|@dataclass|from pydantic import|from dataclasses import dataclass" "$REQ_FILE"; then
    echo "  ✅ Section 4: Pydantic/dataclass models found"
  else
    echo "  ❌ ERROR: SPEC-Ready ≥90% but no Pydantic/dataclass models in Section 4"
    ((content_warnings++))
  fi

  # Section 5.3: Exception Definitions
  if grep -qE "class.*Error\(.*Exception\)|class.*Error\(.*Error\)" "$REQ_FILE"; then
    echo "  ✅ Section 5.3: Exception definitions found"
  else
    echo "  ❌ ERROR: SPEC-Ready ≥90% but no exception definitions in Section 5.3"
    ((content_warnings++))
  fi

  # Section 7.3: Configuration Schema
  if grep -qE "\`\`\`yaml|\`\`\`yml" "$REQ_FILE"; then
    if grep -q "### .*Configuration Schema" "$REQ_FILE" || grep -q "7.3 Configuration Schema" "$REQ_FILE"; then
       echo "  ✅ Section 7.3: YAML configuration found"
    else
       # Fallback for old templates if yaml exists but not explicitly in 7.3
       echo "  ⚠️  WARNING: YAML configuration found but not in Section 7.3"
    fi
  else
    echo "  ❌ ERROR: SPEC-Ready ≥90% but no YAML configuration in Section 7.3"
    ((content_warnings++))
  fi

  if [ $content_warnings -gt 0 ]; then
    echo "  ❌ SPEC-Ready content validation: $content_warnings ERRORS"
    echo "           Required: Protocol/ABC, Pydantic Models, Exceptions, YAML Config"
    ((ERRORS += content_warnings))
  else
    echo "  ✅ SPEC-Ready content validation complete - all critical sections present"
  fi
else
  echo "  ℹ️  SPEC-Ready score <90% - content validation skipped"
fi

# ============================================
# CHECK 21: Unit Tests Table Validation
# ============================================
echo "CHECK 21: Unit Tests Table Validation"
echo "-----------------------------------------"

if [ "$PROFILE" = "mvp" ]; then
  # Check if Section 8.1 Unit Tests title exists
  if grep -q "### 8.1 Unit Tests" "$REQ_FILE"; then
    echo "  ✅ Found: Section 8.1 Unit Tests title"
    
    # Check for table structure (pipes and hyphens)
    if grep -q "| Test Case | Input | Expected Output | Coverage |" "$REQ_FILE"; then
       echo "  ✅ Found: Unit Tests table structure"
       
       # Count table rows (excluding header and separator) in Section 8.1
       # Extract lines between 8.1 and 8.2 (or end of file)
       section_content=$(sed -n '/### 8.1 Unit Tests/,/^### 8.2/p' "$REQ_FILE")
       
       # Count rows starting with |, excluding header/sep
       row_count=$(echo "$section_content" | grep "^|" | grep -v "Test Case" | grep -v "\-\-\-" | wc -l)
       
       if [ "$row_count" -ge 3 ]; then
         echo "  ✅ Found: $row_count Unit Test entries (min 3)"
         
         # Check for category prefixes
         if echo "$section_content" | grep -qE "\[Logic\]|\[State\]|\[Validation\]|\[Edge\]"; then
           echo "  ✅ Found: Category prefixes ([Logic], [State], etc.)"
         else
           echo "  ⚠️  WARNING: Unit Tests entries missing category prefix [Logic/State/Validation/Edge]"
           ((WARNINGS++))
         fi
       else
         echo "  ⚠️  WARNING: Unit Tests table has < 3 entries (found: $row_count, required: ≥3)"
         ((WARNINGS++))
       fi
    else
       echo "  ⚠️  WARNING: Unit Tests table missing required columns: Test Case | Input | Expected Output | Coverage"
       ((WARNINGS++))
    fi
  else
    echo "  ⚠️  WARNING: Section 8.1 missing 'Unit Tests' title - drives SPEC interface design"
    ((WARNINGS++))
  fi
else
  echo "  ℹ️  Standard Profile: Skipping Unit Tests check"
fi

echo ""

# ============================================
# SUMMARY
# ============================================
echo "========================================="
echo "VALIDATION SUMMARY"
echo "========================================="
echo "File: $REQ_FILE"
echo "Script Version: ${SCRIPT_VERSION}"
echo "Template Version: ${template_version}"
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
  echo "✅ PASSED: All validation checks passed with no warnings"
  echo ""
  echo "Document complies with:"
  echo "  - REQ-MVP-TEMPLATE.md"
  echo "  - doc-flow SDD framework"
  echo "  - Cumulative tagging hierarchy (Layer 7)"
  exit 0
elif [ $ERRORS -eq 0 ]; then
  echo "⚠️  PASSED WITH WARNINGS: Document valid but has $WARNINGS warnings"
  echo ""
  echo "Recommendations:"
  echo "  - Review warnings for quality improvements"
  echo "  - See REQ-MVP-TEMPLATE.md for best practices"
  exit 0
else
  echo "❌ FAILED: $ERRORS critical errors found"
  echo ""
  echo "Action Required:"
  echo "  1. Fix all errors listed above"
  echo "  2. Review REQ-MVP-TEMPLATE.md for requirements"
  echo "  3. Check doc-flow TRACEABILITY.md for tagging rules"
  echo "  4. Re-run validation: ./scripts/validate_req_template.sh $REQ_FILE"
  exit 1
fi

# ============================================
# ============================================
echo ""
