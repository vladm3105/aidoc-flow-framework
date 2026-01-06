#!/bin/bash
# Bulk update TYPE.NNN.NNN to TYPE.NN.EE.SS format
# Run from /opt/data/docs_flow_framework

set -e

echo "Starting element ID format update..."

# Define the base directory
BASE_DIR="/opt/data/docs_flow_framework"

# Function to update files with sed
update_file() {
    local file="$1"
    if [ -f "$file" ]; then
        # Replace TYPE.NNN.NNN patterns with TYPE.NN.EE.SS
        sed -i 's/TYPE\.NNN\.NNN/TYPE.NN.EE.SS/g' "$file"
        sed -i 's/{DOC_TYPE}\.NNN\.NNN/{DOC_TYPE}.NN.EE.SS/g' "$file"

        # Replace specific artifact patterns
        sed -i 's/BRD\.NNN\.NNN/BRD.NN.EE.SS/g' "$file"
        sed -i 's/PRD\.NNN\.NNN/PRD.NN.EE.SS/g' "$file"
        sed -i 's/EARS\.NNN\.NNN/EARS.NN.EE.SS/g' "$file"
        sed -i 's/BDD\.NNN\.NNN/BDD.NN.EE.SS/g' "$file"
        sed -i 's/ADR\.NNN\.NNN/ADR.NN.EE.SS/g' "$file"
        sed -i 's/SYS\.NNN\.NNN/SYS.NN.EE.SS/g' "$file"
        sed -i 's/REQ\.NNN\.NNN/REQ.NN.EE.SS/g' "$file"
        sed -i 's/SPEC\.NNN\.NNN/SPEC.NN.EE.SS/g' "$file"
        sed -i 's/CTR\.NNN\.NNN/CTR.NN.EE.SS/g' "$file"
        sed -i 's/IMPL\.NNN\.NNN/IMPL.NN.EE.SS/g' "$file"
        sed -i 's/TASKS\.NNN\.NNN/TASKS.NN.EE.SS/g' "$file"
        sed -i 's/IPLAN\.NNN\.NNN/IPLAN.NN.EE.SS/g' "$file"
        sed -i 's/DOC\.NNN\.NNN/DOC.NN.EE.SS/g' "$file"

        echo "Updated: $file"
    fi
}

# Update ai_dev_flow files
echo "=== Phase 1: Schema files ==="
for f in "$BASE_DIR"/ai_dev_flow/*/*.yaml "$BASE_DIR"/ai_dev_flow/*/*_SCHEMA.yaml; do
    [ -f "$f" ] && update_file "$f"
done

echo "=== Phase 2: Creation Rules ==="
for f in "$BASE_DIR"/ai_dev_flow/*/*_CREATION_RULES.md; do
    [ -f "$f" ] && update_file "$f"
done

echo "=== Phase 3: Validation Rules ==="
for f in "$BASE_DIR"/ai_dev_flow/*/*_VALIDATION_RULES.md; do
    [ -f "$f" ] && update_file "$f"
done

echo "=== Phase 4: Templates ==="
for f in "$BASE_DIR"/ai_dev_flow/*/*-TEMPLATE*.md "$BASE_DIR"/ai_dev_flow/*/*-TEMPLATE*.yaml; do
    [ -f "$f" ] && update_file "$f"
done

echo "=== Phase 5: Core Documents ==="
update_file "$BASE_DIR/ai_dev_flow/TRACEABILITY.md"
update_file "$BASE_DIR/ai_dev_flow/TRACEABILITY_VALIDATION.md"
update_file "$BASE_DIR/ai_dev_flow/TRACEABILITY_MATRIX_COMPLETE-TEMPLATE.md"
update_file "$BASE_DIR/ai_dev_flow/AI_ASSISTANT_RULES.md"
update_file "$BASE_DIR/ai_dev_flow/ID_NAMING_STANDARDS.md"

echo "=== Phase 6: Other files ==="
update_file "$BASE_DIR/ai_dev_flow/scripts/README.md"
update_file "$BASE_DIR/ai_dev_flow/scripts/validate_cross_document.py"
update_file "$BASE_DIR/ai_dev_flow/scripts/validate_ears.py"
update_file "$BASE_DIR/ai_dev_flow/BRD/FR_EXAMPLES_GUIDE.md"
update_file "$BASE_DIR/ai_dev_flow/BDD/BDD-000_index.md"
update_file "$BASE_DIR/ai_dev_flow/IPLAN/README.md"

echo "=== Phase 7: Skills ==="
for f in "$BASE_DIR"/.claude/skills/doc-*/SKILL.md; do
    [ -f "$f" ] && update_file "$f"
done

echo "Done! Verifying remaining occurrences..."
grep -r "\.NNN\.NNN" "$BASE_DIR/ai_dev_flow" --include="*.md" --include="*.yaml" --include="*.py" 2>/dev/null | grep -v "archive/" | head -20 || echo "No more occurrences found."
