# PLUGIN-PROD-READINESS-001 Plan — fix the playbook-path-escape BLOCKER + 3 SHOULD-FIX items from the production-readiness audit

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | PLUGIN-PROD-READINESS-001                   |
| Type           | fix (production-readiness batch)            |
| Status         | READY — 2026-07-06 (Pass 2 independent; Pass 3 self) |
| Depends on     | none                                        |
| Feeds          | the Claude Code plugin is release-ready (core review works in a distributed install) |
| Version impact | **plugin PATCH** (`0.23.1 → 0.23.2`). **No `framework/` change** — all edits are the plugin's own skills/agents/README + the example meta-README; no GATE-SPEC, no spec bump. Auto-mergeable (non-spec-tier). |

## Objective

A 4-agent production-readiness audit of the Claude Code plugin found it clean/green on
packaging, conformance, tooling, versioning, and skill structure — with **one BLOCKER** and
three SHOULD-FIX items. This batch fixes them so the plugin is release-ready.

**🔴 BLOCKER — playbook / REVIEW_TEAM path escape.** The 9 `doc-*-audit` skills resolve their
per-`(layer,lens)` playbook from `${CLAUDE_PLUGIN_ROOT}/../../framework/playbooks/…`, and
`agents/synthesizer.md` reads `REVIEW_TEAM.md` the same way. The `/../../` climbs **two levels
above** the plugin root, but the files are vendored **inside** it at
`${CLAUDE_PLUGIN_ROOT}/framework/…`. The escaping path only resolves in the source-repo
checkout by coincidence (`platforms/claude-code-plugin/../../` = repo root, which happens to
contain `framework/`); **in a distributed install it points outside the plugin → every
playbook/contract load fails → the weighted-crew review collapses to zero coverage** (each
lens hits its own `BRANCH_FAILED "playbook missing"` path). the many other refs (500+) in the same skills
use the correct `${CLAUDE_PLUGIN_ROOT}/framework/…` — the `/../../` is a bug.

## Scope

**In:**

1. **[BLOCKER] Drop `/../../`** — replace `${CLAUDE_PLUGIN_ROOT}/../../framework/` →
   `${CLAUDE_PLUGIN_ROOT}/framework/` in the **11 refs**: the playbook-injection line of the 9
   `doc-*-audit` skills + the **2** `REVIEW_TEAM.md` refs in `agents/synthesizer.md` (`:121`
   and `:252`). (Verified: no other plugin file — commands/hooks/README/other agents — uses
   the `/../../` escape; V1 greps the whole `skills/`+`agents/` tree to zero.)
2. **[SHOULD-FIX] doc-ears drift** — `doc-ears/SKILL.md` mandates percentiles for **all**
   timing in **two** spots (`:106` "all timing uses p50/p95/p99 notation" + **`:143`** "Fill
   Quality Attributes (tabular, **percentile timing**)"), and `doc-ears-audit/SKILL.md:344`
   (the "Quantifiable constraints" audit row) does the same. Reconcile all three to the
   **already-shipped D54-F04 model**: latency/response-time → percentiles; a **non-latency**
   bound (cycle/iteration counts, event-windows, batch sizes, `*.count`) → a concrete value +
   unit (percentiles do not apply). Matches `framework/layers/03_EARS/EARS-TEMPLATE.yaml:223`.
   (Keep `:103` "`real-time` → p50<100ms…" — a legitimate vague-latency→percentile mapping.)
3. **[SHOULD-FIX] Deprecated-stub milestone** — `doc-review` + `trace-check` say "removed in
   v0.7.0"; the plugin is 0.23.1. **Bump the target to `v1.0.0`** (the ROADMAP cutover — the
   natural point to drop deprecated stubs) across the **7 occurrences**: the 4 SKILL lines + 2
   README rows + **`docs/SKILL_AUTHORING.md:25`** ("hard removal in v0.7.0"). *(Chose
   bump over remove: the stubs are exemplary — clearly `deprecated: true`, redirect to
   `doc-validator`, carry a migration command — and removing them ripples into the skill
   count + manifests + PARITY docs for no consumer benefit.)*
4. **[SHOULD-FIX] Example corpus baseline note** — the flagship `examples/url-shortener/`
   exits lint non-zero (1 `TH-RES-001` error — `CORPUS-PRD-TH-RES` — + 16 by-design `COV02`
   orphan warnings), both **known/tracked** baselines deferred to the next wholesale regen,
   but nothing in the corpus tells a consumer they're expected. Add a **"Known lint baseline"**
   note to `examples/url-shortener/README.md` (the meta-README, NOT a `docs/` cascade
   artifact) so a consumer running the example understands the non-zero exit; while there,
   drop the phantom `docs/.version` line (that file doesn't exist / isn't generated).
5. Bump `platforms/claude-code-plugin/VERSION` `0.23.1 → 0.23.2` (→ `sync-version-refs.sh`
   propagates to the 52 SKILL frontmatter + README + PARITY); plugin `CHANGELOG.md`; root
   `CHANGELOG.md`; `plans/DECISIONS.md` (D-0060); `plans/HANDOFF.md`.

**Out of scope (deferred — with rationale):**

- **The SHA-256 element-ID honesty gap** (framework-side, `ID_NAMING_STANDARDS.md`) — a
  `framework/` spec change gated on PROVISIONAL-IDS-002 (H-11c); separate + lower, not a
  plugin blocker.
- **GD-02…05 "Proposed → Accepted" status flip** — a `framework/governance/DECISIONS.md`
  hygiene item, separate from plugin readiness.
- **Regenerating the corpus** to clear the `TH-RES-001` + COV02 baselines — deferred to the
  wholesale regen per convention ([[project-examples-regenerated-wholesale]]); this plan only
  documents them so a consumer isn't surprised.

## Approach / Design (D-0060)

Four independent, low-risk fixes; the BLOCKER is the only load-bearing one. The path fix is
mechanical and unambiguous (the 500+ sibling `${CLAUDE_PLUGIN_ROOT}/framework/…` refs prove the
correct pattern; the playbooks are verified present at
`${CLAUDE_PLUGIN_ROOT}/framework/playbooks/`). doc-ears reconciliation
mirrors the D54-F04 wording already shipped in the template (no new design). The stub bump +
corpus note are doc-only. **No `framework/` file is touched** (the plugin skills are the
plugin's own canonical files, not the vendored bundle) → no GATE-SPEC, plugin PATCH.

**Backward-compat.** The path fix *restores* intended behavior (playbooks load in installs);
it doesn't change source-checkout behavior (the vendored path also resolves there). doc-ears
broadens acceptance (non-latency bounds stop being mis-mandated). Purely corrective.

## File structure

### Modified

| Path | Change |
| ---- | ------ |
| `platforms/claude-code-plugin/skills/doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan,chg}-audit/SKILL.md` | drop `/../../` from the playbook-injection ref (9 files) |
| `platforms/claude-code-plugin/agents/synthesizer.md` | drop `/../../` from the 2 `REVIEW_TEAM.md` refs |
| `platforms/claude-code-plugin/skills/doc-ears/SKILL.md` (`:106` + `:143`) + `doc-ears-audit/SKILL.md` (`:344`) | latency-vs-non-latency quantification (D54-F04 propagation) |
| `platforms/claude-code-plugin/skills/doc-review/SKILL.md` + `trace-check/SKILL.md` + `README.md` + `docs/SKILL_AUTHORING.md` | stub removal target `v0.7.0 → v1.0.0` (7 occurrences) |
| `examples/url-shortener/README.md` | "Known lint baseline" note; drop phantom `docs/.version` line |
| `platforms/claude-code-plugin/VERSION` (→ `0.23.2`) + plugin/root `CHANGELOG.md` | version + entries |
| `plans/DECISIONS.md` (D-0060) / `plans/HANDOFF.md` | docs |

## Verification

| #  | Check | Expected | Maps to |
| -- | ----- | -------- | ------- |
| V1 | grep the plugin `skills/` + `agents/` for `CLAUDE_PLUGIN_ROOT}/\.\./\.\./` | **zero** (all escapes removed) | BLOCKER |
| V2 | grep the 9 audit skills for the playbook ref | each now `${CLAUDE_PLUGIN_ROOT}/framework/playbooks/<NN>/<lens>.md` (resolves in the vendored bundle) | BLOCKER |
| V3 | grep `doc-ears/SKILL.md` + `doc-ears-audit/SKILL.md` for `percentile`/`p50/p95/p99` | every remaining hit is latency-scoped or the vague-latency mapping (`:103`); no surviving "all timing"/"percentile timing" universal mandate; non-latency→concrete bound added | doc-ears drift |
| V4 | grep the WHOLE plugin (incl. `docs/`) for `v0.7.0` | none (all 7 → `v1.0.0`) | stub milestone |
| V5 | `examples/url-shortener/README.md` has a "Known lint baseline" note; no `docs/.version` line | present / absent | corpus note |
| V6 | `python -m pytest tests/conformance -q` | green (incl. plugin drift/vendoring/manifest/version guards) | no regression |
| V7 | `platforms/claude-code-plugin/VERSION` = `0.23.2`; SKILL frontmatter version propagated | bumped | version |
| V8 | `git diff --stat` touches no `framework/**` | zero framework files | not spec-tier |

## Docs to update

- [ ] `platforms/claude-code-plugin/CHANGELOG.md` — `[0.23.2]`
- [ ] root `CHANGELOG.md` — plugin `0.23.1 → 0.23.2`
- [ ] `plans/DECISIONS.md` — D-0060 (production-readiness batch; the path-escape BLOCKER)
- [ ] `plans/HANDOFF.md` — progress + the deferred spec-side items

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | The path fix breaks source-checkout resolution | low | the vendored `${CLAUDE_PLUGIN_ROOT}/framework/playbooks/` also resolves in the checkout (verified present); V2 confirms the target exists |
| R2 | Missed one `/../../` occurrence | low | V1 greps the whole `skills/`+`agents/` tree for the escape pattern |
| R3 | doc-ears reconciliation contradicts the template audit lens | low | mirror the template's `:223` wording exactly (V3) |
| R4 | Removing the `.version` README line hides a real generated file | low | grep-confirmed the file does not exist and is not gitignored (it's a phantom) |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | The audit skill's playbook ref escapes the plugin root (BLOCKER) | `${CLAUDE_PLUGIN_ROOT}/../../framework/playbooks` | platforms/claude-code-plugin/skills/doc-brd-audit/SKILL.md:102 |
| 2  | The synthesizer agent escapes for REVIEW_TEAM.md | `${CLAUDE_PLUGIN_ROOT}/../../framework/governance/REVIEW_TEAM.md` | platforms/claude-code-plugin/agents/synthesizer.md:121 |
| 3  | The correct in-root pattern already exists in the same audit skill | `${CLAUDE_PLUGIN_ROOT}/framework/governance/` | platforms/claude-code-plugin/skills/doc-brd-audit/SKILL.md:66 |
| 4  | The playbooks ARE vendored at the in-root path (so the fix resolves) | `lens: architect` | platforms/claude-code-plugin/framework/playbooks/01_BRD/architect.md:3 |
| 5  | doc-ears mandates percentiles for ALL timing (drift) | `timing uses p50/p95/p99 notation` | platforms/claude-code-plugin/skills/doc-ears/SKILL.md:106 |
| 6  | doc-ears-audit's quantifiable-constraints row mandates percentiles | `timing uses p50/p95/p99` | platforms/claude-code-plugin/skills/doc-ears-audit/SKILL.md:344 |
| 7  | The current EARS spec splits latency vs non-latency (D54-F04) | `All latency/response-time requirements have p50/p95/p99 values;` | framework/layers/03_EARS/EARS-TEMPLATE.yaml:223 |
| 8  | The deprecated stubs promise removal in v0.7.0 (stale) | `removed in v0.7.0` | platforms/claude-code-plugin/skills/doc-review/SKILL.md:3 |
| 9  | The README repeats the v0.7.0 removal target | `removal in v0.7.0` | platforms/claude-code-plugin/README.md:55 |
| 10 | The example README documents a phantom `docs/.version` file | `.version` | examples/url-shortener/README.md:57 |
| 11 | The TH-RES-001 corpus baseline is tracked (deferred to regen) | `CORPUS-PRD-TH-RES` | plans/CORPUS-REGEN-RUNBOOK.md:31 |
| 12 | Current plugin version is 0.23.1 (PATCH target 0.23.2) | `0.23.1` | platforms/claude-code-plugin/VERSION:1 |

## Review log

### Pass 1 — 2026-07-06 — self-review

Drafted from the 4-agent production-readiness audit. The BLOCKER is verified (11 escaping
refs — 9 audit skills + synthesizer ×2 — vs the correct in-root pattern used 500+×; playbooks confirmed vendored in-root; only-resolves-in-checkout by
coincidence). doc-ears drift is the plugin-side gap left by D54-F04 (template-only). Stub bump
chosen over remove (minimal blast radius). Corpus note documents a tracked baseline (no
hand-edit of `docs/` artifacts). No `framework/` change → plugin PATCH, auto-mergeable. Pending:
independent Pass 2.

### Pass 2 — 2026-07-06 — independent (fresh-context adversarial)

All 12 citations verified. BLOCKER fix direction confirmed at source (the 11 escaping refs
exist; the playbook + REVIEW_TEAM targets ARE vendored in-root; the correct pattern is used
500+× in the same files; no other plugin file uses the escape). Stub-bump-vs-remove, phantom
`.version`, and the plugin-only boundary all confirmed. **Two LOAD-BEARING enumeration gaps
folded:**

- **7th `v0.7.0` occurrence missed** — `docs/SKILL_AUTHORING.md:25` ("hard removal in v0.7.0")
  was not in scope; `sync-version-refs.sh` won't touch it, so an implementer following the
  file list ships a stale doc and V4's whole-plugin grep fails. → Added to Scope #3 + the file
  table; V4 broadened to grep the whole plugin incl. `docs/`.
- **3rd doc-ears drift spot missed** — `doc-ears/SKILL.md:143` ("Fill Quality Attributes
  (tabular, **percentile timing**)") reinforces percentiles-for-all-timing; the old V3 grep
  wouldn't catch it. → Added `:143` to the reconciliation; V3 broadened to grep `percentile`
  in doc-ears (keeping the legit `:103` vague-latency mapping).

Plus 2 count fixes: the escape total is **11** (was "10"); the correct-pattern count is 500+
(was "59"). 0 remaining load-bearing.

### Pass 3 — 2026-07-06 — self-review (re-validate the Pass-2 fold)

Re-checked: the 7th v0.7.0 spot + the 3rd doc-ears line are now in Scope + the file table, and
V3/V4 are broadened to catch them (V4 = whole-plugin incl. `docs/`; V3 greps `percentile` in
doc-ears). Counts corrected (11 escapes / 500+ correct). Boundary still plugin-only (no
`framework/**`) → plugin PATCH. D-0060 is the next free decision number (D-0059 = H-11b). No
new gaps.

**Result:** ready
