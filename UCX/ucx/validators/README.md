# UCX Validators

## Overview

The validators module provides non-AI document validation for UCX. It validates document structure, metadata, element codes, and quality gates without requiring AI API calls.

**Version**: 1.9.4

## Architecture

```
validators/
├── common/                 # Shared validation utilities
│   ├── error_codes.py      # Severity, ErrorCode, ERROR_REGISTRY
│   ├── file_utils.py       # File collection, companion detection
│   ├── frontmatter.py      # YAML frontmatter parsing
│   ├── result.py           # ValidationIssue, UnifiedValidationResult
│   ├── links.py            # Link validation (Tier 2)
│   ├── references.py       # Forward reference validation (Tier 2)
│   └── diagrams.py         # Diagram consistency (Tier 2)
│
├── brd/                    # UnifiedBRDValidator (L1)
│   ├── __init__.py         # UnifiedBRDValidator class
│   ├── schema.py           # Constants (sections, codes, patterns)
│   ├── element_codes.py    # BRD.NN.TT.SS validation
│   ├── structure.py        # Document structure validation
│   ├── metadata.py         # YAML frontmatter validation
│   └── quality_gate.py     # 10 GATE quality checks
│
├── base.py                 # BaseValidator ABC
├── registry.py             # Validator registry (@register_validator)
├── brd_validator.py        # Registry-compatible BRD wrapper
├── prd.py                  # PRD validator (legacy)
├── ears.py                 # EARS validator (legacy)
├── bdd.py                  # BDD validator (legacy)
├── adr.py                  # ADR validator (legacy)
├── sys.py                  # SYS validator (legacy)
├── req.py                  # REQ validator (legacy)
├── ctr.py                  # CTR validator (legacy)
├── spec.py                 # SPEC validator (legacy)
├── tspec.py                # TSPEC validator (legacy)
└── generic.py              # Generic fallback validator
```

## Element Type Codes

Valid BRD element type codes (used in `BRD.NN.TT.SS` format):

| Code | Element Type | Section |
|------|--------------|---------|
| 01 | Functional Requirement | 6.x |
| 02 | Quality Attribute (generic) | 7.1 |
| 03 | Constraint | 8.1 |
| 04 | Assumption | 8.2 |
| 05 | Dependency | 10.x (legacy) |
| 06 | Acceptance Criteria | 9.x |
| 07 | Risk | 10.x |
| 08 | Metric | - |
| 09 | User Story | 5.x |
| 10 | Decision | 7.2 |
| 22 | Feature Item | 3.x |
| 23 | Business Objective | 2.x |
| 24 | Stakeholder Need | 4.x |
| 32 | Architecture Topic | 7.2 (legacy) |
| **91** | **Performance Requirement** | **7.3** |
| **92** | **Reliability Requirement** | **7.4** |
| **94** | **Scalability Requirement** | **7.5** |
| **96** | **Security Requirement** | **7.6** |
| **98** | **Observability Requirement** | **7.7** |
| **99** | **Maintainability Requirement** | **7.8** |

> **Note**: Codes 91-99 are canonical for Quality Attribute subcategories. Code 02 accepted for legacy/overview sections.
> See `ai_dev_ssd_flow/ID_NAMING_STANDARDS.md` for complete reference.

## Section-to-Code Mapping

| Section | Valid Codes | Canonical |
|---------|-------------|-----------|
| 2 (Business Objectives) | 23 | 23 |
| 3 (Project Scope) | 22 | 22 |
| 4 (Stakeholders) | 24 | 24 |
| 5 (User Stories) | 09 | 09 |
| 6 (Functional Requirements) | 01, 06 | 01 |
| 7.1 (QA Overview) | 02 | 02 |
| 7.2 (Architecture Decisions) | 10, 32 | 10 |
| 7.3 (Performance) | 02, 05, 91 | 91 |
| 7.4 (Reliability) | 02, 05, 92 | 92 |
| 7.5 (Scalability) | 02, 05, 94 | 94 |
| 7.6 (Security) | 02, 05, 96 | 96 |
| 7.7 (Observability) | 02, 05, 98 | 98 |
| 7.8 (Maintainability) | 02, 05, 99 | 99 |
| 8.1 (Constraints) | 03 | 03 |
| 8.2 (Assumptions) | 04 | 04 |
| 9 (Acceptance Criteria) | 06 | 06 |
| 10 (Risk Management) | 05, 07 | 07 |

## Tiered Validation

| Tier | Type | Blocking | Description |
|------|------|----------|-------------|
| **Tier 1** | Core | Yes (exit 2) | Element codes, structure, metadata, quality gates (errors) |
| **Tier 2** | Advisory | No (exit 1) | Links, references, diagrams, glossary (warnings) |

## Usage

### CLI

```bash
# Full validation (Tier 1 + Tier 2)
ucx validate brd docs/01_BRD/BRD-01/

# Pre-commit (Tier 1 only, fast)
ucx validate brd docs/01_BRD/BRD-01/ --tier1-only

# Strict mode (warnings as errors)
ucx validate brd docs/01_BRD/BRD-01/ --strict

# JSON output for CI/CD
ucx validate brd docs/01_BRD/BRD-01/ --format json
```

### Python API

```python
from pathlib import Path
from ucx.validators.brd import UnifiedBRDValidator

# Direct usage
validator = UnifiedBRDValidator()
result = validator.validate(Path("docs/01_BRD/BRD-01/"))

# Tier 1 only (for pre-commit)
result = validator.validate(Path("docs/01_BRD/BRD-01/"), tier1_only=True)

# Check results
if result.has_tier1_errors:
    print(f"Validation failed: {len(result.tier1_errors)} errors")
    for issue in result.tier1_issues:
        print(f"  [{issue.code}] {issue.message}")
else:
    print("Validation passed")

# Exit code
exit_code = result.exit_code(strict=False)
```

### Via Registry

```python
from ucx.validators.registry import get_validator
from ucx.models.enums import DocType

validator = get_validator(DocType.BRD)
result = validator.validate(Path("docs/01_BRD/BRD-01/"))
```

## Quality Gates (BRD)

| GATE | Check | Tier | Description |
|------|-------|------|-------------|
| GATE-01 | Placeholder detection | 1 | [TBD], TODO, FIXME markers |
| GATE-02 | Downstream references | 1 | Premature PRD/REQ references |
| GATE-03 | Count consistency | 2 | Stated counts vs actual items |
| GATE-04 | Index synchronization | 1 | Section-based layout index |
| GATE-06 | Diagram contracts | 1 | Required @diagram tags |
| GATE-07 | Glossary consistency | 2 | Technical terms defined |
| GATE-08 | Element uniqueness | 1 | Duplicate BRD.NN.TT.SS IDs |
| GATE-09 | Cost format | 2 | Cost estimate formatting |
| GATE-10 | File size | 1 | Token limit (20K) |

## Error Codes

### BRD Errors (Tier 1)

| Code | Description |
|------|-------------|
| BRD-E001 | Invalid element code format |
| BRD-E002 | Missing Document Control section |
| BRD-E003 | Missing required tag |
| BRD-E004 | Invalid H1 title format |
| BRD-E005 | Invalid file naming pattern |
| BRD-E006 | Missing required section |
| BRD-E007 | Placeholder text found |
| BRD-E008 | Premature downstream reference |
| BRD-E009 | Duplicate element ID |
| BRD-E010 | File exceeds token limit |

### BRD Warnings (Tier 2)

| Code | Description |
|------|-------------|
| BRD-W001 | Element code in wrong section |
| BRD-W002 | Missing glossary term |
| BRD-W003 | Count mismatch |
| BRD-W004 | Cost format inconsistency |

### Link/Reference Errors (Tier 2)

| Code | Description |
|------|-------------|
| LINK-E001 | Broken internal link (file not found) |
| LINK-E002 | Broken anchor link |
| LINK-W001 | Placeholder link |
| FWDREF-E001 | Forward reference to non-existent document |
| FWDREF-W001 | Forward reference to downstream layer |
| DIAG-E001 | Mermaid syntax error |
| DIAG-W001 | Missing diagram for section |

## Exit Codes

| Code | Meaning | Pre-commit |
|------|---------|------------|
| 0 | All checks passed | Pass |
| 1 | Warnings only (Tier 2) | Pass (unless --strict) |
| 2 | Errors present (Tier 1) | Fail |
| 3 | Script/runtime error | Fail |

## Pre-commit Integration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ucx-brd-validate
        name: UCX BRD Validation (Tier 1)
        entry: bash -c 'source /opt/data/docs_flow_framework/.venv/bin/activate && ucx validate brd docs/01_BRD --tier1-only'
        language: system
        files: ^docs/01_BRD/.*\.md$
        stages: [pre-commit]
```

## Migration from Legacy Scripts

The following scripts are deprecated as of v1.9.0 and will be removed in v2.0.0:

| Legacy Script | Replacement |
|--------------|-------------|
| `validate_brd.py` | `ucx validate brd` |
| `validate_standardized_element_codes.py` | `ucx validate brd` |
| `validate_brd_quality_score.sh` | `ucx validate brd` |
| `validate_brd_wrapper.sh` | `ucx validate brd` |
| `detect_legacy_element_ids.py` | `ucx validate brd` |
| `validate_metadata.py` | `ucx validate brd` |
| `validate_links.py` | `ucx validate brd` |
| `validate_forward_references.py` | `ucx validate brd` |
| `validate_diagram_consistency.py` | `ucx validate brd` |

## Adding New Layer Validators

To add validation for a new layer (e.g., PRD):

1. Create `validators/prd/` directory with same structure as `brd/`
2. Create `UnifiedPRDValidator` in `__init__.py`
3. Define layer-specific schema in `schema.py`
4. Implement validation modules (element_codes, structure, metadata, quality_gate)
5. Update `prd_validator.py` to delegate to `UnifiedPRDValidator`
6. Register with `@register_validator(DocType.PRD)`

See PLAN-001 for the migration roadmap (v1.10.0: PRD/EARS, v1.11.0: BDD/ADR/SYS, etc.).

## Traceability Tag Patterns

All traceability tags require 2+ digit document numbers per ID_NAMING_STANDARDS.md:

| Tag | Pattern | Example |
|-----|---------|---------|
| `@brd:` | `BRD-\d{2,}` | `@brd: BRD-01` |
| `@prd:` | `PRD-\d{2,}` | `@prd: PRD-01` |
| `@ears:` | `EARS-\d{2,}` | `@ears: EARS-01` |
| `@bdd:` | `BDD-\d{2,}` | `@bdd: BDD-01` |
| `@adr:` | `ADR-\d{2,}` | `@adr: ADR-01` |
| `@sys:` | `SYS-\d{2,}` | `@sys: SYS-01` |
| `@req:` | `REQ.\d{2,}.\d{2}.\d{2,}` | `@req: REQ.01.01.01` |
| `@ctr:` | `CTR-\d{2,}` | `@ctr: CTR-01` |
| `@spec:` | `SPEC-\d{2,}` | `@spec: SPEC-01` |
| `@tasks:` | `TASKS-\d{2,}` | `@tasks: TASKS-01` |

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.9.7 | 2026-03-11 | Extended `--fix` for Tier 2 count mismatches: GATE-W003 (stated vs actual), DIAG-W001 (diagram nodes) |
| 1.9.6 | 2026-03-11 | Added `--fix` for auto-fixing structural issues; `--report` for auto-report; `--fix --report --clean-reports` combo; New `BRDFixer` module; Fixed Document Control regex |
| 1.9.5 | 2026-03-11 | Added `--clean-reports` and `--keep-versions` to `ucx validate` for report cleanup |
| 1.9.4 | 2026-03-11 | Added QA subcategory codes 91-99; Section 3/4 mappings; Updated tag patterns to require 2+ digits |
| 1.9.2 | 2026-03-11 | Registry integration with UnifiedBRDValidator |
| 1.9.0 | 2026-03-11 | Initial unified validation architecture |
