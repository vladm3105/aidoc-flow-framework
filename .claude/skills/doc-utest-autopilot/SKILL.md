---
name: doc-utest-autopilot
description: Automated UTEST generation and review orchestration for component-level unit test workflows
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - automation-workflow
    - utest
  custom_fields:
    layer: 10
    artifact_type: UTEST
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: automation-workflow
    upstream_artifacts: [REQ, SPEC, CTR]
    downstream_artifacts: [TASKS]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks UTEST-MVP-TEMPLATE schema_version"
---

# doc-utest-autopilot

## Purpose

Automate UTEST lifecycle for subtype-specific workflows:
- generate UTEST from upstream context,
- validate and audit outputs,
- hand off to fixer when required.

---

## Input Contract (IPLAN-004 Standard)

- Supported modes:
  - `--ref <path>`
  - `--prompt "<text>"`
  - `--iplan <path|IPLAN-NNN>`
- Precedence: `--iplan > --ref > --prompt`
- IPLAN resolution order:
  1. Use explicit file path when it exists
  2. Resolve `work_plans/IPLAN-NNN*.md`
  3. Resolve `governance/plans/IPLAN-NNN*.md`
  4. If multiple matches exist, fail with disambiguation request
- Merge conflict rule:
  - Objective/scope conflicts between primary and supplemental sources are blocking and require user clarification.

---

## Execution Modes

### Generate/Find Mode

Input:
- `UTEST-NN` (self type): review existing
- `REQ-NN` or `SPEC-NN`: generate if missing, else review existing `UTEST-NN`
- optional `CTR-NN`: include contract-alignment checks when present

### Audit/Fix Mode

- Run `doc-utest-audit`
- If fail or below gate, run `doc-utest-fixer`
- Re-run audit until pass or max iteration reached

---

## Orchestration Flow

```text
1) Resolve target UTEST document
2) Generate or load UTEST
3) Run doc-utest-audit
4) If needed, run doc-utest-fixer
5) Re-audit
6) Emit status and next-step recommendation
```

---

## Naming and Contract Rules

- Primary audit output: `UTEST-NN.A_audit_report_vNNN.md`
- Legacy-compatible review output: `UTEST-NN.R_review_report_vNNN.md`
- Fix report: `UTEST-NN.F_fix_report_vNNN.md`

All reports are stored beside parent UTEST in nested folder.

---

## Canonical References

- `ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST_MVP_CREATION_RULES.md`
- `ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST_MVP_VALIDATION_RULES.md`
- `ai_dev_ssd_flow/10_TSPEC/scripts/validate_utest.py`

---

## Unit-Test Gate Constraints

- TASKS-Ready score target must be `>=90%`.
- REQ coverage target must be `>=90%`.
- Required categories: `[Logic]`, `[State]`, `[Validation]`, `[Edge]`.
- Every test case requires Input/Output table.
- Complex logic requires pseudocode.

---

## Coexistence Rules with `doc-tspec-autopilot`

Use `doc-utest-autopilot` when UTEST-only scope is required.  
Route to `doc-tspec-autopilot` when cross-subtype orchestration is required.

Fallback:
- If unresolved subtype blockers persist, escalate to `doc-tspec-autopilot` while preserving report compatibility (`.A_` preferred, `.R_` legacy).

---

## Example Invocations

```bash
/doc-utest-autopilot UTEST-01
/doc-utest-autopilot REQ-01
/doc-utest-autopilot SPEC-01
/doc-utest-autopilot CTR-01
```

---

## Quality Gate

Pass when:
- UTEST structure matches 6-section contract,
- required tags are complete,
- REQ coverage and TASKS-Ready score meet `>=90%`,
- I/O tables and pseudocode requirements are met,
- audit status is PASS under UTEST gate requirements.

---

## Related Skills

- `doc-utest`
- `doc-utest-validator`
- `doc-utest-reviewer`
- `doc-utest-fixer`
- `doc-utest-audit`
- `doc-tspec-autopilot` (fallback for mixed subtype workflows)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial UTEST autopilot skill with explicit input contract, audit-fix orchestration, and UTEST-specific 90% gate constraints |
