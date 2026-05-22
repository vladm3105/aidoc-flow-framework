---
name: doc-ptest-autopilot
description: Automated generation and review orchestration for performance-focused TDD (Layer 7) test cases - performance category and threshold validation
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - tdd-performance-helper
    - automation-workflow
  custom_fields:
    layer: 7
    artifact_type: TDD
    test_focus: performance
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

# doc-ptest-autopilot

## Purpose

Automate the lifecycle for performance-focused **TDD (Layer 7)** test cases:
- generate performance test cases from upstream context,
- validate and audit outputs,
- hand off to fixer when required.

This skill is a **TDD (Layer 7) specialization** for the performance-test
focus. It authors TDD documents with a performance emphasis and references the
single canonical artifact contract `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
(see `../doc-tdd/`); it does **not** define a separate artifact, template, or
element-code.

**Layer**: 7 (TDD — performance focus)

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
- `SPEC-NN`: generate performance test cases if missing, else review existing `TDD-NN`

### Audit/Fix Mode

- Run `doc-ptest-audit`
- If fail or below threshold, run `doc-ptest-fixer`
- Re-run audit until pass or max iteration reached

---

## Orchestration Flow

```text
1) Resolve target TDD document
2) Generate or load performance-focused TDD test cases
3) Run doc-ptest-audit
4) If needed, run doc-ptest-fixer
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

Performance test cases live in Section 4 with a `type` attribute and a scenario
label (Load/Stress/Endurance/Spike) — NOT a separate artifact or element-code.

---

## Canonical References

- Canonical TDD artifact contract: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
- Layer overview: `framework/layers/07_TDD/README.md`
- Performance threshold rules: `framework/governance/THRESHOLD_NAMING_RULES.md`
- Parent TDD skill: `../doc-tdd/`

---

## Coexistence Rules with `../doc-tdd/`

Use `doc-ptest-autopilot` when a performance-test focus is required.
Route to `../doc-tdd/` (or its autopilot) when authoring general
functional unit/integration/e2e test cases is primary.

Fallback:
- If unresolved blockers persist, escalate to `../doc-tdd/` while preserving
  report compatibility (`.A_` preferred, `.R_` legacy).

---

## Example Invocations

```bash
/doc-ptest-autopilot TDD-01
/doc-ptest-autopilot SPEC-01
```

---

## Quality Gate

Pass when:
- TDD structure matches `framework/layers/07_TDD/TDD-TEMPLATE.yaml` (7 sections),
- required cumulative tags are complete (`@brd`..`@spec` + `@tdd`),
- performance scenario categories and measurable `@threshold:`-tagged targets are represented,
- audit status is PASS and score meets the configured threshold.

---

## Related Skills

- `doc-ptest`
- `doc-ptest-validator`
- `doc-ptest-reviewer`
- `doc-ptest-fixer`
- `doc-ptest-audit`
- `../doc-tdd/` (parent TDD authoring skill)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer model. Repositioned as a TDD (Layer 7) performance-test autopilot over the single `framework/layers/07_TDD/TDD-TEMPLATE.yaml` (no PTEST/TSPEC artifact, subtype code, or `test_type_code`). Upstream BRD,PRD,EARS,BDD,ADR,SPEC; downstream IPLAN; report contract emits `TDD-NN.*`. |
| 1.0 | 2026-02-27 | Initial PTEST autopilot skill (pre-migration, legacy 12-layer model). |
