#!/bin/bash
#
# lint_file_sizes.sh - Check documentation files against size limits
#
# TODO: This script is a placeholder. Implement the following functionality:
#
# 1. File Size Checking:
#    - Target: 800 lines per file
#    - Maximum: 1200 lines per file (absolute limit)
#    - Check all .md files in documentation directories
#
# 2. Token Estimation:
#    - Estimate tokens from file size (tokens ≈ (KB × 1024) ÷ 4)
#    - Warn if files exceed tool token limits:
#      - Claude Code: 50,000 tokens standard, 100,000 max
#      - GitHub Copilot: 30KB
#
# 3. Output:
#    - List files exceeding target (800 lines)
#    - Flag files exceeding maximum (1200 lines) as errors
#    - Suggest splitting for large files
#
# Usage:
#    ./scripts/lint_file_sizes.sh [directory]
#    ./scripts/lint_file_sizes.sh ai_dev_flow/
#    ./scripts/lint_file_sizes.sh docs/
#
# See Also:
#    - DOCUMENT_SPLITTING_RULES.md: Guidelines for splitting large documents
#    - AI_TOOL_OPTIMIZATION_GUIDE.md: Token limits by tool
#
# Author: AI-Driven SDD Framework
# Version: 0.1.0 (placeholder)

set -e

# Configuration
TARGET_LINES=800
MAX_LINES=1200
TARGET_KB=50    # ~12,500 tokens
MAX_KB=100      # ~25,000 tokens

# Default directory
SEARCH_DIR="${1:-.}"

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "File Size Lint - Checking documentation files"
echo "=============================================="
echo "Target: ${TARGET_LINES} lines / ${TARGET_KB}KB"
echo "Maximum: ${MAX_LINES} lines / ${MAX_KB}KB"
echo "Directory: ${SEARCH_DIR}"
echo ""

warnings=0
errors=0

# Find all markdown files
while IFS= read -r -d '' file; do
    # Skip index files (typically small)
    if [[ "$file" == *"_index.md" ]] || [[ "$file" == *"-00_"* ]]; then
        continue
    fi

    # Get line count
    lines=$(wc -l < "$file")

    # Get file size in KB
    size_bytes=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
    size_kb=$((size_bytes / 1024))

    # Estimate tokens
    estimated_tokens=$((size_bytes / 4))

    # Check against limits
    if [ "$lines" -gt "$MAX_LINES" ] || [ "$size_kb" -gt "$MAX_KB" ]; then
        echo -e "${RED}ERROR${NC}: $file"
        echo "  Lines: $lines (max: $MAX_LINES)"
        echo "  Size: ${size_kb}KB (max: ${MAX_KB}KB)"
        echo "  Est. tokens: ~$estimated_tokens"
        echo "  Action: MUST split this file. See DOCUMENT_SPLITTING_RULES.md"
        echo ""
        ((errors++))
    elif [ "$lines" -gt "$TARGET_LINES" ] || [ "$size_kb" -gt "$TARGET_KB" ]; then
        echo -e "${YELLOW}WARNING${NC}: $file"
        echo "  Lines: $lines (target: $TARGET_LINES)"
        echo "  Size: ${size_kb}KB (target: ${TARGET_KB}KB)"
        echo "  Est. tokens: ~$estimated_tokens"
        echo "  Action: Consider splitting this file"
        echo ""
        ((warnings++))
    fi
done < <(find "$SEARCH_DIR" -name "*.md" -type f -print0 2>/dev/null)

# Summary
echo "=============================================="
echo "Summary:"
echo -e "  ${RED}Errors${NC}: $errors (files exceeding maximum)"
echo -e "  ${YELLOW}Warnings${NC}: $warnings (files exceeding target)"

if [ "$errors" -gt 0 ]; then
    echo ""
    echo -e "${RED}FAILED${NC}: $errors file(s) exceed maximum limits"
    exit 1
elif [ "$warnings" -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}PASSED with warnings${NC}: Consider splitting large files"
    exit 0
else
    echo ""
    echo -e "${GREEN}PASSED${NC}: All files within size limits"
    exit 0
fi
