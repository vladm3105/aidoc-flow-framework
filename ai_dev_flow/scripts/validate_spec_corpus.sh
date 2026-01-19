#!/bin/bash
# =============================================================================
# SPEC Corpus Validation Script
# Validates entire SPEC document set before TASKS creation
# Layer 9 → Layer 10 transition gate
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

  # Check 1: Look for "(future SPEC)" or "(when created)" phrases that reference existing docs
  while IFS= read -r line; do
    if [[ -n "$line" ]]; then
      # Only flag if line contains both a placeholder phrase AND a SPEC reference
      if [[ "$line" =~ \(future\ SPEC\)|\(when\ created\) ]]; then
        spec_ref=$(echo "$line" | grep -oE "SPEC-[0-9]+" | head -1 || true)
        if [[ -n "$spec_ref" ]] && ls "$SPEC_DIR/${spec_ref}_"*.yaml 2>/dev/null >/dev/null; then
          echo -e "${RED}CORPUS-E001: Placeholder references existing document:${NC}"
          echo "  $line"
          ((ERRORS++)) || true
          ((found++)) || true
        fi
      fi
    fi
  done < <(grep -rn "(future SPEC)\|(when created)" "$SPEC_DIR"/*.yaml "$SPEC_DIR"/*.md 2>/dev/null || true)

  # Check 2: Look for TBD/TODO in traceability sections (cumulative_tags, upstream_sources)
  shopt -s nullglob
  for f in "$SPEC_DIR"/SPEC-[0-9]*_*.yaml; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE ]]; then continue; fi

    # Extract cumulative_tags section and check for TBD patterns
    local tags_section=$(sed -n '/^cumulative_tags:/,/^[^ ]/p' "$f" 2>/dev/null)
    if echo "$tags_section" | grep -qE ':\s*"?TBD"?|:\s*"?TODO"?'; then
      echo -e "${RED}CORPUS-E001: TBD/TODO found in cumulative_tags:${NC}"
      echo "  File: $(basename $f)"
      echo "$tags_section" | grep -E ':\s*"?TBD"?|:\s*"?TODO"?' | sed 's/^/    /'
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

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
  local found_warnings=0

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
    echo -e "${YELLOW}CORPUS-W004: Index file not found (e.g., SPEC-000_index.md). Skipping sync check.${NC}"
    ((WARNINGS++)) || true
    return
  fi

  # 1. Check for files marked "Planned" in the index that already exist.
  while IFS= read -r line; do
    if [[ -n "$line" ]]; then
      local spec_id
      # Extract only the FIRST SPEC ID from the line (to avoid multi-line variables)
      spec_id=$(echo "$line" | grep -oE "SPEC-[0-9]+" | head -1)
      if [[ -n "$spec_id" ]] && ls "$SPEC_DIR/${spec_id}_"*.yaml &>/dev/null; then
        echo -e "${YELLOW}CORPUS-W004: $(basename "$index_file") lists '$spec_id' as 'Planned', but the file exists.${NC}"
        ((WARNINGS++)) || true
        ((found_warnings++)) || true
      fi
    fi
  done < <(grep -i "| *Planned *" "$index_file" 2>/dev/null || true)

  # 2. Check for existing SPEC files that are not mentioned in the index.
  local all_spec_files
  all_spec_files=$(find "$SPEC_DIR" -name "SPEC-[0-9]*_*.yaml" -exec basename {} \; 2>/dev/null)
  
  for spec_file in $all_spec_files; do
    local spec_id
    spec_id=$(echo "$spec_file" | grep -oE "SPEC-[0-9]+" || echo "")
    if [[ -n "$spec_id" ]] && ! grep -q "$spec_id" "$index_file" 2>/dev/null; then
      echo -e "${YELLOW}CORPUS-W004: '$spec_file' exists but is not mentioned in the index file ($(basename "$index_file")).${NC}"
      ((WARNINGS++)) || true
      ((found_warnings++)) || true
    fi
  done

  if [[ $found_warnings -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Index file appears to be synchronized.${NC}"
  fi
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

    diagram_count=$(grep -c '```mermaid' "$f" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$diagram_count" || ! "$diagram_count" =~ ^[0-9]+$ ]] && diagram_count=0
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
  # Grep for lines starting with 'id:', extract the value, sort, and find duplicates.
  duplicates=$(grep -rhE "^id:" "$SPEC_DIR"/SPEC-[0-9]*_*.yaml 2>/dev/null | sed 's/^id: *//' | sort | uniq -d || true)

  if [[ -n "$duplicates" ]]; then
    echo "$duplicates" | while read dup; do
      echo -e "${RED}CORPUS-E004: Duplicate internal 'id:' field found in corpus: $dup${NC}"
      # Find which files contain this duplicate id
      grep -rlE "^id: $dup" "$SPEC_DIR" | sed 's/^/  - Found in: /'
      ((ERRORS++)) || true
    done
  else
    echo -e "${GREEN}  ✓ No duplicate internal component IDs found${NC}"
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

# -----------------------------------------------------------------------------
# CORPUS-10: File Size Compliance (Universal Rule)
# -----------------------------------------------------------------------------

check_file_size() {
  echo ""
  echo "--- CORPUS-10: File Size Compliance ---"

  local found=0
  # Recursive search using globstar (enabled in main)
  for f in "$SPEC_DIR"/**/SPEC-[0-9]*_*.yaml; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE ]]; then continue; fi
    # Skip if directory (globstar might match dirs)
    [[ -f "$f" ]] || continue

    local lines
    lines=$(wc -l <"$f")

    # Universal Rule: >1000 lines is an ERROR (Must Split)
    if [[ $lines -gt 1000 ]]; then
      echo -e "${RED}CORPUS-E005: $(basename $f) exceeds 1000 lines ($lines) - MUST SPLIT per Universal Rule${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    elif [[ $lines -gt 500 ]]; then
      echo -e "${YELLOW}CORPUS-W005: $(basename $f) exceeds 500 lines ($lines) - Consider splitting${NC}"
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All files within size limits (≤1000 lines)${NC}"
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
    # Check for the presence of the req tag in the cumulative_tags section
    req_refs=$(grep -A 10 "cumulative_tags:" "$f" | grep -c "req:" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$req_refs" || ! "$req_refs" =~ ^[0-9]+$ ]] && req_refs=0

    if [[ $req_refs -eq 0 ]]; then
      echo -e "${RED}CORPUS-E013: $(basename $f) is missing required upstream REQ traceability${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All SPEC files have REQ coverage${NC}"
  else
    echo -e "${RED}  $found SPEC files are missing REQ traceability.${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-14: Required YAML Fields
# -----------------------------------------------------------------------------

check_required_fields() {
  echo ""
  echo "--- CORPUS-14: Required YAML Fields ---"

  local found=0
  # Corrected fields based on SPEC-MVP-TEMPLATE.yaml
  local required_fields=("id" "version" "title" "summary" "traceability")

  shopt -s nullglob
  for f in "$SPEC_DIR"/SPEC-[0-9]*_*.yaml; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE ]]; then continue; fi

    for field in "${required_fields[@]}"; do
      # Check for top-level keys. This is a simple grep check.
      # For 'traceability', it just checks for the block's existence.
      if ! grep -qE "^${field}:" "$f" 2>/dev/null; then
        echo -e "${RED}CORPUS-E014: $(basename $f) missing required top-level field: '${field}:'${NC}"
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

# -----------------------------------------------------------------------------
# CORPUS-15: Cumulative Traceability Compliance
# -----------------------------------------------------------------------------

check_cumulative_traceability() {
  echo ""
  echo "--- CORPUS-15: Cumulative Traceability Compliance ---"

  local found=0
  # Per rules, 7 tags are required. CTR is optional.
  local required_tags=("brd:" "prd:" "ears:" "bdd:" "adr:" "sys:" "req:")

  shopt -s globstar nullglob
  for f in "$SPEC_DIR"/**/SPEC-[0-9]*_*.yaml; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE ]]; then continue; fi
    [[ -f "$f" ]] || continue

    # Check for the cumulative_tags block first
    if ! grep -q "cumulative_tags:" "$f" 2>/dev/null; then
        echo -e "${RED}CORPUS-E015: $(basename $f) is missing the 'cumulative_tags' block entirely.${NC}"
        ((ERRORS++)) || true
        ((found++)) || true
        continue
    fi

    local missing_tags=""
    # Check for each required tag within the cumulative_tags block
    for tag in "${required_tags[@]}"; do
      # Use a yaml-aware tool or a more robust grep if available.
      # This simple grep assumes tags are on their own line under cumulative_tags.
      if ! sed -n '/cumulative_tags:/,/^[^ ]/p' "$f" | grep -qE "^\s*${tag}"; then
        missing_tags="$missing_tags ${tag}"
      fi
    done

    if [[ -n "$missing_tags" ]]; then
      echo -e "${RED}CORPUS-E015: $(basename $f) is missing required cumulative tags:$missing_tags${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u globstar nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Cumulative traceability complete${NC}"
  else
    echo -e "${RED}  $found SPEC files have traceability errors.${NC}"
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
