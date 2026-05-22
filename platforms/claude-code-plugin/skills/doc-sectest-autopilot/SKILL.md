---
name: doc-sectest-autopilot
description: Automated generation and review orchestration of security-focused TDD (Layer 7) test cases for threat and control validation
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - tdd-security-helper
    - automation-workflow
  custom_fields:
    layer: 7
    artifact_type: TDD
    test_focus: security
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: automation-workflow
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SPEC]
    downstream_artifacts: [IPLAN, Code]
    version: "2.0"
    last_updated: "2026-05-22"
---

# doc-sectest-autopilot

## Purpose

Automated pipeline that generates **security-focused TDD** test cases — the
security-test specialization of TDD (Layer 7). It processes upstream artifacts
to author threat scenarios, security control validation, and vulnerability
test cases inside the parent TDD document, then validates and audits them.

This skill is a **TDD (Layer 7) specialization**. It authors TDD test cases
with a security focus and references the single canonical artifact contract
`framework/layers/07_TDD/TDD-TEMPLATE.yaml` (see `../doc-tdd/`); it does **not**
define a separate artifact, template, or element-code. Security tests are the
`security` `type` of TDD test cases.

**Layer**: 7 (TDD — security-test focus)

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
  - Objective/scope conflicts between primary and supplemental sources are
    blocking and require user clarification.

---

## Execution Modes

### Generate/Find Mode

Input:
- `TDD-NN` (self type): review existing security cases
- `SPEC-NN`: generate security cases if missing, else review existing `TDD-NN`
- optional `ADR-NN`: include security-decision alignment checks when present

### Audit/Fix Mode

- Run `doc-sectest-audit`
- If fail or below threshold, run `doc-sectest-fixer`
- Re-run audit until pass or max iteration reached

---

## Orchestration Flow

```text
1) Resolve target TDD document
2) Generate or load security-focused TDD test cases
3) Run doc-sectest-audit
4) If needed, run doc-sectest-fixer
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
     layer: 7
   ```

3. **Validation**: Generated documents MUST have `document_type: tdd-document`.
   Security test cases carry a `type: security` attribute — NOT a separate
   numeric code.

**Error Handling**: If `document_type` is missing from the template, default to
`tdd-document`.

---

## Canonical References

- Canonical TDD artifact contract: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
- Layer overview: `framework/layers/07_TDD/README.md`
- Parent TDD skill: `../doc-tdd/`
- Governance / ID & naming standards: `framework/governance/`

---

## Safety Constraints

- Security tests must run in isolated environments only.
- Never run security tests against production systems.
- Unsafe guidance markers (`against production`, `exploit execution`,
  `offensive payload execution`) are disallowed.

---

## Coexistence Rules with `../doc-tdd/`

Use `doc-sectest-autopilot` when security-only TDD authoring scope is required.
Route to `../doc-tdd/` when the full TDD document spanning all test types
(unit, integration, e2e, security) is required.

Fallback:
- If unresolved blockers persist, escalate to `../doc-tdd/` while preserving
  report compatibility (`.A_` preferred, `.R_` legacy).

---

## Example Invocations

```bash
/doc-sectest-autopilot TDD-01
/doc-sectest-autopilot SPEC-01
/doc-sectest-autopilot ADR-01
```

---

## Quality Gate

Pass when:
- Security test cases match the TDD template (`type: security`, Section 4),
- required cumulative tags are complete (`@brd`..`@spec` plus `@tdd`),
- security categories, threat scenarios, and control checks are represented,
- safety constraints are explicitly preserved,
- audit status is PASS and IPLAN-Ready score meets `>=90`.

---

## Related Skills

- `doc-sectest`
- `doc-sectest-validator`
- `doc-sectest-reviewer`
- `doc-sectest-fixer`
- `doc-sectest-audit`
- `../doc-tdd/` (parent TDD authoring skill — full document, all test types)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer TDD model (Layer 7). Repositioned as a security-test-focused TDD autopilot referencing `framework/layers/07_TDD/TDD-TEMPLATE.yaml` (no separate SECTEST/TSPEC artifact, template, or numeric code; `type: security` cases). Upstream BRD,PRD,EARS,BDD,ADR,SPEC; downstream IPLAN. Dead validation scripts removed; safety constraints preserved. |
| 1.0 | 2026-02-27 | Initial security-test autopilot (pre-migration legacy layer). |
