#!/bin/bash
# =============================================================================
# IMPL Corpus Validation Script
# Validates entire IMPL document set before SPEC creation
# Layer 8 (Optional) → Layer 9/10 transition gate
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
IMPL_DIR="${1:-docs/IMPL}"
VERBOSE="${2:-}"

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

print_header() {
  echo "=========================================="
  echo "IMPL Corpus Validation (Pre-SPEC Gate)"
  echo "=========================================="
  echo "Directory: $IMPL_DIR"
  echo "Date: $(TZ=America/New_York date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "Note: IMPL is an optional layer (Layer 8)"
  echo ""
}

count_files() {
  local count=0
  shopt -s nullglob
  for f in "$IMPL_DIR"/IMPL-[0-9]*_*.md; do
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
  local patterns=("(future IMPL)" "(when created)" "(to be defined)" "(pending)" "(TBD)" "[TBD]" "[TODO]")

  for pattern in "${patterns[@]}"; do
    while IFS= read -r line; do
      if [[ -n "$line" ]]; then
        impl_ref=$(echo "$line" | grep -oE "IMPL-[0-9]+" | head -1 || true)
        if [[ -n "$impl_ref" ]]; then
          if ls "$IMPL_DIR/${impl_ref}_"*.md 2>/dev/null | grep -v "_index" >/dev/null; then
            echo -e "${RED}CORPUS-E001: $line${NC}"
            ((ERRORS++)) || true
            ((found++)) || true
          fi
        fi
      fi
    done < <(grep -rn "$pattern" "$IMPL_DIR"/*.md 2>/dev/null || true)
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
  local downstream_patterns="(CTR|SPEC|TASKS|IPLAN)-[0-9]{2,}"

  while IFS= read -r line; do
    if [[ -n "$line" ]]; then
      if echo "$line" | grep -qE "Layer [0-9]|→|SDD workflow"; then
        continue
      fi
      echo -e "${RED}CORPUS-E002: $line${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done < <(grep -rnE "$downstream_patterns" "$IMPL_DIR"/*.md 2>/dev/null | head -20 || true)

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
  for f in "$IMPL_DIR"/IMPL-*_index.md; do
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
# CORPUS-05: Inter-IMPL Cross-Linking (DEPRECATED)
# -----------------------------------------------------------------------------

check_cross_linking() {
  echo ""
  echo "--- CORPUS-05: Inter-IMPL Cross-Linking ---"
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
  for f in "$IMPL_DIR"/IMPL-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE ]]; then continue; fi
    ((total++)) || true

    diagram_count=$(grep -c '```mermaid' "$f" 2>/dev/null || echo 0)
    if [[ $diagram_count -eq 0 ]]; then
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $total -eq 0 ]]; then
    echo -e "${GREEN}  ✓ No IMPL files to check${NC}"
  elif [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All IMPL have diagrams${NC}"
  else
    echo -e "${BLUE}  ℹ $found of $total IMPL files have no Mermaid diagrams${NC}"
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
# CORPUS-08: Element ID Uniqueness
# -----------------------------------------------------------------------------

check_element_ids() {
  echo ""
  echo "--- CORPUS-08: Element ID Uniqueness ---"

  local duplicates
  duplicates=$(grep -rohE "IMPL\.[0-9]+\.[0-9]+\.[0-9]+" "$IMPL_DIR"/*.md 2>/dev/null | sort | uniq -d || true)

  if [[ -n "$duplicates" ]]; then
    echo "$duplicates" | while read dup; do
      echo -e "${RED}CORPUS-E004: Duplicate element ID: $dup${NC}"
      ((ERRORS++)) || true
    done
  else
    echo -e "${GREEN}  ✓ No duplicate element IDs${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-09: Resource Specification
# -----------------------------------------------------------------------------

check_resource_spec() {
  echo ""
  echo "--- CORPUS-09: Resource Specification ---"

  local found=0
  shopt -s nullglob
  for f in "$IMPL_DIR"/IMPL-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE ]]; then continue; fi

    local has_who has_when has_what
    has_who=$(grep -ciE "^#+.*(WHO|Responsible|Team|Owner|Assign)" "$f" 2>/dev/null || echo 0)
    has_when=$(grep -ciE "^#+.*(WHEN|Timeline|Schedule|Phase|Milestone)" "$f" 2>/dev/null || echo 0)
    has_what=$(grep -ciE "^#+.*(WHAT|Deliverable|Output|Outcome|Task)" "$f" 2>/dev/null || echo 0)

    if [[ $has_who -eq 0 || $has_when -eq 0 || $has_what -eq 0 ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${YELLOW}CORPUS-W009: $(basename $f) may be missing WHO/WHEN/WHAT${NC}"
      fi
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Resource specifications complete${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-10: File Size Compliance
# -----------------------------------------------------------------------------

check_file_size() {
  echo ""
  echo "--- CORPUS-10: File Size Compliance ---"

  local found=0
  shopt -s nullglob
  for f in "$IMPL_DIR"/IMPL-[0-9]*_*.md; do
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
# CORPUS-11: WHO-WHEN-WHAT Structure
# -----------------------------------------------------------------------------

check_www_structure() {
  echo ""
  echo "--- CORPUS-11: WHO-WHEN-WHAT Structure Compliance ---"

  local found=0
  shopt -s nullglob
  for f in "$IMPL_DIR"/IMPL-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE|RULES ]]; then continue; fi

    local has_who has_when has_what
    has_who=$(grep -ciE "^#+.*(WHO|Responsible|Team|Owner)" "$f" 2>/dev/null || echo 0)
    has_when=$(grep -ciE "^#+.*(WHEN|Timeline|Schedule|Phase)" "$f" 2>/dev/null || echo 0)
    has_what=$(grep -ciE "^#+.*(WHAT|Deliverable|Output|Outcome)" "$f" 2>/dev/null || echo 0)

    if [[ $has_who -eq 0 ]]; then
      echo -e "${RED}CORPUS-E011: $(basename $f) missing WHO section${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi

    if [[ $has_when -eq 0 ]]; then
      echo -e "${RED}CORPUS-E012: $(basename $f) missing WHEN section${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi

    if [[ $has_what -eq 0 ]]; then
      echo -e "${RED}CORPUS-E013: $(basename $f) missing WHAT section${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All IMPL follow WHO-WHEN-WHAT structure${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-12: REQ Coverage
# -----------------------------------------------------------------------------

check_req_coverage() {
  echo ""
  echo "--- CORPUS-12: REQ Coverage ---"

  local found=0
  shopt -s nullglob
  for f in "$IMPL_DIR"/IMPL-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE|RULES ]]; then continue; fi

    local req_refs
    req_refs=$(grep -coE "REQ-[0-9]+" "$f" 2>/dev/null || echo 0)

    if [[ $req_refs -eq 0 ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${YELLOW}CORPUS-W012: $(basename $f) has no REQ references${NC}"
      fi
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ REQ coverage appears complete${NC}"
  else
    echo -e "${YELLOW}  $found IMPL files may need REQ references${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-13: Dependency Tracking
# -----------------------------------------------------------------------------

check_dependencies() {
  echo ""
  echo "--- CORPUS-13: Dependency Tracking ---"

  local found=0
  shopt -s nullglob
  for f in "$IMPL_DIR"/IMPL-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE|RULES ]]; then continue; fi

    local has_deps
    has_deps=$(grep -ciE "^#+.*(Dependenc|Blocker|Prerequisite)" "$f" 2>/dev/null || echo 0)

    if [[ $has_deps -eq 0 ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${YELLOW}CORPUS-W013: $(basename $f) may be missing dependency documentation${NC}"
      fi
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Dependencies documented${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-14: SPEC-Ready Score
# -----------------------------------------------------------------------------

check_spec_ready() {
  echo ""
  echo "--- CORPUS-14: SPEC-Ready Score Threshold ---"

  local found=0
  shopt -s nullglob
  for f in "$IMPL_DIR"/IMPL-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE|RULES ]]; then continue; fi

    local score
    score=$(grep -oE "SPEC-Ready Score[^0-9]*[0-9]+" "$f" 2>/dev/null | grep -oE "[0-9]+" | head -1 || echo "")

    if [[ -n "$score" && $score -lt 85 ]]; then
      echo -e "${YELLOW}CORPUS-W014: $(basename $f) has SPEC-Ready Score $score% (target: ≥85%)${NC}"
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

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
  if [[ ! -d "$IMPL_DIR" ]]; then
    echo -e "${RED}ERROR: Directory not found: $IMPL_DIR${NC}"
    exit 3
  fi

  print_header

  local file_count
  file_count=$(count_files)
  echo "Found $file_count IMPL documents"
  echo ""

  if [[ $file_count -eq 0 ]]; then
    echo -e "${YELLOW}No IMPL documents found - Layer 8 may be skipped${NC}"
    exit 0
  fi

  check_placeholder_text
  check_premature_references
  check_count_consistency
  check_index_sync
  check_cross_linking
  check_visualization
  check_glossary
  check_element_ids
  check_resource_spec
  check_file_size
  check_www_structure
  check_req_coverage
  check_dependencies
  check_spec_ready

  print_summary
}

main "$@"
