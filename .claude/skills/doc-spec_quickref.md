# doc-spec - Quick Reference

**Skill ID:** doc-spec
**Layer:** 10 (Technical Specifications)
**Purpose:** Create implementation-ready specifications in YAML format

## Quick Start

```bash
# Invoke skill
skill: "doc-spec"

# Common requests
- "Create technical specification from REQ-001"
- "Generate implementation-ready SPEC"
- "Document Layer 10 specification for validation service"
```

## What This Skill Does

1. Create 100% implementation-ready specifications
2. Define modules, functions, and algorithms
3. Specify interfaces and data models (with CTR references)
4. Document error handling and configuration
5. Define testing, deployment, and monitoring requirements

## Output Location

```
ai_dev_flow/SPEC/SPEC-NNN_{slug}.yaml
```

## Format: Pure YAML (NOT Markdown)

```yaml
metadata:
  spec_id: SPEC-001
  title: "Service Specification"
  version: "1.0.0"

cumulative_tags:
  brd: ["BRD-001:section-3"]
  prd: ["PRD-001:feature-2"]
  # ... all upstream tags

architecture:
  pattern: "layered"
  layers:
    - name: "controller"
      technology: "FastAPI"

implementation:
  modules:
    - name: "services/validator.py"
      purpose: "Business logic"
  functions:
    - name: "validate_order"
      signature: "async def validate_order()"
      algorithm:
        - "Step 1: Validate input"
        - "Step 2: Process logic"
```

## Required Sections (12)

1. metadata, 2. cumulative_tags, 3. overview, 4. architecture
5. interfaces, 6. implementation, 7. error_handling, 8. configuration
9. testing, 10. deployment, 11. monitoring, 12. traceability

## Upstream/Downstream

```
BRD through REQ/IMPL/CTR → SPEC → TASKS, IPLAN, Code
```

## Quick Validation

- [ ] Pure YAML format (not markdown)
- [ ] cumulative_tags section with 7-9 upstream tags
- [ ] All modules have file paths
- [ ] All functions have signatures and algorithms
- [ ] contract_ref links to CTR (if Layer 9 created)
- [ ] 100% implementation-ready (no ambiguity)

## Template Location

```
ai_dev_flow/SPEC/SPEC-TEMPLATE.yaml
```

## Related Skills

- `doc-req` - Atomic requirements (upstream)
- `doc-ctr` - Data contracts (upstream, optional)
- `doc-tasks` - Task breakdown (downstream)
