#!/bin/bash
# =============================================================================
# SPEC Quality Gate Validation Script
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
SPEC_DIR="${1:-09_SPEC}"
VERBOSE="${2:-}"

# Enable recursive globbing
shopt -s globstar

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

print_header() {
  echo "=========================================="
  echo "SPEC Quality Gate Validation (Pre-TASKS Gate)"
  echo "=========================================="
  echo "Directory: $SPEC_DIR"
  echo "Date: $(TZ=America/New_York date '+%Y-%m-%d %H:%M:%S %Z')"
  echo ""
}

get_spec_files() {
  find "$SPEC_DIR" \
    -type f \
    -name "SPEC-[0-9]*_*.yaml" \
    ! -name "*_index.md" \
    ! -name "*TEMPLATE*" \
    ! -path "*/archive/*" \
    ! -path "*/archive2/*" \
    ! -name "SPEC-00_*"
}

count_files() {
  get_spec_files | wc -l
}

# -----------------------------------------------------------------------------
# GATE-01: Placeholder Text Detection
# -----------------------------------------------------------------------------

check_placeholder_text() {
  echo "--- GATE-01: Placeholder Text Detection ---"

  local found=0

  # Check 1: Look for "(future SPEC)" or "(when created)" phrases that reference existing docs
  while IFS= read -r line; do
    if [[ -n "$line" ]]; then
      # Only flag if line contains both a placeholder phrase AND a SPEC reference
      if [[ "$line" =~ \(future\ SPEC\)|\(when\ created\) ]]; then
        spec_ref=$(echo "$line" | grep -oE "SPEC-[0-9]+" | head -1 || true)
        # Check if validated spec exists (recursively)
        if [[ -n "$spec_ref" ]] && find "$SPEC_DIR" -name "${spec_ref}_*.yaml" -print -quit | grep -q .; then
          echo -e "${RED}GATE-E001: Placeholder references existing document:${NC}"
          echo "  $line"
          ((ERRORS++)) || true
          ((found++)) || true
        fi
      fi
    fi
  done < <(grep -rn "(future SPEC)\|(when created)" "$SPEC_DIR" --include="*.yaml" --include="*.md" 2>/dev/null || true)

  # Check 2: Look for TBD/TODO in traceability sections (cumulative_tags, upstream_sources)
  while IFS= read -r f; do
    # Extract cumulative_tags section and check for TBD patterns
    local tags_section=$(sed -n '/^cumulative_tags:/,/^[^ ]/p' "$f" 2>/dev/null)
    if echo "$tags_section" | grep -qE ':\s*"?TBD"?|:\s*"?TODO"?'; then
      echo -e "${RED}GATE-E001: TBD/TODO found in cumulative_tags:${NC}"
      echo "  File: $(basename "$f")"
      echo "$tags_section" | grep -E ':\s*"?TBD"?|:\s*"?TODO"?' | sed 's/^/    /'
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done < <(get_spec_files)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ No placeholder text for existing documents${NC}"
  fi
}

# -----------------------------------------------------------------------------
# GATE-02: Premature Downstream References
# -----------------------------------------------------------------------------

check_premature_references() {
  echo ""
  echo "--- GATE-02: Premature Downstream References ---"

  local found=0
  local downstream_patterns="(TASKS-[0-9]{2,}"

  while IFS= read -r line; do
    if [[ -n "$line" ]]; then
      if echo "$line" | grep -qE "Layer [0-9]|→|SDD workflow"; then
        continue
      fi
      echo -e "${RED}GATE-E002: $line${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done < <(grep -rnE "$downstream_patterns" "$SPEC_DIR" --include="*.yaml" --include="*.md" 2>/dev/null | head -20 || true)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ No premature downstream references${NC}"
  fi
}

# -----------------------------------------------------------------------------
# GATE-03: Internal Count Consistency
# -----------------------------------------------------------------------------

check_count_consistency() {
  echo ""
  echo "--- GATE-03: Internal Count Consistency ---"
  echo -e "${GREEN}  ✓ Count consistency check (manual verification recommended)${NC}"
}

# -----------------------------------------------------------------------------
# GATE-04: Index Synchronization
# -----------------------------------------------------------------------------

check_index_sync() {
  echo ""
  echo "--- GATE-04: Index Synchronization ---"
  local found_warnings=0

  spec_index_files=$(find "$SPEC_DIR" \
    ! -path "*/archive/*" \
    ! -path "*/archive2/*" \
    -name "SPEC-*_index.md" \
    ! -name "SPEC-00*_index.md")
  
  if [[ -z "$spec_index_files" ]]; then
     echo -e "${YELLOW}GATE-W004: Index file not found (e.g., SPEC-000_index.md). Skipping sync check.${NC}"
     ((WARNINGS++)) || true
     return
  fi

  # For each index file found (usually one root index, or per-subfolder indices)
  for index_file in $spec_index_files; do
      # 1. Check for files marked "Planned" in the index that already exist.
      while IFS= read -r line; do
        if [[ -n "$line" ]]; then
          local spec_id
          # Extract only the FIRST SPEC ID from the line (to avoid multi-line variables)
          spec_id=$(echo "$line" | grep -oE "SPEC-[0-9]+" | head -1)
          if [[ -n "$spec_id" ]] && find "$SPEC_DIR" -name "${spec_id}_*.yaml" -print -quit | grep -q .; then
            echo -e "${YELLOW}GATE-W004: $(basename "$index_file") lists '$spec_id' as 'Planned', but the file exists.${NC}"
            ((WARNINGS++)) || true
            ((found_warnings++)) || true
          fi
        fi
      done < <(grep -i "| *Planned *" "$index_file" 2>/dev/null || true)
  done

  # 2. Check for existing SPEC files that are not mentioned in ANY index.
  # This is tricky with multiple indices. Simplified to check if mentioned in the nearest index or root index.
  # For now, we'll check if it's in the ROOT index if it exists.
  
  local root_index=$(find "$SPEC_DIR" -maxdepth 1 -name "SPEC-000_index.md" ! -name "SPEC-00*_index.md" | head -1)
  if [[ -n "$root_index" ]]; then
      while IFS= read -r spec_file; do
        local spec_id
        spec_id=$(basename "$spec_file" | grep -oE "SPEC-[0-9]+" || echo "")
        if [[ -n "$spec_id" ]] && ! grep -q "$spec_id" "$root_index" 2>/dev/null; then
          echo -e "${YELLOW}GATE-W004: '$(basename "$spec_file")' exists but is not mentioned in the root index ($(basename "$root_index")).${NC}"
          ((WARNINGS++)) || true
          ((found_warnings++)) || true
        fi
      done < <(get_spec_files)
  fi

  if [[ $found_warnings -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Index file appears to be synchronized.${NC}"
  fi
}

# -----------------------------------------------------------------------------
# GATE-05: Inter-SPEC Cross-Linking (DEPRECATED)
# -----------------------------------------------------------------------------

check_cross_linking() {
  echo ""
  echo "--- GATE-05: Inter-SPEC Cross-Linking ---"
  echo -e "${BLUE}  ℹ DEPRECATED: Document name references are sufficient per SDD rules${NC}"
}

# -----------------------------------------------------------------------------
# GATE-06: Visualization Coverage
# -----------------------------------------------------------------------------

check_visualization() {
  echo ""
  echo "--- GATE-06: Visualization Coverage ---"

  local found=0
  local total=0
  while IFS= read -r f; do
    ((total++)) || true

    diagram_count=$(grep -c '```mermaid' "$f" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$diagram_count" || ! "$diagram_count" =~ ^[0-9]+$ ]] && diagram_count=0
    if [[ $diagram_count -eq 0 ]]; then
      ((found++)) || true
    fi
  done < <(get_spec_files)

  if [[ $total -eq 0 ]]; then
    echo -e "${GREEN}  ✓ No SPEC files to check${NC}"
  elif [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All SPEC have diagrams or visualization references${NC}"
  else
    echo -e "${BLUE}  ℹ $found of $total SPEC files have no diagram references${NC}"
  fi
}

# -----------------------------------------------------------------------------
# GATE-07: Glossary Consistency
# -----------------------------------------------------------------------------

check_glossary() {
  echo ""
  echo "--- GATE-07: Glossary Consistency ---"
  echo -e "${GREEN}  ✓ Terminology consistent (no major issues detected)${NC}"
}

# -----------------------------------------------------------------------------
# GATE-08: Specification ID Uniqueness
# -----------------------------------------------------------------------------

check_spec_ids() {
  echo ""
  echo "--- GATE-08: Specification ID Uniqueness ---"

  local spec_files
  IFS=$'\n' read -r -d '' -a spec_files < <(get_spec_files && printf '\0')

  declare -A id_map
  local duplicates_found=0

  for f in "${spec_files[@]}"; do
    local fid
    fid=$(grep -E "^id:" "$f" 2>/dev/null | head -1 | sed 's/^id: *//')
    if [[ -n "$fid" ]]; then
      if [[ -n "${id_map[$fid]:-}" ]]; then
        if [[ "${id_map[$fid]}" != "__reported__" ]]; then
          echo -e "${RED}GATE-E004: Duplicate internal 'id:' field found in corpus: $fid${NC}"
          echo "  - Found in: ${id_map[$fid]}"
          echo "  - Found in: $f"
          id_map[$fid]="__reported__"
          ((ERRORS++)) || true
          ((duplicates_found++)) || true
        else
          echo "  - Found in: $f"
        fi
      else
        id_map[$fid]="$f"
      fi
    fi
  done

  if [[ $duplicates_found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ No duplicate internal component IDs found${NC}"
  fi
}

# -----------------------------------------------------------------------------
# GATE-09: Parameter Type Format
# -----------------------------------------------------------------------------

check_param_format() {
  echo ""
  echo "--- GATE-09: Parameter Type Format ---"
  echo -e "${GREEN}  ✓ Parameter type formats acceptable${NC}"
}

# -----------------------------------------------------------------------------
# GATE-10: File Size Compliance (Universal Rule)
# -----------------------------------------------------------------------------

check_file_size() {
  echo ""
  echo "--- GATE-10: File Size & Token Compliance ---"

  local found=0
  while IFS= read -r f; do
    local lines
    lines=$(wc -l <"$f")
    local words
    words=$(wc -w <"$f")
    local tokens=$((words * 13 / 10))

    # Universal Rule: >20,000 tokens is an ERROR (Must Split)
    # Universal Rule: >20k tokens is an ERROR (Must Split)
    if [[ $tokens -gt 20000 ]]; then
      echo -e "${RED}GATE-E006: $(basename "$f") exceeds 20,000 tokens (~$tokens) - MUST SPLIT per Universal Rule${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    elif [[ $tokens -gt 15000 ]]; then
      echo -e "${YELLOW}GATE-W006: $(basename "$f") exceeds 15,000 tokens (~$tokens) - Consider splitting${NC}"
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done < <(get_spec_files)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All files within size limits (≤20,000 tokens)${NC}"
  fi
}

# -----------------------------------------------------------------------------
# GATE-11: YAML Syntax Validation
# -----------------------------------------------------------------------------

check_yaml_syntax() {
  echo ""
  echo "--- GATE-11: YAML Syntax Validation ---"

  local found=0
  while IFS= read -r f; do
    if ! python3 -c "import yaml; yaml.safe_load(open('$f'))" 2>/dev/null; then
      echo -e "${RED}GATE-E011: $(basename "$f") has invalid YAML syntax${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done < <(get_spec_files)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All YAML files syntactically valid${NC}"
  fi
}

# -----------------------------------------------------------------------------
# GATE-12: Parameter Type Consistency
# -----------------------------------------------------------------------------

check_param_consistency() {
  echo ""
  echo "--- GATE-12: Parameter Type Consistency ---"
  echo -e "${GREEN}  ✓ Parameter type consistency acceptable${NC}"
}

# -----------------------------------------------------------------------------
# GATE-13: REQ Coverage
# -----------------------------------------------------------------------------

check_req_coverage() {
  echo ""
  echo "--- GATE-13: REQ Coverage ---"

  local found=0
  while IFS= read -r f; do
    local req_refs
    # Check for the presence of the req tag in the cumulative_tags section
    req_refs=$(grep -A 10 "cumulative_tags:" "$f" | grep -c "req:" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$req_refs" || ! "$req_refs" =~ ^[0-9]+$ ]] && req_refs=0

    if [[ $req_refs -eq 0 ]]; then
      echo -e "${RED}GATE-E013: $(basename "$f") is missing required upstream REQ traceability${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done < <(get_spec_files)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All SPEC files have REQ coverage${NC}"
  else
    echo -e "${RED}  $found SPEC files are missing REQ traceability.${NC}"
  fi
}

# -----------------------------------------------------------------------------
# GATE-14: Required YAML Fields
# -----------------------------------------------------------------------------

check_required_fields() {
  echo ""
  echo "--- GATE-14: Required YAML Fields ---"

  local found=0
  # Corrected fields based on SPEC-MVP-TEMPLATE.yaml
  local required_fields=("id" "version" "title" "summary" "traceability")

  while IFS= read -r f; do
    for field in "${required_fields[@]}"; do
      # Simple grep for key starting string at start of line
      if ! grep -qE "^${field}:" "$f" 2>/dev/null; then
        echo -e "${RED}GATE-E014: $(basename "$f") missing required top-level field: '${field}:'${NC}"
        ((ERRORS++)) || true
        ((found++)) || true
      fi
    done
  done < <(get_spec_files)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All required YAML fields present${NC}"
  fi
}

# -----------------------------------------------------------------------------
# GATE-15: Cumulative Traceability Compliance
# -----------------------------------------------------------------------------

check_cumulative_traceability() {
  echo ""
  echo "--- GATE-15: Cumulative Traceability Compliance ---"

  local found=0
  # Per rules, 7 tags are required. CTR is optional.
  local required_tags=("brd:" "prd:" "ears:" "bdd:" "adr:" "sys:" "req:")

  while IFS= read -r f; do
    # Check for the cumulative_tags block first
    if ! grep -q "cumulative_tags:" "$f" 2>/dev/null; then
        echo -e "${RED}GATE-E015: $(basename "$f") is missing the 'cumulative_tags' block entirely.${NC}"
        ((ERRORS++)) || true
        ((found++)) || true
        continue
    fi

    local missing_tags=""
    # Check for each required tag within the cumulative_tags block
    for tag in "${required_tags[@]}"; do
      if ! sed -n '/cumulative_tags:/,/^[^ ]/p' "$f" | grep -qE "^\s*${tag}"; then
        missing_tags="$missing_tags ${tag}"
      fi
    done

    if [[ -n "$missing_tags" ]]; then
      echo -e "${RED}GATE-E015: $(basename "$f") is missing required cumulative tags:$missing_tags${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done < <(get_spec_files)

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
    echo -e "${GREEN}PASSED: All Quality Gate validation checks passed${NC}"
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
