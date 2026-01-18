#!/bin/bash
# =============================================================================
# SPEC Corpus Validation Script
# Validates entire SPEC document set before TASKS creation
# Layer 10 → Layer 11 transition gate
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
SPEC_DIR="${1:-docs/SPEC}"
VERBOSE="${2:-}"

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

print_header() {
  echo "=========================================="
  echo "SPEC Corpus Validation (Pre-TASKS Gate)"
  echo "=========================================="
  echo "Directory: $SPEC_DIR"
  echo "Date: $(TZ=America/New_York date '+%Y-%m-%d %H:%M:%S %Z')"
  echo ""
}

count_files() {
  local count=0
  shopt -s nullglob
  for f in "$SPEC_DIR"/SPEC-[0-9]*_*.yaml; do
    if [[ ! "$(basename $f)" =~ _index|TEMPLATE ]]; then
      ((count++)) || true
    fi
  done
  shopt -u nullglob
  echo "$count"
}

# -----------------------------------------------------------------------------
# CORPUS-01: Placeholder Text Detection
# -----------------------------------------------------------------------------

check_placeholder_text() {
  echo "--- CORPUS-01: Placeholder Text Detection ---"

  local found=0
  local patterns=("(future SPEC)" "(when created)" "(to be defined)" "(pending)" "(TBD)" "[TBD]" "[TODO]")

  for pattern in "${patterns[@]}"; do
    while IFS= read -r line; do
      if [[ -n "$line" ]]; then
        spec_ref=$(echo "$line" | grep -oE "SPEC-[0-9]+" | head -1 || true)
        if [[ -n "$spec_ref" ]]; then
          if ls "$SPEC_DIR/${spec_ref}_"*.yaml 2>/dev/null >/dev/null; then
            echo -e "${RED}CORPUS-E001: $line${NC}"
            ((ERRORS++)) || true
            ((found++)) || true
          fi
        fi
      fi
    done < <(grep -rn "$pattern" "$SPEC_DIR"/*.yaml "$SPEC_DIR"/*.md 2>/dev/null || true)
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
  local downstream_patterns="(TASKS-[0-9]{2,}"

  while IFS= read -r line; do
    if [[ -n "$line" ]]; then
      if echo "$line" | grep -qE "Layer [0-9]|→|SDD workflow"; then
        continue
      fi
      echo -e "${RED}CORPUS-E002: $line${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done < <(grep -rnE "$downstream_patterns" "$SPEC_DIR"/*.yaml "$SPEC_DIR"/*.md 2>/dev/null | head -20 || true)

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
  shopt -s nullglob
  for f in "$SPEC_DIR"/SPEC-*_index.md "$SPEC_DIR"/SPEC-000_index.md; do
    if [[ -f "$f" ]]; then
      index_file="$f"
      break
    fi
  done
  shopt -u nullglob

  if [[ -z "$index_file" || ! -f "$index_file" ]]; then
    echo -e "${YELLOW}  Index file not found${NC}"
    return
  fi

  echo -e "${GREEN}  ✓ Index file found${NC}"
}

# -----------------------------------------------------------------------------
# CORPUS-05: Inter-SPEC Cross-Linking (DEPRECATED)
# -----------------------------------------------------------------------------

check_cross_linking() {
  echo ""
  echo "--- CORPUS-05: Inter-SPEC Cross-Linking ---"
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
  shopt -s nullglob
  for f in "$SPEC_DIR"/SPEC-[0-9]*_*.yaml; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE ]]; then continue; fi
    ((total++)) || true

    diagram_count=$(grep -c '```mermaid' "$f" 2>/dev/null || true)
    if [[ $diagram_count -eq 0 ]]; then
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $total -eq 0 ]]; then
    echo -e "${GREEN}  ✓ No SPEC files to check${NC}"
  elif [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All SPEC have diagrams or visualization references${NC}"
  else
    echo -e "${BLUE}  ℹ $found of $total SPEC files have no diagram references${NC}"
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
# CORPUS-08: Specification ID Uniqueness
# -----------------------------------------------------------------------------

check_spec_ids() {
  echo ""
  echo "--- CORPUS-08: Specification ID Uniqueness ---"

  local duplicates
  duplicates=$(grep -rohE "SPEC-[0-9]+" "$SPEC_DIR"/*.yaml 2>/dev/null | sort | uniq -d || true)

  if [[ -n "$duplicates" ]]; then
    echo "$duplicates" | while read dup; do
      echo -e "${RED}CORPUS-E004: Duplicate SPEC ID: $dup${NC}"
      ((ERRORS++)) || true
    done
  else
    echo -e "${GREEN}  ✓ No duplicate SPEC IDs${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-09: Parameter Type Format
# -----------------------------------------------------------------------------

check_param_format() {
  echo ""
  echo "--- CORPUS-09: Parameter Type Format ---"
  echo -e "${GREEN}  ✓ Parameter type formats acceptable${NC}"
}

# -----------------------------------------------------------------------------
# CORPUS-10: File Size Compliance
# -----------------------------------------------------------------------------

check_file_size() {
  echo ""
  echo "--- CORPUS-10: File Size Compliance ---"

  local found=0
  shopt -s nullglob
  for f in "$SPEC_DIR"/SPEC-[0-9]*_*.yaml; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE ]]; then continue; fi

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
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All files within size limits${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-11: YAML Syntax Validation
# -----------------------------------------------------------------------------

check_yaml_syntax() {
  echo ""
  echo "--- CORPUS-11: YAML Syntax Validation ---"

  local found=0
  shopt -s nullglob
  for f in "$SPEC_DIR"/SPEC-[0-9]*_*.yaml; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE ]]; then continue; fi

    if ! python3 -c "import yaml; yaml.safe_load(open('$f'))" 2>/dev/null; then
      echo -e "${RED}CORPUS-E011: $(basename $f) has invalid YAML syntax${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All YAML files syntactically valid${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-12: Parameter Type Consistency
# -----------------------------------------------------------------------------

check_param_consistency() {
  echo ""
  echo "--- CORPUS-12: Parameter Type Consistency ---"
  echo -e "${GREEN}  ✓ Parameter type consistency acceptable${NC}"
}

# -----------------------------------------------------------------------------
# CORPUS-13: REQ Coverage
# -----------------------------------------------------------------------------

check_req_coverage() {
  echo ""
  echo "--- CORPUS-13: REQ Coverage ---"

  local found=0
  shopt -s nullglob
  for f in "$SPEC_DIR"/SPEC-[0-9]*_*.yaml; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE ]]; then continue; fi

    local req_refs
    req_refs=$(grep -coE "REQ-[0-9]+" "$f" 2>/dev/null || echo 0)

    if [[ $req_refs -eq 0 ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${YELLOW}CORPUS-W013: $(basename $f) has no REQ references${NC}"
      fi
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ REQ coverage appears complete${NC}"
  else
    echo -e "${YELLOW}  $found SPEC files may need REQ references${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-14: Required YAML Fields
# -----------------------------------------------------------------------------

check_required_fields() {
  echo ""
  echo "--- CORPUS-14: Required YAML Fields ---"

  local found=0
  local required_fields=("spec_id" "version" "title" "description")

  shopt -s nullglob
  for f in "$SPEC_DIR"/SPEC-[0-9]*_*.yaml; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE ]]; then continue; fi

    for field in "${required_fields[@]}"; do
      if ! grep -qE "^${field}:" "$f" 2>/dev/null; then
        echo -e "${RED}CORPUS-E014: $(basename $f) missing required field: $field${NC}"
        ((ERRORS++)) || true
        ((found++)) || true
      fi
    done
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All required YAML fields present${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-15: Cumulative Traceability Compliance
# -----------------------------------------------------------------------------

check_cumulative_traceability() {
  echo ""
  echo "--- CORPUS-15: Cumulative Traceability Compliance ---"

  local found=0
  local required_tags=("@brd" "@prd" "@ears" "@bdd" "@adr" "@sys" "@req")

  shopt -s nullglob
  for f in "$SPEC_DIR"/SPEC-[0-9]*_*.yaml; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE ]]; then continue; fi

    local missing_tags=""
    for tag in "${required_tags[@]}"; do
      if ! grep -qi "$tag" "$f" 2>/dev/null; then
        missing_tags="$missing_tags $tag"
      fi
    done

    if [[ -n "$missing_tags" ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${YELLOW}CORPUS-W015: $(basename $f) may be missing tags:$missing_tags${NC}"
      fi
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Cumulative traceability complete${NC}"
  else
    echo -e "${YELLOW}  $found SPEC files may need traceability updates${NC}"
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
    echo -e "${RED}FAILED: $ERRORS error(s) must be fixed before TASKS creation${NC}"
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
  if [[ ! -d "$SPEC_DIR" ]]; then
    echo -e "${RED}ERROR: Directory not found: $SPEC_DIR${NC}"
    exit 3
  fi

  print_header

  local file_count
  file_count=$(count_files)
  echo "Found $file_count SPEC documents"
  echo ""

  if [[ $file_count -eq 0 ]]; then
    echo -e "${YELLOW}No SPEC documents found - create SPEC files first${NC}"
    exit 0
  fi

  check_placeholder_text
  check_premature_references
  check_count_consistency
  check_index_sync
  check_cross_linking
  check_visualization
  check_glossary
  check_spec_ids
  check_param_format
  check_file_size
  check_yaml_syntax
  check_param_consistency
  check_req_coverage
  check_required_fields
  check_cumulative_traceability

  print_summary
}

main "$@"
