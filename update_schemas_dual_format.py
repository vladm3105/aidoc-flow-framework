#!/usr/bin/env python3
"""
Update remaining YAML schemas with dual-format notes.

Adds the dual-format note block after the yaml_template field.
"""

import os

schemas_to_update = [
    "ai_dev_flow/03_EARS/EARS_MVP_SCHEMA.yaml",
    "ai_dev_flow/05_ADR/ADR_MVP-TEMPLATE.yaml",
    "ai_dev_flow/06_SYS/SYS_MVP-TEMPLATE.yaml",
    "ai_dev_flow/07_REQ/REQ_MVP-TEMPLATE.yaml",
    "ai_dev_flow/08_CTR/CTR_MVP-TEMPLATE.yaml",
    "ai_dev_flow/10_TASKS/TASKS_MVP-TEMPLATE.yaml",
]

dual_format_note = """\
---
> **🔄 Dual-Format Note**: \
> \
> This MD template is a **primary source** for human workflow. \
> - **For Autopilot**: See `{template}_MVP-TEMPLATE.yaml` (YAML template) \
> - **Shared Validation**: Both formats are validated by `{layer}_MVP_SCHEMA.yaml` \
> - **Complete Explanation**: See [DUAL_MVP_TEMPLATES_ARCHITECTURE.md](../DUAL_MVP_TEMPLATES_ARCHITECTURE.md) for full comparison of formats, authority hierarchy, and when to use each. \
> \
> ---
"""

def update_schema(schema_path):
    """Update a single schema file with dual-format note."""
    try:
        with open(schema_path, 'r') as f:
            lines = f.readlines()
        
        # Find the yaml_template line and get line number
        yaml_template_line_num = None
        for i, line in enumerate(lines):
            if '  yaml_template:' in line and yaml_template_line_num is None:
                yaml_template_line_num = i
                yaml_template_line = line
                break
            # Skip if there's already a dual-format note
            if '🔄 Dual-Format Note' in line:
                print(f"  {schema_path} already has dual-format note, skipping")
                return
        
        # Find line number for insertion (after yaml_template_line)
        # Insert dual-format note after yaml_template line
        yaml_template_line_num = yaml_template_line_num + 2  # yaml_template is line 20, dual-format note goes at line 21
        
        # Build new content
        new_lines = []
        new_lines.extend(lines[:yaml_template_line_num + 1])  # Keep everything before yaml_template
        new_lines.append(dual_format_note)
        new_lines.append("")  # Blank line separator
        new_lines.append("")  # Blank line separator
        new_lines.extend(lines[yaml_template_line_num + 1:])  # Keep yaml_template line and everything after up to dual-format note insert point
        
        # Write back file
        with open(schema_path, 'w') as f:
            f.writelines(new_lines)
        
        print(f"✅ Updated: {os.path.basename(schema_path)}")
        
    except Exception as e:
        print(f"❌ Error updating {schema_path}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    for schema_path in schemas_to_update:
        update_schema(schema_path)