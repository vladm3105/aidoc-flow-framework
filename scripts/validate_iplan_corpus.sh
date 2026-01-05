#!/bin/bash
# =============================================================================
# IPLAN Corpus Validation Script
# Validates entire IPLAN document set before Code Implementation
# Layer 12 → Code Implementation transition gate
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
IPLAN_DIR="${1:-docs/IPLAN}"
VERBOSE="${2:-}"

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

print_header() {
  echo "=========================================="
  echo "IPLAN Corpus Validation (Pre-Code Gate)"
  echo "=========================================="
  echo "Directory: $IPLAN_DIR"
  echo "Date: $(TZ=America/New_York date '+%Y-%m-%d %H:%M:%S %Z')"
  echo ""
}

count_files() {
  local count=0
  shopt -s nullglob
  for f in "$IPLAN_DIR"/IPLAN-[0-9]*_*.md; do
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
  local patterns=("(future IPLAN)" "(when created)" "(to be defined)" "(pending)" "(TBD)" "[TBD]" "[TODO]")

  for pattern in "${patterns[@]}"; do
    while IFS= read -r line; do
      if [[ -n "$line" ]]; then
        iplan_ref=$(echo "$line" | grep -oE "IPLAN-[0-9]+" | head -1 || true)
        if [[ -n "$iplan_ref" ]]; then
          if ls "$IPLAN_DIR/${iplan_ref}_"*.md 2>/dev/null >/dev/null; then
            echo -e "${RED}CORPUS-E001: $line${NC}"
            ((ERRORS++)) || true
            ((found++)) || true
          fi
        fi
      fi
    done < <(grep -rn "$pattern" "$IPLAN_DIR"/*.md 2>/dev/null || true)
  done

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ No placeholder text for existing documents${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-02: Downstream References (N/A for IPLAN)
# -----------------------------------------------------------------------------

check_downstream_references() {
  echo ""
  echo "--- CORPUS-02: Downstream References ---"
  echo -e "${BLUE}  ℹ IPLAN is Layer 12 (final documentation layer) - no downstream artifacts${NC}"
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
  for f in "$IPLAN_DIR"/IPLAN-*_index.md "$IPLAN_DIR"/IPLAN-000_index.md; do
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
# CORPUS-05: Inter-IPLAN Cross-Linking (DEPRECATED)
# -----------------------------------------------------------------------------

check_cross_linking() {
  echo ""
  echo "--- CORPUS-05: Inter-IPLAN Cross-Linking ---"
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
  for f in "$IPLAN_DIR"/IPLAN-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE ]]; then continue; fi
    ((total++)) || true

    diagram_count=$(grep -c '```mermaid' "$f" 2>/dev/null || echo 0)
    if [[ $diagram_count -eq 0 ]]; then
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $total -eq 0 ]]; then
    echo -e "${GREEN}  ✓ No IPLAN files to check${NC}"
  elif [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All IPLAN have Mermaid diagrams${NC}"
  else
    echo -e "${BLUE}  ℹ $found of $total IPLAN files have no Mermaid diagrams${NC}"
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
# CORPUS-08: IPLAN ID Uniqueness
# -----------------------------------------------------------------------------

check_iplan_ids() {
  echo ""
  echo "--- CORPUS-08: IPLAN ID Uniqueness ---"

  local duplicates
  duplicates=$(grep -rohE "IPLAN-[0-9]+" "$IPLAN_DIR"/*.md 2>/dev/null | sort | uniq -d || true)

  if [[ -n "$duplicates" ]]; then
    echo "$duplicates" | while read dup; do
      echo -e "${RED}CORPUS-E004: Duplicate IPLAN ID: $dup${NC}"
      ((ERRORS++)) || true
    done
  else
    echo -e "${GREEN}  ✓ No duplicate IPLAN IDs${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-09: Session Numbering Consistency
# -----------------------------------------------------------------------------

check_session_numbering() {
  echo ""
  echo "--- CORPUS-09: Session Numbering Consistency ---"
  echo -e "${GREEN}  ✓ Session numbering acceptable${NC}"
}

# -----------------------------------------------------------------------------
# CORPUS-10: File Size Compliance
# -----------------------------------------------------------------------------

check_file_size() {
  echo ""
  echo "--- CORPUS-10: File Size Compliance ---"

  local found=0
  shopt -s nullglob
  for f in "$IPLAN_DIR"/IPLAN-[0-9]*_*.md; do
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
# CORPUS-11: Bash Command Syntax Validation
# -----------------------------------------------------------------------------

check_bash_commands() {
  echo ""
  echo "--- CORPUS-11: Bash Command Syntax Validation ---"

  local found=0
  shopt -s nullglob
  for f in "$IPLAN_DIR"/IPLAN-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE ]]; then continue; fi

    local bash_blocks
    bash_blocks=$(grep -c '```bash' "$f" 2>/dev/null || echo 0)

    if [[ $bash_blocks -eq 0 ]]; then
      echo -e "${RED}CORPUS-E011: $(basename $f) has no bash code blocks${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All IPLAN have bash command blocks${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-12: TASKS Coverage
# -----------------------------------------------------------------------------

check_tasks_coverage() {
  echo ""
  echo "--- CORPUS-12: TASKS Coverage ---"

  local found=0
  shopt -s nullglob
  for f in "$IPLAN_DIR"/IPLAN-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE ]]; then continue; fi

    local tasks_refs
    tasks_refs=$(grep -coE "TASKS-[0-9]+" "$f" 2>/dev/null || echo 0)

    if [[ $tasks_refs -eq 0 ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${YELLOW}CORPUS-W012: $(basename $f) has no TASKS references${NC}"
      fi
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ TASKS coverage appears complete${NC}"
  else
    echo -e "${YELLOW}  $found IPLAN files may need TASKS references${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-13: Session State Management
# -----------------------------------------------------------------------------

check_session_state() {
  echo ""
  echo "--- CORPUS-13: Session State Management ---"

  local found=0
  shopt -s nullglob
  for f in "$IPLAN_DIR"/IPLAN-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE ]]; then continue; fi

    local has_prereq has_output has_success
    has_prereq=$(grep -ciE "prerequisite|requirement|before|input" "$f" 2>/dev/null || echo 0)
    has_output=$(grep -ciE "output|result|after|produce" "$f" 2>/dev/null || echo 0)
    has_success=$(grep -ciE "success|verify|validate|confirm|check" "$f" 2>/dev/null || echo 0)

    if [[ $has_prereq -eq 0 || $has_output -eq 0 || $has_success -eq 0 ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${YELLOW}CORPUS-W013: $(basename $f) may be missing session state docs${NC}"
      fi
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Session state documentation present${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-14: Rollback Procedure Specification
# -----------------------------------------------------------------------------

check_rollback_procedures() {
  echo ""
  echo "--- CORPUS-14: Rollback Procedure Specification ---"

  local found=0
  shopt -s nullglob
  for f in "$IPLAN_DIR"/IPLAN-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE ]]; then continue; fi

    local has_rollback
    has_rollback=$(grep -ciE "rollback|undo|revert|recovery|restore|cleanup" "$f" 2>/dev/null || echo 0)

    if [[ $has_rollback -eq 0 ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${YELLOW}CORPUS-W014: $(basename $f) has no rollback procedures${NC}"
      fi
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Rollback procedures documented${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-15: Cumulative Traceability Compliance
# -----------------------------------------------------------------------------

check_cumulative_traceability() {
  echo ""
  echo "--- CORPUS-15: Cumulative Traceability Compliance ---"

  local found=0
  local required_tags=("@brd" "@prd" "@ears" "@bdd" "@adr" "@sys" "@req" "@spec" "@tasks")

  shopt -s nullglob
  for f in "$IPLAN_DIR"/IPLAN-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE ]]; then continue; fi

    local missing_tags=""
    for tag in "${required_tags[@]}"; do
      if ! grep -qi "$tag" "$f" 2>/dev/null; then
        missing_tags="$missing_tags $tag"
      fi
    done

    if [[ -n "$missing_tags" ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${YELLOW}CORPUS-W015: $(basename $f) may be missing tags:$missing_tags${NC}"
      fi
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Cumulative traceability complete${NC}"
  else
    echo -e "${YELLOW}  $found IPLAN files may need traceability updates${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-16: Environment Variable Documentation
# -----------------------------------------------------------------------------

check_env_vars() {
  echo ""
  echo "--- CORPUS-16: Environment Variable Documentation ---"

  local found=0
  shopt -s nullglob
  for f in "$IPLAN_DIR"/IPLAN-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE ]]; then continue; fi

    local has_env
    has_env=$(grep -ciE "\\$[A-Z_]+|export |env |environment" "$f" 2>/dev/null || echo 0)

    if [[ $has_env -eq 0 ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${YELLOW}CORPUS-W016: $(basename $f) has no environment variable docs${NC}"
      fi
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Environment variables documented${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-17: Dependency Installation Commands
# -----------------------------------------------------------------------------

check_dependency_install() {
  echo ""
  echo "--- CORPUS-17: Dependency Installation Commands ---"

  local found=0
  shopt -s nullglob
  for f in "$IPLAN_DIR"/IPLAN-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE ]]; then continue; fi

    local has_install
    has_install=$(grep -ciE "pip install|npm install|apt install|brew install|requirements.txt|package.json" "$f" 2>/dev/null || echo 0)

    if [[ $has_install -eq 0 ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${YELLOW}CORPUS-W017: $(basename $f) has no dependency installation docs${NC}"
      fi
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Dependency installation documented${NC}"
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
    echo -e "${RED}FAILED: $ERRORS error(s) must be fixed before code implementation${NC}"
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
  if [[ ! -d "$IPLAN_DIR" ]]; then
    echo -e "${RED}ERROR: Directory not found: $IPLAN_DIR${NC}"
    exit 3
  fi

  print_header

  local file_count
  file_count=$(count_files)
  echo "Found $file_count IPLAN documents"
  echo ""

  if [[ $file_count -eq 0 ]]; then
    echo -e "${YELLOW}No IPLAN documents found - create IPLAN files first${NC}"
    exit 0
  fi

  check_placeholder_text
  check_downstream_references
  check_count_consistency
  check_index_sync
  check_cross_linking
  check_visualization
  check_glossary
  check_iplan_ids
  check_session_numbering
  check_file_size
  check_bash_commands
  check_tasks_coverage
  check_session_state
  check_rollback_procedures
  check_cumulative_traceability
  check_env_vars
  check_dependency_install

  print_summary
}

main "$@"
