---
name: doc-chg-fixer
description: Apply fixes to a Change Management (CHG) record from the latest doc-chg-audit report - schema/required fields, change-level correctness, source-to-gate routing, impact/cascade completeness, conditional blocks, links, and registry. Use after an audit reports a FAIL.
metadata:
  tags:
    - sdd-workflow
    - change-management
    - quality-assurance
  custom_fields:
    artifact_type: CHG
    skill_category: quality-assurance
    version: "0.2.0"
    framework_spec_version: "0.3.0"
    last_updated: "2026-05-23"
---

# doc-chg-fixer

## Purpose

Read the latest audit report and apply fixes to a CHG record, bridging
`../doc-chg-audit/SKILL.md` and a gate-ready CHG so the audit↔fix cycle can
converge.

CHG is **NOT a lifecycle layer**: no layer number, no readiness score. The
fixer drives the record to `gate_ready: true` (audit PASS); the actual approval
is a human decision via `../gate-check/SKILL.md`, never auto-granted here.

**Scope**: a CHG can touch any artifact along
`BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code`.
**Upstream**: the CHG record + `CHG-NN.A_audit_report_vNNN.md`.
**Downstream**: the fixed CHG + `CHG-NN.F_fix_report_vNNN.md`.

## When to Use

After `doc-chg-audit` returns `FAIL`, as part of an Audit → Fix → Audit loop.
Do **not** use without an audit report (run the audit first), to author a new
CHG (use `../doc-chg/SKILL.md` / `../doc-chg-autopilot/SKILL.md`), or to grant
gate approval (that is a human decision via `../gate-check/SKILL.md`).

## Input Contract

Consume the latest `CHG-NN.A_audit_report_vNNN.md`. Back up the CHG before
editing (`tmp/backup/CHG-NN_<ts>/`); on error, restore. Schema and routing rules
come from `framework/governance/chg/CHG-TEMPLATE.yaml` and
`framework/governance/chg/README.md`; gate definitions from
`framework/governance/chg/gates/`.

## Fix Phases

Run in order; later phases assume the earlier ones succeeded.

| Phase | Scope | Representative actions |
|-------|-------|------------------------|
| 0 — Schema | required sections/fields (CHG-E001) | insert missing template sections (`change_description`, `impact_assessment`, `implementation`, `verification`) from `CHG-TEMPLATE.yaml`; fill `document_type: chg-document`, `purpose: governance` |
| 1 — Change level | level vs scope (CHG-E001) | correct `change_level` to match scope (typo→C1, section→C2, cross-layer→C3, P0/P1 prod→Emergency); when scope expands, escalate and flag the new conditional blocks |
| 2 — Routing | source→gate (CHG-E002) | set/correct `entry_gate` per the source table (Upstream/External→GATE-01, Midstream→GATE-03, Design→GATE-06, Execution→GATE-08, Feedback→GATE-CODE, Spec→GATE-SPEC); set `change_source` if missing; for `spec` set `semver_impact` and ensure ≥C2 |
| 3 — Impact / cascade | completeness (CHG-E003) | re-trace the chain and add every affected artifact to `impact_assessment.affected_layers`; set `cascade_direction` (downstream / bubble-up / lateral); set `risk_level` |
| 4 — Conditional blocks | level-required blocks (CHG-E004) | scaffold `rollback_plan` for C2/C3; `gate_approval` for C3; `emergency_change` for Emergency (`emergency_id`, `incident_severity`, `fix_deployed`, `post_mortem_due` = deploy + 48h) |
| 5 — Links & registry | references | recompute relative paths; convert absolute → relative; add/update the entry in `CHG-00_index.md`; validate `supersedes` IDs |
| 6 — IDs & metadata | ID form | normalize to dash `CHG-NN` (or `CHG-EMG-YYYYMMDD-HHMM`); drop any hierarchical 4-segment IDs; fix `change_level`/`change_source` enum values |

**Routing re-derivation:** `entry_gate = f(change_source)` per the README table;
never invent a gate not in {GATE-01, GATE-03, GATE-06, GATE-08, GATE-CODE,
GATE-SPEC, None (C1)}. **Post-mortem due date:** Emergency `post_mortem_due =
fix_deployed + 48h`.

## Confidence Classification

Tag every applied fix and surface counts in the report:

| Confidence | Meaning |
|------------|---------|
| `auto-safe` | deterministic, low semantic risk (link/path, ID form, enum normalize, derived `entry_gate`/`post_mortem_due`) |
| `auto-assisted` | template insertion with partial assumptions (scaffolded `rollback_plan`/`emergency_change`, inferred affected layers from a diff) |
| `manual-required` | domain content cannot be inferred (business justification, root-cause layer, approver decision, true cascade scope) |

## Content-Preservation Rules

- Never delete recorded change history; insert template blocks only where a
  section is missing or below minimum structure.
- Never auto-fill approval/signature fields, `date_approved`, or
  `gate_approval.approver` — those are human decisions (defer to
  `../gate-check/SKILL.md`).
- Mark superseded-but-retained artifacts `[DEPRECATED]` rather than removing them
  from `impact_assessment` or `supersedes`.

## Fix Report Format

Write `CHG-NN.F_fix_report_vNNN.md` with: **Summary** (issues in / fixed /
remaining; files created / modified) · **Fixes Applied** (code, issue, fix,
field/section, confidence) · **Manual-Review Queue** · **Gate-Readiness After
Fix** (`gate_ready: true|false` and remaining blocking codes before→after — no
numeric score) · **Cleanup Summary** (delete superseded fix reports) · **Next
Steps** (re-run `../doc-chg-audit/SKILL.md`; when gate-ready, hand to
`../gate-check/SKILL.md` for C3/Emergency). Loop until the audit PASSes or max
iterations reached.

## Related Resources

- Audit (input): `../doc-chg-audit/SKILL.md` · Create: `../doc-chg/SKILL.md`
- Orchestration: `../doc-chg-autopilot/SKILL.md` · Gate: `../gate-check/SKILL.md`
- Authority: `framework/governance/chg/CHG-TEMPLATE.yaml`,
  `framework/governance/chg/README.md`,
  `framework/governance/chg/gates/`
