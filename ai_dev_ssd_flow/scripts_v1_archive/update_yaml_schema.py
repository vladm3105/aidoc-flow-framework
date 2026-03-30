#!/usr/bin/env python3
"""
Update YAML schemas for dual-format architecture.

Updates the `references` section in schema files to add `yaml_template` field
alongside the existing `template` field (which is the MD template).
"""

import sys
from pathlib import Path
import re

def update_schema(schema_path):
    """Update a single schema file to reference template+schema only."""
    with open(schema_path, 'r') as f:
        content = f.read()

    schema_file = Path(schema_path).name
    artifact = schema_file.replace("_MVP_SCHEMA.yaml", "")
    md_template = f"{artifact}-MVP-TEMPLATE.md"
    yaml_template = f"{artifact}-MVP-TEMPLATE.yaml"

    # Normalize references keys and drop deprecated rules references.
    content = re.sub(r"(?m)^\s*template:\s*\".*\"\s*$", f"  md_template: \"{md_template}\"", content)
    content = re.sub(r"(?m)^\s*creation_rules:\s*\".*\"\s*$", f"  md_template: \"{md_template}\"", content)
    content = re.sub(r"(?m)^\s*validation_rules:\s*\".*\"\s*$", f"  schema_reference: \"{artifact}_MVP_SCHEMA.yaml\"", content)

    if "md_template:" not in content:
        content = content.replace("references:\n", f"references:\n  md_template: \"{md_template}\"\n")
    if "yaml_template:" not in content:
        content = content.replace("references:\n", f"references:\n  yaml_template: \"{yaml_template}\"\n")
    if "schema_reference:" not in content:
        content = content.replace("references:\n", f"references:\n  schema_reference: \"{artifact}_MVP_SCHEMA.yaml\"\n")

    # Ensure no deprecated references remain.
    content = re.sub(r"(?m)^\s*(creation_rules|validation_rules):\s*\".*\"\s*$\n?", "", content)
    
    with open(schema_path, 'w') as f:
        f.write(content)
    
    print(f"[PASS] Updated: {schema_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 update_schema.py <schema_file> [schema_file2] ...")
        print("\nUpdates references section in schema to add yaml_template field.")
        print("Example: python3 update_schema.py ai_dev_flow/02_PRD/PRD_MVP_SCHEMA.yaml")
        sys.exit(1)
    
    for schema_path in sys.argv[1:]:
        update_schema(schema_path)
