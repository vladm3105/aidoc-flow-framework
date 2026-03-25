---
name: doc-sectest-autopilot
description: Automated SECTEST generation and review orchestration for security threat and control validation
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - automation-workflow
    - sectest
  custom_fields:
    layer: 10
    artifact_type: SECTEST
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: automation-workflow
    upstream_artifacts: [SYS, SPEC, CTR]
    downstream_artifacts: [TASKS]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks SECTEST-MVP-TEMPLATE schema_version"
---

# doc-sectest-autopilot

## Purpose

Automate SECTEST lifecycle for subtype-specific workflows:
- generate SECTEST from upstream context,
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
- `SECTEST-NN` (self type): review existing
- `SYS-NN` or `SPEC-NN`: generate if missing, else review existing `SECTEST-NN`
- optional `CTR-NN`: include contract-alignment checks when present

### Audit/Fix Mode

- Run `doc-sectest-audit`
- If fail or below threshold, run `doc-sectest-fixer`
- Re-run audit until pass or max iteration reached

---

## Orchestration Flow

```text
1) Resolve target SECTEST document
2) Generate or load SECTEST
3) Run doc-sectest-audit
4) If needed, run doc-sectest-fixer
5) Re-audit
6) Emit status and next-step recommendation
```

---

## Naming and Contract Rules

- Primary audit output: `SECTEST-NN.A_audit_report_vNNN.md`
- Legacy-compatible review output: `SECTEST-NN.R_review_report_vNNN.md`
- Fix report: `SECTEST-NN.F_fix_report_vNNN.md`

All reports are stored beside parent SECTEST in nested folder.

---

## Document Type Contract (MANDATORY)

When generating SECTEST document instances, the autopilot MUST:

1. **Read** `instance_document_type` from template:
   - Source: `ai_dev_ssd_flow/10_TSPEC/SECTEST/SECTEST-MVP-TEMPLATE.yaml`
   - Field: `metadata.instance_document_type: "sectest-document"`

2. **Set** `document_type` in generated document frontmatter:
   ```yaml
   custom_fields:
     document_type: sectest-document    # NOT "template"
     artifact_type: SECTEST
     layer: 10
     test_type_code: 45
   ```

3. **Validation**: Generated documents MUST have `document_type: sectest-document`
   - Templates have `document_type: template`
   - Instances have `document_type: sectest-document`
   - Schema validates both values

**Error Handling**: If `instance_document_type` is missing from template, default to `sectest-document`.

---

## Canonical References

- `ai_dev_ssd_flow/10_TSPEC/SECTEST/SECTEST-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/10_TSPEC/SECTEST/SECTEST-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/10_TSPEC/SECTEST/SECTEST_MVP_SCHEMA.yaml`
- `ai_dev_ssd_flow/10_TSPEC/scripts/validate_sectest.py`

---

## Safety Constraints

- Security tests must run in isolated environments only.
- Never run security tests against production systems.
- Unsafe guidance markers (`against production`, `exploit execution`, `offensive payload execution`) are disallowed.

---

## Coexistence Rules with `doc-tspec-autopilot`

Use `doc-sectest-autopilot` when SECTEST-only scope is required.  
Route to `doc-tspec-autopilot` when cross-subtype orchestration is required.

Fallback:
- If unresolved subtype blockers persist, escalate to `doc-tspec-autopilot` while preserving report compatibility (`.A_` preferred, `.R_` legacy).

---

## Example Invocations

```bash
/doc-sectest-autopilot SECTEST-01
/doc-sectest-autopilot SYS-01
/doc-sectest-autopilot SPEC-01
/doc-sectest-autopilot CTR-01
```

---

## Quality Gate

Pass when:
- SECTEST structure matches 6-section contract,
- required tags are complete,
- security categories, threat scenarios, and control checks are represented,
- safety constraints are explicitly preserved,
- audit status is PASS and score meets configured threshold.

---

## Related Skills

- `doc-sectest`
- `doc-sectest-validator`
- `doc-sectest-reviewer`
- `doc-sectest-fixer`
- `doc-sectest-audit`
- `doc-tspec-autopilot` (fallback for mixed subtype workflows)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial SECTEST autopilot skill with generate/find plus audit-fix orchestration, explicit input contract, and safety constraints |
