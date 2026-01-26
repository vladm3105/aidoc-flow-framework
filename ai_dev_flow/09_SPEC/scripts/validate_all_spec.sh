#!/bin/bash
# SPEC Validation Helper - Run all SPEC validators on a file or directory

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

usage() {
    cat << EOF
Usage: $0 [OPTIONS] <path>

Run SPEC validation tools on a file or directory.

OPTIONS:
    -h, --help              Show this help message
    -f, --file <path>       Validate single SPEC file
    -d, --directory <path>  Validate SPEC directory (corpus)
    --min-score <int>       Minimum readiness score (default: 90)
    --skip-quality          Skip quality gate validator
    --skip-readiness        Skip implementation-readiness validator
    --skip-standard         Skip schema/template validator (validate_spec.py)

EXAMPLES:
    # Single file (standard + readiness)
    $0 --file docs/09_SPEC/SPEC-01_iam.yaml

    # Directory (all validators)
    $0 --directory docs/09_SPEC --min-score 90

    # Directory without quality gates
    $0 --directory docs/09_SPEC --skip-quality
EOF
    exit 0
}

# Defaults
TARGET=""
MODE=""
MIN_SCORE=90
SKIP_QUALITY=false
SKIP_READINESS=false
SKIP_STANDARD=false

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        -f|--file)
            MODE="file"
            TARGET="$2"
            shift 2
            ;;
        -d|--directory)
            MODE="directory"
            TARGET="$2"
            shift 2
            ;;
        --min-score)
            MIN_SCORE="$2"
            shift 2
            ;;
        --skip-quality)
            SKIP_QUALITY=true
            shift
            ;;
        --skip-readiness)
            SKIP_READINESS=true
            shift
            ;;
        --skip-standard)
            SKIP_STANDARD=true
            shift
            ;;
        *)
            if [[ -z "$TARGET" ]]; then
                TARGET="$1"
                if [[ -f "$TARGET" ]]; then
                    MODE="file"
                elif [[ -d "$TARGET" ]]; then
                    MODE="directory"
                else
                    echo -e "${RED}Error: Invalid path: $TARGET${NC}" >&2
                    exit 1
                fi
            fi
            shift
            ;;
    esac
done

# Validate input
if [[ -z "$TARGET" ]]; then
    echo -e "${RED}Error: No file or directory specified${NC}" >&2
    usage
fi

if [[ ! -e "$TARGET" ]]; then
    echo -e "${RED}Error: Path does not exist: $TARGET${NC}" >&2
    exit 1
fi

# Absolute path
TARGET="$(cd "$(dirname "$TARGET")" && pwd)/$(basename "$TARGET")"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              SPEC VALIDATION SUITE                               ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"

echo -e "Mode:   ${YELLOW}${MODE}${NC}"
echo -e "Target: ${YELLOW}${TARGET}${NC}"

echo ""

TOTAL_PASSED=0
TOTAL_FAILED=0
TOTAL_WARNINGS=0

run_validator() {
    local name="$1"
    local cmd="$2"

    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}▶ ${name}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    if eval $cmd; then
        echo ""
        echo -e "${GREEN}✓ ${name} PASSED${NC}"
        ((TOTAL_PASSED++))
        return 0
    else
        local exit_code=$?
        echo ""
        if [[ $exit_code -eq 1 ]]; then
            echo -e "${YELLOW}⚠ ${name} PASSED WITH WARNINGS${NC}"
            ((TOTAL_WARNINGS++))
            return 0
        else
            echo -e "${RED}✗ ${name} FAILED${NC}"
            ((TOTAL_FAILED++))
            return $exit_code
        fi
    fi
}

# 1) Quality gates (directory only)
if [[ "$MODE" == "directory" ]] && [[ "$SKIP_QUALITY" == false ]]; then
    run_validator "Quality Gate Validator" \
        "\"$SCRIPT_DIR/validate_spec_quality_score.sh\" \"$TARGET\""
    echo ""
fi

# 2) Schema/template validator (validate_spec.py)
if [[ "$SKIP_STANDARD" == false ]]; then
    if [[ "$MODE" == "file" ]]; then
        run_validator "Schema/Template Validator" \
            "python3 \"$SCRIPT_DIR/validate_spec.py\" \"$TARGET\""
    else
        run_validator "Schema/Template Validator" \
            "python3 \"$SCRIPT_DIR/validate_spec.py\" \"$TARGET\""
    fi
    echo ""
fi

# 3) Implementation-readiness scorer
if [[ "$SKIP_READINESS" == false ]]; then
    if [[ "$MODE" == "file" ]]; then
        run_validator "Implementation Readiness" \
            "python3 \"$SCRIPT_DIR/validate_spec_implementation_readiness.py\" --spec-file \"$TARGET\" --min-score $MIN_SCORE"
    else
        run_validator "Implementation Readiness" \
            "python3 \"$SCRIPT_DIR/validate_spec_implementation_readiness.py\" --directory \"$TARGET\" --min-score $MIN_SCORE"
    fi
    echo ""
fi

# Summary
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    VALIDATION SUMMARY                            ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"

echo -e "Passed: ${GREEN}${TOTAL_PASSED}${NC}"
echo -e "Failed: ${RED}${TOTAL_FAILED}${NC}"

echo ""

if [[ $TOTAL_FAILED -eq 0 ]]; then
    echo -e "${GREEN}✓ All validation checks passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some validation checks failed${NC}"
    exit 1
fi
