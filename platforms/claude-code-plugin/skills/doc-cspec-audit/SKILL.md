---
name: doc-cspec-audit
description: Quality gate for component-focused SPEC (Layer 6) documents - validates structure, detects issues, computes TDD-Ready score, and produces a report for doc-cspec-fixer
metadata:
  tags:
    - sdd-workflow
    - layer-6-artifact
    - spec-component-helper
    - quality-assurance
  custom_fields:
    layer: 6
    artifact_type: SPEC
    spec_focus: component
    deliverable_type: code
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [SPEC]
    downstream_artifacts: [Audit Report]
    version: "2.0"
    last_updated: "2026-05-22"
---

# doc-cspec-audit

## Purpose

Quality gate for **component-focused SPEC** documents — the component-design
specialization of SPEC (Layer 6). It combines structural validation, content
review, and TDD-Ready scoring into a single comprehensive audit, producing a
standardized report that `doc-cspec-fixer` can consume for automated
remediation.

This skill is a **SPEC (Layer 6) specialization**. It audits SPEC documents
authored with a component-design focus; it does **not** define a separate
artifact, template, or element-code. The canonical artifact contract is
`framework/layers/06_SPEC/SPEC-TEMPLATE.yaml` (see `../doc-spec/`).

**Layer**: 6 (SPEC — component focus)

**Upstream**: SPEC document (component focus)

**Downstream**: Audit Report (`SPEC-NN.A_audit_report_vNNN.md`)

---

## When to Use

Use `doc-cspec-audit` when:
- **Pre-Release Check**: Final quality gate before TDD/IPLAN generation
- **Comprehensive Review**: Need both structural and content validation
- **Score Verification**: Need official TDD-Ready score
- **CI/CD Integration**: Automated quality checks in pipeline

**Preferred over individual skills when**:
- Need single comprehensive report
- Running automated pipeline
- Need consistent scoring methodology

---

## Audit Components

### 1. Structure Validation (30%)
- File location compliance
- YAML syntax validity
- Required sections present (8 core SPEC sections)
- Metadata completeness

### 2. Content Quality (40%)
- Interface definitions complete
- Behavior contracts verified
- Algorithm/behavior specifications present
- Implementation guidance adequate

### 3. Traceability (15%)
- Upstream tags complete (`@brd`, `@prd`, `@ears`, `@bdd`, `@adr`)
- ADR mappings valid (`@adr: ADR-NN`)
- Behavior contract references valid
- Downstream TDD mappings present

### 4. Readiness Metrics (15%)
- TDD-Ready score calculation
- Downstream readiness assessment
- Risk identification

---

## TDD-Ready Score Calculation

| Component | Weight | Scoring Criteria |
|-----------|--------|------------------|
| Interface Completeness | 20% | All interfaces documented with full signatures |
| Behavior Contracts | 20% | All behavior/validation contracts specified |
| Algorithm Specification | 15% | Core algorithms documented with complexity analysis |
| Error Handling | 15% | Error handling defined for all interfaces |
| TDD Contract Mapping | 15% | Downstream TDD test contracts referenced |
| Traceability | 15% | All upstream tags present and valid |

**Thresholds**:
- **PASS**: ≥90%
- **CONDITIONAL**: 80-89%
- **FAIL**: <80%

---

## Audit Report Format

```markdown
# SPEC-NN Audit Report (component focus)

## Document Information
- **SPEC ID**: SPEC-NN
- **Title**: {title}
- **Audit Date**: YYYY-MM-DD
- **Audit Version**: vNNN

## Executive Summary
- **TDD-Ready Score**: NN% [PASS/CONDITIONAL/FAIL]
- **Critical Issues**: N
- **Warnings**: N
- **Recommendations**: N

## Detailed Findings

### Structure Validation
| Check | Status | Details |
|-------|--------|---------|
| File Location | PASS/FAIL | |
| YAML Syntax | PASS/FAIL | |
| Required Sections | PASS/FAIL | |
| Metadata | PASS/FAIL | |

### Content Quality
| Check | Status | Details |
|-------|--------|---------|
| Interfaces | NN% | |
| Behavior Contracts | NN% | |
| Algorithms | NN% | |
| Error Handling | NN% | |

### Traceability
| Tag | Present | Valid |
|-----|---------|-------|
| @brd | Yes/No | Yes/No |
| @prd | Yes/No | Yes/No |
| @ears | Yes/No | Yes/No |
| @bdd | Yes/No | Yes/No |
| @adr | Yes/No | Yes/No |

### Issues

#### Critical (Must Fix)
1. [Issue description]

#### Warnings (Should Fix)
1. [Warning description]

#### Recommendations (Nice to Have)
1. [Recommendation]

## Metrics Summary
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| TDD-Ready | NN% | ≥90% | |
| Interface Coverage | NN% | 100% | |
| Behavior Contracts | NN% | 100% | |
| TDD Contract Mapping | NN% | 90% | |

## Next Steps
1. Run `doc-cspec-fixer` with this report
2. Re-audit after fixes applied
3. Proceed to TDD generation when PASS
```

---

## Output Files

| File | Purpose |
|------|---------|
| `SPEC-NN.A_audit_report_vNNN.md` | Comprehensive audit report |

---

## Integration

### Audit → Fix → Re-Audit Cycle
```
doc-cspec-audit → SPEC-NN.A_audit_report.md → doc-cspec-fixer → doc-cspec-audit
```

### CI/CD Pipeline
```yaml
steps:
  - name: SPEC (component) Audit
    run: invoke doc-cspec-audit --spec docs/06_SPEC/SPEC-NN/
  - name: Check Score
    run: check TDD-Ready >= 90%
  - name: Fix if Needed
    run: invoke doc-cspec-fixer --report SPEC-NN.A_audit_report.md
```

---

## References

- Canonical SPEC artifact contract: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Layer overview: `framework/layers/06_SPEC/README.md`
- Governance / ID & naming standards: `framework/governance/`
- Parent SPEC skill: `../doc-spec/`
