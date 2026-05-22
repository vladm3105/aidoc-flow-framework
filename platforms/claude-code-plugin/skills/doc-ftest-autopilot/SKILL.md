---
name: doc-ftest-autopilot
description: Automated generation and review orchestration for functional-focused TDD (Layer 7) test cases - end-to-end scenarios and quality-attribute thresholds
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - tdd-functional-helper
    - automation-workflow
  custom_fields:
    layer: 7
    artifact_type: TDD
    tdd_focus: functional
    deliverable_type: code
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

# doc-ftest-autopilot

## Purpose

Automate the functional-TDD lifecycle for functional-focused
**TDD (Layer 7)** test cases:
- generate functional TDD test cases from upstream context,
- validate and audit outputs,
- hand off to fixer when required.

This skill is a **TDD (Layer 7) specialization** for the functional-test focus.
It authors TDD documents (Section 4 end-to-end / quality-attribute cases) against
the single canonical artifact contract `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
(see `../doc-tdd/`); it does **not** define a separate artifact, template, or
element-code.

**Layer**: 7 (TDD — functional focus)

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
- `SPEC-NN`: generate functional TDD test cases if missing, else review existing `TDD-NN`

### Audit/Fix Mode

- Run `doc-ftest-audit`
- If fail or below threshold, run `doc-ftest-fixer`
- Re-run audit until pass or max iteration reached

---

## Orchestration Flow

```text
1) Resolve target TDD document
2) Generate or load functional TDD test cases
3) Run doc-ftest-audit
4) If needed, run doc-ftest-fixer
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
   metadata:
     document_type: tdd-document    # NOT "template"
     artifact_type: TDD
     deliverable_type: code
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
- ID & naming standards: `framework/governance/ID_NAMING_STANDARDS.md`
- Parent TDD skill: `../doc-tdd/`

---

## Coexistence with `../doc-tdd/`

Use `doc-ftest-autopilot` when the functional / end-to-end test focus is the
scope. Use the parent `../doc-tdd/` skill for the full unified TDD authoring
contract across all test types. Both author the same single TDD artifact —
report compatibility is preserved (`.A_` preferred, `.R_` legacy).

---

## Example Invocations

```bash
/doc-ftest-autopilot TDD-01
/doc-ftest-autopilot SPEC-01
```

---

## Quality Gate

Pass when:
- TDD structure matches the single 7-section template contract,
- required cumulative upstream tags are complete (no SYS),
- functional test cases (Section 4) and quality-attribute thresholds
  (Section 5) are present and measurable,
- audit status is PASS and IPLAN-Ready score meets the configured threshold
  (>=90/100).

---

## Related Skills

- `doc-ftest`
- `doc-ftest-validator`
- `doc-ftest-reviewer`
- `doc-ftest-fixer`
- `doc-ftest-audit`
- `../doc-tdd/` (parent TDD authoring skill — full unified contract)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer model (D-0015). Repositioned as a TDD (Layer 7) functional-test specialization referencing the single `framework/layers/07_TDD/TDD-TEMPLATE.yaml` — no FTEST/TSPEC artifact, template, or numeric subtype-code. Generates functional/end-to-end TDD test cases; upstream BRD,PRD,EARS,BDD,ADR,SPEC; downstream IPLAN,Code; dropped SYS upstream; report contract retargeted to `TDD-NN.*`. |
| 1.0 | 2026-02-27 | Initial functional-test autopilot (pre-migration legacy model). |
