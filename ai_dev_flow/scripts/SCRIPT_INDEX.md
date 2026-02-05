---
title: "Script Index"
description: "Comprehensive registry of all scripts in the AI Dev Flow framework"
---

# Script Index

This index lists all scripts available in the framework, categorized by logical layer and purpose.

## Core Orchestration (root/scripts)

| Script | Purpose |
|--------|---------|
| `validate_all.py` | **Main Entry Point**. Runs validators for specific layers or the entire project. |
| `validate_cross_document.py` | Validates inter-document consistency (links, tags, dependencies). |
| `validate_traceability_matrix.py` | Validates matrix files against actual documents. |
| `generate_traceability_matrix.py` | Generates traceability matrices from document headers. |
| `update_traceability_matrix.py` | incrementally updates matrix files. |

## Utilities & Cross-Document Validators (root/scripts)

| Script | Purpose |
|--------|---------|
| `validate_documentation_paths.py` | Validates relative paths and image links in markdown. |
| `validate_links.py` | Checks validity of internal links. |
| `validate_tags_against_docs.py` | Verifies cumulative usage of tags across documents. |
| `validate_diagram_consistency.py` | Checks if diagrams match prose content (heuristic). |
| `validate_terminology.py` | Enforces consistent terminology usage. |
| `validate_counts.py` | Validates numbered lists match claimed counts (e.g. "3 steps"). |
| `validate_forward_references.py` | Prevents premature references to downstream layers. |
| `validate_schema_sync.py` | Checks sync between schemas and templates. |


## Layer-Specific Validators

Each layer has dedicated validators located in `0X_LAYER/scripts/`.

### Layer 1: Business Requirements (BRD)
- `01_BRD/scripts/validate_brd_quality_score.sh`: **Primary Quality Gate**. Checks file sizes, formatting, and placeholder text.
- `01_BRD/scripts/validate_brd.py`: Python-based structural validation (called by quality score script).

### Layer 2: Product Requirements (PRD)
- `02_PRD/scripts/validate_prd_quality_score.sh`: **Primary Quality Gate**.
- `02_PRD/scripts/validate_prd.py`: Structural validation.

### Layer 3: Engineering Requirements (EARS)
- `03_EARS/scripts/validate_ears_quality_score.sh`: **Primary Quality Gate**.
- `03_EARS/scripts/validate_ears.py`: Syntax validator for EARS patterns.

### Layer 4: Behavior Driven Development (BDD)
- `04_BDD/scripts/validate_bdd_quality_score.sh`: **Primary Quality Gate**.
- `04_BDD/scripts/validate_bdd.py`: Gherkin syntax validator.

### Layer 5: Architecture Decisions (ADR)
- `05_ADR/scripts/validate_adr_quality_score.sh`: **Primary Quality Gate**.
- `05_ADR/scripts/validate_adr.py`: Status and formatting validator.

### Layer 6: System Architecture (SYS)
- `06_SYS/scripts/validate_sys_quality_score.sh`: **Primary Quality Gate**.
- `06_SYS/scripts/validate_sys.py`: Section and prompt validation.

### Layer 7: Atomic Requirements (REQ)
- `07_REQ/scripts/validate_req_quality_score.sh`: **Primary Quality Gate**. Validates 12-section format.

### Layer 8: Contracts (CTR)
- `08_CTR/scripts/validate_ctr_quality_score.sh`: **Primary Quality Gate**. Validates API/Data schemas.

### Layer 9: Specifications (SPEC)
- `09_SPEC/scripts/validate_spec_quality_score.sh`: **Primary Quality Gate**. Validates YAML specs.
- `09_SPEC/scripts/validate_spec.py`: Python usage of SPEC schema validation.

### Layer 10: Tasks (TASKS)
- `11_TASKS/scripts/validate_tasks_quality_score.sh`: **Primary Quality Gate**. Validates task breakdown and linking.

## Autopilot & CI/CD
Located in `AUTOPILOT/scripts/`:
- `mvp_autopilot.py`: Automated pipeline runner.
- `validate_quality_gates.sh`: CI/CD gate checker.
- `validate_metadata.py`: strict metadata validation.
