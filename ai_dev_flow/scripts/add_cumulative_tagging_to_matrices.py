#!/usr/bin/env python3
"""Add cumulative tagging sections to remaining traceability matrix templates."""

import re
from pathlib import Path

# Layer configurations
LAYER_CONFIGS = {
    "ADR": {
        "layer": 5,
        "full_name": "ADR (Architecture Decision Records)",
        "required_tags": ["@brd", "@prd", "@ears", "@bdd"],
        "tag_count": "4",
        "example_id": "ADR-033",
        "example_title": "Order Service Architecture",
        "example_tags": {
            "brd": "BRD-009:FR-015, BRD-009:NFR-006",
            "prd": "PRD-016:FEATURE-003",
            "ears": "EARS-012:EVENT-002, EARS-012:STATE-001",
            "bdd": "BDD-015:scenario-place-order, BDD-015:scenario-reject-invalid"
        },
        "traceability_role": "ADR documents architectural choices that implement BDD acceptance criteria, bridging validated requirements and system design."
    },
    "SYS": {
        "layer": 6,
        "full_name": "SYS (System Requirements)",
        "required_tags": ["@brd", "@prd", "@ears", "@bdd", "@adr"],
        "tag_count": "5",
        "example_id": "SYS-012",
        "example_title": "Order Service System Requirements",
        "example_tags": {
            "brd": "BRD-009:FR-015, BRD-009:NFR-006",
            "prd": "PRD-016:FEATURE-003",
            "ears": "EARS-012:EVENT-002, EARS-012:STATE-001",
            "bdd": "BDD-015:scenario-place-order",
            "adr": "ADR-033"
        },
        "traceability_role": "SYS translates architecture decisions into concrete system-level requirements that can be decomposed into atomic specifications."
    },
    "IMPL": {
        "layer": 8,
        "full_name": "IMPL (Implementation Plans)",
        "required_tags": ["@brd", "@prd", "@ears", "@bdd", "@adr", "@sys", "@req"],
        "tag_count": "7",
        "example_id": "IMPL-003",
        "example_title": "Order Service Implementation Plan",
        "example_tags": {
            "brd": "BRD-009:FR-015, BRD-009:NFR-006",
            "prd": "PRD-016:FEATURE-003",
            "ears": "EARS-012:EVENT-002",
            "bdd": "BDD-015:scenario-place-order",
            "adr": "ADR-033",
            "sys": "SYS-012:FUNC-001",
            "req": "REQ-045:interface-spec"
        },
        "traceability_role": "IMPL plans phased implementation of atomic requirements, providing roadmap from requirements to code. (Optional layer - include only if exists in chain)"
    },
    "CTR": {
        "layer": 9,
        "full_name": "CTR (API Contracts)",
        "required_tags": ["@brd", "@prd", "@ears", "@bdd", "@adr", "@sys", "@req", "@impl"],
        "tag_count": "8",
        "example_id": "CTR-005",
        "example_title": "Order Placement API Contract",
        "example_tags": {
            "brd": "BRD-009:FR-015",
            "prd": "PRD-016:FEATURE-003",
            "ears": "EARS-012:EVENT-002",
            "bdd": "BDD-015:scenario-place-order",
            "adr": "ADR-033",
            "sys": "SYS-012:FUNC-001",
            "req": "REQ-045:interface-spec",
            "impl": "IMPL-003:phase2"
        },
        "traceability_role": "CTR defines formal API contracts implementing requirements, ensuring interface compliance. (Optional layer - include only if exists in chain)"
    },
    "TASKS": {
        "layer": 11,
        "full_name": "TASKS (Implementation Tasks)",
        "required_tags": ["@brd", "@prd", "@ears", "@bdd", "@adr", "@sys", "@req", "@spec"],
        "tag_count": "8-10 (includes @spec, optional @impl, @ctr)",
        "example_id": "TASKS-015",
        "example_title": "Order Service Implementation Tasks",
        "example_tags": {
            "brd": "BRD-009:FR-015",
            "prd": "PRD-016:FEATURE-003",
            "ears": "EARS-012:EVENT-002",
            "bdd": "BDD-015:scenario-place-order",
            "adr": "ADR-033",
            "sys": "SYS-012:FUNC-001",
            "req": "REQ-045:interface-spec",
            "impl": "IMPL-003:phase2",
            "ctr": "CTR-005",
            "spec": "SPEC-018"
        },
        "traceability_role": "TASKS breaks down technical specifications into atomic, session-scoped implementation units with complete upstream traceability."
    },
    "TASKS_PLANS": {
        "layer": 12,
        "full_name": "tasks_plans (Session Plans)",
        "required_tags": ["@brd", "@prd", "@ears", "@bdd", "@adr", "@sys", "@req", "@spec", "@tasks"],
        "tag_count": "9-11 (includes all layers through @tasks)",
        "example_id": "session-2025-11-13-order-service",
        "example_title": "Order Service Development Session",
        "example_tags": {
            "brd": "BRD-009:FR-015",
            "prd": "PRD-016:FEATURE-003",
            "ears": "EARS-012:EVENT-002",
            "bdd": "BDD-015:scenario-place-order",
            "adr": "ADR-033",
            "sys": "SYS-012:FUNC-001",
            "req": "REQ-045:interface-spec",
            "impl": "IMPL-003:phase2",
            "ctr": "CTR-005",
            "spec": "SPEC-018",
            "tasks": "TASKS-015"
        },
        "traceability_role": "tasks_plans organizes session-specific implementation work, maintaining complete chain from business requirements through tasks."
    }
}


def generate_cumulative_tagging_section(artifact_type: str) -> str:
    """Generate Section 2 content for an artifact type."""
    config = LAYER_CONFIGS[artifact_type]

    # Build tag examples
    tag_examples = "\n".join([f"@{tag_type}: {tag_value}"
                               for tag_type, tag_value in config["example_tags"].items()])

    # Build tag format list
    tag_format_list = ", ".join([f"`{tag}`" for tag in config["required_tags"]])

    section = f"""---

## 2. Required Tags (Cumulative Tagging Hierarchy - Layer {config['layer']})

### 2.1 Tag Requirements for {artifact_type} Artifacts

**Layer**: {config['layer']}
**Artifact Type**: {config['full_name']}
**Required Tags**: {tag_format_list}
**Tag Count**: {config['tag_count']}

### 2.2 Tag Format

```markdown
{tag_examples}
```

**Format Rules**:
- Prefix: `@` symbol
- Artifact Type: lowercase ({", ".join([f"`{t[1:]}`" for t in config['required_tags']])})
- Separator: colon `:` after artifact type, `:` between document ID and requirement ID
- Document ID: Standard format (e.g., `{artifact_type}-NNN`)
- Requirement ID: Specific requirement/section identifier
- Multiple Values: comma-separated for same artifact type

### 2.3 Example: {artifact_type} with Required Tags

```markdown
# {config['example_id']}: {config['example_title']}

## 7. Traceability

### 7.1 Upstream Sources

**Required Tags** (Cumulative Tagging Hierarchy - Layer {config['layer']}):
```markdown
{tag_examples}
```

### 7.2 Downstream Artifacts
[Links to SPEC, TASKS, Code that reference this {artifact_type}]
```

### 2.4 Validation Rules

1. **Required**: Each {artifact_type} artifact MUST include at least one tag for each required layer
2. **Format Compliance**: All tags must follow `@artifact-type:DOC-ID:REQ-ID` format
3. **Valid References**: All referenced documents and requirements must exist
4. **No Gaps**: Cannot skip any required upstream layer in the chain
5. **Tag Count**: Must have exactly {config['tag_count']} tags for Layer {config['layer']}

### 2.5 Tag Discovery

{artifact_type} tags can be discovered automatically:
```bash
# Find all {artifact_type}s and their upstream tags
python scripts/extract_tags.py --type {artifact_type} --show-all-upstream

# Validate {config['example_id']} has required tags
python scripts/validate_tags_against_docs.py \\
  --artifact {config['example_id']} \\
  --expected-layers {",".join([t[1:] for t in config['required_tags']])} \\
  --strict

# Generate {artifact_type} traceability report
python scripts/generate_traceability_matrices.py \\
  --type {artifact_type} \\
  --show-coverage
```

### 2.6 {artifact_type} Traceability Pattern

**Key Role**: {config['traceability_role']}

---
"""
    return section


def renumber_sections(content: str, start_section: int) -> str:
    """Renumber sections starting from start_section."""
    lines = content.split('\n')
    result = []
    current_section = start_section

    for line in lines:
        # Match main section headers (## N. Title)
        main_match = re.match(r'^##\s+(\d+)\.\s+(.+)$', line)
        if main_match:
            old_num = int(main_match.group(1))
            title = main_match.group(2)
            if old_num >= start_section:
                result.append(f"## {current_section}. {title}")
                current_section += 1
                continue

        # Match subsection headers (### N.M Title)
        sub_match = re.match(r'^###\s+(\d+)\.(\d+)\s+(.+)$', line)
        if sub_match:
            main_num = int(sub_match.group(1))
            sub_num = sub_match.group(2)
            title = sub_match.group(3)
            # Only renumber if main section >= start_section
            if main_num >= start_section:
                new_main = main_num + 1
                result.append(f"### {new_main}.{sub_num} {title}")
                continue

        result.append(line)

    return '\n'.join(result)


def update_matrix_template(artifact_type: str, template_path: Path):
    """Update a matrix template with cumulative tagging section."""
    print(f"\n{'='*60}")
    print(f"Updating {artifact_type} matrix template...")
    print(f"{'='*60}")

    # Read template
    content = template_path.read_text(encoding='utf-8')

    # Check if already has Section 2 with cumulative tagging
    if "## 2. Required Tags (Cumulative Tagging Hierarchy" in content:
        print(f"✅ {artifact_type} already has cumulative tagging section - skipping")
        return False

    # Generate new Section 2
    new_section_2 = generate_cumulative_tagging_section(artifact_type)

    # Find insertion point (after ## 1. Overview section ends)
    # Look for the line with "---" that comes after "## 1. Overview"
    pattern = r'(## 1\. Overview.*?\n---\n)'
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        print(f"❌ Could not find insertion point in {artifact_type} template")
        return False

    # Insert new section
    insertion_point = match.end()
    updated_content = (
        content[:insertion_point] +
        "\n" + new_section_2 +
        content[insertion_point:]
    )

    # Renumber subsequent sections (original 2 becomes 3, 3 becomes 4, etc.)
    final_content = renumber_sections(updated_content, 2)

    # Write back
    template_path.write_text(final_content, encoding='utf-8')
    print(f"✅ {artifact_type} template updated successfully")
    return True


def main():
    """Update all remaining matrix templates."""
    base_dir = Path(__file__).parent.parent

    templates_to_update = [
        ("ADR", base_dir / "ADR" / "ADR-000_TRACEABILITY_MATRIX-TEMPLATE.md"),
        ("SYS", base_dir / "SYS" / "SYS-000_TRACEABILITY_MATRIX-TEMPLATE.md"),
        ("IMPL", base_dir / "IMPL" / "IMPL-000_TRACEABILITY_MATRIX-TEMPLATE.md"),
        ("CTR", base_dir / "CONTRACTS" / "CTR-000_TRACEABILITY_MATRIX-TEMPLATE.md"),
        ("TASKS", base_dir / "TASKS" / "TASKS-000_TRACEABILITY_MATRIX-TEMPLATE.md"),
        ("TASKS_PLANS", base_dir / "tasks_plans" / "TASKS_PLANS-000_TRACEABILITY_MATRIX-TEMPLATE.md"),
    ]

    updated_count = 0
    for artifact_type, template_path in templates_to_update:
        if not template_path.exists():
            print(f"⚠️  Template not found: {template_path}")
            continue

        if update_matrix_template(artifact_type, template_path):
            updated_count += 1

    print(f"\n{'='*60}")
    print(f"✅ Updated {updated_count} templates")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
