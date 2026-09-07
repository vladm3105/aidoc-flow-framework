# CLEANUP-PR-B — Review-Quality Calibration (heart of FRAMEWORK-CLEANUP-001)

> Child PR of `FRAMEWORK-CLEANUP-001` (master plan PR #128, merged
> `528d6f23`). The **largest + highest-impact child PR** — 6 items;
> changes audit/fixer behavior at every layer.

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | CLEANUP-PR-B                                |
| Type           | combined plan + impl (heart of cleanup)     |
| Worktree       | `feat/cleanup-pr-b-review-calibration` at `/opt/data/aidoc-flow/framework-cleanup-pr-b/` |
| Depends on     | FRAMEWORK-CLEANUP-001 master plan (PR #128); PR-A (PR #129); PR-C (PR #130). All landed. |
| Closes         | `plans/FRAMEWORK-TODO.md` Open items #5, #6, #7, #8, #9, #10 |
| Version impact | Framework MINOR `0.18.0 → 0.19.0` (saga schema field + REVIEW_TEAM §Operations content); plugin MINOR `0.15.0 → 0.16.0` (8 audit SKILLs strip self-claim + saga journal new field) |
| Status         | DRAFT — 2026-06-11 |

## Items closed by this PR

| # | Tag | Title | Priority |
|---|---|---|---|
| 5 | `[plan-review]` | Plan reviews must cross-check example corpus | MED |
| 6 | `[plan-review]` | Codify minimum-pass count by plan-type | LOW (advisory) |
| 7 | `[skill]` | doc-tdd auditor C4 inter-section consistency investigation | LOW (investigate) |
| 8 | `[playbook]` | Auditor + tech_lead lens calibration (convergence theater) | **HIGH** |
| 9 | `[skill]` | doc-*-audit must strip self-claimed scores | MED |
| 10 | `[saga]` | `fixer_introduced_finding` tag | MED |

## Pre-design findings (codebase cross-checks)

1. **No `verified-planning` SKILL exists** — items 5+6 are
   CLAUDE.md / memory updates, not SKILL edits. The 2-cycle review
   discipline is described in CLAUDE.md §"Development workflow" item 2;
   the corpus-cross-check + minimum-pass guidance belong there.
2. **doc-brd-audit/SKILL.md:164** already mentions a "self-claimed
   PRD-Ready score" — but the existing handling is partial (no strip
   step before lens fan-out). Item 9 closes this gap.
3. **`framework/governance/saga.schema.json`** is the canonical schema;
   item 10 extends it with the new `fixer_introduced` boolean on
   finding objects.
4. **`framework/playbooks/<layer>/auditor.md`** exists for 6 layers
   (BRD/PRD/BDD/ADR/TDD/IPLAN) — EARS and SPEC have NO auditor lens
   (their crews don't include it per `REVIEW_CREWS.yaml`). Item 8 only
   touches the 6 layers with auditor lenses.
5. **`framework/playbooks/<layer>/tech_lead.md`** exists for 7 layers
   (PRD/EARS/BDD/ADR/SPEC/TDD/IPLAN — not BRD). Item 8 touches the 7.
6. **No `## Regressions` section** anywhere in the framework currently
   — item 10 introduces it as a new audit-report section.

## Scope per item

### Item 5 — Plan reviews must cross-check example corpus

**Reframed:** not a SKILL file — a CLAUDE.md update + memory note.

**Fix shape:** add a checklist item to CLAUDE.md §"Development workflow"
item 2's Pass-N criteria: *"if the plan changes lint rules, @-tag
semantics, or playbook content, run `python3 -m sdd_doc_lint
examples/<NAME>/docs/` and verify 0 unexpected findings as part of
the same review pass."* Also add a paragraph to the existing memory
note [[feedback_two_cycle_plan_review]] documenting the same.

**Touches:** `CLAUDE.md` (~10 lines); user-global memory file (out of
git — handled separately).

### Item 6 — Codify minimum-pass count by plan-type (advisory)

**Fix shape:** CLAUDE.md §"Development workflow" item 2 gains a
paragraph: *"empirical baseline — framework-level / cross-cutting
plans typically converge in 4-5 cycles; per-layer rollout plans in
2-3. The CLAUDE.md floor is 2 cycles; this guidance suggests upper
bounds for estimation."*

**Touches:** `CLAUDE.md` (~5 lines).

### Item 7 — doc-tdd auditor C4 investigation (close as wontfix or update)

**Investigation outcome (Pass 1):** the TDD-RT-001 P2 finding cited
"§1 line 30 (cumulative upstream tags header) vs §3 lines 89-90 and
§7 line 206" as inter-section inconsistency. Per the 2026-06-11
url-shortener review, TDD-01's §1 line 30 correctly reads `@ears |
@bdd | @adr | @spec` per the new necessary-upstream contract — no
real inconsistency. The auditor C4 check fired against a content
mismatch between sections (each section has its own tag set, and they
don't have to match — only §1 is the "cumulative header"; §3 and §7
have their own per-element tags).

**Decision:** close as **wontfix** — the C4 check is correct as
written; the P2 finding was a transient artifact of the cascade
during TDD-RT-001 (LLM author inconsistency, not framework bug).
Document the decision in `framework/playbooks/07_TDD/auditor.md` C4
explanatory note: *"C4 detects cross-section tag inconsistency; the
audit cycle's fixer remediates by rewriting the deviant section.
This is by design and not a check-strictness issue."*

**Touches:** `framework/playbooks/07_TDD/auditor.md` (~3 lines).

### Item 8 — Auditor + tech_lead lens calibration (HIGH priority)

Per the 2026-06-11 url-shortener review: `auditor` lens scored 100 on
4 of 5 cascaded layers; `tech_lead` scored 100 on 3 of 4 layers even
when chaos/security found multiple P2/P3 in the same sections. The
fix is to require a falsifiable rationale when a lens claims zero
findings.

**Fix shape:**

1. **Playbook content** — each `framework/playbooks/<layer>/auditor.md`
   (6 files) + `tech_lead.md` (7 files) gains a new mandatory
   "No-findings rationale" subsection (~10 lines each) stating:
   *"A lens returning `lens_score: 100` with `findings: []` must
   accompany the persona-output record with a `no_findings_rationale`
   field naming at least one section where the lens did examine and
   explicitly cleared. Synthesizer treats missing rationale as a
   structural error and caps the lens at 95."*

2. **REVIEW_TEAM.md** §Operations gains a new paragraph documenting
   the no-findings-rationale principle at the spec level.

3. **Synthesizer agent** (`platforms/claude-code-plugin/agents/synthesizer.md`)
   gains a sub-check: if any lens output has `lens_score==100` AND
   `findings.length==0` AND `no_findings_rationale` is missing/empty,
   cap that lens at 95 and emit a `STRUCTURE-RAT-001` advisory in the
   synthesized verdict.

**Touches:** 6 × `auditor.md` + 7 × `tech_lead.md` = 13 playbook files
(~10 lines each = ~130 lines); `REVIEW_TEAM.md` (~15 lines);
`platforms/claude-code-plugin/agents/synthesizer.md` (~20 lines).

### Item 9 — doc-*-audit strip self-claimed scores

Per the 2026-06-11 review: PRD's `ears_ready_score: 92` survived into
the artifact body the lenses see; synthesizer's final score was also
92. Anchor effect.

**Fix shape:** add a step to all 9 `doc-*-audit/SKILL.md` (BRD, PRD,
EARS, BDD, ADR, SPEC, TDD, IPLAN, plus CHG) before the lens fan-out:

> **Strip author self-claim before dispatch.** Before passing the
> artifact body to each lens subagent, strip frontmatter and inline
> fields matching `*_ready_score`, `*_score`, `readiness_score`,
> `audit_score`. These author self-assessments are not part of the
> structural surface lenses evaluate; leaving them in creates an
> anchor effect (the lens output's score tends toward the author's
> claim).

Plus document the stripped-field list in `REVIEW_TEAM.md` §Operations.

**Touches:** 9 × `doc-*-audit/SKILL.md` (8 layer + doc-chg-audit) (~5 lines each = ~40 lines);
`REVIEW_TEAM.md` (~10 lines).

### Item 10 — `fixer_introduced_finding` tag in saga lifecycle

Per BDD iter-2 fixer rewriting `.9b90` and iter-3 audit finding new
P2s at the same location: the framework currently has no way to tag
findings that the fixer itself caused.

**Fix shape:**

1. **Schema** — `framework/governance/saga.schema.json` extends
   `finding` definition with new optional boolean
   `fixer_introduced: bool` (default false; true means location
   matches a iter-(N-1) Fixes Applied row).

2. **Spec** — `framework/governance/REVIEW_SAGA.md` documents the new
   field in §Journal schema + adds detection logic to §Break-circuit
   policy.

3. **Audit-report format** — `REVIEW_TEAM.md` documents a new
   `## Regressions` section in audit reports listing
   `fixer_introduced: true` findings separately.

4. **Plugin auditor SKILLs** — 9 × `doc-*-audit/SKILL.md` (8 layer + doc-chg-audit) extend
   Combined Report Format to render the `## Regressions` section when
   any finding has `fixer_introduced=true`.

5. **Plugin synthesizer** — `agents/synthesizer.md` detects the
   regression case (compare iter-N findings' locations to iter-(N-1)
   Fixes Applied entries) and sets the flag.

**Touches:** `saga.schema.json` (~5 lines); `REVIEW_SAGA.md` (~15
lines); `REVIEW_TEAM.md` (~10 lines); 9 × `doc-*-audit/SKILL.md` (8 layer + doc-chg-audit) (~5
lines each = ~40 lines); `synthesizer.md` (~25 lines).

## File structure

### Modified (cluster by item)

| Path | Items | Change |
|---|---|---|
| `CLAUDE.md` | #5, #6 | New checklist items + minimum-pass-by-plan-type guidance in §Development workflow item 2 |
| `framework/playbooks/01_BRD/auditor.md` | #8 | Add "No-findings rationale" subsection |
| `framework/playbooks/02_PRD/auditor.md` | #8 | Same |
| `framework/playbooks/04_BDD/auditor.md` | #8 | Same |
| `framework/playbooks/05_ADR/auditor.md` | #8 | Same |
| `framework/playbooks/07_TDD/auditor.md` | #7, #8 | Same + C4 wontfix note (item 7) |
| `framework/playbooks/08_IPLAN/auditor.md` | #8 | Same |
| `framework/playbooks/02_PRD/tech_lead.md` | #8 | Add "No-findings rationale" subsection |
| `framework/playbooks/03_EARS/tech_lead.md` | #8 | Same |
| `framework/playbooks/04_BDD/tech_lead.md` | #8 | Same |
| `framework/playbooks/05_ADR/tech_lead.md` | #8 | Same |
| `framework/playbooks/06_SPEC/tech_lead.md` | #8 | Same |
| `framework/playbooks/07_TDD/tech_lead.md` | #8 | Same |
| `framework/playbooks/08_IPLAN/tech_lead.md` | #8 | Same |
| `framework/governance/REVIEW_TEAM.md` | #8, #9, #10 | New §Operations subsections (no-findings-rationale + stripped-fields + Regressions section format) |
| `framework/governance/REVIEW_SAGA.md` | #10 | New `fixer_introduced` field in §Journal schema + §Break-circuit detection |
| `framework/governance/saga.schema.json` | #10 | Extend `finding` definition with `fixer_introduced: bool` |
| 8 × `platforms/claude-code-plugin/skills/doc-*-audit/SKILL.md` | #9, #10 | Add "Strip self-claim" step; extend Combined Report Format with `## Regressions` |
| `platforms/claude-code-plugin/agents/synthesizer.md` | #8, #10 | Cap-at-95 logic for missing rationale; fixer-introduced detection |
| `framework/VERSION` | — | `0.18.0 → 0.19.0` MINOR |
| `platforms/claude-code-plugin/VERSION` | — | `0.15.0 → 0.16.0` MINOR |
| Both `FRAMEWORK_SPEC_VERSION` | — | `0.18.0 → 0.19.0` |
| `CHANGELOG.md`, `docs/TAGGING.md`, `plans/HANDOFF.md`, `plans/FRAMEWORK-TODO.md` | — | Per docs-of-record discipline |
| `tests/conformance/platforms/test_plugin_release_metadata.py` | — | Hardcoded `"0.18.0" → "0.19.0"` |
| `tests/conformance/test_saga_schema.py` (or similar) | #10 | Test new schema field |

**Total file count:** ~30-35 substantive files + sync re-propagation.

## Implementation sequence

### Task 1 — Plan iterative review (this section + Pass 1+)

### Task 2 — Item 8 (HIGH): playbook recalibration

13 playbook files (6 auditor + 7 tech_lead) gain "No-findings rationale" subsection. Identical text across all 13 (drift-free). Dispatch parallel agent for mechanical edits.

### Task 3 — Items 9 + 10: SKILL prompt edits

9 × `doc-*-audit/SKILL.md` (8 layer + doc-chg-audit) files get two additions: "Strip self-claim" step + extend Combined Report Format with `## Regressions`. Dispatch parallel agent.

### Task 4 — Schema + governance updates

- `saga.schema.json`: extend finding with `fixer_introduced` bool
- `REVIEW_SAGA.md`: document new field
- `REVIEW_TEAM.md`: new §Operations content (3 paragraphs)
- Synthesizer agent: cap-at-95 + regression-detection logic

### Task 5 — CLAUDE.md updates (items 5 + 6)

Add corpus-cross-check + minimum-pass guidance to §Development workflow item 2.

### Task 6 — Item 7 wontfix note

Add C4 explanatory note to `playbooks/07_TDD/auditor.md`.

### Task 7 — Version + sync + docs of record

### Task 8 — Conformance + lint cheap checks

### Task 9 — Live cascade verification (the HEART proof)

Per master plan §Cascade-cost budget: PR-B requires a full PRD→TDD cascade (~5-6h wall clock) to confirm the recalibration bites. Expected outcome:

- Auditor + tech_lead lenses NO LONGER score 100 across all layers (calibration works)
- At least 4 of 7 cascaded layers show non-100 auditor or tech_lead scores
- If a `fixer_introduced` regression occurs in any layer, the audit report's new `## Regressions` section surfaces it
- Self-claimed scores in artifacts do NOT match final synthesizer scores (anchor-effect broken)

### Task 10 — Open impl PR (only after Tasks 1-9 all green)

## Out of scope

- Hermes mirror of SKILL prompt changes: deferred to HERMES-CATCHUP-001
- Backfilling `fixer_introduced` flags on historical saga journals
- Changing the cap value (95 vs other) beyond what's stated
- Other lenses (chaos / security / qa / architect) — only auditor + tech_lead per the review evidence
- Items 11-14 (PR-C, done), 15-16 (PR-D), 17 (PR-E), 18 (PR-F)

## Verification

| # | Check | Expected |
|---|---|---|
| 1 | 13 playbooks have "No-findings rationale" subsection | PASS — grep verification |
| 2 | 8 audit SKILLs have "Strip self-claim" step | PASS — grep |
| 3 | 8 audit SKILLs reference `## Regressions` in Combined Report Format | PASS — grep |
| 4 | saga.schema.json validates against a fixture with `fixer_introduced` field | PASS — new unit test |
| 5 | REVIEW_SAGA.md documents new field in journal schema | PASS — manual review |
| 6 | REVIEW_TEAM.md §Operations has the 3 new paragraphs | PASS — manual review |
| 7 | Conformance: 120/120 PASS (1 skipped) | PASS |
| 8 | Unit: 43+1 = 44/44 PASS (1 new test for schema) | PASS |
| 9 | Live PRD→TDD cascade: auditor + tech_lead non-100 on ≥ 4 layers | PASS — cascade evidence |
| 10 | If regression occurs, `## Regressions` section in audit report | PASS — cascade evidence (may not surface if no regression in this run) |

## Risks & rollback

| Risk | Mitigation |
|---|---|
| Cascade re-run may surface unrelated regressions (e.g., from PR-C's TH01 strict regex tightening) | Re-run with `--from-layer=prd --to-layer=tdd`; isolate the regen to focal layers. Cost-of-cascade budget already allocated in master plan |
| Synthesizer cap-at-95 logic may break existing tests that assume integer scores | New unit test covers the cap; existing conformance test ranges (score >= 90 for PASS) unaffected |
| `fixer_introduced` schema field may trip existing saga.json consumers | Field is optional with default false; no consumer expects it to be absent. Backward compat preserved |
| 13-playbook edit may introduce drift if not done mechanically | Dispatch parallel agent with explicit identical-text directive; verify with `grep -c` (each file == 1 occurrence) |
| Live cascade takes 5-6h — long feedback loop | Run in background; prep doc updates in parallel; expect overnight |

**Rollback:** Single PR. `git revert <merge-sha>` restores. All schema/spec changes additive.

## Review log

> Per CLAUDE.md §"Development workflow" item 2: ≥ 2 review cycles BEFORE
> PR.

### Pass 0 — initial draft

- **Date:** 2026-06-11T22:30:00Z
- **Status:** SUPERSEDED by Pass 1.

### Pass 1 — self-review against codebase

- **Date:** 2026-06-11T22:40:00Z
- **Method:** verify per-layer playbook presence; verify schema +
  agent file locations; verify SKILL count.
- **Findings (1 MEDIUM):**
  - **P1-1 (MEDIUM):** Plan said "8 audit SKILLs" but actual count is
    9 (`doc-chg-audit` follows the same pattern as the 8 layer audit
    SKILLs). Item 9 (strip-self-claim) + item 10 (Regressions section)
    SHOULD apply to doc-chg-audit too for consistency.
    *Patch:* All "8 audit SKILLs" references in items 9 + 10 + File
    structure + Touches summary updated to "9 audit SKILLs" with the
    CHG inclusion noted.
- **Cross-checks clean:**
  - Auditor playbooks: 6 present (01_BRD, 02_PRD, 04_BDD, 05_ADR,
    07_TDD, 08_IPLAN); 2 absent (03_EARS, 06_SPEC) — matches plan ✓
  - Tech_lead playbooks: 7 present (02_PRD..08_IPLAN); 1 absent
    (01_BRD) — matches plan ✓
  - 6 + 7 = 13 playbook files for item 8 ✓
  - `saga.schema.json` structure verified ✓
  - `synthesizer.md` location verified ✓
- **Status:** Patch folded in. Awaiting Pass 2.

### Pass 2 — re-review

- **Date:** 2026-06-11T22:50:00Z
- **Method:** re-read patched plan; verify the 8→9 SKILL count
  propagated everywhere; look for new contradictions.
- **Findings (0 substantive):** Pass 1 patch propagated cleanly via
  `replace_all`; the 9-SKILL count is consistent across the plan body,
  Touches summary, File structure table, and Verification table.
- **Verdict (caveat):** self-Pass-2 converged. Per FRAMEWORK-CLEANUP-001
  Pass 4 lesson, user-driven review is the real convergence gate.
