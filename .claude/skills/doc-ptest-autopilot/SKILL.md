---
name: doc-ptest-autopilot
description: Automated PTEST generation and review orchestration for performance category and threshold validation
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - automation-workflow
    - ptest
  custom_fields:
    layer: 10
    artifact_type: PTEST
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: automation-workflow
    upstream_artifacts: [SYS, SPEC]
    downstream_artifacts: [TASKS]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks PTEST-MVP-TEMPLATE schema_version"
---

# doc-ptest-autopilot

## Purpose

Automate PTEST lifecycle for subtype-specific workflows:
- generate PTEST from upstream context,
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
- `PTEST-NN` (self type): review existing
- `SYS-NN` or `SPEC-NN`: generate if missing, else review existing `PTEST-NN`

### Audit/Fix Mode

- Run `doc-ptest-audit`
- If fail or below threshold, run `doc-ptest-fixer`
- Re-run audit until pass or max iteration reached

---

## Orchestration Flow

```text
1) Resolve target PTEST document
2) Generate or load PTEST
3) Run doc-ptest-audit
4) If needed, run doc-ptest-fixer
5) Re-audit
6) Emit status and next-step recommendation
```

---

## Naming and Contract Rules

- Primary audit output: `PTEST-NN.A_audit_report_vNNN.md`
- Legacy-compatible review output: `PTEST-NN.R_review_report_vNNN.md`
- Fix report: `PTEST-NN.F_fix_report_vNNN.md`

All reports are stored beside parent PTEST in nested folder.

---

## Canonical References

- `ai_dev_ssd_flow/10_TSPEC/PTEST/PTEST-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/10_TSPEC/PTEST/PTEST_MVP_CREATION_RULES.md`
- `ai_dev_ssd_flow/10_TSPEC/PTEST/PTEST_MVP_VALIDATION_RULES.md`
- `ai_dev_ssd_flow/10_TSPEC/scripts/validate_ptest.py`

---

## Coexistence Rules with `doc-tspec-autopilot`

Use `doc-ptest-autopilot` when PTEST-only scope is required.  
Route to `doc-tspec-autopilot` when cross-subtype orchestration is required.

Fallback:
- If unresolved subtype blockers persist, escalate to `doc-tspec-autopilot` while preserving report compatibility (`.A_` preferred, `.R_` legacy).

---

## Example Invocations

```bash
/doc-ptest-autopilot PTEST-01
/doc-ptest-autopilot SYS-01
/doc-ptest-autopilot SPEC-01
```

---

## Quality Gate

Pass when:
- PTEST structure matches 6-section contract,
- required tags are complete,
- performance categories and thresholds are represented,
- audit status is PASS and score meets configured threshold.

---

## Related Skills

- `doc-ptest`
- `doc-ptest-validator`
- `doc-ptest-reviewer`
- `doc-ptest-fixer`
- `doc-ptest-audit`
- `doc-tspec-autopilot` (fallback for mixed subtype workflows)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial PTEST autopilot skill with generate/find plus audit-fix orchestration, versioned report contracts, and TSPEC coexistence routing |
