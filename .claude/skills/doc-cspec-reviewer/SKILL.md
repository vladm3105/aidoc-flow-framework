---
name: doc-cspec-reviewer
description: Comprehensive content review and quality assurance for CSPEC documents - validates code specification completeness, CTR compliance, interface definitions, and identifies issues requiring manual attention
metadata:
  tags:
    - sdd-workflow
    - layer-9-artifact
    - cspec-artifact
    - quality-assurance
  custom_fields:
    layer: 9
    subtype_code: 50
    artifact_type: CSPEC
    deliverable_type: code
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [CSPEC]
    downstream_artifacts: []
    version: "1.0"
    last_updated: "2026-03-01"
---

# doc-cspec-reviewer

## Purpose

Comprehensive **content review and quality assurance** for Code Specification (CSPEC) documents. This skill performs deep content analysis beyond structural validation, checking interface completeness, CTR compliance, algorithm specifications, and identifying issues that require manual review.

**Layer**: 9.50 (CSPEC Quality Assurance)

**Upstream**: CSPEC (from `doc-cspec-autopilot`)

**Downstream**: None (final QA gate before TSPEC/TASKS generation)

---

## When to Use

Use `doc-cspec-reviewer` when:
- **After CSPEC Generation**: Run immediately after `doc-cspec-autopilot` completes
- **Manual CSPEC Edits**: After making manual changes to CSPEC
- **Pre-TASKS Check**: Before running `doc-tasks-autopilot`
- **Pre-TSPEC Check**: Before running `doc-tspec-autopilot`
- **Periodic Review**: Regular quality checks on existing CSPECs

**Do NOT use when**:
- CSPEC does not exist yet (use `doc-cspec-autopilot` first)
- Only structural validation needed (use `doc-cspec-validator`)

---

## Review Checklist

### 1. Interface Definition Review

- [ ] All public interfaces documented
- [ ] Method signatures complete (params, returns, exceptions)
- [ ] Type definitions accurate
- [ ] API contracts match CTR specifications

### 2. CTR Compliance Review

- [ ] CTR reference valid and accessible
- [ ] Interface implementations match CTR schema
- [ ] Error responses match CTR error definitions
- [ ] Data models align with CTR schemas

### 3. Algorithm Specification Review

- [ ] Core algorithms documented
- [ ] Complexity analysis provided
- [ ] Edge cases identified
- [ ] Performance considerations noted

### 4. Implementation Guidance Review

- [ ] Class/module structure defined
- [ ] Dependency injection patterns specified
- [ ] Configuration options documented
- [ ] Resource management specified

### 5. Test Mapping Review

- [ ] Unit test cases cover all methods
- [ ] Integration test cases cover interfaces
- [ ] Edge cases have test coverage
- [ ] Performance test requirements defined

### 6. Traceability Review

- [ ] All cumulative tags present (@brd through @ctr)
- [ ] REQ requirements mapped to implementations
- [ ] CTR contracts linked
- [ ] Test references complete

---

## Review Report Format

```markdown
# CSPEC-NN Review Report

## Summary
- **Document**: CSPEC-NN_{slug}
- **Review Date**: YYYY-MM-DD
- **CODE-Ready Score**: NN%
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
| CTR Compliance | NN% | 100% |
| Test Mapping | NN% | 90% |
```

---

## Output Files

| File | Purpose |
|------|---------|
| `CSPEC-NN.A_audit_report_vNNN.md` | Audit report with findings |
| `CSPEC-NN.R_review_report_vNNN.md` | Legacy review report format |

---

## Integration with Fixer

After review, issues can be fixed automatically:
1. Run `doc-cspec-reviewer` to identify issues
2. Review generates `CSPEC-NN.A_audit_report_vNNN.md`
3. Run `doc-cspec-fixer` to apply automated fixes
4. Re-run reviewer to verify fixes

---

## References

- Template: `ai_dev_ssd_flow/09_SPEC/CSPEC/CSPEC-MVP-TEMPLATE.yaml`
- Schema: `ai_dev_ssd_flow/09_SPEC/CSPEC/CSPEC_MVP_SCHEMA.yaml`
- Validation Rules: `ai_dev_ssd_flow/09_SPEC/CSPEC/CSPEC_MVP_VALIDATION_RULES.md`
