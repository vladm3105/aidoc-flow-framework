---
name: doc-riskspec-reviewer
description: Comprehensive content review and quality assurance for RISKSPEC documents - validates risk specification completeness, control coverage, and mitigation adequacy
metadata:
  tags:
    - sdd-workflow
    - layer-9-artifact
    - riskspec-artifact
    - quality-assurance
  custom_fields:
    layer: 9
    subtype_code: 53
    artifact_type: RISKSPEC
    deliverable_type: risk
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [RISKSPEC]
    downstream_artifacts: []
    version: "1.0"
    last_updated: "2026-03-01"
---

# doc-riskspec-reviewer

## Purpose

Comprehensive **content review and quality assurance** for Risk Specification (RISKSPEC) documents. Validates risk identification, impact analysis, control measures, and mitigation planning.

**Layer**: 9.53 (RISKSPEC Quality Assurance)

---

## Review Checklist

### 1. Risk Identification
- [ ] All risks from REQ identified
- [ ] Risk categories appropriate
- [ ] Risk descriptions clear

### 2. Impact Analysis
- [ ] Probability ratings justified
- [ ] Impact ratings justified
- [ ] Risk scores calculated

### 3. Control Measures
- [ ] Controls mapped to risks
- [ ] Control effectiveness rated
- [ ] Control owners identified

### 4. Mitigation Planning
- [ ] Action items defined
- [ ] Timelines realistic
- [ ] Resources identified

### 5. Residual Risk
- [ ] Post-mitigation scores calculated
- [ ] Acceptable risk levels defined
- [ ] Escalation paths documented

---

## References

- Template: `ai_dev_ssd_flow/09_SPEC/RISKSPEC/RISKSPEC-MVP-TEMPLATE.yaml`
- Schema: `ai_dev_ssd_flow/09_SPEC/RISKSPEC/RISKSPEC_MVP_SCHEMA.yaml`
