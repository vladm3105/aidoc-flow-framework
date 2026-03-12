#!/usr/bin/env bash
# =============================================================================
# run_ucrem.sh — UCRem (Unified Context Remediation) Runner
# =============================================================================
# Framework-level script for generating fix proposals from UCR review reports.
# Now includes dynamic skill loading for enhanced fixer persona knowledge.
#
# Usage:
#   ./run_ucrem.sh <ucr_report> <document_path> [output_file]
#
# Examples:
#   ./run_ucrem.sh docs/01_BRD/BRD-01/BRD_UCR_REVIEW.md docs/01_BRD/BRD-01
#   ./run_ucrem.sh prd_review.md docs/02_PRD/PRD-01.md
#
# Arguments:
#   ucr_report    - Path to the UCR review report
#   document_path - Path to the original document(s)
#   output_file   - (Optional) Custom output path for UCRem report
#
# Environment:
#   UCREM_PROMPT_DIR  - Directory containing UCRem prompts (default: script directory)
#   UCREM_MODEL       - Claude model to use (default: opus)
#   UCREM_LOAD_SKILLS - Load skill files into prompt (default: true)
#
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# =============================================================================
# Configuration
# =============================================================================
UCREM_PROMPT_DIR="${UCREM_PROMPT_DIR:-$SCRIPT_DIR}"
UCREM_MODEL="${UCREM_MODEL:-opus}"
UCREM_LOAD_SKILLS="${UCREM_LOAD_SKILLS:-true}"
SKILL_DIR="$SCRIPT_DIR/../skills"

# =============================================================================
# UCRem Fixer Skills (same for all layers)
# =============================================================================
# The 6 fixer personas and their corresponding skill files
# Domain Fixers (loaded adaptively via Python API): architect, auditor, qa_lead, integration_lead
# Mandatory Fixers (always loaded): devils_advocate, chairperson
# Note: For adaptive loading based on UCR findings, use `ucx remediate` command instead
FIXER_SKILLS="architect auditor qa_lead integration_lead devils_advocate chairperson"

# =============================================================================
# Parse arguments
# =============================================================================
UCR_REPORT="${1:-}"
DOC_PATH="${2:-}"
OUTPUT_FILE="${3:-}"

if [[ -z "$UCR_REPORT" || -z "$DOC_PATH" ]]; then
    echo "Usage: ./run_ucrem.sh <ucr_report> <document_path> [output_file]"
    echo ""
    echo "Examples:"
    echo "  ./run_ucrem.sh docs/01_BRD/BRD-01/BRD_UCR_REVIEW.md docs/01_BRD/BRD-01"
    echo "  ./run_ucrem.sh prd_review.md docs/02_PRD/*.md"
    echo ""
    echo "Environment variables:"
    echo "  UCREM_LOAD_SKILLS=false  # Disable skill loading (smaller prompt)"
    echo ""
    exit 1
fi

# Validate inputs exist
if [[ ! -f "$UCR_REPORT" ]]; then
    echo "Error: UCR report not found: $UCR_REPORT"
    exit 1
fi

if [[ ! -e "$DOC_PATH" ]]; then
    echo "Error: Document path not found: $DOC_PATH"
    exit 1
fi

# =============================================================================
# Determine document type from UCR report name
# =============================================================================
REPORT_NAME=$(basename "$UCR_REPORT")

if [[ "$REPORT_NAME" =~ BRD ]]; then
    DOC_TYPE="brd"
elif [[ "$REPORT_NAME" =~ PRD ]]; then
    DOC_TYPE="prd"
elif [[ "$REPORT_NAME" =~ EARS ]]; then
    DOC_TYPE="ears"
elif [[ "$REPORT_NAME" =~ BDD ]]; then
    DOC_TYPE="bdd"
elif [[ "$REPORT_NAME" =~ ADR ]]; then
    DOC_TYPE="adr"
elif [[ "$REPORT_NAME" =~ SYS ]]; then
    DOC_TYPE="sys"
elif [[ "$REPORT_NAME" =~ REQ ]]; then
    DOC_TYPE="req"
elif [[ "$REPORT_NAME" =~ CTR ]]; then
    DOC_TYPE="ctr"
elif [[ "$REPORT_NAME" =~ SPEC ]]; then
    DOC_TYPE="spec"
elif [[ "$REPORT_NAME" =~ TSPEC ]]; then
    DOC_TYPE="tspec"
else
    DOC_TYPE="brd"
    echo "Warning: Could not determine document type from '$REPORT_NAME', defaulting to BRD"
fi

# =============================================================================
# Select UCRem prompt
# =============================================================================
# Check for project-specific prompt first, then fall back to framework prompt
PROJECT_PROMPT="UCRem_PROMPT_${DOC_TYPE^^}_PROJECT.md"
BEELOCAL_PROMPT="UCRem_PROMPT_${DOC_TYPE^^}_BEELOCAL.md"
FRAMEWORK_PROMPT="UCRem_PROMPT_${DOC_TYPE^^}.md"

if [[ -f "$UCREM_PROMPT_DIR/$PROJECT_PROMPT" ]]; then
    PROMPT_FILE="$UCREM_PROMPT_DIR/$PROJECT_PROMPT"
    echo "Using project-specific prompt: $PROJECT_PROMPT"
elif [[ -f "$UCREM_PROMPT_DIR/$BEELOCAL_PROMPT" ]]; then
    PROMPT_FILE="$UCREM_PROMPT_DIR/$BEELOCAL_PROMPT"
    echo "Using project-specific prompt: $BEELOCAL_PROMPT"
elif [[ -f "$UCREM_PROMPT_DIR/$FRAMEWORK_PROMPT" ]]; then
    PROMPT_FILE="$UCREM_PROMPT_DIR/$FRAMEWORK_PROMPT"
else
    echo "Error: No UCRem prompt found for document type '$DOC_TYPE'"
    echo "Searched for:"
    echo "  - $UCREM_PROMPT_DIR/$PROJECT_PROMPT"
    echo "  - $UCREM_PROMPT_DIR/$BEELOCAL_PROMPT"
    echo "  - $UCREM_PROMPT_DIR/$FRAMEWORK_PROMPT"
    exit 1
fi

# =============================================================================
# Set default output path
# =============================================================================
if [[ -z "$OUTPUT_FILE" ]]; then
    REPORT_DIR=$(dirname "$UCR_REPORT")
    OUTPUT_FILE="$REPORT_DIR/${DOC_TYPE^^}_UCRem_REPORT.md"
fi

# =============================================================================
# Build combined input with skills
# =============================================================================
TMP_INPUT=$(mktemp /tmp/ucrem_input_XXXXXX.md)
trap "rm -f $TMP_INPUT" EXIT

echo "Building UCRem input..."
echo "  Prompt: $PROMPT_FILE"
echo "  UCR Report: $UCR_REPORT"
echo "  Document: $DOC_PATH"

# Start with prompt
cat "$PROMPT_FILE" > "$TMP_INPUT"

# =============================================================================
# Load Fixer Skills (if enabled)
# =============================================================================
if [[ "$UCREM_LOAD_SKILLS" == "true" && -d "$SKILL_DIR" ]]; then
    echo "  Skills: $FIXER_SKILLS"

    echo "" >> "$TMP_INPUT"
    echo "---" >> "$TMP_INPUT"
    echo "" >> "$TMP_INPUT"
    echo "## FIXER PERSONA SKILL DEFINITIONS" >> "$TMP_INPUT"
    echo "" >> "$TMP_INPUT"
    echo "Each fixer persona uses the following domain knowledge when validating fixes:" >> "$TMP_INPUT"
    echo "" >> "$TMP_INPUT"

    for skill in $FIXER_SKILLS; do
        SKILL_FILE="$SKILL_DIR/${skill}.md"
        if [[ -f "$SKILL_FILE" ]]; then
            # Map skill to fixer persona name
            case $skill in
                architect) FIXER_NAME="Architect Fixer" ;;
                auditor) FIXER_NAME="Auditor Fixer" ;;
                qa_lead) FIXER_NAME="QA Fixer" ;;
                integration_expert) FIXER_NAME="Integration Fixer" ;;
                devils_advocate) FIXER_NAME="Devil's Advocate" ;;
                *) FIXER_NAME="$skill" ;;
            esac

            echo "### Skill: $FIXER_NAME" >> "$TMP_INPUT"
            echo "" >> "$TMP_INPUT"
            cat "$SKILL_FILE" >> "$TMP_INPUT"
            echo "" >> "$TMP_INPUT"
        fi
    done
else
    echo "  Skills: disabled (UCREM_LOAD_SKILLS=$UCREM_LOAD_SKILLS)"
fi

# Add separator and UCR report
echo "" >> "$TMP_INPUT"
echo "---" >> "$TMP_INPUT"
echo "" >> "$TMP_INPUT"
echo "# UCR REVIEW REPORT" >> "$TMP_INPUT"
echo "" >> "$TMP_INPUT"
cat "$UCR_REPORT" >> "$TMP_INPUT"

# Add separator and document content
echo "" >> "$TMP_INPUT"
echo "---" >> "$TMP_INPUT"
echo "" >> "$TMP_INPUT"
echo "# ORIGINAL DOCUMENT CONTENT" >> "$TMP_INPUT"
echo "" >> "$TMP_INPUT"

# Add document content
if [[ -d "$DOC_PATH" ]]; then
    # Directory: concatenate all markdown files (exclude review reports)
    for f in "$DOC_PATH"/*.md; do
        if [[ -f "$f" && "$(basename "$f")" != *"REVIEW"* && "$(basename "$f")" != *"REPORT"* ]]; then
            echo "## File: $(basename "$f")" >> "$TMP_INPUT"
            echo "" >> "$TMP_INPUT"
            cat "$f" >> "$TMP_INPUT"
            echo "" >> "$TMP_INPUT"
        fi
    done
else
    # Single file or glob pattern
    for f in $DOC_PATH; do
        if [[ -f "$f" ]]; then
            echo "## File: $(basename "$f")" >> "$TMP_INPUT"
            echo "" >> "$TMP_INPUT"
            cat "$f" >> "$TMP_INPUT"
            echo "" >> "$TMP_INPUT"
        fi
    done
fi

# =============================================================================
# Run UCRem
# =============================================================================
INPUT_SIZE=$(wc -c < "$TMP_INPUT")
INPUT_LINES=$(wc -l < "$TMP_INPUT")

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  UCRem (Unified Context Remediation)"
echo "════════════════════════════════════════════════════════════"
echo "  Document Type: ${DOC_TYPE^^}"
echo "  Input Size:    $INPUT_SIZE bytes ($INPUT_LINES lines)"
echo "  Output:        $OUTPUT_FILE"
echo "  Model:         $UCREM_MODEL"
echo "  Skills:        $([[ "$UCREM_LOAD_SKILLS" == "true" ]] && echo "enabled" || echo "disabled")"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Running UCRem remediation planning..."
echo ""

# Run with Claude CLI
if command -v claude &> /dev/null; then
    claude -p --model "$UCREM_MODEL" < "$TMP_INPUT" > "$OUTPUT_FILE"
else
    echo "Error: 'claude' CLI not found."
    echo ""
    echo "Manual execution:"
    echo "  cat '$TMP_INPUT' | claude -p --model $UCREM_MODEL > '$OUTPUT_FILE'"
    exit 1
fi

# =============================================================================
# Summary
# =============================================================================
OUTPUT_SIZE=$(wc -c < "$OUTPUT_FILE")

# Extract fix counts if possible
AUTO_SAFE=$(grep -c "confidence: auto-safe" "$OUTPUT_FILE" 2>/dev/null || echo "0")
AUTO_ASSISTED=$(grep -c "confidence: auto-assisted" "$OUTPUT_FILE" 2>/dev/null || echo "0")
MANUAL_REQ=$(grep -c "confidence: manual-required" "$OUTPUT_FILE" 2>/dev/null || echo "0")

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  UCRem Complete"
echo "════════════════════════════════════════════════════════════"
echo "  Output: $OUTPUT_FILE"
echo "  Size:   $OUTPUT_SIZE bytes"
echo "  Fixes:  auto-safe=$AUTO_SAFE, auto-assisted=$AUTO_ASSISTED, manual=$MANUAL_REQ"
echo ""
echo "  Next steps:"
echo "  1. Review the UCRem report"
echo "  2. Apply auto-safe fixes (Phase 1)"
echo "  3. Apply auto-assisted fixes with [TODO] completion (Phase 2)"
echo "  4. Create tasks for manual-required fixes (Phase 3)"
echo "  5. Re-run UCR to verify improvements"
echo "════════════════════════════════════════════════════════════"
