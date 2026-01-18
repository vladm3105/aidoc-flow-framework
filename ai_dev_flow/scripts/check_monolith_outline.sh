#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/check_monolith_outline.sh TYPE [-n NN] [-f TEMPLATE_PATH]

Description:
  Extracts the H2 (##) outline from a monolithic template (e.g., BRD-MVP-TEMPLATE.md)
  and prints suggested section filenames following DOCUMENT_SPLITTING_RULES.md.

Arguments:
  TYPE            One of: BRD, PRD, ADR, EARS, SYS (case-insensitive)

Options:
  -n NN           Example document number (e.g., 07) for filename suggestions
  -f PATH         Explicit path to the monolithic template (overrides TYPE path)

Examples:
  scripts/check_monolith_outline.sh BRD -n 12
  scripts/check_monolith_outline.sh PRD
  scripts/check_monolith_outline.sh ADR -f ./ADR/ADR-MVP-TEMPLATE.md -n 03

Notes:
  - Only H2 headings (##) are considered sections. Code fences are ignored.
  - Output is advisory to help align section maps; it does not modify files.
USAGE
}

type_arg=""
nn=""
template_path=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    -n) nn="$2"; shift 2 ;;
    -f) template_path="$2"; shift 2 ;;
    *) type_arg="$1"; shift ;;
  esac
done

if [[ -z "$type_arg" && -z "$template_path" ]]; then
  echo "Error: TYPE or -f TEMPLATE_PATH required" >&2
  usage
  exit 1
fi

shopt -s nocasematch
case "$type_arg" in
  brd|prd|adr|ears|sys)
    type_uc=$(echo "$type_arg" | tr '[:lower:]' '[:upper:]')
    default_path="./${type_uc}/${type_uc}-TEMPLATE.md"
    ;;
  "")
    type_uc=""
    default_path="$template_path"
    ;;
  *)
    echo "Error: Unsupported TYPE '$type_arg' (supported: BRD, PRD, ADR, EARS, SYS)" >&2
    exit 1
    ;;
esac
shopt -u nocasematch

tpl="${template_path:-$default_path}"
if [[ ! -f "$tpl" ]]; then
  echo "Error: Template not found at '$tpl'" >&2
  exit 1
fi

echo "Template: $tpl" >&2

# Extract H2 headings outside code fences
mapfile -t headings < <(awk '
  BEGIN { incode=0 }
  /^```/ { incode = 1 - incode; next }
  incode==0 && /^##[[:space:]]/ { sub(/^##[[:space:]]*/, ""); print }
' "$tpl")

if [[ ${#headings[@]} -eq 0 ]]; then
  echo "No H2 headings found (##). Nothing to map." >&2
  exit 0
fi

echo "Sections detected (order preserved):"
idx=1
for h in "${headings[@]}"; do
  printf "  %2d. %s\n" "$idx" "$h"
  ((idx++))
done

# Suggest filenames
if [[ -n "$type_uc" ]]; then
  echo
  echo "Suggested filenames (per DOCUMENT_SPLITTING_RULES.md):"
  idx=1
  for h in "${headings[@]}"; do
    # slugify
    slug=$(echo "$h" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/_/g; s/^_+|_+$//g; s/_+/_/g')
    if [[ -n "$nn" ]]; then
      printf "  %s-%s.%d_%s.md\n" "$type_uc" "$nn" "$idx" "$slug"
    else
      printf "  %s-NN.%d_%s.md\n" "$type_uc" "$idx" "$slug"
    fi
    ((idx++))
  done
fi

exit 0

