---
name: doc-dspec-reviewer
description: Comprehensive content review and quality assurance for DSPEC documents - validates documentation specification completeness, audience alignment, content coverage, and identifies issues requiring manual attention
metadata:
  tags:
    - sdd-workflow
    - layer-9-artifact
    - dspec-artifact
    - quality-assurance
  custom_fields:
    layer: 9
    subtype_code: 51
    artifact_type: DSPEC
    deliverable_type: document
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [DSPEC]
    downstream_artifacts: []
    version: "1.0"
    last_updated: "2026-03-01"
---

# doc-dspec-reviewer

## Purpose

Comprehensive **content review and quality assurance** for Documentation Specification (DSPEC) documents. This skill performs deep content analysis beyond structural validation, checking content coverage, audience alignment, style compliance, and identifying issues that require manual review.

**Layer**: 9.51 (DSPEC Quality Assurance)

**Upstream**: DSPEC (from `doc-dspec-autopilot`)

**Downstream**: None (final QA gate before TASKS generation)

---

## When to Use

Use `doc-dspec-reviewer` when:
- **After DSPEC Generation**: Run immediately after `doc-dspec-autopilot` completes
- **Manual DSPEC Edits**: After making manual changes to DSPEC
- **Pre-TASKS Check**: Before running `doc-tasks-autopilot`
- **Periodic Review**: Regular quality checks on existing DSPECs

---

## Review Checklist

### 1. Content Coverage Review

- [ ] All REQ topics addressed
- [ ] Information architecture logical
- [ ] Content depth appropriate for audience
- [ ] Examples sufficient and relevant

### 2. Audience Alignment Review

- [ ] Primary audience clearly defined
- [ ] Technical level appropriate
- [ ] Prerequisites realistic
- [ ] Terminology appropriate for audience

### 3. Structure Review

- [ ] Logical flow of topics
- [ ] Section hierarchy appropriate
- [ ] Navigation aids specified
- [ ] Cross-references defined

### 4. Style Compliance Review

- [ ] Style guide referenced
- [ ] Voice and tone consistent
- [ ] Formatting standards met
- [ ] Terminology consistent

### 5. Accessibility Review

- [ ] Visual content has alt text specs
- [ ] Color contrast considered
- [ ] Reading level appropriate
- [ ] Multi-format considerations

### 6. Traceability Review

- [ ] All cumulative tags present
- [ ] REQ requirements mapped
- [ ] Source references complete

---

## Review Report Format

```markdown
# DSPEC-NN Review Report

## Summary
- **Document**: DSPEC-NN_{slug}
- **Review Date**: YYYY-MM-DD
- **DOC-Ready Score**: NN%
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
| Content Coverage | NN% | 100% |
| Audience Alignment | NN% | 90% |
| Style Compliance | NN% | 85% |
```

---

## References

- Template: `ai_dev_ssd_flow/09_SPEC/DSPEC/DSPEC-MVP-TEMPLATE.yaml`
- Schema: `ai_dev_ssd_flow/09_SPEC/DSPEC/DSPEC_MVP_SCHEMA.yaml`
