#!/bin/bash
# Standardize workflow diagram references in all README files
# Decision: All READMEs reference index.md as authoritative source

base_dir="/opt/data/docs_flow_framework/ai_dev_flow"

# Standard reference text to use
read -r -d '' STANDARD_REF <<'EOF'
**⚠️ See [../index.md](../index.md#traceability-flow) for the authoritative workflow visualization.**
EOF

echo "Standardizing workflow diagram references..."
echo ""

for readme in "$base_dir"/*/README.md; do
    artifact=$(basename $(dirname "$readme"))
    echo "Processing $artifact/README.md..."

    # Check if file has Position in Development Workflow section
    if grep -q "Position in Development Workflow" "$readme" || \
       grep -q "Position in.*Workflow" "$readme" || \
       grep -q "\[RESOURCE_INSTANCE.*\] in Development Workflow" "$readme"; then

        # Check if already has the standard reference
        if grep -q "See \[../index.md\](../index.md#traceability-flow)" "$readme"; then
            echo "  ✓ Already has standard reference"
        else
            # Need to add standard reference after the heading
            # This is a manual task - flag it
            echo "  ⚠️  Needs manual update to add standard reference"
        fi
    else
        echo "  - No workflow section found"
    fi
done

echo ""
echo "Summary: All README files with workflow sections should include:"
echo "$STANDARD_REF"
