# Batch SDD Pipeline — Single Feature Branch Execution (BRD→BDD)

## Proven Pattern (TradeGent CC BRD-10, 2026-05-14)

A single new feature BRD can be carried through BRD → PRD → EARS → BDD with inline review
at each layer in one session. This is effective when:

- The feature has clearly scoped upstream BRDs for cross-referencing
- The user prefers batch processing ("yes, fix all issues" → "continue")
- Subagent dispatch is unavailable or would timeout on large documents
- All 4 layers need generation + review + remediation in sequence

## Workflow Sequence

```
PLAN → BRD (create → validate → review → remediate)
    → PRD (create → validate → review → remediate)
    → EARS (create → validate → review → remediate)
    → BDD (create → validate → review → remediate)
    → ADR (generate from BDD deferred findings)
```

## Layer-Specific Review Personas (Inline)

| Layer | Personas | Typical Findings |
|-------|----------|-----------------|
| BRD | architect, auditor, business-analyst, chaos | Missing failure modes, scope boundaries, data validation |
| PRD | architect, auditor, tech-lead, product-owner, chaos | Missing user stories, no mock/test strategy, credential storage |
| EARS | requirements-specialist, tech-lead, qa-lead, chaos | Dual-WITHIN, missing reconciliation failure, compound statements |
| BDD | qa-lead, tech-lead, chaos, SRE, security-auditor | Missing parameterized scenarios, rate-limit tests |

## Per-Layer Remediation Patterns

### Common Fix Types

| Layer | Fix Pattern | Tool |
|-------|------------|------|
| BRD | Add business rules to FR sections, add acceptance criteria, add assumptions | execute_code with string replacement |
| PRD | Add user stories, add tech acceptance criteria, add diagram items | execute_code |
| EARS | Split compound requirements, add unwanted-behavior scenarios | execute_code |
| BDD | Add parameterized Scenario Outlines, add error/recovery scenarios | execute_code |

### Metadata Update After Remediation
All remediated documents need:
- `version`: 1.0 → 1.1
- `status`: Draft → Reviewed
- `last_updated`: current ISO 8601 timestamp
- `revision_history`: prepend new entry with fix summary

### Cross-Layer Consistency Checks
- BRD hashes in PRD must match BRD element IDs
- EARS requirements map 1:1 (or N:1) to PRD capabilities
- BDD spec_trace must reference actual EARS requirement names
- All cumulative tags present (`@brd` + `@prd` for PRD, `@brd` + `@prd` + `@ears` for BDD)

## Quality Gates Per Layer

| Layer | Gate | Minimum |
|-------|------|---------|
| BRD | PRD-Ready | >= 90/100 |
| PRD | EARS-Ready | >= 90/100, 3-7 capabilities, 3-5 user stories, diagram_contract populated |
| EARS | BDD-Ready | >= 90/100, state_machine present if operational modes, 25+ requirements |
| BDD | ADR-Ready | >= 90/100, 5+ scenarios, at least 1 recovery, error handling covered |

## Verification Command

After each layer's remediation, run both:
```
sdd_validate doc_type=<type> document=<path> layer=<0N_TYPE>
sdd_score_show report_file=<path>/.ucx/validate/<DOC>.ucx.validate.json
```

Target: 0 errors, 0 warnings, score >= 90.
