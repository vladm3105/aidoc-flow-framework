---
name: doc-cspec-reviewer
description: Comprehensive content review and quality assurance for component-focused SPEC (Layer 6) documents - validates component-spec completeness, behavior contracts, interface definitions, and flags issues requiring manual attention
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
    downstream_artifacts: []
    version: "2.0"
    last_updated: "2026-05-22"
---

# doc-cspec-reviewer

## Purpose

Comprehensive **content review and quality assurance** for component-focused
SPEC (Layer 6) documents. This skill performs deep content analysis beyond
structural validation — checking interface completeness, behavior contracts,
algorithm specifications, and flagging issues that require manual review.

This skill is a **SPEC (Layer 6) specialization** focused on component design.
It does **not** define a separate artifact, template, or element-code; the
canonical artifact contract is `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
(see `../doc-spec/`).

**Layer**: 6 (SPEC — component focus)

**Upstream**: SPEC (from `doc-cspec-autopilot`)

**Downstream**: None (final QA gate before TDD/IPLAN generation)

---

## When to Use

Use `doc-cspec-reviewer` when:
- **After SPEC Generation**: Run immediately after `doc-cspec-autopilot` completes
- **Manual SPEC Edits**: After making manual changes to a component SPEC
- **Pre-IPLAN Check**: Before running IPLAN authoring
- **Pre-TDD Check**: Before running TDD authoring
- **Periodic Review**: Regular quality checks on existing SPECs

**Do NOT use when**:
- SPEC does not exist yet (use `doc-cspec-autopilot` first)
- Only structural validation needed (use `../doc-cspec-validator/`)

---

## Review Checklist

### 1. Interface Definition Review

- [ ] All public interfaces documented
- [ ] Method signatures complete (params, returns, errors)
- [ ] Type definitions accurate
- [ ] Interfaces consistent with upstream EARS/BDD intent

### 2. Behavior Contract Review

- [ ] Validation rules trace to EARS (`@ears: EARS.NN.SS.xxxx`)
- [ ] State transitions trace to BDD (`@bdd: BDD.NN.SS.xxxx`)
- [ ] Error handling responses are defined
- [ ] Data models align with interface contracts

### 3. Algorithm Specification Review

- [ ] Core algorithms documented
- [ ] Complexity analysis provided
- [ ] Edge cases identified
- [ ] Performance considerations noted

### 4. Implementation Guidance Review

- [ ] Class/module structure defined
- [ ] Dependency patterns specified
- [ ] Configuration options documented
- [ ] Resource management specified

### 5. TDD Contract Mapping Review

- [ ] Downstream TDD document referenced (`@tdd: TDD-NN`)
- [ ] Test files identified for interfaces
- [ ] Edge cases flagged for test coverage
- [ ] Performance test requirements noted

### 6. Traceability Review

- [ ] All upstream tags present (`@brd`, `@prd`, `@ears`, `@bdd`, `@adr`)
- [ ] Upstream requirements mapped to interfaces/behavior
- [ ] ADR decisions linked (`@adr: ADR-NN`)
- [ ] Downstream TDD references complete

---

## Review Report Format

```markdown
# SPEC-NN Review Report (component focus)

## Summary
- **Document**: SPEC-NN_{slug}
- **Review Date**: YYYY-MM-DD
- **TDD-Ready Score**: NN%
- **Status**: PASS/FAIL

## Findings

### Critical Issues
1. [Issue description]
   - Location: [section/line]
   - Impact: [description]
   - Recommendation: [fix]

### Warnings
1. [Warning description]

### Recommendations
1. [Improvement suggestion]

## Metrics
| Metric | Value | Target |
|--------|-------|--------|
| Interface Coverage | NN% | 100% |
| Behavior Contracts | NN% | 100% |
| TDD Contract Mapping | NN% | 90% |
```

---

## Output Files

| File | Purpose |
|------|---------|
| `SPEC-NN.A_audit_report_vNNN.md` | Audit report with findings |
| `SPEC-NN.R_review_report_vNNN.md` | Legacy review report format |

---

## Integration with Fixer

After review, issues can be fixed automatically:
1. Run `doc-cspec-reviewer` to identify issues
2. Review generates `SPEC-NN.A_audit_report_vNNN.md`
3. Run `doc-cspec-fixer` to apply automated fixes
4. Re-run reviewer to verify fixes

---

## References

- Canonical SPEC artifact contract: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Layer overview: `framework/layers/06_SPEC/README.md`
- Governance / ID & naming standards: `framework/governance/`
- Parent SPEC skill: `../doc-spec/`
