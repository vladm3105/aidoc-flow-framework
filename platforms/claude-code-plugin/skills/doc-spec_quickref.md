# doc-spec - Quick Reference

**Skill ID:** doc-spec
**Layer:** 6 (Technical Specifications)
**Purpose:** Create implementation-ready specifications in YAML format

## Quick Start

```bash
# Invoke skill
skill: "doc-spec"

# Common requests
- "Create technical specification from ADR-03"
- "Generate implementation-ready SPEC"
- "Document Layer 6 specification for validation service"
```

## What This Skill Does

1. Create 100% implementation-ready specifications
2. Define modules, functions, and algorithms
3. Specify interfaces and data models
4. Document error handling and configuration
5. Define testing, deployment, and monitoring requirements

## Output Location (Nested Folder - MANDATORY)

```
docs/06_SPEC/SPEC-NN_{slug}/SPEC-NN_{slug}.yaml
```

## Format: Pure YAML (NOT Markdown)

```yaml
metadata:
  spec_id: SPEC-01
  title: "Service Specification"
  version: "1.0.0"

cumulative_tags:
  brd: ["BRD.01.01.0a13"]
  prd: ["PRD.01.07.1dbc"]
  ears: ["EARS.01.03.5e2a"]
  bdd: ["BDD.01.14.8f4c"]
  adr: ["ADR-03"]

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

## Required Sections (8 Numbered + 2 Appendices)

1. Document Control, 2. Component Overview, 3. Interfaces, 4. Data Models
5. Behavior, 6. Implementation Notes, 7. Downstream TDD Contracts, 8. Traceability
Appendix A: Glossary, Appendix B: References

## Upstream/Downstream

```
BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code
```

SPEC upstream = @brd, @prd, @ears, @bdd, @adr (no SYS/REQ/CTR).

## Quick Validation

- [ ] Pure YAML format (not markdown)
- [ ] cumulative_tags section with 5 upstream tag families (@brd, @prd, @ears, @bdd, @adr)
- [ ] All modules have file paths
- [ ] All functions have signatures and algorithms
- [ ] Document ID uses `SPEC-NN` (dash notation)
- [ ] 100% implementation-ready (no ambiguity)

## Nested Folder Rule (MANDATORY)

ALL SPEC documents MUST use nested folders:
```
docs/06_SPEC/SPEC-NN_{slug}/SPEC-NN_{slug}.yaml
```

Invalid: `docs/06_SPEC/SPEC-01_api.yaml` (not in nested folder)
Valid: `docs/06_SPEC/SPEC-01_api/SPEC-01_api.yaml`

## Template Location

```
framework/layers/06_SPEC/SPEC-TEMPLATE.yaml   # Specification template
framework/layers/06_SPEC/README.md            # Layer overview
```

## Related Skills

- `doc-adr` - Architecture decisions (upstream)
- `doc-tdd` - Test definitions (downstream)
- `doc-iplan` - Implementation plan (downstream)
