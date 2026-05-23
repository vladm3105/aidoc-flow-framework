---
name: gate-check
description: Run the correct CHG approval gate for a change - select the gate by affected layers, run its checks against the error catalog, and prepare the gate approval form for human sign-off. Use when changing an existing SDD artifact via the CHG process.
metadata:
  tags:
    - sdd-workflow
    - utility
    - quality-assurance
  custom_fields:
    skill_category: utility
    upstream_artifacts: []
    downstream_artifacts: []
    version: "0.2.0"
    framework_spec_version: "0.1.0"
    last_updated: "2026-05-23"
---

# gate-check

## Purpose

Run the correct **CHG approval gate** for a change to an existing SDD artifact:
determine the affected layers, select the matching gate, run that gate's
checks against the gate error catalog, produce a pass/fail gate report, and
prepare the `GATE_APPROVAL_FORM` for the approver. It is the verification
companion to the `../doc-chg/SKILL.md` family, which authors the CHG record.

**CRITICAL — authority boundary:** this skill **prepares and verifies**; it is
**never the approving authority**. It records check results and fills the
approval form, but a **human grants approval** by signing per the change
level's approval matrix. The skill must not mark a change "approved".

**Layer**: cross-cutting governance utility (CHG overlay, not a lifecycle layer).

## When to Use

Use `gate-check` when:
- Modifying an existing SDD artifact through the CHG process (C2/C3 changes).
- Verifying a change's gate checks before requesting human sign-off.
- Preparing the gate approval form for a change.

Do **not** use it for:
- C1 changes (typo/formatting) — no gate applies; fix and commit.
- Creating fresh artifacts in a clean flow — use the layer skills and
  `../trace-check/SKILL.md`.
- Authoring the CHG record itself — use `../doc-chg/SKILL.md`.

## Behavior

The framework ships no runtime code — **this skill is the gate runner**,
applying the declarative gate definitions against the change.

### 1. Determine affected layers

From the CHG record (or the change under review), list every layer the change
touches. A change may enter at one gate and cascade downstream.

### 2. Select the gate (by affected layers)

| Affected layers | Artifacts | Gate |
|-----------------|-----------|------|
| L1-L2 | BRD, PRD | GATE-01 |
| L3-L5 | EARS, BDD, ADR | GATE-03 |
| L6-L7 | SPEC, TDD | GATE-06 |
| L8 | IPLAN | GATE-08 |
| Code | Source code | GATE-CODE |

A change entering upstream cascades to each downstream gate in sequence
(GATE-01 → GATE-03 → GATE-06 → GATE-08 → GATE-CODE); run every gate its layers
span. Source-to-entry routing (Upstream/External → GATE-01, Midstream →
GATE-03, Design → GATE-06, Execution → GATE-08, Feedback → GATE-CODE) is in
`framework/governance/chg/README.md`.

### 3. Run the gate's checks

For each selected gate, run its **entry criteria**, **blocking error checks
(E)**, and **warning checks (W)** from that gate's definition file, applying the
codes from `framework/governance/chg/gates/GATE_ERROR_CATALOG.md`. Examples:
GATE-03 verifies EARS/BDD/ADR upstream-tag counts and syntax; GATE-06 verifies
SPEC TDD-Ready ≥ 90% and SPEC↔TDD coverage; GATE-CODE requires a root-cause
analysis. Also apply cross-gate ROUTE-E* checks (no skipped gate, correct
entry per source) and VAL-E* schema checks.

### 4. Produce the gate report

Emit a pass/fail report per gate: each E-check (pass/fail) with its code, each
W-check (addressed/not), and a gate result of **PASS / PASS WITH WARNINGS /
FAIL**. Any failing E-check means the gate **fails** — list the codes and the
catalog resolution for each. Do not soften a failing check.

### 5. Prepare the approval form

Populate `framework/governance/chg/templates/GATE_APPROVAL_FORM.md` from the
report: change summary, scope (layers/artifacts), per-gate validation results,
risk and rollback sections, and the required-approver rows for the change
level. Leave **all signature, decision, and final-approval fields blank** for
the human approver — the skill never fills them.

**Exit:** all E-checks pass and the form is ready for the approvers named in
the change level's matrix. The change proceeds only after a human signs.

## Related Resources

- CHG overview & source routing: `framework/governance/chg/README.md`
- Gate definitions: `framework/governance/chg/gates/GATE-01_BUSINESS_PRODUCT.md`
  · `GATE-03_REQUIREMENTS_ARCHITECTURE.md` · `GATE-06_DESIGN_TEST.md` ·
  `GATE-08_IPLAN.md` · `GATE-CODE_IMPLEMENTATION.md`
- Error codes: `framework/governance/chg/gates/GATE_ERROR_CATALOG.md`
- Approval form: `framework/governance/chg/templates/GATE_APPROVAL_FORM.md`
- CHG authoring: `../doc-chg/SKILL.md`
- Traceability after a change: `../trace-check/SKILL.md`
