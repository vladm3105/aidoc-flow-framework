#!/bin/bash
# ICON (Implementation Contract) Template Validator v1.0
# Validates ICON documents against:
# - ICON-TEMPLATE.md (authoritative template)
# - doc_flow SDD framework standards
# - Layer 11 artifact requirements
# - Provider/Consumer relationship validation
# Usage: ./scripts/validate_icon.sh <ICON_FILE>

set -e

ICON_FILE=$1
ERRORS=0
WARNINGS=0
SCRIPT_VERSION="1.0.0"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

if [ -z "$ICON_FILE" ]; then
  echo "Usage: $0 <ICON_FILE>"
  echo "Example: $0 /opt/data/project/docs/ICON/ICON-001_gateway_connector_protocol.md"
  exit 1
fi

if [ ! -f "$ICON_FILE" ]; then
  echo -e "${RED}ERROR: File not found: $ICON_FILE${NC}"
  exit 1
fi

echo "========================================="
echo "ICON Template Validator v${SCRIPT_VERSION}"
echo "========================================="
echo "File: $ICON_FILE"
echo "Artifact Type: ICON (Implementation Contract) - Layer 11"
echo ""

# ============================================
# CHECK 1: Filename Format
# ============================================
echo "CHECK 1: Filename Format"
echo "-----------------------------------------"

filename=$(basename "$ICON_FILE")

# Pattern: ICON-NNN_descriptive_slug.md
if [[ $filename =~ ^ICON-[0-9]{3,4}_[a-z0-9_]+\.md$ ]]; then
  echo -e "  ${GREEN}✅ Filename format valid: $filename${NC}"

  # Extract ICON ID
  ICON_ID=$(echo "$filename" | grep -oE "ICON-[0-9]+" | head -1)
  echo "  ICON ID: $ICON_ID"
else
  echo -e "  ${RED}❌ ERROR: Invalid filename format: $filename${NC}"
  echo "           Expected: ICON-NNN_descriptive_slug.md"
  echo "           Pattern: ^ICON-[0-9]{3,4}_[a-z0-9_]+\\.md$"
  ((ERRORS++))
fi

echo ""

# ============================================
# CHECK 2: Frontmatter Validation
# ============================================
echo "CHECK 2: Frontmatter Validation"
echo "-----------------------------------------"

# Check for YAML frontmatter (--- delimiters)
if grep -q "^---" "$ICON_FILE"; then
  echo -e "  ${GREEN}✅ YAML frontmatter present${NC}"

  # Check for required fields
  if grep -q "artifact_type: ICON" "$ICON_FILE"; then
    echo -e "  ${GREEN}✅ artifact_type: ICON${NC}"
  else
    echo -e "  ${RED}❌ ERROR: Missing or invalid artifact_type (must be ICON)${NC}"
    ((ERRORS++))
  fi

  if grep -q "layer: 11" "$ICON_FILE"; then
    echo -e "  ${GREEN}✅ layer: 11${NC}"
  else
    echo -e "  ${RED}❌ ERROR: Missing or invalid layer (must be 11)${NC}"
    ((ERRORS++))
  fi

  if grep -q "layer-11-artifact" "$ICON_FILE"; then
    echo -e "  ${GREEN}✅ layer-11-artifact tag present${NC}"
  else
    echo -e "  ${YELLOW}⚠️  WARNING: Missing layer-11-artifact tag${NC}"
    ((WARNINGS++))
  fi

  # Check contract_type
  if grep -qE "contract_type: (protocol|exception|state-machine|data-model|di-interface)" "$ICON_FILE"; then
    contract_type=$(grep -oE "contract_type: (protocol|exception|state-machine|data-model|di-interface)" "$ICON_FILE" | head -1 | cut -d':' -f2 | tr -d ' ')
    echo -e "  ${GREEN}✅ contract_type: $contract_type${NC}"
  else
    echo -e "  ${RED}❌ ERROR: Missing or invalid contract_type${NC}"
    echo "           Valid values: protocol, exception, state-machine, data-model, di-interface"
    ((ERRORS++))
  fi

  # Check provider_tasks
  if grep -q "provider_tasks: TASKS-" "$ICON_FILE"; then
    provider=$(grep -oE "provider_tasks: TASKS-[0-9]+" "$ICON_FILE" | head -1 | cut -d':' -f2 | tr -d ' ')
    echo -e "  ${GREEN}✅ provider_tasks: $provider${NC}"
  else
    echo -e "  ${RED}❌ ERROR: Missing provider_tasks field${NC}"
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
  "Contract ID"
  "Contract Name"
  "Version"
  "Status"
  "Created"
  "Last Updated"
  "Author"
  "Provider"
  "Consumers"
)

for field in "${required_dc_fields[@]}"; do
  if grep -qi "$field" "$ICON_FILE"; then
    echo -e "  ${GREEN}✅ Found: $field${NC}"
  else
    echo -e "  ${RED}❌ MISSING: $field${NC}"
    ((ERRORS++))
  fi
done

# Check status value
if grep -qE "Status.*\|.*(Draft|Active|Deprecated)" "$ICON_FILE"; then
  echo -e "  ${GREEN}✅ Status has valid enum value${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: Status should be Draft, Active, or Deprecated${NC}"
  ((WARNINGS++))
fi

echo ""

# ============================================
# CHECK 4: Required Sections
# ============================================
echo "CHECK 4: Required Sections"
echo "-----------------------------------------"

required_sections=(
  "## 1. Contract Overview"
  "## 2. Protocol"
  "## 3. Provider Requirements"
  "## 4. Consumer Requirements"
  "## Traceability"
)

for section in "${required_sections[@]}"; do
  if grep -q "$section" "$ICON_FILE"; then
    echo -e "  ${GREEN}✅ Found: $section${NC}"
  else
    echo -e "  ${RED}❌ MISSING: $section${NC}"
    ((ERRORS++))
  fi
done

echo ""

# ============================================
# CHECK 5: Protocol Definition Validation
# ============================================
echo "CHECK 5: Protocol Definition Validation"
echo "-----------------------------------------"

# Check for Python code block
if grep -q '```python' "$ICON_FILE"; then
  echo -e "  ${GREEN}✅ Python code block present${NC}"

  # Check for Protocol class
  if grep -qE "class [A-Z][A-Za-z]+\(Protocol\)" "$ICON_FILE"; then
    protocol_class=$(grep -oE "class [A-Z][A-Za-z]+\(Protocol\)" "$ICON_FILE" | head -1)
    echo -e "  ${GREEN}✅ Protocol class defined: $protocol_class${NC}"
  else
    echo -e "  ${YELLOW}⚠️  WARNING: No typing.Protocol class found${NC}"
    ((WARNINGS++))
  fi

  # Check for type hints
  if grep -qE "-> [A-Za-z\[\]]+:" "$ICON_FILE"; then
    echo -e "  ${GREEN}✅ Return type hints present${NC}"
  else
    echo -e "  ${YELLOW}⚠️  WARNING: No return type hints found${NC}"
    ((WARNINGS++))
  fi

  # Check for @runtime_checkable decorator
  if grep -q "@runtime_checkable" "$ICON_FILE"; then
    echo -e "  ${GREEN}✅ @runtime_checkable decorator present${NC}"
  else
    echo -e "  ${YELLOW}⚠️  WARNING: Consider adding @runtime_checkable decorator${NC}"
    ((WARNINGS++))
  fi

  # Check for docstrings
  if grep -qE '""".*"""' "$ICON_FILE"; then
    echo -e "  ${GREEN}✅ Docstrings present${NC}"
  else
    echo -e "  ${YELLOW}⚠️  WARNING: Add docstrings to protocol methods${NC}"
    ((WARNINGS++))
  fi
else
  echo -e "  ${RED}❌ ERROR: Missing Python code block${NC}"
  ((ERRORS++))
fi

echo ""

# ============================================
# CHECK 6: Contract Type-Specific Validation
# ============================================
echo "CHECK 6: Contract Type-Specific Validation"
echo "-----------------------------------------"

# Get contract type from frontmatter
contract_type=$(grep -oE "contract_type: [a-z-]+" "$ICON_FILE" | head -1 | cut -d':' -f2 | tr -d ' ' || echo "")

case "$contract_type" in
  "protocol")
    if grep -qE "class [A-Z][A-Za-z]+\(Protocol\)" "$ICON_FILE"; then
      echo -e "  ${GREEN}✅ Protocol contract: Protocol class defined${NC}"
    else
      echo -e "  ${RED}❌ ERROR: Protocol contract must define Protocol class${NC}"
      ((ERRORS++))
    fi
    ;;
  "exception")
    if grep -qE "class [A-Z][A-Za-z]+Exception" "$ICON_FILE"; then
      exception_count=$(grep -cE "class [A-Z][A-Za-z]+Exception" "$ICON_FILE" || echo "0")
      echo -e "  ${GREEN}✅ Exception contract: $exception_count exception class(es) defined${NC}"
    else
      echo -e "  ${RED}❌ ERROR: Exception contract must define Exception classes${NC}"
      ((ERRORS++))
    fi
    ;;
  "state-machine")
    if grep -qE "class [A-Z][A-Za-z]+State.*Enum" "$ICON_FILE"; then
      echo -e "  ${GREEN}✅ State machine contract: State Enum defined${NC}"
    else
      echo -e "  ${RED}❌ ERROR: State machine contract must define State Enum${NC}"
      ((ERRORS++))
    fi
    if grep -qiE "transition|valid_transitions" "$ICON_FILE"; then
      echo -e "  ${GREEN}✅ State transitions documented${NC}"
    else
      echo -e "  ${YELLOW}⚠️  WARNING: State machine should document transitions${NC}"
      ((WARNINGS++))
    fi
    ;;
  "data-model")
    if grep -qE "(TypedDict|BaseModel|dataclass)" "$ICON_FILE"; then
      echo -e "  ${GREEN}✅ Data model contract: Typed structures defined${NC}"
    else
      echo -e "  ${RED}❌ ERROR: Data model contract must define typed structures${NC}"
      ((ERRORS++))
    fi
    ;;
  "di-interface")
    if grep -qE "class [A-Z][A-Za-z]+\(ABC\)" "$ICON_FILE"; then
      echo -e "  ${GREEN}✅ DI interface contract: ABC class defined${NC}"
    else
      echo -e "  ${YELLOW}⚠️  WARNING: DI interface should use ABC class${NC}"
      ((WARNINGS++))
    fi
    ;;
  *)
    echo -e "  ${YELLOW}⚠️  WARNING: Unknown contract type: $contract_type${NC}"
    ((WARNINGS++))
    ;;
esac

echo ""

# ============================================
# CHECK 7: Provider/Consumer Validation
# ============================================
echo "CHECK 7: Provider/Consumer Validation"
echo "-----------------------------------------"

base_dir="$(dirname "$ICON_FILE")"
tasks_dir="$base_dir/../TASKS"

# Get provider from document
provider_tasks=$(grep -oE "TASKS-[0-9]+" "$ICON_FILE" | head -1 || echo "")

if [ -n "$provider_tasks" ]; then
  echo "  Provider: $provider_tasks"

  # Check if provider TASKS file exists
  provider_file=$(find "$tasks_dir" -name "${provider_tasks}*.md" 2>/dev/null | head -1)
  if [ -n "$provider_file" ]; then
    echo -e "  ${GREEN}✅ Provider TASKS file exists${NC}"

    # Check if provider references this ICON
    if grep -q "@icon: $ICON_ID" "$provider_file" 2>/dev/null; then
      echo -e "  ${GREEN}✅ Provider references this ICON${NC}"
    else
      echo -e "  ${RED}❌ ERROR: Provider $provider_tasks does not reference $ICON_ID${NC}"
      ((ERRORS++))
    fi
  else
    echo -e "  ${YELLOW}⚠️  WARNING: Provider TASKS file not found${NC}"
    ((WARNINGS++))
  fi
else
  echo -e "  ${RED}❌ ERROR: No provider TASKS referenced${NC}"
  ((ERRORS++))
fi

# Count consumers
if [ -d "$tasks_dir" ]; then
  consumer_count=$(grep -r "@icon-role: consumer" "$tasks_dir/" 2>/dev/null | grep "$ICON_ID" | wc -l || echo "0")
  provider_count=$(grep -r "@icon-role: provider" "$tasks_dir/" 2>/dev/null | grep "$ICON_ID" | wc -l || echo "0")

  echo "  Providers found: $provider_count"
  echo "  Consumers found: $consumer_count"

  if [ "$provider_count" -ne 1 ]; then
    echo -e "  ${RED}❌ ERROR: Expected exactly 1 provider, found $provider_count${NC}"
    ((ERRORS++))
  else
    echo -e "  ${GREEN}✅ Exactly 1 provider${NC}"
  fi

  if [ "$consumer_count" -lt 5 ]; then
    echo -e "  ${YELLOW}⚠️  WARNING: Standalone ICON with <5 consumers ($consumer_count found)${NC}"
    echo "           Consider embedding contract in TASKS file instead"
    ((WARNINGS++))
  else
    echo -e "  ${GREEN}✅ $consumer_count consumers (justifies standalone ICON)${NC}"
  fi
fi

# Check for orphaned ICON
if [ -d "$tasks_dir" ]; then
  total_refs=$(grep -r "@icon: $ICON_ID" "$tasks_dir/" 2>/dev/null | wc -l || echo "0")
  if [ "$total_refs" -eq 0 ]; then
    echo -e "  ${RED}❌ ERROR: Orphaned ICON - no TASKS references found${NC}"
    ((ERRORS++))
  fi
fi

echo ""

# ============================================
# CHECK 8: Traceability Tags (Layer 11)
# ============================================
echo "CHECK 8: Traceability Tags (Layer 11)"
echo "-----------------------------------------"

required_tags=("@brd" "@prd" "@ears" "@bdd" "@adr" "@sys" "@req" "@spec")

tag_count=0
for tag in "${required_tags[@]}"; do
  if grep -qE "^${tag}:|^\- \`${tag}:" "$ICON_FILE"; then
    echo -e "  ${GREEN}✅ Found: $tag${NC}"
    ((tag_count++))
  else
    echo -e "  ${RED}❌ MISSING: $tag${NC}"
    ((ERRORS++))
  fi
done

# Check optional tags
optional_tags=("@impl" "@ctr")
for tag in "${optional_tags[@]}"; do
  if grep -qE "^${tag}:|^\- \`${tag}:" "$ICON_FILE"; then
    echo -e "  ${GREEN}✅ Optional tag present: $tag${NC}"
    ((tag_count++))
  fi
done

echo "  Total traceability tags: $tag_count"
if [ $tag_count -lt 8 ]; then
  echo -e "  ${RED}❌ ERROR: Minimum 8 tags required for Layer 11${NC}"
fi

# Check for empty tags
if grep -qE "@[a-z]+:\s*$" "$ICON_FILE"; then
  echo -e "  ${RED}❌ ERROR: Empty tag value found${NC}"
  ((ERRORS++))
fi

echo ""

# ============================================
# CHECK 9: Cross-Reference Validation
# ============================================
echo "CHECK 9: Cross-Reference Validation"
echo "-----------------------------------------"

# Check TASKS references
tasks_refs=$(grep -oE "TASKS-[0-9]+" "$ICON_FILE" 2>/dev/null | sort -u || echo "")
if [ -n "$tasks_refs" ]; then
  tasks_count=$(echo "$tasks_refs" | wc -l)
  echo "  Found $tasks_count TASKS reference(s)"

  echo "$tasks_refs" | while read -r tasks_ref; do
    tasks_file=$(find "$tasks_dir" -name "${tasks_ref}*.md" 2>/dev/null | head -1)
    if [ -n "$tasks_file" ]; then
      echo -e "    ${GREEN}✅ $tasks_ref exists${NC}"
    else
      echo -e "    ${RED}❌ ERROR: $tasks_ref not found${NC}"
    fi
  done
else
  echo -e "  ${RED}❌ ERROR: No TASKS references found${NC}"
  ((ERRORS++))
fi

# Check SPEC references
spec_refs=$(grep -oE "SPEC-[0-9]+" "$ICON_FILE" 2>/dev/null | sort -u || echo "")
if [ -n "$spec_refs" ]; then
  spec_count=$(echo "$spec_refs" | wc -l)
  echo "  Found $spec_count SPEC reference(s)"
fi

echo ""

# ============================================
# SUMMARY
# ============================================
echo "========================================="
echo "VALIDATION SUMMARY"
echo "========================================="
echo "File: $ICON_FILE"
echo "Script Version: ${SCRIPT_VERSION}"
echo "ICON ID: ${ICON_ID:-unknown}"
echo "Contract Type: ${contract_type:-unknown}"
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
  echo -e "${GREEN}✅ PASSED: All validation checks passed${NC}"
  echo ""
  echo "Document complies with:"
  echo "  - ICON-TEMPLATE.md structure"
  echo "  - doc_flow SDD framework requirements"
  echo "  - Layer 11 artifact standards"
  echo "  - Provider/Consumer relationship rules"
  exit 0
elif [ $ERRORS -eq 0 ]; then
  echo -e "${YELLOW}⚠️  PASSED WITH WARNINGS: Document valid but has $WARNINGS warnings${NC}"
  echo ""
  echo "Recommendations:"
  echo "  - Review warnings for quality improvements"
  echo "  - See ICON-TEMPLATE.md for best practices"
  echo "  - Consider consumer count for standalone ICON justification"
  exit 0
else
  echo -e "${RED}❌ FAILED: $ERRORS critical errors found${NC}"
  echo ""
  echo "Action Required:"
  echo "  1. Fix all errors listed above"
  echo "  2. Review ICON-TEMPLATE.md for requirements"
  echo "  3. Check ICON_CREATION_RULES.md for standards"
  echo "  4. Verify provider/consumer relationships"
  echo "  5. Re-run validation: ./scripts/validate_icon.sh $ICON_FILE"
  exit 1
fi
