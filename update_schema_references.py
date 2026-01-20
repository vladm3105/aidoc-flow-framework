#!/usr/bin/env python3
"""
Update YAML schemas for dual-format architecture.

Updates the `references` section in schema files to add `yaml_template` field
alongside the existing `template` field (which is the MD template).
"""

import sys

def update_schema(schema_path):
    """Update a single schema file to add yaml_template reference."""
    with open(schema_path, 'r') as f:
        content = f.read()
    
    # Find the references section and add yaml_template field
    # Replace single `template:` line with both md and yaml templates
    content = content.replace(
        "  template: \"{}-MVP-TEMPLATE.md\"\n".format(
            sys.argv[1].replace('_', '-')
            .replace('/', '-')
        ),
        "  md_template: \"{}-MVP-TEMPLATE.md\"\n".format(
            sys.argv[1].replace('_', '-')
            .replace('/', '-')
        ),
        "  yaml_template: \"{}-MVP-TEMPLATE.yaml\"\n".format(
            sys.argv[1].replace('_', '-')
            .replace('/', '-')
        ),
        "  creation_rules: \"{}_MVP_CREATION_RULES.md\"\n".format(
            sys.argv[1].replace('_', '-')
            .replace('/', '-')
        ),
        "  validation_rules: \"{}_MVP_VALIDATION_RULES.md\"\n".format(
            sys.argv[1].replace('_', '-')
            .replace('/', '-')
        ),
    )
    
    with open(schema_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated: {schema_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 update_schema_references.py <schema_file> [schema_file2] ...]")
        print("\nUpdates references section in schema to add yaml_template field.")
        print("Example: python3 update_schema_references.py ai_dev_flow/02_PRD/PRD_MVP_SCHEMA.yaml")
        sys.exit(1)
    
    # Skip the script name if it appears in arguments (happens when run with glob patterns)
    schema_paths = [p for p in sys.argv[1:] if not p.endswith('update_schema_references.py')]
    if not schema_paths:
        print("No schema files provided. Usage: python3 update_schema_references.py <schema_file> [schema_file2] ...]")
        sys.exit(1)
    
    for schema_path in schema_paths:
        update_schema(schema_path)