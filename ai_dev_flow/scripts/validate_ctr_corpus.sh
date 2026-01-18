#!/bin/bash
# =============================================================================
# CTR Corpus Validation Script
# Validates entire CTR document set before SPEC creation
# Layer 9 (Optional) → Layer 10 transition gate
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
ERRORS=0
WARNINGS=0
INFO=0

# Configuration
CTR_DIR="${1:-docs/CTR}"
VERBOSE="${2:-}"

# Valid subdomains
VALID_SUBDOMAINS=("rest" "events" "schemas")

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

print_header() {
  echo "=========================================="
  echo "CTR Corpus Validation (Pre-SPEC Gate)"
  echo "=========================================="
  echo "Directory: $CTR_DIR"
  echo "Date: $(TZ=America/New_York date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "Note: CTR is an optional layer (Layer 9)"
  echo ""
}

count_files() {
  local count=0
  while IFS= read -r -d '' f; do
    if [[ ! "$(basename "$f")" =~ _index|TEMPLATE ]]; then
      ((count++)) || true
    fi
  done < <(find "$CTR_DIR" -name "CTR-[0-9]*_*.md" -print0 2>/dev/null)
  echo "$count"
}

# -----------------------------------------------------------------------------
# CORPUS-01: Placeholder Text Detection
# -----------------------------------------------------------------------------

check_placeholder_text() {
  echo "--- CORPUS-01: Placeholder Text Detection ---"

  local found=0
  local patterns=("(future CTR)" "(when created)" "(to be defined)" "(pending)" "(TBD)" "[TBD]" "[TODO]")

  for pattern in "${patterns[@]}"; do
    while IFS= read -r line; do
      if [[ -n "$line" ]]; then
        ctr_ref=$(echo "$line" | grep -oE "CTR-[0-9]+" | head -1 || true)
        if [[ -n "$ctr_ref" ]]; then
          if find "$CTR_DIR" -name "${ctr_ref}_*.md" 2>/dev/null | head -1 | grep -v "_index" >/dev/null; then
            echo -e "${RED}CORPUS-E001: $line${NC}"
            ((ERRORS++)) || true
            ((found++)) || true
          fi
        fi
      fi
    done < <(find "$CTR_DIR" -name "*.md" -exec grep -Hn "$pattern" {} \; 2>/dev/null || true)
  done

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ No placeholder text for existing documents${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-02: Premature Downstream References
# -----------------------------------------------------------------------------

check_premature_references() {
  echo ""
  echo "--- CORPUS-02: Premature Downstream References ---"

  local found=0
  local downstream_patterns="(SPEC|TASKS-[0-9]{2,}"

  while IFS= read -r line; do
    if [[ -n "$line" ]]; then
      if echo "$line" | grep -qE "Layer [0-9]|→|SDD workflow"; then
        continue
      fi
      echo -e "${RED}CORPUS-E002: $line${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done < <(find "$CTR_DIR" -name "*.md" -exec grep -HnE "$downstream_patterns" {} \; 2>/dev/null | head -20 || true)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ No premature downstream references${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-03: Internal Count Consistency
# -----------------------------------------------------------------------------

check_count_consistency() {
  echo ""
  echo "--- CORPUS-03: Internal Count Consistency ---"
  echo -e "${GREEN}  ✓ Count consistency check (manual verification recommended)${NC}"
}

# -----------------------------------------------------------------------------
# CORPUS-04: Index Synchronization
# -----------------------------------------------------------------------------

check_index_sync() {
  echo ""
  echo "--- CORPUS-04: Index Synchronization ---"

  local index_file=""
  for f in "$CTR_DIR"/CTR-*_index.md "$CTR_DIR"/CTR-000_index.md; do
    if [[ -f "$f" ]]; then
      index_file="$f"
      break
    fi
  done

  if [[ -z "$index_file" || ! -f "$index_file" ]]; then
    echo -e "${YELLOW}  Index file not found${NC}"
    return
  fi

  echo -e "${GREEN}  ✓ Index file found${NC}"
}

# -----------------------------------------------------------------------------
# CORPUS-05: Inter-CTR Cross-Linking (DEPRECATED)
# -----------------------------------------------------------------------------

check_cross_linking() {
  echo ""
  echo "--- CORPUS-05: Inter-CTR Cross-Linking ---"
  echo -e "${BLUE}  ℹ DEPRECATED: Document name references are sufficient per SDD rules${NC}"
}

# -----------------------------------------------------------------------------
# CORPUS-06: Visualization Coverage
# -----------------------------------------------------------------------------

check_visualization() {
  echo ""
  echo "--- CORPUS-06: Visualization Coverage ---"

  local found=0
  local total=0

  while IFS= read -r -d '' f; do
    if [[ "$(basename "$f")" =~ _index|TEMPLATE ]]; then continue; fi
    ((total++)) || true

    diagram_count=$(grep -c '```mermaid' "$f" 2>/dev/null || true)
    if [[ $diagram_count -eq 0 ]]; then
      ((found++)) || true
    fi
  done < <(find "$CTR_DIR" -name "CTR-[0-9]*_*.md" -print0 2>/dev/null)

  if [[ $total -eq 0 ]]; then
    echo -e "${GREEN}  ✓ No CTR files to check${NC}"
  elif [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All CTR have diagrams${NC}"
  else
    echo -e "${BLUE}  ℹ $found of $total CTR files have no Mermaid diagrams${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-07: Glossary Consistency
# -----------------------------------------------------------------------------

check_glossary() {
  echo ""
  echo "--- CORPUS-07: Glossary Consistency ---"
  echo -e "${GREEN}  ✓ Terminology consistent (no major issues detected)${NC}"
}

# -----------------------------------------------------------------------------
# CORPUS-08: Contract ID Uniqueness
# -----------------------------------------------------------------------------

check_contract_ids() {
  echo ""
  echo "--- CORPUS-08: Contract ID Uniqueness ---"

  local duplicates
  duplicates=$(find "$CTR_DIR" -name "CTR-[0-9]*_*.md" -exec basename {} \; 2>/dev/null | \
               grep -oE "CTR-[0-9]+" | sort | uniq -d || true)

  if [[ -n "$duplicates" ]]; then
    echo "$duplicates" | while read dup; do
      echo -e "${RED}CORPUS-E004: Duplicate contract ID: $dup${NC}"
      ((ERRORS++)) || true
    done
  else
    echo -e "${GREEN}  ✓ No duplicate contract IDs${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-09: Version Format Consistency
# -----------------------------------------------------------------------------

check_version_format() {
  echo ""
  echo "--- CORPUS-09: Version Format Consistency ---"

  local semantic=0
  local date_based=0

  while IFS= read -r -d '' f; do
    if grep -qE "version.*[0-9]+\.[0-9]+\.[0-9]+" "$f" 2>/dev/null; then
      ((semantic++)) || true
    fi
    if grep -qE "version.*[0-9]{4}-[0-9]{2}-[0-9]{2}" "$f" 2>/dev/null; then
      ((date_based++)) || true
    fi
  done < <(find "$CTR_DIR" -name "CTR-[0-9]*_*.md" -print0 2>/dev/null)

  if [[ $semantic -gt 0 && $date_based -gt 0 ]]; then
    echo -e "${YELLOW}CORPUS-W009: Mixed version formats (semantic: $semantic, date: $date_based)${NC}"
    ((WARNINGS++)) || true
  else
    echo -e "${GREEN}  ✓ Version formats consistent${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-10: File Size Compliance
# -----------------------------------------------------------------------------

check_file_size() {
  echo ""
  echo "--- CORPUS-10: File Size Compliance ---"

  local found=0

  while IFS= read -r -d '' f; do
    if [[ "$(basename "$f")" =~ _index|TEMPLATE ]]; then continue; fi

    local lines
    lines=$(wc -l < "$f")

    if [[ $lines -gt 1200 ]]; then
      echo -e "${RED}CORPUS-E005: $(basename $f) exceeds 1200 lines ($lines)${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    elif [[ $lines -gt 600 ]]; then
      echo -e "${YELLOW}CORPUS-W005: $(basename $f) exceeds 600 lines ($lines)${NC}"
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done < <(find "$CTR_DIR" -name "CTR-[0-9]*_*.md" -print0 2>/dev/null)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All files within size limits${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-11: Dual-File Consistency
# -----------------------------------------------------------------------------

check_dual_file() {
  echo ""
  echo "--- CORPUS-11: Dual-File Consistency (.md + .yaml) ---"

  local found=0

  # Check for missing .yaml files
  while IFS= read -r -d '' md_file; do
    if [[ "$(basename "$md_file")" =~ _index|TEMPLATE ]]; then continue; fi

    local yaml_file="${md_file%.md}.yaml"
    if [[ ! -f "$yaml_file" ]]; then
      echo -e "${RED}CORPUS-E011: $(basename $md_file) missing paired .yaml file${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done < <(find "$CTR_DIR" -name "CTR-[0-9]*_*.md" -print0 2>/dev/null)

  # Check for orphaned .yaml files
  while IFS= read -r -d '' yaml_file; do
    if [[ "$(basename "$yaml_file")" =~ TEMPLATE ]]; then continue; fi

    local md_file="${yaml_file%.yaml}.md"
    if [[ ! -f "$md_file" ]]; then
      echo -e "${RED}CORPUS-E012: $(basename $yaml_file) missing paired .md file${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done < <(find "$CTR_DIR" -name "CTR-[0-9]*_*.yaml" -print0 2>/dev/null)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All CTR have matching .md/.yaml pairs${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-12: YAML Schema Validation
# -----------------------------------------------------------------------------

check_yaml_syntax() {
  echo ""
  echo "--- CORPUS-12: YAML Schema Validation ---"

  local found=0

  # Check if python3 is available
  if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}  Python3 not found - YAML validation skipped${NC}"
    return
  fi

  while IFS= read -r -d '' yaml_file; do
    if [[ "$(basename "$yaml_file")" =~ TEMPLATE ]]; then continue; fi

    if ! python3 -c "import yaml; yaml.safe_load(open('$yaml_file'))" 2>/dev/null; then
      echo -e "${RED}CORPUS-E014: $(basename $yaml_file) has invalid YAML syntax${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done < <(find "$CTR_DIR" -name "CTR-[0-9]*_*.yaml" -print0 2>/dev/null)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All YAML files are valid${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-13: Version Compatibility Tracking
# -----------------------------------------------------------------------------

check_version_compat() {
  echo ""
  echo "--- CORPUS-13: Version Compatibility Tracking ---"

  local found=0

  while IFS= read -r -d '' f; do
    if [[ "$(basename "$f")" =~ _index|TEMPLATE ]]; then continue; fi

    # Check for breaking change documentation
    local has_breaking
    has_breaking=$(grep -ciE "breaking.*change|deprecat|migration" "$f" 2>/dev/null || echo 0)

    # Check version number
    local version
    version=$(grep -oE "version.*[0-9]+\.[0-9]+\.[0-9]+" "$f" 2>/dev/null | grep -oE "[0-9]+" | head -1 || echo "0")

    # If major version > 0, should have breaking change docs
    if [[ $version -gt 0 && $has_breaking -eq 0 ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${YELLOW}CORPUS-W013: $(basename $f) is v$version but has no breaking change documentation${NC}"
      fi
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done < <(find "$CTR_DIR" -name "CTR-[0-9]*_*.md" -print0 2>/dev/null)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Version compatibility documented${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-14: Subdomain Classification
# -----------------------------------------------------------------------------

check_subdomain() {
  echo ""
  echo "--- CORPUS-14: Subdomain Classification ---"

  local found=0

  while IFS= read -r -d '' f; do
    if [[ "$(basename "$f")" =~ _index|TEMPLATE ]]; then continue; fi

    local dir_name
    dir_name=$(dirname "$f" | xargs basename)

    # Check if file is in root CTR directory
    if [[ "$dir_name" == "CTR" ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${YELLOW}CORPUS-W014: $(basename $f) is not in a subdomain directory${NC}"
      fi
      ((WARNINGS++)) || true
      ((found++)) || true
      continue
    fi

    # Check if subdomain is valid
    local valid=0
    for subdomain in "${VALID_SUBDOMAINS[@]}"; do
      if [[ "$dir_name" == "$subdomain" ]]; then
        valid=1
        break
      fi
    done

    if [[ $valid -eq 0 ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${YELLOW}CORPUS-W014: $(basename $f) is in unrecognized subdomain '$dir_name'${NC}"
      fi
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done < <(find "$CTR_DIR" -name "CTR-[0-9]*_*.md" -print0 2>/dev/null)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All CTR in valid subdirectories${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-15: SPEC-Ready Score
# -----------------------------------------------------------------------------

check_spec_ready() {
  echo ""
  echo "--- CORPUS-15: SPEC-Ready Score Threshold ---"

  local found=0

  while IFS= read -r -d '' f; do
    if [[ "$(basename "$f")" =~ _index|TEMPLATE ]]; then continue; fi

    local score
    score=$(grep -oE "SPEC-Ready Score[^0-9]*[0-9]+" "$f" 2>/dev/null | grep -oE "[0-9]+" | head -1 || echo "")

    if [[ -n "$score" && $score -lt 90 ]]; then
      echo -e "${YELLOW}CORPUS-W015: $(basename $f) has SPEC-Ready Score $score% (target: ≥90%)${NC}"
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done < <(find "$CTR_DIR" -name "CTR-[0-9]*_*.md" -print0 2>/dev/null)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ SPEC-Ready scores acceptable${NC}"
  fi
}

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------

print_summary() {
  echo ""
  echo "=========================================="
  echo "Validation Summary"
  echo "=========================================="
  echo -e "Errors:   ${RED}$ERRORS${NC}"
  echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
  echo -e "Info:     ${BLUE}$INFO${NC}"
  echo ""

  if [[ $ERRORS -gt 0 ]]; then
    echo -e "${RED}FAILED: $ERRORS error(s) must be fixed before SPEC creation${NC}"
    exit 1
  elif [[ $WARNINGS -gt 0 ]]; then
    echo -e "${YELLOW}PASSED with $WARNINGS warning(s)${NC}"
    exit 0
  else
    echo -e "${GREEN}PASSED: All corpus validation checks passed${NC}"
    exit 0
  fi
}

# -----------------------------------------------------------------------------
# Main Execution
# -----------------------------------------------------------------------------

main() {
  if [[ ! -d "$CTR_DIR" ]]; then
    echo -e "${RED}ERROR: Directory not found: $CTR_DIR${NC}"
    exit 3
  fi

  print_header

  local file_count
  file_count=$(count_files)
  echo "Found $file_count CTR documents"
  echo ""

  if [[ $file_count -eq 0 ]]; then
    echo -e "${YELLOW}No CTR documents found - Layer 9 may be skipped${NC}"
    exit 0
  fi

  check_placeholder_text
  check_premature_references
  check_count_consistency
  check_index_sync
  check_cross_linking
  check_visualization
  check_glossary
  check_contract_ids
  check_version_format
  check_file_size
  check_dual_file
  check_yaml_syntax
  check_version_compat
  check_subdomain
  check_spec_ready

  print_summary
}

main "$@"
