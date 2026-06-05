---
name: doc-chg-autopilot
description: Drive a Change Management record end-to-end with minimal prompts - detect the change, classify the level, draft the CHG, assess cross-layer cascade, and prep the entry gate. Use to author or batch CHGs hands-off.
metadata:
  tags:
    - sdd-workflow
    - change-management
    - automation-workflow
  custom_fields:
    artifact_type: CHG
    skill_category: automation-workflow
    version: "0.5.0"
    framework_spec_version: "0.13.0"
    last_updated: "2026-05-23"
---

# doc-chg-autopilot

## Purpose

Automated **CHG pipeline**. From a change request — a diff, an incident, a
prompt, or an upstream artifact edit — it detects the change, classifies the
level, drafts a complete CHG record, traces the cross-layer cascade, registers
it, and prepares the entry gate for approval — for one change or a batch.

CHG is **NOT a lifecycle layer**: no layer number, no template chain, no
readiness score. The pipeline closes on **gate approval**, not a numeric score.

## Skill Dependencies

| Skill | Role |
|-------|------|
| `../doc-chg/SKILL.md` | CHG structure, classification, and routing rules |
| `../doc-chg-audit/SKILL.md` | gate-readiness check (pass/fail + fix list) |
| `../doc-chg-fixer/SKILL.md` | applies fixes from the audit report |
| `../gate-check/SKILL.md` | runs the formal gate (C3/Emergency) + approval form |

## Input Contract

Accepts: a target `CHG-NN`/path; a diff or list of edited artifacts; an incident
reference; or a free-text change description. Optional: max fix iterations
(default 3), batch list. With no explicit input, treat the request as a change
description and infer the source.

## Smart Document Detection

For each target, check whether the CHG already exists in the change registry
(`CHG-00_index.md`):

- **Missing** → *generate* mode (draft a new CHG record).
- **Exists** → *review & fix* mode (audit, then fix if it fails gate-readiness).

Infer the change **source** (upstream/midstream/design/execution/external/
feedback) and **level** (C1/C2/C3/Emergency) from the changed artifacts and the
trigger.

## Workflow

1. **Input analysis** — classify the input (diff / incident / prompt / upstream
   edit), locate the touched artifacts, and decide generate vs review-and-fix.
2. **Type & scope** — classify the change level and source per
   `../doc-chg/SKILL.md`; select the entry gate (GATE-01/03/06/08/CODE, or
   GATE-SPEC for a `framework/`-spec change — set `semver_impact`, ≥C2);
   reserve the next `CHG-NN` (or `CHG-EMG-YYYYMMDD-HHMM` for Emergency).
3. **Generation** — populate `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/CHG-TEMPLATE.yaml`:
   metadata, change_control, description (what/why/trigger), implementation,
   verification. **Impact assessment** is mandatory — trace the cascade along
   `BRD→PRD→EARS→BDD→ADR→SPEC→TDD→IPLAN→Code` (downstream for upstream/external,
   bubble-up for feedback, lateral for midstream) and list every affected
   artifact. Add `rollback_plan` (C2/C3), `gate_approval` (C3),
   `emergency_change` (Emergency).
4. **Validation** — run `../doc-chg-audit/SKILL.md` from scratch.
5. **Audit ↔ fix cycle** — while the audit FAILs and iterations < max: run
   `../doc-chg-fixer/SKILL.md`, then re-audit. On pass, update
   `CHG-00_index.md`; on exhausting iterations, flag for manual review.
6. **Gate prep** — C1 commits directly; C2 routes to peer review; **C3/Emergency
   hand off to `../gate-check/SKILL.md`** to run the formal/post-hoc gate and
   complete `GATE_APPROVAL_FORM`. For Emergency, schedule the post-mortem
   (`${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/templates/POST_MORTEM-TEMPLATE.md`) within 48h of
   the fix deploy.

## Execution Modes

- **Single** — one CHG (generate or review-and-fix).
- **Batch** — multiple changes, processed in **chunks of 3** to bound context;
  generate upstream-source CHGs before the downstream ones that depend on them.
- **Dry-run** — report the planned classification, source, entry gate, and
  cascade list without writing files.

## Quality Gates

- A CHG is not "done" until the audit passes (0 blocking findings) **and** the
  required approval is obtained: C1 self, C2 peer review, C3/Emergency gate via
  `../gate-check/SKILL.md`. There is **no numeric readiness score**.
- The change registry is updated only after a CHG passes the audit.
- Fresh audit every cycle — no cached results.

## Error Handling

| Situation | Action |
|-----------|--------|
| Source ambiguous | infer from touched layers; record the assumption in the CHG |
| Cascade incomplete (E003) | re-trace the chain before drafting impact assessment |
| Entry gate mismatch (E002) | re-route per the source table; correct `entry_gate` |
| Max iterations reached, still failing | write reports, flag for manual review, continue batch |
| Emergency post-mortem overdue | block sign-off; escalate; keep `post_mortem_completed: false` |

## Related Resources

- Create: `../doc-chg/SKILL.md` · Audit: `../doc-chg-audit/SKILL.md` · Fix:
  `../doc-chg-fixer/SKILL.md` · Gate: `../gate-check/SKILL.md`
- Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/CHG-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/README.md`,
  `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/CHG-00_index.TEMPLATE.md`,
  `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/gates/`,
  `${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md`
