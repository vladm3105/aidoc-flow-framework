# PLM Plan — Plugin layer-model migration (legacy 12-layer → framework 8-layer)

| Field      | Value                          |
|------------|--------------------------------|
| Task       | PLM (Plugin Layer Migration)   |
| Depends on | P3-T1 §Deferred R2 · P5-T1 Q3 · D-0013 · `framework/registry/LAYER_REGISTRY.yaml` |
| Status     | PLANNED — 2026-05-22T00:48:53Z |
| Feeds      | Removal of the `docs/PARITY.md` "Known parity gap — SDD layer model" section |

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
- **OPEN — subtype families** (`doc-cspec/dspec/uxspec/riskspec/procspec` for
  SPEC; `doc-utest/itest/stest/ftest/ptest/sectest` for tests). The 8-layer
  framework defines SPEC and TDD each as a **single template, no subtypes**.
  These plugin families therefore have no framework backing. Their fate
  (retire / fold into `doc-spec`+`doc-tdd` as documented variants / keep as
  declared plugin-only extras) is a **user decision required before batch B4/B5**.

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
| `ai_dev_ssd_flow/scripts/validate_*.py|sh`, `framework/scripts/*` | **removed** — framework is spec-only (no runtime code). Replace "run `validate_X.py`" with the skill's own declarative validation checklist + a pointer to `framework/governance/` and the layer `README.md`. The plugin skill *is* the validator. |
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
| **B0** | This plan + rewrite spec + the `plm_lint` legacy-fingerprint checker | `plans/PLM-PLAN.md`, `tests/conformance/platforms/plm_lint.py` | — |
| **B1** | Roster: rename `doc-tspec*`→`doc-tdd*`, `doc-tasks*`→`doc-iplan*` (full body rewrite of those 12 skills); retire `doc-sys*`/`doc-req*`/`doc-ctr*`; fix orchestrator cross-refs (`doc-flow`, `skill-recommender`, `project-init`, `doc-naming`, READMEs, `agents/`); interim `docs/PARITY.md` — flip capability-matrix rows 7/8 (TDD/IPLAN no longer "gap") and rescope the gap section to "remaining families still legacy-numbered (see `plans/PLM-PLAN.md`)". May land in sub-commits (rename+retire+crossref; then the 12 body rewrites). | ~12 rewritten + 18 removed + ~16 cross-ref | — |
| **B2** | Body rewrite: `doc-brd`, `doc-prd`, `doc-ears` families | 3 families | — |
| **B3** | Body rewrite: `doc-bdd`, `doc-adr` families | 2 families | — |
| **B4** | Body rewrite: `doc-spec` family **(+ SPEC-subtype decision)** | 1 + OPEN | blocked on OPEN |
| **B5** | Test-subtype decision + rewrite (`doc-*test`) | OPEN | blocked on OPEN |
| **B6** | Helpers/orchestrators: `doc-review`, `doc-ref`, `doc-validator`, `quality-advisor`, remaining `*_quickref.md`, `REVIEW_DOCUMENT_STANDARDS.md`, etc. | residual | — |
| **B7** | Promote `plm_lint` into the conformance suite; delete the PARITY gap section; CHANGELOG/ROADMAP/TODO close-out | docs + tests | — |

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
| R4 | Subtype families have no framework home → ambiguous target | OPEN flagged; user decides before B4/B5; batches sequenced so subtypes are last |
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
