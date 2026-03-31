---
title: "PROCSPEC MVP Creation Rules"
tags:
  - creation-rules
  - layer-9-artifact
  - procspec-subtype
custom_fields:
  document_type: rules
  artifact_type: PROCSPEC
  layer: 9
  subtype_code: 54
---

# PROCSPEC MVP Creation Rules

## Purpose

Guidelines for creating Process Specification (PROCSPEC) documents - specifications for SOPs, runbooks, playbooks, checklists, and workflows.

## When to Create PROCSPEC

Create a PROCSPEC when:
- REQ document has `deliverable_type: process`
- Requirement results in operational procedure output
- Need to document step-by-step processes
- Need to define escalation and rollback procedures

## Prerequisites

Before creating PROCSPEC:

1. **REQ Document**: Atomic requirement with `deliverable_type: process`
2. **ADR Document**: Architecture decisions for tooling and automation
3. **BDD Scenarios**: Test scenarios for process verification
4. **CTR Document**: Optional (only if external APIs are involved)

## File Naming

```
PROCSPEC-NN_process_name.yaml
```

- `NN`: Sequential number (01, 02, 03...)
- `process_name`: Snake_case, descriptive name

## Required Sections

| Section | Required | Description |
|---------|----------|-------------|
| metadata | Yes | Document control with `deliverable_type: process` |
| traceability | Yes | Must include REQ reference |
| process_overview | Yes | Process type, context, roles |
| process_steps | Yes | At least one step with full details |
| decision_points | No | Decision points if branching exists |
| escalation_procedures | No | Escalation paths if needed |
| rollback_procedures | No | Rollback steps if needed |
| verification | Yes | BDD scenarios and verification checklist |
| implementation | Yes | Output type and path |

## Element ID Format

```
PROCSPEC.{DOC}.{TYPE}.{SEQ}
```

| Code | Type | Example |
|------|------|---------|
| 70 | step | PROCSPEC.01.7bee |
| 71 | decision | PROCSPEC.01.2bf4 |
| 72 | escalation | PROCSPEC.01.dd48 |
| 73 | rollback | PROCSPEC.01.fd41 |

## Process Types

| Type | Description | Typical Use |
|------|-------------|-------------|
| sop | Standard Operating Procedure | Routine operations |
| runbook | Operational Runbook | System operations |
| playbook | Incident Playbook | Incident response |
| checklist | Verification Checklist | Quality checks |
| workflow | Multi-step Workflow | Complex processes |

## Execution Context

| Context | Description |
|---------|-------------|
| manual | Human-executed steps |
| automated | Script/tool-executed steps |
| hybrid | Mix of manual and automated |

## CTR Requirement

PROCSPEC does **not require** CTR by default:
- CTR is optional for process specifications
- Include CTR reference only if external APIs are involved
- If using CTR, reference it in traceability section

## Process Step Requirements

Each process step must include:

| Field | Required | Description |
|-------|----------|-------------|
| id | Yes | Unique element ID (PROCSPEC.NN.70.SS) |
| name | Yes | Step name |
| description | Yes | What to do |
| responsible | Yes | Role/Team responsible |
| prerequisites | No | What must be true before |
| inputs | No | Required inputs |
| outputs | No | Expected outputs |
| actions | No | List of actions |
| success_criteria | No | How to verify success |
| estimated_duration | No | Time estimate |
| next_step | No | Next step ID |

## Decision Point Requirements

Each decision point must include:

| Field | Required | Description |
|-------|----------|-------------|
| id | Yes | Unique element ID (PROCSPEC.NN.71.SS) |
| question | Yes | Decision question |
| options | Yes | Array of options with next_step |
| trigger | No | When this decision is needed |
| decision_maker | No | Role/Team making decision |

## Escalation Procedure Requirements

Each escalation procedure must include:

| Field | Required | Description |
|-------|----------|-------------|
| id | Yes | Unique element ID (PROCSPEC.NN.72.SS) |
| trigger | Yes | When to escalate |
| escalation_path | Yes | Array of escalation levels with SLAs |
| name | No | Escalation name |
| information_required | No | Info to include when escalating |

## Rollback Procedure Requirements

Each rollback procedure must include:

| Field | Required | Description |
|-------|----------|-------------|
| id | Yes | Unique element ID (PROCSPEC.NN.73.SS) |
| trigger | Yes | When to rollback |
| rollback_steps | Yes | Array of rollback steps |
| name | No | Rollback name |
| rollback_owner | No | Role/Team responsible |
| max_rollback_time | No | Time limit for rollback |
| verification | No | Verification checks |

## Quality Gate

**PROC-Ready Score Target**: >= 85%

| Criterion | Weight |
|-----------|--------|
| Step Completeness | 25% |
| Decision Points | 20% |
| Escalation Procedures | 20% |
| Rollback Procedures | 15% |
| Traceability | 20% |

## Validation Checklist

- [ ] `deliverable_type: process` in metadata
- [ ] REQ reference in traceability
- [ ] At least one process step defined
- [ ] All steps have ID, name, description, responsible
- [ ] Decision points have options with next_step
- [ ] Escalation procedures have triggers and SLAs
- [ ] Rollback procedures have triggers and steps
- [ ] BDD scenarios referenced in verification
- [ ] Output type and path specified in implementation

## Best Practices

1. **Step Ordering**: Use sequential IDs (70.01, 70.02, 70.03)
2. **Decision Points**: Include default option for fallback
3. **Escalation SLAs**: Define realistic response times
4. **Rollback Scope**: Define what is and is not rolled back
5. **Automation**: Indicate which steps can be automated

---

**Rules Version**: 1.0
**Last Updated**: 2026-03-01

---

## DEPRECATED: Template+Schema migration (2026-03-24)

This file is deprecated and retained for backward compatibility only.

Active references for MCP and framework tooling must use:
- `*-MVP-TEMPLATE.*`
- `*_MVP_SCHEMA.yaml`

Do not add new dependencies on this file.
