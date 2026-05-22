---
name: doc-riskspec-reviewer
description: Comprehensive content review and quality assurance for risk-analysis SPEC (Layer 6) documents - validates risk specification completeness, control coverage, and mitigation adequacy
metadata:
  tags:
    - sdd-workflow
    - layer-6-artifact
    - spec-document
    - quality-assurance
  custom_fields:
    layer: 6
    artifact_type: SPEC
    deliverable_type: risk
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR]
    downstream_artifacts: []
    version: "1.0"
    last_updated: "2026-05-22"
---

# doc-riskspec-reviewer

## Purpose

Comprehensive **content review and quality assurance** for risk-analysis SPEC
documents. Validates risk identification, impact analysis, control measures,
and mitigation planning. This is the risk-spec specialization of the SPEC
(Layer 6) authoring helpers — see the parent skill `../doc-spec/` and the
single SPEC template at `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`.

**Layer**: 6 (SPEC quality assurance, risk-analysis focus)

---

## Review Checklist

### 1. Risk Identification
- [ ] All risks from upstream artifacts identified
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

- Parent skill: `../doc-spec/`
- Template: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Layer guidance: `framework/layers/06_SPEC/README.md`
- ID standards: `framework/governance/ID_NAMING_STANDARDS.md`
