#!/usr/bin/env bash
# =============================================================================
# run_ucr.sh — UCR (Unified Context Review) Runner
# =============================================================================
# Framework-level script for running UCR reviews on any document type.
# Now includes dynamic skill loading for enhanced persona knowledge.
#
# Usage:
#   ./run_ucr.sh <doc_type> <document_path> [output_file]
#
# Examples:
#   ./run_ucr.sh brd docs/01_BRD/BRD-01_platform_architecture
#   ./run_ucr.sh prd docs/02_PRD/PRD-01.md
#
# Arguments:
#   doc_type      - Document type: brd, prd, ears, bdd, adr, sys, req, ctr, spec, tspec
#   document_path - Path to document file or folder
#   output_file   - (Optional) Custom output path
#
# Environment:
#   UCR_PROMPT_DIR  - Directory containing UCR prompts (default: script directory)
#   UCR_MODEL       - Claude model to use (default: opus)
#   UCR_LOAD_SKILLS - Load skill files into prompt (default: true)
#
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# =============================================================================
# Configuration
# =============================================================================
UCR_PROMPT_DIR="${UCR_PROMPT_DIR:-$SCRIPT_DIR}"
UCR_MODEL="${UCR_MODEL:-opus}"
UCR_LOAD_SKILLS="${UCR_LOAD_SKILLS:-true}"
SKILL_DIR="$SCRIPT_DIR/../skills"

# =============================================================================
# Layer-to-Skills Mapping
# =============================================================================
# Which skills to load for each document layer
declare -A LAYER_SKILLS
LAYER_SKILLS[brd]="architect auditor tech_lead strategist devils_advocate operator integration_expert product_owner business_analyst"
LAYER_SKILLS[prd]="architect auditor tech_lead strategist devils_advocate operator integration_expert product_owner qa_lead ux_strategist"
LAYER_SKILLS[ears]="tech_lead devils_advocate integration_expert qa_lead requirements_specialist"
LAYER_SKILLS[bdd]="auditor tech_lead devils_advocate operator integration_expert qa_lead"
LAYER_SKILLS[adr]="architect auditor tech_lead strategist devils_advocate operator integration_expert"
LAYER_SKILLS[sys]="architect tech_lead devils_advocate operator integration_expert qa_lead"
LAYER_SKILLS[req]="tech_lead devils_advocate integration_expert qa_lead requirements_specialist"
LAYER_SKILLS[ctr]="architect auditor tech_lead devils_advocate integration_expert"
LAYER_SKILLS[spec]="architect tech_lead devils_advocate operator integration_expert"
LAYER_SKILLS[tspec]="tech_lead devils_advocate operator integration_expert qa_lead"

# =============================================================================
# Parse arguments
# =============================================================================
DOC_TYPE="${1:-}"
DOC_PATH="${2:-}"
OUTPUT_FILE="${3:-}"

if [[ -z "$DOC_TYPE" || -z "$DOC_PATH" ]]; then
    echo "Usage: ./run_ucr.sh <doc_type> <document_path> [output_file]"
    echo ""
    echo "Document types: brd, prd, ears, bdd, adr, sys, req, ctr, spec, tspec"
    echo ""
    echo "Examples:"
    echo "  ./run_ucr.sh brd docs/01_BRD/BRD-01_platform_architecture"
    echo "  ./run_ucr.sh prd docs/02_PRD/*.md"
    echo ""
    echo "Environment variables:"
    echo "  UCR_LOAD_SKILLS=false  # Disable skill loading (smaller prompt)"
    echo ""
    exit 1
fi

# Normalize doc type to lowercase
DOC_TYPE=$(echo "$DOC_TYPE" | tr '[:upper:]' '[:lower:]')

# =============================================================================
# Select UCR prompt
# =============================================================================
# Check for project-specific prompt first, then fall back to framework prompt
PROJECT_PROMPT="UCR_PROMPT_${DOC_TYPE^^}_PROJECT.md"
BEELOCAL_PROMPT="UCR_PROMPT_${DOC_TYPE^^}_BEELOCAL.md"
FRAMEWORK_PROMPT="UCR_PROMPT_${DOC_TYPE^^}.md"

if [[ -f "$UCR_PROMPT_DIR/$PROJECT_PROMPT" ]]; then
    PROMPT_FILE="$UCR_PROMPT_DIR/$PROJECT_PROMPT"
    echo "Using project-specific prompt: $PROJECT_PROMPT"
elif [[ -f "$UCR_PROMPT_DIR/$BEELOCAL_PROMPT" ]]; then
    PROMPT_FILE="$UCR_PROMPT_DIR/$BEELOCAL_PROMPT"
    echo "Using project-specific prompt: $BEELOCAL_PROMPT"
elif [[ -f "$UCR_PROMPT_DIR/$FRAMEWORK_PROMPT" ]]; then
    PROMPT_FILE="$UCR_PROMPT_DIR/$FRAMEWORK_PROMPT"
else
    echo "Error: No UCR prompt found for document type '$DOC_TYPE'"
    echo "Searched for:"
    echo "  - $UCR_PROMPT_DIR/$PROJECT_PROMPT"
    echo "  - $UCR_PROMPT_DIR/$BEELOCAL_PROMPT"
    echo "  - $UCR_PROMPT_DIR/$FRAMEWORK_PROMPT"
    exit 1
fi

# =============================================================================
# Validate document path
# =============================================================================
if [[ ! -e "$DOC_PATH" ]]; then
    echo "Error: Document path not found: $DOC_PATH"
    exit 1
fi

# =============================================================================
# Set default output path
# =============================================================================
if [[ -z "$OUTPUT_FILE" ]]; then
    if [[ -d "$DOC_PATH" ]]; then
        OUTPUT_FILE="$DOC_PATH/${DOC_TYPE^^}_UCR_REVIEW.md"
    else
        DIR=$(dirname "$DOC_PATH")
        OUTPUT_FILE="$DIR/${DOC_TYPE^^}_UCR_REVIEW.md"
    fi
fi

# =============================================================================
# Build combined input with skills
# =============================================================================
TMP_INPUT=$(mktemp /tmp/ucr_input_XXXXXX.md)
trap "rm -f $TMP_INPUT" EXIT

echo "Building UCR input..."
echo "  Prompt: $PROMPT_FILE"
echo "  Document: $DOC_PATH"

# Start with prompt
cat "$PROMPT_FILE" > "$TMP_INPUT"

# =============================================================================
# Load Skills (if enabled)
# =============================================================================
if [[ "$UCR_LOAD_SKILLS" == "true" && -d "$SKILL_DIR" ]]; then
    SKILLS="${LAYER_SKILLS[$DOC_TYPE]:-}"

    if [[ -n "$SKILLS" ]]; then
        echo "  Skills: $SKILLS"

        echo "" >> "$TMP_INPUT"
        echo "---" >> "$TMP_INPUT"
        echo "" >> "$TMP_INPUT"
        echo "## PERSONA SKILL DEFINITIONS" >> "$TMP_INPUT"
        echo "" >> "$TMP_INPUT"
        echo "The following domain knowledge is available to each persona:" >> "$TMP_INPUT"
        echo "" >> "$TMP_INPUT"

        for skill in $SKILLS; do
            SKILL_FILE="$SKILL_DIR/${skill}.md"
            if [[ -f "$SKILL_FILE" ]]; then
                # Convert skill name to title case for display
                SKILL_TITLE=$(echo "$skill" | sed 's/_/ /g' | sed 's/\b\(.\)/\u\1/g')
                echo "### Skill: $SKILL_TITLE" >> "$TMP_INPUT"
                echo "" >> "$TMP_INPUT"
                cat "$SKILL_FILE" >> "$TMP_INPUT"
                echo "" >> "$TMP_INPUT"
            fi
        done
    fi
else
    echo "  Skills: disabled (UCR_LOAD_SKILLS=$UCR_LOAD_SKILLS)"
fi

# Add separator
echo "" >> "$TMP_INPUT"
echo "---" >> "$TMP_INPUT"
echo "" >> "$TMP_INPUT"
echo "# DOCUMENT CONTENT" >> "$TMP_INPUT"
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
# Run UCR
# =============================================================================
INPUT_SIZE=$(wc -c < "$TMP_INPUT")
INPUT_LINES=$(wc -l < "$TMP_INPUT")

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  UCR (Unified Context Review)"
echo "════════════════════════════════════════════════════════════"
echo "  Document Type: ${DOC_TYPE^^}"
echo "  Input Size:    $INPUT_SIZE bytes ($INPUT_LINES lines)"
echo "  Output:        $OUTPUT_FILE"
echo "  Model:         $UCR_MODEL"
echo "  Skills:        $([[ "$UCR_LOAD_SKILLS" == "true" ]] && echo "enabled" || echo "disabled")"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Running UCR review..."
echo ""

# Run with Claude CLI
if command -v claude &> /dev/null; then
    claude -p --model "$UCR_MODEL" < "$TMP_INPUT" > "$OUTPUT_FILE"
else
    echo "Error: 'claude' CLI not found."
    echo ""
    echo "Manual execution:"
    echo "  cat '$TMP_INPUT' | claude -p --model $UCR_MODEL > '$OUTPUT_FILE'"
    exit 1
fi

# =============================================================================
# Summary
# =============================================================================
OUTPUT_SIZE=$(wc -c < "$OUTPUT_FILE")

# Extract finding counts if possible
P0_COUNT=$(grep -c "P0-" "$OUTPUT_FILE" 2>/dev/null || echo "?")
P1_COUNT=$(grep -c "P1-" "$OUTPUT_FILE" 2>/dev/null || echo "?")
P2_COUNT=$(grep -c "P2-" "$OUTPUT_FILE" 2>/dev/null || echo "?")

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  UCR Complete"
echo "════════════════════════════════════════════════════════════"
echo "  Output:   $OUTPUT_FILE"
echo "  Size:     $OUTPUT_SIZE bytes"
echo "  Findings: P0=$P0_COUNT, P1=$P1_COUNT, P2=$P2_COUNT"
echo ""
echo "  Next steps:"
echo "  1. Review findings in the UCR report"
echo "  2. Run UCRem to generate fix proposals:"
echo "     ./run_ucrem.sh $OUTPUT_FILE $DOC_PATH"
echo "════════════════════════════════════════════════════════════"
