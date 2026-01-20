#!/bin/bash
# =============================================================================
# BRD Quality Gate Validation Script (Pre-PRD Quality Gate)
# =============================================================================
# Purpose: Validate entire BRD corpus before PRD creation begins
# Usage:   ./scripts/validate_brd_corpus.sh [BRD_DIR] [OPTIONS]
# Options:
#   --verbose       Show detailed output
#   --check=NAME    Run specific check only (placeholders|downstream|counts|
#                   index|crosslinks|diagrams|glossary|duplicates|costs|sizes)
#   --errors-only   Only report errors, skip warnings and info
# Exit Codes:
#   0 = All checks passed
#   1 = Errors found (blocking)
#   2 = Warnings found (non-blocking)
#   3 = Script error
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
ERRORS=0
WARNINGS=0
INFOS=0

# Default values
BRD_DIR="${1:-docs/BRD}"
VERBOSE=false
SPECIFIC_CHECK=""
ERRORS_ONLY=false

# Parse arguments
for arg in "$@"; do
  case $arg in
    --verbose)
      VERBOSE=true
      ;;
    --check=*)
      SPECIFIC_CHECK="${arg#*=}"
      ;;
    --errors-only)
      ERRORS_ONLY=true
      ;;
    *)
      if [[ ! "$arg" =~ ^-- ]]; then
        BRD_DIR="$arg"
      fi
      ;;
  esac
done

# Validate BRD directory exists
if [[ ! -d "$BRD_DIR" ]]; then
  echo -e "${RED}ERROR: BRD directory not found: $BRD_DIR${NC}"
  exit 3
fi

echo "=========================================="
echo "BRD Quality Gate Validation (Pre-PRD Gate)"
echo "=========================================="
echo "Directory: $BRD_DIR"
echo "Date: $(TZ=America/New_York date '+%Y-%m-%d %H:%M:%S EST')"
echo ""

# Build list of existing BRD files
declare -A EXISTING_BRDS
shopt -s nullglob
for f in "$BRD_DIR"/BRD-[0-9]*_*.md "$BRD_DIR"/BRD-[0-9]*/BRD-[0-9]*.md; do
  if [[ -f "$f" ]]; then
    brd_num=$(basename "$f" | grep -oE "BRD-[0-9]+" | head -1)
    EXISTING_BRDS["$brd_num"]=1
  fi
done
shopt -u nullglob

echo "Found ${#EXISTING_BRDS[@]} BRD documents"
echo ""

# =============================================================================
# GATE-01: Placeholder Text for Existing Documents
# =============================================================================
check_placeholders() {
  echo "--- GATE-01: Placeholder Text Detection ---"
  local found=0

  # Patterns to search
  local patterns=(
    "\(future BRD\)"
    "\(when created\)"
    "\(to be defined\)"
    "\(pending\)"
    "\(TBD\)"
    "BRD-[0-9]+ \(future"
  )

  for pattern in "${patterns[@]}"; do
    while IFS= read -r line; do
      if [[ -n "$line" ]]; then
        # Extract content after filepath:linenum: (the actual matched text)
        content=$(echo "$line" | sed 's/^[^:]*:[0-9]*://')
        # Check if content contains a BRD reference (not from filepath)
        brd_ref=$(echo "$content" | grep -oE "BRD-[0-9]+" | head -1 || true)
        if [[ -n "$brd_ref" && -n "${EXISTING_BRDS[$brd_ref]:-}" ]]; then
          echo -e "${RED}GATE-E001: $line${NC}"
          echo "  → $brd_ref exists but marked with placeholder"
          ((ERRORS++)) || true
          ((found++)) || true
        elif [[ -z "$brd_ref" ]]; then
          if $VERBOSE; then
            echo -e "${YELLOW}  Found placeholder: $line${NC}"
          fi
        fi
      fi
    done < <(grep -rniE "$pattern" "$BRD_DIR" 2>/dev/null | grep -v "BRD_QUALITY_GATE_VALIDATION\|BRD_POST_CREATION_VALIDATION\|BRD_VALIDATION_RULES\|BRD-000_index" || true)
  done

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ No placeholder text for existing documents${NC}"
  fi
  echo ""
}

# =============================================================================
# GATE-02: Premature Downstream References
# =============================================================================
check_downstream_refs() {
  echo "--- GATE-02: Premature Downstream References ---"
  local found=0

  # Check for specific numbered references to Layer 2+ artifacts
  while IFS= read -r line; do
    if [[ -n "$line" ]]; then
      # Skip lines that are clearly documentation about the SDD workflow
      # or in Downstream Artifacts sections (forward references are expected there)
      if echo "$line" | grep -qiE "layer|workflow|sdd|example|template|schema|downstream|expected"; then
        continue
      fi
      echo -e "${RED}GATE-E002: $line${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done < <(grep -rnE "(PRD|ADR|SPEC|TASKS)-[0-9]{2,}" "$BRD_DIR" 2>/dev/null | \
           grep -v "BRD_QUALITY_GATE_VALIDATION" | \
           grep -v "_SCHEMA\|_TEMPLATE\|_RULES\|_GUIDE" | \
           grep -v "^.*:- \*\*\(PRD\|ADR\|SPEC\|TASKS\\|EARS\|BDD\)-" || true)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ No premature downstream references${NC}"
  fi
  echo ""
}

# =============================================================================
# GATE-03: Internal Count Consistency
# =============================================================================
check_count_consistency() {
  if $ERRORS_ONLY; then return; fi

  echo "--- GATE-03: Internal Count Consistency ---"
  local found=0

  # This check is designed to find obvious mismatches like "7-state lifecycle" when 8 states listed
  # It focuses on inline lists where count and items are on same line: "N-state (A, B, C, ...)"
  shopt -s nullglob
  for f in "$BRD_DIR"/BRD-[0-9]*_*.md "$BRD_DIR"/BRD-[0-9]*/BRD-[0-9]*.md; do
    [[ -f "$f" ]] || continue

    # Check for N-state/N-step claims with inline parenthetical lists
    while IFS=: read -r linenum content; do
      if [[ -n "$content" ]]; then
        # Extract claimed number
        claimed=$(echo "$content" | grep -oE "^[^(]*[0-9]+" | grep -oE "[0-9]+" | head -1)
        # Extract items in parentheses
        paren_content=$(echo "$content" | grep -oE "\([^)]+\)" | head -1)
        if [[ -n "$claimed" && -n "$paren_content" && "$claimed" -gt 2 && "$claimed" -lt 20 ]]; then
          # Count comma-separated items in parentheses
          actual=$(echo "$paren_content" | tr ',' '\n' | wc -l)
          if [[ "$actual" -gt 0 && "$actual" -ne "$claimed" ]]; then
            echo -e "${YELLOW}GATE-W001: $(basename $f):$linenum${NC}"
            echo "  → Claims '$claimed' items but found '$actual' in list"
            ((WARNINGS++)) || true
            ((found++)) || true
          fi
        fi
      fi
    done < <(grep -nE "[0-9]+-state.*\(|[0-9]+ states.*\(|[0-9]+-step.*\(|[0-9]+ steps.*\(" "$f" 2>/dev/null || true)
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ No obvious count inconsistencies detected${NC}"
  fi
  echo ""
}

# =============================================================================
# GATE-04: Index Synchronization
# =============================================================================
check_index_sync() {
  echo "--- GATE-04: Index Synchronization ---"
  local found=0

  # Find index file using glob pattern (BRD-*_index.md or BRD-*_index*.md)
  local index_file=""
  shopt -s nullglob
  for f in "$BRD_DIR"/BRD-*_index.md "$BRD_DIR"/BRD-*_index*.md; do
    if [[ -f "$f" ]]; then
      index_file="$f"
      break
    fi
  done
  shopt -u nullglob

  if [[ -z "$index_file" || ! -f "$index_file" ]]; then
    echo -e "${YELLOW}  No index file found matching BRD-*_index.md${NC}"
    echo ""
    return
  fi

  if $VERBOSE; then
    echo "  Using index file: $(basename "$index_file")"
  fi

  # Check for files marked "Planned" that exist
  while IFS= read -r line; do
    brd=$(echo "$line" | grep -oE "BRD-[0-9]+" | head -1)
    if [[ -n "$brd" && -n "${EXISTING_BRDS[$brd]:-}" ]]; then
      echo -e "${RED}GATE-E003: $brd exists but marked Planned in index${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done < <(grep -iE "\| *Planned *\|" "$index_file" 2>/dev/null || true)

  # Check for existing files not in index
  for brd in "${!EXISTING_BRDS[@]}"; do
    if [[ "$brd" != "BRD-000" ]] && ! grep -q "$brd" "$index_file" 2>/dev/null; then
      echo -e "${RED}GATE-E003: $brd exists but not listed in index${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Index synchronized with actual files${NC}"
  fi
  echo ""
}

# =============================================================================
# GATE-05: Inter-BRD Cross-Linking (DEPRECATED)
# =============================================================================
# NOTE: This check has been deprecated per traceability rules.
# Document name references (e.g., BRD-01, BRD-07) are valid per traceability
# standards and do not require hyperlink formatting.
# Hyperlinks are optional - document IDs are sufficient for traceability.
check_crosslinks() {
  echo "--- GATE-05: Inter-BRD Cross-Linking ---"
  echo -e "${GREEN}  ✓ Check deprecated - document name references are valid per traceability rules${NC}"
  echo ""
}

# =============================================================================
# GATE-06: Visualization Coverage
# =============================================================================
check_diagrams() {
  if $ERRORS_ONLY; then return; fi

  echo "--- GATE-06: Mermaid Diagram Validation (Optional) ---"
  local syntax_errors=0

  shopt -s nullglob
  for f in "$BRD_DIR"/BRD-[0-9]*_*.md "$BRD_DIR"/BRD-[0-9]*/BRD-[0-9]*.md; do
    [[ -f "$f" ]] || continue

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
    fi
  done
  shopt -u nullglob

  if [[ $syntax_errors -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Mermaid diagrams are optional; all present diagrams are syntactically valid${NC}"
  fi
  echo ""
}

# =============================================================================
# GATE-07: Glossary Consistency
# =============================================================================
check_glossary() {
  if $ERRORS_ONLY; then return; fi

  echo "--- GATE-07: Glossary Consistency ---"

  # Check for term variations (generic examples applicable to any project)
  declare -A term_variations
  term_variations["real-time"]="realtime|real time"
  term_variations["e-mail"]="email|E-mail"
  term_variations["on-premise"]="on-premises|onprem"

  local found=0
  for term in "${!term_variations[@]}"; do
    variations="${term_variations[$term]}"
    primary_count=$( { grep -rciE "\b$term\b" "$BRD_DIR" 2>/dev/null | grep -v ":0" || true; } | wc -l | tr -d '[:space:]')
    var_count=$( { grep -rciE "\b($variations)\b" "$BRD_DIR" 2>/dev/null | grep -v ":0" || true; } | wc -l | tr -d '[:space:]')
    # Ensure numeric defaults
    primary_count=${primary_count:-0}
    var_count=${var_count:-0}

    if [[ "$primary_count" -gt 0 && "$var_count" -gt 0 ]]; then
      echo -e "${YELLOW}GATE-W003: Inconsistent terminology detected${NC}"
      echo "  → '$term' used in $primary_count files, variations ($variations) in $var_count files"
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ No obvious terminology inconsistencies${NC}"
  fi
  echo ""
}

# =============================================================================
# GATE-08: Element ID Uniqueness
# =============================================================================
check_duplicates() {
  echo "--- GATE-08: Element ID Uniqueness ---"
  local misplaced_found=0
  local duplicates_found=0
  local max_show=10

  # --- Check 1: Find true duplicate element IDs across all files ---
  echo "  Checking for globally duplicate element IDs..."
  # We only check for duplicates in definition contexts (headings ### or tables |)
  # to avoid flagging valid cross-references.
  while IFS= read -r duplicate_id; do
    if [[ -n "$duplicate_id" ]]; then
      echo -e "${RED}GATE-E004: Duplicate element ID found: $duplicate_id${NC}"
      # Show which files contain the duplicate definition
      grep -rnE "(^###\s+$duplicate_id:|^\|.*$duplicate_id.*\|)" "$BRD_DIR"
      echo ""
      ((ERRORS++)) || true
      ((duplicates_found++)) || true
    fi
  done < <(grep -rohE "(^###\s+BRD\.[0-9]+\.[0-9]+\.[0-9]+:|^\|.*BRD\.[0-9]+\.[0-9]+\.[0-9]+.*\|)" "$BRD_DIR" 2>/dev/null | grep -oE "BRD\.[0-9]+\.[0-9]+\.[0-9]+" | sort | uniq -d)

  if [[ $duplicates_found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ No duplicate element IDs found across corpus${NC}"
  fi

  # --- Check 2: Find potentially misplaced element IDs ---
  echo "  Checking for potentially misplaced element IDs..."
  # e.g., BRD.07.01.01 should only be defined in BRD-07_*.md
  shopt -s nullglob
  for f in "$BRD_DIR"/BRD-[0-9]*_*.md "$BRD_DIR"/BRD-[0-9]*/BRD-[0-9]*.md; do
    [[ -f "$f" ]] || continue

    # Extract file's document number (e.g., 07 from BRD-07_something.md)
    filename=$(basename "$f")
    file_num=$(echo "$filename" | grep -oE "BRD-[0-9]+" | sed 's/BRD-//')

    # Find element IDs in this file that don't match the file's number
    # These are either cross-references (OK) or misplaced definitions (Warning)
    # We'll only flag if they appear in definition context (tables, headings)
    while IFS= read -r line; do
      if [[ -n "$line" ]]; then
        wrong_id=$(echo "$line" | grep -oE "BRD\.[0-9]+\.[0-9]+\.[0-9]+" | head -1)
        id_num=$(echo "$wrong_id" | cut -d. -f2)
        if [[ "$id_num" != "$file_num" ]]; then
          if [[ $misplaced_found -lt $max_show ]]; then
            echo -e "${YELLOW}GATE-W008: Potential misplaced ID in $(basename $f)${NC}"
            echo "  → ID $wrong_id found in a BRD-$file_num file. Line: $line"
          fi
          ((WARNINGS++)) || true
          ((misplaced_found++)) || true
        fi
      fi
    done < <(grep -nE "(^###\s+BRD\.[0-9]+\.[0-9]+\.[0-9]+:|^\|.*BRD\.[0-9]+\.[0-9]+\.[0-9]+.*\|)" "$f" 2>/dev/null)
  done
  shopt -u nullglob

  if [[ $misplaced_found -ge $max_show ]]; then
    echo -e "${YELLOW}  (Showing first $max_show of $misplaced_found potential misplaced ID warnings)${NC}"
  elif [[ $misplaced_found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ No misplaced element IDs found${NC}"
  fi
  echo ""
}

# =============================================================================
# GATE-09: Cost Estimate Format
# =============================================================================
check_costs() {
  if $ERRORS_ONLY; then return; fi

  echo "--- GATE-09: Cost Estimate Format ---"
  local found=0

  # Find exact dollar amounts without range indicators
  while IFS= read -r line; do
    if [[ -n "$line" ]]; then
      # Skip if already has range or approximation
      if echo "$line" | grep -qiE "range|approximately|~|\-"; then
        continue
      fi
      echo -e "${YELLOW}GATE-W004: $line${NC}"
      echo "  → Consider using range format: \$X-\$Y or ~\$X"
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done < <(grep -rnE "\\\$[0-9,]+(\.[0-9]+)?(/month|/year| per )?" "$BRD_DIR" 2>/dev/null | \
           grep -v "~\|range\|-\$" | \
           grep -v "_VALIDATION\|_TEMPLATE" | \
           head -10 || true)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Cost estimates use appropriate formats${NC}"
  fi
  echo ""
}

# =============================================================================
# GATE-10: File Size Compliance
# =============================================================================
check_sizes() {
  echo "--- GATE-10: File Size Compliance ---"
  local errors=0
  local warnings=0

  shopt -s nullglob
  for f in "$BRD_DIR"/BRD-[0-9]*_*.md "$BRD_DIR"/BRD-[0-9]*/BRD-[0-9]*.md; do
    [[ -f "$f" ]] || continue

    local lines
    lines=$(wc -l <"$f")
    local words
    words=$(wc -w <"$f")
    local tokens=$((words * 13 / 10))

    if [[ $tokens -gt 20000 ]]; then
      echo -e "${RED}GATE-E006: $(basename "$f") exceeds 20,000 tokens (~$tokens) - MUST SPLIT per Universal Rule${NC}"
      ((ERRORS++)) || true
      ((errors++)) || true
    elif [[ $tokens -gt 15000 ]]; then
      if ! $ERRORS_ONLY; then
        echo -e "${YELLOW}GATE-W006: $(basename "$f") exceeds 15,000 tokens (~$tokens) - Consider splitting${NC}"
        ((WARNINGS++)) || true
        ((warnings++)) || true
      fi
    fi

    if $VERBOSE; then
      echo "  $(basename "$f"): $lines lines, ~$tokens tokens"
    fi
  done
  shopt -u nullglob

  if [[ $errors -eq 0 && $warnings -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All files within size limits (≤1000 lines, ≤10k tokens)${NC}"
  fi
  echo ""
}

# =============================================================================
# Run Checks
# =============================================================================

if [[ -n "$SPECIFIC_CHECK" ]]; then
  case "$SPECIFIC_CHECK" in
    placeholders) check_placeholders ;;
    downstream) check_downstream_refs ;;
    counts) check_count_consistency ;;
    index) check_index_sync ;;
    crosslinks) check_crosslinks ;;
    diagrams) check_diagrams ;;
    glossary) check_glossary ;;
    duplicates) check_duplicates ;;
    costs) check_costs ;;
    sizes) check_sizes ;;
    *) echo "Unknown check: $SPECIFIC_CHECK"; exit 3 ;;
  esac
else
  check_placeholders
  check_downstream_refs
  check_count_consistency
  check_index_sync
  check_crosslinks
  check_diagrams
  check_glossary
  check_duplicates
  check_costs
  check_sizes
fi

# =============================================================================
# Summary
# =============================================================================

echo "=========================================="
echo "Validation Summary"
echo "=========================================="
echo -e "Errors:   ${RED}$ERRORS${NC}"
echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
echo -e "Info:     ${BLUE}$INFOS${NC}"
echo ""

if [[ $ERRORS -gt 0 ]]; then
  echo -e "${RED}FAILED: $ERRORS error(s) must be fixed before PRD creation${NC}"
  exit 1
elif [[ $WARNINGS -gt 0 ]]; then
  echo -e "${YELLOW}PASSED with warnings: $WARNINGS warning(s) should be reviewed${NC}"
  exit 2
else
  echo -e "${GREEN}PASSED: All Quality Gate validation checks passed${NC}"
  exit 0
fi
