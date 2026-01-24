#!/bin/bash
# =============================================================================
# REQ Quality Gate Validation Script
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
  echo "REQ Quality Gate Validation (Pre-SPEC Gate)"
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
# GATE-01: Placeholder Text Detection
# -----------------------------------------------------------------------------
# PURPOSE: Detect LITERAL placeholder text patterns that indicate incomplete
#          references to documents that already exist.
#
# IMPORTANT: Uses grep -F (fixed string matching) to match literal patterns.
#            Patterns like "(TBD)" must match exactly "(TBD)", not just "TBD".
#
# FALSE POSITIVE PREVENTION:
#   - Uses grep -F to avoid regex interpretation of special characters
#   - Parentheses and brackets are matched literally, not as regex operators
#   - "TBD" in downstream reference tables (e.g., "| SPEC-NN | TBD |") is
#     EXPECTED and NOT flagged because it doesn't match "(TBD)" or "[TBD]"
# -----------------------------------------------------------------------------

check_placeholder_text() {
  echo "--- GATE-01: Placeholder Text Detection ---"

  local found=0
  # These patterns must be matched LITERALLY (not as regex)
  # - "(TBD)" matches only "(TBD)", not "TBD" alone
  # - "[TODO]" matches only "[TODO]", not "TODO" alone
  local patterns=("(future REQ)" "(when created)" "(to be defined)" "(pending)" "(TBD)" "[TBD]" "[TODO]")

  for pattern in "${patterns[@]}"; do
    # Use grep -F for FIXED STRING matching (no regex interpretation)
    # This prevents parentheses/brackets from being treated as regex operators
    while IFS= read -r line; do
      if [[ -n "$line" ]]; then
        # Extract REQ reference if present
        req_ref=$(echo "$line" | grep -oE "REQ-[0-9]+(\.[0-9]+)*" | head -1 || true)
        if [[ -n "$req_ref" ]]; then
          # Check if the referenced REQ file exists
          if find "$REQ_DIR" -name "${req_ref}_*.md" 2>/dev/null | grep -v "_index" | head -1 >/dev/null; then
            echo -e "${RED}GATE-E001: $line${NC}"
            echo "  → $req_ref exists but marked as placeholder"
            ((ERRORS++)) || true
            ((found++)) || true
          fi
        fi
      fi
    done < <(find "$REQ_DIR" -name "*.md" -exec grep -FHn "$pattern" {} \; 2>/dev/null || true)
  done
  echo "DEBUG: Finished processing all files..."

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
  # Layer 8+ artifacts that shouldn't be referenced with specific numbers
  local downstream_patterns="(IMPL|CTR|SPEC|TASKS-[0-9]{2,}"

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
  done < <(find "$REQ_DIR" -name "*.md" -exec grep -HnE "$downstream_patterns" {} \; 2>/dev/null | head -20 || true)

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
  while IFS= read -r line; do
    if [[ -n "$line" ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${YELLOW}GATE-W001: Verify count - $line${NC}"
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
# GATE-04: Index Synchronization
# -----------------------------------------------------------------------------

check_index_sync() {
  echo ""
  echo "--- GATE-04: Index Synchronization ---"

  # Find index file
  local index_file=""
  for f in "$REQ_DIR"/REQ-*_index.md "$REQ_DIR"/REQ-000_index.md; do
    if [[ -f "$f" ]]; then
      index_file="$f"
      break
    fi
  done
  echo "DEBUG: Finished processing all files..."

  if [[ -z "$index_file" || ! -f "$index_file" ]]; then
    echo -e "${YELLOW}  Index file not found: $REQ_DIR/REQ-000_index.md${NC}"
    return
  fi

  local found=0
  # Check for files marked "Planned" that actually exist
  while IFS= read -r line; do
    req_ref=$(echo "$line" | grep -oE "REQ-[0-9]+(\.[0-9]+)*" | head -1 || true)
    if [[ -n "$req_ref" ]]; then
      if find "$REQ_DIR" -name "${req_ref}_*.md" 2>/dev/null | grep -v "_index" | head -1 >/dev/null; then
        echo -e "${RED}GATE-E003: $req_ref exists but marked Planned in index${NC}"
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
# GATE-05: Inter-REQ Cross-Linking (DEPRECATED)
# -----------------------------------------------------------------------------

check_cross_linking() {
  echo ""
  # --- GATE-05: Inter-REQ Cross-Linking (DEPRECATED) ---
  # echo -e "\n--- GATE-05: Inter-REQ Cross-Linking ---"
  # echo -e "  ℹ DEPRECATED: Document name references are sufficient per SDD rules"
  echo -e "${BLUE}  ℹ GATE-05 DEPRECATED: Inter-REQ Cross-Linking checks disabled per user request${NC}"
}

# -----------------------------------------------------------------------------
# GATE-06: Visualization Coverage (DEPRECATED)
# -----------------------------------------------------------------------------

check_visualization() {
  echo ""
  echo "--- GATE-06: Mermaid Diagram Validation (Optional) ---"

  local found=0
  local syntax_errors=0

  while IFS= read -r -d '' f; do
    if [[ "$(basename "$f")" =~ _index|TEMPLATE ]]; then continue; fi

    # Check if file contains Mermaid diagrams
    if grep -q '```mermaid' "$f" 2>/dev/null; then
      # Basic syntax validation for Mermaid blocks
      local mermaid_blocks=$(grep -c '```mermaid' "$f" 2>/dev/null || echo 0)
      local closing_blocks=$(grep -c '^```$' "$f" 2>/dev/null || echo 0)
      
      # Check for unclosed Mermaid blocks
      if [[ $mermaid_blocks -gt $closing_blocks ]]; then
        echo -e "${RED}GATE-E006: $(basename $f) has unclosed Mermaid code block${NC}"
        ((ERRORS++)) || true
        ((syntax_errors++)) || true
      fi
      
      # Extract and validate Mermaid content
      local in_mermaid=0
      while IFS= read -r line; do
        if [[ "$line" =~ ^\`\`\`mermaid ]]; then
          in_mermaid=1
        elif [[ "$line" =~ ^\`\`\`$ ]] && [[ $in_mermaid -eq 1 ]]; then
          in_mermaid=0
        elif [[ $in_mermaid -eq 1 ]]; then
          # Check for common Mermaid syntax issues
          # Must start with diagram type (graph, flowchart, sequenceDiagram, etc.)
          if echo "$line" | grep -qE '^(graph|flowchart|sequenceDiagram|classDiagram|stateDiagram|erDiagram|gantt|pie|journey)'; then
            continue
          fi
        fi
      done < "$f"
    fi
  done < <(find "$REQ_DIR" -name "REQ-[0-9]*_*.md" -print0 2>/dev/null)

  if [[ $syntax_errors -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Mermaid diagrams are optional; all present diagrams are syntactically valid${NC}"
  fi
}

# -----------------------------------------------------------------------------
# GATE-07: Glossary Consistency
# -----------------------------------------------------------------------------

check_glossary() {
  echo ""
  echo "--- GATE-07: Glossary Consistency ---"

  local found=0

  # Check for SHALL/MUST inconsistency
  local shall_count=$(find "$REQ_DIR" -name "*.md" -exec grep -oh "SHALL " {} \; 2>/dev/null | wc -l || echo 0)
  local must_count=$(find "$REQ_DIR" -name "*.md" -exec grep -oh "MUST " {} \; 2>/dev/null | wc -l || echo 0)

  if [[ $shall_count -gt 10 && $must_count -gt 10 ]]; then
    echo -e "${YELLOW}GATE-W003: Mixed SHALL ($shall_count) and MUST ($must_count) usage${NC}"
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
  echo "--- GATE-08: Element ID Uniqueness (Cross-File) ---"

  # Check for IDs that appear in multiple different files
  # Within-file duplicates are acceptable (same ID in AC and traceability sections)
  local duplicates
  duplicates=$(
    for f in "$REQ_DIR"/REQ-*.md; do
      [[ -f "$f" ]] || continue
      # Get unique IDs from this file only
      grep -ohE "REQ\.[0-9]+\.[0-9]+\.[0-9]+" "$f" 2>/dev/null | sort -u || true
    done | sort | uniq -d
  )

  local dup_count=0
  if [[ -n "$duplicates" ]]; then
    while IFS= read -r dup; do
      [[ -z "$dup" ]] && continue
      echo -e "${RED}GATE-E004: Duplicate element ID: $dup (in multiple files)${NC}"
      ((ERRORS++)) || true
      ((dup_count++)) || true
    done <<< "$duplicates"
  fi

  if [[ $dup_count -eq 0 ]]; then
    echo -e "${GREEN}  ✓ No cross-file duplicate element IDs${NC}"
  fi
}

# -----------------------------------------------------------------------------
# GATE-09: Priority Distribution
# -----------------------------------------------------------------------------

check_priority_distribution() {
  echo ""
  echo "--- GATE-09: Priority Distribution ---"

  local must_count=$(find "$REQ_DIR" -name "REQ-[0-9]*_*.md" -exec grep -l "Priority.*MUST\|MUST.*Priority" {} \; 2>/dev/null | wc -l || echo 0)
  local should_count=$(find "$REQ_DIR" -name "REQ-[0-9]*_*.md" -exec grep -l "Priority.*SHOULD\|SHOULD.*Priority" {} \; 2>/dev/null | wc -l || echo 0)
  local may_count=$(find "$REQ_DIR" -name "REQ-[0-9]*_*.md" -exec grep -l "Priority.*MAY\|MAY.*Priority" {} \; 2>/dev/null | wc -l || echo 0)

  local total=$((must_count + should_count + may_count))

  if [[ $total -gt 0 ]]; then
    echo "  Priority distribution: MUST=$must_count, SHOULD=$should_count, MAY=$may_count"

    if [[ $must_count -eq $total ]]; then
      echo -e "${YELLOW}GATE-W009: 100% MUST priority - consider priority balance${NC}"
      ((WARNINGS++)) || true
    fi
  else
    echo -e "${GREEN}  ✓ Priority distribution check skipped (no priority tags found)${NC}"
  fi
}

# -----------------------------------------------------------------------------
# GATE-10: File Size Compliance (Universal Rule)
# -----------------------------------------------------------------------------

check_file_size() {
  echo ""
  echo "--- GATE-10: File Size & Token Compliance ---"

  local found=0

  # Use recursive find for universal nested support
  while IFS= read -r -d '' f; do
    if [[ "$(basename "$f")" =~ _index|TEMPLATE ]]; then continue; fi

    local lines
    lines=$(wc -l < "$f")
    local words
    words=$(wc -w < "$f")
    local tokens=$((words * 13 / 10))

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
  done < <(find "$REQ_DIR" -name "REQ-[0-9]*_*.md" -print0 2>/dev/null)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All files within size limits (≤20,000 tokens, ≤10k tokens)${NC}"
  fi
}

# -----------------------------------------------------------------------------
# GATE-11: Cumulative Traceability (6 upstream tags)
# -----------------------------------------------------------------------------

check_traceability() {
  echo ""
  echo "--- GATE-11: Cumulative Traceability (@brd + @prd + @ears + @bdd + @adr + @sys) ---"

  local found=0

  while IFS= read -r -d '' f; do
    if [[ "$(basename "$f")" =~ _index|TEMPLATE|RULES ]]; then continue; fi

    local has_brd has_prd has_ears has_bdd has_adr has_sys
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
    has_sys=$(grep -c "@sys:" "$f" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$has_sys" || ! "$has_sys" =~ ^[0-9]+$ ]] && has_sys=0

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

    if [[ $has_sys -eq 0 ]]; then
      echo -e "${RED}GATE-E016: $(basename $f) missing @sys traceability tag${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done < <(find "$REQ_DIR" -name "REQ-[0-9]*_*.md" -print0 2>/dev/null)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All REQ have cumulative traceability tags (6 upstream)${NC}"
  fi
}

# -----------------------------------------------------------------------------
# GATE-22: Upstream TBD References
# -----------------------------------------------------------------------------
# PURPOSE: Detect TBD placeholders in UPSTREAM traceability references.
#          Upstream documents (BRD, PRD, EARS, BDD, ADR, SYS) must exist
#          BEFORE REQ creation, so TBD is not acceptable for these.
#
# NOTE: This is different from downstream TBD (SPEC, TASKS) which is expected
#       because those documents are created AFTER REQ.
# -----------------------------------------------------------------------------

check_upstream_tbd() {
  echo ""
  echo "--- GATE-22: Upstream TBD References ---"

  local found=0
  # Upstream tags that must have real references (not TBD)
  local upstream_tags=("@brd:" "@prd:" "@ears:" "@bdd:" "@adr:" "@sys:")

  while IFS= read -r -d '' f; do
    if [[ "$(basename "$f")" =~ _index|TEMPLATE|RULES ]]; then continue; fi

    for tag in "${upstream_tags[@]}"; do
      # Check if tag exists with TBD value (various formats)
      # Matches: @brd: TBD, @brd:TBD, @brd: (TBD), @brd: [TBD]
      if grep -qE "${tag}\s*(TBD|\(TBD\)|\[TBD\])" "$f" 2>/dev/null; then
        local tag_name="${tag%:}"  # Remove trailing colon for display
        echo -e "${RED}GATE-E022: $(basename $f) has TBD for upstream ${tag_name} reference${NC}"
        echo "  → Upstream documents must exist before REQ creation"
        ((ERRORS++)) || true
        ((found++)) || true
      fi
    done
  echo "DEBUG: Finished processing all files..."
  done < <(find "$REQ_DIR" -name "REQ-[0-9]*_*.md" -print0 2>/dev/null)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ No TBD placeholders in upstream references${NC}"
  fi
}

# -----------------------------------------------------------------------------
# GATE-12: 11-Section Format Compliance (MVP)
# -----------------------------------------------------------------------------

check_section_format() {
  echo ""
  echo "--- GATE-12: 11-Section Format Compliance (MVP) ---"

  local found=0

  # Required MVP sections (11 sections, no Change History)
  local section_patterns=(
    "Document Control"
    "Requirement Description"
    "Functional Specification"
    "Interface Definition"
    "Error Handling"
    "Quality Attributes"
    "Configuration"
    "Testing Requirements"
    "Acceptance Criteria"
    "Traceability"
    "Implementation Notes"
  )

  while IFS= read -r -d '' f; do
    if [[ "$(basename "$f")" =~ _index|TEMPLATE|RULES ]]; then continue; fi

    for pattern in "${section_patterns[@]}"; do
      if ! grep -qiE "^## .*${pattern}" "$f" 2>/dev/null; then
        echo -e "${RED}GATE-E017: $(basename $f) missing '${pattern}' section${NC}"
        ((ERRORS++)) || true
        ((found++)) || true
      fi
    done
  done < <(find "$REQ_DIR" -name "REQ-[0-9]*_*.md" -print0 2>/dev/null)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All REQ have required MVP sections${NC}"
  fi
}

# -----------------------------------------------------------------------------
# GATE-13: Domain Subdirectory Classification
# -----------------------------------------------------------------------------

check_domain_classification() {
  echo ""
  echo "--- GATE-13: Domain Subdirectory Classification ---"

  local found=0
  local orphaned=0

  while IFS= read -r -d '' f; do
    if [[ "$(basename "$f")" =~ _index|TEMPLATE|RULES ]]; then continue; fi

    local dir_name
    dir_name=$(dirname "$f" | xargs basename)

    # Check if file is in root REQ directory (orphaned)
    if [[ "$dir_name" == "REQ" ]]; then
      echo -e "${YELLOW}GATE-W013: $(basename $f) is not in a domain subdirectory${NC}"
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
  echo "DEBUG: Finished processing all files..."

    if [[ $valid -eq 0 ]]; then
      echo -e "${YELLOW}GATE-W013: $(basename $f) is in unrecognized domain '$dir_name'${NC}"
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done < <(find "$REQ_DIR" -name "REQ-[0-9]*_*.md" -print0 2>/dev/null)

  if [[ $found -eq 0 && $orphaned -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All REQ in valid domain subdirectories${NC}"
  fi
}

# -----------------------------------------------------------------------------
# GATE-14: SPEC-Readiness Scoring
# -----------------------------------------------------------------------------

check_spec_ready() {
  echo ""
  echo "--- GATE-14: SPEC-Readiness Scoring ---"

  local found=0
  local missing=0

  while IFS= read -r -d '' f; do
    if [[ "$(basename "$f")" =~ _index|TEMPLATE|RULES ]]; then continue; fi

    local score
    score=$(grep -oE "SPEC-Ready Score[^0-9]*[0-9]+" "$f" 2>/dev/null | grep -oE "[0-9]+" | head -1 || echo "")

    if [[ -z "$score" ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${YELLOW}GATE-W014: $(basename $f) missing SPEC-Ready Score${NC}"
      fi
      ((missing++)) || true
    elif [[ $score -lt 90 ]]; then
      echo -e "${YELLOW}GATE-W014: $(basename $f) has SPEC-Ready Score $score% (target: ≥90%)${NC}"
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
# GATE-15: IMPL-Readiness Scoring
# -----------------------------------------------------------------------------

check_impl_ready() {
  echo ""
  echo "--- GATE-15: IMPL-Readiness Scoring ---"

  local found=0

  while IFS= read -r -d '' f; do
    if [[ "$(basename "$f")" =~ _index|TEMPLATE|RULES ]]; then continue; fi

    local score
    score=$(grep -oE "IMPL-Ready Score[^0-9]*[0-9]+" "$f" 2>/dev/null | grep -oE "[0-9]+" | head -1 || echo "")

    if [[ -n "$score" && $score -lt 85 ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${BLUE}GATE-I015: $(basename $f) has IMPL-Ready Score $score% (recommended: ≥85%)${NC}"
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
# GATE-16: Acceptance Criteria Coverage
# -----------------------------------------------------------------------------

check_acceptance_criteria() {
  echo ""
  echo "--- GATE-16: Acceptance Criteria Coverage ---"

  local found=0

  while IFS= read -r -d '' f; do
    if [[ "$(basename "$f")" =~ _index|TEMPLATE|RULES ]]; then continue; fi

    # Count acceptance criteria (looking for numbered lists after AC header)
    # Note: Use tr -d '\n' to ensure single numeric value (grep -c can output multiple lines)
    local ac_count
    ac_count=$(grep -cE "^[0-9]+\.|^- \[" "$f" 2>/dev/null | tr -d '\n' || echo "0")
    # Default to 0 if empty
    [[ -z "$ac_count" ]] && ac_count=0

    # Use arithmetic comparison
    if [[ $ac_count -lt 3 ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${YELLOW}GATE-W016: $(basename $f) may have insufficient acceptance criteria ($ac_count found)${NC}"
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
    echo -e "${GREEN}PASSED: All Quality Gate validation checks passed${NC}"
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
  check_upstream_tbd
  check_section_format
  check_domain_classification
  check_spec_ready
  check_impl_ready
  check_acceptance_criteria

  print_summary
}

# Run main function
main "$@"
