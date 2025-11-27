#!/bin/bash
# CTR (Contract) Template Validator v1.0
# Validates CTR documents against:
# - CTR-TEMPLATE.md and CTR-TEMPLATE.yaml (authoritative templates)
# - doc_flow SDD framework standards
# - Layer 9 artifact requirements
# Usage: ./scripts/validate_ctr.sh <CTR_FILE>

set -e

CTR_FILE=$1
ERRORS=0
WARNINGS=0
SCRIPT_VERSION="1.0.0"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

if [ -z "$CTR_FILE" ]; then
  echo "Usage: $0 <CTR_FILE>"
  echo "Example: $0 /opt/data/project/docs/CTR/CTR-001_service_api.md"
  exit 1
fi

if [ ! -f "$CTR_FILE" ]; then
  echo -e "${RED}ERROR: File not found: $CTR_FILE${NC}"
  exit 1
fi

echo "========================================="
echo "CTR Template Validator v${SCRIPT_VERSION}"
echo "========================================="
echo "File: $CTR_FILE"
echo "Artifact Type: CTR (Contract) - Layer 9"
echo ""

# ============================================
# CHECK 1: Filename Format
# ============================================
echo "CHECK 1: Filename Format"
echo "-----------------------------------------"

filename=$(basename "$CTR_FILE")

# Pattern: CTR-NNN_descriptive_slug.md or CTR-NNN_descriptive_slug.yaml
if [[ $filename =~ ^CTR-[0-9]{3,4}_[a-z0-9_]+\.(md|yaml)$ ]]; then
  echo -e "  ${GREEN}✅ Filename format valid: $filename${NC}"

  # Extract CTR ID
  CTR_ID=$(echo "$filename" | grep -oE "CTR-[0-9]+" | head -1)
  echo "  CTR ID: $CTR_ID"
else
  echo -e "  ${RED}❌ ERROR: Invalid filename format: $filename${NC}"
  echo "           Expected: CTR-NNN_descriptive_slug.md or CTR-NNN_descriptive_slug.yaml"
  echo "           Pattern: ^CTR-[0-9]{3,4}_[a-z0-9_]+\\.(md|yaml)$"
  ((ERRORS++))
fi

echo ""

# ============================================
# CHECK 2: Frontmatter Validation
# ============================================
echo "CHECK 2: Frontmatter Validation"
echo "-----------------------------------------"

# Check for YAML frontmatter (--- delimiters)
if grep -q "^---" "$CTR_FILE"; then
  echo -e "  ${GREEN}✅ YAML frontmatter present${NC}"

  # Check for required fields
  if grep -q "artifact_type: CTR" "$CTR_FILE"; then
    echo -e "  ${GREEN}✅ artifact_type: CTR${NC}"
  else
    echo -e "  ${RED}❌ ERROR: Missing or invalid artifact_type (must be CTR)${NC}"
    ((ERRORS++))
  fi

  if grep -q "layer: 9" "$CTR_FILE"; then
    echo -e "  ${GREEN}✅ layer: 9${NC}"
  else
    echo -e "  ${RED}❌ ERROR: Missing or invalid layer (must be 9)${NC}"
    ((ERRORS++))
  fi

  if grep -q "layer-9-artifact" "$CTR_FILE"; then
    echo -e "  ${GREEN}✅ layer-9-artifact tag present${NC}"
  else
    echo -e "  ${YELLOW}⚠️  WARNING: Missing layer-9-artifact tag${NC}"
    ((WARNINGS++))
  fi

  # Check contract_type
  if grep -qE "contract_type: (api|service|data|event|integration)" "$CTR_FILE"; then
    contract_type=$(grep -oE "contract_type: (api|service|data|event|integration)" "$CTR_FILE" | head -1 | cut -d':' -f2 | tr -d ' ')
    echo -e "  ${GREEN}✅ contract_type: $contract_type${NC}"
  else
    echo -e "  ${YELLOW}⚠️  WARNING: Missing or invalid contract_type${NC}"
    echo "           Valid values: api, service, data, event, integration"
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
  "Contract ID"
  "Contract Name"
  "Version"
  "Status"
  "Created"
  "Last Updated"
  "Author"
)

for field in "${required_dc_fields[@]}"; do
  if grep -qi "$field" "$CTR_FILE"; then
    echo -e "  ${GREEN}✅ Found: $field${NC}"
  else
    echo -e "  ${RED}❌ MISSING: $field${NC}"
    ((ERRORS++))
  fi
done

# Check status value
if grep -qE "Status.*\|.*(Draft|Active|Deprecated|Retired)" "$CTR_FILE"; then
  echo -e "  ${GREEN}✅ Status has valid enum value${NC}"
else
  echo -e "  ${YELLOW}⚠️  WARNING: Status should be Draft, Active, Deprecated, or Retired${NC}"
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
  "## 2. API Specification"
  "## 3. Data Models"
  "## 4. Error Handling"
  "## 5. Versioning"
  "## Traceability"
)

for section in "${required_sections[@]}"; do
  if grep -q "$section" "$CTR_FILE"; then
    echo -e "  ${GREEN}✅ Found: $section${NC}"
  else
    echo -e "  ${RED}❌ MISSING: $section${NC}"
    ((ERRORS++))
  fi
done

echo ""

# ============================================
# CHECK 5: API Endpoint Validation
# ============================================
echo "CHECK 5: API Endpoint Validation"
echo "-----------------------------------------"

# Check for endpoint definitions
endpoint_count=$(grep -cE "(GET|POST|PUT|DELETE|PATCH)\s+/" "$CTR_FILE" 2>/dev/null || echo "0")

if [ "$endpoint_count" -gt 0 ]; then
  echo -e "  ${GREEN}✅ Found $endpoint_count API endpoint(s)${NC}"

  # Check for endpoint table structure
  if grep -q "| Method | Endpoint | Description |" "$CTR_FILE"; then
    echo -e "  ${GREEN}✅ Endpoint table structure present${NC}"
  else
    echo -e "  ${YELLOW}⚠️  WARNING: Consider using table format for endpoints${NC}"
    ((WARNINGS++))
  fi
else
  echo -e "  ${YELLOW}⚠️  WARNING: No API endpoints found${NC}"
  echo "           Format: GET /api/v1/resource or similar"
  ((WARNINGS++))
fi

echo ""

# ============================================
# CHECK 6: Data Model Validation
# ============================================
echo "CHECK 6: Data Model Validation"
echo "-----------------------------------------"

# Check for data model definitions (JSON/TypedDict/Pydantic)
if grep -qE '```(json|python|yaml)' "$CTR_FILE"; then
  code_block_count=$(grep -c '```' "$CTR_FILE" || echo "0")
  code_block_count=$((code_block_count / 2))
  echo -e "  ${GREEN}✅ Found $code_block_count code block(s) for data models${NC}"

  # Check for type definitions
  if grep -qE "(TypedDict|BaseModel|dataclass|interface|type\s+)" "$CTR_FILE"; then
    echo -e "  ${GREEN}✅ Typed data models present${NC}"
  else
    echo -e "  ${YELLOW}⚠️  WARNING: Consider using typed data models (TypedDict, Pydantic, etc.)${NC}"
    ((WARNINGS++))
  fi
else
  echo -e "  ${YELLOW}⚠️  WARNING: No code blocks found for data models${NC}"
  ((WARNINGS++))
fi

echo ""

# ============================================
# CHECK 7: Error Handling Section
# ============================================
echo "CHECK 7: Error Handling Section"
echo "-----------------------------------------"

if grep -q "## 4. Error Handling" "$CTR_FILE"; then
  echo -e "  ${GREEN}✅ Error Handling section present${NC}"

  # Check for error code table
  if grep -qE "\|\s*[0-9]{3}\s*\|" "$CTR_FILE"; then
    error_code_count=$(grep -cE "\|\s*[0-9]{3}\s*\|" "$CTR_FILE" || echo "0")
    echo -e "  ${GREEN}✅ Found $error_code_count HTTP error code(s)${NC}"
  else
    echo -e "  ${YELLOW}⚠️  WARNING: No HTTP error codes found in table format${NC}"
    ((WARNINGS++))
  fi

  # Check for error response structure
  if grep -qi "error.*response\|response.*format" "$CTR_FILE"; then
    echo -e "  ${GREEN}✅ Error response format documented${NC}"
  else
    echo -e "  ${YELLOW}⚠️  WARNING: Document error response structure${NC}"
    ((WARNINGS++))
  fi
else
  echo -e "  ${RED}❌ ERROR: Missing Error Handling section${NC}"
  ((ERRORS++))
fi

echo ""

# ============================================
# CHECK 8: Versioning Strategy
# ============================================
echo "CHECK 8: Versioning Strategy"
echo "-----------------------------------------"

if grep -q "## 5. Versioning" "$CTR_FILE"; then
  echo -e "  ${GREEN}✅ Versioning section present${NC}"

  # Check for semantic versioning mention
  if grep -qi "semantic\|semver\|major.*minor.*patch" "$CTR_FILE"; then
    echo -e "  ${GREEN}✅ Semantic versioning strategy documented${NC}"
  else
    echo -e "  ${YELLOW}⚠️  WARNING: Consider documenting semantic versioning strategy${NC}"
    ((WARNINGS++))
  fi

  # Check for breaking changes documentation
  if grep -qi "breaking.*change\|backward.*compat" "$CTR_FILE"; then
    echo -e "  ${GREEN}✅ Breaking changes policy documented${NC}"
  else
    echo -e "  ${YELLOW}⚠️  WARNING: Document breaking changes policy${NC}"
    ((WARNINGS++))
  fi
else
  echo -e "  ${RED}❌ ERROR: Missing Versioning section${NC}"
  ((ERRORS++))
fi

echo ""

# ============================================
# CHECK 9: Traceability Tags (Layer 9)
# ============================================
echo "CHECK 9: Traceability Tags (Layer 9)"
echo "-----------------------------------------"

required_tags=("@brd" "@prd" "@ears" "@bdd" "@adr" "@sys" "@req")

tag_count=0
for tag in "${required_tags[@]}"; do
  if grep -qE "^${tag}:|^\- \`${tag}:" "$CTR_FILE"; then
    echo -e "  ${GREEN}✅ Found: $tag${NC}"
    ((tag_count++))
  else
    echo -e "  ${RED}❌ MISSING: $tag${NC}"
    ((ERRORS++))
  fi
done

# Check optional tags
optional_tags=("@impl" "@spec")
for tag in "${optional_tags[@]}"; do
  if grep -qE "^${tag}:|^\- \`${tag}:" "$CTR_FILE"; then
    echo -e "  ${GREEN}✅ Optional tag present: $tag${NC}"
    ((tag_count++))
  fi
done

echo "  Total traceability tags: $tag_count"
if [ $tag_count -lt 7 ]; then
  echo -e "  ${RED}❌ ERROR: Minimum 7 tags required for Layer 9${NC}"
  ((ERRORS++))
fi

# Check for empty tags
if grep -qE "@[a-z]+:\s*$" "$CTR_FILE"; then
  echo -e "  ${RED}❌ ERROR: Empty tag value found${NC}"
  ((ERRORS++))
fi

echo ""

# ============================================
# CHECK 10: YAML Companion File (if .md)
# ============================================
echo "CHECK 10: YAML Companion File"
echo "-----------------------------------------"

if [[ "$filename" == *.md ]]; then
  yaml_file="${CTR_FILE%.md}.yaml"

  if [ -f "$yaml_file" ]; then
    echo -e "  ${GREEN}✅ YAML companion file exists: $(basename "$yaml_file")${NC}"

    # Validate YAML syntax
    if command -v python3 &> /dev/null; then
      if python3 -c "import yaml; yaml.safe_load(open('$yaml_file'))" 2>/dev/null; then
        echo -e "  ${GREEN}✅ YAML syntax valid${NC}"
      else
        echo -e "  ${RED}❌ ERROR: YAML syntax invalid${NC}"
        ((ERRORS++))
      fi
    else
      echo -e "  ${YELLOW}⚠️  WARNING: Cannot validate YAML (python3 not available)${NC}"
      ((WARNINGS++))
    fi
  else
    echo -e "  ${YELLOW}⚠️  WARNING: No YAML companion file found${NC}"
    echo "           Recommended: Create $(basename "$yaml_file") for machine-readable spec"
    ((WARNINGS++))
  fi
elif [[ "$filename" == *.yaml ]]; then
  echo "  Primary file is YAML format"

  # Validate YAML syntax
  if command -v python3 &> /dev/null; then
    if python3 -c "import yaml; yaml.safe_load(open('$CTR_FILE'))" 2>/dev/null; then
      echo -e "  ${GREEN}✅ YAML syntax valid${NC}"
    else
      echo -e "  ${RED}❌ ERROR: YAML syntax invalid${NC}"
      ((ERRORS++))
    fi
  fi
fi

echo ""

# ============================================
# CHECK 11: Cross-Reference Validation
# ============================================
echo "CHECK 11: Cross-Reference Validation"
echo "-----------------------------------------"

base_dir="$(dirname "$CTR_FILE")"

# Check SPEC references
spec_refs=$(grep -oE "SPEC-[0-9]+" "$CTR_FILE" 2>/dev/null | sort -u || echo "")
if [ -n "$spec_refs" ]; then
  spec_count=$(echo "$spec_refs" | wc -l)
  echo "  Found $spec_count SPEC reference(s)"

  echo "$spec_refs" | while read -r spec_ref; do
    spec_file=$(find "$base_dir/../SPEC" -name "${spec_ref}*.yaml" 2>/dev/null | head -1)
    if [ -n "$spec_file" ]; then
      echo -e "    ${GREEN}✅ $spec_ref exists${NC}"
    else
      echo -e "    ${YELLOW}⚠️  WARNING: $spec_ref not found (may be planned)${NC}"
    fi
  done
else
  echo -e "  ${YELLOW}⚠️  WARNING: No SPEC references found${NC}"
  ((WARNINGS++))
fi

# Check REQ references
req_refs=$(grep -oE "REQ-[0-9]+" "$CTR_FILE" 2>/dev/null | sort -u || echo "")
if [ -n "$req_refs" ]; then
  req_count=$(echo "$req_refs" | wc -l)
  echo "  Found $req_count REQ reference(s)"
fi

echo ""

# ============================================
# CHECK 12: OpenAPI/Swagger Compliance
# ============================================
echo "CHECK 12: OpenAPI/Swagger Compliance"
echo "-----------------------------------------"

if grep -qi "openapi\|swagger" "$CTR_FILE"; then
  echo -e "  ${GREEN}✅ OpenAPI/Swagger reference found${NC}"

  # Check for version
  if grep -qE "openapi:\s*[0-9]+\.[0-9]+" "$CTR_FILE"; then
    openapi_version=$(grep -oE "openapi:\s*[0-9]+\.[0-9]+" "$CTR_FILE" | head -1)
    echo -e "  ${GREEN}✅ OpenAPI version: $openapi_version${NC}"
  fi
else
  echo -e "  ${YELLOW}ℹ️  INFO: No OpenAPI/Swagger specification found${NC}"
  echo "           Consider including OpenAPI 3.0+ specification for API contracts"
fi

echo ""

# ============================================
# SUMMARY
# ============================================
echo "========================================="
echo "VALIDATION SUMMARY"
echo "========================================="
echo "File: $CTR_FILE"
echo "Script Version: ${SCRIPT_VERSION}"
echo "CTR ID: ${CTR_ID:-unknown}"
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
  echo -e "${GREEN}✅ PASSED: All validation checks passed${NC}"
  echo ""
  echo "Document complies with:"
  echo "  - CTR-TEMPLATE.md structure"
  echo "  - doc_flow SDD framework requirements"
  echo "  - Layer 9 artifact standards"
  exit 0
elif [ $ERRORS -eq 0 ]; then
  echo -e "${YELLOW}⚠️  PASSED WITH WARNINGS: Document valid but has $WARNINGS warnings${NC}"
  echo ""
  echo "Recommendations:"
  echo "  - Review warnings for quality improvements"
  echo "  - See CTR-TEMPLATE.md for best practices"
  exit 0
else
  echo -e "${RED}❌ FAILED: $ERRORS critical errors found${NC}"
  echo ""
  echo "Action Required:"
  echo "  1. Fix all errors listed above"
  echo "  2. Review CTR-TEMPLATE.md for requirements"
  echo "  3. Check CTR_CREATION_RULES.md for standards"
  echo "  4. Re-run validation: ./scripts/validate_ctr.sh $CTR_FILE"
  exit 1
fi
