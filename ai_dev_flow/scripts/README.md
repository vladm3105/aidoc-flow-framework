---
title: "Validation and Traceability Scripts"
tags:
  - index-document
  - shared-architecture
custom_fields:
  document_type: readme
  priority: shared
---

# Validation and Traceability Scripts

**⚠️ IMPORTANT: Layer-specific scripts have moved!**

Scripts that validate specific document types (BRD, PRD, etc.) have been moved to their respective layer directories (e.g., `01_BRD/scripts/`).

**👉 See [SCRIPT_INDEX.md](SCRIPT_INDEX.md) for the complete location registry.**

This directory (`scripts/`) now contains only:
1.  **Core Orchestrators**: Scripts that run across the entire project (`validate_all.py`).
2.  **Shared Validators**: Logic used by multiple layers (`validate_cross_document.py`).
3.  **Traceability Tools**: Matrix generation and validation (`generate_traceability_matrix.py`).

## Core Scripts

### 1. `validate_all.py` (The Orchestrator)

The main entry point for validation. It calls the appropriate layer-specific "Quality Gate" scripts.

**Usage:**
```bash
# Validate everything
python3 validate_all.py --all

# Validate specific layer
python3 validate_all.py --layer BRD
```

### 2. `generate_traceability_matrix.py`

Scans document headers to build traceability matrices.

**Usage:**
```bash
python3 generate_traceability_matrix.py --type REQ --input ../07_REQ --output ../07_REQ/TRACEABILITY_MATRIX_REQ.md
```

### 3. `validate_cross_document.py`

Ensures links and dependencies between documents are valid.

**Usage:**
```bash
python3 validate_cross_document.py --full --strict
```

## Layer-Specific Validation

To run validation for a specific layer manually, use the scripts in that layer's folder. 
**Note:** `validate_all.py` is the recommended way to run these.

| Layer | Script Location |
|-------|-----------------|
| BRD | `01_BRD/scripts/` |
| PRD | `02_PRD/scripts/` |
| EARS | `03_EARS/scripts/` |
| BDD | `04_BDD/scripts/` |
| ADR | `05_ADR/scripts/` |
| SYS | `06_SYS/scripts/` |
| REQ | `07_REQ/scripts/` |
| CTR | `08_CTR/scripts/` |
| SPEC | `09_SPEC/scripts/` |
| TASKS | `10_TASKS/scripts/` |

See [SCRIPT_INDEX.md](SCRIPT_INDEX.md) for details on specific scripts in each folder.
