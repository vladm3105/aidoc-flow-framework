---
name: doc-itest-autopilot
description: Automated ITEST generation and review orchestration for integration contract and interaction validation
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - automation-workflow
    - itest
  custom_fields:
    layer: 10
    artifact_type: ITEST
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: automation-workflow
    upstream_artifacts: [CTR, SYS, SPEC]
    downstream_artifacts: [TASKS]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks ITEST-MVP-TEMPLATE schema_version"
---

# doc-itest-autopilot

## Purpose

Automate ITEST lifecycle for subtype-specific workflows:
- generate ITEST from upstream context,
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
- `ITEST-NN` (self type): review existing
- `CTR-NN`, `SYS-NN`, or `SPEC-NN`: generate if missing, else review existing `ITEST-NN`

### Audit/Fix Mode

- Run `doc-itest-audit`
- If fail or below threshold, run `doc-itest-fixer`
- Re-run audit until pass or max iteration reached

---

## Orchestration Flow

```text
1) Resolve target ITEST document
2) Generate or load ITEST
3) Run doc-itest-audit
4) If needed, run doc-itest-fixer
5) Re-audit
6) Emit status and next-step recommendation
```

---

## Naming and Contract Rules

- Primary audit output: `ITEST-NN.A_audit_report_vNNN.md`
- Legacy-compatible review output: `ITEST-NN.R_review_report_vNNN.md`
- Fix report: `ITEST-NN.F_fix_report_vNNN.md`

All reports are stored beside parent ITEST in nested folder.

---

## Document Type Contract (MANDATORY)

When generating ITEST document instances, the autopilot MUST:

1. **Read** `instance_document_type` from template:
   - Source: `ai_dev_ssd_flow/10_TSPEC/ITEST/ITEST-MVP-TEMPLATE.yaml`
   - Field: `metadata.instance_document_type: "itest-document"`

2. **Set** `document_type` in generated document frontmatter:
   ```yaml
   custom_fields:
     document_type: itest-document    # NOT "template"
     artifact_type: ITEST
     layer: 10
     test_type_code: 41
   ```

3. **Validation**: Generated documents MUST have `document_type: itest-document`
   - Templates have `document_type: template`
   - Instances have `document_type: itest-document`
   - Schema validates both values

**Error Handling**: If `instance_document_type` is missing from template, default to `itest-document`.

---

## Canonical References

- `ai_dev_ssd_flow/10_TSPEC/ITEST/ITEST-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/10_TSPEC/ITEST/ITEST_MVP_CREATION_RULES.md`
- `ai_dev_ssd_flow/10_TSPEC/ITEST/ITEST_MVP_VALIDATION_RULES.md`
- `ai_dev_ssd_flow/10_TSPEC/scripts/validate_itest.py`

---

## Coexistence Rules with `doc-tspec-autopilot`

Use `doc-itest-autopilot` when ITEST-only scope is required.  
Route to `doc-tspec-autopilot` when cross-subtype orchestration is required.

Fallback:
- If unresolved subtype blockers persist, escalate to `doc-tspec-autopilot` while preserving report compatibility (`.A_` preferred, `.R_` legacy).

---

## Example Invocations

```bash
/doc-itest-autopilot ITEST-01
/doc-itest-autopilot CTR-01
/doc-itest-autopilot SYS-01
/doc-itest-autopilot SPEC-01
```

---

## Quality Gate

Pass when:
- ITEST structure matches 6-section contract,
- required tags are complete,
- contract compliance and interaction checks are present,
- audit status is PASS and score meets configured threshold.

---

## Related Skills

- `doc-itest`
- `doc-itest-validator`
- `doc-itest-reviewer`
- `doc-itest-fixer`
- `doc-itest-audit`
- `doc-tspec-autopilot` (fallback for mixed subtype workflows)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial ITEST autopilot skill with generate/find plus audit-fix orchestration, versioned report contracts, and TSPEC coexistence routing |
