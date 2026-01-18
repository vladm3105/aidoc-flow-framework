#!/bin/bash
# =============================================================================
# PRD Corpus Validation Script (Pre-EARS Quality Gate)
# =============================================================================
# Purpose: Validate entire PRD corpus before EARS creation begins
# Usage:   ./scripts/validate_prd_corpus.sh [PRD_DIR] [OPTIONS]
# Options:
#   --verbose       Show detailed output
#   --check=NAME    Run specific check only:
#                   placeholders|downstream|counts|index|crosslinks|diagrams|
#                   glossary|duplicates|costs|sizes|traceability|coverage|
#                   structure|sys_ready|hypothesis|glossary_path|tokens|yaml|dates
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
PRD_DIR="${1:-docs/PRD}"
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
        PRD_DIR="$arg"
      fi
      ;;
  esac
done

# Validate PRD directory exists
if [[ ! -d "$PRD_DIR" ]]; then
  echo -e "${RED}ERROR: PRD directory not found: $PRD_DIR${NC}"
  exit 3
fi

echo "=========================================="
echo "PRD Corpus Validation (Pre-EARS Gate)"
echo "=========================================="
echo "Directory: $PRD_DIR"
echo "Date: $(TZ=America/New_York date '+%Y-%m-%d %H:%M:%S EST')"
echo ""

# Build list of existing PRD files
declare -A EXISTING_PRDS
shopt -s nullglob
for f in "$PRD_DIR"/PRD-[0-9]*_*.md "$PRD_DIR"/PRD-[0-9]*/PRD-[0-9]*.md; do
  if [[ -f "$f" ]]; then
    prd_num=$(basename "$f" | grep -oE "PRD-[0-9]+" | head -1)
    EXISTING_PRDS["$prd_num"]=1
  fi
done
shopt -u nullglob

echo "Found ${#EXISTING_PRDS[@]} PRD documents"
echo ""

# =============================================================================
# CORPUS-01: Placeholder Text for Existing Documents
# =============================================================================
check_placeholders() {
  echo "--- CORPUS-01: Placeholder Text Detection ---"
  local found=0

  local patterns=(
    "\(future PRD\)"
    "\(when created\)"
    "\(to be defined\)"
    "\(pending\)"
    "\(TBD\)"
    "PRD-[0-9]+ \(future"
  )

  for pattern in "${patterns[@]}"; do
    while IFS= read -r line; do
      if [[ -n "$line" ]]; then
        content=$(echo "$line" | sed 's/^[^:]*:[0-9]*://')
        prd_ref=$(echo "$content" | grep -oE "PRD-[0-9]+" | head -1 || true)
        if [[ -n "$prd_ref" && -n "${EXISTING_PRDS[$prd_ref]:-}" ]]; then
          echo -e "${RED}CORPUS-E001: $line${NC}"
          echo "  → $prd_ref exists but marked with placeholder"
          ((ERRORS++)) || true
          ((found++)) || true
        fi
      fi
    done < <(grep -rniE "$pattern" "$PRD_DIR" 2>/dev/null | grep -v "PRD_CORPUS_VALIDATION\|PRD_VALIDATION_RULES\|PRD-00_index" || true)
  done

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ No placeholder text for existing documents${NC}"
  fi
  echo ""
}

# =============================================================================
# CORPUS-02: Premature Downstream References
# =============================================================================
check_downstream_refs() {
  echo "--- CORPUS-02: Premature Downstream References ---"
  local found=0

  # Check for specific numbered references to Layer 3+ artifacts
  while IFS= read -r line; do
    if [[ -n "$line" ]]; then
      if echo "$line" | grep -qiE "layer|workflow|sdd|example|template|schema|downstream|expected"; then
        continue
      fi
      echo -e "${RED}CORPUS-E002: $line${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done < <(grep -rnE "(ADR|SYS|REQ|SPEC|TASKS-[0-9]{2,}" "$PRD_DIR" 2>/dev/null | \
           grep -v "PRD_CORPUS_VALIDATION" | \
           grep -v "_SCHEMA\|_TEMPLATE\|_RULES\|_GUIDE" || true)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ No premature downstream references${NC}"
  fi
  echo ""
}

# =============================================================================
# CORPUS-03: Internal Count Consistency
# =============================================================================
check_count_consistency() {
  if $ERRORS_ONLY; then return; fi

  echo "--- CORPUS-03: Internal Count Consistency ---"
  local found=0

  shopt -s nullglob
  for f in "$PRD_DIR"/PRD-[0-9]*_*.md "$PRD_DIR"/PRD-[0-9]*/PRD-[0-9]*.md; do
    [[ -f "$f" ]] || continue

    while IFS=: read -r linenum content; do
      if [[ -n "$content" ]]; then
        claimed=$(echo "$content" | grep -oE "^[^(]*[0-9]+" | grep -oE "[0-9]+" | head -1)
        paren_content=$(echo "$content" | grep -oE "\([^)]+\)" | head -1)
        if [[ -n "$claimed" && -n "$paren_content" && "$claimed" -gt 2 && "$claimed" -lt 20 ]]; then
          actual=$(echo "$paren_content" | tr ',' '\n' | wc -l)
          if [[ "$actual" -gt 0 && "$actual" -ne "$claimed" ]]; then
            echo -e "${YELLOW}CORPUS-W001: $(basename $f):$linenum${NC}"
            echo "  → Claims '$claimed' items but found '$actual' in list"
            ((WARNINGS++)) || true
            ((found++)) || true
          fi
        fi
      fi
    done < <(grep -nE "[0-9]+ user stor|[0-9]+ feature|[0-9]+ metric" "$f" 2>/dev/null || true)
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ No obvious count inconsistencies detected${NC}"
  fi
  echo ""
}

# =============================================================================
# CORPUS-04: Index Synchronization
# =============================================================================
check_index_sync() {
  echo "--- CORPUS-04: Index Synchronization ---"
  local found=0

  local index_file=""
  shopt -s nullglob
  for f in "$PRD_DIR"/PRD-*_index.md "$PRD_DIR"/PRD-*_index*.md; do
    if [[ -f "$f" ]]; then
      index_file="$f"
      break
    fi
  done
  shopt -u nullglob

  if [[ -z "$index_file" || ! -f "$index_file" ]]; then
    echo -e "${YELLOW}  Index file not found: $PRD_DIR/PRD-*_index.md${NC}"
    echo ""
    return
  fi

  if $VERBOSE; then
    echo "  Using index file: $(basename "$index_file")"
  fi

  while IFS= read -r line; do
    prd=$(echo "$line" | grep -oE "PRD-[0-9]+" | head -1)
    if [[ -n "$prd" && -n "${EXISTING_PRDS[$prd]:-}" ]]; then
      echo -e "${RED}CORPUS-E003: $prd exists but marked Planned in index${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done < <(grep -iE "\| *Planned *\|" "$index_file" 2>/dev/null || true)

  for prd in "${!EXISTING_PRDS[@]}"; do
    if [[ "$prd" != "PRD-00" && "$prd" != "PRD-000" ]] && ! grep -q "$prd" "$index_file" 2>/dev/null; then
      echo -e "${RED}CORPUS-E003: $prd exists but not listed in index${NC}"
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
# CORPUS-05: Inter-PRD Cross-Linking (DEPRECATED)
# =============================================================================
check_crosslinks() {
  echo "--- CORPUS-05: Inter-PRD Cross-Linking ---"
  echo -e "${GREEN}  ✓ Check deprecated - document name references are valid per traceability rules${NC}"
  echo ""
}

# =============================================================================
# CORPUS-06: Visualization Coverage
# =============================================================================
check_diagrams() {
  if $ERRORS_ONLY; then return; fi

  echo "--- CORPUS-06: Visualization Coverage ---"
  local no_diagrams=0

  shopt -s nullglob
  for f in "$PRD_DIR"/PRD-[0-9]*_*.md "$PRD_DIR"/PRD-[0-9]*/PRD-[0-9]*.md; do
    [[ -f "$f" ]] || continue

    diagram_count=$(grep -c '```mermaid' "$f" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$diagram_count" || ! "$diagram_count" =~ ^[0-9]+$ ]] && diagram_count=0
    if [[ "$diagram_count" -eq 0 ]]; then
      echo -e "${BLUE}CORPUS-I001: $(basename $f) has no Mermaid diagrams${NC}"
      ((INFOS++)) || true
      ((no_diagrams++)) || true
    elif $VERBOSE; then
      echo "  $(basename $f): $diagram_count diagram(s)"
    fi
  done
  shopt -u nullglob

  if [[ $no_diagrams -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All PRDs have diagrams${NC}"
  fi
  echo ""
}

# =============================================================================
# CORPUS-07: Glossary Consistency
# =============================================================================
check_glossary() {
  if $ERRORS_ONLY; then return; fi

  echo "--- CORPUS-07: Glossary Consistency ---"

  declare -A term_variations
  term_variations["real-time"]="realtime|real time"
  term_variations["user-story"]="user story|userstory"
  term_variations["e-mail"]="email|E-mail"

  local found=0
  for term in "${!term_variations[@]}"; do
    variations="${term_variations[$term]}"
    primary_count=$( { grep -rciE "\b$term\b" "$PRD_DIR" 2>/dev/null | grep -v ":0" || true; } | wc -l | tr -d '[:space:]')
    var_count=$( { grep -rciE "\b($variations)\b" "$PRD_DIR" 2>/dev/null | grep -v ":0" || true; } | wc -l | tr -d '[:space:]')
    primary_count=${primary_count:-0}
    var_count=${var_count:-0}

    if [[ "$primary_count" -gt 0 && "$var_count" -gt 0 ]]; then
      echo -e "${YELLOW}CORPUS-W003: Inconsistent terminology detected${NC}"
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
# CORPUS-08: Element ID Uniqueness
# =============================================================================
check_duplicates() {
  echo "--- CORPUS-08: Element ID Uniqueness ---"
  local found=0
  local max_show=10

  shopt -s nullglob
  for f in "$PRD_DIR"/PRD-[0-9]*_*.md "$PRD_DIR"/PRD-[0-9]*/PRD-[0-9]*.md; do
    [[ -f "$f" ]] || continue

    filename=$(basename "$f")
    file_num=$(echo "$filename" | grep -oE "PRD-[0-9]+" | sed 's/PRD-//')

    while IFS= read -r line; do
      if [[ -n "$line" ]]; then
        wrong_id=$(echo "$line" | grep -oE "PRD\.[0-9]+\.[0-9]+\.[0-9]+" | head -1)
        id_num=$(echo "$wrong_id" | cut -d. -f2)
        if [[ "$id_num" != "$file_num" ]]; then
          if echo "$line" | grep -qE "^\|.*\|.*\|"; then
            if [[ $found -lt $max_show ]]; then
              echo -e "${YELLOW}CORPUS-W008: Potential misplaced ID in $(basename $f)${NC}"
              echo "  → $wrong_id defined in PRD-$file_num file"
            fi
            ((WARNINGS++)) || true
            ((found++)) || true
          fi
        fi
      fi
    done < <(grep -nE "PRD\.[0-9]+\.[0-9]+\.[0-9]+" "$f" 2>/dev/null | grep -E ":[0-9]+:\|" || true)
  done
  shopt -u nullglob

  if [[ $found -ge $max_show ]]; then
    echo -e "${YELLOW}  (Showing first $max_show of $found potential issues)${NC}"
  elif [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Element IDs appear correctly placed${NC}"
  fi
  echo ""
}

# =============================================================================
# CORPUS-09: Cost Estimate Format
# =============================================================================
check_costs() {
  if $ERRORS_ONLY; then return; fi

  echo "--- CORPUS-09: Cost Estimate Format ---"
  local found=0

  while IFS= read -r line; do
    if [[ -n "$line" ]]; then
      if echo "$line" | grep -qiE "range|approximately|~|\-"; then
        continue
      fi
      echo -e "${YELLOW}CORPUS-W004: $line${NC}"
      echo "  → Consider using range format: \$X-\$Y or ~\$X"
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done < <(grep -rnE "\\\$[0-9,]+(\.[0-9]+)?(/month|/year| per )?" "$PRD_DIR" 2>/dev/null | \
           grep -v "~\|range\|-\$" | \
           grep -v "_VALIDATION\|_TEMPLATE" | \
           head -10 || true)

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Cost estimates use appropriate formats${NC}"
  fi
  echo ""
}

# =============================================================================
# CORPUS-10: File Size Compliance
# =============================================================================
check_sizes() {
  echo "--- CORPUS-10: File Size Compliance ---"
  local errors=0
  local warnings=0

  shopt -s nullglob
  for f in "$PRD_DIR"/PRD-[0-9]*_*.md "$PRD_DIR"/PRD-[0-9]*/PRD-[0-9]*.md; do
    [[ -f "$f" ]] || continue

    # MVP detection
    is_mvp=false
    if [[ "$f" == *"MVP"* ]] || grep -q "template_variant: mvp" "$f" 2>/dev/null || grep -q "template_profile: mvp" "$f" 2>/dev/null; then
      is_mvp=true
    fi

    if $is_mvp; then
      if [[ "$lines" -gt 800 ]]; then
        echo -e "${RED}CORPUS-E005: MVP file $(basename $f) exceeds 800 lines ($lines)${NC}"
        ((ERRORS++)) || true
        ((errors++)) || true
      elif [[ "$lines" -gt 500 ]]; then
        if ! $ERRORS_ONLY; then
          echo -e "${YELLOW}CORPUS-W005: MVP file $(basename $f) exceeds 500 lines ($lines)${NC}"
          ((WARNINGS++)) || true
          ((warnings++)) || true
        fi
      fi
    else
      # Standard limits
      if [[ "$lines" -gt 1200 ]]; then
        echo -e "${RED}CORPUS-E005: $(basename $f) exceeds 1200 lines ($lines)${NC}"
        ((ERRORS++)) || true
        ((errors++)) || true
      elif [[ "$lines" -gt 600 ]]; then
        if ! $ERRORS_ONLY; then
          echo -e "${YELLOW}CORPUS-W005: $(basename $f) exceeds 600 lines ($lines)${NC}"
          ((WARNINGS++)) || true
          ((warnings++)) || true
        fi
      fi
    fi 

    if $VERBOSE; then
      echo "  $(basename $f): $lines lines"
    fi
  done
  shopt -u nullglob

  if [[ $errors -eq 0 && $warnings -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All files within size limits${NC}"
  fi
  echo ""
}

# =============================================================================
# CORPUS-11: BRD Traceability Completeness
# =============================================================================
check_traceability() {
  echo "--- CORPUS-11: BRD Traceability Completeness ---"
  local found=0

  shopt -s nullglob
  for f in "$PRD_DIR"/PRD-[0-9]*_*.md "$PRD_DIR"/PRD-[0-9]*/PRD-[0-9]*.md; do
    [[ -f "$f" ]] || continue

    # Skip index files
    if [[ "$(basename $f)" =~ _index ]]; then
      continue
    fi

    if ! grep -q "@brd:" "$f" 2>/dev/null; then
      echo -e "${RED}CORPUS-E011: $(basename $f) missing @brd traceability tags${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    elif $VERBOSE; then
      brd_count=$(grep -c "@brd:" "$f" 2>/dev/null | tr -d '\n' || echo 0)
      [[ -z "$brd_count" || ! "$brd_count" =~ ^[0-9]+$ ]] && brd_count=0
      echo "  $(basename $f): $brd_count @brd tags"
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All PRDs have BRD traceability tags${NC}"
  fi
  echo ""
}

# =============================================================================
# CORPUS-12: User Story Coverage
# =============================================================================
check_coverage() {
  if $ERRORS_ONLY; then return; fi

  echo "--- CORPUS-12: User Story Coverage ---"
  echo -e "${BLUE}  ℹ Manual verification recommended for BRD→PRD coverage${NC}"
  echo ""
}

# =============================================================================
# CORPUS-13: Template Structure Compliance
# =============================================================================
check_template_structure() {
  echo "--- CORPUS-13: Template Structure Compliance ---"
  local found=0

  local REQUIRED_SECTIONS=(
    "Document Control" "Executive Summary" "Product Vision"
    "Target Audience" "User Stories" "Feature Requirements"
    "Success Metrics" "Acceptance Criteria" "Constraints"
    "Dependencies" "Risks" "Timeline" "MVP Scope"
    "Future Considerations" "Traceability" "Glossary"
  )

  shopt -s nullglob
  for f in "$PRD_DIR"/PRD-[0-9]*_*.md "$PRD_DIR"/PRD-[0-9]*/PRD-[0-9]*.md; do
    [[ -f "$f" ]] || continue
    [[ "$(basename $f)" =~ _index|TEMPLATE|template ]] && continue

    for section in "${REQUIRED_SECTIONS[@]}"; do
      if ! grep -qiE "^##? .*$section" "$f" 2>/dev/null; then
        echo -e "${RED}CORPUS-E013: $(basename $f) missing section: $section${NC}"
        ((ERRORS++)) || true
        ((found++)) || true
      fi
    done
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All PRDs have required template sections${NC}"
  fi
  echo ""
}

# =============================================================================
# CORPUS-14: SYS-Ready Score Validation
# =============================================================================
check_sys_ready_score() {
  echo "--- CORPUS-14: SYS-Ready Score Validation ---"
  local found=0

  shopt -s nullglob
  for f in "$PRD_DIR"/PRD-[0-9]*_*.md "$PRD_DIR"/PRD-[0-9]*/PRD-[0-9]*.md; do
    [[ -f "$f" ]] || continue
    [[ "$(basename $f)" =~ _index|TEMPLATE|template ]] && continue

    score=$(grep -oP 'sys_ready_score:\s*\K[0-9]+' "$f" 2>/dev/null || echo "0")
    if [[ $score -lt 85 ]]; then
      echo -e "${RED}CORPUS-E014: $(basename $f) SYS-Ready score $score < 85 (MVP threshold)${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    elif $VERBOSE; then
      echo "  $(basename $f): SYS-Ready score = $score"
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All PRDs meet SYS-Ready threshold (>= 85)${NC}"
  fi
  echo ""
}

# =============================================================================
# CORPUS-15: MVP Hypothesis Format
# =============================================================================
check_mvp_hypothesis() {
  if $ERRORS_ONLY; then return; fi

  echo "--- CORPUS-15: MVP Hypothesis Format ---"
  local found=0

  shopt -s nullglob
  for f in "$PRD_DIR"/PRD-[0-9]*_*.md "$PRD_DIR"/PRD-[0-9]*/PRD-[0-9]*.md; do
    [[ -f "$f" ]] || continue
    [[ "$(basename $f)" =~ _index|TEMPLATE|template ]] && continue

    if ! grep -qiE 'We believe that.*will.*if we' "$f" 2>/dev/null; then
      echo -e "${YELLOW}CORPUS-W015: $(basename $f) may lack properly formatted MVP hypothesis${NC}"
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All PRDs have MVP hypothesis format${NC}"
  fi
  echo ""
}

# =============================================================================
# CORPUS-16: Glossary Path Standardization
# =============================================================================
check_glossary_path() {
  if $ERRORS_ONLY; then return; fi

  echo "--- CORPUS-16: Glossary Path Standardization ---"
  local found=0

  shopt -s nullglob
  for f in "$PRD_DIR"/PRD-[0-9]*_*.md "$PRD_DIR"/PRD-[0-9]*/PRD-[0-9]*.md; do
    [[ -f "$f" ]] || continue
    [[ "$(basename $f)" =~ _index|TEMPLATE|template ]] && continue

    if grep -q "Glossary" "$f" 2>/dev/null; then
      if ! grep -qE 'glossary\.md|Glossary.*\|' "$f" 2>/dev/null; then
        echo -e "${YELLOW}CORPUS-W016: $(basename $f) glossary path may not be standardized${NC}"
        ((WARNINGS++)) || true
        ((found++)) || true
      fi
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Glossary paths standardized${NC}"
  fi
  echo ""
}

# =============================================================================
# CORPUS-17: Token Count Compliance
# =============================================================================
check_token_count() {
  echo "--- CORPUS-17: Token Count Compliance ---"
  local errors=0
  local warnings=0

  shopt -s nullglob
  for f in "$PRD_DIR"/PRD-[0-9]*_*.md "$PRD_DIR"/PRD-[0-9]*/PRD-[0-9]*.md; do
    [[ -f "$f" ]] || continue
    [[ "$(basename $f)" =~ _index|TEMPLATE|template ]] && continue

    words=$(wc -w < "$f")
    tokens=$((words * 13 / 10))

    if [[ $tokens -gt 80000 ]]; then
      echo -e "${RED}CORPUS-E017: $(basename $f) exceeds 80K tokens (~$tokens)${NC}"
      ((ERRORS++)) || true
      ((errors++)) || true
    elif [[ $tokens -gt 40000 ]]; then
      if ! $ERRORS_ONLY; then
        echo -e "${YELLOW}CORPUS-W017: $(basename $f) exceeds 40K tokens (~$tokens)${NC}"
        ((WARNINGS++)) || true
        ((warnings++)) || true
      fi
    elif $VERBOSE; then
      echo "  $(basename $f): ~$tokens tokens"
    fi
  done
  shopt -u nullglob

  if [[ $errors -eq 0 && $warnings -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All files within token limits${NC}"
  fi
  echo ""
}

# =============================================================================
# CORPUS-18: YAML Frontmatter Validation
# =============================================================================
check_yaml_frontmatter() {
  if $ERRORS_ONLY; then return; fi

  echo "--- CORPUS-18: YAML Frontmatter Validation ---"
  local found=0

  local REQUIRED_FIELDS=("title" "status" "version" "created" "modified")

  shopt -s nullglob
  for f in "$PRD_DIR"/PRD-[0-9]*_*.md "$PRD_DIR"/PRD-[0-9]*/PRD-[0-9]*.md; do
    [[ -f "$f" ]] || continue
    [[ "$(basename $f)" =~ _index|TEMPLATE|template ]] && continue

    if head -1 "$f" | grep -q "^---"; then
      for field in "${REQUIRED_FIELDS[@]}"; do
        if ! grep -q "^$field:" "$f" 2>/dev/null; then
          echo -e "${YELLOW}CORPUS-W018: $(basename $f) missing YAML field: $field${NC}"
          ((WARNINGS++)) || true
          ((found++)) || true
        fi
      done
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ YAML frontmatter fields present${NC}"
  fi
  echo ""
}

# =============================================================================
# CORPUS-19: ISO Date Format Compliance
# =============================================================================
check_date_format() {
  if $ERRORS_ONLY; then return; fi

  echo "--- CORPUS-19: ISO Date Format Compliance ---"
  local found=0

  shopt -s nullglob
  for f in "$PRD_DIR"/PRD-[0-9]*_*.md "$PRD_DIR"/PRD-[0-9]*/PRD-[0-9]*.md; do
    [[ -f "$f" ]] || continue
    [[ "$(basename $f)" =~ _index|TEMPLATE|template ]] && continue

    bad_dates=$(grep -oE '[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}|[A-Za-z]{3} [0-9]{1,2},? [0-9]{4}' "$f" 2>/dev/null | head -3 || true)
    if [[ -n "$bad_dates" ]]; then
      echo -e "${YELLOW}CORPUS-W019: $(basename $f) contains non-ISO dates${NC}"
      echo "  → Found: $(echo $bad_dates | tr '\n' ' ')"
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All dates use ISO format${NC}"
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
    traceability) check_traceability ;;
    coverage) check_coverage ;;
    structure) check_template_structure ;;
    sys_ready) check_sys_ready_score ;;
    hypothesis) check_mvp_hypothesis ;;
    glossary_path) check_glossary_path ;;
    tokens) check_token_count ;;
    yaml) check_yaml_frontmatter ;;
    dates) check_date_format ;;
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
  check_traceability
  check_coverage
  check_template_structure
  check_sys_ready_score
  check_mvp_hypothesis
  check_glossary_path
  check_token_count
  check_yaml_frontmatter
  check_date_format
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
  echo -e "${RED}FAILED: $ERRORS error(s) must be fixed before EARS creation${NC}"
  exit 1
elif [[ $WARNINGS -gt 0 ]]; then
  echo -e "${YELLOW}PASSED with warnings: $WARNINGS warning(s) should be reviewed${NC}"
  exit 2
else
  echo -e "${GREEN}PASSED: All corpus validation checks passed${NC}"
  exit 0
fi
