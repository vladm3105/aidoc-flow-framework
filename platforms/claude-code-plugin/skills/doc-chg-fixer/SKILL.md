---
name: doc-chg-fixer
description: Apply fixes to a Change Management (CHG) record from the latest doc-chg-audit report - schema/required fields, change-level correctness, source-to-gate routing, impact/cascade completeness, conditional blocks, links, registry, and lens-validated content remediations. Use after an audit reports a FAIL.
metadata:
  tags:
    - sdd-workflow
    - change-management
    - quality-assurance
  custom_fields:
    artifact_type: CHG
    skill_category: quality-assurance
    version: "0.25.0"
    framework_spec_version: "0.40.0"
    last_updated: "2026-06-12"
    adapts: [section_toggles, review_mode]
---

# doc-chg-fixer

## Purpose

Read the latest audit report and apply fixes to a CHG record, bridging
`../doc-chg-audit/SKILL.md` and a gate-ready CHG so the audit↔fix cycle can
converge.

CHG is **NOT a lifecycle layer** in the BRD..IPLAN sense: no readiness score.
The fixer drives the record to `gate_ready: true` (audit PASS); the actual
approval is a human decision via `../gate-check/SKILL.md`, never auto-granted
here. For team-mode dispatch purposes the CHG layer is addressed as
**`09_CHG`** (the layer-id slot occupied by the change-management overlay).

**Scope**: a CHG can touch any artifact along
`BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code`.
**Upstream**: the CHG record + `.aidoc/audit/09_CHG-audit.md`.
**Downstream**: the fixed CHG + `CHG-NN.F_fix_report_vNNN.md`.

## When to Use

After `doc-chg-audit` returns `FAIL`, as part of an Audit → Fix → Audit loop.
Do **not** use without an audit report (run the audit first), to author a new
CHG (use `../doc-chg/SKILL.md` / `../doc-chg-autopilot/SKILL.md`), or to grant
gate approval (that is a human decision via `../gate-check/SKILL.md`).

## Input Contract

Consume the `.aidoc/audit/09_CHG-audit.md` report. Back up the CHG before
editing (`tmp/backup/CHG-NN_<ts>/`); on error, restore. Schema and routing rules
come from `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/CHG-TEMPLATE.yaml` and
`${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/README.md`; gate definitions from
`${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/gates/`.

## Remediate Mode

Resolve `review_mode` from `.aidoc/profile.yaml`; if unset, fall through
to the framework default `team` per the precedence chain in
`${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`. Same
fallback applies to other adaptation knobs (`section_toggles`).

### team mode (per REVIEW_TEAM.md §Operations §Remediate)

1. **Read the audit report** at `.aidoc/audit/09_CHG-audit.md` AND,
   when present, the per-persona slots under
   `.aidoc/review/09_CHG/<CHG-id>/` (where `<CHG-id>` is the short
   artifact ID, e.g. `CHG-01` or `CHG-EMG-20260612-1430`).
   - **Prefer the per-persona slots** for the structured findings —
     stable ids, priorities, locations, recommendations.
   - **Slots are optional** — when absent (e.g. single_pass run
     produced no synthesizer output), fall back to parsing the audit
     report's Findings sections directly.
2. **Resolve responsible lenses per finding.** Each blocking finding
   (P0 + P1) carries a `personas` array in the synthesizer's reduced
   form OR can be inferred from per-lens slot membership. Dispatch
   rules:
   - **Single-lens finding** (1 persona): dispatch that lens.
   - **Multi-lens finding** (2+ personas): dispatch **all** listed
     lenses in parallel. Each writes its own `<persona>.fix_<N>.json`
     slot. The fix is accepted only when **every** dispatched lens
     returns no new P0/P1 (any one lens regressing reverts the patch).
   - **No-persona / orphan finding** (empty or missing `personas`):
     dispatch the CHG crew's author lens (per
     `REVIEW_CREWS.yaml`: `integration_lead` for CHG) as the
     default responsible reviewer.

   Lens → agent map for CHG:

   | Lens | Agent |
   |------|-------|
   | `integration_lead` | `solutions-architect` |
   | `architect` | `solutions-architect` |
   | `chaos_engineer` | `chaos-engineer` |
   | `operator` | `devops-release-engineer` |
   | `auditor` | `traceability-auditor` |
   | `security_engineer` | `security-engineer` |

   CHG crew weights: `{integration_lead: 30, architect: 20,
   chaos_engineer: 15, operator: 15, auditor: 10,
   security_engineer: 10}`. Because `solutions-architect` carries two
   lens-roles at CHG (`integration_lead` + `architect`), each lens is
   dispatched as a **separate `Task` subagent** with its own lens
   brief; the validation slots for the two roles are kept separate
   (one file per lens-role, never merged).

   P2/P3 are advisory — apply deterministically without lens
   validation.
3. **Propose and apply a patch** per blocking finding. Fix Phases 0–7
   below describe the patch shapes; the catalogue is the same in both
   modes. Back up first per the existing Input Contract.
4. **Validate non-regression.** For each responsible lens identified
   in step 2, dispatch one `Task` subagent in patch-validation mode:
   `subagent_type=<mapped agent>`; brief = the patched region + the
   original finding + the patch diff; **the lens MUST NOT read, cite, or
   weight any author self-assessment score** (`*_ready_score`/`*_score`/
   `readiness_score`/`audit_score`) when forming its `lens_score`
   (`REVIEW_TEAM.md` GD-05); output = a fresh persona-output
   record (lens_score for the patched region + any new findings).
   Persist each lens's output as
   `.aidoc/review/09_CHG/<CHG-id>/<persona>.fix_<N>.json` (`<N>` =
   sequential fix-iteration counter, starting at 1). Multi-lens
   findings produce one slot file per responsible lens for the same
   `<N>`.
5. **Revert regressions.** If any lens returns new P0/P1 on the patch,
   revert that patch and flag `manual_required` for the original
   finding. **Never silently keep a regressing fix.**
6. **Dispatch the synthesizer once**, after all patches are validated,
   to emit the unified fix report. Persist
   `CHG-NN.F_fix_report_vNNN.md` with both the Fixes Applied table
   AND a Validation Slots index.

### single_pass mode (fallback)

Apply Phase 0–7 directly, single-handed, no lens validation. Unchanged
legacy behaviour — required when the profile says so, when `Task` subagent
dispatch is unavailable, or when no slots are present.

In both modes, P2/P3 advisory findings are applied without lens
validation; only blocking findings (P0/P1) go through the
patch-validation loop in team mode.

## Saga interaction

When invoked by `doc-chg-autopilot` (or directly), this skill reads
and updates the saga journal at
`.aidoc/review/09_CHG/<CHG-id>/saga.json` per
`${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_SAGA.md`. The fixer
acts as the **remediation stage** of the saga: it transitions
branches to `BRANCH_COMPENSATING` during patch validation, then back
to `BRANCH_COMPLETED` (validated) or `BRANCH_FAILED` (regression
detected).

### On entry

At entry, write the fixer's start epoch:

```sh
Bash: mkdir -p .aidoc/review/09_CHG/<CHG-id>/ && date +%s > .aidoc/review/09_CHG/<CHG-id>/.skill-start.fixer
```

If `.aidoc/review/09_CHG/<CHG-id>/saga.json` exists, read it. Validate
that current saga `status` is `FANIN_REDUCED` (post-audit) or
`BRANCH_FAILED` (re-entering after a prior fixer regression). If
status is something else, log a warning and proceed.

### During patch validation (team mode)

For each blocking finding (P0/P1) that requires lens validation:

1. Before dispatching the responsible lens validator(s): for each
   lens in the finding's `personas[]` list, append a transition:
   `{"ts": "<now>", "from": "BRANCH_COMPLETED", "to":
   "BRANCH_COMPENSATING", "scope": "branch:<lens>"}`. Update
   `branches[<lens>].status` to `"BRANCH_COMPENSATING"`. Append an
   entry to `compensation_actions[]`:
   `{"ts": "<now>", "branch": "<lens>", "reason": "<finding_id>:
   <message>", "action": "retry"}`.
2. After the validation Task subagent returns:
   - If patch validated (no regression): transition back to
     `BRANCH_COMPLETED`. Update `compensation_actions[]` last entry
     with the validation result.
   - If patch regresses (lens flags new P0/P1 on patched region):
     transition to `BRANCH_FAILED`. Set
     `compensation_actions[]` last entry's `action` to `"escalate"`.
     The finding becomes `manual_required`.

### Before synthesizer dispatch

Per `REVIEW_SAGA.md` §"Break-circuit policy" — the fixer's
checkpoint boundary is **between multi-lens validation dispatches**
(each blocking finding's per-lens validation is one boundary).
Before dispatching the next validation:

```sh
Bash: echo $(( $(date +%s) - $(cat .aidoc/review/09_CHG/<CHG-id>/.skill-start.fixer) ))
```

If elapsed > `SOFT_DEADLINE` (1500s):

- Append transition: `{"ts": "<now>", "from": "BRANCH_COMPENSATING",
  "to": "PARTIAL_TIMEOUT", "scope": "run"}`.
- Set saga `status: "PARTIAL_TIMEOUT"`. Preserve all completed
  validations (their `fix_N.json` slots remain durable). Set
  `current_phase: "fixer"` so the resume invocation knows to
  continue the remaining validations.
- Update `updated_at`. Write `saga.json`. Exit cleanly.

The remaining validations resume on next invocation per
`doc-chg-autopilot`'s §3.4 resume logic.

### After synthesizer reduce

- Append transition: `{"ts": "<now>", "from": "BRANCH_COMPENSATING",
  "to": "BRANCH_COMPLETED", "scope": "run"}` (run-level: fixer
  pass complete).
- Update saga `status: "BRANCH_COMPLETED"` (autopilot's next phase
  will be `re-review`). Increment saga `iteration` counter.
- Update `updated_at`. Write `saga.json`.

### When invoked standalone (no saga.json on entry)

If `.aidoc/review/09_CHG/<CHG-id>/saga.json` does NOT exist (user
runs `/aidoc-flow:doc-chg-fixer` directly outside the autopilot
loop), do NOT initialize the full saga schema. Log `saga.json not
present; running fixer without saga journal (standalone mode)`. Run
the fix phases as usual; write the fix report; skip all saga.json
transitions. Backward-compatible with direct skill invocation.

### When invoked in single_pass mode

If `review_mode: single_pass` is active, the fixer applies patches
deterministically without lens validation and without writing
saga.json. Existing behavior preserved.

## Break-circuit policy

Per `${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_SAGA.md`
§"Break-circuit policy", this skill checks elapsed wall-clock at one
checkpoint boundary: **after all per-finding patches return and before
invoking the synthesizer**. The SOFT_DEADLINE is 1500s
(`ORCHESTRATOR_TIMEOUT=1800s` minus 300s buffer).

If the soft deadline has been crossed, exit cleanly with saga
`status: "PARTIAL_TIMEOUT"` per §"Before synthesizer dispatch" above.
The fixer's partial progress (`fix_N.json` slots already written) is
durable; resumed invocation continues from where the break-circuit
fired.

When the saga is already at `MAX_ITERATIONS=3` (per
`REVIEW_SAGA.md`) with verdict still `gate_ready: false`, the fixer
must NOT spawn another iteration. The saga driver transitions to
`PARTIAL_TIMEOUT`; the fixer reports the unfixed findings, writes the
fix report, and exits cleanly. The next invocation can resume from
checkpoint via `sdd-lifecycle resume`. Change-level (C1/C2/C3/
Emergency) and gate-routing classifications do NOT relax this cap;
Emergency CHGs likewise stop at MAX_ITERATIONS and wait for a human
review per `framework/governance/chg/README.md`.

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
| 7 — Style | STY01 banned phrases, STY02/03 oversized prose, FM01 frontmatter mismatch | substitute filler; replace flagged superlatives; collapse paragraph (≥ 3 banned phrases in one section) to bullets; reconcile frontmatter ↔ Document Control rows; STY02/03 — split oversized impact_assessment / rollback_plan blocks at the next list item, or mark `manual_required`. Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md` |

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

### Table-pipe escape (MD056)

When emitting markdown table cells that contain code spans with shell
pipes (e.g. `` `docker compose ps | grep 'Up'` ``), the unescaped `|`
inside the code span is parsed by markdownlint as a column separator,
tripping **MD056** (column-count mismatch). Two fixes:

- **Preferred:** escape the pipe inside the code span as `\|` —
  renders as `|` in markdown viewers but doesn't break the table.
  Example row: `` | OP-02 | ... | `docker compose ps \| grep 'Up'` | ... | ``
- **Alternative:** move the code span out of the table cell and
  reference it as a footnote or paragraph below the table. The cell
  then carries plain prose like "shell readiness gate (see below)".

Apply to every report row that emits a shell-pipe code span inside a
table cell. Cascade-output that trips MD056 is a SKILL bug, not a
markdownlint over-strictness — fix here, not by lint-ignoring.

Write `CHG-NN.F_fix_report_vNNN.md` with: **Summary** (issues in / fixed /
remaining; files created / modified) · **Fixes Applied** (code, issue, fix,
field/section, confidence) · **Manual-Review Queue** · **Gate-Readiness After
Fix** (`gate_ready: true|false` and remaining blocking codes before→after — no
numeric score) · **Validation Slots index** — in team mode, list the per-lens
patch-validation outputs persisted at
`.aidoc/review/09_CHG/<CHG-id>/<persona>.fix_<N>.json` for each blocking
finding, one row per `(finding_id, persona, N)` triple · **Cleanup Summary**
(delete superseded fix reports) · **Next Steps** (re-run
`../doc-chg-audit/SKILL.md`; when gate-ready, hand to `../gate-check/SKILL.md`
for C3/Emergency). Loop until the audit PASSes or max iterations reached
(`MAX_ITERATIONS=3` per `REVIEW_SAGA.md` break-circuit policy).

## Adaptation

Before applying fixes, read the project adaptation profile
(`.aidoc/profile.yaml`). Honor `section_toggles`: do not reintroduce an
**optional** section the project has toggled off. CHG's conditional blocks
follow the change-level matrix, not `section_toggles` — never toggle off a
block required by the artifact's `change_level` (`rollback_plan` for C2/C3,
`gate_approval` for C3, `emergency_change` for Emergency). Ignore any unknown
or out-of-surface key.
Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Audit (input): `../doc-chg-audit/SKILL.md` · Create: `../doc-chg/SKILL.md`
- Orchestration: `../doc-chg-autopilot/SKILL.md` · Gate: `../gate-check/SKILL.md`
- Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/CHG-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/README.md`,
  `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/gates/`,
  `${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md`
