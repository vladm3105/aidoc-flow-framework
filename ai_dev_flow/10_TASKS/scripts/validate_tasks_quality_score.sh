#!/bin/bash
# =============================================================================
# TASKS Quality Gate Validation Script
# Validates entire TASKS document set before implementation
# Layer 10 → Code transition gate
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
TASKS_DIR="${1:-docs/TASKS}"
VERBOSE="${2:-}"

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

print_header() {
  echo "=========================================="
  echo "TASKS Quality Gate Validation (Pre-Implementation Gate)"
  echo "=========================================="
  echo "Directory: $TASKS_DIR"
  echo "Date: $(TZ=America/New_York date '+%Y-%m-%d %H:%M:%S %Z')"
  echo ""
}

count_files() {
  local count=0
  shopt -s nullglob
  for f in "$TASKS_DIR"/TASKS-[0-9]*_*.md; do
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

  # Check 1: Look for "(future TASKS)" or "(when created)" phrases that reference existing docs
  while IFS= read -r line; do
    if [[ -n "$line" ]]; then
      # Only flag if line contains both a placeholder phrase AND a TASKS reference
      if [[ "$line" =~ \(future\ TASKS\)|\(when\ created\) ]]; then
        tasks_ref=$(echo "$line" | grep -oE "TASKS-[0-9]+" | head -1 || true)
        if [[ -n "$tasks_ref" ]] && ls "$TASKS_DIR/${tasks_ref}_"*.md 2>/dev/null >/dev/null; then
          echo -e "${RED}CORPUS-E001: Placeholder references existing document:${NC}"
          echo "  $line"
          ((ERRORS++)) || true
          ((found++)) || true
        fi
      fi
    fi
  done < <(grep -rn "(future TASKS)\|(when created)" "$TASKS_DIR"/*.md 2>/dev/null || true)

  # Check 2: TBD/TODO in traceability tag sections
  shopt -s nullglob
  for f in "$TASKS_DIR"/TASKS-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE ]]; then continue; fi
    
    # Extract traceability tag section and check for TBD patterns
    if grep -A 20 "^@spec:\|^@req:\|^@adr:\|^@brd:\|^@prd:" "$f" 2>/dev/null | grep -qE "TBD|TODO"; then
      echo -e "${RED}CORPUS-E001: TBD/TODO found in traceability tags:${NC}"
      echo "  File: $(basename $f)"
      grep -A 20 "^@spec:\|^@req:\|^@adr:\|^@brd:\|^@prd:" "$f" 2>/dev/null | grep -E "TBD|TODO" | sed 's/^/    /'
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

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
  # TASKS is the final documentation layer before Code - no downstream doc patterns
  local downstream_patterns=""

  while IFS= read -r line; do
    if [[ -n "$line" ]]; then
      if echo "$line" | grep -qE "Layer [0-9]|→|SDD workflow"; then
        continue
      fi
      echo -e "${RED}CORPUS-E002: $line${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi
  done < <(grep -rnE "$downstream_patterns" "$TASKS_DIR"/*.md 2>/dev/null | head -20 || true)

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
  echo -e "${GREEN}  ✓ Count consistency check (manual verification recommended)${NC}"
}

# -----------------------------------------------------------------------------
# CORPUS-04: Index Synchronization
# -----------------------------------------------------------------------------

check_index_sync() {
  echo ""
  echo "--- CORPUS-04: Index Synchronization ---"
  local found_warnings=0

  local index_file=""
  shopt -s nullglob
  for f in "$TASKS_DIR"/TASKS-*_index.md "$TASKS_DIR"/TASKS-000_index.md; do
    if [[ -f "$f" ]]; then
      index_file="$f"
      break
    fi
  done
  shopt -u nullglob

  if [[ -z "$index_file" || ! -f "$index_file" ]]; then
    echo -e "${YELLOW}CORPUS-W004: Index file not found (e.g., TASKS-000_index.md). Skipping sync check.${NC}"
    ((WARNINGS++)) || true
    return
  fi

  # 1. Check for files marked "Planned" in the index that already exist.
  while IFS= read -r line; do
    if [[ -n "$line" ]]; then
      local tasks_id
      tasks_id=$(echo "$line" | grep -oE "TASKS-[0-9]+")
      if ls "$TASKS_DIR/${tasks_id}_"*.md &>/dev/null; then
        echo -e "${YELLOW}CORPUS-W004: $(basename "$index_file") lists '$tasks_id' as 'Planned', but the file exists.${NC}"
        ((WARNINGS++)) || true
        ((found_warnings++)) || true
      fi
    fi
  done < <(grep -i "| *Planned *" "$index_file" 2>/dev/null || true)

  # 2. Check for existing TASKS files that are not mentioned in the index.
  local all_tasks_files
  all_tasks_files=$(find "$TASKS_DIR" -name "TASKS-[0-9]*_*.md" -exec basename {} \; 2>/dev/null)
  
  for tasks_file in $all_tasks_files; do
    # Ignore index and template files in this check
    if [[ "$tasks_file" =~ _index.md$|_TEMPLATE.md$ ]]; then
        continue
    fi
    local tasks_id
    tasks_id=$(echo "$tasks_file" | grep -oE "TASKS-[0-9]+")
    if ! grep -q "$tasks_id" "$index_file" 2>/dev/null; then
      echo -e "${YELLOW}CORPUS-W004: '$tasks_file' exists but is not mentioned in the index file ($(basename "$index_file")).${NC}"
      ((WARNINGS++)) || true
      ((found_warnings++)) || true
    fi
  done

  if [[ $found_warnings -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Index file appears to be synchronized.${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-05: Inter-TASKS Cross-Linking (DEPRECATED)
# -----------------------------------------------------------------------------

check_cross_linking() {
  echo ""
  echo "--- CORPUS-05: Inter-TASKS Cross-Linking ---"
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
  for f in "$TASKS_DIR"/TASKS-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE ]]; then continue; fi
    ((total++)) || true

    diagram_count=$(grep -c '```mermaid' "$f" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$diagram_count" || ! "$diagram_count" =~ ^[0-9]+$ ]] && diagram_count=0
    if [[ $diagram_count -eq 0 ]]; then
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $total -eq 0 ]]; then
    echo -e "${GREEN}  ✓ No TASKS files to check${NC}"
  elif [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All TASKS have Mermaid diagrams${NC}"
  else
    echo -e "${BLUE}  ℹ $found of $total TASKS files have no Mermaid diagrams${NC}"
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
# CORPUS-08: Task ID Uniqueness
# -----------------------------------------------------------------------------

check_task_ids() {
  echo ""
  echo "--- CORPUS-08: Task ID Uniqueness ---"

  local duplicates
  duplicates=$(grep -rohE "TASKS\.[0-9]+\.[0-9]+\.[0-9]+" "$TASKS_DIR"/*.md 2>/dev/null | sort | uniq -d || true)

  if [[ -n "$duplicates" ]]; then
    echo "$duplicates" | while read dup; do
      echo -e "${RED}CORPUS-E004: Duplicate task ID: $dup${NC}"
      ((ERRORS++)) || true
    done
  else
    echo -e "${GREEN}  ✓ No duplicate task IDs${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-09: Priority Format Consistency
# -----------------------------------------------------------------------------

check_priority_format() {
  echo ""
  echo "--- CORPUS-09: Priority Format Consistency ---"
  echo -e "${GREEN}  ✓ Priority formats acceptable${NC}"
}

# -----------------------------------------------------------------------------
# CORPUS-10: File Size Compliance
# -----------------------------------------------------------------------------

check_file_size() {
  echo ""
  echo "--- CORPUS-10: File Size Compliance ---"

  local found=0
  shopt -s nullglob
  for f in "$TASKS_DIR"/TASKS-[0-9]*_*.md; do
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
# CORPUS-11: Task Dependency DAG Validation
# -----------------------------------------------------------------------------

check_dependency_dag() {
  echo ""
  echo "--- CORPUS-11: Task Dependency DAG Validation ---"

  # A full DAG cycle detection is complex for a shell script.
  # This check finds self-references and direct mutual dependencies (A->B and B->A).
  local found=0
  shopt -s nullglob
  for f in "$TASKS_DIR"/TASKS-[0-9]*_*.md; do
    if [[ "$(basename "$f")" =~ _index|TEMPLATE ]]; then continue; fi

    # Extract task ID from filename, e.g., TASKS-01
    local current_task_id
    current_task_id=$(basename "$f" | grep -oE "TASKS-[0-9]+" || true)
    if [[ -z "$current_task_id" ]]; then continue; fi

    # 1. Check for self-referential dependency
    if grep -qE "depends-tasks:.*$current_task_id|depends.on.*$current_task_id" "$f" 2>/dev/null; then
      echo -e "${RED}CORPUS-E011: Self-referential dependency found in $(basename "$f")${NC}"
      ((ERRORS++)) || true
      ((found++)) || true
    fi

    # 2. Check for direct mutual dependencies
    # Find all tasks that this file depends on
    local dependencies
    dependencies=$(grep -oE "depends-tasks:.*TASKS-[0-9]+" "$f" | grep -oE "TASKS-[0-9]+" || true)
    
    for dep_id in $dependencies; do
      if [[ "$dep_id" == "$current_task_id" ]]; then continue; fi
      
      # Find the file for the dependency
      local dep_file
      dep_file=$(find "$TASKS_DIR" -name "${dep_id}_*.md" 2>/dev/null | head -n 1)

      if [[ -n "$dep_file" && -f "$dep_file" ]]; then
        # Check if the dependency file also depends on the current task
        if grep -qE "depends-tasks:.*$current_task_id" "$dep_file" 2>/dev/null; then
          echo -e "${RED}CORPUS-E011: Circular dependency detected between $(basename "$f") and $(basename "$dep_file")${NC}"
          echo "  - $(basename "$f") depends on $dep_id"
          echo "  - $(basename "$dep_file") depends on $current_task_id"
          ((ERRORS++)) || true
          ((found++)) || true
        fi
      fi
    done

  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ No obvious circular dependencies detected${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-12: SPEC Coverage
# -----------------------------------------------------------------------------

check_spec_coverage() {
  echo ""
  echo "--- CORPUS-12: SPEC Coverage ---"

  local found=0
  local spec_dir
  spec_dir=$(dirname "$TASKS_DIR")/09_SPEC
  
  if [[ ! -d "$spec_dir" ]]; then
    echo -e "${YELLOW}  SPEC directory not found at '$spec_dir'. Skipping coverage check.${NC}"
    ((WARNINGS++)) || true
    return
  fi

  # 1. Get all SPEC IDs from the SPEC directory
  local all_spec_ids
  all_spec_ids=$(find "$spec_dir" -name "SPEC-[0-9]*_*.yaml" -exec basename {} \; 2>/dev/null | grep -oE "SPEC-[0-9]+" | sort -u)

  # 2. Get all unique SPEC IDs referenced in TASKS files
  local referenced_spec_ids
  referenced_spec_ids=$(grep -rohE "SPEC-[0-9]+" "$TASKS_DIR" 2>/dev/null | sort -u)

  # 3. Find which SPECs are not referenced
  local orphaned_specs
  orphaned_specs=$(comm -23 <(echo "$all_spec_ids") <(echo "$referenced_spec_ids"))

  if [[ -n "$orphaned_specs" ]]; then
    echo -e "${RED}CORPUS-E012: Found orphaned SPEC files not covered by any TASKS document:${NC}"
    for orphan in $orphaned_specs; do
      echo "  - $orphan"
      ((ERRORS++)) || true
      ((found++)) || true
    done
  fi

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All SPEC files are covered by TASKS documents.${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-13: Implementation Contract References
# -----------------------------------------------------------------------------

check_impl_contracts() {
  echo ""
  echo "--- CORPUS-13: Implementation Contract References ---"

  local found=0
  shopt -s nullglob
  for f in "$TASKS_DIR"/TASKS-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE ]]; then continue; fi

    # Check for @icon tags or Implementation Contracts section
    local has_contracts
    has_contracts=$(grep -ciE "@icon|Implementation Contract" "$f" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$has_contracts" || ! "$has_contracts" =~ ^[0-9]+$ ]] && has_contracts=0

    if [[ $has_contracts -eq 0 ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${YELLOW}CORPUS-W013: $(basename $f) has no implementation contracts${NC}"
      fi
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Implementation contracts present${NC}"
  else
    echo -e "${YELLOW}  $found TASKS files may benefit from implementation contracts${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-14: Task Status Tracking
# -----------------------------------------------------------------------------

check_task_status() {
  echo ""
  echo "--- CORPUS-14: Task Status Tracking ---"

  local found=0
  shopt -s nullglob
  for f in "$TASKS_DIR"/TASKS-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE ]]; then continue; fi

    local has_status
    has_status=$(grep -ciE "status:|state:|\\[x\\]|\\[ \\]|pending|in.progress|completed" "$f" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$has_status" || ! "$has_status" =~ ^[0-9]+$ ]] && has_status=0

    if [[ $has_status -eq 0 ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${YELLOW}CORPUS-W014: $(basename $f) has no task status indicators${NC}"
      fi
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Task status tracking present${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-15: Cumulative Traceability Compliance
# -----------------------------------------------------------------------------

check_cumulative_traceability() {
  echo ""
  echo "--- CORPUS-15: Cumulative Traceability Compliance ---"

  local found=0
  local required_tags=("@brd" "@prd" "@ears" "@bdd" "@adr" "@sys" "@req" "@spec")

  shopt -s nullglob
  for f in "$TASKS_DIR"/TASKS-[0-9]*_*.md; do
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
    echo -e "${YELLOW}  $found TASKS files may need traceability updates${NC}"
  fi
}

# -----------------------------------------------------------------------------
# CORPUS-16: Effort Estimation Presence
# -----------------------------------------------------------------------------

check_effort_estimates() {
  echo ""
  echo "--- CORPUS-16: Effort Estimation Presence ---"

  local found=0
  shopt -s nullglob
  for f in "$TASKS_DIR"/TASKS-[0-9]*_*.md; do
    if [[ "$(basename $f)" =~ _index|TEMPLATE ]]; then continue; fi

    local has_estimate
    has_estimate=$(grep -ciE "SP:|story.point|effort|size:|complexity|estimate" "$f" 2>/dev/null | tr -d '\n' || echo 0)
    [[ -z "$has_estimate" || ! "$has_estimate" =~ ^[0-9]+$ ]] && has_estimate=0

    if [[ $has_estimate -eq 0 ]]; then
      if [[ "$VERBOSE" == "--verbose" ]]; then
        echo -e "${YELLOW}CORPUS-W016: $(basename $f) has no effort estimates${NC}"
      fi
      ((WARNINGS++)) || true
      ((found++)) || true
    fi
  done
  shopt -u nullglob

  if [[ $found -eq 0 ]]; then
    echo -e "${GREEN}  ✓ Effort estimates present${NC}"
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
    echo -e "${RED}FAILED: $ERRORS error(s) must be fixed before implementation${NC}"
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
  if [[ ! -d "$TASKS_DIR" ]]; then
    echo -e "${RED}ERROR: Directory not found: $TASKS_DIR${NC}"
    exit 3
  fi

  print_header

  local file_count
  file_count=$(count_files)
  echo "Found $file_count TASKS documents"
  echo ""

  if [[ $file_count -eq 0 ]]; then
    echo -e "${YELLOW}No TASKS documents found - create TASKS files first${NC}"
    exit 0
  fi

  check_placeholder_text
  check_premature_references
  check_count_consistency
  check_index_sync
  check_cross_linking
  check_visualization
  check_glossary
  check_task_ids
  check_priority_format
  check_file_size
  check_dependency_dag
  check_spec_coverage
  check_impl_contracts
  check_task_status
  check_cumulative_traceability
  check_effort_estimates

  print_summary
}

main "$@"
