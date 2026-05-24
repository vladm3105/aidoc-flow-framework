# PLM Plan — Plugin layer-model migration (legacy 12-layer → framework 8-layer)

| Field      | Value                          |
|------------|--------------------------------|
| Task       | PLM (Plugin Layer Migration)   |
| Depends on | P3-T1 §Deferred R2 · P5-T1 Q3 · D-0013 · `framework/registry/LAYER_REGISTRY.yaml` |
| Status     | ✅ COMPLETE — 2026-05-22 (B0–B7 landed; corpus fully 8-layer; conformance 32/32) |
| Feeds      | Removal of the `docs/PARITY.md` "Known parity gap — SDD layer model" section (done) |

## Objective

The Claude Code plugin's skill corpus was authored against the **legacy
12-layer SDD model** (BRD·PRD·EARS·BDD·ADR·**SYS·REQ·CTR**·SPEC·**TSPEC·TASKS**·Code),
not the framework's current **8-layer model**
(BRD·PRD·EARS·BDD·ADR·SPEC·**TDD·IPLAN**·Code). The mismatch is pervasive,
not cosmetic: as of 2026-05-22, **116 of 142 skills (82 %)** carry at least
one legacy fingerprint (legacy `layer:` numbers 9–12, `ai_dev_ssd_flow/`
paths, "Layer 9–12" prose, `.claude/skills/` install paths, SYS/REQ/CTR cited
as upstream layers, legacy element-code scheme, and dead validation-script
references). This task migrates the whole corpus to the 8-layer model so the
plugin conforms to the spec it ships against, then deletes the documented
parity gap.

## Scope

**In:**

- All `platforms/claude-code-plugin/skills/**` (SKILL.md bodies, frontmatter,
  `*_quickref.md`, family READMEs, `SHARED_CONTENT.md`).
- Family roster changes: rename `doc-tspec*`→`doc-tdd*`,
  `doc-tasks*`→`doc-iplan*`; retire `doc-sys*`, `doc-req*`, `doc-ctr*`.
- Cross-references in `agents/`, `commands/`, and orchestrator skills.
- A migration **verification checker** (legacy-fingerprint gate), promoted to
  the conformance suite at the end.
- `docs/PARITY.md`, `CHANGELOG.md`, `ROADMAP.md`, `plans/MIGRATION_TODO.md`.

**Out (this task):**

- Hermes (already on the 8-layer model since P2-T9).
- The `framework/` spec itself (it is the contract; unchanged).
- Net-new skill capability beyond the layer remap.

**Subtype families — RESOLVED (D-0015, 2026-05-22):** the SPEC-subtype
(`doc-cspec/dspec/uxspec/riskspec/procspec`) and test-subtype
(`doc-utest/itest/stest/ftest/ptest/sectest`) families are **kept as
plugin-only authoring helpers** under SPEC (L6) / TDD (L7) and **migrated**
like every other family (not retired, not folded). B4 migrates `doc-spec` +
the 5 SPEC-subtypes; B5 migrates the 6 test-subtypes.

## Approach

### Shared 8-layer rewrite spec (authoritative for every batch)

**(1) Layer mapping** — apply everywhere a layer name/number appears (prose,
`layer:` frontmatter, tags like `layer-NN-artifact`, paths, upstream/downstream
chains):

| Legacy artifact | Legacy # | → New artifact | New # | Notes |
|---|---|---|---|---|
| BRD  | 1  | BRD   | 1 | unchanged |
| PRD  | 2  | PRD   | 2 | unchanged |
| EARS | 3  | EARS  | 3 | unchanged |
| BDD  | 4  | BDD   | 4 | unchanged |
| ADR  | 5  | ADR   | 5 | unchanged |
| SYS  | 6  | **(removed)** | — | system-architecture concerns fold into ADR (L5) + SPEC (L6) |
| REQ  | 7  | **(removed)** | — | atomic requirements fold into EARS (L3) formal requirements |
| CTR  | 8  | **(removed)** | — | interface/data contracts fold into SPEC (L6) behavior contracts |
| SPEC | 9  | SPEC  | 6 | renumbered |
| TSPEC| 10 | **TDD**   | 7 | renamed + renumbered |
| TASKS| 11 | **IPLAN** | 8 | renamed + renumbered |
| Code | 12 | Code  | — | output target, not a doc layer |

Upstream/downstream chains rebuild from `LAYER_REGISTRY.yaml` `can_reference` /
`downstream`: e.g. TDD upstream = BRD,PRD,EARS,BDD,ADR,SPEC; IPLAN upstream =
…,SPEC,TDD; SPEC upstream = BRD,PRD,EARS,BDD,ADR. **No SYS/REQ/CTR in any
chain.**

**(2) Element-ID scheme** — replace the legacy 3-segment `TYPE.NN.xxxx` and the
numeric type-code scheme (SYS.26, REQ.27, TSPEC.40–45, etc.) with the new
4-segment standard from `framework/governance/ID_NAMING_STANDARDS.md`:

- Hierarchical elements: `TYPE.NN.SS.xxxx` (`xxxx` = 4-char hex hash), TYPE ∈
  {BRD,PRD,EARS,BDD,ADR,TDD}.
- Document-level (dash) refs: `SPEC-NN`, `ADR-NN`, `IPLAN-NN`.
- Delete the legacy numeric type-code tables (40/41/42/43/44/45, 26, 27) — the
  8-layer model has no such codes. Test categories live as TDD section content,
  not ID codes.

**(3) Path mapping** — every external path must resolve in the 8-layer repo:

| Legacy reference | → New target |
|---|---|
| `ai_dev_ssd_flow/NN_X/…` / `framework/NN_X/…` | `framework/layers/<newNN>_<X>/…` (e.g. `10_TSPEC`→`07_TDD`, `11_TASKS`→`08_IPLAN`, `09_SPEC`→`06_SPEC`) |
| `…/{TYPE}-MVP-TEMPLATE.md` | `framework/layers/<NN>_<X>/{TYPE}-TEMPLATE.yaml` (templates are `.yaml`) |
| `ai_dev_ssd_flow/scripts/validate_*.py|sh`,`framework/scripts/*` | **removed** — framework is spec-only (no runtime code). Replace "run `validate_X.py`" with the skill's own declarative validation checklist + a pointer to `framework/governance/` and the layer `README.md`. The plugin skill *is* the validator. |
| `.claude/skills/doc-X/…` | plugin-relative `../doc-X/…` (sibling skills) |
| `framework/ADR/…`, `framework/11_TASKS/…` | `framework/layers/05_ADR/…`, `framework/layers/08_IPLAN/…` |

**(4) Frontmatter normalization** — `layer:` → new number (drop for retired);
`artifact_type:` → new prefix; `upstream_artifacts`/`downstream_artifacts` →
rebuilt chains; tag `layer-NN-artifact` → new NN. Skill `name:` always equals
its directory name. `description:` updated to the new artifact + layer.

**(5) Terminology** — TSPEC→TDD, TASKS→IPLAN, drop SYS/REQ/CTR. **Caution:**
the bare tokens `SYS`/`REQ`/`CTR`/`TASKS` also occur as English words
(`requirements`, `system`, `tasks`) and inside traceability/ID prose — never
blanket find/replace. Edit only where the token denotes a *legacy layer*.

### Batches (each: edit → run checker → run conformance → commit → push → tick checklist)

| Batch | Content | Families / files | Status |
|---|---|---|---|
| **B0** | This plan + rewrite spec + the `plm_lint` legacy-fingerprint checker | `plans/PLM-PLAN.md`, `tests/conformance/platforms/plm_lint.py` | ✅ DONE 2026-05-22 |
| **B1** | Roster: renamed `doc-tspec*`→`doc-tdd*`, `doc-tasks*`→`doc-iplan*` (12 bodies fully rewritten to `07_TDD`/`08_IPLAN`); retired `doc-sys*`/`doc-req*`/`doc-ctr*` (142→125 skills); migrated orchestrators `doc-flow`+`SHARED_CONTENT`, `skill-recommender`, `project-init` to the 8-layer flow; realigned the 9-agent roster; interim `docs/PARITY.md`. Verified: `plm_lint` scope `{doc-tdd,doc-iplan,doc-flow,skill-recommender,project-init}` clean; conformance 31/31; 125 skills; frontmatter parses + `name==dir`. `MIGRATED` remaining: 108 files. | 14 rewritten + 17 removed + 5 orchestrators/agents | ✅ DONE 2026-05-22 |
| **B2** | Body rewrite: `doc-brd`, `doc-prd`, `doc-ears` families (21 files; layer numbers 1-3 unchanged, but element IDs 3→4-segment, paths→`framework/layers/`, downstream chains + cumulative-tag tables → 8 layers, dead validation-scripts removed). Verified: `plm_lint` scope clean (91 files remain); conformance 31/31; 125 skills; name==dir. | 3 families / 21 files | ✅ DONE 2026-05-22 |
| **B3** | Body rewrite: `doc-bdd` (L4), `doc-adr` (L5) families + `adr-roadmap` (15 files). ADR uses dual refs (doc `ADR-NN` + element `ADR.NN.SS.xxxx`). Verified: `plm_lint` scope clean (81 remain); conformance 31/31; 125 skills; name==dir. | 2 families + adr-roadmap / 15 files | ✅ DONE 2026-05-22 |
| **B4** | Body rewrite: `doc-spec` (renumbered L9→**L6**, dropped SYS/REQ/CTR upstream) + the 5 SPEC-subtype families (`doc-cspec/dspec/uxspec/riskspec/procspec`) repositioned as SPEC-L6 specialization helpers per D-0015 (33 files). Verified: `plm_lint` scope clean (48 remain); conformance 31/31; 125 skills; name==dir; layer:6. | doc-spec + 5 subtypes / 33 files | ✅ DONE 2026-05-22 |
| **B5** | Body rewrite: the 6 test-subtype families (`doc-utest/itest/stest/ftest/ptest/sectest`) repositioned as TDD-L7 specialization helpers per D-0015 (36 files; legacy TSPEC subtype codes 40-45, L10 → TDD test-case content with a test_focus). Verified: `plm_lint` scope clean (12 remain); conformance 31/31; 125 skills; name==dir; layer:7. | 6 subtypes / 36 files | ✅ DONE 2026-05-22 |
| **B6** | Helper/orchestrator skills (12 files): `doc-naming` (+ the deleted element-code system), `doc-validator`, `doc-ref`, `charts-flow`, `trace-check`, `quality-advisor`, `project-mngt`, `context-analyzer`, `workflow-optimizer`, `REVIEW_DOCUMENT_STANDARDS.md` + 2 quickrefs. Verified: **`plm_lint --all` clean (whole corpus, 0 fingerprints)**; conformance 31/31; 125 skills; all 125 SKILL.md name==dir. | 12 files | ✅ DONE 2026-05-22 |
| **B7** | Promoted the gate into the conformance suite (`tests/conformance/platforms/test_plm_lint.py`, suite 31→**32**, enforces `scan(all)`); deleted the `docs/PARITY.md` gap section (→ "both platforms aligned"); CHANGELOG close-out (project + plugin `[Unreleased]`). | docs + tests | ✅ DONE 2026-05-22 |

## Step sequence

1. **B0** — write this plan (≥2 review passes); write `plm_lint` checker; land.
2. **B1…B6** — per the batch table; one logical change per commit. The checker
   carries a `MIGRATED` set and **fails only on fingerprints inside already-migrated
   families/files**, printing the remaining count for the rest. Each batch adds
   its families to `MIGRATED`. (Consequence: retired-family cross-refs and legacy
   numbers in *not-yet-migrated* families are tolerated until their own batch.)
3. Resolve the **OPEN subtype decision** with the user before B4/B5.
4. **Verify** each batch (below).
5. **B7 / Land** — checker green corpus-wide → promote to conformance; remove
   PARITY gap; update `CHANGELOG.md` / `ROADMAP.md` / `plans/MIGRATION_TODO.md`.

## Verification

Run after every batch; nothing is "done" until both pass:

1. **Existing conformance** stays green: `python3 -m unittest discover -s tests/conformance` (31 checks).
2. **`plm_lint` checker** reports zero legacy fingerprints in the batch's
   completed scope. Fingerprints flagged:
   - `^\s*layer:\s*(9|1[0-2])\b` in frontmatter,
   - `\bLayer (9|10|11|12)\b` / `\bL(9|10|11|12)\b` in prose,
   - `ai_dev_ssd_flow/`, `framework/scripts/`, `\.claude/skills/`,
   - `framework/(ADR|SYS|REQ|CTR|TSPEC|TASKS|\d{2}_[A-Z]+)/` legacy paths —
     note this does **not** match the valid `framework/layers/<NN>_<X>/`
     (after `framework/` comes `layers/`, not `\d{2}_`),
   - `doc-(sys|req|ctr|tspec|tasks)\b` references,
   - legacy element codes: `\b(SYS|REQ|CTR|TSPEC|TASKS)\.\d` and the numeric
     type-code tables.
   Each pattern is **layer-context anchored** to avoid matching the English
   words "system/requirement/tasks" — see checker docstring. Enforced only over
   the `MIGRATED` scope until B7.
3. **Frontmatter still parses** + `name == dirname` for every skill (the
   readiness check already in use).

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Blanket token replace corrupts legitimate prose/IDs (`requirements`, traceability) | Spec rule (5): edit only layer-denoting tokens; checker patterns are context-anchored; per-batch human review of the diff |
| R2 | Conformance does not police skills (out of scope), so regressions slip in | B0 adds `plm_lint`; B7 promotes it into the suite to lock the model in |
| R3 | Renames lose git history / break cross-refs | use `git mv`; grep-sweep cross-refs in the same batch as the rename |
| R4 | Subtype families have no framework home → ambiguous target | RESOLVED (D-0015): kept as plugin-only L6/L7 helpers, migrated in B4/B5 — each subtype references (not redefines) its parent layer's single template |
| R5 | Multi-session work lost to ephemeral container | plan + checker committed in B0; `HANDOFF.md` updated each batch; per-batch push |
| R6 | Retiring SYS/REQ/CTR **deletes their authoring guidance** (the new model has no such layer) — per the user's "retire" decision, no skill content is preserved | If any SYS/REQ/CTR *authoring* guidance should survive inside the ADR/SPEC/EARS skills, that is added scope — flag to the user before B1 deletes the families |

## Review log

### Pass 1 — 2026-05-22T00:48:53Z

- Checker would have failed B1 on B2–B6 content → added a `MIGRATED` scope; the
  checker enforces only migrated families and prints remaining count for the rest.
- Legacy-path pattern risked flagging the valid `framework/layers/<NN>_<X>/` →
  documented that it matches only `framework/<NN>_<X>/` (no `layers/` segment).
- B1 was over-stuffed and silently dropped PARITY → allowed sub-commits and added
  an interim PARITY matrix update (rows 7/8 + rescoped gap section) to B1.
- R6 wrongly implied SYS/REQ/CTR content gets migrated → reworded: "retire" =
  delete; preserving their guidance would be added scope, flag before B1.

### Pass 2 — 2026-05-22T00:48:53Z (verification calibrated against live source)

- Dry-ran every checker pattern: `framework/` (the 8-layer contract) is **clean**
  — zero false positives.
- Legacy-path regex matched `framework/ADR/`, `framework/11_TASKS/` but **not**
  `framework/layers/07_TDD/…` — confirmed.
- Prose regex matched "Layer 10" / "L9" but **not** "Layer 6/7" (valid) —
  confirmed.
- Element-code regex matched `TSPEC.01.4001`, `SYS.01.2601`, `REQ.01.2701` but
  **not** the valid new `BRD.01.07.a7f3` / `SPEC-01` — confirmed.
- No new findings. Plan ready to implement.

---

## Post-migration gap audit — 2026-05-22 (after B7)

A skeptical review (cross-checked against the v3.2 source on
`legacy-ucx-v3.2-read-only`) confirmed the **framework** 8-layer model
correctly absorbs the deprecated SYS/REQ/CTR layers (SYS→SPEC C4-Component;
CTR→SPEC interfaces §3; REQ→EARS atomic-testable requirements). It also found
that the per-batch gate had **blind spots** — it scanned only `skills/`, and
its patterns missed dash-form refs (`SYS-002`/`REQ-001`), legacy `docs/NN_X`
dir tokens, and 3-segment IDs on valid prefixes — which let deprecated-layer
residue survive in the plugin surface.

**Fixed (see D-0016):**

- `agents/requirements-analyst.md` — modeled REQ as a live layer
  (`BRD→PRD→EARS→REQ→SPEC`, `docs/REQ/`, `REQ-NNN`, 3-segment IDs). Rewritten so
  the requirements lane terminates at **EARS**; 4-segment IDs; `docs/03_EARS/`.
- `skills/trace-check/examples/example_validation_report.md` — traced to
  deprecated `SYS-002`/`REQ-001`; rewritten to 8-layer traceability + 2-digit
  doc refs.
- `skills/doc-validator/SKILL.md` — broken `../doc-brd-validator/` → existing
  `../doc-brd-audit/` (doc-brd ships no validator).

**Gate hardened:** `plm_lint` now also scans `agents/` + `commands/` and adds
`legacy-doc-ref`, `legacy-layer-dir`, and a context-aware `legacy-3seg-id`
pattern (still enforced in conformance via `test_plm_lint.py`; suite 32). Bare-
token / `12-layer`-prose patterns intentionally omitted (they recur in
legitimate Version-History rows). `project-mngt` (generic REQ-NN) left as-is per
user decision; excepted in the checker.
