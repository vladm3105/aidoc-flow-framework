#!/bin/bash
# =============================================================================
# EARS Quality Gate Validation Script
# Validates entire EARS document set before BDD creation
# Layer 3 → Layer 4 transition gate
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
EARS_DIR="${1:-docs/EARS}"
VERBOSE="${2:-}"

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

print_header() {
  echo "=========================================="
  echo "EARS Quality Gate Validation (Pre-BDD Gate)"
  echo "=========================================="
  echo "Directory: $EARS_DIR"
  echo "Date: $(TZ=America/New_York date '+%Y-%m-%d %H:%M:%S %Z')"
  echo ""
}

count_files() {
  local count=0
  shopt -s globstar nullglob
  for f in "$EARS_DIR"/**/EARS-[0-9]*_*.md; do
    if [[ ! "$(basename $f)" =~ _index ]]; then
      ((count++)) || true
    fi
  done
  shopt -u globstar nullglob
  echo "$count"
}

# -----------------------------------------------------------------------------
# CORPUS-01: Placeholder Text Detection
# -----------------------------------------------------------------------------

check_placeholder_text() {
  echo "--- CORPUS-01: Placeholder Text Detection ---"

  local found=0
  local patterns=("(future EARS)" "(when created)" "(to be defined)" "(pending)" "(TBD)" "[TBD]" "[TODO]")

  for pattern in "${patterns[@]}"; do
    while IFS= read -r line; do
      if [[ -n "$line" ]]; then
        # Extract EARS reference if present
        ears_ref=$(echo "$line" | grep -oE "EARS-[0-9]+" | head -1 || true)
        if [[ -n "$ears_ref" ]]; then
          # Check if the referenced EARS file exists
          if ls "$EARS_DIR/${ears_ref}_"*.md 2>/dev/null | grep -v "_index" >/dev/null; then
            echo -e "${RED}CORPUS-E001: $line${NC}"
            echo "  → $ears_ref exists but marked as placeholder"
            ((ERRORS++)) || true
            ((found++)) || true
          fi
        fi
      fi
    done < <(grep -rn "$pattern" "$EARS_DIR"/*.md 2>/dev/null || true)
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
  # Layer 4+ artifacts that shouldn't be referenced with specific numbers
  local downstream_patterns="(BDD|ADR|SYS|REQ|SPEC|TASKS-)-[0-9]{2,}"

  while IFS= read -r line; do
    if [[ -n "$line" ]]; then
      # Skip if it's in a layer description or workflow diagram
      if echo "$line" | grep -qE "Layer [0-9]|→|SDD workflow|development workflow"; then
        continue
      fi
      echo -e "${RED}CORPUS-E002: $line${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done < <(grep -rnE "$downstream_patterns" "$EARS_DIR"/*.md 2>/dev/null | head -20 || true)

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

  local found=0
  # Check for count claims that might be inconsistent
  while IFS= read -r line; do
    if [[ -n "$line" ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${YELLOW}CORPUS-W001: Verify count - $line${NC}"
      fi
      ((found++)) || true
    fi
  done < <(grep -rnE "[0-9]+ requirements?|[0-9]+ EARS" "$EARS_DIR"/*.md 2>/dev/null | head -5 || true)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ No obvious count inconsistencies detected${NC}"
  else
    echo -e "${GREEN}  ✓ Found $found count claims (manual verification recommended)${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-04: Index Synchronization
# -----------------------------------------------------------------------------

check_index_sync() {
  echo ""
  echo "--- CORPUS-04: Index Synchronization ---"

  # Find index file
  local index_file=""
  shopt -s nullglob
  for f in "$EARS_DIR"/EARS-*_index.md "$EARS_DIR"/EARS-00_index.md; do
    if [[ -f "$f" ]]; then
      index_file="$f"
      break
    fi
  done
  shopt -u nullglob

  if [[ -z "$index_file" || ! -f "$index_file" ]]; then
    echo -e "${YELLOW}  Index file not found: $EARS_DIR/EARS-00_index.md${NC}"
    return
  fi

  local found=0
  # Check for files marked "Planned" that actually exist
  while IFS= read -r line; do
    ears_ref=$(echo "$line" | grep -oE "EARS-[0-9]+" | head -1 || true)
    if [[ -n "$ears_ref" ]]; then
      if ls "$EARS_DIR/${ears_ref}_"*.md 2>/dev/null | grep -v "_index" >/dev/null; then
        echo -e "${RED}CORPUS-E003: $ears_ref exists but marked Planned in index${NC}"
        ((ERRORS++)) || true
        ((found++)) || true
      fi
    fi
  done < <(grep -E "\| *Planned *\|" "$index_file" 2>/dev/null || true)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Index synchronized with actual files${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-05: Inter-EARS Cross-Linking (DEPRECATED)
# -----------------------------------------------------------------------------

check_cross_linking() {
  echo ""
  echo "--- CORPUS-05: Inter-EARS Cross-Linking ---"
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
  for f in "$EARS_DIR"/EARS-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index ]]; then continue; fi
    ((total++)) || true

    diagram_count=$(grep -c '```mermaid' "$f" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$diagram_count" || ! "$diagram_count" =~ ^[0-9]+$ ]] && diagram_count=0
    if [[ $diagram_count -eq 0 ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${BLUE}CORPUS-I001: $(basename $f) has no Mermaid diagrams${NC}"
      fi
      ((INFO++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All EARS have diagrams${NC}"
  else
    echo -e "${BLUE}  ℹ $found of $total EARS files have no Mermaid diagrams${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-07: Glossary Consistency
# -----------------------------------------------------------------------------

check_glossary() {
  echo ""
  echo "--- CORPUS-07: Glossary Consistency ---"

  local found=0

  # Check for SHALL/MUST inconsistency
  local shall_count=$(grep -roh "SHALL " "$EARS_DIR"/*.md 2>/dev/null | wc -l || echo 0)
  local must_count=$(grep -roh "MUST " "$EARS_DIR"/*.md 2>/dev/null | wc -l || echo 0)

  if [[ $shall_count -gt 0 && $must_count -gt 0 ]]; then
    echo -e "${YELLOW}CORPUS-W003: Mixed SHALL ($shall_count) and MUST ($must_count) usage${NC}"
    echo "  → Standardize on SHALL for EARS syntax"
    ((WARNINGS++)) || true
    ((found++)) || true
  fi

  # Check for WHEN case inconsistency
  local when_upper=$(grep -roh "WHEN " "$EARS_DIR"/*.md 2>/dev/null | wc -l || echo 0)
  local when_lower=$(grep -roh "when " "$EARS_DIR"/*.md 2>/dev/null | wc -l || echo 0)

  if [[ $when_upper -gt 0 && $when_lower -gt 5 ]]; then
    echo -e "${YELLOW}CORPUS-W003: Mixed WHEN ($when_upper) and when ($when_lower) usage${NC}"
    ((WARNINGS++)) || true
    ((found++)) || true
  fi

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Terminology consistent across corpus${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-08: Element ID Uniqueness
# -----------------------------------------------------------------------------

check_element_ids() {
  echo ""
  echo "--- CORPUS-08: Element ID Uniqueness ---"

  local duplicates
  duplicates=$(grep -rohE "EARS\.[0-9]+\.[0-9]+\.[0-9]+" "$EARS_DIR"/*.md 2>/dev/null | sort | uniq -d || true)

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
# CORPUS-09: Timing Constraint Format
# -----------------------------------------------------------------------------

check_timing_format() {
  echo ""
  echo "--- CORPUS-09: Timing Constraint Format ---"

  local found=0

  # Check for vague timing constraints
  local vague_patterns=("reasonable time" "as soon as possible" "quickly" "timely manner")

  for pattern in "${vague_patterns[@]}"; do
    while IFS= read -r line; do
      if [[ -n "$line" ]]; then
        echo -e "${YELLOW}CORPUS-W004: Vague timing constraint - $line${NC}"
        ((WARNINGS++)) || true
        ((found++)) || true
      fi
    done < <(grep -rni "$pattern" "$EARS_DIR"/*.md 2>/dev/null | head -5 || true)
  done

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Timing constraints use measurable formats${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-10: File Size Compliance
# -----------------------------------------------------------------------------

check_file_size() {
  echo ""
  echo "--- CORPUS-10: File Size Compliance ---"

  shopt -s globstar nullglob
  for f in "$EARS_DIR"/**/EARS-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index ]]; then continue; fi

    local lines
    lines=$(wc -l < "$f")

    # Universal Rule: >1000 lines is an ERROR (Must Split)
    if [[ $lines -gt 1000 ]]; then
      echo -e "${RED}CORPUS-E005: $(basename $f) exceeds 1000 lines ($lines) - MUST SPLIT per Universal Rule${NC}"
      ((ERRORS++)) || true
    elif [[ $lines -gt 500 ]]; then
      echo -e "${YELLOW}CORPUS-W005: $(basename $f) exceeds 500 lines ($lines) - Consider splitting${NC}"
      ((WARNINGS++)) || true
    fi
  done
  shopt -u globstar nullglob
}

# -----------------------------------------------------------------------------
# CORPUS-11: WHEN-THE-SHALL-WITHIN Syntax Compliance
# -----------------------------------------------------------------------------

check_ears_syntax() {
  echo ""
  echo "--- CORPUS-11: WHEN-THE-SHALL-WITHIN Syntax Compliance ---"

  local found=0
  shopt -s nullglob
  for f in "$EARS_DIR"/EARS-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index ]]; then continue; fi

    local shall_count
    shall_count=$(grep -cE "SHALL " "$f" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$shall_count" || ! "$shall_count" =~ ^[0-9]+$ ]] && shall_count=0

    if [[ $shall_count -eq 0 ]]; then
      echo -e "${RED}CORPUS-E011: $(basename $f) has no SHALL statements${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All EARS have SHALL statements${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-12: Cumulative Traceability (@brd + @prd)
# -----------------------------------------------------------------------------

check_traceability() {
  echo ""
  echo "--- CORPUS-12: Cumulative Traceability (@brd + @prd) ---"

  local found=0
  shopt -s nullglob
  for f in "$EARS_DIR"/EARS-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index ]]; then continue; fi

    local has_brd has_prd
    has_brd=$(grep -c "@brd:" "$f" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$has_brd" || ! "$has_brd" =~ ^[0-9]+$ ]] && has_brd=0
    has_prd=$(grep -c "@prd:" "$f" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$has_prd" || ! "$has_prd" =~ ^[0-9]+$ ]] && has_prd=0

    if [[ $has_brd -eq 0 ]]; then
      echo -e "${RED}CORPUS-E012: $(basename $f) missing @brd traceability tag${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi

    if [[ $has_prd -eq 0 ]]; then
      echo -e "${RED}CORPUS-E013: $(basename $f) missing @prd traceability tag${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All EARS have cumulative traceability tags (@brd + @prd)${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-13: BDD Translateability Readiness
# -----------------------------------------------------------------------------

check_bdd_ready() {
  echo ""
  echo "--- CORPUS-13: BDD Translateability Readiness ---"

  local found=0
  shopt -s nullglob
  for f in "$EARS_DIR"/EARS-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index ]]; then continue; fi

    # Check BDD-Ready Score
    local score
    score=$(grep -oE "BDD-Ready Score[^0-9]*[0-9]+" "$f" 2>/dev/null | grep -oE "[0-9]+" | head -1 || echo "")

    if [[ -n "$score" && $score -lt 90 ]]; then
      echo -e "${YELLOW}CORPUS-W013: $(basename $f) has BDD-Ready Score $score% (target: ≥90%)${NC}"
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  # Check for compound requirements
  local compound_count
  compound_count=$(grep -rE "SHALL.*and.*and.*and" "$EARS_DIR"/EARS-[0-9]*_*.md 2>/dev/null | wc -l || echo 0)

  if [[ $compound_count -gt 0 ]]; then
    echo -e "${YELLOW}CORPUS-W014: $compound_count compound requirements detected - consider splitting${NC}"
    ((WARNINGS++)) || true
    ((found++)) || true
  fi

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All EARS are BDD-ready${NC}"
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
    echo -e "${RED}FAILED: $ERRORS error(s) must be fixed before BDD creation${NC}"
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
  # Validate directory exists
  if [[ ! -d "$EARS_DIR" ]]; then
    echo -e "${RED}ERROR: Directory not found: $EARS_DIR${NC}"
    exit 3
  fi

  print_header

  local file_count
  file_count=$(count_files)
  echo "Found $file_count EARS documents"
  echo ""

  if [[ $file_count -eq 0 ]]; then
    echo -e "${YELLOW}No EARS documents found to validate${NC}"
    exit 0
  fi

  # Run all checks
  check_placeholder_text
  check_premature_references
  check_count_consistency
  check_index_sync
  check_cross_linking
  check_visualization
  check_glossary
  check_element_ids
  check_timing_format
  check_file_size
  check_ears_syntax
  check_traceability
  check_bdd_ready

  print_summary
}

# Run main function
main "$@"
