---
name: doc-ftest-autopilot
description: Automated FTEST generation and review orchestration for functional quality-attribute test specifications
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - automation-workflow
    - ftest
  custom_fields:
    layer: 10
    artifact_type: FTEST
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: automation-workflow
    upstream_artifacts: [SYS, REQ, SPEC]
    downstream_artifacts: [TASKS]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks FTEST-MVP-TEMPLATE schema_version"
---

# doc-ftest-autopilot

## Purpose

Automate FTEST lifecycle for subtype-specific workflows:
- generate FTEST from upstream context,
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
- `FTEST-NN` (self type): review existing
- `SPEC-NN` or `SYS-NN`: generate if missing, else review existing `FTEST-NN`

### Audit/Fix Mode

- Run `doc-ftest-audit`
- If fail or below threshold, run `doc-ftest-fixer`
- Re-run audit until pass or max iteration reached

---

## Orchestration Flow

```text
1) Resolve target FTEST document
2) Generate or load FTEST
3) Run doc-ftest-audit
4) If needed, run doc-ftest-fixer
5) Re-audit
6) Emit status and next-step recommendation
```

---

## Naming and Contract Rules

- Primary audit output: `FTEST-NN.A_audit_report_vNNN.md`
- Legacy-compatible review output: `FTEST-NN.R_review_report_vNNN.md`
- Fix report: `FTEST-NN.F_fix_report_vNNN.md`

All reports are stored beside parent FTEST in nested folder.

---

## Document Type Contract (MANDATORY)

When generating FTEST document instances, the autopilot MUST:

1. **Read** `instance_document_type` from template:
   - Source: `ai_dev_ssd_flow/10_TSPEC/FTEST/FTEST-MVP-TEMPLATE.yaml`
   - Field: `metadata.instance_document_type: "ftest-document"`

2. **Set** `document_type` in generated document frontmatter:
   ```yaml
   custom_fields:
     document_type: ftest-document    # NOT "template"
     artifact_type: FTEST
     layer: 10
     test_type_code: 43
   ```

3. **Validation**: Generated documents MUST have `document_type: ftest-document`
   - Templates have `document_type: template`
   - Instances have `document_type: ftest-document`
   - Schema validates both values

**Error Handling**: If `instance_document_type` is missing from template, default to `ftest-document`.

---

## Canonical References

- `ai_dev_ssd_flow/10_TSPEC/FTEST/FTEST-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/10_TSPEC/FTEST/FTEST-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/10_TSPEC/FTEST/FTEST_MVP_SCHEMA.yaml`
- `ai_dev_ssd_flow/10_TSPEC/scripts/validate_ftest.py`

---

## Coexistence Rules with `doc-tspec-autopilot`

Use `doc-ftest-autopilot` when FTEST-only scope is required.  
Route to `doc-tspec-autopilot` when cross-subtype orchestration is required.

Fallback:
- If unresolved subtype blockers persist, escalate to `doc-tspec-autopilot` while preserving report compatibility (`.A_` preferred, `.R_` legacy).

---

## Example Invocations

```bash
/doc-ftest-autopilot FTEST-01
/doc-ftest-autopilot SPEC-01
/doc-ftest-autopilot SYS-01
```

---

## Quality Gate

Pass when:
- FTEST structure matches 6-section contract,
- required tags are complete,
- threshold validation content is present,
- audit status is PASS and score meets configured threshold.

---

## Related Skills

- `doc-ftest`
- `doc-ftest-validator`
- `doc-ftest-reviewer`
- `doc-ftest-fixer`
- `doc-ftest-audit`
- `doc-tspec-autopilot` (fallback for mixed subtype workflows)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial FTEST autopilot skill with generate/find plus audit-fix orchestration; versioned report contracts and TSPEC coexistence routing |
