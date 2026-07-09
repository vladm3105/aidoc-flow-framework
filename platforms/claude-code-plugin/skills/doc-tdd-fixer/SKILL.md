---
name: doc-tdd-fixer
description: Apply fixes to a TDD from the latest doc-tdd-audit report - structure, links, element IDs, test-case content, references, and upstream SPEC drift. Use after an audit reports issues.
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - quality-assurance
  custom_fields:
    layer: 7
    artifact_type: TDD
    skill_category: quality-assurance
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SPEC]
    downstream_artifacts: [IPLAN]
    version: "0.23.4"
    framework_spec_version: "0.35.1"
    last_updated: "2026-05-23"
    adapts: [section_toggles, review_mode]
---

# doc-tdd-fixer

## Purpose

Read the latest audit report and apply fixes to a TDD, bridging
`../doc-tdd-audit/SKILL.md` and a passing TDD so the audit↔fix cycle can
converge.

**Layer**: 7 (TDD quality improvement).
**Upstream**: the TDD document + `.aidoc/audit/07_TDD-audit.md`.
**Downstream**: the fixed TDD + `TDD-NN.F_fix_report_vNNN.md`.

## When to Use

After `doc-tdd-audit` returns `FAIL`, as part of an Audit → Fix → Audit loop.
Do **not** use without an audit report (run the audit first) or to create a new
TDD (use `../doc-tdd/SKILL.md` / `../doc-tdd-autopilot/SKILL.md`).

## Input Contract

Consume the `.aidoc/audit/07_TDD-audit.md` report. Back up the TDD before
editing (`tmp/backup/TDD-NN_<ts>/`); on error, restore. Element-ID standards
come from `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`; structure rules from
`${CLAUDE_PLUGIN_ROOT}/framework/layers/07_TDD/TDD-TEMPLATE.yaml` and `README.md`.

## Remediate Mode

Resolve `review_mode` from `.aidoc/profile.yaml`; if unset, fall through
to the framework default `team` per the precedence chain in
`${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`. Same
fallback applies to other adaptation knobs (`section_toggles`).

### team mode (per REVIEW_TEAM.md §Operations §Remediate)

1. **Read the audit report** at `.aidoc/audit/07_TDD-audit.md` AND,
   when present, the per-persona slots under
   `.aidoc/review/07_TDD/<TDD-id>/` (where `<TDD-id>` is the short
   artifact ID, e.g. `TDD-01`).
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
     dispatch the TDD crew's author lens (per
     `REVIEW_CREWS.yaml`: `qa_lead` for TDD) as the
     default responsible reviewer.

   Lens → agent map for TDD:

   | Lens | Agent |
   |------|-------|
   | `qa_lead` | `test-architect` |
   | `tech_lead` | `solutions-architect` |
   | `chaos_engineer` | `chaos-engineer` |
   | `security_engineer` | `security-engineer` |
   | `operator` | `devops-release-engineer` |
   | `auditor` | `traceability-auditor` |

   TDD crew weights: `{qa_lead: 35, tech_lead: 25,
   chaos_engineer: 10, security_engineer: 10, operator: 10, auditor: 10}`.

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
   `.aidoc/review/07_TDD/<TDD-id>/<persona>.fix_<N>.json` (`<N>` =
   sequential fix-iteration counter, starting at 1). Multi-lens
   findings produce one slot file per responsible lens for the same
   `<N>`.
5. **Revert regressions.** If any lens returns new P0/P1 on the patch,
   revert that patch and flag `manual_required` for the original
   finding. **Never silently keep a regressing fix.**
6. **Dispatch the synthesizer once**, after all patches are validated,
   to emit the unified fix report. Persist
   `TDD-NN.F_fix_report_vNNN.md` with both the Fixes Applied table
   AND a Validation Slots index.

### single_pass mode (fallback)

Apply Phase 0–7 directly, single-handed, no lens validation. Unchanged
legacy behaviour — required when the profile says so, when `Task` subagent
dispatch is unavailable, or when no slots are present.

In both modes, P2/P3 advisory findings are applied without lens
validation; only blocking findings (P0/P1) go through the
patch-validation loop in team mode.

## Saga interaction

When invoked by `doc-tdd-autopilot` (or directly), this skill reads
and updates the saga journal at
`.aidoc/review/07_TDD/<TDD-id>/saga.json` per
`${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_SAGA.md`. The fixer
acts as the **remediation stage** of the saga: it transitions
branches to `BRANCH_COMPENSATING` during patch validation, then back
to `BRANCH_COMPLETED` (validated) or `BRANCH_FAILED` (regression
detected).

### On entry

At entry, write the fixer's start epoch:

```sh
Bash: mkdir -p .aidoc/review/07_TDD/<TDD-id>/ && date +%s > .aidoc/review/07_TDD/<TDD-id>/.skill-start.fixer
```

If `.aidoc/review/07_TDD/<TDD-id>/saga.json` exists, read it. Validate
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
Bash: echo $(( $(date +%s) - $(cat .aidoc/review/07_TDD/<TDD-id>/.skill-start.fixer) ))
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
`doc-tdd-autopilot`'s §3.4 resume logic.

### After synthesizer reduce

- Append transition: `{"ts": "<now>", "from": "BRANCH_COMPENSATING",
  "to": "BRANCH_COMPLETED", "scope": "run"}` (run-level: fixer
  pass complete).
- Update saga `status: "BRANCH_COMPLETED"` (autopilot's next phase
  will be `re-review`).
- Update `updated_at`. Write `saga.json`.

### When invoked standalone (no saga.json on entry)

If `.aidoc/review/07_TDD/<TDD-id>/saga.json` does NOT exist (user
runs `/aidoc-flow:doc-tdd-fixer` directly outside the autopilot
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

## Fix Phases

Run in order; later phases assume the earlier ones succeeded.

| Phase | Scope | Representative actions |
|-------|-------|------------------------|
| 0 — Structure | location/filename | move TDD into `docs/07_TDD/`; rename to `TDD-NN_{slug}.yaml`; align slug with the parent SPEC component; fix relative links after the move |
| 1 — Missing files | referenced-but-absent | create index / fixture / reference placeholders from templates |
| 2 — Links | broken/abs paths | recompute relative paths; convert absolute → relative |
| 3 — Element IDs | legacy/invalid IDs | re-derive `TDD.NN.04.xxxx` (Section 4 + content hash); drop legacy 3-segment `TDD.NN.xxxx` and `TC-XXX`/`UT-XXX`/`IT-XXX`/`ST-XXX`/`FT-XXX` (set the `type` attribute instead) |
| 4 — Content | placeholders, malformed cases | fill template dates; add missing inputs/expected output/edge cases; set a `type` attribute; repair the BDD→test mapping; flag `[TODO]`/`[TBD]` for manual completion |
| 5 — References | traceability | add missing `@spec:`/`@bdd:` tags; fix cross-doc paths; update Section 7 traceability and the coverage table |
| 6 — Upstream | metadata + drift | fix `deliverable_type`/`document_type`; when the parent SPEC has changed, apply tiered drift merge (below) |
| 7 — Style | STY01 banned phrases, STY02/03 oversized prose, FM01 frontmatter mismatch | substitute filler; replace flagged superlatives; collapse paragraph (≥ 3 banned phrases in one section) to bullets; reconcile frontmatter ↔ Document Control rows; STY02/03 — split oversized Test Case sections at type/category boundaries, or mark `manual_required`. Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md` |

**Element ID re-derivation:** `ID = TDD.{doc_id}.04.<first 4 hex of
SHA256(case content)>` (extend to 8 on collision). Test type stays a `type`
attribute, never an ID code. Document-level refs (`SPEC-NN`, `ADR-NN`,
`IPLAN-NN`) stay in dash form.

**Tiered upstream drift** (when the parent SPEC changed): <5% change → Tier 1
auto-merge new test-case stubs (patch bump); 5–15% → Tier 2 auto-merge + flag
affected cases for review + changelog (minor bump); >15% → Tier 3 archive
current + regenerate via autopilot (major bump). Never delete tests — mark
`[DEPRECATED]` and retain for traceability. Record results in
`.drift_cache.json`.

## Confidence Classification

Tag every applied fix and surface counts in the report:

| Confidence | Meaning |
|------------|---------|
| `auto-safe` | deterministic, low semantic risk (link/path, ID conversion, date fill) |
| `auto-assisted` | template insertion with partial assumptions (scaffolded test-case fields, coverage rows) |
| `manual-required` | domain content cannot be inferred (unresolved TODO/TBD, test logic, assertions) |

## Content-Preservation Rules

- Never delete existing test logic, assertions, test data, or fixtures; insert
  template blocks only where a case or section is missing required structure.
- Normalize equivalent headings/cases in place rather than duplicating them.
- Deprecated tests are marked, not removed; recalculate coverage after fixes.

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

Write `TDD-NN.F_fix_report_vNNN.md` with: **Summary** (issues in / fixed /
remaining; files created / modified; test cases repaired) · **Fixes Applied**
(code, issue, fix, file, confidence) · **Manual-Review Queue** · **Validation
After Fix** (score/errors/warnings before→after) · **Cleanup Summary** (delete
superseded fix reports) · **Next Steps** (re-run `doc-tdd-audit`). Loop until
score ≥ threshold or max iterations reached.

## Adaptation

Before applying fixes, read the project adaptation profile
(`.aidoc/profile.yaml`). Honor `section_toggles`: do not reintroduce an
**optional** section the project has toggled off. Ignore any unknown or
out-of-surface key.
Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Audit (input): `../doc-tdd-audit/SKILL.md` · Create: `../doc-tdd/SKILL.md`
- Orchestration: `../doc-tdd-autopilot/SKILL.md` · IDs: `../doc-naming/SKILL.md`
- Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/07_TDD/TDD-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
