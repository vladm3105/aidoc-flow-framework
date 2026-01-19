#!/bin/bash
# =============================================================================
# ADR Quality Gate Validation Script
# Validates entire ADR document set before SYS creation
# Layer 5 → Layer 6 transition gate
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
ADR_DIR="${1:-docs/ADR}"
VERBOSE="${2:-}"

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

print_header() {
  echo "=========================================="
  echo "ADR Quality Gate Validation (Pre-SYS Gate)"
  echo "=========================================="
  echo "Directory: $ADR_DIR"
  echo "Date: $(TZ=America/New_York date '+%Y-%m-%d %H:%M:%S %Z')"
  echo ""
}

count_files() {
  local count=0
  shopt -s globstar nullglob
  for f in "$ADR_DIR"/**/ADR-[0-9]*_*.md; do
    if [[ ! "$(basename $f)" =~ _index|TEMPLATE|RULES ]]; then
      ((count++)) || true
    fi
  done
  shopt -u globstar nullglob
  echo "$count"
}

is_adr_ref() {
  local filename="$1"
  [[ "$filename" =~ ADR-REF ]]
}

# -----------------------------------------------------------------------------
# CORPUS-01: Placeholder Text Detection
# -----------------------------------------------------------------------------

check_placeholder_text() {
  echo "--- CORPUS-01: Placeholder Text Detection ---"

  local found=0
  local patterns=("(future ADR)" "(when created)" "(to be defined)" "(pending)" "(TBD)" "[TBD]" "[TODO]")

  for pattern in "${patterns[@]}"; do
    while IFS= read -r line; do
      if [[ -n "$line" ]]; then
        adr_ref=$(echo "$line" | grep -oE "ADR-[0-9]+" | head -1 || true)
        if [[ -n "$adr_ref" ]]; then
          if ls "$ADR_DIR/${adr_ref}_"*.md 2>/dev/null | grep -v "_index" >/dev/null; then
            echo -e "${RED}CORPUS-E001: $line${NC}"
            echo "  → $adr_ref exists but marked as placeholder"
            ((ERRORS++)) || true
            ((found++)) || true
          fi
        fi
      fi
    done < <(grep -rn "$pattern" "$ADR_DIR"/*.md 2>/dev/null || true)
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
  # Layer 6+ artifacts that shouldn't be referenced with specific numbers
  local downstream_patterns="(SYS|REQ|SPEC|TASKS-)-[0-9]{2,}"

  while IFS= read -r line; do
    if [[ -n "$line" ]]; then
      if echo "$line" | grep -qE "Layer [0-9]|→|SDD workflow|development workflow"; then
        continue
      fi
      echo -e "${RED}CORPUS-E002: $line${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done < <(grep -rnE "$downstream_patterns" "$ADR_DIR"/*.md 2>/dev/null | head -20 || true)

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
  done < <(grep -rnE "[0-9]+ alternatives?|[0-9]+ consequences?|[0-9]+ decisions?" "$ADR_DIR"/*.md 2>/dev/null | head -5 || true)

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
  for f in "$ADR_DIR"/ADR-*_index.md "$ADR_DIR"/ADR-00_index.md; do
    if [[ -f "$f" ]]; then
      index_file="$f"
      break
    fi
  done
  shopt -u nullglob

  if [[ -z "$index_file" || ! -f "$index_file" ]]; then
    echo -e "${YELLOW}  Index file not found: $ADR_DIR/ADR-00_index.md${NC}"
    return
  fi

  local found=0
  while IFS= read -r line; do
    adr_ref=$(echo "$line" | grep -oE "ADR-[0-9]+" | head -1 || true)
    if [[ -n "$adr_ref" ]]; then
      if ls "$ADR_DIR/${adr_ref}_"*.md 2>/dev/null | grep -v "_index" >/dev/null; then
        echo -e "${RED}CORPUS-E003: $adr_ref exists but marked Planned in index${NC}"
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
# CORPUS-05: Inter-ADR Cross-Linking (DEPRECATED)
# -----------------------------------------------------------------------------

check_cross_linking() {
  echo ""
  echo "--- CORPUS-05: Inter-ADR Cross-Linking ---"
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
  for f in "$ADR_DIR"/ADR-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE|RULES ]]; then continue; fi
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
    echo -e "${GREEN}  ✓ All ADRs have diagrams${NC}"
  else
    echo -e "${BLUE}  ℹ $found of $total ADR files have no Mermaid diagrams${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-07: Glossary Consistency
# -----------------------------------------------------------------------------

check_glossary() {
  echo ""
  echo "--- CORPUS-07: Glossary Consistency ---"

  local found=0

  # Check for Decision/decision inconsistency
  local decision_upper=$(grep -roh "Decision:" "$ADR_DIR"/*.md 2>/dev/null | wc -l || echo 0)
  local decision_lower=$(grep -roh "decision:" "$ADR_DIR"/*.md 2>/dev/null | wc -l || echo 0)

  if [[ $decision_upper -gt 0 && $decision_lower -gt 5 ]]; then
    echo -e "${YELLOW}CORPUS-W003: Mixed 'Decision:' ($decision_upper) and 'decision:' ($decision_lower) usage${NC}"
    ((WARNINGS++)) || true
    ((found++)) || true
  fi

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Terminology consistent across corpus${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-08: Element ID Uniqueness (Document-level for ADR)
# -----------------------------------------------------------------------------

check_element_ids() {
  echo ""
  echo "--- CORPUS-08: ADR Reference Uniqueness ---"

  local duplicates
  duplicates=$(ls "$ADR_DIR"/ADR-[0-9]*_*.md 2>/dev/null | \
    xargs -I{} basename {} | grep -oE "ADR-[0-9]+" | sort | uniq -d || true)

  if [[ -n "$duplicates" ]]; then
    echo "$duplicates" | while read dup; do
      echo -e "${RED}CORPUS-E004: Duplicate ADR reference: $dup${NC}"
      ((ERRORS++)) || true
    done
  else
    echo -e "${GREEN}  ✓ No duplicate ADR references${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-09: Decision Status Tracking
# -----------------------------------------------------------------------------

check_decision_status() {
  echo ""
  echo "--- CORPUS-09: Decision Status Tracking ---"

  local found=0
  local valid_statuses="Proposed|Accepted|Deprecated|Superseded|Draft|Active"

  shopt -s nullglob
  for f in "$ADR_DIR"/ADR-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE|RULES ]]; then continue; fi

    # Check for Status field
    local status
    status=$(grep -oE "\| *Status *\| *[^|]+" "$f" 2>/dev/null | sed 's/.*| *//' | head -1 || echo "")

    if [[ -n "$status" ]] && ! echo "$status" | grep -qE "$valid_statuses"; then
      echo -e "${YELLOW}CORPUS-W009: $(basename $f) has invalid status: $status${NC}"
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All decision statuses are valid${NC}"
  fi
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

  shopt -s globstar nullglob
  for f in "$ADR_DIR"/**/ADR-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE|RULES ]]; then continue; fi

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
# CORPUS-11: Context-Decision-Consequences Structure
# -----------------------------------------------------------------------------

check_adr_structure() {
  echo ""
  echo "--- CORPUS-11: Context-Decision-Consequences Structure ---"

  local found=0
  shopt -s nullglob
  for f in "$ADR_DIR"/ADR-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE|RULES ]]; then continue; fi
    if is_adr_ref "$(basename $f)"; then continue; fi

    local has_context has_decision has_consequences
    has_context=$(grep -cE "^#+.*Context" "$f" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$has_context" || ! "$has_context" =~ ^[0-9]+$ ]] && has_context=0
    has_decision=$(grep -cE "^#+.*Decision" "$f" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$has_decision" || ! "$has_decision" =~ ^[0-9]+$ ]] && has_decision=0
    has_consequences=$(grep -cE "^#+.*(Consequences|Implications)" "$f" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$has_consequences" || ! "$has_consequences" =~ ^[0-9]+$ ]] && has_consequences=0

    if [[ $has_context -eq 0 ]]; then
      echo -e "${RED}CORPUS-E011: $(basename $f) missing Context section${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
    if [[ $has_decision -eq 0 ]]; then
      echo -e "${RED}CORPUS-E012: $(basename $f) missing Decision section${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
    if [[ $has_consequences -eq 0 ]]; then
      echo -e "${RED}CORPUS-E013: $(basename $f) missing Consequences/Implications section${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All ADRs have Context-Decision-Consequences structure${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-12: Cumulative Traceability (@brd + @prd + @ears + @bdd)
# -----------------------------------------------------------------------------

check_traceability() {
  echo ""
  echo "--- CORPUS-12: Cumulative Traceability (@brd + @prd + @ears + @bdd) ---"

  local found=0
  shopt -s nullglob
  for f in "$ADR_DIR"/ADR-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE|RULES ]]; then continue; fi
    # Skip ADR-REF documents
    if is_adr_ref "$(basename $f)"; then continue; fi

    local has_brd has_prd has_ears has_bdd
    has_brd=$(grep -c "@brd:" "$f" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$has_brd" || ! "$has_brd" =~ ^[0-9]+$ ]] && has_brd=0
    has_prd=$(grep -c "@prd:" "$f" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$has_prd" || ! "$has_prd" =~ ^[0-9]+$ ]] && has_prd=0
    has_ears=$(grep -c "@ears:" "$f" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$has_ears" || ! "$has_ears" =~ ^[0-9]+$ ]] && has_ears=0
    has_bdd=$(grep -c "@bdd:" "$f" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$has_bdd" || ! "$has_bdd" =~ ^[0-9]+$ ]] && has_bdd=0

    if [[ $has_brd -eq 0 ]]; then
      echo -e "${RED}CORPUS-E014: $(basename $f) missing @brd traceability tag${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi

    if [[ $has_prd -eq 0 ]]; then
      echo -e "${RED}CORPUS-E015: $(basename $f) missing @prd traceability tag${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi

    if [[ $has_ears -eq 0 ]]; then
      echo -e "${RED}CORPUS-E016: $(basename $f) missing @ears traceability tag${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi

    if [[ $has_bdd -eq 0 ]]; then
      echo -e "${RED}CORPUS-E017: $(basename $f) missing @bdd traceability tag${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All standard ADRs have cumulative traceability tags${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-13: Decision Conflict Detection
# -----------------------------------------------------------------------------

check_decision_conflicts() {
  echo ""
  echo "--- CORPUS-13: Decision Conflict Detection ---"

  # Extract decision topics and check for potential overlaps
  local decisions
  decisions=$(grep -rhE "^#+.*Decision:" "$ADR_DIR"/ADR-[0-9]*_*.md 2>/dev/null | \
    sed 's/.*Decision:\s*//' | sort | uniq -d || true)

  if [[ -n "$decisions" ]]; then
    echo -e "${YELLOW}CORPUS-W013: Potential decision topic overlaps detected:${NC}"
    echo "$decisions" | while read topic; do
      echo -e "${YELLOW}  → $topic${NC}"
      ((WARNINGS++)) || true
    done
  else
    echo -e "${GREEN}  ✓ No decision conflicts detected${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-14: SYS-Ready Score Threshold
# -----------------------------------------------------------------------------

check_sys_ready() {
  echo ""
  echo "--- CORPUS-14: SYS-Ready Score Threshold ---"

  local found=0
  shopt -s nullglob
  for f in "$ADR_DIR"/ADR-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE|RULES ]]; then continue; fi
    if is_adr_ref "$(basename $f)"; then continue; fi

    local score
    score=$(grep -oE "SYS-Ready Score[^0-9]*[0-9]+" "$f" 2>/dev/null | grep -oE "[0-9]+" | head -1 || echo "")

    if [[ -n "$score" && $score -lt 90 ]]; then
      echo -e "${YELLOW}CORPUS-W014: $(basename $f) has SYS-Ready Score $score% (target: ≥90%)${NC}"
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All ADRs are SYS-ready${NC}"
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
    echo -e "${RED}FAILED: $ERRORS error(s) must be fixed before SYS creation${NC}"
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
  if [[ ! -d "$ADR_DIR" ]]; then
    echo -e "${RED}ERROR: Directory not found: $ADR_DIR${NC}"
    exit 3
  fi

  print_header

  local file_count
  file_count=$(count_files)
  echo "Found $file_count ADR documents"
  echo ""

  if [[ $file_count -eq 0 ]]; then
    echo -e "${YELLOW}No ADR documents found to validate${NC}"
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
  check_decision_status
  check_file_size
  check_adr_structure
  check_traceability
  check_decision_conflicts
  check_sys_ready

  print_summary
}

main "$@"
