# doc-tdd Quick Reference

## TDD Overview

| Attribute | Value |
|-----------|-------|
| **Layer** | 7 |
| **Artifact Type** | TDD |
| **Format** | YAML (.yaml) |
| **Location** | `docs/07_TDD/TDD-NN_{slug}/TDD-NN_{slug}.yaml` |

TDD is a **single unified template — no test subtypes**. Test categories are
content within one TDD document, distinguished by a `type` attribute.

## Test Type Categories

| Type | Purpose | Primary Source |
|------|---------|----------------|
| unit | Individual function/method and data-model constraint tests | SPEC (Sections 3-4) |
| integration | Component interaction, state, error-handling tests | SPEC (Section 5) |
| e2e | Full workflow tests mapped from acceptance scenarios | BDD (Layer 4) |
| security (optional) | Vulnerability/threat tests when SPEC or ADR mandates them | SPEC, ADR |

## Element ID Format

**Pattern**: `TDD.NN.04.xxxx` (4 segments — test cases live in Section 4)

| Component | Description | Range |
|-----------|-------------|-------|
| `TDD` | Artifact prefix | — |
| `NN` | Document number | 01-99 |
| `04` | Section number (test cases) | 04 |
| `xxxx` | 4-char hex content hash | 0000-ffff |

**Examples**:
- `TDD.01.04.a3c1` = Document 1, test case (unit)
- `TDD.01.04.5e2a` = Document 1, test case (integration)
- `TDD.02.04.8f4c` = Document 2, test case (e2e)

Categorize each case with a `type` attribute (unit/integration/e2e/security),
NOT a numeric ID code or a separate document.

## Cumulative Tags (6 Required)

```yaml
@brd: BRD.NN.SS.xxxx
@prd: PRD.NN.SS.xxxx
@ears: EARS.NN.SS.xxxx
@bdd: BDD.NN.SS.xxxx
@adr: ADR.NN.SS.xxxx
@spec: SPEC-NN
```

Plus the self-tag `@tdd: TDD-NN` and downstream `@iplan: IPLAN-NN` in
Section 7 (Traceability).

## Nested Folder Rule (MANDATORY)

ALL TDD documents MUST be in nested folders:

```
docs/07_TDD/
├── TDD-01_auth_service/
│   └── TDD-01_auth_service.yaml
├── TDD-02_order_processing/
│   └── TDD-02_order_processing.yaml
└── TDD-00_index.md
```

## Required Sections (single unified template)

| Section | Title |
|---------|-------|
| 1 | Document Control |
| 2 | Test Pyramid |
| 3 | BDD Scenario to Test Mapping |
| 4 | Test Case Definitions (includes edge/error cases) |
| 5 | Test Thresholds |
| 6 | TDD Execution Order |
| 7 | Traceability |

## Coverage Targets

| Test Type | Coverage Target |
|-----------|-----------------|
| unit | >= 90% |
| integration | >= 85% |
| e2e | >= 75% of happy paths (<=300s budget) |
| security (optional) | all auth/authz paths; no OWASP Top 10 |

**Quality Gate**: IPLAN-Ready Score >= 90/100.

## Templates

| Template | Path |
|----------|------|
| TDD | `framework/layers/07_TDD/TDD-TEMPLATE.yaml` |
| TDD Index | `framework/layers/07_TDD/TDD-00_index.TEMPLATE.md` |

## Related Skills

| Skill | Purpose |
|-------|---------|
| `doc-tdd` | Create TDD documents |
| `doc-tdd-validator` | Validate TDD structure |
| `doc-tdd-autopilot` | Automated generation from SPEC |
| `doc-tdd-reviewer` | Content review and QA |
| `doc-tdd-audit` | Combined validator + reviewer audit |
| `doc-tdd-fixer` | Apply fixes from review |
| `doc-iplan` | Downstream implementation plan (Layer 8) |
| `doc-naming` | Element ID standards |

## Deprecated Patterns (Do NOT Use)

| Old Pattern | Use Instead |
|-------------|-------------|
| `TC-XXX` | `TDD.NN.04.xxxx` |
| `UT-XXX` / `IT-XXX` / `ST-XXX` / `FT-XXX` | `TDD.NN.04.xxxx` with a `type` attribute |
| Numeric type codes (40-45) | `type` attribute on the test case |
| 3-segment IDs (`TDD.NN.xxxx`) | 4-segment `TDD.NN.04.xxxx` |
| Flat files | Nested folder structure |

## Validation

The framework is spec-only — there are no validation scripts. The
`doc-tdd-validator` skill *is* the validator; apply its declarative checklist
with `framework/layers/07_TDD/README.md` and `framework/governance/` as
authority.

---

*Version: 1.1 | Last Updated: 2026-05-22*
