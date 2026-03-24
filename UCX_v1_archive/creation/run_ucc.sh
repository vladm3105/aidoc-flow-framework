#!/usr/bin/env bash
# =============================================================================
# run_ucc.sh — UCC (Unified Context Creation) Runner
# =============================================================================
# Framework-level script for creating documents using multi-persona authoring.
# Includes dynamic skill loading for enhanced persona knowledge.
#
# Usage:
#   ./run_ucc.sh <doc_type> <output_path> [options]
#
# Examples:
#   ./run_ucc.sh brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/
#   ./run_ucc.sh prd docs/02_PRD/PRD-01.md --from-upstream docs/01_BRD/BRD-01/
#   ./run_ucc.sh ears docs/03_EARS/EARS-01.md --from-upstream docs/02_PRD/PRD-01.md
#
# Arguments:
#   doc_type    - Document type: brd, prd, ears, bdd, adr, sys, req, ctr, spec, tspec
#   output_path - Path to output file or directory
#
# Options:
#   --from-ref <dir>       - Load reference documents from directory
#   --from-upstream <file> - Load upstream artifact(s)
#   --template <file>      - Use custom template (default: MVP template)
#   --multi-file           - Generate multi-file output (for BRD)
#
# Environment:
#   UCC_PROMPT_DIR  - Directory containing UCC prompts (default: script directory)
#   UCC_MODEL       - Claude model to use (default: opus)
#   UCC_LOAD_SKILLS - Load skill files into prompt (default: true)
#
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UCX_ROOT="$(dirname "$SCRIPT_DIR")"

# =============================================================================
# Configuration
# =============================================================================
UCC_PROMPT_DIR="${UCC_PROMPT_DIR:-$SCRIPT_DIR}"
UCC_MODEL="${UCC_MODEL:-opus}"
UCC_LOAD_SKILLS="${UCC_LOAD_SKILLS:-true}"
SKILL_DIR="$UCX_ROOT/skills"
TEMPLATE_DIR="$UCX_ROOT/templates"

# =============================================================================
# Layer-to-Skills Mapping (Author Personas)
# =============================================================================
declare -A LAYER_SKILLS
LAYER_SKILLS[brd]="architect product_owner business_analyst strategist tech_lead"
LAYER_SKILLS[prd]="product_owner ux_strategist tech_lead qa_lead architect"
LAYER_SKILLS[ears]="requirements_specialist tech_lead qa_lead chaos_engineer"
LAYER_SKILLS[bdd]="qa_lead tech_lead chaos_engineer operator"
LAYER_SKILLS[adr]="architect tech_lead strategist chaos_engineer operator"
LAYER_SKILLS[sys]="architect tech_lead operator integration_expert"
LAYER_SKILLS[req]="requirements_specialist tech_lead integration_expert"
LAYER_SKILLS[ctr]="architect tech_lead integration_expert"
LAYER_SKILLS[spec]="tech_lead architect operator integration_expert"
LAYER_SKILLS[tspec]="qa_lead tech_lead operator"

# =============================================================================
# Parse arguments
# =============================================================================
DOC_TYPE="${1:-}"
OUTPUT_PATH="${2:-}"
shift 2 || true

FROM_REF=""
FROM_UPSTREAM=""
CUSTOM_TEMPLATE=""
MULTI_FILE="false"

while [[ $# -gt 0 ]]; do
    case $1 in
        --from-ref)
            FROM_REF="$2"
            shift 2
            ;;
        --from-upstream)
            FROM_UPSTREAM="$2"
            shift 2
            ;;
        --template)
            CUSTOM_TEMPLATE="$2"
            shift 2
            ;;
        --multi-file)
            MULTI_FILE="true"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [[ -z "$DOC_TYPE" || -z "$OUTPUT_PATH" ]]; then
    echo "Usage: ./run_ucc.sh <doc_type> <output_path> [options]"
    echo ""
    echo "Document types: brd, prd, ears, bdd, adr, sys, req, ctr, spec, tspec"
    echo ""
    echo "Options:"
    echo "  --from-ref <dir>       Load reference documents"
    echo "  --from-upstream <file> Load upstream artifact"
    echo "  --template <file>      Use custom template"
    echo "  --multi-file           Generate multi-file output"
    echo ""
    echo "Examples:"
    echo "  ./run_ucc.sh brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/"
    echo "  ./run_ucc.sh prd docs/02_PRD/PRD-01.md --from-upstream docs/01_BRD/BRD-01/"
    echo ""
    echo "Environment variables:"
    echo "  UCC_LOAD_SKILLS=false  # Disable skill loading"
    echo ""
    exit 1
fi

# Normalize doc type to lowercase
DOC_TYPE=$(echo "$DOC_TYPE" | tr '[:upper:]' '[:lower:]')

# =============================================================================
# Select UCC prompt
# =============================================================================
PROJECT_PROMPT="UCC_PROMPT_${DOC_TYPE^^}_PROJECT.md"
BEELOCAL_PROMPT="UCC_PROMPT_${DOC_TYPE^^}_BEELOCAL.md"
FRAMEWORK_PROMPT="UCC_PROMPT_${DOC_TYPE^^}.md"

if [[ -f "$UCC_PROMPT_DIR/$PROJECT_PROMPT" ]]; then
    PROMPT_FILE="$UCC_PROMPT_DIR/$PROJECT_PROMPT"
    echo "Using project-specific prompt: $PROJECT_PROMPT"
elif [[ -f "$UCC_PROMPT_DIR/$BEELOCAL_PROMPT" ]]; then
    PROMPT_FILE="$UCC_PROMPT_DIR/$BEELOCAL_PROMPT"
    echo "Using project-specific prompt: $BEELOCAL_PROMPT"
elif [[ -f "$UCC_PROMPT_DIR/$FRAMEWORK_PROMPT" ]]; then
    PROMPT_FILE="$UCC_PROMPT_DIR/$FRAMEWORK_PROMPT"
else
    echo "Error: No UCC prompt found for document type '$DOC_TYPE'"
    echo "Searched for:"
    echo "  - $UCC_PROMPT_DIR/$PROJECT_PROMPT"
    echo "  - $UCC_PROMPT_DIR/$BEELOCAL_PROMPT"
    echo "  - $UCC_PROMPT_DIR/$FRAMEWORK_PROMPT"
    exit 1
fi

# =============================================================================
# Select Template
# =============================================================================
if [[ -n "$CUSTOM_TEMPLATE" ]]; then
    TEMPLATE_FILE="$CUSTOM_TEMPLATE"
elif [[ -f "$TEMPLATE_DIR/${DOC_TYPE^^}-MVP-TEMPLATE.md" ]]; then
    TEMPLATE_FILE="$TEMPLATE_DIR/${DOC_TYPE^^}-MVP-TEMPLATE.md"
elif [[ -f "$TEMPLATE_DIR/${DOC_TYPE^^}-MVP-TEMPLATE.feature" ]]; then
    TEMPLATE_FILE="$TEMPLATE_DIR/${DOC_TYPE^^}-MVP-TEMPLATE.feature"
else
    TEMPLATE_FILE=""
    echo "Warning: No template found for $DOC_TYPE"
fi

# =============================================================================
# Set output path
# =============================================================================
if [[ "$MULTI_FILE" == "true" ]]; then
    # Create output directory
    mkdir -p "$OUTPUT_PATH"
    OUTPUT_FILE="$OUTPUT_PATH/${DOC_TYPE^^}_CREATED.md"
else
    # Ensure parent directory exists
    mkdir -p "$(dirname "$OUTPUT_PATH")"
    OUTPUT_FILE="$OUTPUT_PATH"
fi

# =============================================================================
# Build combined input with skills
# =============================================================================
TMP_INPUT=$(mktemp /tmp/ucc_input_XXXXXX.md)
trap "rm -f $TMP_INPUT" EXIT

echo "Building UCC input..."
echo "  Prompt: $PROMPT_FILE"
echo "  Output: $OUTPUT_FILE"

# Start with prompt
cat "$PROMPT_FILE" > "$TMP_INPUT"

# =============================================================================
# Load Author Skills (if enabled)
# =============================================================================
if [[ "$UCC_LOAD_SKILLS" == "true" && -d "$SKILL_DIR" ]]; then
    SKILLS="${LAYER_SKILLS[$DOC_TYPE]:-}"

    if [[ -n "$SKILLS" ]]; then
        echo "  Skills: $SKILLS"

        echo "" >> "$TMP_INPUT"
        echo "---" >> "$TMP_INPUT"
        echo "" >> "$TMP_INPUT"
        echo "## AUTHOR PERSONA SKILL DEFINITIONS" >> "$TMP_INPUT"
        echo "" >> "$TMP_INPUT"
        echo "The following domain knowledge is available to each author persona:" >> "$TMP_INPUT"
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
    echo "  Skills: disabled (UCC_LOAD_SKILLS=$UCC_LOAD_SKILLS)"
fi

# =============================================================================
# Add Template (if available)
# =============================================================================
if [[ -n "$TEMPLATE_FILE" && -f "$TEMPLATE_FILE" ]]; then
    echo "  Template: $TEMPLATE_FILE"
    echo "" >> "$TMP_INPUT"
    echo "---" >> "$TMP_INPUT"
    echo "" >> "$TMP_INPUT"
    echo "# DOCUMENT TEMPLATE" >> "$TMP_INPUT"
    echo "" >> "$TMP_INPUT"
    echo "Follow this template structure exactly:" >> "$TMP_INPUT"
    echo "" >> "$TMP_INPUT"
    cat "$TEMPLATE_FILE" >> "$TMP_INPUT"
fi

# =============================================================================
# Add Reference Documents (if provided)
# =============================================================================
if [[ -n "$FROM_REF" && -d "$FROM_REF" ]]; then
    echo "  Reference: $FROM_REF"
    echo "" >> "$TMP_INPUT"
    echo "---" >> "$TMP_INPUT"
    echo "" >> "$TMP_INPUT"
    echo "# REFERENCE DOCUMENTS" >> "$TMP_INPUT"
    echo "" >> "$TMP_INPUT"

    for f in "$FROM_REF"/*.md "$FROM_REF"/*.txt; do
        if [[ -f "$f" ]]; then
            echo "## Reference: $(basename "$f")" >> "$TMP_INPUT"
            echo "" >> "$TMP_INPUT"
            cat "$f" >> "$TMP_INPUT"
            echo "" >> "$TMP_INPUT"
        fi
    done
fi

# =============================================================================
# Add Upstream Artifact (if provided)
# =============================================================================
if [[ -n "$FROM_UPSTREAM" ]]; then
    echo "  Upstream: $FROM_UPSTREAM"
    echo "" >> "$TMP_INPUT"
    echo "---" >> "$TMP_INPUT"
    echo "" >> "$TMP_INPUT"
    echo "# UPSTREAM ARTIFACT" >> "$TMP_INPUT"
    echo "" >> "$TMP_INPUT"

    if [[ -d "$FROM_UPSTREAM" ]]; then
        # Directory: concatenate all markdown files
        for f in "$FROM_UPSTREAM"/*.md; do
            if [[ -f "$f" ]]; then
                echo "## File: $(basename "$f")" >> "$TMP_INPUT"
                echo "" >> "$TMP_INPUT"
                cat "$f" >> "$TMP_INPUT"
                echo "" >> "$TMP_INPUT"
            fi
        done
    elif [[ -f "$FROM_UPSTREAM" ]]; then
        # Single file
        echo "## File: $(basename "$FROM_UPSTREAM")" >> "$TMP_INPUT"
        echo "" >> "$TMP_INPUT"
        cat "$FROM_UPSTREAM" >> "$TMP_INPUT"
        echo "" >> "$TMP_INPUT"
    fi
fi

# =============================================================================
# Run UCC
# =============================================================================
INPUT_SIZE=$(wc -c < "$TMP_INPUT")
INPUT_LINES=$(wc -l < "$TMP_INPUT")

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  UCC (Unified Context Creation)"
echo "════════════════════════════════════════════════════════════"
echo "  Document Type: ${DOC_TYPE^^}"
echo "  Input Size:    $INPUT_SIZE bytes ($INPUT_LINES lines)"
echo "  Output:        $OUTPUT_FILE"
echo "  Model:         $UCC_MODEL"
echo "  Skills:        $([[ "$UCC_LOAD_SKILLS" == "true" ]] && echo "enabled" || echo "disabled")"
echo "  Multi-file:    $MULTI_FILE"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Running UCC document creation..."
echo ""

# Run with Claude CLI
if command -v claude &> /dev/null; then
    claude -p --model "$UCC_MODEL" < "$TMP_INPUT" > "$OUTPUT_FILE"
else
    echo "Error: 'claude' CLI not found."
    echo ""
    echo "Manual execution:"
    echo "  cat '$TMP_INPUT' | claude -p --model $UCC_MODEL > '$OUTPUT_FILE'"
    exit 1
fi

# =============================================================================
# Summary
# =============================================================================
OUTPUT_SIZE=$(wc -c < "$OUTPUT_FILE")
OUTPUT_LINES=$(wc -l < "$OUTPUT_FILE")

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  UCC Complete"
echo "════════════════════════════════════════════════════════════"
echo "  Output:  $OUTPUT_FILE"
echo "  Size:    $OUTPUT_SIZE bytes ($OUTPUT_LINES lines)"
echo ""
echo "  Next steps:"
echo "  1. Review the generated document"
echo "  2. Run UCR to validate:"
echo "     ../review/run_ucr.sh $DOC_TYPE $OUTPUT_PATH"
echo "════════════════════════════════════════════════════════════"
