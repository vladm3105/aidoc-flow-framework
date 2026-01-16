#!/usr/bin/env bash
set -euo pipefail

# Lints documentation files for size limits.
# Target: 300–500 lines; Max: 600 lines (absolute).

# Generic limits (Markdown/feature)
MAX_MD=600
MAX_FEATURE=600
TARGET_LOW=300
TARGET_HIGH=500

# YAML-specific limits (monolithic files)
# Prefer allowing larger YAML specs; warn above 1000, error above 2000
MAX_YAML_WARN=1000
MAX_YAML_ERROR=2000

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"

# Directories to scan (relative to ROOT_DIR)
DIRS=(BRD PRD EARS BDD ADR SYS REQ SPEC CTR TASKS)

# File globs per type
GLOBS=("*.md" "*.feature" "*.yaml")

EXIT=0

echo "[lint_file_sizes] Scanning sizes (target ${TARGET_LOW}-${TARGET_HIGH}; MD/feature max ${MAX_MD}; YAML warn>${MAX_YAML_WARN}, error>${MAX_YAML_ERROR})."

for dir in "${DIRS[@]}"; do
  [ -d "$ROOT_DIR/$dir" ] || continue
  while IFS= read -r -d '' file; do
    # Skip archived and examples and backups
    case "$file" in
      *"/archived/"*|*"/examples/"*|*".bak."*|*"/archive/"*) continue;;
    esac
    lines=$(wc -l < "$file" | tr -d ' ')
    case "$file" in
      *.yaml|*.yml)
        if (( lines > MAX_YAML_ERROR )); then
          echo "ERROR: $file has $lines lines (> ${MAX_YAML_ERROR})."
          echo "  YAML is monolithic; consider logical split only if extremely large or harming maintainability."
          EXIT=1
        elif (( lines > MAX_YAML_WARN )); then
          echo "WARN: $file has $lines lines (above YAML target ${MAX_YAML_WARN}). Generally acceptable; ensure readability."
        fi
        ;;
      *.feature)
        if (( lines > MAX_FEATURE )); then
          echo "ERROR: $file has $lines lines (> ${MAX_FEATURE})."
          echo "  Suggestion: Split into subsections ('.SS.mm') and add aggregator ('.SS.00') as needed."
          EXIT=1
        elif (( lines > TARGET_HIGH )); then
          echo "WARN: $file has $lines lines (above target ${TARGET_HIGH}). Consider splitting soon."
        fi
        ;;
      *)
        if (( lines > MAX_MD )); then
          echo "ERROR: $file has $lines lines (> ${MAX_MD})."
          echo "  Suggestion: Split into section files using the type's SECTION-TEMPLATE and update the index."
          EXIT=1
        elif (( lines > TARGET_HIGH )); then
          echo "WARN: $file has $lines lines (above target ${TARGET_HIGH}). Consider splitting soon."
        fi
        ;;
    esac
  done < <(find "$ROOT_DIR/$dir" \( -name "*.md" -o -name "*.feature" -o -name "*.yaml" \) -type f -print0)
done

if (( EXIT != 0 )); then
  echo "[lint_file_sizes] One or more files exceed max thresholds (MD/feature>${MAX_MD}, YAML>${MAX_YAML_ERROR})."
else
  echo "[lint_file_sizes] OK: No files exceed max thresholds (MD/feature<=${MAX_MD}, YAML<=${MAX_YAML_ERROR})."
fi

exit "$EXIT"
