---
name: doc-stest-autopilot
description: Automated smoke-focused TDD (Layer 7) generation and review orchestration for deployment smoke validation
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - tdd-smoke-helper
    - automation-workflow
  custom_fields:
    layer: 7
    artifact_type: TDD
    test_focus: smoke
    deliverable_type: code
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: automation-workflow
    upstream_artifacts: [EARS, BDD, ADR, SPEC]
    downstream_artifacts: [IPLAN]
    version: "2.0"
    last_updated: "2026-05-22"
  versioning_policy: "tracks TDD-TEMPLATE schema_version"
---

# doc-stest-autopilot

## Purpose

Automate the lifecycle of **smoke-focused TDD (Layer 7)** test cases:
- generate smoke-focused TDD test cases from upstream context,
- validate and audit outputs,
- hand off to fixer when required.

This skill is a **TDD (Layer 7) specialization**. It orchestrates TDD documents
whose test cases carry a smoke / deployment critical-path focus; it does **not**
define a separate artifact, template, or element-code. The canonical artifact
contract is `framework/layers/07_TDD/TDD-TEMPLATE.yaml` (see `../doc-tdd/`).

**Layer**: 7 (TDD — smoke focus)

---

## Input Contract (IPLAN-004 Standard)

- Supported modes:
  - `--ref <path>`
  - `--prompt "<text>"`
  - `--iplan <path|IPLAN-NN>`
- Precedence: `--iplan > --ref > --prompt`
- IPLAN resolution order:
  1. Use explicit file path when it exists
  2. Resolve `plans/IPLAN-NN*.yaml`
  3. Resolve `governance/plans/IPLAN-NN*.yaml`
  4. If multiple matches exist, fail with disambiguation request
- Merge conflict rule:
  - Objective/scope conflicts between primary and supplemental sources are blocking and require user clarification.

---

## Execution Modes

### Generate/Find Mode

Input:
- `TDD-NN` (self type): review existing
- `EARS-NN` or `BDD-NN`: generate if missing, else review existing `TDD-NN`
- optional `SPEC-NN`: include deployment-target consistency checks when present

### Audit/Fix Mode

- Run `doc-stest-audit`
- If fail or below gate, run `doc-stest-fixer`
- Re-run audit until pass or max iteration reached

---

## Orchestration Flow

```text
1) Resolve target TDD document
2) Generate or load smoke-focused TDD test cases
3) Run doc-stest-audit
4) If needed, run doc-stest-fixer
5) Re-audit
6) Emit status and next-step recommendation
```

---

## Naming and Contract Rules

- Primary audit output: `TDD-NN.A_audit_report_vNNN.md`
- Legacy-compatible review output: `TDD-NN.R_review_report_vNNN.md`
- Fix report: `TDD-NN.F_fix_report_vNNN.md`

All reports are stored beside the parent TDD document.

---

## Document Type Contract (MANDATORY)

When generating TDD document instances, the autopilot MUST:

1. **Read** `document_type` from the canonical template:
   - Source: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
   - Field: `metadata.document_type: "tdd-document"`

2. **Set** `document_type` in generated document frontmatter:
   ```yaml
   custom_fields:
     document_type: tdd-document    # NOT "template"
     artifact_type: TDD
     test_focus: smoke
     layer: 7
   ```

3. **Validation**: Generated documents MUST have `document_type: tdd-document`
   - Templates have `document_type: template`
   - Instances have `document_type: tdd-document`

**Error Handling**: If `document_type` is missing from the template, default to `tdd-document`.

---

## Canonical References

- Canonical TDD artifact contract: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
- Layer overview: `framework/layers/07_TDD/README.md`
- ID & tag standards: `framework/governance/ID_NAMING_STANDARDS.md`
- Parent TDD skill: `../doc-tdd/`

---

## Deployment Gate Constraints (smoke focus)

- Total smoke timeout budget should be `<=300s` (max 300s).
- Critical-path target: 100% (`100% quality gate`).
- Every critical-path test case must declare a rollback procedure.
- Critical-path checks must use binary pass/fail criteria.

---

## Coexistence Rules with `../doc-tdd/`

Use `doc-stest-autopilot` when a smoke / deployment critical-path focus is
required. Route to `../doc-tdd/` (and its autopilot) for full-suite TDD
authoring across unit/integration/e2e/security types.

Fallback:
- If unresolved blockers persist, escalate to the full TDD autopilot while
  preserving report compatibility (`.A_` preferred, `.R_` legacy).

---

## Example Invocations

```bash
/doc-stest-autopilot TDD-01
/doc-stest-autopilot EARS-01
/doc-stest-autopilot BDD-01
/doc-stest-autopilot SPEC-01
```

---

## Quality Gate

Pass when:
- TDD structure matches the 7-section template,
- required cumulative tags are complete (`@brd`..`@spec` + `@tdd`),
- smoke timeout/rollback/100%-gate constraints are present,
- binary pass/fail criteria are explicit,
- audit status is PASS under strict gate requirements.

---

## Related Skills

- `doc-stest`
- `doc-stest-validator`
- `doc-stest-reviewer`
- `doc-stest-fixer`
- `doc-stest-audit`
- `../doc-tdd/` (full-suite TDD authoring)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer model (D-0015). Repositioned as a TDD (Layer 7) smoke-focus autopilot over `TDD-NN` documents; dropped the legacy smoke-test subtype identity, numeric subtype code, legacy flow paths, dead validation scripts, and the retired upstream layers. References `framework/layers/07_TDD/TDD-TEMPLATE.yaml`; downstream IPLAN. |
| 1.0 | 2026-02-27 | Initial smoke-test autopilot skill (pre-migration). |
