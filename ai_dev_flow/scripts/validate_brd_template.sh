#!/bin/bash
# BRD Template Validator v1.0
# Validates BRD documents against:
# - BRD-TEMPLATE.md (authoritative template)
# - doc_flow SDD framework standards
# - Platform vs Feature BRD validation rules
# Usage: ./scripts/validate_brd_template.sh <BRD_FILE>

set -e

BRD_FILE=$1
ERRORS=0
WARNINGS=0
SCRIPT_VERSION="1.0.0"

if [ -z "$BRD_FILE" ]; then
  echo "Usage: $0 <BRD_FILE>"
  echo "Example: $0 /opt/data/docs_flow_framework/docs/BRD/BRD-001_platform_architecture.md"
  exit 1
fi

if [ ! -f "$BRD_FILE" ]; then
  echo "❌ File not found: $BRD_FILE"
  exit 1
fi

echo "========================================="
echo "BRD Template Validator v${SCRIPT_VERSION}"
echo "========================================="
echo "File: $BRD_FILE"
echo "Template: BRD-TEMPLATE.md + doc_flow framework"
echo ""

# ============================================
# CHECK 1: Required Sections
# ============================================
echo "CHECK 1: Required Sections"
echo "-----------------------------------------"

required_sections=(
  "## 1. Introduction"
  "## 2. Business Objectives"
  "## 3. Project Scope"
  "## 4. Stakeholders"
  "## 5. Functional Requirements"
  "## 6. Non-Functional Requirements"
  "## 7. Assumptions and Constraints"
  "## 8. Acceptance Criteria"
  "## 9."
  "## 10. Implementation Approach"
  "## 11. Training and Change Management"
  "## 12. Support and Maintenance"
  "## 13. Cost-Benefit Analysis"
  "## 14. Project Governance"
  "## 15. Quality Assurance"
  "## 16. Glossary"
  "## 17. Appendices"
)

for section in "${required_sections[@]}"; do
  if grep -q "^$section" "$BRD_FILE"; then
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
  "| \*\*Project Name\*\* |"
  "| \*\*Document Version\*\* |"
  "| \*\*Date\*\* |"
  "| \*\*Document Owner\*\* |"
  "| \*\*Prepared By\*\* |"
  "| \*\*Status\*\* |"
)

field_names=(
  "Project Name"
  "Document Version"
  "Date"
  "Document Owner"
  "Prepared By"
  "Status"
)

for i in "${!required_fields[@]}"; do
  if grep -q "${required_fields[$i]}" "$BRD_FILE"; then
    echo "  ✅ Found: ${field_names[$i]}"
  else
    echo "  ❌ MISSING: ${field_names[$i]}"
    ((ERRORS++))
  fi
done

echo ""

# ============================================
# CHECK 3: Document Revision History
# ============================================
echo "CHECK 3: Document Revision History"
echo "-----------------------------------------"

if grep -q "### Document Revision History" "$BRD_FILE"; then
  echo "  ✅ Found: Document Revision History subsection"

  # Count revision history entries
  revision_count=$(grep -A 100 "### Document Revision History" "$BRD_FILE" | grep "^|" | grep -v "^|---" | grep -v "^| Date" | wc -l)

  if [ "$revision_count" -gt 0 ]; then
    echo "  ✅ Document Revision History has $revision_count entries"
  else
    echo "  ❌ MISSING: Document Revision History entries"
    ((ERRORS++))
  fi
else
  echo "  ❌ MISSING: Document Revision History subsection"
  ((ERRORS++))
fi

echo ""

# ============================================
# CHECK 4: Filename/ID Format Validation
# ============================================
echo "CHECK 4: Filename/ID Format Validation"
echo "-----------------------------------------"

filename=$(basename "$BRD_FILE")

# Pattern: BRD-NNN or BRD-NNN-YY_{slug}.md
if [[ $filename =~ ^BRD-[0-9]{3,4}(-[0-9]{2,3})?_[a-z0-9_]+\.md$ ]]; then
  echo "  ✅ Filename format valid: $filename"

  # Check if it follows Platform or Feature pattern
  if echo "$filename" | grep -qE "platform|infrastructure"; then
    echo "  ✅ Recognized as Platform BRD pattern"
  elif echo "$filename" | grep -qE "^BRD-[0-9]{3,4}(-[0-9]{2,3})?_[a-z0-9_]+\.md$"; then
    # Additional check to ensure it's not Platform (contains platform/infrastructure keywords)
    if echo "$filename" | grep -qE "_platform_|_infrastructure_"; then
      echo "  ✅ Confirmed Platform BRD"
    else
      echo "  ✅ Recognized as Feature BRD pattern"
    fi
  fi
else
  echo "  ❌ ERROR: Invalid filename format: $filename"
  echo "           Expected: BRD-NNN_descriptive_title.md or BRD-NNN-YY_descriptive_title.md"
  echo "           Platform: BRD-NNN_platform_* or BRD-NNN_infrastructure_*"
  echo "           Feature: BRD-NNN_{feature_name}"
  ((ERRORS++))
fi

echo ""

# ============================================
# CHECK 5: Platform vs Feature BRD Type Validation
# ============================================
echo "CHECK 5: Platform vs Feature BRD Type Validation"
echo "-----------------------------------------"

# Determine BRD type from filename
brd_type=""
if echo "$filename" | grep -qE "_platform_|_infrastructure_"; then
  brd_type="platform"
  echo "  📋 BRD Type: Platform BRD"
elif [[ $filename =~ ^BRD-[0-9]{3,4}(-[0-9]{2,3})?_[a-z0-9_]+\.md$ ]]; then
  brd_type="feature"
  echo "  📋 BRD Type: Feature BRD"
else
  echo "  ❌ ERROR: Cannot determine BRD type from filename"
  ((ERRORS++))
fi

if [ "$brd_type" = "platform" ]; then
  # Platform BRD validation
  if grep -q "## 3.6 Technology Stack Prerequisites" "$BRD_FILE" && grep -qE "## 3.6.*Prerequisites" "$BRD_FILE"; then
    echo "  ✅ Platform BRD: Section 3.6 (Technology Stack Prerequisites) found"
  else
    echo "  ❌ ERROR: Platform BRD missing required Section 3.6 (Technology Stack Prerequisites)"
    ((ERRORS++))
  fi

  if grep -q "## 3.7 Mandatory Technology Conditions" "$BRD_FILE" || grep -q "## 3.7.*Technology Conditions" "$BRD_FILE"; then
    echo "  ✅ Platform BRD: Section 3.7 (Mandatory Technology Conditions) found"
  else
    echo "  ❌ ERROR: Platform BRD missing required Section 3.7 (Mandatory Technology Conditions)"
    ((ERRORS++))
  fi
elif [ "$brd_type" = "feature" ]; then
  # Feature BRD validation - optional technology sections
  if grep -q "## 3.6 Technology Stack Prerequisites" "$BRD_FILE"; then
    echo "  ⚠️  WARNING: Feature BRD has technology section (may reference Platform BRD instead)"
    ((WARNINGS++))
  else
    echo "  ℹ️  Feature BRD: No technology sections (normal for Feature BRDs)"
  fi

  if grep -q "## 3.7 Mandatory Technology Conditions" "$BRD_FILE"; then
    echo "  ⚠️  WARNING: Feature BRD should focus on business conditions, not technology constraints"
    ((WARNINGS++))
  fi
fi

echo ""

# ============================================
# CHECK 6: Architecture Decision Requirements Section
# ============================================
echo "CHECK 6: Architecture Decision Requirements Section"
echo "-----------------------------------------"

if grep -q "## 5.2 Architecture Decision Requirements" "$BRD_FILE"; then
  echo "  ✅ Found: Section 5.2 Architecture Decision Requirements"

  # Check for required table structure
  if grep -q "| Topic Area | Decision Needed | Business Driver | Key Considerations |" "$BRD_FILE"; then
    echo "  ✅ Section 5.2 has required table structure"
  else
    echo "  ❌ ERROR: Section 5.2 missing required table structure (Topic Area, Decision Needed, Business Driver, Key Considerations)"
    ((ERRORS++))
  fi

  # Check for minimum 3 architectural topics
  topic_count=$(grep -A 100 "## 5.2 Architecture Decision Requirements" "$BRD_FILE" | grep "^|" | grep -v "^|---" | grep -v "^| Topic Area " | wc -l)

  if [ "$topic_count" -ge 3 ]; then
    echo "  ✅ Section 5.2 identifies $topic_count architectural topics (≥3 required)"
  else
    echo "  ❌ ERROR: Section 5.2 must identify at least 3 architectural topics (found: $topic_count)"
    ((ERRORS++))
  fi
else
  echo "  ❌ MISSING: Section 5.2 Architecture Decision Requirements"
  ((ERRORS++))
fi

echo ""

# ============================================
# CHECK 7: Business Objectives SMART Validation
# ============================================
echo "CHECK 7: Business Objectives SMART Validation"
echo "-----------------------------------------"

# Look for BO-XXX objectives
bo_count=$(grep -c "BO-[0-9]\+:" "$BRD_FILE")

if [ "$bo_count" -gt 0 ]; then
  echo "  Found $bo_count business objectives (BO-NNN format)"

  # Check each objective for SMART criteria
  grep "BO-[0-9]\+:" "$BRD_FILE" | while read -r line; do
    objective=$(echo "$line" | sed 's/BO-[0-9]\+: *//')

    # Check for quantifiable elements (numbers, percentages, time periods)
    if ! echo "$objective" | grep -qE '[0-9]+%|within.*month|within.*year|\$[0-9]+|by.*[0-9]{4}'; then
      echo "  ⚠️  WARNING: Business objective missing quantifiable elements: $objective"
      ((WARNINGS++))
    fi

    # Check for time-bound elements
    if ! echo "$objective" | grep -qE 'within|by.*[0-9]{4}|in.*month|in.*year'; then
      echo "  ⚠️  WARNING: Business objective not time-bound: $objective"
      ((WARNINGS++))
    fi
  done
else
  echo "  ⚠️  WARNING: No business objectives found (BO-NNN format expected)"
  ((WARNINGS++))
fi

echo ""

# ============================================
# CHECK 8: Acceptance Criteria Format
# ============================================
echo "CHECK 8: Acceptance Criteria Format"
echo "-----------------------------------------"

# Check for business acceptance criteria
if grep -q "### 8.1 Business Acceptance Criteria" "$BRD_FILE"; then
  echo "  ✅ Found: Business acceptance criteria section"
else
  echo "  ⚠️  WARNING: Business acceptance criteria section recommended"
  ((WARNINGS++))
fi

# Check for quantifiable measures in acceptance criteria
ac_content=$(grep -A 50 "### 8.1 Business Acceptance Criteria" "$BRD_FILE" 2>/dev/null || echo "")
if [ -n "$ac_content" ]; then
  if echo "$ac_content" | grep -qE '[0-9]+%|per.*second|within.*[0-9]+|\$[0-9]+'; then
    echo "  ✅ Business acceptance criteria include quantifiable measures"
  else
    echo "  ⚠️  WARNING: Business acceptance criteria missing quantifiable measures"
    ((WARNINGS++))
  fi
fi

# Check for KPIs table
if grep -q "### 8.7 Success Metrics and KPIs" "$BRD_FILE"; then
  echo "  ✅ Found: Success metrics and KPIs section"
  # Check for required table columns
  if grep -A 20 "### 8.7 Success Metrics and KPIs" "$BRD_FILE" | grep -q "| KPI | Baseline | Target |"; then
    echo "  ✅ KPIs table has required structure"
  else
    echo "  ⚠️  WARNING: KPIs table missing required columns (KPI, Baseline, Target, etc.)"
    ((WARNINGS++))
  fi
else
  echo "  ⚠️  WARNING: Success metrics and KPIs section recommended"
  ((WARNINGS++))
fi

echo ""

# ============================================
# CHECK 9: ADR Reference Validation
# ============================================
echo "CHECK 9: ADR Reference Validation"
echo "-----------------------------------------"

adr_references=""

# Check for specific ADR number references (prohibited)
if grep -qE "ADR-[0-9]" "$BRD_FILE"; then
  echo "  ❌ ERROR: BRD must not reference specific ADR numbers"

  # Show the offending references
  grep -E "ADR-[0-9]+" "$BRD_FILE" | while read -r line; do
    echo "           Found: $line"
  done

  ((ERRORS++))
else
  echo "  ✅ No specific ADR number references found (correct for BRD phase)"
fi

# Verify Section 5.2 exists (where ADR topics should be listed)
if grep -q "## 5.2 Architecture Decision Requirements" "$BRD_FILE"; then
  adr_topics=$(grep -A 100 "## 5.2 Architecture Decision Requirements" "$BRD_FILE" | grep "^|" | grep -v "^|---" | grep -v "^| Topic Area " | wc -l)
  echo "  ✅ Section 5.2 identifies $adr_topics ADR topics for future creation"
else
  echo "  ❌ ERROR: Missing Section 5.2 to identify ADR topics"
  ((ERRORS++))
fi

echo ""

# ============================================
# CHECK 10: Strategy Document Traceability
# ============================================
echo "CHECK 10: Strategy Document Traceability"
echo "-----------------------------------------"

strategy_refs=""

# Check for option_strategy document references
if grep -q "option_strategy" "$BRD_FILE"; then
  echo "  ✅ References to option_strategy/ documents found"

  # Check for specific document references
  if grep -qE "integrated_strategy_algo_v5\.md|Integrated_strategy_desc\.md|README\.md" "$BRD_FILE"; then
    echo "  ✅ Specific strategy documents referenced"
  else
    echo "  ⚠️  WARNING: General option_strategy/ reference but no specific document references"
    ((WARNINGS++))
  fi
else
  echo "  ⚠️  WARNING: No references to option_strategy/ documents found"
  ((WARNINGS++))
fi

# Check for section references
if grep -qE "Section [0-9]+\.[0-9]*" "$BRD_FILE"; then
  echo "  ✅ Strategy document section references found"
else
  echo "  ⚠️  WARNING: Strategy references should include specific sections"
  ((WARNINGS++))
fi

echo ""

# ============================================
# CHECK 11: Markdown Link Resolution
# ============================================
echo "CHECK 11: Markdown Link Resolution"
echo "-----------------------------------------"

base_dir="$(dirname "$BRD_FILE")"
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

  ((checked_links++))

  # Resolve relative path
  resolved_path="$(cd "$base_dir" && realpath -m "$path" 2>/dev/null || echo "INVALID")"

  if [ ! -f "$resolved_path" ]; then
    echo "  ❌ ERROR: Broken link - file not found"
    echo "           Link: $path"
    echo "           Resolved: $resolved_path"
    ((broken_links++))
  fi
done < <(grep -oE '\[.*?\]\([^)]+\)' "$BRD_FILE" || true)

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
# CHECK 12: Out-of-Scope Clarity
# ============================================
echo "CHECK 12: Out-of-Scope Clarity"
echo "-----------------------------------------"

if grep -q "### 3.3 Out-of-Scope Items" "$BRD_FILE"; then
  echo "  ✅ Found: Out-of-Scope Items section"

  # Check if section has content
  oos_content=$(grep -A 20 "### 3.3 Out-of-Scope Items" "$BRD_FILE" | head -20)

  if echo "$oos_content" | grep -qE "^[0-9]+\.\s*\*\*.*\*\*" || echo "$oos_content" | grep -qE "- "; then
    echo "  ✅ Out-of-Scope Items section has substantive content"

    # Check for rationale
    if echo "$oos_content" | grep -qE "- excluded|:|reason|rationale" | head -5 | grep -q .; then
      echo "  ✅ Out-of-scope items include rationale"
    else
      echo "  ⚠️  WARNING: Out-of-scope items should include rationale"
      ((WARNINGS++))
    fi
  else
    echo "  ⚠️  WARNING: Out-of-Scope Items section appears minimal or empty"
    ((WARNINGS++))
  fi
else
  echo "  ⚠️  WARNING: Out-of-Scope Items section recommended for scope clarity"
  ((WARNINGS++))
fi

echo ""

# ============================================
# SUMMARY
# ============================================
echo "========================================="
echo "VALIDATION SUMMARY"
echo "========================================="
echo "File: $BRD_FILE"
echo "Script Version: ${SCRIPT_VERSION}"
echo "BRD Type: ${brd_type:-unknown}"
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
  echo "✅ PASSED: All validation checks passed with no warnings"
  echo ""
  echo "Document complies with:"
  echo "  - BRD-TEMPLATE.md structure"
  echo "  - doc_flow SDD framework requirements"
  echo "  - Platform/Feature BRD validation rules"
  exit 0
elif [ $ERRORS -eq 0 ]; then
  echo "⚠️  PASSED WITH WARNINGS: Document valid but has $WARNINGS warnings"
  echo ""
  echo "Recommendations:"
  echo "  - Review warnings for quality improvements"
  echo "  - See BRD-TEMPLATE.md for best practices"
  echo "  - Consider impact on downstream PRD/SYS/EARS artifacts"
  exit 0
else
  echo "❌ FAILED: $ERRORS critical errors found"
  echo ""
  echo "Action Required:"
  echo "  1. Fix all errors listed above"
  echo "  2. Review BRD-TEMPLATE.md for requirements"
  echo "  3. Check BRD_CREATION_RULES.md for standards"
  echo "  4. Re-run validation: ./scripts/validate_brd_template.sh $BRD_FILE"
  exit 1
fi

# task_progress List (Optional - Plan Mode)

While in PLAN MODE, if you've outlined concrete steps or requirements for the user, you may include a preparatory todo list using the task_progress parameter.

Reminder on how to use the task_progress parameter:


1. To create or update a todo list, include the task_progress parameter in the next tool call
2. Review each item and update its status:
   - Mark completed items with: - [x]
   - Keep incomplete items as: - [ ]
   - Add new items for any remaining tasks
3. Modify the list as needed:
		- Add any new steps you've discovered
		- Reorder if the sequence has changed
4. Ensure the list accurately reflects the current state

   - Add new items for any remaining tasks
