#!/bin/bash
# REQ Template Validator v3.0
# Validates REQ documents against:
# - REQ-TEMPLATE-V3.md (primary template - authoritative)
# - AI Dev Flow SDD framework standards
# - Cumulative tagging hierarchy (Layer 7: 6 required tags)
# Usage: ./validate_req_template.sh <REQ_FILE>

set -e

REQ_FILE=$1
ERRORS=0
WARNINGS=0
SCRIPT_VERSION="3.0.0"

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
echo "Template: REQ-TEMPLATE-V3.md + AI Dev Flow framework"
echo ""

# ============================================
# CHECK 1: Required Sections
# ============================================
echo "CHECK 1: Required Sections"
echo "-----------------------------------------"

# Detect profile
PROFILE="standard"
if grep -q "template_profile: mvp" "$REQ_FILE"; then
  PROFILE="mvp"
  echo "  ℹ️  MVP Profile detected"
fi

required_sections_standard=(
  "## 1. Description"
  "## 2. Functional Requirements"
  "## 3. Interface Specifications"
  "## 4. Data Schemas"
  "## 5. Error Handling Specifications"
  "## 6. Configuration Specifications"
  "## 7. Quality Attributes"
  "## 8. Implementation Guidance"
  "## 9. Acceptance Criteria"
  "## 10. Verification Methods"
  "## 11. Traceability"
  "## 12. Change History"
)

required_sections_mvp=(
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

if [ "$PROFILE" = "mvp" ]; then
  required_sections=("${required_sections_mvp[@]}")
else
  required_sections=("${required_sections_standard[@]}")
fi

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
  "| \*\*Priority\*\* |"
  "| \*\*Source Document\*\* |"
  "| \*\*SPEC-Ready Score\*\* |"
  "| \*\*Template Version\*\* |"
)

field_names=(
  "Status"
  "Version"
  "Date Created"
  "Last Updated"
  "Priority"
  "Source Document"
  "SPEC-Ready Score"
  "Template Version"
)

for i in "${!required_fields[@]}"; do
  if grep -q "${required_fields[$i]}" "$REQ_FILE"; then
    echo "  ✅ Found: ${field_names[$i]}"
  else
    echo "  ❌ MISSING: ${field_names[$i]}"
    ((ERRORS++))
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

echo ""

# ============================================
# CHECK 9: Template Version
# ============================================
echo "CHECK 9: Template Version"
echo "-----------------------------------------"

template_version=$(grep "| \*\*Template Version\*\* |" "$REQ_FILE" | sed 's/.*| \(.*\) |.*/\1/' | xargs)

if [ "$template_version" = "2.0" ]; then
  echo "  ✅ Template Version is 2.0"
elif [ "$template_version" = "1.0" ]; then
  echo "  ✅ Template Version is 1.0"
else
  echo "  ⚠️  WARNING: Template Version is '$template_version' (expected 1.0 or 2.0)"
  ((WARNINGS++))
fi

echo ""

# ============================================
# CHECK 10: Change History
# ============================================
echo "CHECK 10: Change History"
echo "-----------------------------------------"

# Skip Change History check for MVP if not present, or enforce relaxed rule
if [ "$PROFILE" = "mvp" ]; then
  if grep -q "## .*Change History" "$REQ_FILE"; then
     # Use standard check logic if section exists
     check_history=true
  else
     echo "  ℹ️  MVP Profile: Skipping Change History check (optional)"
     check_history=false
  fi
else
  check_history=true
fi

if [ "$check_history" = "true" ]; then
  # Count change history entries (rows in the table)
  change_count=$(grep -A 100 "## .*Change History" "$REQ_FILE" | grep "^|.*|.*|.*|.*|$" | grep -v "^| Date " | grep -v "^|---" | wc -l)

  if [ "$change_count" -gt 0 ]; then
    echo "  ✅ Change History has $change_count entries"

    # Check if latest change matches current version
    latest_change_version=$(grep -A 100 "## .*Change History" "$REQ_FILE" | grep "^|.*|.*|.*|.*|$" | grep -v "^| Date " | grep -v "^|---" | head -1 | awk -F'|' '{print $3}' | xargs)

    if [ "$latest_change_version" = "$version" ]; then
      echo "  ✅ Latest change history entry matches current version: $version"
    else
      echo "  ⚠️  WARNING: Latest change history version ($latest_change_version) doesn't match document version ($version)"
      ((WARNINGS++))
    fi
  else
    echo "  ❌ MISSING: Change History entries"
    ((ERRORS++))
  fi
fi

echo ""

# ============================================
# CHECK 11: Filename/ID Format Validation
# ============================================
echo "CHECK 11: Filename/ID Format Validation"
echo "-----------------------------------------"

filename=$(basename "$REQ_FILE")

# Pattern: REQ-NN or REQ-NN-YY_{slug}.md
if [[ $filename =~ ^REQ-[0-9]{2,}(-[0-9]{2,3})?_[a-z0-9_]+\.md$ ]]; then
  echo "  ✅ Filename format valid: $filename"

  # Extract ID from filename
  file_id=$(echo "$filename" | sed -E 's/^(REQ-[0-9]{2,}(-[0-9]{2,3})?)_.*/\1/')

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
# CHECK 12: Resource Tag Validation (Template 2.0)
# ============================================
echo "CHECK 12: Resource Tag Validation (Template 2.0)"
echo "-----------------------------------------"

if [ "$template_version" = "2.0" ]; then
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
    echo "  ❌ ERROR: Template 2.0 requires [RESOURCE_INSTANCE] tag in H1"
    echo "           Current H1: $h1_line"
    echo "           Expected: # REQ-NN: [TAG] Title"
    echo "           Valid tags: [EXTERNAL_SERVICE_GATEWAY], [HEALTH_CHECK_SERVICE], etc."
    ((ERRORS++))
  fi
else
  echo "  ℹ️  Template 1.0: Resource tag not required (skip)"
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

  # Validate tag format: @artifact-type: DOCUMENT-ID:REQUIREMENT-ID
  while IFS= read -r tag_line; do
    if ! [[ $tag_line =~ ^@(brd|prd|ears|bdd|adr|sys):[[:space:]][A-Z]+-[0-9]{2,}(-[0-9]{2,3})?(:[A-Z0-9_-]+)? ]]; then
      echo "  ❌ ERROR: Invalid tag format: $tag_line"
      echo "           Expected: @type: DOC-ID:REQ-ID"
      echo "           Example: @brd: BRD.09.01.15"
      ((tag_format_errors++))
    fi
  done < <(grep -E '^@(brd|prd|ears|bdd|adr|sys):' "$REQ_FILE")

  if [[ $tag_format_errors -gt 0 ]]; then
    ((ERRORS += tag_format_errors))
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
  set -e

  if [ $found -eq 0 ]; then
    echo "  ✅ Found: $type upstream source"
  else
    missing_upstream+=("$type")
  fi
done

if [[ ${#missing_upstream[@]} -gt 0 ]]; then
  echo "  ❌ ERROR: Incomplete upstream chain - missing: ${missing_upstream[*]}"
  echo "           Complete chain required: BRD → PRD → EARS → BDD → ADR → SYS"
  echo "           Reference: REQ-TEMPLATE-UNIFIED.md Section 15 (RULE 2)"
  ((ERRORS++))
else
  echo "  ✅ Complete upstream traceability chain (all 6 layers)"
fi

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
  if grep -q "### Traceability Matrix\|### 11.4\|## 11.4" "$REQ_FILE"; then
    echo "  ✅ Traceability Matrix section found (complex REQ)"
    echo "     Upstream sources: $upstream_count, Sub-components: $has_subcomponents"
  else
    echo "  ⚠️  WARNING: Complex REQ detected but Section 11.4 (Traceability Matrix) missing"
    echo "           Upstream sources: $upstream_count (≥5 suggests complexity)"
    echo "           Sub-components: $has_subcomponents"
    echo "           Recommendation: Add Section 11.4 or create separate REQ-NN_TRACEABILITY_MATRIX.md"
    echo "           Reference: REQ-TEMPLATE-UNIFIED.md Section 11.4"
    ((WARNINGS++))
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

  # Section 3: Interface Specifications
  if grep -qE "class.*Protocol|class.*ABC|from typing import Protocol|from abc import.*ABC" "$REQ_FILE"; then
    echo "  ✅ Section 3: Protocol/ABC class found"
  else
    echo "  ⚠️  WARNING: SPEC-Ready ≥90% but no Protocol/ABC class in Section 3"
    ((content_warnings++))
  fi

  # Section 4: Data Schemas
  if grep -qE "BaseModel|@dataclass|from pydantic import|from dataclasses import dataclass" "$REQ_FILE"; then
    echo "  ✅ Section 4: Pydantic/dataclass models found"
  else
    echo "  ⚠️  WARNING: SPEC-Ready ≥90% but no Pydantic/dataclass models in Section 4"
    ((content_warnings++))
  fi

  # Section 5: Error Handling
  if grep -qE "Exception.*Error|class.*Error|raise.*Error" "$REQ_FILE"; then
    echo "  ✅ Section 5: Exception definitions found"
  else
    echo "  ⚠️  WARNING: SPEC-Ready ≥90% but no exception definitions in Section 5"
    ((content_warnings++))
  fi

  # Section 6: Configuration
  if grep -qE "\`\`\`yaml|\`\`\`yml" "$REQ_FILE"; then
    echo "  ✅ Section 6: YAML configuration found"
  else
    echo "  ⚠️  WARNING: SPEC-Ready ≥90% but no YAML configuration in Section 6"
    ((content_warnings++))
  fi

  if [ $content_warnings -gt 0 ]; then
    echo "  ⚠️  SPEC-Ready content validation: $content_warnings warnings"
    echo "           Score may be inaccurate - verify Sections 3-6 completeness"
    ((WARNINGS += content_warnings))
  else
    echo "  ✅ SPEC-Ready content validation complete - all critical sections present"
  fi
else
  echo "  ℹ️  SPEC-Ready score <90% - content validation skipped"
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
  echo "  - REQ-TEMPLATE-UNIFIED.md"
  echo "  - doc-flow SDD framework"
  echo "  - Cumulative tagging hierarchy (Layer 7)"
  exit 0
elif [ $ERRORS -eq 0 ]; then
  echo "⚠️  PASSED WITH WARNINGS: Document valid but has $WARNINGS warnings"
  echo ""
  echo "Recommendations:"
  echo "  - Review warnings for quality improvements"
  echo "  - See REQ-TEMPLATE-UNIFIED.md for best practices"
  exit 0
else
  echo "❌ FAILED: $ERRORS critical errors found"
  echo ""
  echo "Action Required:"
  echo "  1. Fix all errors listed above"
  echo "  2. Review REQ-TEMPLATE-UNIFIED.md for requirements"
  echo "  3. Check doc-flow TRACEABILITY.md for tagging rules"
  echo "  4. Re-run validation: ./scripts/validate_req_template.sh $REQ_FILE"
  exit 1
fi
