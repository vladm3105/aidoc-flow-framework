#!/bin/bash
# =============================================================================
# SYS Quality Gate Validation Script
# Validates entire SYS document set before REQ creation
# Layer 6 → Layer 7 transition gate
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
SYS_DIR="${1:-docs/SYS}"
VERBOSE="${2:-}"

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

print_header() {
  echo "=========================================="
  echo "SYS Quality Gate Validation (Pre-REQ Gate)"
  echo "=========================================="
  echo "Directory: $SYS_DIR"
  echo "Date: $(TZ=America/New_York date '+%Y-%m-%d %H:%M:%S %Z')"
  echo ""
}

count_files() {
  local count=0
  shopt -s globstar nullglob
  for f in "$SYS_DIR"/**/SYS-[0-9]*_*.md; do
    if [[ ! "$(basename $f)" =~ _index ]]; then
      ((count++)) || true
    fi
  done
  shopt -u globstar nullglob
  echo "$count"
}

# -----------------------------------------------------------------------------
# GATE-01: Placeholder Text Detection
# -----------------------------------------------------------------------------

check_placeholder_text() {
  echo "--- GATE-01: Placeholder Text Detection ---"

  local found=0
  local patterns=("(future SYS)" "(when created)" "(to be defined)" "(pending)" "(TBD)" "[TBD]" "[TODO]")

  for pattern in "${patterns[@]}"; do
    while IFS= read -r line; do
      if [[ -n "$line" ]]; then
        # Extract SYS reference if present
        sys_ref=$(echo "$line" | grep -oE "SYS-[0-9]+" | head -1 || true)
        if [[ -n "$sys_ref" ]]; then
          # Check if the referenced SYS file exists
          if ls "$SYS_DIR/${sys_ref}_"*.md 2>/dev/null | grep -v "_index" >/dev/null; then
            echo -e "${RED}GATE-E001: $line${NC}"
            echo "  → $sys_ref exists but marked as placeholder"
            ((ERRORS++)) || true
            ((found++)) || true
          fi
        fi
      fi
    done < <(grep -rn "$pattern" "$SYS_DIR"/*.md 2>/dev/null || true)
  done

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
  # Layer 7+ artifacts that shouldn't be referenced with specific numbers
  local downstream_patterns="(REQ|SPEC|TASKS-)-[0-9]{2,}"

  while IFS= read -r line; do
    if [[ -n "$line" ]]; then
      # Skip if it's in a layer description or workflow diagram
      if echo "$line" | grep -qE "Layer [0-9]|→|SDD workflow|development workflow"; then
        continue
      fi
      echo -e "${RED}GATE-E002: $line${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done < <(grep -rnE "$downstream_patterns" "$SYS_DIR"/*.md 2>/dev/null | head -20 || true)

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

  local found=0
  # Check for count claims that might be inconsistent
  while IFS= read -r line; do
    if [[ -n "$line" ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${YELLOW}GATE-W001: Verify count - $line${NC}"
      fi
      ((found++)) || true
    fi
  done < <(grep -rnE "[0-9]+ requirements?|[0-9]+ SYS|[0-9]+ interfaces?" "$SYS_DIR"/*.md 2>/dev/null | head -5 || true)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ No obvious count inconsistencies detected${NC}"
  else
    echo -e "${GREEN}  ✓ Found $found count claims (manual verification recommended)${NC}"
  fi
}

# -----------------------------------------------------------------------------
# GATE-04: Index Synchronization
# -----------------------------------------------------------------------------

check_index_sync() {
  echo ""
  echo "--- GATE-04: Index Synchronization ---"

  # Find index file
  local index_file=""
  shopt -s nullglob
  for f in "$SYS_DIR"/SYS-*_index.md "$SYS_DIR"/SYS-00_index.md; do
    if [[ -f "$f" ]]; then
      index_file="$f"
      break
    fi
  done
  shopt -u nullglob

  if [[ -z "$index_file" || ! -f "$index_file" ]]; then
    echo -e "${YELLOW}  Index file not found: $SYS_DIR/SYS-00_index.md${NC}"
    return
  fi

  local found=0
  # Check for files marked "Planned" that actually exist
  while IFS= read -r line; do
    sys_ref=$(echo "$line" | grep -oE "SYS-[0-9]+" | head -1 || true)
    if [[ -n "$sys_ref" ]]; then
      if ls "$SYS_DIR/${sys_ref}_"*.md 2>/dev/null | grep -v "_index" >/dev/null; then
        echo -e "${RED}GATE-E003: $sys_ref exists but marked Planned in index${NC}"
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
# GATE-05: Inter-SYS Cross-Linking (DEPRECATED)
# -----------------------------------------------------------------------------

check_cross_linking() {
  echo ""
  echo "--- GATE-05: Inter-SYS Cross-Linking ---"
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
  shopt -s nullglob
  for f in "$SYS_DIR"/SYS-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index ]]; then continue; fi
    ((total++)) || true

    diagram_count=$(grep -c '```mermaid' "$f" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$diagram_count" || ! "$diagram_count" =~ ^[0-9]+$ ]] && diagram_count=0
    if [[ $diagram_count -eq 0 ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${BLUE}GATE-I001: $(basename $f) has no Mermaid diagrams${NC}"
      fi
      ((INFO++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All SYS have diagrams${NC}"
  else
    echo -e "${BLUE}  ℹ $found of $total SYS files have no Mermaid diagrams${NC}"
  fi
}

# -----------------------------------------------------------------------------
# GATE-07: Glossary Consistency
# -----------------------------------------------------------------------------

check_glossary() {
  echo ""
  echo "--- GATE-07: Glossary Consistency ---"

  local found=0

  # Check for term inconsistency (e.g., system vs System)
  local system_lower=$(grep -roh "the system " "$SYS_DIR"/*.md 2>/dev/null | wc -l || echo 0)
  local system_upper=$(grep -roh "the System " "$SYS_DIR"/*.md 2>/dev/null | wc -l || echo 0)

  if [[ $system_lower -gt 5 && $system_upper -gt 5 ]]; then
    echo -e "${YELLOW}GATE-W003: Mixed 'system' ($system_lower) and 'System' ($system_upper) usage${NC}"
    ((WARNINGS++)) || true
    ((found++)) || true
  fi

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Terminology consistent across corpus${NC}"
  fi
}

# -----------------------------------------------------------------------------
# GATE-08: Element ID Uniqueness
# -----------------------------------------------------------------------------

check_element_ids() {
  echo ""
  echo "--- GATE-08: Element ID Uniqueness ---"

  local duplicates
  duplicates=$(grep -rohE "SYS\.[0-9]+\.[0-9]+\.[0-9]+" "$SYS_DIR"/*.md 2>/dev/null | sort | uniq -d || true)

  if [[ -n "$duplicates" ]]; then
    echo "$duplicates" | while read dup; do
      echo -e "${RED}GATE-E004: Duplicate element ID: $dup${NC}"
      ((ERRORS++)) || true
    done
  else
    echo -e "${GREEN}  ✓ No duplicate element IDs${NC}"
  fi
}

# -----------------------------------------------------------------------------
# GATE-09: Quality Attribute Quantification
# -----------------------------------------------------------------------------

check_quality_quantification() {
  echo ""
  echo "--- GATE-09: Quality Attribute Quantification ---"

  local found=0

  # Check for vague quality attributes
  local vague_patterns=("fast response" "high availability" "highly available" "scalable" "performant" "efficient")

  for pattern in "${vague_patterns[@]}"; do
    while IFS= read -r line; do
      if [[ -n "$line" ]]; then
        echo -e "${YELLOW}GATE-W004: Vague quality attribute - $line${NC}"
        ((WARNINGS++)) || true
        ((found++)) || true
      fi
    done < <(grep -rni "$pattern" "$SYS_DIR"/*.md 2>/dev/null | head -5 || true)
  done

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Quality attributes use measurable specifications${NC}"
  fi
}

# -----------------------------------------------------------------------------
# GATE-10: File Size Compliance
# -----------------------------------------------------------------------------

check_file_size() {
  echo ""
  echo "--- GATE-10: File Size & Token Compliance ---"

  local found=0
  shopt -s nullglob
  for f in "$SYS_DIR"/SYS-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index ]]; then continue; fi

    local words
    words=$(wc -w < "$f")
    local tokens=$((words * 13 / 10))

    if [[ $tokens -gt 20000 ]]; then
      echo -e "${RED}GATE-E006: $(basename "$f") exceeds 20,000 tokens (~$tokens) - MUST SPLIT per Universal Rule${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    elif [[ $tokens -gt 15000 ]]; then
      echo -e "${YELLOW}GATE-W006: $(basename "$f") exceeds 15,000 tokens (~$tokens) - Consider splitting${NC}"
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All files within size limits (≤20k tokens)${NC}"
  fi
}

# -----------------------------------------------------------------------------
# GATE-11: Cumulative Traceability (@brd + @prd + @ears + @bdd + @adr)
# -----------------------------------------------------------------------------

check_traceability() {
  echo ""
  echo "--- GATE-11: Cumulative Traceability (@brd + @prd + @ears + @bdd + @adr) ---"

  local found=0
  shopt -s nullglob
  for f in "$SYS_DIR"/SYS-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE|RULES ]]; then continue; fi

    local has_brd has_prd has_ears has_bdd has_adr
    has_brd=$(grep -c "@brd:" "$f" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$has_brd" || ! "$has_brd" =~ ^[0-9]+$ ]] && has_brd=0
    has_prd=$(grep -c "@prd:" "$f" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$has_prd" || ! "$has_prd" =~ ^[0-9]+$ ]] && has_prd=0
    has_ears=$(grep -c "@ears:" "$f" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$has_ears" || ! "$has_ears" =~ ^[0-9]+$ ]] && has_ears=0
    has_bdd=$(grep -c "@bdd:" "$f" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$has_bdd" || ! "$has_bdd" =~ ^[0-9]+$ ]] && has_bdd=0
    has_adr=$(grep -c "@adr:" "$f" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$has_adr" || ! "$has_adr" =~ ^[0-9]+$ ]] && has_adr=0

    if [[ $has_brd -eq 0 ]]; then
      echo -e "${RED}GATE-E011: $(basename $f) missing @brd traceability tag${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi

    if [[ $has_prd -eq 0 ]]; then
      echo -e "${RED}GATE-E012: $(basename $f) missing @prd traceability tag${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi

    if [[ $has_ears -eq 0 ]]; then
      echo -e "${RED}GATE-E013: $(basename $f) missing @ears traceability tag${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi

    if [[ $has_bdd -eq 0 ]]; then
      echo -e "${RED}GATE-E014: $(basename $f) missing @bdd traceability tag${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi

    if [[ $has_adr -eq 0 ]]; then
      echo -e "${RED}GATE-E015: $(basename $f) missing @adr traceability tag${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All SYS have cumulative traceability tags (5 upstream)${NC}"
  fi
}

# -----------------------------------------------------------------------------
# GATE-12: Quality Attribute Coverage
# -----------------------------------------------------------------------------

check_quality_coverage() {
  echo ""
  echo "--- GATE-12: Quality Attribute Coverage ---"

  local found=0
  local qa_keywords=("performance" "reliability" "security" "maintainability" "scalability" "availability")

  for qa in "${qa_keywords[@]}"; do
    local count
    count=$(grep -ril "$qa" "$SYS_DIR"/SYS-[0-9]*_*.md 2>/dev/null | wc -l || echo 0)
    if [[ $count -eq 0 ]]; then
      echo -e "${YELLOW}GATE-W012: No SYS documents address '$qa'${NC}"
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All quality attributes covered${NC}"
  fi
}

# -----------------------------------------------------------------------------
# GATE-13: Non-Functional Requirement Completeness
# -----------------------------------------------------------------------------

check_nfr_completeness() {
  echo ""
  echo "--- GATE-13: Non-Functional Requirement Completeness ---"

  local found=0
  local nfr_categories=("Performance" "Capacity" "Availability" "Security" "Integration")

  for nfr in "${nfr_categories[@]}"; do
    local count
    count=$(grep -rilE "^#+.*$nfr|$nfr Requirements" "$SYS_DIR"/SYS-[0-9]*_*.md 2>/dev/null | wc -l || echo 0)
    if [[ $count -eq 0 ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${YELLOW}GATE-W013: No SYS documents have '$nfr' section${NC}"
      fi
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All NFR categories addressed${NC}"
  else
    echo -e "${YELLOW}  $found NFR categories may need attention${NC}"
  fi
}

# -----------------------------------------------------------------------------
# GATE-14: Interface Definition Completeness
# -----------------------------------------------------------------------------

check_interface_completeness() {
  echo ""
  echo "--- GATE-14: Interface Definition Completeness ---"

  local found=0
  # Check if interface-related SYS files have protocol/format definitions
  shopt -s nullglob
  for f in "$SYS_DIR"/SYS-[0-9]*_*interface*.md "$SYS_DIR"/SYS-[0-9]*_*api*.md; do
    if [[ ! -f "$f" ]]; then continue; fi

    local has_protocol has_format
    has_protocol=$(grep -ciE "protocol|http|grpc|websocket|rest" "$f" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$has_protocol" || ! "$has_protocol" =~ ^[0-9]+$ ]] && has_protocol=0
    has_format=$(grep -ciE "json|protobuf|xml|format" "$f" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$has_format" || ! "$has_format" =~ ^[0-9]+$ ]] && has_format=0

    if [[ $has_protocol -eq 0 ]]; then
      echo -e "${YELLOW}GATE-W014: $(basename $f) may be missing protocol specification${NC}"
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Interface definitions appear complete${NC}"
  fi
}

# -----------------------------------------------------------------------------
# GATE-15: REQ-Ready Score Threshold
# -----------------------------------------------------------------------------

check_req_ready() {
  echo ""
  echo "--- GATE-15: REQ-Ready Score Threshold ---"

  local found=0
  shopt -s nullglob
  for f in "$SYS_DIR"/SYS-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE|RULES ]]; then continue; fi

    # Check REQ-Ready Score
    local score
    score=$(grep -oE "REQ-Ready Score[^0-9]*[0-9]+" "$f" 2>/dev/null | grep -oE "[0-9]+" | head -1 || echo "")

    if [[ -n "$score" && $score -lt 90 ]]; then
      echo -e "${YELLOW}GATE-W015: $(basename $f) has REQ-Ready Score $score% (target: ≥90%)${NC}"
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All SYS meet REQ-Ready threshold${NC}"
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
    echo -e "${RED}FAILED: $ERRORS error(s) must be fixed before REQ creation${NC}"
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
  if [[ ! -d "$SYS_DIR" ]]; then
    echo -e "${RED}ERROR: Directory not found: $SYS_DIR${NC}"
    exit 3
  fi

  print_header

  local file_count
  file_count=$(count_files)
  echo "Found $file_count SYS documents"
  echo ""

  if [[ $file_count -eq 0 ]]; then
    echo -e "${YELLOW}No SYS documents found to validate${NC}"
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
  check_quality_quantification
  check_file_size
  check_traceability
  check_quality_coverage
  check_nfr_completeness
  check_interface_completeness
  check_req_ready

  print_summary
}

# Run main function
main "$@"
