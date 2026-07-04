---
name: doc-iplan-fixer
description: Apply fixes to an IPLAN from the latest doc-iplan-audit report - structure, links, IDs, file manifest, session handoff, implementation contracts, references, and upstream drift. Use after an audit reports issues.
metadata:
  tags:
    - sdd-workflow
    - layer-8-artifact
    - quality-assurance
  custom_fields:
    layer: 8
    artifact_type: IPLAN
    skill_category: quality-assurance
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SPEC, TDD]
    downstream_artifacts: [CODE]
    version: "0.23.0"
    framework_spec_version: "0.32.7"
    last_updated: "2026-05-23"
    adapts: [section_toggles, review_mode]
---

# doc-iplan-fixer

## Purpose

Read the latest audit report and apply fixes to an IPLAN, bridging
`../doc-iplan-audit/SKILL.md` and a passing IPLAN so the audit↔fix cycle can
converge.

**Layer**: 8 (IPLAN quality improvement).
**Upstream**: the IPLAN document + `IPLAN-NN.A_audit_report_vNNN.md`.
**Downstream**: the fixed IPLAN + `IPLAN-NN.F_fix_report_vNNN.md`.

## When to Use

After `doc-iplan-audit` returns `FAIL`, as part of an Audit → Fix → Audit loop.
Do **not** use without an audit report (run the audit first) or to create a new
IPLAN (use `../doc-iplan/SKILL.md` / `../doc-iplan-autopilot/SKILL.md`).

## Input Contract

Consume the latest `IPLAN-NN.A_audit_report_vNNN.md`. Back up the IPLAN before
editing (`tmp/backup/IPLAN-NN_<ts>/`); on error, restore. ID standards come from
`${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`; structure rules from
`${CLAUDE_PLUGIN_ROOT}/framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml` and `README.md`.

## Remediate Mode

Resolve `review_mode` from `.aidoc/profile.yaml`; if unset, fall through
to the framework default `team` per the precedence chain in
`${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`. Same
fallback applies to other adaptation knobs (`section_toggles`).

### team mode (per REVIEW_TEAM.md §Operations §Remediate)

1. **Read the audit report** at `IPLAN-NN.A_audit_report_vNNN.md` AND,
   when present, the per-persona slots under
   `.aidoc/review/08_IPLAN/<IPLAN-id>/` (where `<IPLAN-id>` is the
   short artifact ID, e.g. `IPLAN-01`).
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
     dispatch the IPLAN crew's author lens (per
     `REVIEW_CREWS.yaml`: `tech_lead` for IPLAN) as the
     default responsible reviewer.

   Lens → agent map for IPLAN:

   | Lens | Agent |
   |------|-------|
   | `tech_lead` | `solutions-architect` |
   | `architect` | `solutions-architect` |
   | `operator` | `devops-release-engineer` |
   | `integration_lead` | `solutions-architect` |
   | `auditor` | `traceability-auditor` |
   | `chaos_engineer` | `chaos-engineer` |

   IPLAN crew weights: `{tech_lead: 30, architect: 25, operator: 15,
   integration_lead: 12, auditor: 10, chaos_engineer: 8}`.

   P2/P3 are advisory — apply deterministically without lens
   validation.
3. **Propose and apply a patch** per blocking finding. Fix Phases 0–7
   below describe the patch shapes; the catalogue is the same in both
   modes. Back up first per the existing Input Contract.
4. **Validate non-regression.** For each responsible lens identified
   in step 2, dispatch one `Task` subagent in patch-validation mode:
   `subagent_type=<mapped agent>`; brief = the patched region + the
   original finding + the patch diff; output = a fresh persona-output
   record (lens_score for the patched region + any new findings).
   Persist each lens's output as
   `.aidoc/review/08_IPLAN/<IPLAN-id>/<persona>.fix_<N>.json` (`<N>` =
   sequential fix-iteration counter, starting at 1). Multi-lens
   findings produce one slot file per responsible lens for the same
   `<N>`.
5. **Revert regressions.** If any lens returns new P0/P1 on the patch,
   revert that patch and flag `manual_required` for the original
   finding. **Never silently keep a regressing fix.**
6. **Dispatch the synthesizer once**, after all patches are validated,
   to emit the unified fix report. Persist
   `IPLAN-NN.F_fix_report_vNNN.md` with both the Fixes Applied table
   AND a Validation Slots index.

### single_pass mode (fallback)

Apply Phase 0–7 directly, single-handed, no lens validation. Unchanged
legacy behaviour — required when the profile says so, when `Task` subagent
dispatch is unavailable, or when no slots are present.

In both modes, P2/P3 advisory findings are applied without lens
validation; only blocking findings (P0/P1) go through the
patch-validation loop in team mode.

## Saga interaction

When invoked by `doc-iplan-autopilot` (or directly), this skill reads
and updates the saga journal at
`.aidoc/review/08_IPLAN/<IPLAN-id>/saga.json` per
`${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_SAGA.md`. The fixer
acts as the **remediation stage** of the saga: it transitions
branches to `BRANCH_COMPENSATING` during patch validation, then back
to `BRANCH_COMPLETED` (validated) or `BRANCH_FAILED` (regression
detected).

### On entry

At entry, write the fixer's start epoch:

```sh
Bash: mkdir -p .aidoc/review/08_IPLAN/<IPLAN-id>/ && date +%s > .aidoc/review/08_IPLAN/<IPLAN-id>/.skill-start.fixer
```

If `.aidoc/review/08_IPLAN/<IPLAN-id>/saga.json` exists, read it. Validate
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
Bash: echo $(( $(date +%s) - $(cat .aidoc/review/08_IPLAN/<IPLAN-id>/.skill-start.fixer) ))
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
`doc-iplan-autopilot`'s §3.4 resume logic.

### After synthesizer reduce

- Append transition: `{"ts": "<now>", "from": "BRANCH_COMPENSATING",
  "to": "BRANCH_COMPLETED", "scope": "run"}` (run-level: fixer
  pass complete).
- Update saga `status: "BRANCH_COMPLETED"` (autopilot's next phase
  will be `re-review`). Increment saga `iteration` counter.
- Update `updated_at`. Write `saga.json`.

### When invoked standalone (no saga.json on entry)

If `.aidoc/review/08_IPLAN/<IPLAN-id>/saga.json` does NOT exist (user
runs `/aidoc-flow:doc-iplan-fixer` directly outside the autopilot
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
`REVIEW_SAGA.md`) with verdict still `FAIL`, the fixer must NOT spawn
another iteration. The saga driver transitions to `PARTIAL_TIMEOUT`;
the fixer reports the unfixed findings, writes the fix report, and
exits cleanly. The next invocation can resume from checkpoint via
`sdd-lifecycle resume`.

## Fix Phases

Run in order; later phases assume the earlier ones succeeded.

| Phase | Scope | Representative actions |
|-------|-------|------------------------|
| 0 — Structure | naming/placement | move permanent IPLAN to `docs/08_IPLAN/IPLAN-NN_{slug}.yaml`; move temporary plans to `tmp/` and remove from index; rename file to match ID; fix relative links after the move |
| 1 — Missing sections | absent template sections | seed `file_manifest`, `session_handoff`, `implementation_contracts`, `code_inventory` from the template; create stub test/impl files at declared manifest paths |
| 2 — Links | broken/abs paths | recompute relative paths to SPEC/TDD; convert absolute → relative; fix malformed manifest paths |
| 3 — IDs | invalid IDs | convert hierarchical `IPLAN.NN.SS.xxxx` → document-level `IPLAN-NN`; re-number 3-digit `IPLAN-NNN` → two-digit; add 4-hex hash to `TDD.NN.SS` → `TDD.NN.SS.xxxx`; convert `SPEC.NN.SS.xxxx` → `SPEC-NN` |
| 4 — Content & manifest | placeholders, ordering | fill template dates; reorder manifest to test-first; add missing `status`/`verified` markers; flag `[TODO]`/`[TBD]` for manual completion |
| 5 — References | traceability | add tags missing from this layer's `required_tags` (per `LAYER_REGISTRY.yaml` necessary-upstream contract — IPLAN requires `@spec @tdd`); add missing `code_inventory` entries |
| 6 — Upstream | drift | when SPEC/TDD changed since creation, apply tiered drift merge (below) |
| 7 — Style | STY01 banned phrases, STY02/03 oversized prose, FM01 frontmatter mismatch | substitute filler; replace flagged superlatives; collapse paragraph (≥ 3 banned phrases in one section) to bullets; reconcile frontmatter ↔ Document Control rows; STY02/03 — split oversized session-handoff narrative at session boundaries, or mark `manual_required`. Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md` |

**ID re-derivation:** IPLAN is document-level — always `IPLAN-NN` (dash form),
never a dotted element ID. Document-level upstreams (`SPEC-NN`, `ADR-NN`) stay
dash; hierarchical upstreams keep the dotted 4-segment form (`TDD.NN.SS.xxxx`).

**Tiered upstream drift** (SPEC/TDD changed): <5% change → Tier 1 auto-merge new
manifest entries (patch bump); 5–15% → Tier 2 auto-merge + detailed changelog
(minor bump); >15% → Tier 3 archive current + regenerate via autopilot (major
bump). Never delete manifest entries — mark `[CANCELLED]` with a reason and
retain for the audit trail. Record results in `.drift_cache.json`.

## Confidence Classification

Tag every applied fix and surface counts in the report:

| Confidence | Meaning |
|------------|---------|
| `auto-safe` | deterministic, low semantic risk (link/path, ID conversion, manifest reorder) |
| `auto-assisted` | template insertion with partial assumptions (scaffolded sections/contracts) |
| `manual-required` | domain content cannot be inferred (unresolved TODO/TBD, contract method bodies, Tier 3 drift) |

## Content-Preservation Rules

- Never delete existing manifest entries, contracts, or session history; insert
  template blocks only where a section is missing or below minimum structure.
- Preserve file descriptions, dependency logic, complexity values, and prior
  session entries; normalize format only.
- Mark removed-upstream manifest entries `[CANCELLED]` (keep all original
  fields) rather than deleting them.

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

Write `IPLAN-NN.F_fix_report_vNNN.md` with: **Summary** (issues in / fixed /
remaining; sections created; files modified) · **Fixes Applied** (code, issue,
fix, file, confidence) · **Manual-Review Queue** · **Validation After Fix**
(score/errors/warnings before→after) · **Validation Slots index** — in team
mode, list the per-lens patch-validation outputs persisted at
`.aidoc/review/08_IPLAN/<IPLAN-id>/<persona>.fix_<N>.json` for each
blocking finding, one row per `(finding_id, persona, N)` triple ·
**Cleanup Summary** (delete superseded fix reports) · **Next Steps**
(re-run `doc-iplan-audit`). Loop until score ≥ threshold or max
iterations reached (`MAX_ITERATIONS=3` per `REVIEW_SAGA.md`
break-circuit policy).

## Adaptation

Before applying fixes, read the project adaptation profile
(`.aidoc/profile.yaml`). Honor `section_toggles`: do not reintroduce an
**optional** section the project has toggled off. Ignore any unknown or
out-of-surface key.
Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Audit (input): `../doc-iplan-audit/SKILL.md` · Create: `../doc-iplan/SKILL.md`
- Orchestration: `../doc-iplan-autopilot/SKILL.md` · IDs: `../doc-naming/SKILL.md`
- Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
