---
title: "BDD-00: BDD Index"
tags:
  - index-document
  - layer-4-artifact
  - shared-architecture
custom_fields:
  document_type: index-template
  artifact_type: BDD
  layer: 4
  priority: shared
  last_updated: "YYYY-MM-DD"
---

# BDD-00: Behavior-Driven Development Index

> **Index template.** Copy this file to `BDD-00_index.md` in a project and
> populate the registry as BDD documents are created.

## Position in Document Workflow

```mermaid
flowchart LR
    EARS[EARS - L3] --> BDD[BDD - L4]
    BDD --> ADR[ADR - L5]

    style BDD fill:#c8e6c9,stroke:#2e7d32,stroke-width:3px
```

**Layer**: 4 (Behavior-Driven Development Layer)
**Upstream**: BRD, PRD, EARS
**Downstream**: ADR (Architecture Decision Records, Layer 5)
**Traceability chain**: BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code

### BDD Purpose

- **Input**: BRD, PRD, EARS (formal requirements)
- **Output**: YAML-structured Given-When-Then scenarios with spec_trace links to downstream SPEC
- **Consumer**: All downstream artifacts (ADR, SPEC, TDD, Code) must satisfy BDD scenarios

---

## File Format

BDD uses **`.yaml` files** (unified YAML template pattern across all layers).

**Template**: [BDD-TEMPLATE.yaml](./BDD-TEMPLATE.yaml) — single source of truth

---

## Allocation Rules

- **Numbering**: Allocate sequentially starting at `01` (e.g., `BDD-01`, `BDD-02`)
- **Keep numbers stable**: Never reuse or renumber
- **Filename**: `BDD-NN_{descriptive_slug}.yaml`
- **One feature per file**: Each BDD file covers one primary feature or capability
- **Necessary-upstream tag**: Include `@ears` (BDD's `required_tags`); `@brd`/`@prd` optional provenance only
- **BDD-Ready score**: >=90/100 required before downstream ADR generation

---

## Document Registry

| ID | Feature/Suite | Sourced From | Status | Last Updated |
|----|---------------|--------------|--------|--------------|
| - | - | - | - | No BDD documents created yet |

## Planned

| ID | Feature | Source (03_EARS) | Priority | Notes |
|----|---------|-------------------|----------|-------|
| BDD-XX | … | EARS-YY | High/Med/Low | … |

---

## Usage Guidelines

### Creating a New BDD Document

1. **Generate from template**: Copy `BDD-TEMPLATE.yaml` into a new `BDD-NN` file
2. **Assign sequential ID**: `BDD-01`, `BDD-02`, etc.
3. **Write tag section**: Include `@ears` (the required necessary-upstream tag)
4. **Define scenarios**: Given/When/Then; include success path, error handling, edge cases
5. **Update this index**: Add entry to the document registry

### Tagging Convention

```yaml
tags:
  - "@brd: BRD.NN.SS.xxxx"
  - "@prd: PRD.NN.SS.xxxx"
  - "@ears: EARS.NN.SS.xxxx"  # element-level (GD-03); a Feature realizing several
                              # EARS pipe-delimits them: "@ears: E… | @ears: E…"
```

### Scenario Organization

1. **Success Path Scenarios**: Happy path acceptance criteria
2. **Error Handling Scenarios**: Negative tests and error conditions
3. **Edge Case Scenarios**: Boundary conditions and corner cases
4. **Integration Scenarios**: Cross-component interactions

---

## Validation Checklist

- [ ] All BDD files follow naming: `BDD-NN_{slug}.yaml`
- [ ] All BDD files have the necessary-upstream tag (`@ears`)
- [ ] All BDD files have upstream links (EARS)
- [ ] All BDD files have downstream links (ADR)
- [ ] All requirements have corresponding BDD scenarios
- [ ] All BDD scenarios are executable (valid Gherkin syntax)
- [ ] This index is up-to-date with all BDD files
- [ ] BDD-Ready score >=90/100 confirmed

---

## Traceability

### Upstream Sources

| Source Type | Document ID | Relationship |
|-------------|-------------|--------------|
| BRD | BRD-NN | Business requirements driving acceptance criteria |
| PRD | PRD-NN | Product requirements defining features |
| EARS | EARS-NN | Event-driven specifications formalizing behavior |

### Downstream Consumers

| Consumer Type | Document ID | Relationship |
|---------------|-------------|--------------|
| ADR | ADR-NN | Architecture decisions must satisfy BDD scenarios |
| SPEC | SPEC-NN | Technical specifications implement BDD acceptance criteria |
| TDD | TDD-NN | Test cases map to BDD scenarios |
| IPLAN | IPLAN-NN | Execution plans reference BDD scenario coverage |

---

## Related Documents

- **Template**: [BDD-TEMPLATE.yaml](./BDD-TEMPLATE.yaml)
- **README**: [README.md](./README.md) — BDD purpose, structure, and best practices
- **Upstream**: [03_EARS](../03_EARS/) — Formal requirements
- **Downstream**: [05_ADR](../05_ADR/) — Architecture decisions

---

**Last Updated**: YYYY-MM-DD
**Maintainer**: [Project Team]
