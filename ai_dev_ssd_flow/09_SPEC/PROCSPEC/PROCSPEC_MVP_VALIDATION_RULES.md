---
title: "PROCSPEC MVP Validation Rules"
tags:
  - validation-rules
  - layer-9-artifact
  - procspec-subtype
custom_fields:
  document_type: rules
  artifact_type: PROCSPEC
  layer: 9
  subtype_code: 54
---

# PROCSPEC MVP Validation Rules

## Purpose

Validation checklist for Process Specification (PROCSPEC) documents after creation.

## Validation Checklist

### Structure Validation

- [ ] File is valid YAML
- [ ] File name matches `PROCSPEC-NN_name.yaml` format
- [ ] All required sections present
- [ ] `instance_document_type: procspec-document`
- [ ] `deliverable_type: process`

### Metadata Validation

- [ ] Version is semantic version format (X.Y.Z)
- [ ] Status is valid (draft, review, approved, implemented)
- [ ] Dates are YYYY-MM-DD format
- [ ] At least one author specified
- [ ] `ctr_required: false` (or true if CTR is used)

### Traceability Validation

- [ ] REQ reference present (required)
- [ ] CTR reference present if external APIs used (optional)
- [ ] All cumulative tags complete (BRD through REQ)
- [ ] Downstream artifacts defined (TASKS, output paths)
- [ ] Element IDs use PROCSPEC.NN.TT.SS format

### Process Overview Validation

- [ ] process_type is valid (sop, runbook, playbook, checklist, workflow)
- [ ] execution_context is valid (manual, automated, hybrid)
- [ ] Roles and responsibilities defined
- [ ] Element IDs listed for all elements

### Process Steps Validation

- [ ] At least one process step defined
- [ ] Each step has ID (PROCSPEC.NN.70.SS format)
- [ ] Each step has name
- [ ] Each step has description
- [ ] Each step has responsible party
- [ ] Steps have inputs and outputs (recommended)
- [ ] Steps have success criteria (recommended)

### Decision Points Validation

- [ ] Each decision has ID (PROCSPEC.NN.71.SS format)
- [ ] Each decision has question
- [ ] Each decision has at least two options
- [ ] Each option has next_step reference
- [ ] Default option defined (recommended)

### Escalation Procedures Validation

- [ ] Each escalation has ID (PROCSPEC.NN.72.SS format)
- [ ] Each escalation has trigger
- [ ] Each escalation has escalation_path
- [ ] Escalation path has multiple levels (recommended)
- [ ] Each level has SLA defined
- [ ] Contact methods specified

### Rollback Procedures Validation

- [ ] Each rollback has ID (PROCSPEC.NN.73.SS format)
- [ ] Each rollback has trigger
- [ ] Each rollback has rollback_steps
- [ ] Rollback owner specified (recommended)
- [ ] Verification checks defined (recommended)

### Verification Validation

- [ ] At least one BDD scenario referenced
- [ ] Verification checklist defined
- [ ] Check owners specified

### Implementation Validation

- [ ] output_type specified (sop, runbook, playbook, checklist)
- [ ] output_path specified
- [ ] format specified (markdown, wiki, confluence)
- [ ] Automation level indicated (none, partial, full)

## PROC-Ready Score Calculation

| Criterion | Weight | Check |
|-----------|--------|-------|
| Step Completeness | 25% | All steps have ID, name, description, responsible, inputs, outputs, success criteria |
| Decision Points | 20% | All decisions have questions, options with next_step, default option |
| Escalation Procedures | 20% | All escalations have triggers, multi-level paths, SLAs |
| Rollback Procedures | 15% | All rollbacks have triggers, steps, verification |
| Traceability | 20% | REQ reference, element IDs, downstream artifacts |

**Target**: >= 85%

### Scoring Details

**Step Completeness (25%)**
- 5%: All steps have ID
- 5%: All steps have name and description
- 5%: All steps have responsible party
- 5%: Steps have inputs and outputs
- 5%: Steps have success criteria

**Decision Points (20%)**
- 5%: Decision points defined where needed
- 5%: Questions are clear and actionable
- 5%: All options have next_step
- 5%: Default options provided

**Escalation Procedures (20%)**
- 5%: Escalation triggers defined
- 5%: Multi-level escalation paths
- 5%: SLAs specified for each level
- 5%: Contact methods documented

**Rollback Procedures (15%)**
- 5%: Rollback triggers defined
- 5%: Rollback steps are actionable
- 5%: Verification checks defined

**Traceability (20%)**
- 5%: REQ reference present
- 5%: Element IDs properly formatted
- 5%: Downstream artifacts specified
- 5%: Cumulative tags complete

## Error Codes

| Code | Severity | Message |
|------|----------|---------|
| PROCSPEC-E001 | Error | File is not valid YAML |
| PROCSPEC-E002 | Error | Missing required field |
| PROCSPEC-E003 | Error | deliverable_type must be 'process' |
| PROCSPEC-E004 | Error | Missing REQ reference |
| PROCSPEC-E005 | Error | No process steps defined |
| PROCSPEC-E006 | Error | Process step missing required field |
| PROCSPEC-E007 | Error | Decision point missing required field |
| PROCSPEC-E008 | Error | Escalation procedure missing required field |
| PROCSPEC-E009 | Error | Rollback procedure missing required field |
| PROCSPEC-E010 | Error | No output_type specified |
| PROCSPEC-W001 | Warning | Element ID format incorrect |
| PROCSPEC-W002 | Warning | Missing SLA in escalation |
| PROCSPEC-W003 | Warning | Missing BDD references |
| PROCSPEC-W004 | Warning | Missing success criteria |
| PROCSPEC-W005 | Warning | CTR missing (if external APIs used) |

## Validation Commands

```bash
# Validate YAML syntax
yamllint PROCSPEC-NN_name.yaml

# Validate against schema
python scripts/validate_spec.py PROCSPEC-NN_name.yaml --schema PROCSPEC_MVP_SCHEMA.yaml

# Calculate PROC-Ready score
python scripts/calculate_readiness.py PROCSPEC-NN_name.yaml --type PROCSPEC
```

---

**Rules Version**: 1.0
**Last Updated**: 2026-03-01
