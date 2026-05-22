---
name: doc-utest-autopilot
description: Automated generation and review orchestration for unit-focused TDD (Layer 7) test cases
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - tdd-unit-helper
    - automation-workflow
  custom_fields:
    layer: 7
    artifact_type: TDD
    test_focus: unit
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: automation-workflow
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SPEC]
    downstream_artifacts: [IPLAN, Code]
    version: "2.0"
    last_updated: "2026-05-22"
---

# doc-utest-autopilot

## Purpose

Automate the unit-focused **TDD (Layer 7)** lifecycle:
- generate unit-focused TDD test cases from upstream context,
- validate and audit outputs,
- hand off to fixer when required.

This skill is a **TDD (Layer 7) specialization** for the unit-test focus of TDD.
It generates against the single canonical artifact contract
(`framework/layers/07_TDD/TDD-TEMPLATE.yaml`, see `../doc-tdd/`) and does **not**
define a separate artifact, template, or element-code.

**Layer**: 7 (TDD — unit-test focus)

**Upstream**: BRD (Layer 1), PRD (Layer 2), EARS (Layer 3), BDD (Layer 4),
ADR (Layer 5), SPEC (Layer 6)

**Downstream**: IPLAN (Layer 8), Code

---

## Input Contract (IPLAN Standard)

- Supported modes:
  - `--ref <path>`
  - `--prompt "<text>"`
  - `--iplan <path|IPLAN-NN>`
- Precedence: `--iplan > --ref > --prompt`
- IPLAN resolution order:
  1. Use the explicit file path when it exists
  2. Resolve `plans/IPLAN-NN*.md`
  3. Resolve `governance/plans/IPLAN-NN*.md`
  4. If multiple matches exist, fail with a disambiguation request
- Merge conflict rule:
  - Objective/scope conflicts between primary and supplemental sources are
    blocking and require user clarification.

---

## Execution Modes

### Generate/Find Mode

Input:
- `TDD-NN` (self type): review existing
- `SPEC-NN`: generate unit cases if missing, else review existing `TDD-NN`
- upstream `BDD-NN`: include scenario-to-unit-test mapping when present

### Audit/Fix Mode

- Run `doc-utest-audit`
- If fail or below gate, run `doc-utest-fixer`
- Re-run audit until pass or max iteration reached

---

## Orchestration Flow

```text
1) Resolve target TDD document
2) Generate or load unit-focused TDD test cases
3) Run doc-utest-audit
4) If needed, run doc-utest-fixer
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

1. **Read** the document type from the canonical template:
   - Source: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
   - Field: `metadata.document_type: "tdd-document"`

2. **Set** the document type in generated document frontmatter:
   ```yaml
   metadata:
     document_type: tdd-document    # NOT "template"
     artifact_type: TDD
     test_focus: unit
     layer: 7
   ```

3. **Validation**: Generated documents MUST have `document_type: tdd-document`;
   templates have `document_type: template`.

**Error Handling**: If the document type is missing from the template, default
to `tdd-document`.

---

## Canonical References

- Canonical TDD artifact contract: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
- Layer overview: `framework/layers/07_TDD/README.md`
- Governance / ID & naming standards: `framework/governance/`
- Parent TDD skill: `../doc-tdd/`

---

## Unit-Test Gate Constraints

- IPLAN-Ready score target must be `>=90`.
- Unit coverage target must be `>=90%`.
- Unit cases must cover logic, state, validation, and edge conditions.
- Every unit case requires concrete inputs and expected outputs.
- Complex logic requires documented edge cases.

---

## Example Invocations

```bash
/doc-utest-autopilot TDD-01
/doc-utest-autopilot SPEC-01
```

---

## Quality Gate

Pass when:
- unit-focused TDD test cases match the `TDD-TEMPLATE.yaml` contract,
- required tags are complete (`@brd`..`@spec`, `@tdd` self-tag),
- unit coverage and IPLAN-Ready score meet `>=90`/`>=90%`,
- inputs/outputs and edge-case requirements are met,
- audit status is PASS under the unit-test gate requirements.

---

## Related Skills

- `doc-utest`
- `doc-utest-validator`
- `doc-utest-reviewer`
- `doc-utest-fixer`
- `doc-utest-audit`
- `../doc-tdd/` (parent TDD authoring skill)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer TDD model (Layer 7). Generates unit-focused TDD test cases from `framework/layers/07_TDD/TDD-TEMPLATE.yaml` (no UTEST/TSPEC artifact or numeric code); upstream BRD,PRD,EARS,BDD,ADR,SPEC; downstream IPLAN,Code; dead validation scripts removed; audit-fix orchestration and IPLAN input contract retained. |
| 1.0 | 2026-02-27 | Initial unit-test autopilot (pre-migration legacy layer). |
