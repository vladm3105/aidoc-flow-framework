---
title: "Validation and Traceability Scripts"
tags:
  - index-document

Consumer onboarding guide:

- `governance/setup/PRECOMMIT_HOOK_LIBRARY_CONSUMER_GUIDE.md`
  - shared-architecture
custom_fields:
  document_type: readme
  priority: shared
---

<!-- markdownlint-disable MD009 MD022 MD025 MD030 MD031 MD032 MD037 MD040 MD060 -->

# Validation and Traceability Scripts

**[WARN] IMPORTANT: Layer-specific scripts have moved!**

Scripts that validate specific document types (BRD, PRD, etc.) have been moved to their respective layer directories (e.g., `01_BRD/scripts/`).

** See [SCRIPT_INDEX.md](SCRIPT_INDEX.md) for the complete location registry.**

This directory (`scripts/`) now contains only:
1.  **Core Orchestrators**: Scripts that run across the entire project (`validate_all.py`).
2.  **Shared Validators**: Logic used by multiple layers (`validate_cross_document.py`).
3.  **Traceability Tools**: Matrix generation and validation (`generate_traceability_matrix.py`).
4.  **Tag Extraction**: Extract traceability tags to JSON (`extract_tags.py`).
5.  **File Utilities**: Check file sizes against limits (`lint_file_sizes.sh`).
6.  **BRD Naming Guardrails**: Validate standardized BRD element type codes (`validate_standardized_element_codes.py`).

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

### 4. `extract_tags.py`

Extracts traceability tags (@brd, @prd, @req, etc.) from source code, documentation, and test files.

**Usage:**
```bash
# Extract tags to JSON
python3 extract_tags.py --source src/ docs/ tests/ --output docs/generated/tags.json

# Validate tag format only
python3 extract_tags.py --validate-only

# Extract specific artifact type
python3 extract_tags.py --type REQ --show-all-upstream
```

### 5. `lint_file_sizes.sh`

Checks documentation files against size limits (target: 800 lines, max: 1200 lines).

**Usage:**
```bash
# Check current directory
./lint_file_sizes.sh

# Check specific directory
./lint_file_sizes.sh ai_dev_ssd_flow/
```

### 6. `validate_standardized_element_codes.py`

Validates BRD element IDs against standardized element type codes and section-element mapping rules.

Primary orchestration path for enforcement is the BRD wrapper:
- `ai_dev_ssd_flow/01_BRD/scripts/validate_brd_wrapper.sh ... --skip-advisory`
- The wrapper invokes this script as its first core blocking check.

**Usage:**
```bash
# Validate BRD files under ai_dev_ssd_flow/01_BRD
python3 validate_standardized_element_codes.py --strict

# Validate from repository root
python3 ai_dev_ssd_flow/scripts/validate_standardized_element_codes.py --strict
```

**Enforcement points:**
- Local pre-commit hook via `.pre-commit-config.yaml` (wrapper core mode)
- CI jobs in `.github/workflows/ci.yml` and `.github/workflows/sdd-artifact-validation.yml` (wrapper core mode)

### 7. BRD Hook Entry Scripts (`01_BRD/scripts/`)

Reusable BRD hook wrappers for projects that consume framework validation rules.

| Script | Purpose |
|--------|---------|
| `../01_BRD/scripts/brd_standardized_element_codes_hook.sh` | Run standardized BRD element code validation for a target BRD root |
| `../01_BRD/scripts/claude_brd_skill_audit_hook.sh` | Run optional manual Claude `/doc-brd-audit` on changed BRD files |

Framework template config:
- `governance/templates/pre-commit-config.framework-library.yaml`

### 7a. All-Layer Matrix Hook (`pre_commit_hooks/`)

The all-layer matrix hook is the canonical project pre-commit orchestration entrypoint:

- `ai_dev_ssd_flow/scripts/pre_commit_hooks/sdd_layer_quality_matrix_hook.sh docs`
- `ai_dev_ssd_flow/scripts/pre_commit_hooks/sdd_layer_quality_matrix_hook.sh docs --changed-only`

Behavior notes:
- Defaults `DOCS_ROOT` to `docs` when omitted.
- Enforces project-artifact scope and rejects `ai_dev_ssd_flow` as `DOCS_ROOT`.
- In `--changed-only` mode, targets only touched layers/modules/files.

### 7b. BRD Section-Based Handling

Current BRD wrapper/gate behavior for section-based BRD modules:

- Wrapper auto-detects section-based BRD roots (for example `BRD-01.0_index.md`) and skips monolithic structural validation in that mode.
- BRD quality gate excludes companion report artifacts (`*.A_audit_report*`, `*.R_review_report*`, `*.F_fix_report*`, `*.V_validation_report*`).
- Diagram contract checks are skipped for section-based BRD layout in BRD Layer 1 quality gate mode.

### 8. PRD Wrapper Entry Script (`02_PRD/scripts/`)

Canonical PRD validation entrypoint for local hooks, automation, and orchestration.

Primary orchestration path for enforcement is the PRD wrapper:
- `ai_dev_ssd_flow/02_PRD/scripts/prd_core_wrapper_hook.sh ai_dev_ssd_flow/02_PRD`
- The wrapper runs blocking core checks first, then optional advisory checks.

**Enforcement points:**
- Local pre-commit hook via `.pre-commit-config.yaml` (`prd-core-wrapper`)
- `validate_all.py` layer execution for PRD (`--skip-advisory` wrapper mode)

### 9. PRD Hook Entry Scripts (`02_PRD/scripts/`)

Reusable PRD hook wrappers for projects that consume framework validation rules.

| Script | Purpose |
|--------|---------|
| `../02_PRD/scripts/prd_core_wrapper_hook.sh` | Run canonical PRD core checks (wrapper in `--skip-advisory` mode) |
| `../02_PRD/scripts/prd_quality_gate_hook.sh` | Backward-compatible alias for manual PRD core quality gate runs |
| `../02_PRD/scripts/prd_standardized_element_codes_hook.sh` | Run strict PRD standardized element type code checks |
| `../02_PRD/scripts/prd_legacy_pattern_hook.sh` | Detect legacy PRD element ID patterns in target PRD root |

### 10. EARS Hook Entry Scripts (`03_EARS/scripts/`)

Reusable EARS hook wrappers for projects that consume framework validation rules.

| Script | Purpose |
|--------|---------|
| `../03_EARS/scripts/ears_core_validator_hook.sh` | Run canonical EARS validator over a target EARS root |
| `../03_EARS/scripts/ears_quality_gate_hook.sh` | Run EARS corpus quality gate checks for Layer 3 → Layer 4 transition |
| `../03_EARS/scripts/ears_ready_score_hook.sh` | Validate template-versioned EARS readiness score thresholds |

### 11. BDD Hook Entry Scripts (`04_BDD/scripts/`)

Reusable BDD hook wrappers for projects that consume framework validation rules.

| Script | Purpose |
|--------|---------|
| `../04_BDD/scripts/bdd_core_validator_hook.sh` | Run canonical BDD validator over a target BDD root |
| `../04_BDD/scripts/bdd_quality_gate_hook.sh` | Run BDD corpus quality gate checks before Layer 4 → Layer 5 transition |
| `../04_BDD/scripts/bdd_adr_ready_score_hook.sh` | Validate template-versioned BDD ADR-ready score thresholds |

### 12. ADR Hook Entry Scripts (`05_ADR/scripts/`)

Reusable ADR hook wrappers for projects that consume framework validation rules.

| Script | Purpose |
|--------|---------|
| `../05_ADR/scripts/adr_core_validator_hook.sh` | Run canonical ADR validator over a target ADR root |
| `../05_ADR/scripts/adr_quality_gate_hook.sh` | Run ADR corpus quality gate checks before Layer 5 → Layer 6 transition |
| `../05_ADR/scripts/adr_sys_ready_score_hook.sh` | Validate template-versioned ADR SYS-ready score thresholds |

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
| TASKS | `11_TASKS/scripts/` |

See [SCRIPT_INDEX.md](SCRIPT_INDEX.md) for details on specific scripts in each folder.

---

## PROJECT Model v2.2 Scripts

The following scripts support the SDD Project Model v2.2 methodology for sprint integration,
drift detection, and change management. See [PROJECT/SETUP_GUIDE.md](../PROJECT/SETUP_GUIDE.md).

### 6. `tasks_to_github.py`

Converts TASKS YAML to GitHub Issues with Project V2 board integration.

**Usage:**
```bash
python3 tasks_to_github.py \
  --tasks-file docs/11_TASKS/TASKS-01.yaml \
  --repo owner/repo \
  --project-number 31 \
  --dry-run
```

### 7. `drift_check.py`

Detects documentation drift by comparing artifact dates with GitHub issue close dates.

**Usage:**
```bash
python3 drift_check.py \
  --sdd-root docs/ \
  --repo owner/repo \
  --max-age-days 14 \
  --report tmp/drift_report.md
```

### 8. `validate_artifact.py`

Unified artifact validation with 4-Gate system integration.

**Usage:**
```bash
# Validate single artifact
python3 validate_artifact.py --path docs/BRD/BRD-01.md --strict

# Validate with gate check
python3 validate_artifact.py --path docs/BRD/BRD-01.md --gate GATE-01

# Detect affected gates
python3 validate_artifact.py --path docs/ --detect-gates
```

### 9. `chg_generator.py`

Generates CHG (Change Request) documents with 4-Gate validation requirements.

**Usage:**
```bash
python3 chg_generator.py \
  --description "Add email localization support" \
  --affected-layers 2,9,11 \
  --output docs/CHG/
```

### 10. `sprint0_setup.py`

Sprint 0 checklist generation and artifact readiness validation.

**Usage:**
```bash
# Check artifact readiness
python3 sprint0_setup.py --docs-root docs/ --check-readiness

# Create Sprint 0 GitHub issues
python3 sprint0_setup.py --repo owner/repo --create-issues
```

### 11. `raci_generator.py`

Generates RACI matrix from PROJECT_MODEL configuration.

**Usage:**
```bash
python3 raci_generator.py \
  --output docs/RACI_MATRIX.md \
  --format markdown \
  --validate
```

### 12. `layer_selector.py`

Decision framework for determining which SDD layers are needed.

**Usage:**
```bash
# Interactive decision tree
python3 layer_selector.py --interactive

# Automated classification
python3 layer_selector.py --work-type "bug fix"

# Show decision matrix
python3 layer_selector.py --show-matrix
```

---

## Dependencies

**Core Scripts** (existing):
```bash
pip install pyyaml
```

**PROJECT Model Scripts** (additional):
```bash
pip install -r requirements-project.txt
# Includes: PyGithub, click, rich, requests, python-dateutil
```
