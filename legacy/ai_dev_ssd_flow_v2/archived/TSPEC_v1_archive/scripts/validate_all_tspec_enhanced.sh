#!/bin/bash
# validate_all_tspec.sh (Enhanced v2.0)
# Batch validation for all TSPEC documents with enhanced features
# Usage: ./validate_all_tspec.sh [options] <docs_path>
#
# Options:
#   --verbose          Show detailed validation output
#   --quality-gates    Run quality gate validation
#   --json             Output results in JSON format
#   --color            Use color-coded output (default: auto)
#   --no-color         Disable color output
#   --help             Show this help message

set -euo pipefail

# Default values
DOCS_PATH=""
VERBOSE=false
QUALITY_GATES=false
JSON_OUTPUT=false
USE_COLOR=auto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Color codes (will be set based on USE_COLOR)
RED=""
GREEN=""
YELLOW=""
BLUE=""
RESET=""

# Function to show help
show_help() {
    echo "Usage: $0 [options] <docs_path>"
    echo ""
    echo "Options:"
    echo "  --verbose          Show detailed validation output"
    echo "  --quality-gates    Run quality gate validation"
    echo "  --json             Output results in JSON format"
    echo "  --color            Use color-coded output (default: auto)"
    echo "  --no-color         Disable color output"
    echo "  --help             Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 --verbose --quality-gates ucx_flow_v3/10_TSPEC"
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose)
            VERBOSE=true
            shift
            ;;
        --quality-gates)
            QUALITY_GATES=true
            shift
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --color)
            USE_COLOR=yes
            shift
            ;;
        --no-color)
            USE_COLOR=no
            shift
            ;;
        --help)
            show_help
            ;;
        -*)
            echo "Unknown option: $1"
            show_help
            ;;
        *)
            DOCS_PATH="$1"
            shift
            ;;
    esac
done

# Set default docs path if not provided
DOCS_PATH="${DOCS_PATH:-docs/10_TSPEC}"

# Determine if we should use color
if [ "$USE_COLOR" = "auto" ]; then
    if [ -t 1 ]; then
        USE_COLOR=yes
    else
        USE_COLOR=no
    fi
fi

# Set color codes if enabled
if [ "$USE_COLOR" = "yes" ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    RESET='\033[0m'
fi

# Initialize JSON output structure
declare -a json_results=()

# Track results
declare -a failed_files=()
declare -A type_stats=()
total_files=0
passed_files=0

# Initialize type stats
for type in UTEST ITEST STEST FTEST PTEST SECTEST; do
    type_stats["${type}_total"]=0
    type_stats["${type}_passed"]=0
done

# Function to print colored message
print_color() {
    local color="$1"
    local message="$2"
    if [ "$JSON_OUTPUT" = false ]; then
        echo -e "${color}${message}${RESET}"
    fi
}

# Function to validate files
validate_type() {
    local type="$1"
    local validator="$2"

    if [ "$JSON_OUTPUT" = false ]; then
        echo ""
        print_color "$BLUE" "=== $type Validation ==="
    fi

    # Find files excluding templates, reserved IDs, and report files
    local files=$(find "$DOCS_PATH/$type" -type f -name "${type}-[0-9]*_*.md" \
        ! -name "${type}-00_*" \
        ! -name "*TEMPLATE*" \
        ! -name "*FIX_PLAN*" \
        ! -name "*.A_audit_report*" \
        ! -name "*.R_review_report*" \
        ! -name "*.F_fix_report*" \
        ! -name "*.V_validation_report*" \
        2>/dev/null || true)

    if [ -z "$files" ]; then
        if [ "$JSON_OUTPUT" = false ] && [ "$VERBOSE" = true ]; then
            echo "No $type files found"
        fi
        return 0
    fi

    local type_total=0
    local type_passed=0

    while IFS= read -r file; do
        [ -z "$file" ] && continue

        ((total_files++)) || true
        ((type_total++)) || true
        type_stats["${type}_total"]=$type_total

        # Build validator command
        local cmd="python3 $SCRIPT_DIR/$validator $file"
        if [ "$QUALITY_GATES" = true ]; then
            cmd="$cmd --quality-gates"
        fi

        # Run validation
        local result_code=0
        local output=""

        if [ "$VERBOSE" = true ]; then
            if $cmd; then
                result_code=0
            else
                result_code=$?
            fi
        else
            if output=$($cmd 2>&1); then
                result_code=0
            else
                result_code=$?
            fi
        fi

        # Track results
        if [ $result_code -eq 0 ]; then
            ((passed_files++)) || true
            ((type_passed++)) || true
            type_stats["${type}_passed"]=$type_passed

            if [ "$JSON_OUTPUT" = false ]; then
                if [ "$VERBOSE" = true ]; then
                    print_color "$GREEN" "✓ PASS $(basename "$file")"
                else
                    print_color "$GREEN" "✓ $(basename "$file")"
                fi
            fi
        else
            failed_files+=("$file")

            if [ "$JSON_OUTPUT" = false ]; then
                if [ "$VERBOSE" = true ]; then
                    print_color "$RED" "✗ FAIL $(basename "$file")"
                    if [ -n "$output" ]; then
                        echo "$output" | sed 's/^/  /'
                    fi
                else
                    print_color "$RED" "✗ $(basename "$file")"
                fi
            fi
        fi

        # Add to JSON results
        if [ "$JSON_OUTPUT" = true ]; then
            local status="pass"
            [ $result_code -ne 0 ] && status="fail"
            json_results+=("{\"type\":\"$type\",\"file\":\"$file\",\"status\":\"$status\"}")
        fi

    done <<< "$files"

    if [ "$JSON_OUTPUT" = false ] && [ "$VERBOSE" = true ]; then
        echo ""
        print_color "$BLUE" "$type: $type_passed/$type_total passed"
    fi
}

# Print header
if [ "$JSON_OUTPUT" = false ]; then
    echo "========================================="
    echo "TSPEC Batch Validation (Enhanced v2.0)"
    echo "========================================="
    echo "Path: $DOCS_PATH"
    echo "Date: $(date)"
    echo "Options:"
    [ "$VERBOSE" = true ] && echo "  - Verbose output enabled"
    [ "$QUALITY_GATES" = true ] && echo "  - Quality gates enabled"
    [ "$USE_COLOR" = "yes" ] && echo "  - Color output enabled"
    echo "========================================="
fi

# Validate each type
validate_type "UTEST" "validate_utest.py"
validate_type "ITEST" "validate_itest.py"
validate_type "STEST" "validate_stest.py"
validate_type "FTEST" "validate_ftest.py"
validate_type "PTEST" "validate_ptest.py"
validate_type "SECTEST" "validate_sectest.py"

# Output results
if [ "$JSON_OUTPUT" = true ]; then
    # JSON output
    echo "{"
    echo "  \"summary\": {"
    echo "    \"total_files\": $total_files,"
    echo "    \"passed\": $passed_files,"
    echo "    \"failed\": $((total_files - passed_files))"
    echo "  },"
    echo "  \"by_type\": {"
    for type in UTEST ITEST STEST FTEST PTEST SECTEST; do
        echo "    \"$type\": {"
        echo "      \"total\": ${type_stats[${type}_total]},"
        echo "      \"passed\": ${type_stats[${type}_passed]}"
        if [ "$type" = "SECTEST" ]; then
            echo "    }"
        else
            echo "    },"
        fi
    done
    echo "  },"
    echo "  \"results\": ["
    first=true
    for result in "${json_results[@]}"; do
        if [ "$first" = true ]; then
            echo "    $result"
            first=false
        else
            echo "    ,$result"
        fi
    done
    echo "  ]"
    echo "}"
else
    # Human-readable output
    echo ""
    echo "========================================="
    echo "Validation Summary"
    echo "========================================="

    # Per-type breakdown
    for type in UTEST ITEST STEST FTEST PTEST SECTEST; do
        total=${type_stats[${type}_total]}
        passed=${type_stats[${type}_passed]}
        if [ $total -gt 0 ]; then
            failed=$((total - passed))
            printf "%-8s %3d/%3d passed" "$type:" "$passed" "$total"
            if [ $failed -gt 0 ]; then
                print_color "$RED" " ($failed failed)"
            else
                print_color "$GREEN" " ✓"
            fi
        fi
    done

    echo ""
    echo "-----------------------------------------"
    printf "%-8s %3d/%3d passed\n" "Total:" "$passed_files" "$total_files"
    echo "========================================="

    if [ ${#failed_files[@]} -gt 0 ]; then
        echo ""
        print_color "$YELLOW" "Failed files:"
        for file in "${failed_files[@]}"; do
            echo "  - $file"
        done
        echo ""
        print_color "$RED" "Status: [FAIL] VALIDATION FAILED"
        exit 1
    else
        echo ""
        if [ $total_files -gt 0 ]; then
            print_color "$GREEN" "Status: [PASS] ALL VALIDATIONS PASSED ✓"
        else
            print_color "$YELLOW" "Status: [SKIP] NO FILES TO VALIDATE"
        fi
        exit 0
    fi
fi
