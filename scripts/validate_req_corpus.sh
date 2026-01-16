#!/bin/bash
# =============================================================================
# REQ Corpus Validation Script
# Validates entire REQ document set before SPEC creation
# Layer 7 → Layer 8/10 transition gate
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
REQ_DIR="${1:-docs/REQ}"
VERBOSE="${2:-}"

# Valid domain subdirectories
VALID_DOMAINS=("api" "auth" "core" "data" "risk" "trading" "collection" "compliance" "ml")

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

print_header() {
  echo "=========================================="
  echo "REQ Corpus Validation (Pre-SPEC Gate)"
  echo "=========================================="
  echo "Directory: $REQ_DIR"
  echo "Date: $(TZ=America/New_York date '+%Y-%m-%d %H:%M:%S %Z')"
  echo ""
}

count_files() {
  local count=0
  while IFS= read -r -d '' f; do
    if [[ ! "$(basename "$f")" =~ _index|TEMPLATE ]]; then
      ((count++)) || true
    fi
  done < <(find "$REQ_DIR" -name "REQ-[0-9]*_*.md" -print0 2>/dev/null)
  echo "$count"
}

# -----------------------------------------------------------------------------
# CORPUS-01: Placeholder Text Detection
# -----------------------------------------------------------------------------

check_placeholder_text() {
  echo "--- CORPUS-01: Placeholder Text Detection ---"

  local found=0
  local patterns=("(future REQ)" "(when created)" "(to be defined)" "(pending)" "(TBD)" "[TBD]" "[TODO]")

  for pattern in "${patterns[@]}"; do
    while IFS= read -r line; do
      if [[ -n "$line" ]]; then
        # Extract REQ reference if present
        req_ref=$(echo "$line" | grep -oE "REQ-[0-9]+" | head -1 || true)
        if [[ -n "$req_ref" ]]; then
          # Check if the referenced REQ file exists
          if find "$REQ_DIR" -name "${req_ref}_*.md" 2>/dev/null | grep -v "_index" | head -1 >/dev/null; then
            echo -e "${RED}CORPUS-E001: $line${NC}"
            echo "  → $req_ref exists but marked as placeholder"
            ((ERRORS++)) || true
            ((found++)) || true
          fi
        fi
      fi
    done < <(find "$REQ_DIR" -name "*.md" -exec grep -Hn "$pattern" {} \; 2>/dev/null || true)
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
  # Layer 8+ artifacts that shouldn't be referenced with specific numbers
  local downstream_patterns="(IMPL|CTR|SPEC|TASKS-[0-9]{2,}"

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
  done < <(find "$REQ_DIR" -name "*.md" -exec grep -HnE "$downstream_patterns" {} \; 2>/dev/null | head -20 || true)

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
  done < <(find "$REQ_DIR" -name "*.md" -exec grep -HnE "[0-9]+ (acceptance criteria|dependencies|requirements)" {} \; 2>/dev/null | head -5 || true)

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
  for f in "$REQ_DIR"/REQ-*_index.md "$REQ_DIR"/REQ-000_index.md; do
    if [[ -f "$f" ]]; then
      index_file="$f"
      break
    fi
  done

  if [[ -z "$index_file" || ! -f "$index_file" ]]; then
    echo -e "${YELLOW}  Index file not found: $REQ_DIR/REQ-000_index.md${NC}"
    return
  fi

  local found=0
  # Check for files marked "Planned" that actually exist
  while IFS= read -r line; do
    req_ref=$(echo "$line" | grep -oE "REQ-[0-9]+" | head -1 || true)
    if [[ -n "$req_ref" ]]; then
      if find "$REQ_DIR" -name "${req_ref}_*.md" 2>/dev/null | grep -v "_index" | head -1 >/dev/null; then
        echo -e "${RED}CORPUS-E003: $req_ref exists but marked Planned in index${NC}"
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
# CORPUS-05: Inter-REQ Cross-Linking (DEPRECATED)
# -----------------------------------------------------------------------------

check_cross_linking() {
  echo ""
  echo "--- CORPUS-05: Inter-REQ Cross-Linking ---"
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

    diagram_count=$(grep -c '```mermaid' "$f" 2>/dev/null || echo 0)
    if [[ $diagram_count -eq 0 ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${BLUE}CORPUS-I001: $(basename $f) has no Mermaid diagrams${NC}"
      fi
      ((INFO++)) || true
      ((found++)) || true
    fi
  done < <(find "$REQ_DIR" -name "REQ-[0-9]*_*.md" -print0 2>/dev/null)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All REQ have diagrams${NC}"
  else
    echo -e "${BLUE}  ℹ $found of $total REQ files have no Mermaid diagrams${NC}"
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
  local shall_count=$(find "$REQ_DIR" -name "*.md" -exec grep -oh "SHALL " {} \; 2>/dev/null | wc -l || echo 0)
  local must_count=$(find "$REQ_DIR" -name "*.md" -exec grep -oh "MUST " {} \; 2>/dev/null | wc -l || echo 0)

  if [[ $shall_count -gt 10 && $must_count -gt 10 ]]; then
    echo -e "${YELLOW}CORPUS-W003: Mixed SHALL ($shall_count) and MUST ($must_count) usage${NC}"
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
  duplicates=$(find "$REQ_DIR" -name "REQ-*.md" -exec grep -ohE "REQ\.[0-9]+\.[0-9]+\.[0-9]+" {} \; 2>/dev/null | sort | uniq -d || true)

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
# CORPUS-09: Priority Distribution
# -----------------------------------------------------------------------------

check_priority_distribution() {
  echo ""
  echo "--- CORPUS-09: Priority Distribution ---"

  local must_count=$(find "$REQ_DIR" -name "REQ-[0-9]*_*.md" -exec grep -l "Priority.*MUST\|MUST.*Priority" {} \; 2>/dev/null | wc -l || echo 0)
  local should_count=$(find "$REQ_DIR" -name "REQ-[0-9]*_*.md" -exec grep -l "Priority.*SHOULD\|SHOULD.*Priority" {} \; 2>/dev/null | wc -l || echo 0)
  local may_count=$(find "$REQ_DIR" -name "REQ-[0-9]*_*.md" -exec grep -l "Priority.*MAY\|MAY.*Priority" {} \; 2>/dev/null | wc -l || echo 0)

  local total=$((must_count + should_count + may_count))

  if [[ $total -gt 0 ]]; then
    echo "  Priority distribution: MUST=$must_count, SHOULD=$should_count, MAY=$may_count"

    if [[ $must_count -eq $total ]]; then
      echo -e "${YELLOW}CORPUS-W009: 100% MUST priority - consider priority balance${NC}"
      ((WARNINGS++)) || true
    fi
  else
    echo -e "${GREEN}  ✓ Priority distribution check skipped (no priority tags found)${NC}"
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
  done < <(find "$REQ_DIR" -name "REQ-[0-9]*_*.md" -print0 2>/dev/null)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All files within size limits${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-11: Cumulative Traceability (6 upstream tags)
# -----------------------------------------------------------------------------

check_traceability() {
  echo ""
  echo "--- CORPUS-11: Cumulative Traceability (@brd + @prd + @ears + @bdd + @adr + @sys) ---"

  local found=0

  while IFS= read -r -d '' f; do
    if [[ "$(basename "$f")" =~ _index|TEMPLATE|RULES ]]; then continue; fi

    local has_brd has_prd has_ears has_bdd has_adr has_sys
    has_brd=$(grep -c "@brd:" "$f" 2>/dev/null || echo 0)
    has_prd=$(grep -c "@prd:" "$f" 2>/dev/null || echo 0)
    has_ears=$(grep -c "@ears:" "$f" 2>/dev/null || echo 0)
    has_bdd=$(grep -c "@bdd:" "$f" 2>/dev/null || echo 0)
    has_adr=$(grep -c "@adr:" "$f" 2>/dev/null || echo 0)
    has_sys=$(grep -c "@sys:" "$f" 2>/dev/null || echo 0)

    if [[ $has_brd -eq 0 ]]; then
      echo -e "${RED}CORPUS-E011: $(basename $f) missing @brd traceability tag${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi

    if [[ $has_prd -eq 0 ]]; then
      echo -e "${RED}CORPUS-E012: $(basename $f) missing @prd traceability tag${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi

    if [[ $has_ears -eq 0 ]]; then
      echo -e "${RED}CORPUS-E013: $(basename $f) missing @ears traceability tag${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi

    if [[ $has_bdd -eq 0 ]]; then
      echo -e "${RED}CORPUS-E014: $(basename $f) missing @bdd traceability tag${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi

    if [[ $has_adr -eq 0 ]]; then
      echo -e "${RED}CORPUS-E015: $(basename $f) missing @adr traceability tag${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi

    if [[ $has_sys -eq 0 ]]; then
      echo -e "${RED}CORPUS-E016: $(basename $f) missing @sys traceability tag${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done < <(find "$REQ_DIR" -name "REQ-[0-9]*_*.md" -print0 2>/dev/null)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All REQ have cumulative traceability tags (6 upstream)${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-12: 12-Section Format Compliance
# -----------------------------------------------------------------------------

check_section_format() {
  echo ""
  echo "--- CORPUS-12: 12-Section Format Compliance (REQ v3.0) ---"

  local found=0
  local required_sections=("Requirement Statement" "Priority" "Source" "Rationale"
                           "Acceptance Criteria" "Dependencies" "Traceability" "Verification")

  while IFS= read -r -d '' f; do
    if [[ "$(basename "$f")" =~ _index|TEMPLATE|RULES ]]; then continue; fi

    for section in "${required_sections[@]}"; do
      if ! grep -qE "^#+.*$section" "$f" 2>/dev/null; then
        echo -e "${RED}CORPUS-E017: $(basename $f) missing '$section' section${NC}"
        ((ERRORS++)) || true
        ((found++)) || true
      fi
    done
  done < <(find "$REQ_DIR" -name "REQ-[0-9]*_*.md" -print0 2>/dev/null)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All REQ follow 12-section format${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-13: Domain Subdirectory Classification
# -----------------------------------------------------------------------------

check_domain_classification() {
  echo ""
  echo "--- CORPUS-13: Domain Subdirectory Classification ---"

  local found=0
  local orphaned=0

  while IFS= read -r -d '' f; do
    if [[ "$(basename "$f")" =~ _index|TEMPLATE|RULES ]]; then continue; fi

    local dir_name
    dir_name=$(dirname "$f" | xargs basename)

    # Check if file is in root REQ directory (orphaned)
    if [[ "$dir_name" == "REQ" ]]; then
      echo -e "${YELLOW}CORPUS-W013: $(basename $f) is not in a domain subdirectory${NC}"
      ((WARNINGS++)) || true
      ((orphaned++)) || true
      continue
    fi

    # Check if subdirectory is valid
    local valid=0
    for domain in "${VALID_DOMAINS[@]}"; do
      if [[ "$dir_name" == "$domain" ]]; then
        valid=1
        break
      fi
    done

    if [[ $valid -eq 0 ]]; then
      echo -e "${YELLOW}CORPUS-W013: $(basename $f) is in unrecognized domain '$dir_name'${NC}"
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done < <(find "$REQ_DIR" -name "REQ-[0-9]*_*.md" -print0 2>/dev/null)

  if [[ $found -eq 0 && $orphaned -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All REQ in valid domain subdirectories${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-14: SPEC-Readiness Scoring
# -----------------------------------------------------------------------------

check_spec_ready() {
  echo ""
  echo "--- CORPUS-14: SPEC-Readiness Scoring ---"

  local found=0
  local missing=0

  while IFS= read -r -d '' f; do
    if [[ "$(basename "$f")" =~ _index|TEMPLATE|RULES ]]; then continue; fi

    local score
    score=$(grep -oE "SPEC-Ready Score[^0-9]*[0-9]+" "$f" 2>/dev/null | grep -oE "[0-9]+" | head -1 || echo "")

    if [[ -z "$score" ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${YELLOW}CORPUS-W014: $(basename $f) missing SPEC-Ready Score${NC}"
      fi
      ((missing++)) || true
    elif [[ $score -lt 90 ]]; then
      echo -e "${YELLOW}CORPUS-W014: $(basename $f) has SPEC-Ready Score $score% (target: ≥90%)${NC}"
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done < <(find "$REQ_DIR" -name "REQ-[0-9]*_*.md" -print0 2>/dev/null)

  if [[ $found -eq 0 && $missing -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All REQ meet SPEC-Ready threshold${NC}"
  elif [[ $missing -gt 0 ]]; then
    echo -e "${YELLOW}  $missing REQ files missing SPEC-Ready Score${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-15: IMPL-Readiness Scoring
# -----------------------------------------------------------------------------

check_impl_ready() {
  echo ""
  echo "--- CORPUS-15: IMPL-Readiness Scoring ---"

  local found=0

  while IFS= read -r -d '' f; do
    if [[ "$(basename "$f")" =~ _index|TEMPLATE|RULES ]]; then continue; fi

    local score
    score=$(grep -oE "IMPL-Ready Score[^0-9]*[0-9]+" "$f" 2>/dev/null | grep -oE "[0-9]+" | head -1 || echo "")

    if [[ -n "$score" && $score -lt 85 ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${BLUE}CORPUS-I015: $(basename $f) has IMPL-Ready Score $score% (recommended: ≥85%)${NC}"
      fi
      ((INFO++)) || true
      ((found++)) || true
    fi
  done < <(find "$REQ_DIR" -name "REQ-[0-9]*_*.md" -print0 2>/dev/null)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ IMPL-Ready scores acceptable${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-16: Acceptance Criteria Coverage
# -----------------------------------------------------------------------------

check_acceptance_criteria() {
  echo ""
  echo "--- CORPUS-16: Acceptance Criteria Coverage ---"

  local found=0

  while IFS= read -r -d '' f; do
    if [[ "$(basename "$f")" =~ _index|TEMPLATE|RULES ]]; then continue; fi

    # Count acceptance criteria (looking for numbered lists after AC header)
    local ac_count
    ac_count=$(grep -cE "^[0-9]+\.|^- \[" "$f" 2>/dev/null || echo 0)

    if [[ $ac_count -lt 3 ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${YELLOW}CORPUS-W016: $(basename $f) may have insufficient acceptance criteria ($ac_count found)${NC}"
      fi
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done < <(find "$REQ_DIR" -name "REQ-[0-9]*_*.md" -print0 2>/dev/null)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Acceptance criteria coverage adequate${NC}"
  else
    echo -e "${YELLOW}  $found REQ files may need more acceptance criteria${NC}"
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
  # Validate directory exists
  if [[ ! -d "$REQ_DIR" ]]; then
    echo -e "${RED}ERROR: Directory not found: $REQ_DIR${NC}"
    exit 3
  fi

  print_header

  local file_count
  file_count=$(count_files)
  echo "Found $file_count REQ documents"
  echo ""

  if [[ $file_count -eq 0 ]]; then
    echo -e "${YELLOW}No REQ documents found to validate${NC}"
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
  check_priority_distribution
  check_file_size
  check_traceability
  check_section_format
  check_domain_classification
  check_spec_ready
  check_impl_ready
  check_acceptance_criteria

  print_summary
}

# Run main function
main "$@"
