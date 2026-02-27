---
name: doc-stest-autopilot
description: Automated STEST generation and review orchestration for deployment smoke validation
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - automation-workflow
    - stest
  custom_fields:
    layer: 10
    artifact_type: STEST
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: automation-workflow
    upstream_artifacts: [EARS, BDD, REQ, SPEC]
    downstream_artifacts: [TASKS]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks STEST-MVP-TEMPLATE schema_version"
---

# doc-stest-autopilot

## Purpose

Automate STEST lifecycle for subtype-specific workflows:
- generate STEST from upstream context,
- validate and audit outputs,
- hand off to fixer when required.

---

## Execution Modes

### Generate/Find Mode

Input:
- `STEST-NN` (self type): review existing
- `EARS-NN` or `BDD-NN` or `REQ-NN`: generate if missing, else review existing `STEST-NN`
- optional `SPEC-NN`: include deployment-target consistency checks when present

### Audit/Fix Mode

- Run `doc-stest-audit`
- If fail or below gate, run `doc-stest-fixer`
- Re-run audit until pass or max iteration reached

---

## Orchestration Flow

```text
1) Resolve target STEST document
2) Generate or load STEST
3) Run doc-stest-audit
4) If needed, run doc-stest-fixer
5) Re-audit
6) Emit status and next-step recommendation
```

---

## Naming and Contract Rules

- Primary audit output: `STEST-NN.A_audit_report_vNNN.md`
- Legacy-compatible review output: `STEST-NN.R_review_report_vNNN.md`
- Fix report: `STEST-NN.F_fix_report_vNNN.md`

All reports are stored beside parent STEST in nested folder.

---

## Canonical References

- `ai_dev_ssd_flow/10_TSPEC/STEST/STEST-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/10_TSPEC/STEST/STEST_MVP_CREATION_RULES.md`
- `ai_dev_ssd_flow/10_TSPEC/STEST/STEST_MVP_VALIDATION_RULES.md`
- `ai_dev_ssd_flow/10_TSPEC/scripts/validate_stest.py`

---

## Deployment Gate Constraints

- Total timeout budget must be `<=300s` (max 300s).
- Target: 100% (`100% quality gate`).
- Every test must have rollback procedure.
- Critical path checks must use binary pass/fail criteria.

---

## Coexistence Rules with `doc-tspec-autopilot`

Use `doc-stest-autopilot` when STEST-only scope is required.  
Route to `doc-tspec-autopilot` when cross-subtype orchestration is required.

Fallback:
- If unresolved subtype blockers persist, escalate to `doc-tspec-autopilot` while preserving report compatibility (`.A_` preferred, `.R_` legacy).

---

## Example Invocations

```bash
/doc-stest-autopilot STEST-01
/doc-stest-autopilot EARS-01
/doc-stest-autopilot BDD-01
/doc-stest-autopilot REQ-01
/doc-stest-autopilot SPEC-01
```

---

## Quality Gate

Pass when:
- STEST structure matches 6-section contract,
- required tags are complete,
- timeout/rollback/100%-gate constraints are present,
- binary pass/fail criteria are explicit,
- audit status is PASS under strict gate requirements.

---

## Related Skills

- `doc-stest`
- `doc-stest-validator`
- `doc-stest-reviewer`
- `doc-stest-fixer`
- `doc-stest-audit`
- `doc-tspec-autopilot` (fallback for mixed subtype workflows)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial STEST autopilot skill with explicit input contract, audit-fix orchestration, and strict deployment gate constraints |
