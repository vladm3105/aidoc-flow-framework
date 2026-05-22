---
name: doc-procspec-reviewer
description: Comprehensive content review and quality assurance for process-spec SPEC (Layer 6) documents - validates process completeness, step clarity, and role coverage
metadata:
  tags:
    - sdd-workflow
    - layer-6-artifact
    - spec-artifact
    - quality-assurance
  custom_fields:
    layer: 6
    artifact_type: SPEC
    spec_focus: process-design
    deliverable_type: document
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [SPEC]
    downstream_artifacts: []
    version: "1.0"
    last_updated: "2026-05-22"
---

# doc-procspec-reviewer

## Purpose

Comprehensive **content review and quality assurance** for process-spec SPEC
documents. Validates step completeness, role assignments, decision points, and
error handling. This is a plugin-only authoring helper — a process/workflow-design
specialization of SPEC (Layer 6) — that reviews against the single framework
SPEC template (`framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`, see `../doc-spec/`).

**Layer**: 6 (SPEC — process-design quality assurance)

**Parent**: `../doc-spec/`

**Upstream**: SPEC (from `../doc-procspec-autopilot/`)

---

## Review Checklist

### 1. Step Completeness
- [ ] All process steps documented
- [ ] Step sequence logical
- [ ] Pre/post conditions stated

### 2. Role Assignment
- [ ] Each step has responsible role
- [ ] RACI matrix complete
- [ ] Escalation paths defined

### 3. Decision Points
- [ ] Branch conditions clear
- [ ] Outcomes documented
- [ ] Default paths defined

### 4. Error Handling
- [ ] Error scenarios identified
- [ ] Recovery steps documented
- [ ] Fallback procedures defined

### 5. Verification
- [ ] Completion criteria stated
- [ ] Quality checks defined
- [ ] Sign-off requirements noted

### 6. Traceability
- [ ] All cumulative upstream tags present (@brd, @prd, @ears, @bdd, @adr)
- [ ] Upstream requirements mapped

---

## References

- Parent skill: `../doc-spec/`
- Template: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Layer guide: `framework/layers/06_SPEC/README.md`
- ID standards: `framework/governance/ID_NAMING_STANDARDS.md`
