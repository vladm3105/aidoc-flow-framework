# doc-spec - Quick Reference

**Skill ID:** doc-spec
**Layer:** 9 (Technical Specifications)
**Purpose:** Create implementation-ready specifications in YAML format

## Quick Start

```bash
# Invoke skill
skill: "doc-spec"

# Common requests
- "Create technical specification from REQ-001"
- "Generate implementation-ready SPEC"
- "Document Layer 9 specification for validation service"
```

## What This Skill Does

1. Create 100% implementation-ready specifications
2. Define modules, functions, and algorithms
3. Specify interfaces and data models (with CTR references)
4. Document error handling and configuration
5. Define testing, deployment, and monitoring requirements

## Output Location (Nested Folder - MANDATORY)

```
docs/09_SPEC/SPEC-NN_{slug}/SPEC-NN_{slug}.yaml
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

## Required Sections (MVP - 8 Numbered + 2 Appendices)

1. Document Control, 2. Traceability, 3. Component Overview, 4. Technical Design
5. Implementation Logic, 6. Configuration, 7. Non-Functional Requirements, 8. Quality Gates
Appendix A: Glossary, Appendix B: References

## Upstream/Downstream

```
BRD through REQ/IMPL/CTR → SPEC → TASKS → Code
```

## Quick Validation

- [ ] Pure YAML format (not markdown)
- [ ] cumulative_tags section with 7-9 upstream tags
- [ ] All modules have file paths
- [ ] All functions have signatures and algorithms
- [ ] contract_ref links to CTR (if Layer 8 created)
- [ ] 100% implementation-ready (no ambiguity)

## Nested Folder Rule (MANDATORY)

ALL SPEC documents MUST use nested folders:
```
docs/09_SPEC/SPEC-NN_{slug}/SPEC-NN_{slug}.yaml
```

Invalid: `docs/09_SPEC/SPEC-01_api.yaml` (not in nested folder)
Valid: `docs/09_SPEC/SPEC-01_api/SPEC-01_api.yaml`

## Template Location

```
ai_dev_ssd_flow/09_SPEC/SPEC-MVP-TEMPLATE.md    # Human workflow
ai_dev_ssd_flow/09_SPEC/SPEC-MVP-TEMPLATE.yaml  # Autopilot workflow
```

## Related Skills

- `doc-req` - Atomic requirements (upstream)
- `doc-ctr` - Data contracts (upstream, optional)
- `doc-tasks` - Task breakdown (downstream)
