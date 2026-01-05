#!/bin/bash
# =============================================================================
# BDD Corpus Validation Script
# Validates entire BDD document set before ADR creation
# Layer 4 → Layer 5 transition gate
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
BDD_DIR="${1:-docs/BDD}"
VERBOSE="${2:-}"

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

print_header() {
  echo "=========================================="
  echo "BDD Corpus Validation (Pre-ADR Gate)"
  echo "=========================================="
  echo "Directory: $BDD_DIR"
  echo "Date: $(TZ=America/New_York date '+%Y-%m-%d %H:%M:%S %Z')"
  echo ""
}

count_files() {
  local count=0
  shopt -s nullglob
  for f in "$BDD_DIR"/BDD-[0-9]*_*.feature "$BDD_DIR"/BDD-[0-9]*_*.md; do
    if [[ ! "$(basename $f)" =~ _index|TEMPLATE|RULES ]]; then
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
  local patterns=("(future BDD)" "(when created)" "(to be defined)" "(pending)" "(TBD)" "[TBD]" "[TODO]")

  for pattern in "${patterns[@]}"; do
    while IFS= read -r line; do
      if [[ -n "$line" ]]; then
        bdd_ref=$(echo "$line" | grep -oE "BDD-[0-9]+" | head -1 || true)
        if [[ -n "$bdd_ref" ]]; then
          if ls "$BDD_DIR/${bdd_ref}_"*.feature 2>/dev/null | grep -v "_index" >/dev/null; then
            echo -e "${RED}CORPUS-E001: $line${NC}"
            echo "  → $bdd_ref exists but marked as placeholder"
            ((ERRORS++)) || true
            ((found++)) || true
          fi
        fi
      fi
    done < <(grep -rn "$pattern" "$BDD_DIR"/*.feature "$BDD_DIR"/*.md 2>/dev/null || true)
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
  # Layer 5+ artifacts that shouldn't be referenced with specific numbers
  local downstream_patterns="(ADR|SYS|REQ|SPEC|TASKS|IPLAN)-[0-9]{2,}"

  while IFS= read -r line; do
    if [[ -n "$line" ]]; then
      if echo "$line" | grep -qE "Layer [0-9]|→|SDD workflow|development workflow"; then
        continue
      fi
      echo -e "${RED}CORPUS-E002: $line${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done < <(grep -rnE "$downstream_patterns" "$BDD_DIR"/*.feature "$BDD_DIR"/*.md 2>/dev/null | head -20 || true)

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
  while IFS= read -r line; do
    if [[ -n "$line" ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${YELLOW}CORPUS-W001: Verify count - $line${NC}"
      fi
      ((found++)) || true
    fi
  done < <(grep -rnE "[0-9]+ scenarios?|[0-9]+ features?" "$BDD_DIR"/*.feature "$BDD_DIR"/*.md 2>/dev/null | head -5 || true)

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

  local index_file=""
  shopt -s nullglob
  for f in "$BDD_DIR"/BDD-*_index.md "$BDD_DIR"/BDD-00_index.md; do
    if [[ -f "$f" ]]; then
      index_file="$f"
      break
    fi
  done
  shopt -u nullglob

  if [[ -z "$index_file" || ! -f "$index_file" ]]; then
    echo -e "${YELLOW}  Index file not found: $BDD_DIR/BDD-00_index.md${NC}"
    return
  fi

  local found=0
  while IFS= read -r line; do
    bdd_ref=$(echo "$line" | grep -oE "BDD-[0-9]+" | head -1 || true)
    if [[ -n "$bdd_ref" ]]; then
      if ls "$BDD_DIR/${bdd_ref}_"*.feature 2>/dev/null | grep -v "_index" >/dev/null; then
        echo -e "${RED}CORPUS-E003: $bdd_ref exists but marked Planned in index${NC}"
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
# CORPUS-05: Inter-BDD Cross-Linking (DEPRECATED)
# -----------------------------------------------------------------------------

check_cross_linking() {
  echo ""
  echo "--- CORPUS-05: Inter-BDD Cross-Linking ---"
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
  for f in "$BDD_DIR"/BDD-[0-9]*_*.feature "$BDD_DIR"/BDD-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE|RULES ]]; then continue; fi
    ((total++)) || true

    diagram_count=$(grep -c '```mermaid' "$f" 2>/dev/null || echo 0)
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
    echo -e "${GREEN}  ✓ All BDD have diagrams${NC}"
  else
    echo -e "${BLUE}  ℹ $found of $total BDD files have no Mermaid diagrams${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-07: Glossary Consistency
# -----------------------------------------------------------------------------

check_glossary() {
  echo ""
  echo "--- CORPUS-07: Glossary Consistency ---"

  local found=0

  # Check for Given/When/Then case inconsistency
  local given_upper=$(grep -roh "Given " "$BDD_DIR"/*.feature 2>/dev/null | wc -l || echo 0)
  local given_lower=$(grep -roh "given " "$BDD_DIR"/*.feature 2>/dev/null | wc -l || echo 0)

  if [[ $given_upper -gt 0 && $given_lower -gt 0 ]]; then
    echo -e "${YELLOW}CORPUS-W003: Mixed 'Given' ($given_upper) and 'given' ($given_lower) usage${NC}"
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
  duplicates=$(grep -rohE "BDD\.[0-9]+\.[0-9]+\.[0-9]+" "$BDD_DIR"/*.feature "$BDD_DIR"/*.md 2>/dev/null | sort | uniq -d || true)

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
  local vague_patterns=("reasonable time" "as soon as possible" "quickly" "timely manner")

  for pattern in "${vague_patterns[@]}"; do
    while IFS= read -r line; do
      if [[ -n "$line" ]]; then
        echo -e "${YELLOW}CORPUS-W004: Vague timing constraint - $line${NC}"
        ((WARNINGS++)) || true
        ((found++)) || true
      fi
    done < <(grep -rni "$pattern" "$BDD_DIR"/*.feature 2>/dev/null | head -5 || true)
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

  shopt -s nullglob
  for f in "$BDD_DIR"/BDD-[0-9]*_*.feature "$BDD_DIR"/BDD-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE|RULES ]]; then continue; fi

    local lines
    lines=$(wc -l < "$f")

    if [[ $lines -gt 1200 ]]; then
      echo -e "${RED}CORPUS-E005: $(basename $f) exceeds 1200 lines ($lines)${NC}"
      ((ERRORS++)) || true
    elif [[ $lines -gt 600 ]]; then
      echo -e "${YELLOW}CORPUS-W005: $(basename $f) exceeds 600 lines ($lines)${NC}"
      ((WARNINGS++)) || true
    fi
  done
  shopt -u nullglob
}

# -----------------------------------------------------------------------------
# CORPUS-11: Given-When-Then Syntax Compliance
# -----------------------------------------------------------------------------

check_gherkin_syntax() {
  echo ""
  echo "--- CORPUS-11: Given-When-Then Syntax Compliance ---"

  local found=0
  shopt -s nullglob
  for f in "$BDD_DIR"/BDD-[0-9]*_*.feature; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE ]]; then continue; fi

    # Check for Feature declaration
    if ! grep -qE "^Feature:" "$f" 2>/dev/null; then
      echo -e "${RED}CORPUS-E011: $(basename $f) missing Feature: declaration${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi

    # Check for Given/When/Then
    local has_given has_when has_then
    has_given=$(grep -cE "^\s+Given " "$f" 2>/dev/null || echo 0)
    has_when=$(grep -cE "^\s+When " "$f" 2>/dev/null || echo 0)
    has_then=$(grep -cE "^\s+Then " "$f" 2>/dev/null || echo 0)

    if [[ $has_given -eq 0 && $has_when -eq 0 && $has_then -eq 0 ]]; then
      echo -e "${RED}CORPUS-E011: $(basename $f) has no Given/When/Then steps${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All BDD files have proper Gherkin syntax${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-12: Cumulative Traceability (@brd + @prd + @ears)
# -----------------------------------------------------------------------------

check_traceability() {
  echo ""
  echo "--- CORPUS-12: Cumulative Traceability (@brd + @prd + @ears) ---"

  local found=0
  shopt -s nullglob
  for f in "$BDD_DIR"/BDD-[0-9]*_*.feature; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE ]]; then continue; fi

    local has_brd has_prd has_ears
    has_brd=$(grep -c "@brd:" "$f" 2>/dev/null || echo 0)
    has_prd=$(grep -c "@prd:" "$f" 2>/dev/null || echo 0)
    has_ears=$(grep -c "@ears:" "$f" 2>/dev/null || echo 0)

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

    if [[ $has_ears -eq 0 ]]; then
      echo -e "${RED}CORPUS-E014: $(basename $f) missing @ears traceability tag${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All BDD have cumulative traceability tags (@brd + @prd + @ears)${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-13: Feature File Aggregation (Split-File Consistency)
# -----------------------------------------------------------------------------

check_split_files() {
  echo ""
  echo "--- CORPUS-13: Feature File Aggregation (Split-File Consistency) ---"

  local found=0
  shopt -s nullglob
  for dir in "$BDD_DIR"/BDD-[0-9]*_*/; do
    if [[ -d "$dir" ]]; then
      if ! ls "$dir"/BDD-*.0_*.md 2>/dev/null >/dev/null; then
        echo -e "${YELLOW}CORPUS-W013: Split BDD $(basename $dir) missing index file${NC}"
        ((WARNINGS++)) || true
        ((found++)) || true
      fi
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Split-file structures are consistent${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-14: Step Reusability (Duplicate Step Detection)
# -----------------------------------------------------------------------------

check_step_reusability() {
  echo ""
  echo "--- CORPUS-14: Step Reusability (Duplicate Step Detection) ---"

  shopt -s nullglob
  local step_duplicates
  step_duplicates=$(grep -rhE "^\s+(Given|When|Then|And|But) " "$BDD_DIR"/*.feature 2>/dev/null | \
    sed 's/^\s*//' | sort | uniq -c | sort -rn | \
    awk '$1 > 2 {print}' | head -5 || true)

  if [[ -n "$step_duplicates" ]]; then
    echo -e "${BLUE}  ℹ Frequently used steps (consider step definitions):${NC}"
    echo "$step_duplicates" | while read line; do
      echo -e "${BLUE}    $line${NC}"
      ((INFO++)) || true
    done
  else
    echo -e "${GREEN}  ✓ No frequently duplicated steps detected${NC}"
  fi
  shopt -u nullglob
}

# -----------------------------------------------------------------------------
# CORPUS-15: ADR-Ready Score Threshold
# -----------------------------------------------------------------------------

check_adr_ready() {
  echo ""
  echo "--- CORPUS-15: ADR-Ready Score Threshold ---"

  local found=0
  shopt -s nullglob
  for f in "$BDD_DIR"/BDD-[0-9]*_*.feature "$BDD_DIR"/BDD-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE|RULES ]]; then continue; fi

    local score
    score=$(grep -oE "ADR-Ready Score[^0-9]*[0-9]+" "$f" 2>/dev/null | grep -oE "[0-9]+" | head -1 || echo "")

    if [[ -n "$score" && $score -lt 90 ]]; then
      echo -e "${YELLOW}CORPUS-W015: $(basename $f) has ADR-Ready Score $score% (target: ≥90%)${NC}"
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All BDD are ADR-ready${NC}"
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
    echo -e "${RED}FAILED: $ERRORS error(s) must be fixed before ADR creation${NC}"
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
  if [[ ! -d "$BDD_DIR" ]]; then
    echo -e "${RED}ERROR: Directory not found: $BDD_DIR${NC}"
    exit 3
  fi

  print_header

  local file_count
  file_count=$(count_files)
  echo "Found $file_count BDD documents"
  echo ""

  if [[ $file_count -eq 0 ]]; then
    echo -e "${YELLOW}No BDD documents found to validate${NC}"
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
  check_gherkin_syntax
  check_traceability
  check_split_files
  check_step_reusability
  check_adr_ready

  print_summary
}

main "$@"
