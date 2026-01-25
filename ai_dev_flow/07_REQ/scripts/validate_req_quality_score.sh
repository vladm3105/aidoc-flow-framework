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

# Valid domain labels (from custom_fields.domain in REQ files)
VALID_DOMAINS=(
  "auth"
  "session"
  "observability"
  "security"
  "selfops"
  "infrastructure"
  "config"
  "connectivity"
  "UX"
)

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

  # Find index file (check in REQ root first, then in passed directory)
  # Index file format: *-00_index.md (e.g., REQ-00_index.md)
  local index_file=""
  local req_root="$(dirname "$REQ_DIR")"
  
  # If passed dir is a subdirectory (e.g., REQ-01_f1_iam), check parent for index
  if [[ -d "$req_root" ]] && [[ "$(basename "$req_root")" == "07_REQ" ]]; then
    for f in "$req_root"/*-00_index.md; do
      if [[ -f "$f" ]]; then
        index_file="$f"
        break
      fi
    done
  fi
  
  # Also check passed directory itself
  if [[ -z "$index_file" ]]; then
    for f in "$REQ_DIR"/*-00_index.md; do
      if [[ -f "$f" ]]; then
        index_file="$f"
        break
      fi
    done
  fi
  
  echo "DEBUG: Finished processing all files..."

  if [[ -z "$index_file" || ! -f "$index_file" ]]; then
    echo -e "${YELLOW}  Index file not found: $(dirname "$REQ_DIR")/*-00_index.md or $REQ_DIR/*-00_index.md${NC}"
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

# -----------------------------------------------
# GATE-05: Inter-REQ Cross-Linking (Optional, Informational)
# -----------------------------------------------
# PURPOSE: Map cross-references between related REQ files
#          Helps detect orphaned/isolated requirements
#          Non-blocking, informational only
# -----------------------------------------------

check_cross_linking() {
  echo ""
  echo "--- GATE-05: Inter-REQ Cross-Linking (Informational; Error if All Isolated) ---"

  local found=0
  local isolated=0
  local total_files=0

  # Patterns that indicate cross-references to other REQ files
  local xref_patterns=("See also REQ-" "Related to REQ-" "@depends:" "@discoverability:" "cross-reference:" "implements REQ-")

  while IFS= read -r -d '' f; do
    if [[ "$(basename "$f")" =~ _index|TEMPLATE|RULES ]]; then continue; fi

    ((total_files++)) || true
    local filename
    filename=$(basename "$f")
    local has_xref=0

    # Check for any cross-reference patterns
    for pattern in "${xref_patterns[@]}"; do
      if grep -qi "$pattern" "$f" 2>/dev/null; then
        has_xref=1
        break
      fi
    done

    # Check for references to OTHER REQ files (simpler approach)
    local req_refs=0
    local self_ref
    self_ref=$(echo "$filename" | grep -oE "REQ-[0-9]+\.[0-9]+" | head -1)
    
    if [[ -n "$self_ref" ]]; then
      # Count REQ references that are NOT self-references
      while read -r ref; do
        if [[ "$ref" != "$self_ref" ]]; then
          ((req_refs++)) || true
        fi
      done < <(grep -oE "REQ-[0-9]+\.[0-9]+" "$f" 2>/dev/null || true)
    else
      # Count ALL REQ references in file
      while read -r ref; do
        if [[ -n "$ref" ]]; then
          ((req_refs++)) || true
        fi
      done < <(grep -oE "REQ-[0-9]+\.[0-9]+" "$f" 2>/dev/null || true)
    fi

    # Additionally, detect references by REQ title phrases (natural language cross-links)
    # This helps when authors mention other requirements by name rather than code
    local title_refs=0
    while IFS= read -r -d '' other; do
      [[ "$other" == "$f" ]] && continue
      # Extract other code
      local other_code
      local other_code_raw
      other_code_raw=$(basename "$other" | grep -oE "REQ-[0-9]+\.[0-9]+" | head -1 || true)
      other_code="$other_code_raw"
      [[ -n "$self_ref" && "$other_code" == "$self_ref" ]] && continue

      # Try YAML title first
      local other_title
      local raw_title
      raw_title=$(grep -m1 '^title:' "$other" 2>/dev/null || true)
      other_title=$(echo "$raw_title" | sed -E 's/^title:\s*"?([^"\n]+)"?.*/\1/' | tr -d '\r')
      # If title includes code, strip leading code and colon
      if [[ -n "$other_title" ]]; then
        other_title=$(echo "$other_title" | sed -E 's/^REQ-[0-9]+\.[0-9]+:\s*//')
      fi
      # Fallback to H1 header pattern
      if [[ -z "$other_title" ]]; then
        local raw_h1
        raw_h1=$(grep -m1 -E '^#\s*REQ-[0-9]+\.[0-9]+:' "$other" 2>/dev/null || true)
        other_title=$(echo "$raw_h1" | sed -E 's/^#\s*REQ-[0-9]+\.[0-9]+:\s*(\[[^]]*\]\s*)?//')
      fi
      # If we have a reasonably specific title, check for its mention
      if [[ -n "$other_title" && ${#other_title} -ge 6 ]]; then
        if grep -qiF "$other_title" "$f" 2>/dev/null; then
          ((title_refs++)) || true
        fi
      fi
    done < <(find "$REQ_DIR" -name "REQ-[0-9]*_*.md" -print0 2>/dev/null)

    local total_refs=$((req_refs + title_refs))
    if [[ $has_xref -eq 0 && $total_refs -eq 0 ]]; then
      echo -e "${BLUE}  ℹ INFO: $(basename $f) has no cross-references (may be isolated)${NC}"
      ((INFO++)) || true
      ((isolated++)) || true
    elif [[ $total_refs -gt 0 ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${BLUE}  ℹ INFO: $(basename $f) references ${req_refs} by code and ${title_refs} by title${NC}"
      fi
      ((found++)) || true
    fi
  done < <(find "$REQ_DIR" -name "REQ-[0-9]*_*.md" -print0 2>/dev/null)

  if [[ $isolated -eq 0 ]]; then
    echo -e "${GREEN}  ✓ No isolated requirements found${NC}"
  elif [[ $isolated -eq $total_files && $total_files -gt 0 ]]; then
    # CRITICAL: ALL files are isolated - corpus has no cross-linking
    echo -e "${RED}  ✗ GATE-05 ERROR: ALL $total_files files have no cross-references (corpus completely isolated)${NC}"
    echo -e "${YELLOW}  → Attempting auto-fix: running cross-reference injection script${NC}"
    ((ERRORS++)) || true
    
    # Run the cross-reference script if available
    local xref_script="/tmp/add_cross_refs.py"
    if [[ -f "$xref_script" ]]; then
      echo "  → Executing: python3 $xref_script"
      python3 "$xref_script" 2>&1 | sed 's/^/    /'
      echo "  → Cross-references injected. Re-run validation to confirm."
    else
      echo -e "${YELLOW}  ⚠ Cross-reference script not found at $xref_script${NC}"
      echo "  → Create it with: python3 -c 'from pathlib import Path; ...' (see directive DIR-05)"
    fi
  elif [[ $isolated -gt 0 ]]; then
    echo -e "${BLUE}  ℹ $isolated REQ file(s) with no cross-references (informational)${NC}"
  fi
}

# -----------------------------------------------
# GATE-06: Mermaid Diagram Validation (Optional)
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

  while IFS= read -r -d '' f; do
    if [[ "$(basename "$f")" =~ _index|TEMPLATE|RULES ]]; then continue; fi

    local dir_name
    dir_name=$(dirname "$f" | xargs basename)

    # Derive canonical label from folder name (suffix after REQ-XX_)
    local folder_label
    folder_label=$(echo "$dir_name" | sed -E 's/^REQ-[0-9]{2}_//')

    # Extract custom_fields.domain from frontmatter if present
    local cf_domain=""
    cf_domain=$(awk 'BEGIN{in_front=0; in_cf=0}
      NR==1 && $0=="---"{in_front=1; next}
      in_front==1 && $0=="---"{in_front=0; exit}
      in_front==1 && $0 ~ /^custom_fields:\s*$/ {in_cf=1; next}
      in_front==1 && in_cf==1 && $0 ~ /^\s*domain:\s*/ {
        sub(/^.*domain:\s*/,"",$0);
        gsub(/[" ]/,"",$0);
        print; exit
      }' "$f" 2>/dev/null)

    # Fallback: top-level domain (legacy) inside frontmatter, if any
    local root_domain=""
    root_domain=$(awk 'BEGIN{in_front=0}
      NR==1 && $0=="---"{in_front=1; next}
      in_front==1 && $0=="---"{in_front=0; exit}
      in_front==1 && $0 ~ /^domain:\s*/ {
        sub(/^.*domain:\s*/,"",$0);
        gsub(/[" ]/,"",$0);
        print; exit
      }' "$f" 2>/dev/null)

    # Prefer custom_fields.domain, then root domain, then folder label
    local metadata_domain="${cf_domain:-$root_domain}"

    # Use metadata domain if present; otherwise fall back to folder name
    local domain_to_check="$metadata_domain"
    if [[ -z "$domain_to_check" ]]; then
      domain_to_check="$folder_label"
    fi

    # Check if domain is in VALID_DOMAINS list
    local valid=0
    for domain in "${VALID_DOMAINS[@]}"; do
      if [[ "$domain_to_check" == "$domain" ]]; then
        valid=1
        break
      fi
    done

    if [[ $valid -eq 0 ]]; then
      echo -e "${YELLOW}GATE-W013: $(basename $f) has invalid domain '$domain_to_check' (valid: ${VALID_DOMAINS[*]})${NC}"
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done < <(find "$REQ_DIR" -name "REQ-[0-9]*_*.md" -print0 2>/dev/null)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All REQ have valid domain (folder or metadata)${NC}"
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
    exit 2
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
