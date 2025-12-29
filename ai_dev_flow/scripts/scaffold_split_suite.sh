#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# BDD Split Suite Scaffolding Script
# =============================================================================
# Purpose: Generate standardized BDD split-suite structure from templates
# Framework: AI Dev Flow SDD methodology
# Version: 1.0
# Date: 2025-12-27
# =============================================================================

usage() {
  cat <<USAGE
Usage: $0 -n <suite_number> -s <slug> -t <title> [options]

Required:
  -n    Suite number (e.g., 07)
  -s    Suite slug (e.g., level1_portfolio_orchestrator)
  -t    Suite title (e.g., "Level 1 Portfolio Orchestrator")

Options:
  -p    PRD doc number (default: same as suite number)
  -e    EARS doc number (default: same as suite number)
  -b    BRD doc number (default: 01)
  -z    IANA timezone placeholder replacement (default: America/New_York)
  -d    Docs base dir (default: docs/BDD)
  -y    Assume yes; do not prompt (default: false)

Example:
  $0 -n 07 -s level1_portfolio_orchestrator -t "Level 1 Portfolio Orchestrator"

Output:
  docs/BDD/BDD-NN_[slug]/           # Suite directory
  ├── README.md                      # Suite overview
  ├── TRACEABILITY.md                # Upstream/downstream mapping
  ├── GLOSSARY.md                    # Domain terminology
  └── features/                      # Feature files directory
      ├── BDD-NN.SS_circuit_breaker.feature
      ├── BDD-NN.SS_daily_lifecycle.feature
      ├── BDD-NN.SS_phase_management.feature
      ├── BDD-NN.SS_risk_prechecks.feature
      ├── BDD-NN.SS_state_recovery.feature
      └── BDD-NN.SS_strategy_governance.feature
  docs/BDD/BDD-NN_[slug]/BDD-NN.SS.00_[slug].feature    # Aggregator (redirect)
USAGE
}

confirm() {
  local msg=${1:-Proceed?}
  if [[ "$ASSUME_YES" == "1" ]]; then return 0; fi
  read -rp "$msg [y/N]: " ans || true
  [[ "$ans" =~ ^[Yy]$ ]]
}

# =============================================================================
# Parse Arguments
# =============================================================================
NN=""; SLUG=""; TITLE=""; PRDNN=""; EARSNN=""; BRDNN="01"
TZ="America/New_York"; DOCS_DIR="docs/BDD"; ASSUME_YES="0"

while getopts ":n:s:t:p:e:b:z:d:y" opt; do
  case $opt in
    n) NN="$OPTARG" ;;
    s) SLUG="$OPTARG" ;;
    t) TITLE="$OPTARG" ;;
    p) PRDNN="$OPTARG" ;;
    e) EARSNN="$OPTARG" ;;
    b) BRDNN="$OPTARG" ;;
    z) TZ="$OPTARG" ;;
    d) DOCS_DIR="$OPTARG" ;;
    y) ASSUME_YES="1" ;;
    *) usage; exit 2 ;;
  esac
done

if [[ -z "$NN" || -z "$SLUG" || -z "$TITLE" ]]; then
  usage; exit 2
fi

PRDNN=${PRDNN:-$NN}
EARSNN=${EARSNN:-$NN}

# =============================================================================
# Validate Dependencies
# =============================================================================
command -v rg >/dev/null 2>&1 || { echo "Error: ripgrep (rg) is required." >&2; exit 1; }

TEMPL_DIR="BDD/templates/BDD_SPLIT_SUITE"
[[ -d "$TEMPL_DIR" ]] || { echo "Error: Templates dir not found: $TEMPL_DIR (run from repo root)" >&2; exit 1; }

# =============================================================================
# Setup Target Directory
# =============================================================================
TARGET_DIR="$DOCS_DIR/BDD-$NN_${SLUG}"
if [[ -d "$TARGET_DIR" ]]; then
  echo "Target exists: $TARGET_DIR"
  confirm "Continue and possibly overwrite files?" || exit 1
else
  mkdir -p "$TARGET_DIR/features"
fi

# =============================================================================
# Template Rendering Function
# =============================================================================
copy_and_render() {
  local src="$1"; local dst="$2"
  sed \
    -e "s/BDD-NN/BDD-$NN/g" \
    -e "s/\[Suite Title\]/$TITLE/g" \
    -e "s/\[suite-slug\]/$SLUG/g" \
    -e "s/<IANA_timezone>/$TZ/g" \
    -e "s/PRD\.NN/PRD\.$PRDNN/g" \
    -e "s/EARS\.NN/EARS\.$EARSNN/g" \
    -e "s/BRD\.NN/BRD\.$BRDNN/g" \
    "$src" > "$dst"
}

# =============================================================================
# Render Companion Files
# =============================================================================
echo "Rendering companion files..."
copy_and_render "$TEMPL_DIR/README_TEMPLATE.md" "$TARGET_DIR/README.md"
copy_and_render "$TEMPL_DIR/TRACEABILITY_TEMPLATE.md" "$TARGET_DIR/TRACEABILITY.md"
copy_and_render "$TEMPL_DIR/GLOSSARY_TEMPLATE.md" "$TARGET_DIR/GLOSSARY.md"

# =============================================================================
# Render Feature Files
# =============================================================================
echo "Rendering feature files..."
for f in "$TEMPL_DIR"/features/BDD-NN_*.feature; do
  base=$(basename "$f")
  out_name=${base/BDD-NN_/BDD-$NN_}
  copy_and_render "$f" "$TARGET_DIR/features/$out_name"
done

# =============================================================================
# Create/Refresh Top-Level Redirect Stub
# =============================================================================
STUB_PATH="$DOCS_DIR/BDD-$NN_${SLUG}.feature"
if [[ -f "$STUB_PATH" ]]; then
  ts=$(date +%Y%m%d%H%M%S)
  echo "Existing top-level feature detected: $STUB_PATH"
  if confirm "Backup and replace with framework redirect stub?"; then
    cp "$STUB_PATH" "${STUB_PATH}.bak-$ts"
    copy_and_render "$TEMPL_DIR/REDIRECT_STUB_TEMPLATE.feature" "$STUB_PATH"
  else
    echo "Skipping redirect stub replacement for $STUB_PATH"
  fi
else
  copy_and_render "$TEMPL_DIR/REDIRECT_STUB_TEMPLATE.feature" "$STUB_PATH"
fi

echo ""
echo "✅ Scaffolded split suite at: $TARGET_DIR"
echo ""

# =============================================================================
# Basic Validation Checks
# =============================================================================
echo "Running validation checks..."
ERRORS=0

# Check 1: File size >500 lines
echo -n "  [CHECK 1] File size limits... "
while IFS= read -r file; do
  lines=$(wc -l < "$file" | awk '{print $1}')
  if [[ $lines -gt 500 ]]; then
    echo "❌ FAILED"
    echo "    ERROR: >500 lines: $file ($lines lines)"
    ERRORS=$((ERRORS+1))
  fi
done < <(find "$TARGET_DIR/features" -type f -name "*.feature" 2>/dev/null)
[[ $ERRORS -eq 0 ]] && echo "✅ PASS"

# Check 2: Markdown headings in .feature
echo -n "  [CHECK 2] No Markdown headings in .feature... "
if rg -n "^##+\s" "$TARGET_DIR"/features/*.feature >/dev/null 2>&1; then
  echo "❌ FAILED"
  echo "    ERROR: Markdown headings found in .feature files"
  rg -n "^##+\s" "$TARGET_DIR"/features/*.feature 2>/dev/null || true
  ERRORS=$((ERRORS+1))
else
  echo "✅ PASS"
fi

# Check 3: Raw durations/attempts heuristic
echo -n "  [CHECK 3] No raw numeric durations... "
if rg -n "WITHIN\s+[0-9]+\s+(seconds?|minutes?)|after\s+[0-9]+\s+(attempts?|retries?)|\b[0-9]+\s+(seconds?|minutes?)\b" "$TARGET_DIR"/features/*.feature >/dev/null 2>&1; then
  echo "❌ FAILED"
  echo "    ERROR: Raw numeric durations/attempts detected"
  rg -n "WITHIN\s+[0-9]+\s+(seconds?|minutes?)|after\s+[0-9]+\s+(attempts?|retries?)|\b[0-9]+\s+(seconds?|minutes?)\b" "$TARGET_DIR"/features/*.feature 2>/dev/null || true
  ERRORS=$((ERRORS+1))
else
  echo "✅ PASS"
fi

# Check 4: Ambiguous TZ abbreviations
echo -n "  [CHECK 4] No ambiguous timezone abbreviations... "
if rg -n "\b(EST|EDT|PST|PDT|CST|CDT|IST|BST)\b" "$TARGET_DIR"/features/*.feature >/dev/null 2>&1; then
  echo "❌ FAILED"
  echo "    ERROR: Ambiguous timezone abbreviation detected"
  rg -n "\b(EST|EDT|PST|PDT|CST|CDT|IST|BST)\b" "$TARGET_DIR"/features/*.feature 2>/dev/null || true
  ERRORS=$((ERRORS+1))
else
  echo "✅ PASS"
fi

# Check 5: Redirect stub integrity
echo -n "  [CHECK 5] Redirect stub integrity... "
STUB_ERRORS=0
if [[ -f "$STUB_PATH" ]]; then
  # No executable scenarios in stub
  if rg -n "^\s*Scenario( Outline)?:" "$STUB_PATH" >/dev/null 2>&1; then
    echo "❌ FAILED"
    echo "    ERROR: Redirect stub contains scenarios: $STUB_PATH"
    rg -n "^\s*Scenario( Outline)?:" "$STUB_PATH" 2>/dev/null || true
    STUB_ERRORS=$((STUB_ERRORS+1))
  fi
  # Must be tagged as redirect
  if ! rg -n "^@.*\\bredirect\\b" "$STUB_PATH" >/dev/null 2>&1; then
    echo "❌ FAILED"
    echo "    ERROR: Redirect stub missing @redirect tag: $STUB_PATH"
    STUB_ERRORS=$((STUB_ERRORS+1))
  fi
  # Disallow project-specific initialization in stub background
  if rg -n "Knowledge Engine is initialized" "$STUB_PATH" >/dev/null 2>&1; then
    echo "❌ FAILED"
    echo "    ERROR: Redirect stub contains project-specific initialization: $STUB_PATH"
    rg -n "Knowledge Engine is initialized" "$STUB_PATH" 2>/dev/null || true
    STUB_ERRORS=$((STUB_ERRORS+1))
  fi
  if [[ $STUB_ERRORS -gt 0 ]]; then
    ERRORS=$((ERRORS+STUB_ERRORS))
  else
    echo "✅ PASS"
  fi
else
  echo "⚠️  WARNING: Redirect stub not created"
fi

# =============================================================================
# Results
# =============================================================================
echo ""
if [[ $ERRORS -gt 0 ]]; then
  echo "❌ Validation completed with $ERRORS error(s)."
  echo "   Please fix the issues above before committing."
  exit 1
fi

echo "✅ All checks passed!"
echo ""
echo "Next steps:"
echo "  1. Customize companion files (README.md, TRACEABILITY.md, GLOSSARY.md)"
echo "  2. Author feature files in features/ directory"
echo "  3. Replace placeholders with actual EARS requirements"
echo "  4. Add threshold keys to PRD registry"
echo "  5. Run full validation: ./scripts/validate_bdd_suite.py --root $DOCS_DIR"
echo ""
