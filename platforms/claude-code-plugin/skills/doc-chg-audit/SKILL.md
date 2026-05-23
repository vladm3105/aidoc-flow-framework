---
name: doc-chg-audit
description: Audit a Change Management (CHG) record - run declarative schema, impact/cascade, gate-routing, and change-level checks, then produce a pass/fail gate-readiness report (no numeric score) for doc-chg-fixer. Use to validate a CHG before requesting gate approval.
metadata:
  tags:
    - sdd-workflow
    - change-management
    - quality-assurance
  custom_fields:
    artifact_type: CHG
    skill_category: quality-assurance
    version: "0.2.0"
    framework_spec_version: "0.2.0"
    last_updated: "2026-05-23"
---

# doc-chg-audit

## Purpose

Run a **unified CHG audit** — declarative schema checks plus impact, cascade,
gate-routing, and change-level review — in one pass, producing a single
combined report that `../doc-chg-fixer/SKILL.md` consumes. The framework ships
no runtime code, so **this skill is the validator**: Claude performs each check
directly against the CHG record using the spec as the contract.

CHG is **NOT a lifecycle layer**: it has no layer number and no readiness score.
This audit therefore reports **gate-readiness as a pass/fail** plus a fix list —
it does **not** compute a 0–100 readiness score. The quality bar is **gate
approval**, granted by a human via `../gate-check/SKILL.md`, not by a number.

**Scope**: a CHG can touch any artifact along
`BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code`.
**Upstream**: a CHG record. **Downstream**:
`CHG-NN.A_audit_report_vNNN.md` and an optional fix-cycle trigger.

## When to Use

Use after a CHG record exists and before handing it to `../gate-check/SKILL.md`
for C3/Emergency approval, or inside the autopilot's audit↔fix cycle. Do **not**
use to author a CHG (use `../doc-chg/SKILL.md` or `../doc-chg-autopilot/SKILL.md`)
or to run the formal gate itself (that is `../gate-check/SKILL.md`).

**Fresh-audit policy:** always audit from scratch — never reuse prior results;
re-evaluate gate-readiness independently each run.

**Report cleanup:** after writing the new report, delete superseded
`CHG-NN.A_audit_report_v*.md`; keep `CHG-NN.F_fix_report_v*.md`. Record a
cleanup summary in the report.

## Execution Contract

**Input:** CHG path (`docs/governance/chg/CHG-NN_*...`, or
`CHG-EMG-YYYYMMDD-HHMM` for Emergency).

**Sequence:** 1) run schema/required-field checks → 2) run change-level,
source-routing, and impact/cascade checks → 3) record findings → 4)
merge/normalize findings → 5) write `CHG-NN.A_audit_report_vNNN.md` → 6) if
auto-fixable findings exist, hand off to `doc-chg-fixer`.

## Structural Checklist

Authority: `framework/governance/chg/CHG-TEMPLATE.yaml`,
`framework/governance/chg/README.md`, and the gate definitions under
`framework/governance/chg/gates/`.

**Tier 1 — blocking (error):**

| Check | Verifies | Code |
|-------|----------|------|
| Schema / required fields | `metadata`, `change_control`, `change_description`, `impact_assessment`, `implementation`, `verification` present and non-empty per template | CHG-E001 |
| Change level | `change_level` is one of C1/C2/C3/Emergency **and** matches the actual scope (typo→C1, section→C2, cross-layer→C3, P0/P1 prod→Emergency) | CHG-E001 |
| Gate routing | `entry_gate` matches `change_source` (Upstream/External→GATE-01, Midstream→GATE-03, Design→GATE-06, Execution→GATE-08, Feedback→GATE-CODE, Spec→GATE-SPEC) | CHG-E002 |
| Impact / cascade | `impact_assessment.affected_layers` lists **every** affected artifact; `cascade_direction` correct for the source (downstream / bubble-up / lateral); no template anti-pattern | CHG-E003 |
| Conditional blocks | `rollback_plan` present for C2/C3; `gate_approval.gate` set for C3; `emergency_change` complete for Emergency (incl. `post_mortem_due`, `incident_severity`) | CHG-E004 |
| Spec change | if `change_source: spec`: `semver_impact` set; `change_level` ≥ C2 (never C1); `major`⇒C3; provenance (`why`/`trigger`) present — see `gates/GATE-SPEC_FRAMEWORK.md` | CHG-E002 |

**Tier 2 — advisory (warning):** ID form (`CHG-NN` dash, or
`CHG-EMG-YYYYMMDD-HHMM`; no hierarchical 4-segment IDs); internal links and
template/gate references resolve; registry entry exists; `supersedes` lists
valid artifact IDs; verification checks cover each affected layer.

**Combined status:** `PASS` (gate-ready) only if all Tier 1 checks pass and no
blocking issues remain; otherwise `FAIL`. There is **no numeric score** — the
report states `gate_ready: true|false` and the next required approval (C1 self,
C2 peer review, C3/Emergency `../gate-check/SKILL.md`).

## Metadata Checks

| Field | Required | Valid values |
|-------|----------|--------------|
| `document_type` | yes | `chg-document` (not `template`) |
| `purpose` | yes | `governance` |
| `change_level` | yes | `C1`, `C2`, `C3`, `Emergency` |
| `change_source` | yes (≥C2) | `upstream`, `midstream`, `design`, `execution`, `external`, `feedback`, `spec` |

Findings: `VALID-M001` missing `change_source`; `VALID-M002` invalid level/source
value; `VALID-M003` `document_type` not `chg-document`.

## Combined Report Format

Output: `CHG-NN.A_audit_report_vNNN.md`, with sections — **Summary** (CHG ID,
timestamp, overall status, `gate_ready: true|false`, change level, entry gate) ·
**Gate-Readiness** (PASS/FAIL + the required approver per the change level, not a
score) · **Metadata Findings** · **Schema Findings** · **Change-Level &
Routing Findings** · **Impact / Cascade Findings** · **Fix Queue**
(`auto_fixable` / `manual_required` / `blocked`) · **Recommended Next Step**
(fixer, or `../gate-check/SKILL.md` if gate-ready) · **Cleanup Summary**.

## Hand-off to doc-chg-fixer

Normalize every finding to: `source` (`schema`|`routing`|`impact`|`metadata`),
`code`, `severity` (`error`|`warning`|`info`), `file`, `field/section`,
`action_hint`, `confidence` (`auto-safe`|`auto-assisted`|`manual-required`).
`doc-chg-fixer` consumes the latest `CHG-NN.A_audit_report_vNNN.md`.

## Related Resources

- Create: `../doc-chg/SKILL.md` · Fix: `../doc-chg-fixer/SKILL.md` · Generate:
  `../doc-chg-autopilot/SKILL.md` · Gate: `../gate-check/SKILL.md`
- Authority: `framework/governance/chg/CHG-TEMPLATE.yaml`,
  `framework/governance/chg/README.md`,
  `framework/governance/chg/gates/`
