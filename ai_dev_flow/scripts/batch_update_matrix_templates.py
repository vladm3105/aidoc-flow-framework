#!/usr/bin/env python3
"""
Batch update traceability matrix templates with cumulative tagging sections.

This script adds layer-specific cumulative tagging requirements to each
artifact type's traceability matrix template.
"""

import os
from pathlib import Path

# Define cumulative tags for each layer
LAYER_CONFIGS = {
    "BRD": {
        "layer": 1,
        "required_tags": "None",
        "tag_count": 0,
        "description": "Business Requirements Document - top level, no upstream dependencies",
        "example_tags": "# No upstream tags required for BRD (Layer 1)",
    },
    "PRD": {
        "layer": 2,
        "required_tags": "`@brd`",
        "tag_count": 1,
        "description": "Product Requirements Document",
        "example_tags": "@brd: BRD-009:FR-015, BRD-009:NFR-006",
    },
    "EARS": {
        "layer": 3,
        "required_tags": "`@brd`, `@prd`",
        "tag_count": 2,
        "description": "Engineering Requirements (EARS format)",
        "example_tags": "@brd: BRD-009:FR-015\n@prd: PRD-016:FEATURE-003",
    },
    "BDD": {
        "layer": 4,
        "required_tags": "`@brd`, `@prd`, `@ears`",
        "tag_count": "3+",
        "description": "Behavior-Driven Development test scenarios",
        "example_tags": "@brd: BRD-009:FR-015\n@prd: PRD-016:FEATURE-003\n@ears: EARS-012:EVENT-002",
    },
    "ADR": {
        "layer": 5,
        "required_tags": "`@brd`, `@prd`, `@ears`, `@bdd`",
        "tag_count": 4,
        "description": "Architecture Decision Record",
        "example_tags": "@brd: BRD-009:FR-015\n@prd: PRD-016:FEATURE-003\n@ears: EARS-012:EVENT-002\n@bdd: BDD-015:scenario-place-order",
    },
    "SYS": {
        "layer": 6,
        "required_tags": "`@brd` through `@adr`",
        "tag_count": 5,
        "description": "System Requirements Document",
        "example_tags": "@brd: BRD-009:FR-015\n@prd: PRD-016:FEATURE-003\n@ears: EARS-012:EVENT-002\n@bdd: BDD-015:scenario-place-order\n@adr: ADR-033",
    },
    "REQ": {
        "layer": 7,
        "required_tags": "`@brd` through `@sys`",
        "tag_count": 6,
        "description": "Atomic Requirements Document",
        "example_tags": "@brd: BRD-009:FR-015\n@prd: PRD-016:FEATURE-003\n@ears: EARS-012:EVENT-002\n@bdd: BDD-015:scenario-place-order\n@adr: ADR-033\n@sys: SYS-012:PERF-001",
    },
    "IMPL": {
        "layer": 8,
        "required_tags": "`@brd` through `@req`",
        "tag_count": 7,
        "description": "Implementation Plan (optional layer)",
        "example_tags": "@brd: BRD-009:FR-015\n@prd: PRD-016:FEATURE-003\n@ears: EARS-012:EVENT-002\n@bdd: BDD-015:scenario-place-order\n@adr: ADR-033\n@sys: SYS-012:PERF-001\n@req: REQ-045:interface-spec",
    },
    "CTR": {
        "layer": 9,
        "required_tags": "`@brd` through `@impl`",
        "tag_count": 8,
        "description": "API Contract Document (optional layer)",
        "example_tags": "@brd: BRD-009:FR-015\n@prd: PRD-016:FEATURE-003\n@ears: EARS-012:EVENT-002\n@bdd: BDD-015:scenario-place-order\n@adr: ADR-033\n@sys: SYS-012:PERF-001\n@req: REQ-045:interface-spec\n@impl: IMPL-003:phase2",
    },
    "SPEC": {
        "layer": 10,
        "required_tags": "`@brd` through `@req` + optional `@impl`, `@ctr`",
        "tag_count": "7-9",
        "description": "Technical Specification (YAML)",
        "example_tags": "@brd: BRD-009:FR-015\n@prd: PRD-016:FEATURE-003\n@ears: EARS-012:EVENT-002\n@bdd: BDD-015:scenario-place-order\n@adr: ADR-033\n@sys: SYS-012:PERF-001\n@req: REQ-045:interface-spec\n@impl: IMPL-003:phase2  # Optional\n@ctr: CTR-005  # Optional",
    },
    "TASKS": {
        "layer": 11,
        "required_tags": "`@brd` through `@spec`",
        "tag_count": "8-10",
        "description": "Implementation Tasks Document",
        "example_tags": "@brd: BRD-009:FR-015\n@prd: PRD-016:FEATURE-003\n@ears: EARS-012:EVENT-002\n@bdd: BDD-015:scenario-place-order\n@adr: ADR-033\n@sys: SYS-012:PERF-001\n@req: REQ-045:interface-spec\n@impl: IMPL-003:phase2\n@ctr: CTR-005\n@spec: SPEC-018",
    },
    "TASKS_PLANS": {
        "layer": 12,
        "required_tags": "`@brd` through `@tasks`",
        "tag_count": "9-11",
        "description": "Implementation Session Plans",
        "example_tags": "@brd: BRD-009:FR-015\n@prd: PRD-016:FEATURE-003\n@ears: EARS-012:EVENT-002\n@bdd: BDD-015:scenario-place-order\n@adr: ADR-033\n@sys: SYS-012:PERF-001\n@req: REQ-045:interface-spec\n@impl: IMPL-003:phase2\n@ctr: CTR-005\n@spec: SPEC-018\n@tasks: TASKS-018:task-3",
    },
}


def generate_tag_section(artifact_type: str) -> str:
    """Generate the cumulative tagging section for a specific artifact type."""
    config = LAYER_CONFIGS[artifact_type]

    section = f"""---

## 2. Required Tags (Cumulative Tagging Hierarchy - Layer {config['layer']})

### 2.1 Tag Requirements for {artifact_type} Artifacts

**Layer**: {config['layer']}
**Artifact Type**: {artifact_type} ({config['description']})
**Required Tags**: {config['required_tags']}
**Tag Count**: {config['tag_count']}

### 2.2 Tag Format

```markdown
"""

    # Add tag format example based on layer
    if config['layer'] == 1:
        section += "# BRD is Layer 1 - no upstream tags required\n"
    else:
        section += f"{config['example_tags']}\n"

    section += """```

**Format Rules**:
- Prefix: `@` symbol
- Artifact Type: lowercase
- Separator: colon `:` after artifact type
- Document ID: `TYPE-NNN` format
- Requirement ID: specific requirement/section identifier
- Multiple Values: comma-separated

### 2.3 Example: {artifact_type} with Required Tags

```markdown
"""

    # Add concrete example
    if config['layer'] == 1:
        section += f"""# {artifact_type}-009: Broker Integration Business Requirements

## 7. Traceability

### 7.1 Upstream Sources

**Required Tags** (Cumulative Tagging Hierarchy - Layer {config['layer']}):
- None (BRD is top-level artifact)

**Strategic Source**: Market Analysis Report Section 4.2 - Broker Integration Requirements
```"""
    else:
        section += f"""# {artifact_type}-XXX: [Document Title]

## 7. Traceability

### 7.1 Upstream Sources

**Required Tags** (Cumulative Tagging Hierarchy - Layer {config['layer']}):
```markdown
{config['example_tags']}
```
```"""

    section += f"""

### 2.4 Validation Rules

1. **Required**: Each {artifact_type} MUST include all required upstream tags
2. **Format Compliance**: All tags must follow `@type: DOC-ID:REQ-ID` format
3. **Valid References**: All referenced documents and requirements must exist
4. **No Gaps**: Cannot skip intermediate layers in the cumulative chain

### 2.5 Tag Discovery

{artifact_type} tags can be discovered automatically:
```bash
# Find all {artifact_type}s and their upstream tags
python scripts/extract_tags.py --type {artifact_type} --show-all-upstream
```

---
"""

    return section


def main():
    """Generate tag sections for each artifact type."""
    base_dir = Path(__file__).parent.parent

    print("Cumulative Tagging Sections for Traceability Matrix Templates")
    print("=" * 70)

    for artifact_type in LAYER_CONFIGS.keys():
        print(f"\n{'=' * 70}")
        print(f"ARTIFACT TYPE: {artifact_type} (Layer {LAYER_CONFIGS[artifact_type]['layer']})")
        print(f"{'=' * 70}")
        print(generate_tag_section(artifact_type))


if __name__ == "__main__":
    main()
