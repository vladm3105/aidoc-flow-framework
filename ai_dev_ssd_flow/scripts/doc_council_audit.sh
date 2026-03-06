#!/usr/bin/env bash

# AI Expert Board Automation Script
# Generates a COUNCIL_AUDIT_REPORT acting as a formal framework audit gate.

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
FRAMEWORK_ROOT="$(dirname "$DIR")"

# ANSI colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper for warnings/errors
error() { echo -e "${RED}[ERROR]${NC} $1" >&2; exit 1; }
warn()  { echo -e "${YELLOW}[WARNING]${NC} $1" >&2; }
info()  { echo -e "${BLUE}[INFO]${NC} $1"; }

# Check for required tools
command -v claude >/dev/null 2>&1 || error "claude CLI is required but not installed."
command -v yq >/dev/null 2>&1 || warn "yq is not installed. Will use basic grep for yaml extraction if needed."

# Arguments
TARGET_FILE="$1"
if [ -z "$TARGET_FILE" ]; then
    echo "Usage: $0 path/to/target_document.md"
    exit 1
fi

if [ ! -f "$TARGET_FILE" ]; then
    error "Target file not found: $TARGET_FILE"
fi

TARGET_DIR=$(dirname "$TARGET_FILE")
TARGET_FILENAME=$(basename "$TARGET_FILE")
TARGET_BASENAME="${TARGET_FILENAME%.*}" # e.g., PRD-50_octo_agent

# Locate project_experts.yaml (Look in TARGET_DIR, then docs/AI_EXPERTS, then fallback to template)
EXPERTS_YAML=""
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)

if [ -f "$TARGET_DIR/project_experts.yaml" ]; then
    EXPERTS_YAML="$TARGET_DIR/project_experts.yaml"
elif [ -n "$PROJECT_ROOT" ] && [ -f "$PROJECT_ROOT/docs/AI_EXPERTS/project_experts.yaml" ]; then
    EXPERTS_YAML="$PROJECT_ROOT/docs/AI_EXPERTS/project_experts.yaml"
else
    warn "No custom project_experts.yaml found. Falling back to framework template."
    EXPERTS_YAML="$FRAMEWORK_ROOT/AI_EXPERTS/project_experts.template.yaml"
fi

info "Using Expert Profile: $EXPERTS_YAML"

# Extract Frontmatter Metadata from target file
doc_id=$(grep -m 1 "^doc_id:" "$TARGET_FILE" | awk '{print $2}' || echo "UNKNOWN")
version=$(grep -m 1 "^version:" "$TARGET_FILE" | awk '{print $2}' || echo "UNKNOWN")
current_date=$(date -I)

if [[ "$doc_id" == "UNKNOWN" ]]; then
    warn "Target file lacks 'doc_id' YAML frontmatter. Using filename as ID."
    doc_id="$TARGET_BASENAME"
fi

# Set output path (Same directory as target file)
OUTPUT_FILE="$TARGET_DIR/${doc_id}_COUNCIL_AUDIT_REPORT.md"
TEMPLATE_FILE="$FRAMEWORK_ROOT/AI_EXPERTS/COUNCIL-MVP-TEMPLATE.md"

info "Target Document: $TARGET_BASENAME (ID: $doc_id, v$version)"
info "Generating audit reports via Claude CLI..."

# Internal Temp Files for the 7 persona responses
mkdir -p "/tmp/council_audit_$$"
TMP_DIR="/tmp/council_audit_$$"

# This is a simplified sequential execution loop for the bash script using Claude CLI
# In a highly advanced setup, this would be parallelized, but sequential ensures stability for the prototype.

PERSONAS=("architect" "auditor" "domain_specialist" "strategist" "qa_lead" "operator" "integration_expert")

echo "--- Commencing Phase 2 Blind Audit ---"

for persona in "${PERSONAS[@]}"; do
    echo -n "Summoning $persona... "
    
    # Very basic grep extraction since we cannot guarantee `yq` is present in all environments
    P_NAME=$(grep -A 5 "$persona:" "$EXPERTS_YAML" | grep "name:" | cut -d'"' -f2 | head -1)
    P_FOCUS=$(grep -A 5 "$persona:" "$EXPERTS_YAML" | grep "focus:" | cut -d'"' -f2 | head -1)
    P_BIAS=$(grep -A 5 "$persona:" "$EXPERTS_YAML" | grep "anti_bias_directive:" | cut -d'"' -f2 | head -1)
    
    cat << EOF > "$TMP_DIR/prompt_$persona.txt"
You are $P_NAME. Your operational focus is: $P_FOCUS.
CRITICAL CONSTRAINT: $P_BIAS

Review the following technical document strictly from your persona's perspective. Do not sugarcoat. Do not be polite. Find the flaws.
Output your findings in EXACTLY three sections:
- 1. Major Risks
- 2. Unhandled Edge Cases
- 3. Alternative Approach

EOF

    # If the persona is integration_expert, append the integration matrix for context
    if [ "$persona" = "integration_expert" ]; then
        MATRIX_FILE="$PROJECT_ROOT/docs/01_BRD/BRD-00_INTEGRATION_MATRIX.md"
        if [ -f "$MATRIX_FILE" ]; then
            echo "=== SYSTEM INTEGRATION MATRIX ===" >> "$TMP_DIR/prompt_$persona.txt"
            cat "$MATRIX_FILE" >> "$TMP_DIR/prompt_$persona.txt"
            echo "=== END SYSTEM INTEGRATION MATRIX ===" >> "$TMP_DIR/prompt_$persona.txt"
            echo "" >> "$TMP_DIR/prompt_$persona.txt"
        else
            warn "Integration matrix not found for integration_expert ($MATRIX_FILE). The expert will audit without it."
        fi
    fi

    cat << EOF >> "$TMP_DIR/prompt_$persona.txt"
=== TARGET DOCUMENT START ===
$(cat "$TARGET_FILE")
=== TARGET DOCUMENT END ===
EOF

    # Execute Claude CLI silently
    cat "$TMP_DIR/prompt_$persona.txt" | claude -p > "$TMP_DIR/response_$persona.txt"
    echo -e "${GREEN}Done.${NC}"
done

echo "--- Summarizing via Chairperson ---"
# Gather all 6 responses
C_NAME=$(grep -A 5 "chairperson:" "$EXPERTS_YAML" | grep "name:" | cut -d'"' -f2 | head -1)
C_BIAS=$(grep -A 5 "chairperson:" "$EXPERTS_YAML" | grep "anti_bias_directive:" | cut -d'"' -f2 | head -1)

cat << EOF > "$TMP_DIR/prompt_chairperson.txt"
You are $C_NAME. 
$C_BIAS

Read the following 7 conflicting expert reports regarding document $doc_id.
Adjudicate and synthesize them into the final markdown structure provided in the template. Do not include the YAML block, just the markdown body starting from the H1 header.

=== EXPERT REPORTS ===
$(for p in "${PERSONAS[@]}"; do echo "--- Report from $p ---"; cat "$TMP_DIR/response_$p.txt"; echo ""; done)
=== END EXPERT REPORTS ===

=== REQUIRED OUTPUT STRUCTURE (Follow exactly) ===
# Expert Board Audit Report: $doc_id

> **Target Document**: $doc_id (Version $version)
> **Audit Date**: $current_date
> **Board Configuration**: project_experts.yaml

## 1. Executive Summary
*   **Consensus Recommendation**: (Proceed / Remediation Required / Fundamental Redesign)
*   *Chairperson's Synthesis*: [Your synthesized paragraph]

[... Fill out Sections 2 through 6 based on the template requirements]
EOF

cat "$TMP_DIR/prompt_chairperson.txt" | claude -p > "$TMP_DIR/final_body.md"

# Assemble the final file
echo -e "${BLUE}[INFO]${NC} Assembling $OUTPUT_FILE"

# 1. Generate YAML Frontmatter from template, replacing variables
cat "$TEMPLATE_FILE" | awk '/^---/{if(++c==2) {print; exit}} {print}' | \
    sed "s/{NN}/${doc_id//[!0-9]/}/g" | \
    sed "s/{TARGET_DOC_ID}/$doc_id/g" | \
    sed "s/{TARGET_DOC_VERSION}/$version/g" | \
    sed "s/{PASS_OR_FAIL}/PENDING_REVIEW/g" | \
    sed "s/{CURRENT_DATE}/$current_date/g" > "$OUTPUT_FILE"

# 2. Append Chairperson Body
cat "$TMP_DIR/final_body.md" >> "$OUTPUT_FILE"

# Clean up
rm -rf "$TMP_DIR"

echo -e "${GREEN}[SUCCESS]${NC} COUNCIL Audit Report successfully generated at:"
echo "$OUTPUT_FILE"
echo "This document MUST pass validation before moving the target document to the next SDD layer."
