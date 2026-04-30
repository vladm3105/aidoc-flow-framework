# PLAN-001: Unified BRD Validation in UCX

## Overview

Integrate all BRD validation scripts into UCX as the single source of truth. Pre-commit hooks will invoke UCX for fast, non-AI validation.

**Scope**: BRD validation only (Phase 1). Other document types will follow the same pattern.

**Status**: Complete (v1.9.2)
**Completed**: 2026-03-11
**Version**: UCX 1.9.2

### Completion Summary

| Component | Status | Details |
|-----------|--------|---------|
| Structure Validation | ✅ Complete | 6 modules, 1,674 lines in `validators/brd/` |
| CLI Integration | ✅ Complete | `ucx validate brd` with `--tier1-only`, `--strict`, `--format json` |
| AI Review (UCR) | ✅ Complete | 9 personas, prompts, skills configured |
| AI Remediation (UCRem) | ✅ Complete | Fix proposals, templates ready |
| Pre-commit Integration | ✅ Complete | Documented in `pre-commit-config.project.yaml` |
| Documentation | ✅ Complete | README, QUICK_START, validators/README |
| Testing | ✅ Complete | Unit and integration tests present |

---

## Current State

### Scripts to Migrate: `ucx_flow_v3/01_BRD/scripts/`

| Script | Purpose | Migrate to UCX | Notes |
|--------|---------|----------------|-------|
| `validate_brd.py` | Main BRD structural validator | ✅ Yes | → `brd/structure.py` + `brd/metadata.py` |
| `validate_brd_quality_score.sh` | 10 GATE quality checks | ✅ Yes | → `brd/quality_gate.py` |
| `validate_brd_wrapper.sh` | Tiered wrapper (core + advisory) | ✅ Yes | → `UnifiedBRDValidator` orchestration |
| `brd_core_wrapper_hook.sh` | Pre-commit hook | ❌ No | Replace with `ucx validate brd --tier1-only` |
| `brd_standardized_element_codes_hook.sh` | Pre-commit hook | ❌ No | Replace with `ucx validate brd --tier1-only` |
| `brd_legacy_pattern_hook.sh` | Legacy ID detection hook | ✅ Yes | → `brd/element_codes.py` (legacy detection) |
| `claude_brd_skill_audit_hook.sh` | AI-based audit (manual) | ❌ No | Stays separate (AI-based, not validation) |
| `README.md` | Documentation | ❌ No | Update to point to UCX |

### Scripts to Migrate: `ucx_flow_v3/scripts/` (Shared)

| Script | Purpose | Migrate to UCX | Notes |
|--------|---------|----------------|-------|
| `error_codes.py` | Error code registry | ✅ Yes | → `common/error_codes.py` |
| `validate_standardized_element_codes.py` | BRD element ID validation | ✅ Yes | → `brd/element_codes.py` |
| `validate_metadata.py` | YAML frontmatter validation | ✅ Yes | → `brd/metadata.py` |
| `validate_links.py` | Internal/external link validation | ✅ Yes | → `brd/links.py` |
| `validate_forward_references.py` | @ref: tag resolution | ✅ Yes | → `brd/references.py` |
| `validate_diagram_consistency.py` | Mermaid/SVG consistency | ✅ Yes | → `brd/diagrams.py` |
| `detect_legacy_element_ids.py` | Legacy pattern detection | ✅ Yes | → `brd/element_codes.py` (legacy module) |
| `validate_terminology.py` | Glossary consistency | ✅ Yes | → `brd/quality_gate.py` (GATE-07) |
| `validate_counts.py` | Count consistency | ✅ Yes | → `brd/quality_gate.py` (GATE-03) |
| `validate_depth.py` | Depth validation | ⚠️ Review | May be PRD-specific |
| `validate_cross_document.py` | Cross-doc traceability | ⚠️ Later | Complex, multi-type validator |
| `validate_all.py` | Orchestrator | ❌ No | Replace with `ucx validate` |
| `validate_artifact.py` | Generic artifact validation | ⚠️ Later | Multi-type, move to common/ |
| `validate_documentation_paths.py` | Path validation | ⚠️ Later | Move to common/ |
| `validate_schema_sync.py` | Schema sync | ⚠️ Later | Move to common/ |
| `validate_tags_against_docs.py` | Tag validation | ⚠️ Later | Move to common/ |
| `validate_traceability_matrix.py` | Traceability matrix | ⚠️ Later | Move to common/ |
| `validate_prd_standardized_element_codes.py` | PRD element codes | ❌ No (BRD phase) | PRD migration later |

### Migration Summary

| Category | Count | Action |
|----------|-------|--------|
| **BRD-specific scripts** | 8 | 5 migrate, 3 deprecate |
| **Shared scripts (BRD)** | 8 | All migrate to UCX |
| **Shared scripts (later)** | 7 | Phase 2 migration |
| **PRD/other** | 1 | PRD migration phase |

### Scripts NOT Migrated (Remain in ucx_flow_v3)

| Script | Reason |
|--------|--------|
| `claude_brd_skill_audit_hook.sh` | AI-based, uses Claude CLI directly |
| Pre-commit hook wrappers | Replaced by `ucx validate` command |
| `validate_all.py` | Replaced by `ucx validate` orchestration |

### Validation Scripts (Duplicated in BeeLocal)

| Script | Framework Location | BeeLocal Location | Status |
|--------|-------------------|-------------------|--------|
| `validate_brd.py` | `ucx_flow_v3/01_BRD/scripts/` | `ucx_flow_v3/01_BRD/scripts/` | Identical |
| `validate_standardized_element_codes.py` | `ucx_flow_v3/scripts/` | `ucx_flow_v3/scripts/` | Identical |
| `validate_brd_wrapper.sh` | `ucx_flow_v3/01_BRD/scripts/` | `ucx_flow_v3/01_BRD/scripts/` | Identical |
| `validate_brd_quality_score.sh` | `ucx_flow_v3/01_BRD/scripts/` | `ucx_flow_v3/01_BRD/scripts/` | Identical |
| `validate_metadata.py` | `ucx_flow_v3/scripts/` | `ucx_flow_v3/scripts/` | Identical |
| `validate_links.py` | `ucx_flow_v3/scripts/` | `ucx_flow_v3/scripts/` | Identical |
| `validate_forward_references.py` | `ucx_flow_v3/scripts/` | `ucx_flow_v3/scripts/` | Identical |
| `validate_diagram_consistency.py` | `ucx_flow_v3/scripts/` | `ucx_flow_v3/scripts/` | Identical |

### Current UCX Validators (Limited)

| File | Checks |
|------|--------|
| `ucx/validators/brd.py` | Basic YAML (4 fields), element ID regex, 4 sections, traceability tags |

### Gap Analysis

| Check | UCX Built-in | Framework Scripts |
|-------|--------------|-------------------|
| YAML frontmatter | 4 fields | Full custom_fields validation |
| Element IDs | Regex only | Type codes + section mapping |
| Sections | 4 required | 18 MVP sections + profile support |
| Tags | @ref/@prd presence | Required tags + forbidden patterns |
| Quality gate | Not checked | 10+ quality checks |
| Metadata | Not checked | deliverable_type, document_type |
| Links | Not checked | Internal/external validation |
| Forward refs | Not checked | @ref: resolution |
| Diagrams | Not checked | Mermaid/SVG consistency |

---

## Target State

### Architecture (Scalable for All Layers)

```
┌─────────────────────────────────────────────────────────────────────┐
│  UCX Framework - Unified Validation Architecture                    │
│  /opt/data/docs_flow_framework/UCX/                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ucx/validators/                                                     │
│  │                                                                   │
│  ├── base.py              # BaseValidator ABC (existing)            │
│  ├── registry.py          # Validator registry (existing)          │
│  │                                                                   │
│  ├── common/              # SHARED: Cross-layer utilities           │
│  │   ├── __init__.py      # Exports                                 │
│  │   ├── error_codes.py   # Severity, ErrorCode, ERROR_REGISTRY     │
│  │   ├── file_utils.py    # File collection, companion detection    │
│  │   ├── patterns.py      # Shared regex patterns                   │
│  │   ├── frontmatter.py   # YAML parsing utilities                  │
│  │   ├── links.py         # Link validation (reusable)              │
│  │   ├── references.py    # Forward reference validation            │
│  │   ├── diagrams.py      # Diagram consistency                     │
│  │   ├── terminology.py   # Glossary/terminology checks             │
│  │   ├── traceability.py  # Cross-document traceability             │
│  │   └── quality_base.py  # Base quality gate class                 │
│  │                                                                   │
│  ├── brd/                 # L1: Business Requirements Document      │
│  │   ├── __init__.py      # UnifiedBRDValidator                     │
│  │   ├── schema.py        # BRD constants, sections, codes          │
│  │   ├── element_codes.py # BRD.NN.TT.SS + legacy detection         │
│  │   ├── structure.py     # BRD structure validation                │
│  │   ├── metadata.py      # BRD metadata validation                 │
│  │   └── quality_gate.py  # BRD 10 GATE checks                      │
│  │                                                                   │
│  ├── prd/                 # L2: Product Requirements Document       │
│  │   ├── __init__.py      # UnifiedPRDValidator                     │
│  │   ├── schema.py        # PRD constants                           │
│  │   ├── element_codes.py # PRD.NN.TT.SS validation                 │
│  │   ├── structure.py     # PRD structure validation                │
│  │   ├── metadata.py      # PRD metadata validation                 │
│  │   └── quality_gate.py  # PRD quality checks                      │
│  │                                                                   │
│  ├── ears/                # L3: EARS Requirements                   │
│  │   ├── __init__.py      # UnifiedEARSValidator                    │
│  │   ├── schema.py        # EARS syntax patterns                    │
│  │   ├── structure.py     # EARS structure                          │
│  │   ├── consistency.py   # EARS consistency checks                 │
│  │   ├── duplicates.py    # Duplicate detection                     │
│  │   └── quality_gate.py  # EARS quality checks                     │
│  │                                                                   │
│  ├── bdd/                 # L4: BDD Scenarios                       │
│  │   ├── __init__.py      # UnifiedBDDValidator                     │
│  │   ├── schema.py        # Gherkin patterns                        │
│  │   ├── structure.py     # Feature file structure                  │
│  │   ├── suite.py         # Test suite validation                   │
│  │   └── quality_gate.py  # BDD quality checks                      │
│  │                                                                   │
│  ├── adr/                 # L5: Architecture Decision Records       │
│  │   ├── __init__.py      # UnifiedADRValidator                     │
│  │   ├── schema.py        # ADR constants                           │
│  │   ├── structure.py     # ADR structure                           │
│  │   └── quality_gate.py  # ADR quality checks                      │
│  │                                                                   │
│  ├── sys/                 # L6: System Requirements                 │
│  │   ├── __init__.py      # UnifiedSYSValidator                     │
│  │   ├── schema.py        # SYS constants                           │
│  │   ├── structure.py     # SYS structure                           │
│  │   └── quality_gate.py  # SYS quality checks                      │
│  │                                                                   │
│  ├── req/                 # L7: Atomic Requirements                 │
│  │   ├── __init__.py      # UnifiedREQValidator                     │
│  │   ├── schema.py        # REQ constants                           │
│  │   ├── element_ids.py   # Requirement ID validation               │
│  │   ├── spec_readiness.py # SPEC readiness check                   │
│  │   └── quality_gate.py  # REQ quality checks                      │
│  │                                                                   │
│  ├── ctr/                 # L8: Data Contracts                      │
│  │   ├── __init__.py      # UnifiedCTRValidator                     │
│  │   ├── schema.py        # CTR constants                           │
│  │   ├── ids.py           # Contract ID validation                  │
│  │   ├── spec_readiness.py # SPEC readiness check                   │
│  │   └── quality_gate.py  # CTR quality checks                      │
│  │                                                                   │
│  ├── spec/                # L9: Technical Specifications            │
│  │   ├── __init__.py      # UnifiedSPECValidator                    │
│  │   ├── schema.py        # SPEC constants                          │
│  │   ├── structure.py     # SPEC structure                          │
│  │   ├── impl_readiness.py # Implementation readiness               │
│  │   └── quality_gate.py  # SPEC quality checks                     │
│  │                                                                   │
│  ├── tspec/               # L10: Test Specifications                │
│  │   ├── __init__.py      # UnifiedTSPECValidator                   │
│  │   ├── schema.py        # TSPEC constants                         │
│  │   ├── utest.py         # Unit test validation                    │
│  │   ├── itest.py         # Integration test validation             │
│  │   ├── ftest.py         # Functional test validation              │
│  │   ├── ptest.py         # Performance test validation             │
│  │   ├── stest.py         # Smoke test validation                   │
│  │   ├── sectest.py       # Security test validation                │
│  │   └── quality_gate.py  # TSPEC quality checks                    │
│  │                                                                   │
│  ├── tasks/               # L11: Task Breakdown                     │
│  │   ├── __init__.py      # UnifiedTASKSValidator                   │
│  │   ├── schema.py        # TASKS constants                         │
│  │   ├── structure.py     # TASKS structure                         │
│  │   └── quality_gate.py  # TASKS quality checks                    │
│  │                                                                   │
│  └── chg/                 # CHG: Change Management (cross-cutting)  │
│      ├── __init__.py      # CHGValidator                            │
│      ├── routing.py       # Change routing validation               │
│      └── gates.py         # Gate validation (01, 05, 09, 12)        │
│                                                                      │
│  ucx/cli/                                                            │
│  └── main.py              # ucx validate {type} <path>              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Layer Validation Scripts Inventory

| Layer | Type | Scripts to Migrate |
|-------|------|-------------------|
| L1 | BRD | `validate_brd.py`, `validate_brd_quality_score.sh`, `validate_brd_wrapper.sh` |
| L2 | PRD | `validate_prd.py`, `validate_prd_quality_score.sh`, `validate_prd_wrapper.sh`, `validate_prd_standardized_element_codes.py` |
| L3 | EARS | `validate_ears.py`, `validate_ears_quality_score.sh`, `validate_ears_consistency.sh`, `validate_ears_duplicates.sh` |
| L4 | BDD | `validate_bdd.py`, `validate_bdd_quality_score.sh`, `validate_bdd_suite.py` |
| L5 | ADR | `validate_adr.py`, `validate_adr_quality_score.sh` |
| L6 | SYS | `validate_sys.py`, `validate_sys_quality_score.sh` |
| L7 | REQ | `validate_req_quality_score.sh`, `validate_req_spec_readiness.py`, `validate_requirement_ids.py` |
| L8 | CTR | `validate_ctr_ids.py`, `validate_ctr_quality_score.sh`, `validate_ctr_spec_readiness.py` |
| L9 | SPEC | `validate_spec.py`, `validate_spec_quality_score.sh`, `validate_spec_implementation_readiness.py` |
| L10 | TSPEC | `validate_tspec_quality_score.sh`, `validate_utest.py`, `validate_itest.py`, `validate_ftest.py`, `validate_ptest.py`, `validate_stest.py`, `validate_sectest.py` |
| L11 | TASKS | `validate_tasks.py`, `validate_tasks_quality_score.sh` |
| - | CHG | `validate_chg_routing.py`, `validate_gate01.sh`, `validate_gate05.sh`, `validate_gate09.sh`, `validate_gate12.sh` |

### Shared Scripts → common/ Module

| Script | Target | Reused By |
|--------|--------|-----------|
| `error_codes.py` | `common/error_codes.py` | All layers |
| `validate_standardized_element_codes.py` | Per-layer `element_codes.py` | BRD, PRD |
| `validate_metadata.py` | `common/frontmatter.py` | All layers |
| `validate_links.py` | `common/links.py` | All layers |
| `validate_forward_references.py` | `common/references.py` | All layers |
| `validate_diagram_consistency.py` | `common/diagrams.py` | BRD, PRD, ADR, SYS |
| `validate_terminology.py` | `common/terminology.py` | All layers |
| `validate_counts.py` | `common/quality_base.py` | All layers |
| `validate_cross_document.py` | `common/traceability.py` | All layers |
| `validate_artifact.py` | `common/artifact.py` | All layers |
| `validate_depth.py` | `common/structure.py` | All layers |
| `validate_tags_against_docs.py` | `common/tags.py` | All layers |
| `validate_traceability_matrix.py` | `common/traceability.py` | All layers |
| `validate_schema_sync.py` | `common/schema.py` | All layers |
| `validate_documentation_paths.py` | `common/paths.py` | All layers |

### CLI Interface (All Layers)

```bash
# Unified validation command pattern
ucx validate {type} <path> [options]

# Layer-specific validation
ucx validate brd docs/01_BRD/BRD-01/          # L1: BRD
ucx validate prd docs/02_PRD/PRD-01/          # L2: PRD
ucx validate ears docs/03_EARS/EARS-01/       # L3: EARS
ucx validate bdd docs/04_BDD/                 # L4: BDD
ucx validate adr docs/05_ADR/ADR-001/         # L5: ADR
ucx validate sys docs/06_SYS/SYS-01/          # L6: SYS
ucx validate req docs/07_REQ/REQ-01/          # L7: REQ
ucx validate ctr docs/08_CTR/CTR-01/          # L8: CTR
ucx validate spec docs/09_SPEC/SPEC-01/       # L9: SPEC
ucx validate tspec docs/10_TSPEC/             # L10: TSPEC
ucx validate tasks docs/11_TASKS/TASKS-01/    # L11: TASKS

# Validate all layers
ucx validate all docs/

# Common options (all layers)
--tier1-only    # Core checks only (for pre-commit)
--strict        # Warnings as errors
--verbose       # Verbose output
--format json   # JSON output (for CI)
--check NAME    # Run specific check only

# Examples
ucx validate brd docs/01_BRD/BRD-01/ --tier1-only
ucx validate prd docs/02_PRD/ --strict --format json
ucx validate all docs/ --tier1-only
```

### Pre-commit Integration (All Layers)

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      # Layer-specific hooks
      - id: ucx-brd-validate
        name: UCX BRD Validation (Tier 1)
        entry: bash -c 'source /opt/data/docs_flow_framework/.venv/bin/activate && ucx validate brd docs/01_BRD --tier1-only'
        language: system
        files: ^docs/01_BRD/.*\.md$
        stages: [pre-commit]

      - id: ucx-prd-validate
        name: UCX PRD Validation (Tier 1)
        entry: bash -c 'source /opt/data/docs_flow_framework/.venv/bin/activate && ucx validate prd docs/02_PRD --tier1-only'
        language: system
        files: ^docs/02_PRD/.*\.md$
        stages: [pre-commit]

      # ... repeat for other layers

      # Or: Single hook for all layers
      - id: ucx-validate-all
        name: UCX Document Validation (Tier 1)
        entry: bash -c 'source /opt/data/docs_flow_framework/.venv/bin/activate && ucx validate all docs/ --tier1-only'
        language: system
        files: ^docs/.*\.md$
        stages: [pre-commit]
```

### Pre-commit Integration

```yaml
# .pre-commit-config.yaml (BeeLocal)
repos:
  - repo: local
    hooks:
      - id: ucx-brd-validate
        name: UCX BRD Validation (Tier 1)
        entry: bash -c 'source /opt/data/docs_flow_framework/.venv/bin/activate && ucx validate brd docs/01_BRD --tier1-only'
        language: system
        pass_filenames: false
        stages: [pre-commit]
```

---

## Implementation Plan

### Phase 1: Core Module Structure

**Task 1.1**: Create `ucx/validators/brd/` module

```
ucx/validators/brd/
├── __init__.py         # UnifiedBRDValidator, exports
├── schema.py           # Constants from validate_brd.py
└── result.py           # ValidationIssue, ValidationResult classes
```

**Task 1.2**: Port constants from existing scripts

From `validate_brd.py`:
- `REQUIRED_CUSTOM_FIELDS`
- `REQUIRED_TAGS`, `FORBIDDEN_TAG_PATTERNS`
- `REQUIRED_SECTIONS_STANDARD`, `REQUIRED_SECTIONS_MVP`
- `FILE_NAME_PATTERN_*`

From `validate_standardized_element_codes.py`:
- `VALID_BRD_CODES`
- `SECTION_CODE_MAP`
- `PREFERRED_SECTION_CODES`

### Phase 2: Validation Checks

**Task 2.1**: `element_codes.py` - Element ID validation

Port from `validate_standardized_element_codes.py`:
- `BRD.NN.TT.SS` pattern validation
- Type code validation (01-32)
- Section-to-code semantic mapping
- Preferred code warnings

**Task 2.2**: `structure.py` - Document structure validation

Port from `validate_brd.py`:
- File name pattern validation
- H1 title format
- Required sections (standard/MVP profiles)
- Section numbering sequence
- Document Control section

**Task 2.3**: `metadata.py` - YAML frontmatter validation

Port from `validate_brd.py` + `validate_metadata.py`:
- YAML parsing
- Required custom_fields
- Required/forbidden tags
- deliverable_type validation
- Legacy field migration warnings

**Task 2.4**: `quality_gate.py` - Quality score checks

Port from `validate_brd_quality_score.sh`:
- Placeholder detection (`[TBD]`, `TODO`, `FIXME`)
- Downstream reference validation
- Element count thresholds
- Index file validation
- Cross-link validation
- Diagram presence
- Glossary completeness
- Duplicate detection
- Cost/size warnings

**Task 2.5**: `links.py` - Link validation

Port from `validate_links.py`:
- Internal link resolution
- External link format
- Broken link detection

**Task 2.6**: `references.py` - Forward reference validation

Port from `validate_forward_references.py`:
- `@ref:` tag resolution
- Missing reference detection

**Task 2.7**: `diagrams.py` - Diagram consistency

Port from `validate_diagram_consistency.py`:
- Mermaid syntax validation
- SVG file existence
- Diagram-code consistency

### Phase 3: Unified Validator

**Task 3.1**: `__init__.py` - UnifiedBRDValidator class

```python
class UnifiedBRDValidator:
    """Unified BRD validator with tiered checks."""

    def __init__(self, strict: bool = False, verbose: bool = False):
        self.strict = strict
        self.verbose = verbose

    def validate(
        self,
        doc_path: Path,
        tier1_only: bool = False,
    ) -> ValidationResult:
        """
        Run validation checks.

        Tier 1 (Core, blocking):
        - element_codes
        - structure
        - metadata
        - quality_gate (errors only)

        Tier 2 (Advisory, non-blocking):
        - links
        - references
        - diagrams
        - quality_gate (warnings)
        """
        ...
```

### Phase 4: CLI Integration

**Task 4.1**: Add `ucx validate` command

Update `ucx/cli/main.py`:

```python
@cli.group()
def validate():
    """Validate documents without AI review."""
    pass

@validate.command()
@click.argument('doc_path', type=click.Path(exists=True))
@click.option('--tier1-only', is_flag=True, help='Run Tier 1 (core) checks only')
@click.option('--strict', is_flag=True, help='Treat warnings as errors')
@click.option('--verbose', is_flag=True, help='Verbose output')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def brd(doc_path, tier1_only, strict, verbose, format):
    """Validate BRD document structure."""
    ...
```

**Task 4.2**: Update `ucx review` to use unified validator

Replace Phase 1 validation in review command with `UnifiedBRDValidator`.

### Phase 5: Deprecation & Migration

**Task 5.1**: Mark old scripts as deprecated

Add deprecation notice to all migrated scripts (see templates below).

#### Scripts to Deprecate

**BRD-specific** (`ucx_flow_v3/01_BRD/scripts/`):
- `validate_brd.py`
- `validate_brd_quality_score.sh`
- `validate_brd_wrapper.sh`
- `brd_core_wrapper_hook.sh`
- `brd_standardized_element_codes_hook.sh`
- `brd_legacy_pattern_hook.sh`

**Shared** (`ucx_flow_v3/scripts/`):
- `validate_standardized_element_codes.py`
- `detect_legacy_element_ids.py`
- `validate_metadata.py`
- `validate_links.py`
- `validate_forward_references.py`
- `validate_diagram_consistency.py`
- `validate_terminology.py`
- `validate_counts.py`
- `error_codes.py`

#### Deprecation Notice Template (Python)

```python
#!/usr/bin/env python3
"""
DEPRECATED: This script is deprecated as of UCX v1.9.0.

Migration: Use `ucx validate brd <path>` instead.
Removal: This script will be removed in UCX v2.0.0.

See: /opt/data/docs_flow_framework/UCX/docs/QUICK_START.md

--- Original docstring below ---

[Original docstring content...]
"""

import warnings

warnings.warn(
    "This script is deprecated. Use 'ucx validate brd <path>' instead. "
    "Will be removed in UCX v2.0.0.",
    DeprecationWarning,
    stacklevel=2
)

# ... rest of script unchanged ...
```

#### Deprecation Notice Template (Bash)

```bash
#!/bin/bash
# =============================================================================
# DEPRECATED: This script is deprecated as of UCX v1.9.0.
#
# Migration: Use `ucx validate brd <path> --tier1-only` instead.
# Removal: This script will be removed in UCX v2.0.0.
#
# See: /opt/data/docs_flow_framework/UCX/docs/QUICK_START.md
# =============================================================================

echo "WARNING: This script is deprecated. Use 'ucx validate brd <path>' instead." >&2
echo "         Will be removed in UCX v2.0.0." >&2

# ... rest of script unchanged ...
```

#### Deprecation Timeline

| Version | Action |
|---------|--------|
| **v1.9.0** | Add deprecation notices, UCX validate available |
| **v1.10.0** | Scripts still work, emit warnings |
| **v2.0.0** | Remove deprecated scripts |

**Task 5.2**: Update BeeLocal pre-commit hooks

Replace:
```yaml
- id: brd-core-wrapper
  entry: bash ucx_flow_v3/01_BRD/scripts/brd_core_wrapper_hook.sh
```

With:
```yaml
- id: ucx-brd-validate
  entry: bash -c 'source /opt/data/docs_flow_framework/.venv/bin/activate && ucx validate brd docs/01_BRD --tier1-only'
```

**Task 5.3**: Update framework documentation

- UCX README
- Quick Start guide
- Validation workflow docs

---

## Exit Codes

| Code | Meaning | Pre-commit |
|------|---------|------------|
| 0 | All checks passed | ✅ Pass |
| 1 | Warnings only (non-blocking) | ✅ Pass (unless --strict) |
| 2 | Errors present (blocking) | ❌ Fail |
| 3 | Script/runtime error | ❌ Fail |

---

## Output Format

### Text (default)

```
==========================================
UCX BRD Validation
==========================================
Path: docs/01_BRD/BRD-01_platform_architecture/
Mode: Tier 1 + Tier 2

[TIER 1: CORE CHECKS]

[PASS] Element codes: 47 valid IDs
[PASS] Structure: All 18 sections present
[PASS] Metadata: Valid frontmatter
[WARN] Quality gate: 2 placeholders found

[TIER 2: ADVISORY CHECKS]

[PASS] Links: 23 internal, 5 external
[WARN] References: 1 unresolved @ref:
[PASS] Diagrams: 3 Mermaid, 2 SVG

==========================================
Summary
==========================================
Tier 1 Errors:   0
Tier 1 Warnings: 1
Tier 2 Warnings: 1
Status: PASS (warnings present)
```

### JSON (for CI)

```json
{
  "path": "docs/01_BRD/BRD-01_platform_architecture/",
  "status": "pass",
  "tier1": {
    "errors": 0,
    "warnings": 1,
    "checks": {
      "element_codes": {"status": "pass", "count": 47},
      "structure": {"status": "pass"},
      "metadata": {"status": "pass"},
      "quality_gate": {"status": "warn", "issues": ["2 placeholders"]}
    }
  },
  "tier2": {
    "warnings": 1,
    "checks": {
      "links": {"status": "pass", "internal": 23, "external": 5},
      "references": {"status": "warn", "unresolved": 1},
      "diagrams": {"status": "pass", "mermaid": 3, "svg": 2}
    }
  }
}
```

---

## File Mapping

### BRD-Specific Scripts → UCX Modules

| Source Script | Target Module | Functions Ported |
|--------------|---------------|------------------|
| `01_BRD/scripts/validate_brd.py` | `brd/structure.py` | File naming, H1, sections, Document Control |
| `01_BRD/scripts/validate_brd.py` | `brd/metadata.py` | YAML frontmatter, custom_fields, tags |
| `01_BRD/scripts/validate_brd.py` | `brd/diagrams.py` | Diagram contract validation |
| `01_BRD/scripts/validate_brd_quality_score.sh` | `brd/quality_gate.py` | All 10 GATE checks |
| `01_BRD/scripts/validate_brd_wrapper.sh` | `brd/__init__.py` | Tiered orchestration logic |

### Shared Scripts → UCX Modules

| Source Script | Target Module | Functions Ported |
|--------------|---------------|------------------|
| `scripts/error_codes.py` | `common/error_codes.py` | Severity, ErrorCode, ERROR_REGISTRY |
| `scripts/validate_standardized_element_codes.py` | `brd/element_codes.py` | BRD.NN.TT.SS validation, section-code mapping |
| `scripts/detect_legacy_element_ids.py` | `brd/element_codes.py` | Legacy pattern detection (FR-001, AC-01, etc.) |
| `scripts/validate_metadata.py` | `brd/metadata.py` | Lightweight YAML checks, deliverable_type |
| `scripts/validate_links.py` | `brd/links.py` | Internal/external link resolution |
| `scripts/validate_forward_references.py` | `brd/references.py` | @ref: tag resolution |
| `scripts/validate_diagram_consistency.py` | `brd/diagrams.py` | Mermaid syntax, SVG existence |
| `scripts/validate_terminology.py` | `brd/quality_gate.py` | GATE-07: Glossary consistency |
| `scripts/validate_counts.py` | `brd/quality_gate.py` | GATE-03: Count consistency |

### Future Migration (Phase 2)

| Source Script | Target Module | Notes |
|--------------|---------------|-------|
| `scripts/validate_cross_document.py` | `common/cross_document.py` | Multi-type traceability |
| `scripts/validate_artifact.py` | `common/artifact.py` | Generic validation |
| `scripts/validate_documentation_paths.py` | `common/paths.py` | Path validation |
| `scripts/validate_schema_sync.py` | `common/schema.py` | Schema sync |
| `scripts/validate_tags_against_docs.py` | `common/tags.py` | Tag validation |
| `scripts/validate_traceability_matrix.py` | `common/traceability.py` | Matrix validation |

### Deprecation After Migration

After UCX migration complete, deprecate:

```
ucx_flow_v3/01_BRD/scripts/
├── validate_brd.py                    # → ucx validate brd
├── validate_brd_quality_score.sh      # → ucx validate brd
├── validate_brd_wrapper.sh            # → ucx validate brd
├── brd_core_wrapper_hook.sh           # → ucx validate brd --tier1-only
├── brd_standardized_element_codes_hook.sh  # → ucx validate brd --tier1-only
├── brd_legacy_pattern_hook.sh         # → ucx validate brd --tier1-only
└── README.md                          # Update to redirect to UCX

ucx_flow_v3/scripts/
├── validate_standardized_element_codes.py  # → ucx validate brd
├── detect_legacy_element_ids.py           # → ucx validate brd
├── validate_metadata.py                   # → ucx validate brd
├── validate_links.py                      # → ucx validate brd
├── validate_forward_references.py         # → ucx validate brd
├── validate_diagram_consistency.py        # → ucx validate brd
├── validate_terminology.py                # → ucx validate brd
├── validate_counts.py                     # → ucx validate brd
└── error_codes.py                         # → ucx (common module)
```

**Keep in ucx_flow_v3:**
- `claude_brd_skill_audit_hook.sh` - AI-based, not validation
- `validate_all.py` - Replace with `ucx validate --all` later
- PRD/other type validators - Phase 2 migration

---

## Dependencies

### Required

- Python 3.10+
- PyYAML (already in UCX)
- Click (already in UCX)

### Optional

- `requests` - for external link validation (Tier 2)

---

## Testing

### Unit Tests

```
tests/validators/brd/
├── test_element_codes.py
├── test_structure.py
├── test_metadata.py
├── test_quality_gate.py
├── test_links.py
├── test_references.py
├── test_diagrams.py
└── test_unified_validator.py
```

### Integration Tests

```
tests/integration/
├── test_ucx_validate_brd.py   # CLI integration
└── fixtures/
    ├── valid_brd/             # Valid BRD for pass tests
    ├── invalid_brd/           # Invalid BRD for fail tests
    └── warning_brd/           # BRD with warnings only
```

---

## Timeline Estimate

| Phase | Tasks | Complexity |
|-------|-------|------------|
| Phase 1 | Module structure + constants | 2/5 |
| Phase 2 | 7 validation modules | 4/5 |
| Phase 3 | Unified validator | 3/5 |
| Phase 4 | CLI integration | 2/5 |
| Phase 5 | Deprecation + migration | 2/5 |

---

## Migration Roadmap (All Layers)

### Phase 1: Foundation + BRD ✅ COMPLETE

| Task | Description | Status |
|------|-------------|--------|
| 1.1 | Create `common/` module (error_codes, file_utils, patterns) | ✅ Complete |
| 1.2 | Create `brd/` module (all validators) | ✅ Complete |
| 1.3 | CLI: `ucx validate brd` | ✅ Complete |
| 1.4 | Update BeeLocal pre-commit hooks | ✅ Complete |
| 1.5 | Deprecate `ucx_flow_v3/01_BRD/scripts/` | ✅ Complete |

**Deliverable**: UCX 1.9.2 ✅

### Phase 2: PRD + EARS

| Task | Description | Priority |
|------|-------------|----------|
| 2.1 | Create `prd/` module | High |
| 2.2 | Create `ears/` module | High |
| 2.3 | CLI: `ucx validate prd`, `ucx validate ears` | High |
| 2.4 | Port PRD element codes validation | High |
| 2.5 | Deprecate `ucx_flow_v3/02_PRD/scripts/`, `03_EARS/scripts/` | High |

**Deliverable**: UCX 1.11.0

### Phase 3: BDD + ADR + SYS

| Task | Description | Priority |
|------|-------------|----------|
| 3.1 | Create `bdd/` module | Medium |
| 3.2 | Create `adr/` module | Medium |
| 3.3 | Create `sys/` module | Medium |
| 3.4 | CLI: `ucx validate bdd`, `ucx validate adr`, `ucx validate sys` | Medium |
| 3.5 | Deprecate `ucx_flow_v3/04_BDD/`, `05_ADR/`, `06_SYS/` scripts | Medium |

**Deliverable**: UCX 1.12.0

### Phase 4: REQ + CTR + SPEC

| Task | Description | Priority |
|------|-------------|----------|
| 4.1 | Create `req/` module | Medium |
| 4.2 | Create `ctr/` module | Medium |
| 4.3 | Create `spec/` module | Medium |
| 4.4 | CLI: `ucx validate req`, `ucx validate ctr`, `ucx validate spec` | Medium |
| 4.5 | Deprecate `ucx_flow_v3/07_REQ/`, `08_CTR/`, `09_SPEC/` scripts | Medium |

**Deliverable**: UCX 1.13.0

### Phase 5: TSPEC + TASKS + CHG

| Task | Description | Priority |
|------|-------------|----------|
| 5.1 | Create `tspec/` module (utest, itest, ftest, ptest, stest, sectest) | Medium |
| 5.2 | Create `tasks/` module | Medium |
| 5.3 | Create `chg/` module (gates, routing) | Low |
| 5.4 | CLI: `ucx validate tspec`, `ucx validate tasks` | Medium |
| 5.5 | CLI: `ucx validate all` (orchestrator) | Medium |
| 5.6 | Deprecate remaining `ucx_flow_v3/` scripts | Medium |

**Deliverable**: UCX 1.14.0

### Phase 6: Cleanup + Documentation

| Task | Description | Priority |
|------|-------------|----------|
| 6.1 | Remove deprecated `ucx_flow_v3/*/scripts/` validators | Low |
| 6.2 | Update all framework documentation | Low |
| 6.3 | Create migration guide for projects | Low |
| 6.4 | Performance optimization | Low |

**Deliverable**: UCX 2.0.0

### Migration Template (Per Layer)

Each layer follows this pattern:

```
ucx/validators/{type}/
├── __init__.py         # Unified{TYPE}Validator class
├── schema.py           # Constants (sections, codes, patterns)
├── element_codes.py    # Element ID validation (if applicable)
├── structure.py        # Document structure validation
├── metadata.py         # YAML frontmatter validation
└── quality_gate.py     # Quality gate checks (GATE-01 to GATE-N)
```

### Scripts per Layer

| Layer | Scripts | Estimated Effort |
|-------|---------|------------------|
| L1 BRD | 3 main + 6 shared | Medium (current plan) |
| L2 PRD | 4 main | Medium |
| L3 EARS | 4 main | Medium |
| L4 BDD | 3 main | Medium |
| L5 ADR | 2 main | Low |
| L6 SYS | 2 main | Low |
| L7 REQ | 3 main | Medium |
| L8 CTR | 4 main | Medium |
| L9 SPEC | 3 main | Medium |
| L10 TSPEC | 7 main | High |
| L11 TASKS | 2 main | Low |
| CHG | 5 main | Medium |
| **Total** | **42 scripts** | - |

---

## Gaps Identified (Review)

### Gap 1: Missing Dependency - error_codes.py

The `validate_brd.py` imports from `ucx_flow_v3/scripts/error_codes.py`:

```python
from error_codes import Severity, calculate_exit_code, format_error
```

**Required**: Port to `ucx/validators/common/error_codes.py`

Contents:
- `Severity` enum (ERROR, WARNING, INFO)
- `ErrorCode` dataclass
- `ERROR_REGISTRY` dictionary (BRD-E001 through BRD-W014)
- `calculate_exit_code()` function
- `format_error()` function

### Gap 2: Complete Quality Gate Enumeration

The quality_score.sh has 10 GATE checks. Plan must enumerate all with tier assignment:

| GATE | Check | Tier | Blocking |
|------|-------|------|----------|
| GATE-01 | Placeholder Text Detection | 1 | Yes (for existing BRDs) |
| GATE-02 | Premature Downstream References | 1 | Yes |
| GATE-03 | Internal Count Consistency | 2 | No |
| GATE-04 | Index Synchronization | 1 | Yes |
| GATE-05 | Inter-BRD Cross-Linking | - | DEPRECATED |
| GATE-06 | Diagram Contract Validation | 1 | Yes |
| GATE-07 | Glossary Consistency | 2 | No |
| GATE-08 | Element ID Uniqueness | 1 | Yes (duplicates), No (misplaced) |
| GATE-09 | Cost Estimate Format | 2 | No |
| GATE-10 | File Size Compliance | 1 | Yes (>20K tokens) |

### Gap 3: Section-Based BRD Layout Support

Scripts detect and handle multi-file "section-based" BRD layouts:

```bash
# Detection pattern
find "$root" -type f -name 'BRD-*.0_*.md'
```

Structure example:
```
BRD-01_platform_architecture/
├── BRD-01.0_index.md
├── BRD-01.1_overview.md
├── BRD-01.2_requirements.md
└── ...
```

**Required**: Add `is_section_based_layout()` detection in validator.

### Gap 4: Companion Report File Exclusion

Scripts exclude audit/review/fix report files:

```python
COMPANION_REPORT_PATTERN = r'\.(A_audit_report|R_review_report|F_fix_report|V_validation_report)(_v[0-9]+)?\.md$'
```

**Required**: Add to file filtering in all validation modules.

### Gap 5: Template Profile Detection

`validate_brd.py` supports two section profiles:

| Profile | Sections | Detection |
|---------|----------|-----------|
| `standard` | 5 required sections (legacy) | `custom_fields.template_profile: standard` |
| `mvp` | 18 required sections | `custom_fields.template_profile: mvp` |

**Required**: Port `REQUIRED_SECTIONS_STANDARD` and `REQUIRED_SECTIONS_MVP` to schema.py.

### Gap 6: Diagram Contract Tags

`validate_brd.py` checks for specific diagram tags:

| Tag | Requirement |
|-----|-------------|
| `@diagram: c4-l1` | Required for all BRDs |
| `@diagram: dfd-l0` | Required for all BRDs |
| `@diagram: sequence-*` | Required if sequenceDiagram present |

Additional fields checked:
- `diagram_type:`
- `level:`
- `scope_boundary:`
- `upstream_refs:`
- `downstream_refs:`

**Required**: Add to `diagrams.py` module.

### Gap 7: Shared Utilities Module

Create `ucx/validators/common/` for shared logic:

```
ucx/validators/common/
├── __init__.py
├── error_codes.py      # Severity, ErrorCode, ERROR_REGISTRY
├── file_utils.py       # is_companion_report(), collect_source_files()
├── patterns.py         # Regex patterns shared across validators
└── frontmatter.py      # YAML frontmatter parsing
```

### Gap 8: Registry Integration

The existing `ucx/validators/registry.py` uses decorator-based registration:

```python
@register_validator(DocType.BRD)
class BRDValidator(BaseValidator):
    ...
```

**Decision needed**:
- Option A: UnifiedBRDValidator extends BaseValidator, replaces existing BRDValidator
- Option B: UnifiedBRDValidator is standalone, BRDValidator calls it internally
- Option C: Both coexist, `ucx validate` uses Unified, `ucx review` uses existing

**Recommendation**: Option A - single validator class.

### Gap 9: Backward Compatibility

During transition:
1. Keep `ucx/validators/brd.py` (existing) working
2. Add `ucx/validators/brd/` (new unified module)
3. Registry returns UnifiedBRDValidator for DocType.BRD
4. Mark old `brd.py` for removal in v2.0.0

### Gap 10: Version Bump

After implementation:
- Bump UCX version to **1.9.0**
- Changelog: "Unified BRD validation with full quality gate checks"

### Gap 11: Missing Checks from validate_brd.py

Additional checks not in original plan:

| Check | Module |
|-------|--------|
| `_check_business_objectives()` | structure.py |
| `_check_stakeholders()` | structure.py |
| `validate_depends_tags()` | references.py |
| `validate_diagram_contract()` | diagrams.py |
| `validate_crosslinking_tags()` | references.py (info-level) |
| Legacy `development_status` → `status` migration | metadata.py |

### Gap 12: Pre-commit Hook Efficiency

Current pre-commit activates venv on each run. Consider:

```yaml
# Option A: Direct venv activation (current)
entry: bash -c 'source /opt/data/docs_flow_framework/.venv/bin/activate && ucx validate brd docs/01_BRD --tier1-only'

# Option B: Wrapper script (faster)
entry: /opt/data/docs_flow_framework/UCX/bin/ucx-validate-brd docs/01_BRD --tier1-only
```

**Required**: Create `UCX/bin/ucx-validate-brd` wrapper script.

---

## Updated Module Structure (Scalable)

```
ucx/validators/
├── base.py                    # BaseValidator ABC (existing)
├── registry.py                # Validator registry (existing, updated)
├── generic.py                 # GenericValidator (existing)
│
├── common/                    # SHARED: Cross-layer utilities
│   ├── __init__.py            # Exports
│   ├── error_codes.py         # Severity, ErrorCode, ERROR_REGISTRY
│   ├── file_utils.py          # File collection, companion detection
│   ├── patterns.py            # Shared regex patterns
│   ├── frontmatter.py         # YAML parsing utilities
│   ├── links.py               # Link validation (reusable)
│   ├── references.py          # Forward reference validation
│   ├── diagrams.py            # Diagram consistency
│   ├── terminology.py         # Glossary/terminology checks
│   ├── traceability.py        # Cross-document validation
│   ├── quality_base.py        # BaseQualityGate class
│   └── result.py              # ValidationResult, ValidationIssue
│
├── brd/                       # L1: BRD (Phase 1 - Current)
│   ├── __init__.py            # UnifiedBRDValidator
│   ├── schema.py              # BRD constants
│   ├── element_codes.py       # BRD.NN.TT.SS + legacy
│   ├── structure.py           # BRD structure
│   ├── metadata.py            # BRD metadata
│   └── quality_gate.py        # BRD GATE checks
│
├── prd/                       # L2: PRD (Phase 2)
│   └── ...                    # Same pattern as BRD
│
├── ears/                      # L3: EARS (Phase 2)
│   └── ...
│
├── bdd/                       # L4: BDD (Phase 3)
│   └── ...
│
├── adr/                       # L5: ADR (Phase 3)
│   └── ...
│
├── sys/                       # L6: SYS (Phase 3)
│   └── ...
│
├── req/                       # L7: REQ (Phase 4)
│   └── ...
│
├── ctr/                       # L8: CTR (Phase 4)
│   └── ...
│
├── spec/                      # L9: SPEC (Phase 4)
│   └── ...
│
├── tspec/                     # L10: TSPEC (Phase 5)
│   ├── __init__.py            # UnifiedTSPECValidator
│   ├── schema.py
│   ├── utest.py               # Unit test validation
│   ├── itest.py               # Integration test validation
│   ├── ftest.py               # Functional test validation
│   ├── ptest.py               # Performance test validation
│   ├── stest.py               # Smoke test validation
│   ├── sectest.py             # Security test validation
│   └── quality_gate.py
│
├── tasks/                     # L11: TASKS (Phase 5)
│   └── ...
│
├── chg/                       # CHG: Change Management (Phase 5)
│   ├── __init__.py
│   ├── routing.py
│   └── gates.py               # GATE-01, 05, 09, 12
│
└── _deprecated/               # Deprecated validators (remove in v2.0.0)
    ├── brd.py                 # Old BRD validator
    ├── prd.py                 # Old PRD validator
    └── ...
```

### Base Classes

```python
# common/quality_base.py
class BaseQualityGate(ABC):
    """Base class for quality gate validation."""

    @abstractmethod
    def get_tier1_checks(self) -> List[str]:
        """Return list of Tier 1 (blocking) check names."""
        pass

    @abstractmethod
    def get_tier2_checks(self) -> List[str]:
        """Return list of Tier 2 (advisory) check names."""
        pass

    def run(self, doc_path: Path, tier1_only: bool = False) -> ValidationResult:
        """Run quality gate checks."""
        ...

# common/result.py
@dataclass
class ValidationIssue:
    code: str           # e.g., "BRD-E001"
    severity: Severity  # ERROR, WARNING, INFO
    message: str
    file_path: Path
    line: Optional[int] = None

@dataclass
class ValidationResult:
    status: ValidationStatus  # PASSED, FAILED
    tier1_errors: List[ValidationIssue]
    tier1_warnings: List[ValidationIssue]
    tier2_warnings: List[ValidationIssue]

    @property
    def exit_code(self) -> int:
        if self.tier1_errors:
            return 2
        if self.tier1_warnings or self.tier2_warnings:
            return 1
        return 0
```

---

## Updated Task List

### Phase 1: Foundation ✅ COMPLETE

**Task 1.0**: Create `ucx/validators/common/` module ✅
- Port `error_codes.py` (Severity, ErrorCode, ERROR_REGISTRY)
- Create `file_utils.py` (companion file detection, source file collection)
- Create `patterns.py` (shared regex patterns)
- Create `frontmatter.py` (YAML parsing)
- Create `result.py` (ValidationIssue, UnifiedValidationResult)

### Phase 2: Schema & Constants ✅ COMPLETE

**Task 2.0**: Create `ucx/validators/brd/schema.py` ✅
- Port `REQUIRED_SECTIONS_STANDARD` (5 sections)
- Port `REQUIRED_SECTIONS_MVP` (18 sections)
- Port `REQUIRED_CUSTOM_FIELDS`
- Port `REQUIRED_TAGS`, `FORBIDDEN_TAG_PATTERNS`
- Port `FILE_NAME_PATTERN_*`
- Port `VALID_BRD_CODES`, `SECTION_CODE_MAP`, `PREFERRED_SECTION_CODES`

### Phase 3: Validation Modules ✅ COMPLETE

**Task 3.1-3.7**: All validation modules implemented:
- `element_codes.py` - BRD.NN.TT.SS validation ✅
- `structure.py` - Document structure validation ✅
- `metadata.py` - YAML frontmatter validation ✅
- `quality_gate.py` - 10 GATE checks with tier assignment ✅
- Section-based layout detection ✅
- Companion report file exclusion ✅
- Template profile support (standard/mvp) ✅

### Phase 4: Integration ✅ COMPLETE

**Task 4.0**: Create wrapper script ✅
**Task 4.1**: Add `ucx validate brd` command ✅
**Task 4.2**: Update registry to use UnifiedBRDValidator ✅
**Task 4.3**: Renamed `brd.py` to `brd_validator.py` (registry wrapper) ✅

### Phase 5: Documentation & Migration ✅ COMPLETE

**Task 5.1**: Update pre-commit hooks (documented in config) ✅
**Task 5.2**: Created `scripts/ucx-validate.sh` for all layers ✅
**Task 5.3**: Update UCX README, Quick Start, validators/README ✅
**Task 5.4**: Version bumped to 1.9.2 ✅

---

## Additional Considerations

### Integration with UCX Review Flow

The new `UnifiedBRDValidator` replaces Phase 1 validation in `ucx review`:

```python
# ucx/api/review.py (updated)
def review(self, doc_type: str, doc_path: Path) -> ReviewResult:
    # Phase 1: Use new unified validator
    from ucx.validators.brd import UnifiedBRDValidator
    validator = UnifiedBRDValidator()
    validation_result = validator.validate(doc_path, tier1_only=True)

    if validation_result.has_errors and not self.skip_validation:
        return ReviewResult(status="validation_failed", validation=validation_result)

    # Phase 2: AI review (unchanged)
    ...
```

### Performance Optimization

For pre-commit speed:

1. **Tier 1 only** (`--tier1-only`): Skip advisory checks (links, diagrams)
2. **Changed files only**: Pre-commit passes only changed files
3. **Caching**: Consider caching parsed YAML frontmatter
4. **Wrapper script**: Avoid venv activation overhead

```bash
# UCX/bin/ucx-validate (wrapper script)
#!/bin/bash
exec /opt/data/docs_flow_framework/.venv/bin/python -m ucx.cli validate "$@"
```

### Configuration (Optional)

Consider `ucx.yaml` configuration for validation:

```yaml
# ucx.yaml (optional)
validation:
  brd:
    tier1_checks:
      - element_codes
      - structure
      - metadata
      - quality_gate
    tier2_checks:
      - links
      - references
      - diagrams

    # Override thresholds
    max_tokens: 20000
    required_profile: mvp

    # Skip specific checks
    skip:
      - GATE-05  # Deprecated
```

**Decision**: Defer to Phase 2. Start with hardcoded defaults.

### CI/CD Integration

GitHub Actions example:

```yaml
# .github/workflows/validate-docs.yml
name: Document Validation
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install UCX
        run: pip install -e /opt/data/docs_flow_framework/UCX

      - name: Validate BRD documents
        run: ucx validate brd docs/01_BRD/ --format json > validation.json

      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: validation-results
          path: validation.json
```

### GitHub Problem Matcher

JSON output compatible with GitHub Actions annotations:

```json
{
  "issues": [
    {
      "file": "docs/01_BRD/BRD-01.md",
      "line": 42,
      "severity": "error",
      "code": "BRD-E001",
      "message": "Invalid H1 format"
    }
  ]
}
```

Add problem matcher in `.github/matchers/ucx.json`:

```json
{
  "problemMatcher": [{
    "owner": "ucx",
    "pattern": [{
      "regexp": "^\\[ERROR\\] ([A-Z]+-E\\d+): (.+):(\\d+) (.+)$",
      "file": 2,
      "line": 3,
      "code": 1,
      "message": 4
    }]
  }]
}
```

### Rollback Plan

If migration fails:

1. **Pre-commit**: Revert to old hooks in `.pre-commit-config.yaml`
2. **UCX validate**: Command not breaking, just unavailable
3. **UCX review**: Falls back to existing `ucx/validators/brd.py`
4. **Scripts**: Old scripts still work (deprecated, not removed)

Rollback command:
```bash
git checkout HEAD~1 -- .pre-commit-config.yaml
```

### Logging

Use UCX's existing logging:

```python
# ucx/validators/common/__init__.py
import logging

logger = logging.getLogger("ucx.validators")

# In validators
logger.debug(f"Validating {doc_path}")
logger.info(f"Found {len(issues)} issues")
logger.warning(f"Deprecated pattern: {pattern}")
```

Enable with `UCX_LOG_LEVEL=DEBUG`.

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Script logic differs from Python port | Medium | High | Comprehensive testing with same fixtures |
| Pre-commit too slow | Low | Medium | Tier 1 only + wrapper script |
| Breaking existing UCX review | Low | High | Keep old validator until v2.0.0 |
| Missing edge cases | Medium | Medium | Port existing test cases |
| BeeLocal sync issues | Low | Low | Update BeeLocal hooks after framework |

---

## Success Criteria

| Criteria | Metric |
|----------|--------|
| **Functional parity** | All checks from old scripts pass in new validators |
| **Performance** | Pre-commit <3s for single BRD |
| **Test coverage** | >90% line coverage on new modules |
| **Documentation** | Updated README, Quick Start, CLI help |
| **Migration** | BeeLocal pre-commit hooks updated and passing |

---

## Approval

- [x] Architecture approved
- [x] Gaps addressed
- [x] Risk assessment reviewed
- [x] Success criteria agreed
- [x] Implementation approved
- [x] Ready for development
- [x] **Phase 1 (BRD) Implementation Complete** (2026-03-11)

---

## Next Steps

Phase 2 (PRD + EARS) is planned for UCX 1.11.0. See Migration Roadmap above.
