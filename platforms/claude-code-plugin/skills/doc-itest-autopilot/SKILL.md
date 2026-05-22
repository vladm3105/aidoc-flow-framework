---
name: doc-itest-autopilot
description: Automated generation and review orchestration for integration-focused TDD (Layer 7) test cases - contract and interaction validation
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - automation-workflow
    - itest
  custom_fields:
    layer: 7
    artifact_type: TDD
    test_focus: integration
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: automation-workflow
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SPEC]
    downstream_artifacts: [IPLAN, Code]
    version: "2.0"
    last_updated: "2026-05-22"
  versioning_policy: "tracks TDD-TEMPLATE schema_version"
---

# doc-itest-autopilot

## Purpose

Automate the lifecycle of integration-focused **TDD (Layer 7)** test cases:
- generate the TDD document (integration focus) from upstream context,
- validate and audit outputs,
- hand off to fixer when required.

This skill is a **TDD (Layer 7) specialization** (integration-test focus). It
authors TDD documents referencing the single canonical artifact contract
`framework/layers/07_TDD/TDD-TEMPLATE.yaml` (see `../doc-tdd/`); it does **not**
define a separate artifact, template, or element-code.

**Layer**: 7 (TDD — integration-test focus)

**Upstream**: BRD (Layer 1), PRD (Layer 2), EARS (Layer 3), BDD (Layer 4),
ADR (Layer 5), SPEC (Layer 6)

**Downstream**: IPLAN (Layer 8), Code

---

## Input Contract (IPLAN-004 Standard)

- Supported modes:
  - `--ref <path>`
  - `--prompt "<text>"`
  - `--iplan <path|IPLAN-NN>`
- Precedence: `--iplan > --ref > --prompt`
- IPLAN resolution order:
  1. Use explicit file path when it exists
  2. Resolve `plans/IPLAN-NN*.md`
  3. Resolve `governance/plans/IPLAN-NN*.md`
  4. If multiple matches exist, fail with disambiguation request
- Merge conflict rule:
  - Objective/scope conflicts between primary and supplemental sources are blocking and require user clarification.

---

## Execution Modes

### Generate/Find Mode

Input:
- `TDD-NN` (self type): review existing
- `SPEC-NN`: generate the integration-focused TDD if missing, else review existing `TDD-NN`

### Audit/Fix Mode

- Run `doc-itest-audit`
- If fail or below threshold, run `doc-itest-fixer`
- Re-run audit until pass or max iteration reached

---

## Orchestration Flow

```text
1) Resolve target TDD document
2) Generate or load the integration-focused TDD
3) Run doc-itest-audit
4) If needed, run doc-itest-fixer
5) Re-audit
6) Emit status and next-step recommendation
```

---

## Naming and Contract Rules

- Primary audit output: `TDD-NN.A_audit_report_vNNN.md`
- Legacy-compatible review output: `TDD-NN.R_review_report_vNNN.md`
- Fix report: `TDD-NN.F_fix_report_vNNN.md`

All reports are stored beside the parent TDD document in its nested folder.

---

## Document Type Contract (MANDATORY)

When generating TDD document instances, the autopilot MUST:

1. **Read** `document_type` from the canonical template:
   - Source: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
   - Field: `metadata.document_type: "tdd-document"`

2. **Set** `document_type` in generated document frontmatter:
   ```yaml
   metadata:
     document_type: tdd-document    # NOT "template"
     artifact_type: TDD
     layer: 7
   ```
   Each integration test case in Section 4 carries `type: integration`.

3. **Validation**: Generated documents MUST have `document_type: tdd-document`
   - Templates have `document_type: template`
   - Instances have `document_type: tdd-document`

**Error Handling**: If `document_type` is missing from the template, default to
`tdd-document`.

---

## Canonical References

- `framework/layers/07_TDD/TDD-TEMPLATE.yaml` — the single TDD artifact contract
- `framework/layers/07_TDD/README.md` — layer overview
- `framework/governance/ID_NAMING_STANDARDS.md` — element ID and tag formats
- `../doc-tdd/SKILL.md` — the parent TDD authoring skill

---

## Relationship to `../doc-tdd/`

Use `doc-itest-autopilot` when integration-focused TDD scope is required.
Use the parent `../doc-tdd/` authoring skill when a full-spectrum TDD document
(all test types) is required. Both produce TDD (Layer 7) documents against the
same single template; report contracts (`.A_` preferred, `.R_` legacy) remain
compatible.

---

## Example Invocations

```bash
/doc-itest-autopilot TDD-01
/doc-itest-autopilot SPEC-01
```

---

## Quality Gate

Pass when:
- the TDD document matches the 7-section template,
- required cumulative tags are complete (@brd through @spec, plus @tdd),
- contract compliance and interaction checks are present in the integration cases,
- audit status is PASS and score meets the configured threshold (>=90/100).

---

## Related Skills

- `doc-itest`
- `doc-itest-validator`
- `doc-itest-reviewer`
- `doc-itest-fixer`
- `doc-itest-audit`
- `../doc-tdd/` (parent TDD authoring skill — full-spectrum test cases)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer model. Repositioned as a TDD (Layer 7) integration-focus autopilot over the single `framework/layers/07_TDD/TDD-TEMPLATE.yaml` (no separate ITEST/TSPEC artifact, template, or numeric subtype code). Targets/reports keyed to `TDD-NN`; upstream BRD,PRD,EARS,BDD,ADR,SPEC; downstream IPLAN,Code. Dead validation-script references removed (framework is spec-only). |
| 1.0 | 2026-02-27 | Initial autopilot skill with generate/find plus audit-fix orchestration (pre-migration legacy 12-layer model). |
