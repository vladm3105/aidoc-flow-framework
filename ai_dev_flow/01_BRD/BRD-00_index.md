---
title: "BRD-00: Business Requirements Document Index"
tags:
  - brd
  - index
  - layer-1-artifact
custom_fields:
  document_type: brd-index
  artifact_type: BRD-INDEX
  layer: 1
  last_updated: "2026-02-10T22:30:00"
---

# BRD-00: Business Requirements Document Index

Master index of all Business Requirements Documents for the project.

---

## Quick Start

### Generate New BRD

```bash
# From reference documents (primary)
/doc-brd-autopilot docs/00_REF/foundation/F1_Technical_Specification.md

# From REF directory (alternative)
/doc-brd-autopilot REF/

# Interactive mode (prompts for input)
/doc-brd-autopilot
```

### Review Existing BRD

```bash
/doc-brd-reviewer BRD-01
```

### Fix BRD Issues

```bash
/doc-brd-fixer BRD-01
```

---

## Document Registry

| BRD ID | Module | Type | Status | PRD-Ready | Location |
|--------|--------|------|--------|-----------|----------|
| - | - | - | - | - | No BRDs created yet |

---

## Module Categories

### Foundation Modules (F1-F7)

Domain-agnostic, reusable infrastructure modules.

| ID | Module Name | BRD | Status |
|----|-------------|-----|--------|
| F1 | Identity & Access Management | Pending | - |
| F2 | Session Management | Pending | - |
| F3 | Observability | Pending | - |
| F4 | SecOps | Pending | - |
| F5 | Events | Pending | - |
| F6 | Infrastructure | Pending | - |
| F7 | Configuration | Pending | - |

### Domain Modules (D1-D7)

Business-specific modules (customize per project).

| ID | Module Name | BRD | Status |
|----|-------------|-----|--------|
| D1 | [Domain Module 1] | Pending | - |
| D2 | [Domain Module 2] | Pending | - |
| D3 | [Domain Module 3] | Pending | - |
| D4 | [Domain Module 4] | Pending | - |
| D5 | [Domain Module 5] | Pending | - |
| D6 | [Domain Module 6] | Pending | - |
| D7 | [Domain Module 7] | Pending | - |

---

## Input Sources

BRD autopilot uses these source directories (in priority order):

| Priority | Location | Content |
|----------|----------|---------|
| 1 | `docs/00_REF/` | Technical specifications, gap analysis |
| 2 | `REF/` | Alternative reference documents |
| 3 | `docs/` | Existing project documentation |
| 4 | User Prompts | Interactive input (fallback) |

---

## Quick Links

- **Glossary**: [BRD-00_GLOSSARY.md](BRD-00_GLOSSARY.md)
- **Reference Documents**: [00_REF](../00_REF/)
- **PRD Layer**: [02_PRD](../02_PRD/)
- **Templates**: [BRD-MVP-TEMPLATE.md](../../ai_dev_flow/01_BRD/BRD-MVP-TEMPLATE.md)

---

## Statistics

| Metric | Value |
|--------|-------|
| Total BRDs | 0 |
| Foundation Modules | 0/7 |
| Domain Modules | 0/7 |
| Average PRD-Ready Score | - |

---

## Planned BRDs

| ID | Title | Priority | Target Date | Notes |
|----|-------|----------|-------------|-------|
| BRD-01 | [First module] | High | TBD | - |

---

## Allocation Rules

- **Numbering**: Allocate sequentially starting at `01`; keep numbers stable
- **Foundation**: F1-F7 modules use BRD-01 through BRD-07
- **Domain**: D1-D7 modules use BRD-08 through BRD-14 (or custom numbering)
- **Feature BRDs**: Continue sequence from last allocated number

---

*Last Updated: 2026-02-10T22:30:00*
