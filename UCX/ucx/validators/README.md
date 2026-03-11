# UCX Validators

## Overview

The validators module provides non-AI document validation for UCX. It validates document structure, metadata, element codes, and quality gates without requiring AI API calls.

**Version**: 1.9.2

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
