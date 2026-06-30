# BL-READY-SCORE-ADVISORY Plan — mark `*_ready_score` / `target_score` advisory in the layer templates

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | BL-READY-SCORE-ADVISORY                      |
| Type           | documentation                               |
| Status         | PLANNED — 2026-06-30T07:59:00-04:00         |
| Depends on     | none (design locked by author Q4 in `plans/FRAMEWORK-TODO.md`) |
| Feeds          | wholesale corpus regen (advisory wording propagates on regen) |
| Version impact | framework spec **PATCH** (`0.32.3 → 0.32.4`); plugin/Hermes product versions unchanged |

## Objective

Every layer template ships a `<next>_ready_score: "[Score]/100"` field (in
`document_control`) and a `target_score: ">=90/100"` field (in `health_score`).
These read as a **required gate**, but the score is **advisory** — it is computed
by the auditor review lens, never hand-authored, and the real gate is the
deterministic `sdd_doc_lint` floor. A blank score therefore makes a finished
artifact look half-done (BeeLocal #56, 52 occurrences across their artifact set).
This change marks the fields explicitly advisory in the framework templates (the
source), so the misread stops at the root. **No rubric, no offline scorer**
(author Q4 — that would contradict D54-F03: the audit skill IS the rubric).

## Scope

**In:**

- Add an advisory marker to **both** score fields in **all 7 layer templates**
  (BRD…TDD) — `<next>_ready_score` (×7) and `target_score` (×7), 14 field lines.
  See "Approach" for why all 7, not only the ADR/SPEC/TDD named in the feedback.
- Framework-spec PATCH bump (`0.32.3 → 0.32.4`) + CHANGELOG entry (GATE-SPEC) +
  re-vendor the plugin's bundled `framework/` copy.
- Record the marker-design choice as D-0042.

**Out of scope (deferred):**

- `framework/governance/REVIEW_TEAM.md:86` and
  `framework/layers/08_IPLAN/IPLAN-ECOSYSTEM.md:56` — these *document* the
  `*_ready_score` / `exec_ready_score` field families in reference tables; they
  are not artifact-template gate fields and do not produce the "blank reads as
  incomplete" misread. Left as-is (one optional clarifying clause considered in
  Pass review; see Review log).
- Any offline readiness rubric/tool (author Q4 — explicitly not built).
- `BL-STATUS-SCOPE` per-context `status` enum work (separate P3 item).
- Element-granular score semantics — n/a; the score is doc-level.

## Approach / Design

### Why all 7 layer templates, not only ADR/SPEC/TDD

The feedback (BeeLocal #56) names ADR/SPEC/TDD because that is what BeeLocal
authored, but the identical field pattern ships in **every** layer template:
`prd_ready_score` (BRD), `ears_ready_score` (PRD), `bdd_ready_score` (EARS),
`adr_ready_score` (BDD), `spec_ready_score` (ADR), `tdd_ready_score` (SPEC),
`iplan_ready_score` (TDD); plus a `target_score` in each `health_score` block.
Marking only 3 of 7 would leave the same misread live in the other 4 and create
an inconsistency a future consumer would re-file. The fix is uniform across all 7.

### Marker design (D-0042)

Two complementary, comment/guidance-only markers — no new content data keys in
`document_control`:

1. **Inline `#` comment on each score line.** `document_control` already annotates
   fields with inline comments (e.g. `status: Proposed  # Proposed | Accepted | …`),
   so this matches house style and never reads as data:

   ```yaml
   spec_ready_score: "[Score]/100"  # advisory — auditor-lens score; blank ≠ incomplete (the sdd_doc_lint floor is the gate)
   ```

   ```yaml
   health_score:
     spec_ready: "[X]%"
     target_score: ">=90/100"  # advisory readability target, not a merge gate
   ```

2. **One `_note:` key per `health_score` block** carrying the fuller statement.
   `_note:` is the established template guidance key (e.g.
   `ADR-TEMPLATE.yaml:376,435`, `TDD-TEMPLATE.yaml:223`):

   ```yaml
   health_score:
     spec_ready: "[X]%"
     target_score: ">=90/100"  # advisory readability target, not a merge gate
     _note: "Scores are advisory — computed by the auditor review lens, not hand-authored. The deterministic sdd_doc_lint floor is the real gate; a blank score is NOT incomplete."
   ```

The `<next>_ready_score` field gets the inline comment only (no sibling `_note:`,
because a `_note` key inside `document_control` would read as annotating the whole
block, not the one field — inline comment is unambiguous and matches the block's
existing style).

**Token-hygiene constraint:** the `test_spec_hygiene.py` scanner forbids engine
tokens (`hermes`, `mcp`, `.claude/`, …) and a *narrow* set of version strings —
only the literal field name `framework_version` and `SDD v3` strings, **not**
general semver (so `>=90/100`, `/100` are fine). The marker text uses none of the
banned tokens — `sdd_doc_lint` is the agnostic tool name, not a banned
`sdd_<verb>` token (the banned set is validate/create/review/remediate/…, not
`doc_lint`).

## File structure

### Modified

| Path | Change |
| ---- | ------ |
| `framework/layers/01_BRD/BRD-TEMPLATE.yaml` | inline comment on `prd_ready_score` (:186) + `target_score` (:958); `_note` in `health_score` |
| `framework/layers/02_PRD/PRD-TEMPLATE.yaml` | same for `ears_ready_score` (:139) + `target_score` (:627) |
| `framework/layers/03_EARS/EARS-TEMPLATE.yaml` | same for `bdd_ready_score` (:127) + `target_score` (:379) |
| `framework/layers/04_BDD/BDD-TEMPLATE.yaml` | same for `adr_ready_score` (:128) + `target_score` (:323) |
| `framework/layers/05_ADR/ADR-TEMPLATE.yaml` | same for `spec_ready_score` (:137) + `target_score` (:417) |
| `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml` | same for `tdd_ready_score` (:78) + `target_score` (:224) |
| `framework/layers/07_TDD/TDD-TEMPLATE.yaml` | same for `iplan_ready_score` (:44) + `target_score` (:282) |
| `framework/VERSION` | `0.32.3 → 0.32.4` (via `bump_version.py 0.32.4`) |
| `tests/conformance/platforms/test_plugin_release_metadata.py` | hand-edit the hard-pin literal `"0.32.3"` → `"0.32.4"` (:139) — the **one** step `bump_version.py` deliberately does NOT do (tripwire) |
| `CHANGELOG.md` | `[Unreleased]` entry (GATE-SPEC-E008) |
| `platforms/claude-code-plugin/framework/...` | re-vendored byte-identical copy of the 7 templates — **done automatically by `bump_version.py`** (it runs `sync-plugin-framework.sh` + `sdd_doc_lint/sync-vendored.sh` + `sync-version-refs.sh`) |
| `plans/DECISIONS.md` | D-0042 (marker design) |
| `plans/FRAMEWORK-TODO.md` | move `BL-READY-SCORE-ADVISORY` to Closed with merge ref |
| `plans/HANDOFF.md` | banner update |

(`bump_version.py 0.32.4` also rewrites both `FRAMEWORK_SPEC_VERSION` pins, every
skill manifest + playbook `framework_spec_version`, `SKILL_AUTHORING.md`, and the
READMEs, then runs the three sync scripts — all mechanical, not enumerated here.
The sole manual follow-up is the hard-pin literal above + the CHANGELOG entry.)

## Implementation sequence

### Task 1: annotate the 7 templates

- For each layer template, add the inline comment to the two score lines and the
  `_note:` key to the `health_score` block, per the marker design.
- Keep the YAML valid and the existing field values byte-unchanged (only comments
  - one new `_note` guidance key added).

### Task 2: framework-spec PATCH bump

- `python tools/bump_version.py 0.32.4` — bumps `framework/VERSION`, both FSV
  pins, all skill/playbook frontmatter + READMEs, and runs the three sync
  scripts (re-vendors the plugin bundle + vendored lint, fans the version refs).
- **Hand-edit the one tripwire** `bump_version.py` won't touch:
  `tests/conformance/platforms/test_plugin_release_metadata.py:139`
  `self.assertEqual(_plugin_framework_spec_version(), "0.32.3")` → `"0.32.4"`.
- Add the `CHANGELOG.md` `[Unreleased]` entry (GATE-SPEC-E008).

### Task 3: docs of record

- D-0042 in `plans/DECISIONS.md`; close the TODO entry; update HANDOFF banner.

## Verification

| #  | Check (command or observable) | Expected result | Maps to |
| -- | ----------------------------- | --------------- | ------- |
| V1 | `python -m pytest tests/conformance -q` | green (template parse + metadata + hygiene unaffected) | scope |
| V2 | `python tests/chg/spec_gate.py --base origin/main` | pass — VERSION + CHANGELOG present alongside the framework change | GATE-SPEC |
| V3 | `grep -rn advisory framework/layers/0[1-7]_*/*-TEMPLATE.yaml` rollup | 14 score lines annotated + 7 `_note`s across layers 01–07 (IPLAN/08 has none) | scope (all 7 layers) |
| V4 | plugin bundle drift guard (`test_plugin_framework_bundle.py`) | green — vendored copy byte-matches canonical | re-vendor |
| V5 | `python -m sdd_doc_lint examples/url-shortener/docs/` | unchanged vs `main` baseline (1× TH-RES-001, 5× REFGRAN01, 6× STY02) | no corpus regression |
| V6 | `python -m pytest tests/conformance/platforms/test_plugin_release_metadata.py test_version.py -q` | green — FSV pins + hard-pin literal == `0.32.4`; versions consistent | bump + tripwire |

## Docs to update

- [ ] `CHANGELOG.md` — `[Unreleased]` `### … Framework Spec 0.32.3 → 0.32.4` entry
- [ ] `plans/DECISIONS.md` — D-0042 (marker design)
- [ ] `plans/FRAMEWORK-TODO.md` — `BL-READY-SCORE-ADVISORY` → Closed
- [ ] `plans/HANDOFF.md` — banner + next steps
- [ ] `ROADMAP.md` — not applicable (no roadmap-level milestone)

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | A new `_note` key surfaces in authored docs and trips the linter | low | `tools/sdd_doc_lint` is key-agnostic — it never references `health_score`/`target_score`/`ready_score`/`_note`, and its only unknown-key validation is the `id_state` + `reuse.state` allow-lists (`__init__.py:507,1740`); there is no frontmatter unknown-key rejection path, so an extra `_note`/inline comment cannot be flagged |
| R2 | Marker text trips `test_spec_hygiene.py` engine-token / version-string scan | low | text uses no banned token (see Approach token-hygiene note); V1 catches it |
| R3 | Bump misses a propagation surface (recurring `bump_version.py` straggler) | med | V6 + the conformance version test; `BUMP-SKILL-AUTHORING-CHECKLIST-STRAGGLER` was closed 2026-06-29 so the known straggler is handled |
| R4 | Forget the manual hard-pin literal at `test_plugin_release_metadata.py:139` (PLANSTD-001 was bitten by exactly this) | med | explicit Task 2 step; V6 runs that test and fails red if the literal is stale |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | `*_ready_score` + `target_score` appear exactly 14× across the 7 layer templates (7 + 7), uniform pattern | `spec_ready_score` | framework/layers/05_ADR/ADR-TEMPLATE.yaml:137 |
| 2  | ADR `target_score` lives in a `health_score:` block beside `spec_ready` | `health_score` | framework/layers/05_ADR/ADR-TEMPLATE.yaml:415 |
| 3  | `document_control` annotates fields with inline `#` comments (house style for the score-line marker) | `status` | framework/layers/05_ADR/ADR-TEMPLATE.yaml:128 |
| 4  | `_note:` is an established template guidance key (quoted string sibling) | `_note` | framework/layers/05_ADR/ADR-TEMPLATE.yaml:376 |
| 5  | The only template-structure conformance test parses YAML + checks `metadata.layer`/`document_type` — it asserts no exact key set on `document_control`/`health_score` (adding comments + one `_note` is safe) | `test_template_parses_and_metadata_matches_registry` | tests/conformance/test_layers.py:35 |
| 6  | `test_spec_hygiene.py` forbids engine tokens + version strings in `framework/`; `sdd_doc_lint` is NOT a banned `sdd_<verb>` token | `ENGINE_TOKENS` | tests/conformance/test_spec_hygiene.py:19 |
| 7  | GATE-SPEC requires `framework/VERSION` bump (E005) + `CHANGELOG.md` (E008) on any `framework/**` change; reminder to re-vendor plugin bundle | `evaluate` | tests/chg/spec_gate.py:79 |
| 8  | Current framework spec version is `0.32.3` (→ `0.32.4` PATCH) | `0.32.3` | framework/VERSION:1 |
| 9  | Most recent decision is D-0041 → next free is D-0042 | `D-0041` | plans/DECISIONS.md:13 |
| 10 | The score field is auditor-lens-computed (advisory premise is true) — REVIEW_TEAM lists `*_ready_score` among fields the review subagent computes | `*_ready_score` | framework/governance/REVIEW_TEAM.md:86 |
| 11 | `bump_version.py <semver>` auto-runs `sync-plugin-framework.sh` + `sync-vendored.sh` + `sync-version-refs.sh` (re-vendor is NOT a separate manual step) | `sync-plugin-framework.sh` | tools/bump_version.py:135 |
| 12 | `bump_version.py` deliberately leaves one manual tripwire: the hard-pin literal in the plugin release-metadata test | `0.32.3` | tests/conformance/platforms/test_plugin_release_metadata.py:139 |
| 13 | IPLAN (08) template carries neither score field (`grep ready_score` → NONE) — "all 7 layer templates" = BRD…TDD (01–07) | `IPLAN-TEMPLATE.yaml` | framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:1 |
| 14 | Every `target_score` sits as the last key of a uniform `health_score:` block (clean `_note` insertion point) | `health_score` | framework/layers/01_BRD/BRD-TEMPLATE.yaml:958 |

## Review log

### Pass 1 — 2026-06-30T07:59:00-04:00 — self-review

- **F1 (re-vendor coupling wrong).** Draft listed `sync-plugin-framework.sh` as a
  separate manual Task-2 step. Verified `tools/bump_version.py:134` runs the three
  sync scripts itself → corrected Task 2 + the Modified table; re-vendor is
  automatic. Added Claim 11.
- **F2 (missing manual tripwire).** `bump_version.py` deliberately does NOT touch
  the hard-pin literal `"0.32.3"` at `test_plugin_release_metadata.py:139`
  (PLANSTD-001 was bitten by exactly this). Added it as an explicit Task-2 step, a
  Modified-table row, R4, V6, and Claim 12.
- **F3 (scope precision).** Confirmed IPLAN/08 template carries neither field
  (`grep` → NONE); "all 7 layer templates" = BRD…TDD (01–07). Tightened V3 glob to
  `0[1-7]_*` and added Claim 13.
- **F4 (health_score uniformity).** Confirmed all 7 `target_score`s are the last
  key of a `health_score:` block → uniform `_note` insertion. Added Claim 14.
- **F5 (bump invocation).** Confirmed CLI is `bump_version.py <semver>` (positional)
  → Task 2 now says `bump_version.py 0.32.4`.

### Pass 2 — 2026-06-30T08:15:00-04:00 — independent (fresh-context)

Dispatched a fresh-context `code-reviewer` agent against the real source with
instructions to verify every ledger citation, hunt missing load-bearing claims,
and challenge D-0042. It opened every cited file:line and confirmed all 14 ledger
rows + every File-structure citation literally true; confirmed no conformance
test / linter / bundle drift-guard / GATE-SPEC / hard-pin is broken by the edits;
confirmed the bundle guard is byte-identical `cp -R` (comments + `_note`
preserved) and the acceptance goldens are independent hand-crafted fixtures, not
template-derived. **Verdict: 0 load-bearing findings.** Two MINOR precision notes
folded in:

- **M1** — R1's evidence reworded: the real reason `_note` is safe is that
  `sdd_doc_lint` is key-agnostic (its only unknown-key checks are `id_state` +
  `reuse.state` at `__init__.py:507,1740`), not "copies into docs today" (no doc
  under `examples/*/docs/` carries a `_note` key).
- **M2** — Approach + token-hygiene wording tightened: the hygiene scanner's
  version-string ban is narrow (`framework_version` field name + `SDD v3` only),
  not general semver — `>=90/100` was never at risk.

**Result:** ready
