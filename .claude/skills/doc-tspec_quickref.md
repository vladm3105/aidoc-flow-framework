# doc-tspec Quick Reference

## TSPEC Overview

| Attribute | Value |
|-----------|-------|
| **Layer** | 10 |
| **Artifact Type** | TSPEC |
| **Format** | Markdown (.md) |
| **Location** | `docs/10_TSPEC/{TYPE}/{TYPE}-NN_{slug}/{TYPE}-NN_{slug}.md` |

## Test Type Codes

| Code | Type | Abbreviation | Purpose |
|------|------|--------------|---------|
| 40 | Unit Test | UTEST | Individual function/method tests |
| 41 | Integration Test | ITEST | Component interaction tests |
| 42 | Smoke Test | STEST | Post-deployment health checks |
| 43 | Functional Test | FTEST | System behavior validation |
| 44 | Performance Test | PTEST | Load, stress, and response time testing |
| 45 | Security Test | SECTEST | Vulnerability and threat testing |

## Element ID Format

**Pattern**: `TSPEC.NN.xxxx`

| Component | Description | Range |
|-----------|-------------|-------|
| `NN` | Document number | 01-99 |
| `TT` | Test type code | 40-45 |
| `SS` | Sequential test case | 01-99 |

**Examples**:
- `TSPEC.01.4001` = Document 1, Unit Test #1
- `TSPEC.01.4103` = Document 1, Integration Test #3
- `TSPEC.01.4401` = Document 1, Performance Test #1

## Cumulative Tags (8-9 Required)

```markdown
@brd: BRD.NN.xxxx
@prd: PRD.NN.xxxx
@ears: EARS.NN.25.SS
@bdd: BDD.NN.14.SS
@adr: ADR-NN
@sys: SYS.NN.26.SS
@req: REQ.NN.27.SS
@spec: SPEC-NN
@ctr: CTR-NN  (optional - if CTR exists)
```

## Nested Folder Rule (MANDATORY)

ALL TSPEC documents MUST be in nested folders:

```
docs/10_TSPEC/
├── UTEST/
│   └── UTEST-01_{slug}/
│       └── UTEST-01_{slug}.md
├── ITEST/
│   └── ITEST-01_{slug}/
│       └── ITEST-01_{slug}.md
├── STEST/
│   └── STEST-01_{slug}/
│       └── STEST-01_{slug}.md
├── FTEST/
│   └── FTEST-01_{slug}/
│       └── FTEST-01_{slug}.md
├── PTEST/
│   └── PTEST-01_{slug}/
│       └── PTEST-01_{slug}.md
└── SECTEST/
    └── SECTEST-01_{slug}/
        └── SECTEST-01_{slug}.md
```

## Required Sections (Individual Templates)

| Section | Title |
|---------|-------|
| 1 | Document Control |
| 2 | Test Scope |
| 3 | Test Case Index |
| 4 | Test Case Details (includes Error Cases) |
| 5 | Coverage Matrix |
| 6 | Traceability |

## TASKS-Ready Targets

| Test Type | Target Score |
|-----------|--------------|
| UTEST | >= 90% |
| ITEST | >= 90% |
| STEST | 100% |
| FTEST | >= 90% |
| PTEST | >= 85% |
| SECTEST | >= 90% |

## Templates

| Template | Path |
|----------|------|
| Aggregator (MD) | `ai_dev_ssd_flow/10_TSPEC/TSPEC-MVP-TEMPLATE.md` |
| Aggregator (YAML) | `ai_dev_ssd_flow/10_TSPEC/TSPEC-MVP-TEMPLATE.yaml` |
| UTEST | `ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST-MVP-TEMPLATE.md` |
| ITEST | `ai_dev_ssd_flow/10_TSPEC/ITEST/ITEST-MVP-TEMPLATE.md` |
| STEST | `ai_dev_ssd_flow/10_TSPEC/STEST/STEST-MVP-TEMPLATE.md` |
| FTEST | `ai_dev_ssd_flow/10_TSPEC/FTEST/FTEST-MVP-TEMPLATE.md` |
| PTEST | `ai_dev_ssd_flow/10_TSPEC/PTEST/PTEST-MVP-TEMPLATE.md` |
| SECTEST | `ai_dev_ssd_flow/10_TSPEC/SECTEST/SECTEST-MVP-TEMPLATE.md` |

## Related Skills

| Skill | Purpose |
|-------|---------|
| `doc-tspec` | Create TSPEC documents |
| `doc-tspec-validator` | Validate TSPEC structure |
| `doc-tspec-autopilot` | Automated generation from SPEC |
| `doc-tspec-reviewer` | Content review and QA |
| `doc-tspec-fixer` | Apply fixes from review |
| `doc-naming` | Element ID standards |

## Deprecated Patterns (Do NOT Use)

| Old Pattern | Use Instead |
|-------------|-------------|
| `TC-XXX` | `TSPEC.NN.40.SS` |
| `UT-XXX` | `TSPEC.NN.40.SS` |
| `IT-XXX` | `TSPEC.NN.41.SS` |
| `ST-XXX` | `TSPEC.NN.42.SS` |
| `FT-XXX` | `TSPEC.NN.43.SS` |
| `PT-XXX` | `TSPEC.NN.44.SS` |
| Flat files | Nested folder structure |

## Validation Command

```bash
bash ai_dev_ssd_flow/10_TSPEC/scripts/validate_all_tspec.sh docs/10_TSPEC/
```

---

*Version: 1.0 | Last Updated: 2026-02-26*
