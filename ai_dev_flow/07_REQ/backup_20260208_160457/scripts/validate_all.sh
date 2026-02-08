#!/bin/bash
# REQ Validation Helper - Run all validators on a file or directory

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

Run all REQ validation tools on a file or directory.

OPTIONS:
    -h, --help              Show this help message
    -f, --file <path>       Validate single file
    -d, --directory <path>  Validate directory (corpus)
    --min-score <int>       Minimum SPEC-ready score (default: 90)
    --skip-quality          Skip quality gate validator
    --skip-spec             Skip SPEC-readiness validator
    --skip-template         Skip template compliance checker
    --skip-ids              Skip requirement IDs validator
    --test-gate05           Run GATE-05 isolation detection test (creates isolated corpus)

EXAMPLES:
    # Single file (all validators)
    $0 --file /path/to/REQ-01.01_file.md

    # Directory (all validators)
    $0 --directory /path/to/REQ-01_folder

    # Custom SPEC-ready threshold
    $0 --directory /path/to/REQ-01_folder --min-score 85

    # Skip template check (for directory validation)
    $0 --directory /path/to/REQ-01_folder --skip-template

    # Run GATE-05 isolation detection test
    $0 --test-gate05

EOF
    exit 0
}

# Parse arguments
TARGET=""
MODE=""
MIN_SCORE=90
SKIP_QUALITY=false
SKIP_SPEC=false
SKIP_TEMPLATE=false
SKIP_IDS=false
TEST_GATE05=false

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
        --skip-spec)
            SKIP_SPEC=true
            shift
            ;;
        --skip-template)
            SKIP_TEMPLATE=true
            shift
            ;;
        --skip-ids)
            SKIP_IDS=true
            shift
            ;;
        --test-gate05)
            TEST_GATE05=true
            shift
            ;;
        *)
            if [[ -z "$TARGET" ]]; then
                TARGET="$1"
                # Auto-detect mode
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
if [[ -z "$TARGET" ]] && [[ "$TEST_GATE05" == false ]]; then
    echo -e "${RED}Error: No file or directory specified${NC}" >&2
    usage
fi

if [[ -n "$TARGET" ]] && [[ ! -e "$TARGET" ]]; then
    echo -e "${RED}Error: Path does not exist: $TARGET${NC}" >&2
    exit 1
fi

# Convert to absolute path (if target specified)
if [[ -n "$TARGET" ]]; then
    TARGET="$(cd "$(dirname "$TARGET")" && pwd)/$(basename "$TARGET")"
fi

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              REQ VALIDATION SUITE                                ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Handle special test mode
if [[ "$TEST_GATE05" == true ]]; then
    echo -e "${YELLOW}▶ GATE-05 Isolation Detection Test${NC}"
    echo ""
    if bash "$SCRIPT_DIR/test_gate05_isolation.sh"; then
        echo ""
        echo -e "${GREEN}✓ GATE-05 Test PASSED${NC}"
        exit 0
    else
        echo ""
        echo -e "${RED}✗ GATE-05 Test FAILED${NC}"
        exit 1
    fi
fi

echo -e "Mode:   ${YELLOW}${MODE}${NC}"
echo -e "Target: ${YELLOW}${TARGET}${NC}"
echo ""

# Initialize counters
TOTAL_PASSED=0
TOTAL_FAILED=0
TOTAL_WARNINGS=0

# Helper function to run validator
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

# 1. Quality Gate Validator (directory only)
if [[ "$MODE" == "directory" ]] && [[ "$SKIP_QUALITY" == false ]]; then
    run_validator "Quality Gate Validator (16 gates)" \
        "\"$SCRIPT_DIR/validate_req_quality_score.sh\" \"$TARGET\""
    echo ""
fi

# 2. SPEC-Readiness Validator
if [[ "$SKIP_SPEC" == false ]]; then
    if [[ "$MODE" == "file" ]]; then
        run_validator "SPEC-Readiness Validator" \
            "python3 \"$SCRIPT_DIR/validate_req_spec_readiness.py\" --req-file \"$TARGET\" --min-score $MIN_SCORE"
    else
        run_validator "SPEC-Readiness Validator" \
            "python3 \"$SCRIPT_DIR/validate_req_spec_readiness.py\" --directory \"$TARGET\" --min-score $MIN_SCORE"
    fi
    echo ""
fi

# 3. Template Compliance Checker (file only)
if [[ "$MODE" == "file" ]] && [[ "$SKIP_TEMPLATE" == false ]]; then
    run_validator "Template Compliance Checker" \
        "\"$SCRIPT_DIR/validate_req_template.sh\" \"$TARGET\""
    echo ""
fi

# 4. Requirement IDs Validator
if [[ "$SKIP_IDS" == false ]]; then
    if [[ "$MODE" == "file" ]]; then
        run_validator "Requirement IDs Validator" \
            "python3 \"$SCRIPT_DIR/validate_requirement_ids.py\" --req-file \"$TARGET\" --all-checks"
    else
        run_validator "Requirement IDs Validator" \
            "python3 \"$SCRIPT_DIR/validate_requirement_ids.py\" --directory \"$TARGET\" --all-checks"
    fi
    echo ""
fi

# Summary
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    VALIDATION SUMMARY                            ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""
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
