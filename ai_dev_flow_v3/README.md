# SDD v3 — Streamlined Specification-Driven Development

## Overview

SDD v3 is a **7-layer documentation-to-code framework** that produces implementation-ready technical specifications from business requirements. Each layer is a single YAML document type with cumulative traceability.

```
BRD → PRD → EARS → BDD → ADR → TDD → SPEC → Code
```

## Why v3?

SDD v2 (14 layers) required maintaining ~40 reference documents, 20+ templates, and a 14-deep traceability chain. v3 collapses this to 7 document layers plus code, reducing documentation surface area by 50%.

## Layer Structure

```
ai_dev_flow_v3/
├── README.md
├── LAYER_REGISTRY.yaml             # Authoritative layer definitions
├── SPEC_DRIVEN_DEVELOPMENT_GUIDE.md
├── ID_NAMING_STANDARDS.md
├── TRACEABILITY.md
├── DIAGRAM_STANDARDS.md
├── THRESHOLD_NAMING_RULES.md
├── TESTING_STRATEGY_TDD.md
├── QUICK_REFERENCE.md
├── 01_BRD/                         # Business Requirements
│   ├── BRD-TEMPLATE.yaml
│   └── BRD-00_index.md
├── 02_PRD/                         # Product Requirements
│   ├── PRD-TEMPLATE.yaml
│   └── PRD-00_index.md
├── 03_EARS/                        # Formal Requirements
│   ├── EARS-TEMPLATE.yaml
│   └── EARS-00_index.md
├── 04_BDD/                         # Behavior-Driven Development
│   ├── BDD-TEMPLATE.yaml
│   └── BDD-00_index.md
├── 05_ADR/                         # Architecture Decision Records
│   ├── ADR-TEMPLATE.yaml
│   └── ADR-00_index.md
├── 06_TDD/                         # Test-Driven Development Guide
│   ├── TDD-TEMPLATE.yaml
│   └── TDD-00_index.md
└── 07_SPEC/                        # Technical Specification
    ├── SPEC-TEMPLATE.yaml
    └── SPEC-00_index.md
```

## Quick Start

1. **Set up**: Copy this directory to your project as `ai_dev_flow/`
2. **Create BRD**: `cp 01_BRD/BRD-TEMPLATE.yaml 01_BRD/BRD-01.yaml` and fill in business requirements
3. **Follow the chain**: Generate PRD from BRD, EARS from PRD, BDD from EARS, etc.
4. **Generate code**: SPEC is the final output — implementation-ready with test contracts from TDD

## Layer Flow

| Step | From | To | Readiness Gate |
|------|------|----|---------------|
| 1 | — | BRD | — |
| 2 | BRD | PRD | PRD-Ready >=90 |
| 3 | PRD | EARS | EARS-Ready >=90 |
| 4 | EARS | BDD | BDD-Ready >=90 |
| 5 | BDD | ADR | ADR-Ready >=90 |
| 6 | ADR | TDD | TDD-Ready >=90 |
| 7 | TDD | SPEC | CODE-Ready >=90 |

## v2 to v3 Migration

See [MIGRATION_PLAN.md](MIGRATION_PLAN.md) for detailed changes.

| v2 | v3 | Change |
|----|-----|--------|
| 14 layers | 7 layers | Cut SYS, REQ, CTR, TSPEC (42 files), TASKS, TESTS, VALIDATION |
| 42 TSPEC files | 1 TDD template | 6 test subtypes collapsed to single document |
| 5 SPEC subtypes | 1 SPEC template | CSPEC/DSPEC/UXSPEC/RISKSPEC/PROCSPEC unified |
| 14 cumulative tags | 6 cumulative tags | Traceability chain depth reduced by 57% |
