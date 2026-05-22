---
name: doc-dspec-reviewer
description: Comprehensive content review and quality assurance for data-spec SPEC (Layer 6) documents - validates data-model completeness, interface coverage, behavior contracts, and identifies issues requiring manual attention
metadata:
  tags:
    - sdd-workflow
    - layer-6-artifact
    - spec-artifact
    - quality-assurance
  custom_fields:
    layer: 6
    artifact_type: SPEC
    spec_focus: data-design
    deliverable_type: document
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR]
    downstream_artifacts: []
    version: "1.0"
    last_updated: "2026-05-22"
---

# doc-dspec-reviewer

## Purpose

Comprehensive **content review and quality assurance** for data-spec SPEC
(Layer 6) documents. This skill performs deep content analysis beyond
structural validation, checking data-model completeness, interface coverage,
behavior contracts, and identifying issues that require manual review. It is a
plugin-only authoring helper — a data-design specialization of SPEC — and
reviews against the single framework SPEC template.

**Layer**: 6 (SPEC — data-design quality assurance)

**Parent**: `../doc-spec/`

**Upstream**: SPEC (from `../doc-dspec-autopilot/`)

**Downstream**: None (final QA gate before TDD generation)

---

## When to Use

Use `doc-dspec-reviewer` when:
- **After SPEC Generation**: Run immediately after `../doc-dspec-autopilot/` completes
- **Manual SPEC Edits**: After making manual changes to a SPEC's data models
- **Pre-TDD Check**: Before authoring the downstream TDD
- **Periodic Review**: Regular quality checks on existing data-focused SPECs

---

## Review Checklist

### 1. Data-Model Coverage Review

- [ ] All upstream data requirements addressed
- [ ] Field types and required flags complete
- [ ] Constraints and invariants captured
- [ ] No SQL/ORM implementation leakage

### 2. Interface Review

- [ ] Public exports defined with typed signatures
- [ ] Return shapes carry the specified data models
- [ ] Error conditions documented per export

### 3. Behavior Review

- [ ] Validation rules sourced from EARS
- [ ] State transitions sourced from BDD
- [ ] Error handling defined

### 4. Implementation Notes Review

- [ ] Constraints documented
- [ ] Patterns appropriate for the data design
- [ ] Performance considerations noted

### 5. Downstream TDD Contract Review

- [ ] TDD document referenced (`@tdd: TDD-NN`)
- [ ] Test files cover data models and schemas

### 6. Traceability Review

- [ ] All upstream tags present (`@brd`, `@prd`, `@ears`, `@bdd`, `@adr`)
- [ ] Architecture decision linked (`@adr: ADR-NN`)
- [ ] This document tagged `@spec: SPEC-NN`

---

## Review Report Format

```markdown
# SPEC-NN Review Report

## Summary
- **Document**: SPEC-NN_{slug}
- **Review Date**: YYYY-MM-DD
- **TDD-Ready Score**: NN%
- **Status**: PASS/FAIL

## Findings

### Critical Issues
1. [Issue description]

### Warnings
1. [Warning description]

### Recommendations
1. [Improvement suggestion]

## Metrics
| Metric | Value | Target |
|--------|-------|--------|
| Data-Model Coverage | NN% | 100% |
| Interface Completeness | NN% | 90% |
| Behavior Specification | NN% | 90% |
```

---

## References

- Parent skill: `../doc-spec/`
- Template: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Layer guide: `framework/layers/06_SPEC/README.md`
- ID standards: `framework/governance/ID_NAMING_STANDARDS.md`
