#!/usr/bin/env python3
"""
Update all YAML schemas with dual-format references.

Adds yaml_template field to references section alongside existing template field.
This replaces complex sed commands with simple, reliable Python operations.
"""

import os
import sys

def main():
    """Update all YAML schemas with dual-format architecture references."""
    if len(sys.argv) < 2:
        print("Usage: python3 update_schemas_dual_format.py <schema_file> [schema_file2] ...]")
        sys.exit(1)
    
    # Define schema paths - excluding CHG (change management, not a layer artifact)
    schemas = [
        "ai_dev_flow/01_BRD/BRD_MVP_SCHEMA.yaml",
        "ai_dev_flow/02_PRD/PRD_MVP_SCHEMA.yaml",
        "ai_dev_flow/03_EARS/EARS_MVP_SCHEMA.yaml",
        "ai_dev_flow/05_ADR/ADR_MVP_SCHEMA.yaml",
        "ai_dev_flow/06_SYS/SYS/MVP_SCHEMA.yaml",
        "ai_dev_flow/07_REQ/REQ_MVP_SCHEMA.yaml",
        "ai_dev_flow/08_CTR/CTR_MVP_SCHEMA.yaml",
        "ai_dev_flow/10_TASKS/TASKS_MVP_SCHEMA.yaml"
    ]
    
    for schema in schemas:
        update_single_schema(schema)

def update_single_schema(schema_path):
    """Update a single schema file with dual-format references."""
    try:
        if not os.path.exists(schema_path):
            print(f"⚠️  Schema not found: {schema_path}")
            return
        
        with open(schema_path, 'r') as f:
            lines = f.readlines()
        
        # Find yaml_template line number (skip YAML frontmatter)
        yaml_template_line_num = None
        frontmatter_end_line_num = None
        for i, line in enumerate(lines, 1):
            line = line.rstrip()
            
            # Skip YAML frontmatter (starts with '---' or '#')
            if line in ('#', '---'):
                frontmatter_end_line_num = i
                continue
            
            # Find yaml_template line: should have yaml_template field
            if 'yaml_template:' in line and frontmatter_end_line_num is not None:
                yaml_template_line_num = i
                # Continue to find exact position
                continue
        
        # Find references section (after title, before any other content)
        for i in range(frontmatter_end_line_num + 1, len(lines)):
            line = lines[i].rstrip()
            if 'references:' in line.lower() and yaml_template_line_num is None:
                references_line_num = i
                yaml_template_line_num = i + 2  # Found references section
        
        # Add/update yaml_template field if missing
        if yaml_template_line_num is None:
            print(f"⚠️  yaml_template field not found in {schema_path}")
            return
        
        # Check if references section exists
        has_references = False
        for i in range(references_line_num + 1, len(lines)):
            line = lines[i].rstrip()
            if line.strip() == "":
                continue
            if 'references:' in line.lower():
                has_references = True
                break
        
        if not has_references:
            print(f"⚠️  No references section found in {schema_path}")
            return
        
        # Add yaml_template field after references
        new_lines = []
        
        # Keep content up to yaml_template line (exclusive)
        in_yaml_frontmatter = False
        
        for i in range(references_line_num, len(lines)):
            line = lines[i].rstrip()
            if i == yaml_template_line_num:
                in_yaml_frontmatter = True
                new_lines.append(line)
                continue
            elif '---' in line:
                new_lines.append(line)
                break
            else:
                new_lines.append(line)
        
        # Keep all content after yaml_template line
        if yaml_template_line_num is not None:
            for line in range(references_line_num + 1, len(lines)):
                new_lines.append(lines[i].rstrip())
        
        # Write back to file
        if new_lines:
            with open(schema_path, 'w') as f:
                f.writelines(new_lines)
                print(f"✅ Updated {os.path.basename(schema_path)}")
        else:
            print(f"✅ No changes needed for {os.path.basename(schema_path)}")
    
    except Exception as e:
        print(f"❌ Error updating {schema_path}: {e}")

def update_single_schema(schema_path):
    """Update a single schema file with dual-format references."""
    update_single_schema(schema_path)

def main():
    """Entry point - updates all schemas in the framework."""
    schemas = [
        "ai_dev_flow/01_BRD/BRD_MVP_SCHEMA.yaml",
        "ai_dev_flow/02_PRD/PRD_MVP_SCHEMA.yaml",
        "ai_dev_flow/03_EARS/EARS_MVP_SCHEMA.yaml",
        "ai_dev_flow/05_ADR/ADR_MVP_SCHEMA.yaml",
        "ai_dev_flow/06_SYS/SYS/MVP_SCHEMA.yaml",
        "ai_dev_flow/07_REQ/REQ_MVP_SCHEMA.yaml",
        "ai_dev_flow/08_CTR/CTR_MVP_SCHEMA.yaml",
        "ai_dev_flow/10_TASKS/TASKS_MVP_SCHEMA.yaml",
    ]
    
    for schema in schemas:
        update_single_schema(schema)
    
    print("✅ All schemas updated with dual-format references")
    sys.exit(0)

if __name__ == "__main__":
    main()