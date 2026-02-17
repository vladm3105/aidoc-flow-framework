#!/bin/bash
# Validate Framework Configuration
# Checks that all placeholder variables have been replaced
#
# Usage: ./validate_configuration.sh [--fix]
#
# Options:
#   --fix    Show sed commands to fix common placeholders

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo "=== Framework Configuration Validator ==="
echo "Project root: ${PROJECT_ROOT}"
echo ""

# ============================================
# STEP 1: Find unreplaced placeholders
# ============================================
echo "Step 1: Scanning for unreplaced placeholders..."

# Find all placeholders in the format {PLACEHOLDER_NAME}
PLACEHOLDERS=$(grep -roh '\{[A-Z][A-Z0-9_]*\}' "${PROJECT_ROOT}" \
    --include="*.md" \
    --include="*.yml" \
    --include="*.yaml" \
    --include="*.sh" \
    --include="*.json" \
    --include="*.py" \
    2>/dev/null | sort -u | grep -v "^{}$" || true)

if [ -z "${PLACEHOLDERS}" ]; then
    echo -e "${GREEN}   No unreplaced placeholders found!${NC}"
    echo ""
    echo "Configuration is complete."
    exit 0
fi

# Count unique placeholders
PLACEHOLDER_COUNT=$(echo "${PLACEHOLDERS}" | wc -l)
echo -e "${YELLOW}  Found ${PLACEHOLDER_COUNT} unique unreplaced placeholders${NC}"
echo ""

# ============================================
# STEP 2: Categorize placeholders
# ============================================
echo "Step 2: Categorizing placeholders..."
echo ""

# Core placeholders
echo "=== CORE (Required) ==="
echo "${PLACEHOLDERS}" | grep -E "PROJECT_PREFIX|PROJECT_NAME|REPO_NAME|GITHUB_ORG|GITHUB_HOST|PROJECT_BOARD" || echo "  (none remaining)"
echo ""

# Team placeholders
echo "=== TEAM ==="
echo "${PLACEHOLDERS}" | grep -E "CODEOWNER|TEAM_SLUG" || echo "  (none remaining)"
echo ""

# Cloud - GCP
echo "=== CLOUD - GCP ==="
echo "${PLACEHOLDERS}" | grep -E "GCP_|WIF_" || echo "  (none remaining)"
echo ""

# Cloud - AWS
echo "=== CLOUD - AWS ==="
echo "${PLACEHOLDERS}" | grep -E "AWS_|ECR_" || echo "  (none remaining)"
echo ""

# Cloud - Azure
echo "=== CLOUD - Azure ==="
echo "${PLACEHOLDERS}" | grep -E "AZURE_|ACR_" || echo "  (none remaining)"
echo ""

# AI/Configuration
echo "=== AI & CONFIGURATION ==="
echo "${PLACEHOLDERS}" | grep -E "AI_|TIMEZONE|BOARD_OPTION|SERVICE_NAME|PHASE_COUNT" || echo "  (none remaining)"
echo ""

# Other
echo "=== OTHER ==="
echo "${PLACEHOLDERS}" | grep -vE "PROJECT_|REPO_|GITHUB_|CODEOWNER|TEAM_|GCP_|WIF_|AWS_|ECR_|AZURE_|ACR_|AI_|TIMEZONE|BOARD_|SERVICE_|PHASE_" || echo "  (none remaining)"
echo ""

# ============================================
# STEP 3: Show files with most placeholders
# ============================================
echo "Step 3: Files with most unreplaced placeholders..."
echo ""

grep -rc '\{[A-Z][A-Z0-9_]*\}' "${PROJECT_ROOT}" \
    --include="*.md" \
    --include="*.yml" \
    --include="*.yaml" \
    --include="*.sh" \
    --include="*.json" \
    2>/dev/null | grep -v ":0$" | sort -t: -k2 -rn | head -10 || true

echo ""

# ============================================
# STEP 4: Generate fix commands (optional)
# ============================================
if [[ "${1:-}" == "--fix" ]]; then
    echo "=== Fix Commands ==="
    echo ""
    echo "Run these commands to replace placeholders (customize values first):"
    echo ""

    # Core replacements
    echo "# Core"
    echo "find ${PROJECT_ROOT} -type f \\( -name '*.md' -o -name '*.yml' -o -name '*.sh' -o -name '*.json' \\) -exec sed -i 's|{PROJECT_PREFIX}|YOUR_PREFIX|g' {} \\;"
    echo "find ${PROJECT_ROOT} -type f \\( -name '*.md' -o -name '*.yml' -o -name '*.sh' -o -name '*.json' \\) -exec sed -i 's|{PROJECT_NAME}|Your Project Name|g' {} \\;"
    echo "find ${PROJECT_ROOT} -type f \\( -name '*.md' -o -name '*.yml' -o -name '*.sh' -o -name '*.json' \\) -exec sed -i 's|{REPO_NAME}|your-repo-name|g' {} \\;"
    echo "find ${PROJECT_ROOT} -type f \\( -name '*.md' -o -name '*.yml' -o -name '*.sh' -o -name '*.json' \\) -exec sed -i 's|{GITHUB_ORG}|your-org|g' {} \\;"
    echo "find ${PROJECT_ROOT} -type f \\( -name '*.md' -o -name '*.yml' -o -name '*.sh' -o -name '*.json' \\) -exec sed -i 's|{GITHUB_HOST}|github.com|g' {} \\;"
    echo ""
fi

# ============================================
# SUMMARY
# ============================================
echo "=== Summary ==="
echo ""
echo -e "Total unreplaced placeholders: ${YELLOW}${PLACEHOLDER_COUNT}${NC}"
echo ""
echo "Next steps:"
echo "  1. Review CONFIG.md for placeholder documentation"
echo "  2. Replace placeholders using find/sed commands"
echo "  3. Re-run this script to verify"
echo ""
echo "Run with --fix to see replacement commands:"
echo "  ./validate_configuration.sh --fix"
