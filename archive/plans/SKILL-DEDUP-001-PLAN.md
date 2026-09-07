# SKILL-DEDUP-001 Plan — de-duplicate the 36 per-layer plugin skills via template generation

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | SKILL-DEDUP-001                             |
| Type           | refactor                                    |
| Status         | PARKED — 2026-07-09 (founder decision). Template-generation approach **rejected** by independent review (see Review log Pass 2 — the per-layer skills are not ~96% boilerplate; chg-audit ≈60% identical, per-layer content is large/irregular). The motivating drift is already fixed (FRWK-REVIEW-002 PR-A). Not re-investigate this approach. If revisited, the candidate is **shared-section extraction** (dedup only the ~90-line identical blocks; runtime-Read trade-off) — a fresh founder decision + redraft. |
| Depends on     | FRWK-REVIEW-002 (surfaced the duplication; PR-A fixed the drift *instances*, this fixes the *class*). Consumes the post-FRWK-REVIEW-002 skill text as the generation baseline. |
| Feeds          | drift-proof per-layer skills; future per-layer changes edit one template, not 9 copies |
| Version impact | plugin MINOR (build-time generation + a new drift guard is a structural addition; no user-visible skill-behavior change if generation is faithful) |

## Objective

The 36 per-layer plugin skills (4 families × 9 layers — `doc-<layer>`,
`-audit`, `-fixer`, `-autopilot`) are ~57% duplicated boilerplate (measured:
`doc-prd-audit` and `doc-tdd-audit` differ by 26 of 589 lines after
layer-token normalization — ~96% identical). PR-A of FRWK-REVIEW-002 fixed the
drift *instances* by hand across all copies; this plan eliminates the drift
*class* by **generating** the 36 per-layer `SKILL.md` from one template per
family plus a small per-layer parameter block, with a conformance guard that
fails CI if a committed skill diverges from its generated form. Editing a
shared block then means editing one template, not 9 copies.

## Scope

**In:** the **36 per-layer family skills** (`doc-{brd,prd,ears,bdd,adr,spec,tdd,
iplan,chg} {,-audit,-fixer,-autopilot}` — 9 layers × 4 families). A per-family
template + per-layer parameter data + a generator + a drift-guard conformance
test + a regeneration pre-commit hook.

**Out of scope (deferred):**

- The **16 non-layer skills** (doc-flow, doc-naming, review-team, gate-check,
  project-*, security-audit, knowledge-extractor, adr-roadmap, charts-flow,
  quality-advisor, doc-validator, doc-ref, + the 2 deprecated stubs). They are
  genuinely distinct — not a template family — and stay hand-authored.
- **L16 (quality-advisor re-implements the audits' Structural-Checklist
  checks)** — a shared-source concern for a *non-layer* skill; if addressed, it
  is by pointing quality-advisor at the generated audit template's checklist,
  tracked as a follow-up once the template exists.
- **Behavioral change.** Generation must be *faithful* — the generated skills
  are byte-equivalent in meaning to today's hand-authored ones (modulo the
  drift PR-A already reconciled). This plan does not redesign skill behavior.
- The **framework/ spec**. Skills consume the spec; this is a Platform-B
  (plugin) build-tooling change only. No `framework/VERSION` bump.

## Approach

**Chosen: template generation** (recommended over the shared-reference
alternative — see Risks). Precedent: `scripts/sync-version-refs.sh` already
rewrites all 52 `SKILL.md` frontmatters in a pre-commit loop, so build-time
rewriting of committed skill files under a drift guard is an established pattern
in this repo.

1. **Extract templates.** For each of the 4 families, author a
   `skills/_templates/<family>.SKILL.md.tmpl` capturing the shared body with
   placeholders (`{{LAYER}}`, `{{NN}}`, `{{TYPE}}`, `{{LAYER_TITLE}}`, and named
   insertion points for the per-layer-specific blocks). The template body is the
   post-PR-A reconciled text (the audit-report path, iteration-cap citation,
   review_mode section, verdict clarifier are already unified — the template
   captures the *correct* version once).
2. **Per-layer parameter data.** `skills/_templates/layers.yaml` — one entry per
   layer with the ~5–25% layer-specific values: layer number, TYPE, title,
   crew/lens deltas, layer-specific checklist items, the genuinely-per-layer
   prose the normalization diff flagged (e.g. IPLAN's "solutions-architect
   carries three lens-roles" note).
3. **Generator.** `scripts/gen_skills.py` renders each of the 36
   `skills/<name>/SKILL.md` from `<family>.tmpl` + the layer's params. Frontmatter
   `version`/`framework_spec_version` stay owned by `sync-version-refs.sh` (the
   generator emits the current values; the sync hook remains the version
   authority — the two must not fight).
4. **Drift guard.** New `tests/conformance/platforms/test_skill_generation.py`:
   re-run the generator into a temp dir and assert byte-equality with the
   committed 36 skills (the same pattern as the vendored-bundle guard
   `test_plugin_framework_bundle` and the lint-vendoring guard). A hand-edit to a
   generated skill fails CI with "edit the template, not the generated file".
5. **Regeneration hook.** Add `gen_skills.py --check` (or `--write`) to
   pre-commit so a template/param edit regenerates and re-stages the 36 files
   (mirrors `sync-version-refs.sh`'s re-stage-on-its-own behavior).
6. **Cutover.** Generate the 36 files, confirm byte-identical to the current
   committed versions (proving faithful extraction), then commit the templates +
   generator + guard + the (unchanged) generated files together.

## Implementation sequence

1. **Extract one family first (audit) + generate + prove byte-identity** against
   the 9 current audit skills. If the generated output is not byte-identical, the
   template/params are wrong — iterate until zero diff. (Verify-one-family-before-
   propagating, mirroring the per-layer rollout discipline.)
2. Repeat for fixer, autopilot, creator families.
3. Add the drift-guard conformance test; confirm green.
4. Wire the pre-commit regeneration hook.
5. Re-sync the vendored plugin bundle (`tools/sync-plugin-framework.sh`) —
   the skills are NOT in the vendored `framework/` subtree, so confirm no bundle
   impact; the templates live under `skills/_templates/` (plugin tree, shipped).
6. Plugin VERSION MINOR bump; CHANGELOG + TAGGING row.

## Verification

- `python3 -m unittest discover -s tests/conformance` — green, including the new
  `test_skill_generation` drift guard, `test_skill_template_alignment`,
  `test_autopilot_saga_parity`, `test_model_precheck` (the generated skills must
  still satisfy every existing skill-structure test).
- `python3 tests/conformance/platforms/plm_lint.py --all` — clean (no legacy
  fingerprints introduced by the templates).
- **Byte-identity proof:** `git diff` after the first generation run shows **zero
  change** to the 36 `SKILL.md` files (proving the extraction is faithful, not a
  rewrite). The diff is purely additive (templates + generator + test + hook).
- `bash scripts/sync-version-refs.sh` dry-run on a scratch VERSION bump → the 36
  generated skills' frontmatter still updates correctly (generator and sync hook
  coexist).

## Docs to update

- `platforms/claude-code-plugin/CHANGELOG.md` (MINOR entry), root `CHANGELOG.md`
  `[Unreleased]`, `docs/TAGGING.md` release row, `plans/HANDOFF.md`.
- `platforms/claude-code-plugin/docs/SKILL_AUTHORING.md` — document that the 36
  per-layer skills are generated; contributors edit `skills/_templates/`, not the
  generated files.
- Close the `SKILL-DEDUP-001` entry in `plans/FRAMEWORK-TODO.md`.

## Risks

| Risk | Mitigation |
|------|------------|
| Extraction is not faithful (generated ≠ current) → silent behavior change | The cutover gate is **byte-identity** with the current committed skills; any diff blocks the commit until template/params are corrected. Extraction, not rewrite. |
| Generator and `sync-version-refs.sh` fight over frontmatter version | The generator emits current version values but the sync hook stays the version authority; the drift guard runs generation with the *current* VERSION so the two agree. Documented in SKILL_AUTHORING. |
| Genuinely-per-layer content mis-classified as shared → a real per-layer nuance lost | The normalization diff (26 lines for prd↔tdd) enumerates exactly what is per-layer; those become explicit `layers.yaml` params, reviewed per family before propagating. |
| Alternative (shared-reference extraction — move blocks into governance docs the skills cite) rejected | It adds a runtime `Read` per skill invocation and leaves the per-layer *wrappers* still duplicated; template generation removes the duplication at source with no runtime cost. Recorded here as the considered-and-rejected alternative. |
| Scope creep into the 16 non-layer skills | Explicitly out of scope; they are not a template family. |

## Claim ledger

| #   | Claim | Symbol | Citation |
| --- | ----- | ------ | -------- |
| 1 | 36 per-layer family skills exist (9 layers × 4 families) | `doc-brd-audit` | platforms/claude-code-plugin/skills/doc-brd-audit/SKILL.md:1 |
| 2 | audit siblings are ~96% identical after layer-token normalization (26 of 589 lines differ, prd↔tdd) — measured 2026-07-09 | `## Structural Checklist` | platforms/claude-code-plugin/skills/doc-prd-audit/SKILL.md:334 |
| 3 | total plugin skill body is ~13,790 lines (measured 2026-07-09) | `SKILL.md` | platforms/claude-code-plugin/skills/doc-tdd-audit/SKILL.md:1 |
| 4 | `sync-version-refs.sh` already rewrites all 52 SKILL.md frontmatters in a pre-commit loop (the build-time-rewrite precedent) | `for skill in platforms/claude-code-plugin/skills/*/SKILL.md` | scripts/sync-version-refs.sh:138 |
| 5 | a template-alignment conformance test already constrains skill structure (generated skills must keep passing it) | `test_required_structure_count_matches_template` | tests/conformance/platforms/test_skill_template_alignment.py:173 |
| 6 | autopilot saga parity is conformance-guarded (generated autopilots must keep passing) | `class AutopilotSagaParity` | tests/conformance/platforms/test_autopilot_saga_parity.py:51 |
| 7 | model-precheck conformance asserts exactly the 8 layer autopilots (generation must preserve the CHG-excluded asymmetry) | `class ModelPrecheckRollout` | tests/conformance/platforms/test_model_precheck.py:43 |
| 8 | plm_lint enforces no legacy fingerprints across skill families (templates must stay clean) | `def scan` | tests/conformance/platforms/plm_lint.py:137 |
| 9 | the vendored-bundle drift-guard pattern (regenerate → assert byte-identity) exists to mirror for the skill drift guard | `test_bundle_fileset_matches_canonical` | tests/conformance/platforms/test_plugin_framework_bundle.py:45 |
| 10 | no skill-generation tooling exists yet (this is net-new; verified by directory scan 2026-07-09) | `scripts/` | scripts/sync-version-refs.sh:10 |
| 11 | PR-A already reconciled the drift instances the template will capture as the correct single copy (audit-report path, iteration-cap citation) | `.aidoc/audit/01_BRD-audit.md` | platforms/claude-code-plugin/skills/doc-brd-audit/SKILL.md:32 |
| 12 | the IPLAN-specific "three lens-roles" nuance is a genuine per-layer param (not shared boilerplate) | `solutions-architect` | platforms/claude-code-plugin/skills/doc-iplan-audit/SKILL.md:18 |

## Review log

### Pass 1 — 2026-07-09 — self-review (draft)

- Scoped to the 36 per-layer family skills only; the 16 non-layer skills and the
  L16 quality-advisor concern are explicitly deferred (minimal-and-realistic).
- Chose template generation over shared-reference extraction (Risks table
  records the rejected alternative and why: no runtime Read cost, removes the
  per-layer wrapper duplication that shared-ref leaves behind).
- Grounded the central duplication claim in a fresh measurement (prd↔tdd audit =
  26/589 lines differ after normalization) rather than the prior review's
  estimate.
- Anchored the design on two existing repo patterns: the `sync-version-refs.sh`
  pre-commit rewrite loop (build-time file rewriting) and the vendored-bundle
  drift guard (regenerate → assert byte-identity).
- Open question for the independent pass: does any conformance test read a skill
  file's *exact byte content* (vs structure) in a way that a faithful-but-
  reformatted generation would break? The byte-identity cutover gate should catch
  this, but the reviewer should confirm the generator can reproduce the current
  files exactly (whitespace, section order) or the guard is unachievable.

### Pass 2 — 2026-07-09 — independent (fresh-context subagent) — APPROACH INVALIDATED

The independent review found **3 load-bearing findings; the plan is NOT ready
and the whole-file template-generation premise does not hold**:

- **LB-1 (decisive):** the central duplication measurement was cherry-picked
  from the single most-similar pair and understated. Independently re-measured:
  prd↔tdd audit differ by **44–48** lines (not 26); family-wide, **`chg-audit`
  vs `prd-audit` = 238/589 differing (~60% identical, not ~96%)**,
  `iplan-audit` = 107, `brd-audit` = 52; all 9 normalized audit skills have
  distinct md5s. The genuinely-per-layer content — crew-weight dicts
  (`doc-prd-audit:84` vs `doc-tdd-audit:84`), lens→agent maps, layer-specific
  Structural-Checklist rows (`:354-357`), `deliverable_type` values, output
  findings-sections — is **large and irregular**, not a "small param block."
  Byte-identity is reachable only by pushing ~238 lines of chg-specific content
  into `layers.yaml`, at which point the template degenerates into per-layer
  content and the dedup ROI is illusory for chg/iplan.
- **LB-2:** the creator family (`doc-<layer>`, ~37% identical: prd↔tdd = 129/205
  differing) yields near-zero dedup and should be deferred, not templated.
- **LB-3:** SemVer should be **PATCH** (byte-identical shipped output = internal
  build tooling), not MINOR — per the REVIEW-CALIBRATION-001 precedent.
- Minor: row-12 line should be `:94-100` (claim true, line off); generator ↔
  sync-hook coexistence + pre-commit ordering under-specified;
  `sync-version-refs.sh:305` uses `git add -u` (tracked only) so net-new
  generated files need explicit `git add`; row-7 CHG "asymmetry" overstated (the
  exclusion is in the test's list, not the skill content).

**Consequence:** the whole-file template-generation approach is **rejected as
drafted**. The real, verified duplication is concentrated in the ~90-line
*shared sections* (Saga interaction, Break-circuit policy, Adaptation, report
format) that ARE near-identical across layers — while the per-layer content
(crews, checklists, lens maps) genuinely differs. That points to the
**shared-section extraction** approach (dedup the identical blocks via a shared
reference the skills already cite; keep per-layer content hand-authored) — the
alternative this plan's Pass 1 rejected. Re-scoping to that approach is an
architectural fork with its own trade-off (a runtime `Read` per invocation), so
it is **escalated to the founder** rather than folded unilaterally.

**Result:** NOT ready — approach requires a founder decision before redraft
(template-generation rejected; shared-section extraction is the candidate
replacement). Blocked pending that decision.
