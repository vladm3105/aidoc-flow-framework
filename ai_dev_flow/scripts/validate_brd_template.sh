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

# Check for domain-specific business logic document references
# Accepts: {domain_strategy}/, domain-specific business logic, or actual strategy paths
if grep -qE "\{domain_strategy\}|domain-specific business logic|strategy.*\.md" "$BRD_FILE"; then
  echo "  ✅ References to domain-specific business logic documents found"

  # Check for specific document references (generic or actual strategy files)
  if grep -qE "\.md|business_logic|risk_management|strategy" "$BRD_FILE"; then
    echo "  ✅ Specific strategy documents referenced"
  else
    echo "  ⚠️  WARNING: General strategy reference but no specific document references"
    ((WARNINGS++))
  fi
else
  echo "  ⚠️  WARNING: No references to domain-specific business logic documents found"
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
# CHECK 13: PRD-Ready Score Validation
# ============================================
echo "CHECK 13: PRD-Ready Score Validation"
echo "-----------------------------------------"

# Check for PRD-Ready Score field in Document Control
if grep -q "| \*\*PRD-Ready Score\*\* |" "$BRD_FILE"; then
  echo "  ✅ Found: PRD-Ready Score field in Document Control"

  # Extract score value
  score_line=$(grep "| \*\*PRD-Ready Score\*\* |" "$BRD_FILE" || echo "")

  # Check format: should have ✅ emoji and percentage
  if echo "$score_line" | grep -qE "✅.*[0-9]+/100"; then
    score_value=$(echo "$score_line" | grep -oE "[0-9]+/100" | head -1 | cut -d'/' -f1)
    echo "  ✅ PRD-Ready Score format valid: $score_value/100"

    # Check threshold
    if [ "$score_value" -ge 90 ]; then
      echo "  ✅ PRD-Ready Score meets ≥90/100 threshold"
    elif [ "$score_value" -ge 70 ]; then
      echo "  ⚠️  WARNING: PRD-Ready Score below 90/100: $score_value/100"
      echo "           Recommended: Refactor to achieve ≥90/100"
      ((WARNINGS++))
    else
      echo "  ❌ ERROR: PRD-Ready Score below minimum threshold: $score_value/100"
      echo "           Target: ≥90/100"
      ((ERRORS++))
    fi
  else
    echo "  ❌ ERROR: PRD-Ready Score missing ✅ emoji and/or proper format"
    echo "           Expected: ✅ [Score]/100 (Target: ≥90/100)"
    ((ERRORS++))
  fi
else
  echo "  ❌ MISSING: PRD-Ready Score field in Document Control"
  echo "           Add: | **PRD-Ready Score** | ✅ [Score]/100 (Target: ≥90/100) |"
  ((ERRORS++))
fi

echo ""

# ============================================
# CHECK 14: Code Blocks in Functional Requirements
# ============================================
echo "CHECK 14: Code Blocks in Functional Requirements"
echo "-----------------------------------------"

# Extract Section 4 content
section4_start=$(grep -n "^## 4\. " "$BRD_FILE" | head -1 | cut -d':' -f1)
section5_start=$(grep -n "^## 5\. " "$BRD_FILE" | head -1 | cut -d':' -f1)

code_blocks_found=0
code_block_lines=""

if [ -n "$section4_start" ] && [ -n "$section5_start" ]; then
  # Search for code blocks between Section 4 and Section 5
  code_block_lines=$(sed -n "${section4_start},${section5_start}p" "$BRD_FILE" | grep -n '```' | cut -d':' -f1 || echo "")

  if [ -n "$code_block_lines" ]; then
    code_blocks_found=$(echo "$code_block_lines" | wc -l)
    code_blocks_found=$((code_blocks_found / 2))  # Divide by 2 (opening and closing ```)

    echo "  ❌ ERROR: Found $code_blocks_found code block(s) in Section 4 (Functional Requirements)"
    echo "           Code blocks are PRD-level content and must be removed from BRDs"
    echo "           Replace with business-level descriptions (see BRD-TEMPLATE.md Appendix B)"
    ((ERRORS++))
  else
    echo "  ✅ No code blocks found in Section 4"
  fi
else
  echo "  ⚠️  WARNING: Could not locate Section 4 boundaries for code block scanning"
  ((WARNINGS++))
fi

echo ""

# ============================================
# CHECK 15: API/Technical Terminology in FRs
# ============================================
echo "CHECK 15: API/Technical Terminology in Functional Requirements"
echo "-----------------------------------------"

technical_terms=(
  "POST" "GET" "PUT" "DELETE" "PATCH"
  "JSON" "XML" "YAML"
  "endpoint" "API" "request" "response" "payload" "header"
  "database" "table" "column" "query" "schema"
  "INSERT" "UPDATE" "SELECT" "DELETE"
)

technical_term_count=0
technical_term_lines=""

if [ -n "$section4_start" ] && [ -n "$section5_start" ]; then
  for term in "${technical_terms[@]}"; do
    # Case-insensitive search in Section 4
    matches=$(sed -n "${section4_start},${section5_start}p" "$BRD_FILE" | grep -i "$term" || echo "")
    if [ -n "$matches" ]; then
      match_count=$(echo "$matches" | wc -l)
      technical_term_count=$((technical_term_count + match_count))
    fi
  done

  if [ $technical_term_count -gt 0 ]; then
    echo "  ⚠️  WARNING: Found $technical_term_count technical term instance(s) in Section 4"
    echo "           Technical terms indicate potential PRD-level contamination"
    echo "           Suggested: Replace with business-level language"
    echo "           Example: 'Customer initiates transaction' (not 'POST /api/v1/transactions')"
    ((WARNINGS++))
  else
    echo "  ✅ No technical terminology found in Section 4"
  fi
else
  echo "  ⚠️  WARNING: Could not locate Section 4 for technical term scanning"
  ((WARNINGS++))
fi

echo ""

# ============================================
# CHECK 16: UI-Specific Language in FRs
# ============================================
echo "CHECK 16: UI-Specific Language in Functional Requirements"
echo "-----------------------------------------"

ui_terms=(
  "button" "dropdown" "modal" "dialog" "popup"
  "form" "checkbox" "radio button"
  "click" "tap" "swipe" "scroll"
  "screen" "page" "view" "panel"
  "display" "show" "hide"
)

ui_term_count=0

if [ -n "$section4_start" ] && [ -n "$section5_start" ]; then
  for term in "${ui_terms[@]}"; do
    # Case-insensitive search in Section 4
    matches=$(sed -n "${section4_start},${section5_start}p" "$BRD_FILE" | grep -i "$term" || echo "")
    if [ -n "$matches" ]; then
      match_count=$(echo "$matches" | wc -l)
      ui_term_count=$((ui_term_count + match_count))
    fi
  done

  if [ $ui_term_count -gt 0 ]; then
    echo "  ⚠️  WARNING: Found $ui_term_count UI-specific term instance(s) in Section 4"
    echo "           UI terms indicate potential PRD-level contamination"
    echo "           Suggested: Replace with business action descriptions"
    echo "           Example: 'Customer selects recipient' (not 'Customer clicks dropdown')"
    ((WARNINGS++))
  else
    echo "  ✅ No UI-specific language found in Section 4"
  fi
else
  echo "  ⚠️  WARNING: Could not locate Section 4 for UI term scanning"
  ((WARNINGS++))
fi

echo ""

# ============================================
# CHECK 17: FR 6-Subsection Structure
# ============================================
echo "CHECK 17: Functional Requirement 6-Subsection Structure"
echo "-----------------------------------------"

# Find all FRs (#### FR-NNN: format)
fr_count=$(grep -c "^#### FR-[0-9]\+:" "$BRD_FILE" || echo "0")

if [ "$fr_count" -gt 0 ]; then
  echo "  Found $fr_count Functional Requirement(s)"

  incomplete_frs=0

  # Check each FR for 6 required subsections
  grep -n "^#### FR-[0-9]\+:" "$BRD_FILE" | while IFS=: read -r line_num fr_title; do
    fr_id=$(echo "$fr_title" | grep -oE "FR-[0-9]+" | head -1)

    # Get FR content (from this FR to next FR or end of section)
    next_fr_line=$(grep -n "^#### FR-[0-9]\+:" "$BRD_FILE" | grep -A1 "^${line_num}:" | tail -1 | cut -d':' -f1)
    if [ "$next_fr_line" = "$line_num" ]; then
      # Last FR - go to next section
      next_fr_line=$(grep -n "^## 5\. " "$BRD_FILE" | head -1 | cut -d':' -f1)
    fi

    fr_content=$(sed -n "${line_num},${next_fr_line}p" "$BRD_FILE")

    # Check for 6 required subsections
    missing_subsections=""

    if ! echo "$fr_content" | grep -q "^\*\*Business Capability\*\*:"; then
      missing_subsections="${missing_subsections}Business Capability, "
    fi

    if ! echo "$fr_content" | grep -q "^\*\*Business Requirements\*\*:"; then
      missing_subsections="${missing_subsections}Business Requirements, "
    fi

    if ! echo "$fr_content" | grep -q "^\*\*Business Rules\*\*:"; then
      missing_subsections="${missing_subsections}Business Rules, "
    fi

    if ! echo "$fr_content" | grep -q "^\*\*Business Acceptance Criteria\*\*:"; then
      missing_subsections="${missing_subsections}Business Acceptance Criteria, "
    fi

    if ! echo "$fr_content" | grep -q "^\*\*Related Requirements\*\*:"; then
      missing_subsections="${missing_subsections}Related Requirements, "
    fi

    if ! echo "$fr_content" | grep -q "^\*\*Complexity\*\*:"; then
      missing_subsections="${missing_subsections}Complexity, "
    fi

    if [ -n "$missing_subsections" ]; then
      echo "  ❌ ERROR: $fr_id missing subsections: ${missing_subsections%, }"
      incomplete_frs=$((incomplete_frs + 1))
    fi
  done

  if [ $incomplete_frs -gt 0 ]; then
    echo "  ❌ ERROR: $incomplete_frs FR(s) missing required subsections"
    echo "           All FRs must have: Business Capability, Business Requirements, Business Rules,"
    echo "           Business Acceptance Criteria, Related Requirements, Complexity"
    ((ERRORS++))
  else
    echo "  ✅ All FRs have complete 6-subsection structure"
  fi
else
  echo "  ⚠️  WARNING: No Functional Requirements found (#### FR-NNN: format expected)"
  ((WARNINGS++))
fi

echo ""

# ============================================
# CHECK 18: Related Requirements Cross-Reference Validation
# ============================================
echo "CHECK 18: Related Requirements Cross-Reference Validation"
echo "-----------------------------------------"

# Find all BRD-NNN references in Related Requirements subsections
brd_refs=$(grep -A 5 "^\*\*Related Requirements\*\*:" "$BRD_FILE" | grep -oE "BRD-[0-9]+" || echo "")

if [ -n "$brd_refs" ]; then
  brd_ref_count=$(echo "$brd_refs" | wc -l)
  echo "  Found $brd_ref_count BRD cross-reference(s)"

  invalid_refs=0
  brd_dir=$(dirname "$BRD_FILE")

  echo "$brd_refs" | sort -u | while read -r brd_ref; do
    # Check if BRD file exists (BRD-NNN_*.md pattern)
    brd_files=$(find "$brd_dir" -name "${brd_ref}_*.md" 2>/dev/null || echo "")

    if [ -z "$brd_files" ]; then
      echo "  ⚠️  WARNING: Referenced BRD not found: $brd_ref"
      echo "           Expected file: ${brd_dir}/${brd_ref}_*.md"
      invalid_refs=$((invalid_refs + 1))
    fi
  done

  if [ $invalid_refs -gt 0 ]; then
    echo "  ⚠️  WARNING: $invalid_refs invalid BRD cross-reference(s) found"
    echo "           Verify all referenced BRD files exist"
    ((WARNINGS++))
  else
    echo "  ✅ All BRD cross-references valid"
  fi
else
  echo "  ⚠️  WARNING: No BRD cross-references found in Related Requirements"
  echo "           FRs should reference Platform BRDs (BRD-001 through BRD-005)"
  ((WARNINGS++))
fi

echo ""

# ============================================
# PRD-READY SCORE CALCULATION
# ============================================
echo "========================================="
echo "PRD-READY SCORE CALCULATION"
echo "========================================="

# Initialize deduction categories
deduction_cat1=0  # PRD-Level Content Contamination (max 50)
deduction_cat2=0  # FR Structure Completeness (max 30)
deduction_cat3=0  # Document Structure and Quality (max 20)

# Category 1: PRD-Level Content Contamination
echo "Category 1: PRD-Level Content Contamination"
echo "-----------------------------------------"

# Code blocks: -10 points per block (max -50)
if [ $code_blocks_found -gt 0 ]; then
  code_block_deduction=$((code_blocks_found * 10))
  if [ $code_block_deduction -gt 50 ]; then
    code_block_deduction=50
  fi
  deduction_cat1=$((deduction_cat1 + code_block_deduction))
  echo "  Code blocks: $code_blocks_found found → -$code_block_deduction points"
fi

# API/Technical terms: -2 points per instance (max -20)
if [ $technical_term_count -gt 0 ]; then
  tech_term_deduction=$((technical_term_count * 2))
  if [ $tech_term_deduction -gt 20 ]; then
    tech_term_deduction=20
  fi
  deduction_cat1=$((deduction_cat1 + tech_term_deduction))
  echo "  API/technical terms: $technical_term_count instances → -$tech_term_deduction points"
fi

# UI terms: -2 points per instance (max -20)
if [ $ui_term_count -gt 0 ]; then
  ui_term_deduction=$((ui_term_count * 2))
  if [ $ui_term_deduction -gt 20 ]; then
    ui_term_deduction=20
  fi
  deduction_cat1=$((deduction_cat1 + ui_term_deduction))
  echo "  UI-specific terms: $ui_term_count instances → -$ui_term_deduction points"
fi

if [ $deduction_cat1 -eq 0 ]; then
  echo "  ✅ No PRD-level contamination detected → -0 points"
fi

echo "Category 1 Total: -$deduction_cat1 points"
echo ""

# Category 2: FR Structure Completeness
echo "Category 2: FR Structure Completeness"
echo "-----------------------------------------"

# Missing FR subsections: -5 points per incomplete FR (max -30)
if [ $incomplete_frs -gt 0 ]; then
  fr_structure_deduction=$((incomplete_frs * 5))
  if [ $fr_structure_deduction -gt 30 ]; then
    fr_structure_deduction=30
  fi
  deduction_cat2=$((deduction_cat2 + fr_structure_deduction))
  echo "  Incomplete FRs: $incomplete_frs FRs missing subsections → -$fr_structure_deduction points"
fi

# Invalid cross-references: -2 points per invalid ref (max -10)
if [ $invalid_refs -gt 0 ]; then
  crossref_deduction=$((invalid_refs * 2))
  if [ $crossref_deduction -gt 10 ]; then
    crossref_deduction=10
  fi
  deduction_cat2=$((deduction_cat2 + crossref_deduction))
  echo "  Invalid cross-refs: $invalid_refs references → -$crossref_deduction points"
fi

if [ $deduction_cat2 -eq 0 ]; then
  echo "  ✅ Complete FR structure with valid cross-references → -0 points"
fi

echo "Category 2 Total: -$deduction_cat2 points"
echo ""

# Category 3: Document Structure and Quality
echo "Category 3: Document Structure and Quality"
echo "-----------------------------------------"

# PRD-Ready Score field missing: -5 points
if ! grep -q "| \*\*PRD-Ready Score\*\* |" "$BRD_FILE"; then
  deduction_cat3=$((deduction_cat3 + 5))
  echo "  PRD-Ready Score field missing → -5 points"
fi

# Document Control fields: -3 points if any missing (already checked in CHECK 2)
# Section validation: -1 point per missing section (already checked in CHECK 1)
# Revision History: -3 points if missing (already checked in CHECK 3)

if [ $deduction_cat3 -eq 0 ]; then
  echo "  ✅ Complete document structure → -0 points"
fi

echo "Category 3 Total: -$deduction_cat3 points"
echo ""

# Calculate final score
total_deductions=$((deduction_cat1 + deduction_cat2 + deduction_cat3))
prd_ready_score=$((100 - total_deductions))

echo "========================================="
echo "Total Deductions: -$total_deductions points"
echo "PRD-Ready Score: $prd_ready_score/100"
echo "========================================="
echo ""

# Validation outcome based on score
if [ $prd_ready_score -ge 90 ]; then
  echo "✅ EXCELLENT: PRD-Ready Score meets ≥90/100 threshold"
  echo "   BRD ready for PRD development"
elif [ $prd_ready_score -ge 70 ]; then
  echo "⚠️  MODERATE: PRD-Ready Score 70-89/100"
  echo "   Moderate PRD-level contamination detected"
  echo "   Recommendation: Refactor to achieve ≥90/100"
  echo "   See BRD_REFACTORING_GUIDE.md for guidance"
else
  echo "❌ NEEDS IMPROVEMENT: PRD-Ready Score <70/100"
  echo "   Heavy PRD-level contamination detected"
  echo "   Action Required: Major refactoring needed"
  echo "   See BRD_REFACTORING_GUIDE.md for step-by-step guidance"
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
