# Framework TODO — Example-Driven Discovery Backlog

> Triage queue for framework inconsistencies / bugs / improvements
> discovered while driving the examples corpus (`examples/url-shortener/`)
> end-to-end. Per [[feedback_framework_todo_list]] and
> [[feedback_seed_examples_are_acceptance_tests]]: examples are the
> system-under-test; their friction is the framework's truth.
>
> **Rules:**
>
> - Append entries inline as discovered. No "later PR" — the entry IS
>   the capture moment.
> - Each entry: tag + one-line title + Context (link to commit/PR/plan
>   that surfaced it) + Fix shape (one-line description of what would
>   resolve it). ≤ 3 lines per entry.
> - Tags: `[lint]` / `[harness]` / `[skill]` / `[template]` / `[sync]` /
>   `[plan-review]` / `[docs]` / `[hermes-parity]` / `[example-corpus]`.
> - Once an item is large enough to design, promote to a formal plan
>   and link from the TODO entry as `→ <NAME>-PLAN.md`. The TODO entry
>   stays open until the plan ships, then moves to **Closed** with the
>   merge-commit ref.
> - Don't double-track. If a plan already exists, cross-reference it
>   instead of creating a new entry.

## Open

> **CONSUMER-FEEDBACK-001 progress (2026-06-27):** 3 consumer logs triaged → 22
> items (the 3 dated banners below), orchestrated by
> `plans/CONSUMER-FEEDBACK-001-PLAN.md`. **Closed:** `BL-TAG-CHAIN-GATE-SYNC`
> (#180/#181). **CFB-PR-2 coverage engine — SHIPPED (full arc):**
> `ENG-FWD-COVERAGE` forward gate `COV01` (#187, spec 0.24.0); `D54-F13`/`D54-F05`
> backward gate `COV02` (#190, 0.25.0); GD-03 ref-granularity policy (#192,
> 0.26.0); `BL-REF-GRANULARITY` + `D54-F07` enforcement `REFGRAN01` (#194,
> 0.27.0). **Remaining open items** (in this file): `CORPUS-REFGRAN-RECASCADE`,
> the element-level `COV01`/`COV02` upgrade (catches the 15 orphaned BDD
> scenarios), `BL-STATUS-SCOPE` (PR-3b), sub-PRs 2c (phase reconciliation) + 2d
> (BDD roll-up), and the D54/ENG/BL items for the later waves.

### `[sync]` `BUMP-SKILL-AUTHORING-CHECKLIST-STRAGGLER` — `bump_version.py` misses the SKILL_AUTHORING acceptance-checklist line

- *Context:* recurred in CFB-PR-2 2a-core step 6 (0.23.1→0.24.0) AND 2b step 3
  (0.24.0→0.25.0). `SKILL_AUTHORING.md:112` (`- [ ] … framework_spec_version:
  "X" present.`) is a backtick-wrapped checklist line, not the `^…
  framework_spec_version: "…"` frontmatter form `bump_version.bump_fsv` matches,
  so every framework bump leaves it stale (fixed by hand each time). Author-facing
  (a skill author following the checklist asserts the wrong value).
- *Fix shape:* extend `bump_version.py` (a `bump_plugin_readme`-style targeted
  rewrite for the SKILL_AUTHORING checklist line), or add a conformance guard
  asserting the checklist version == `framework/VERSION`.

### `[harness]` `RELEASE-CHANGELOG-TEST-CONVENTION-GAP` — `tests/release/test_changelog_entry.py` doesn't match the `[Unreleased]` convention

- *Context:* surfaced in CFB-PR-2b self-review. The test requires a top-level
  `## [<version>]` heading, but the repo nests releases under `## [Unreleased]`
  with `### Added — Framework Spec X → Y`. It is RED at HEAD for `0.25.0` (and on
  `main` for `0.24.0`) — but **outside CI scope** (conformance.yml runs only
  `tests/conformance`; hermes.yml runs pytest under `platforms/hermes`), so CI
  stays green. Pre-existing, not a 2b regression.
- *Fix shape:* update the test to recognize the `[Unreleased]` + `### … X → Y`
  convention, or move release entries to top-level `## [X]` headings on release.

### `[sync]` `SYNC-VERSION-PROVENANCE-OVERBUMP` — `sync-version-refs.sh` global-sed rewrites historical version refs

- *Context:* CFB-PR-2 2a-core step 6 (`a0cb426f`). The framework-spec bump
  `0.23.1 → 0.24.0` swept two HISTORICAL provenance lines in `docs/PARITY.md`
  (SAGA-PARITY-001 / D-0031 "arriving with framework spec 0.23.0") to 0.24.0 —
  `scripts/sync-version-refs.sh` does a global `sed s|<old>|<new>|g` for the
  framework-spec string, matching every occurrence, not just the current-state
  row. (It only matched because the current-state rows were themselves stale at
  0.23.0, so `fw_prev` resolved to 0.23.0.)
- *Fix shape:* anchor the framework-spec replacement to the documented
  current-state row only (drop the `/g`, or match the `claude-code-plugin/vX
  (framework spec …)` line specifically) so future bumps stop rewriting
  provenance. Restored the two lines by hand in `a0cb426f`.

### `[example-corpus]` `CORPUS-REFGRAN-RECASCADE` — 7 doc-level trace tags need element-level re-cascade (REFGRAN01)

- *Context:* CFB-PR-3 shipped `REFGRAN01` (GD-03 enforcement). The corpus carries
  **7 doc-level trace tags to element-declaring layers** (warnings in `build`,
  errors in `gate-code`): `BDD-01:31,55`, `SPEC-01:31,67,469`, `TDD-01:204`,
  `IPLAN-01:43`. 5 are redundant (drop — element-level sibling present); 2 need
  conversion (`BDD-01:55` feature `@ears` → fan-out the union of its 26 scenarios'
  elements per GD-03; `SPEC-01:67` prose → element-level).
- *Fix shape:* re-cascade via the `doc-<layer>-fixer` skills (never hand-edit) —
  **blocked in framework-dev sessions** (the plugin skills aren't invocable
  here). Either run the fixers in a live plugin session, OR add a REFGRAN
  `--fix` mechanical auto-fixer (drop-redundant + fan-out are deterministic;
  aligns with PR-4's `rehash` subcommand direction). Until then `REFGRAN01` is
  warnings-only in `build` mode (does not raise the exit code); gate-code-clean
  (plan V7) lands with the re-cascade.

### `[example-corpus]` `CORPUS-PRD-TH-RES` — PRD-01 missing `component_decomposition` → 11 unresolvable `@threshold:` citations

- *Context:* surfaced while verifying CFB-PR-2 2a-core step 4 (forward-coverage
  gate) on `examples/url-shortener/docs/`. `02_PRD/PRD-01.md` trips `TH-RES-001`
  (error): downstream docs cite `@threshold: PRD.01.perf.*` but PRD-01 declares
  no `component_decomposition` thresholds. Pre-existing — identical under main's
  linter; unrelated to coverage (CLEANUP-PR-D threshold-resolution).
- *Fix shape:* dispatch `doc-prd-fixer` to add the `component_decomposition`
  thresholds the downstream `@threshold:` tags expect, then re-cascade. Never
  hand-edit the example artifact.

### `[template]` `INDEX-UPSTREAM-RESIDUE` — stale cumulative `Upstream:` enumerations in layer index templates / READMEs

- *Context:* CFB-PR-1 (PR #180) migrated cumulative→necessary-upstream across
  ~20 surfaces, but its V6 grep keyed on the literal "cumulative" and missed the
  per-layer **`Upstream:` enumerations** in the layer index templates / READMEs.
  Concrete: `framework/layers/06_SPEC/SPEC-00_index.TEMPLATE.md:27` declares
  `Upstream: BRD, PRD, EARS, BDD, ADR` (the old full chain) where SPEC's
  `required_tags` is `[ears, bdd, adr]`; `:29` carries the full-chain line. The
  other layer index templates likely carry the same.
- *Fix shape:* sweep the `NN_*/<TYPE>-00_index.TEMPLATE.*` + layer READMEs;
  correct each `Upstream:` line to the registry `required_tags`. Same class as
  CFB-PR-1; doc-only. (CFB-PR-2 2b fixes the SPEC-00 two lines in-passing while
  it's open; this entry tracks the cross-layer sweep.)
- *Status:* OPEN — P3 (residual cumulative debt).

### `[harness]` `TRACE-RES-001-PER-LAYER-TEST-MODE` — per-layer acceptance tests duplicate the upstream chain

- *Context:* ACCEPTANCE-FIXTURES-DRIFT (2026-06-14) closed 12
  long-standing deterministic-test failures by copying upstream
  goldens (layers 1..N-1) into each `tests/acceptance/fixtures/layer_NN_<NAME>/valid/`
  dir — 28 files total. This is intentional duplication so each
  per-layer fixture dir is self-contained; the per-layer
  `assert_golden_passes_lint` runs `run_lint(golden.parent)` which
  satisfies TRACE-RES-001 only when the cited upstream host docs are
  present in the same directory.
- *Fix shape (deferred):* extend `sdd_doc_lint` with a CLI flag
  `--allow-unresolved-upstream` (or `--isolated-layer`) that
  downgrades TRACE-RES-001 to a warning when the upstream host doc is
  missing. The per-layer tests pass that flag; fullpath does not.
  Eliminates the 28-file duplication; the per-layer dirs again
  contain only the layer's own golden. Weakens the rule slightly but
  the fullpath chain still enforces it strictly.
- *Status:* Parked. Not a blocker — the duplication is small, the
  fixtures are stable, and the rule remains strict where it matters
  (fullpath integration). Pull when fixture maintenance becomes a
  real burden, OR when adding a new layer makes the duplication
  pattern obvious.

### `[sync]` `WEBSITE-VERSION-BADGE-DRIFT` — `web-site/src/pages/index.astro` `Pre-release v<X.Y.Z>` badge

- *Context:* IPLAN-0008 step 6 closed the bug class for the web-site
  home-page badge by extending `scripts/sync-version-refs.sh` to
  propagate `Pre-release v<X.Y.Z>` into the sibling
  `../web-site/src/pages/index.astro` (cross-submodule write at the
  umbrella layer). The script change ships in the framework PR;
  the actual badge value is set in the web-site PR (also part of
  IPLAN-0008, step 4-5-7). This entry exists so the cross-repo
  coupling is discoverable from the framework side.
- *Fix shape:* Same `replace_in_file "Pre-release v<old>" "Pre-release v<new>"` shape
  as the v0.20.1 plugin-README fix used. The replace_in_file helper is
  no-op if `../web-site/src/pages/index.astro` does not exist
  (framework cloned standalone without the umbrella siblings). When
  framework's plugin VERSION bumps next, the hook propagates to the
  web-site working tree; the developer commits the change in
  web-site's own PR.
- *Status:* Closed by the framework PR for IPLAN-0008 step 3+6 — the
  sync-script extension lands here; the cross-repo verification (bump
  VERSION → run sync → observe web-site badge change) is the
  Confirmation gate in IPLAN-0008.

### `[sync]` `HERMES-README-VERSION-DRIFT` — `platforms/hermes/README.md` Version + framework-spec cells stale

- *Context:* Plugin `0.20.1` PATCH (2026-06-14) found and fixed the same
  drift class in `platforms/claude-code-plugin/README.md` (`0.6.3` →
  `claude-code-plugin/v<X.Y.Z>` canonical form). `platforms/hermes/README.md`
  lines 107-108 still carry the bug: `Version | hermes/v0.1.0` (actual
  `0.3.0`) and `framework spec 0.1.0` (actual `0.21.1`).
- *Fix shape:* (a) Canonicalize the hermes README Version cell to the
  `hermes/v<X.Y.Z>` tag form — the v0.20.1 sync-script extension now
  covers this pattern, so the next Hermes VERSION bump auto-propagates.
  (b) The "Conforms to" cell uses a bare framework-spec X.Y.Z and needs
  a separate sync pattern in `scripts/sync-version-refs.sh` (the
  framework-VERSION fanout block) — add
  `replace_in_file platforms/hermes/README.md "framework spec \`$fw_prev\`" ...`.
  Out of scope for the plugin-first PATCH; pull when Hermes work resumes.

### `[skill]` `MODEL-PRECHECK-ROLLOUT` — original framing (superseded; see PARKED entry above)

- The original "wire `model.precheck` into every `doc-*` SKILL (up to 32),
  compare against the session model, gate by the acceptance suite" framing
  (introduced by PLUGIN-USER-COMMANDS, merged 2026-06-14) was **superseded**
  by the 2026-06-21 review: a skill cannot read its own session model, so the
  *compare* premise is unworkable; the redesign prints the recommendation
  instead and scopes to interactive entry points. Tracked in the **PARKED**
  entry near the top of this Open section + `plans/MODEL-PRECHECK-ROLLOUT-PLAN.md`.

### `[layer-promotion]` Promote `component_decomposition` to a first-class `02b_DECOMP` layer (Option B from DECISION-GATE-D)

- *Context:* DECISION-GATE-D (2026-06-11) resolved as Option A
  (subsection in PRD). Option B (new layer between PRD and EARS) was
  deferred because most aidoc-flow consumers will have ≤ 5-component
  systems where buried decomp in PRD is sufficient. **User direction:
  "We will have complex projects in the future — keep Option B as
  further development for when Option A is not enough."**
- *When to revisit:* signs that Option A is insufficient include:
  (a) consumer PRDs growing past ~600 lines because component
  decomp is bloating PRD §7b; (b) auditor lens unable to evaluate
  decomp quality at PRD altitude because it competes with product
  concerns; (c) `@decomp:` becoming a desired @-tag form for richer
  downstream binding; (d) C4-L2 diagrams or component-level chaos
  scenarios that don't fit cleanly in PRD §7b.
- *Fix shape (when triggered):* new layer `02b_DECOMP` between PRD
  (02) and EARS (03). `DECOMP-NN.yaml` artifact with components +
  dataflow + threshold bindings. EARS pivots its `required_tags` from
  `[prd]` → `[decomp]`. ADR + SPEC gain `decomp` in their
  necessary-upstream sets. New 6-lens crew (architect, tech_lead,
  integration_lead, chaos_engineer, security_engineer, auditor).
  4 new SKILLs (doc-decomp / -audit / -fixer / -autopilot). Estimated
  framework MINOR `0.20.x → 0.21.0`; 5-6h cascade re-run required.
- *Effort estimate:* ~12-15h (vs. PR-D's ~3h). See
  `plans/CLEANUP-PR-D-DECOMP-THRESHOLD-GATES-PLAN.md` §Option B
  comparison for the full scope analysis preserved during the
  decision gate.

### D54 consumer feedback (CC Phase-1 manual L1–L8 build) — triaged 2026-06-26

> Source: D54 "Framework Usage Feedback" (2026-06-12), a consumer-project
> log from authoring the full 8-layer chain BY HAND against spec 0.13.1,
> no plugin. Re-checked against live spec 0.23.0: F-10 (inline-Mermaid)
> and F-11 (compat matrix + `/about`) already ADDRESSED — not logged.
> F-03 (offline readiness score) and F-09 (MVP sizing) resolved-by-design
> — see notes in `[lint] D54-F01` and below. Each entry below carries the
> author's resolved fork-decision (clarified 2026-06-26).
>
> **Orchestration:** → `plans/CONSUMER-FEEDBACK-001-PLAN.md` sequences all
> 22 items (D54 + Engramory + BeeLocal) into child PRs PR-1…PR-12.

### `[template]` `D54-F02-REUSE-MANIFEST` — no first-class reuse of an existing/external artifact

- *Context:* D54 F-02 (P1, make-or-break for brownfield). Framework
  assumes greenfield authoring of all 8 layers; `active_layers` only
  *disables* BDD/ADR, can't *satisfy-by-reference*. `trace_walk.py`
  treats a referenced artifact as orphan/missing. Absent from this
  backlog + ROADMAP. The CC build improvised `*-00_index.md` reuse-maps.
- *Fix shape:* one element-granular reuse manifest — each element marked
  `authored | referenced`; whole-layer mid-chain reuse (the P1 need) is
  just "all elements referenced." Introduce `satisfied_by_reference`:
  passes coverage/traceability ("present + linked") but records "reuse,
  not re-audited" — does NOT earn an authored-layer ≥90 readiness score
  for free. Reference target MUST be in-repo / pinned (path + commit),
  deterministically verifiable; live external URLs allowed only as
  non-authoritative `@discoverability` hints, never the trace target.
- *Status:* OPEN — P1. Promote to a plan; large enough to design.

### `[lint]` `D54-F01-PROVISIONAL-IDS` — manual-mode placeholder-ID convention + hash-algo parity

- *Context:* D54 F-01 (P1). Templates still use `xxxx`; the id regex
  `[a-f0-9]{4,8}` rejects it, and `sdd_doc_lint`'s placeholder check
  `\bXX+\b` only catches *uppercase* — leftover lowercase `xxxx` passes
  silently. No doc-level provisional flag, no rehash. (F-03 "offline
  readiness score" folds here: author concedes the score stays the LLM
  `-audit` skill; the no-tooling need is met by the published hash
  algorithm plus this placeholder convention plus a trivial plugin install,
  not an offline scorer.) Engramory feedback #2 corroborates + sharpens: the SHA-256
  algorithm IS published, but only in `EARS-TEMPLATE.yaml:94-100`, NOT in
  `ID_NAMING_STANDARDS.md` (which states only "4-char hex SHA256"), and
  the standard never says hand-authored hashes are placeholders-until-
  canonical — so the parity premise isn't yet anchored where authors look.
- *Fix shape:* (a) add `metadata.id_standard.state: provisional|canonical`
  (keystone — marks "all IDs here are placeholders; canonicalize" once
  per doc, not per-ID character); (b) section-ordinal hex placeholder
  (`BRD.01.07.0001`) as a *temporary crutch* — stable-across-reorder
  content-hash is still the canonical end-state, the `provisional→canonical`
  flip guards provisional ordering from leaking; (c) ship a regex-valid
  literal (`0000`) in templates + fix the lint to flag lowercase `xxxx`;
  (d) promote the SHA-256 algorithm from template `_guidance` prose to a
  *normative* spec (pin input normalization + 4→8 collision rule) so an
  external reference-aware `rehash` produces byte-identical IDs to the
  plugin. Land `rehash` as an `sdd_doc_lint` subcommand, not a new CLI.
  Concretely: lift the `EARS-TEMPLATE.yaml:94-100` algorithm into
  `ID_NAMING_STANDARDS.md` as the normative source + add a
  "hand-authored hashes are placeholders until canonicalized" statement
  there (Engramory #2).
- *Status:* OPEN — P1.

### `[template]` `D54-F06-IPLAN-PROJECT-TYPES` — IPLAN hardcodes a Python source tree

- *Context:* D54 F-06. `IPLAN-TEMPLATE.yaml` still hardcodes
  `pytest/mypy/ruff`, `src/`, `tests/`; PR-E sub-types only split
  `code_build`/`deploy`/`combined`, not language/deliverable. Non-Python
  deliverables (plugin SKILL.md sets, managed infra) don't fit.
- *Fix shape:* **cross-reference `plans/IPLAN-LANG-001-PLAN.md`** (already
  drafted, PLANNED, not merged) — language-neutral template inheriting
  `language:`/`dependencies:` from SPEC. Revive + merge it; extend with
  non-code deliverable scaffolds (plugin/infra/docs) if SPEC-inheritance
  alone doesn't cover them. Do NOT duplicate the plan here.
- *Status:* OPEN — P2. → `IPLAN-LANG-001-PLAN.md`.

### `[lint]` `D54-F13-PHASE-SCOPE-RECONCILIATION` — no phase tag / no missing-downstream check

- *Context:* D54 F-13 (gap only — the underlying drift was a workflow
  error, not a framework defect). `trace_walk.py`/TRACE-RES-001 detect
  *orphans* (downstream→no upstream) but there is no *missing-downstream*
  check (accepted feature → no IPLAN) and no phase/scope-band tag.
- *Fix shape:* asymmetric, per author: "accepted feature has no IPLAN" =
  **warning** (legitimately mid-build; respects the completeness-check
  convention); "out-of-phase item leaked into an in-phase plan" (Phase-2
  SP in a Phase-1 IPLAN) = **blocking/high-severity** — a correctness
  defect, not incompleteness. Add a first-class phase tag on capability
  elements. The "scope ledger" is a *designated section of the existing
  BRD acceptance/index* (acceptance_criteria / launch_gates), NOT a new
  artifact — everything references it.
- *Status:* OPEN — P2.

### `[lint]` `D54-F05-BDD-COVERAGE-ROLLUP` — no aggregate EARS coverage across a split BDD set

- *Context:* D54 F-05. `ears_coverage` is per-file only; no tool
  aggregates EARS coverage across `BDD-01/02`; per-file reads "partial"
  when split, true coverage only visible by reading both. "≤12 scenarios
  → split" is an unenforced antipattern, decoupled from the 50k-token
  split trigger.
- *Fix shape:* first-class the "multiple BDD files → one EARS" relation —
  an EARS-level coverage roll-up across the BDD set (in `sdd_doc_lint` /
  `trace_walk.py`) + a documented split-by-functional-block convention so
  per-file "partial" aggregates to a true score.
- *Status:* OPEN — P2.

### `[docs]` `D54-F07-TAG-SYNTAX-REFERENCE` — per-layer tag punctuation undocumented + unenforced

- *Context:* D54 F-07. BDD template demands no-space `@brd:BRD.01`
  (Gherkin-parser-forced); EARS/ADR/SPEC use pipe+space `@brd: X | @prd: Y`
  (convention). `sdd_doc_lint`'s `\s*:\s*` accepts both everywhere, so the
  per-layer rule is never enforced.
- *Fix shape:* narrowed (author) to **document + enforce**, NOT unify
  (Gherkin makes one-format impossible): a single tag-syntax reference
  page stating the legitimately-per-layer rules, plus `taglint` (an
  `sdd_doc_lint` check) enforcing them per layer.
- *Status:* OPEN — P2.

### `[playbook]` `D54-F04-EARS-NONLATENCY-RUBRIC` — readiness rubric docks non-latency quantified bounds

- *Context:* D54 F-04. Syntax already flexes (`@threshold:` + cycle-based
  `WITHIN` + a `batch` category work), but the EARS-Ready checklist
  mandates `p50/p95/p99` and docks a quantified cycle/iteration/event-window
  bound for lacking percentiles.
- *Fix shape:* the rubric is the real work — broaden the EARS-Ready
  scoring criteria (`framework/layers/03_EARS/` + auditor playbook) to
  count a quantified non-latency bound as "quantified." No new syntax.
- *Status:* OPEN — P3.

### `[template]` `D54-F12-AGENTIC-ANTIPATTERNS` — BRD/PRD business-vs-technical boundary fuzzy for AI-agent systems

- *Context:* D54 F-12. BRD/PRD antipatterns are CRUD-flavored; no agentic
  example distinguishing "independent review stage" (business) from
  "multi-stage agent pipeline w/ timeouts" (architecture).
- *Fix shape:* add agentic/AI-system examples to the BRD/PRD
  `_antipatterns` business-vs-technical lists (resolve via C4 altitude).
  Cheap docs/template fix.
- *Status:* OPEN — P3.

### `[harness]` `D54-F08-SKELETON-EMIT` — no content-keys-only template emit

- *Context:* D54 F-08. Templates are large (`BRD-TEMPLATE.yaml` 992 lines)
  and `_guidance`-dense; the internal audit context-strip is not a
  user-facing skeleton emit.
- *Fix shape:* a `--skeleton` emit (strip `_guidance`/`_example`/
  `_antipatterns`, leave content keys) — land as plugin tooling, not a
  new CLI.
- *Status:* OPEN — P3.

### Engramory consumer feedback (SDD authoring against v0.23.0) — triaged 2026-06-26

> Source: aidoc-flow-engramory feedback log (June 2026), authoring
> Engramory's SDD artifacts against spec 0.23.0. All 🟡 (clarification /
> improvement) — none block. Item #2 (standalone hash helper) folded into
> `D54-F01-PROVISIONAL-IDS` above; item #7's forward-coverage half overlaps
> `D54-F13` — see `ENG-FWD-COVERAGE` below. Item #6's *premise is invalid*
> (Lite/Standard/Full depth variants were removed 2026-06-12; the framework
> is single-path) — only the stale-docs residue it exposed is logged.
>
> **Orchestration:** → `plans/CONSUMER-FEEDBACK-001-PLAN.md` (PR-2/5/6/7/10).

### `[lint]` `ENG-FWD-COVERAGE` — no full-chain FORWARD coverage gate; single-upstream EARS hides built requirements

- *Context:* Engramory #7 (extends BeeLocal #54). Two implemented core
  requirements traced to NO IPLAN because the serving EARS lines carried
  only one `@brd:` each. `trace_walk.py` is BACKWARD-only (downstream →
  upstream orphan resolution); nothing asserts FORWARD that every BRD FR
  reaches ≥1 SPEC and ≥1 IPLAN. `ID_NAMING_STANDARDS.md:34-36` permits
  multi-`@brd:` at *document* level but not explicitly at EARS-*line* level,
  and no lint flags a BRD FR with zero downstream coverage.
- *Fix shape:* (a) a forward coverage report/GATE-CODE pre-check
  (`sdd_coverage`): resolve the `@`-tag graph, assert every BRD FR reaches
  ≥1 SPEC + ≥1 IPLAN, emit the full BRD→…→IPLAN matrix, list broken/empty
  downstream paths. **Severity is split (author):** a BRD FR explicitly
  marked `deferred:`/future-cycle with no IPLAN = **warning** (legitimately
  mid-build); an *in-scope* FR with no IPLAN at GATE-CODE = **block** (can't
  codegen an in-scope requirement with no plan); the **SPEC leg is stricter
  than the IPLAN leg** — a BRD FR reaching NO SPEC at all = **block** (the
  false-pass design gap the gate exists to catch). (b) Permit + encourage
  multiple `@brd:` per EARS line; lint any BRD FR with zero downstream EARS
  coverage. **Syntax (author):** repeated same-layer tags, pipe-delimited —
  `@brd: X | @brd: Z | @prd: Y`; `taglint` splits on `|`, parses each token
  as `@<layer>: <ID>`, OR-groups by layer. NOT comma lists (the EARS
  traceability antipattern already forbids commas/ranges — would collide
  with `D54-F07`). Backward-compatible: single-tag lines are the degenerate
  case. (c) Bind the gate at each layer's native granularity — element-level
  for BRD→…→ADR, **document-level** for SPEC/TDD/IPLAN (`@spec: SPEC-NN`,
  `@iplan: IPLAN-NN` are document-level by design), so the gate never
  depends on SPEC/IPLAN element IDs (keeps it non-conflicting with
  `ENG-SPEC-IPLAN-ID-EXEMPTION-NOTE`). (d) **Backward leg (BeeLocal #54/#10):**
  add a `coverage` section to the `SPEC-00` index template — each L3/L4
  (EARS/BDD) element → its covering SPEC or an explicit `deferred: <reason>`
  — plus a GATE-06 backward-coverage check flagging any EARS req / BDD
  scenario with no downstream SPEC/TDD, distinguishing *deferred* from
  *missed* (BeeLocal measured EARS-01 11/16, BDD-02 6/12 uncovered at
  element level, indistinguishable today). (e) The forward gate's emitted
  BRD→…→IPLAN matrix doubles as BeeLocal #52's "recommended generated
  `TRACEABILITY.md` matrix" (#8b — the cardinality *note* is already closed
  via CLEANUP-PR-F; only the generated matrix remained open).
- *Related:* the "every accepted feature → ≥1 IPLAN = warning" half is
  shared with `D54-F13-PHASE-SCOPE-RECONCILIATION`; one forward-coverage
  engine can serve both. Build once.
- *Status:* OPEN — P2.

### `[docs]` `ENG-BRD-SKETCH-ROADMAP` — no project-init roadmap + BRD "sketch" sub-form

- *Context:* Engramory #1 (extends the "author current cycle full, stub the
  rest" practice). Authoring only `BRD-01` full + index one-liners leaves
  whole-project scope under-specified before cycle 1. `BRD-00_index` already
  has an optional "Planned BRDs" table and `@depends:` chaining exists, but
  there is no scope-only "sketch" form: `BRD-TEMPLATE.yaml:179` status is
  only `Draft|In Review|Approved`, and a scope-only future-cycle BRD would
  fail lint as an incomplete full BRD.
- *Fix shape (author scoped to docs-only now; lint deferred):* (a) document
  a project-initiation step (README + `01_BRD/README.md`): enumerate all MVP
  cycles **by extending the existing `BRD-00_index` "Planned BRDs" table**
  with cycle / PROD / `@depends:` columns (its natural home — avoids
  colliding with a consumer's top-level `ROADMAP.md` product-strategy file);
  *recommend* the BRD-layer location, do NOT mandate a path. (b) Add a
  `status: Sketch` value for scope-only future-cycle BRDs (document_control,
  introduction, business_objectives hypothesis, project_scope only). (c) A
  sketch is **trace-inert**: carries only its document-level `BRD-NN` +
  `@depends:` for sequencing — no element IDs, not in the `@`-tag graph,
  ignored by `ENG-FWD-COVERAGE`; on graduation to a full BRD it gets element
  IDs + enters the graph. (d) Add a `SKETCH-001` lint (forbid downstream
  content / element IDs on a Sketch) **only if** over-authoring drift shows
  up in practice — deferred to keep this out of MINOR territory.
- *Status:* OPEN — P3, docs-only. Collapses back toward the `BRD-00_index`
  home (the original "stub the rest" practice); not a standalone plan.

### `[template]` `ENG-PLATFORM-ADR-TIMING` — "ADRs created BEFORE PRD" wording conflicts with cumulative-tag chain

- *Context:* Engramory #5 (resolves BeeLocal #40 by clarification).
  `BRD-TEMPLATE.yaml:101` (platform-BRD guidance): "ADRs created BEFORE PRD
  to validate architectural decisions." Read literally this conflicts with
  the chain — an ADR carries `@ears`/`@bdd`, which can't exist pre-PRD.
- *Fix shape:* reword: author ADRs in sequence (after BDD) so they carry
  the full cumulative chain; "decided before PRD" refers to decision
  *provenance* (recorded in the ADR's `context`/`originating_topic`), not
  authoring *order*. **Confirmed pure wording fix — no platform-ADR-first
  workflow variant (author Q8):** Engramory authored in strict layer order,
  ADRs carried full `@ears`/`@bdd`, #40 never bit; their 5 ADRs were
  converted from prior design decisions but still authored in-sequence.
  **BeeLocal #40 adds a PRD-layer manifestation:** `PRD-TEMPLATE`
  traceability says "Do NOT reference specific ADR numbers — ADRs don't
  exist yet" and frames `adr_topic_elaboration` as "options for ADR to
  evaluate" — backwards for a platform PRD whose ADRs are already decided.
  Add a platform-flow note to the PRD template too (a platform PRD MAY cite
  existing ADRs). Same clarification, second surface.
- *Status:* OPEN — P3.

### `[template]` `ENG-SPEC-IPLAN-ID-EXEMPTION-NOTE` — element-ID exemption lives only in the standard, not the templates

- *Context:* Engramory #4. `ID_NAMING_STANDARDS.md:64-98` documents that
  SPEC §5/§3 and IPLAN §4/§2 MAY omit layer-local element IDs, but
  `SPEC-TEMPLATE.yaml` / `IPLAN-TEMPLATE.yaml` are silent — an author
  reading only the template may over-assign IDs (noise) or worry they're
  missing required ones. Follow-on to the closed item that *added* the
  exemption to the standard (CLEANUP-PR-C).
- *Fix shape:* add a one-line `_note` in SPEC §5/§3 and IPLAN §4/§2
  template guidance cross-referencing the exemption; **keep the exemption**
  (author Q7 — do NOT require element IDs everywhere; that would reintroduce
  the second-naming-surface the standard created the exemption to avoid).
  Non-conflicting with `ENG-FWD-COVERAGE`: that gate binds SPEC/TDD/IPLAN at
  *document* level, so it never relied on their element IDs. Keep the
  standard authoritative; the template just cross-references it.
- *Status:* OPEN — P3.

### `[docs]` `ENG-IPLAN-REGISTRY-README` — registry-vs-document schema distinction undocumented in the layer README

- *Context:* Engramory #3. `IPLAN-00_index` is `document_type:
  iplan-registry` (no `document_control`); `IPLAN-NN_*` are
  `iplan-document`. A naive "validate every `08_IPLAN/IPLAN-*.yaml`" glob
  trips on the registry. `sdd_doc_lint` ALREADY special-cases INDEX docs
  (`__init__.py:927-969`, `:836-850`) — so only the *author-facing note* is
  missing.
- *Fix shape:* one-line note in `08_IPLAN/README.md` that registry vs
  document are distinct schemas + how each is validated (lint exempts
  `artifact_type: *-INDEX`). Docs-only.
- *Status:* OPEN — P3.

### `[hermes-parity]` `ENG-STALE-DEPTH-DOCS` — dead Lite/Standard/Full tables still in Hermes orchestrator docs

- *Context:* Engramory #6 — its *requested clarification is moot* (depth
  variants are dead since 2026-06-12, framework is single-path; author
  confirmed via clone-grep that no Engramory component was authored "Lite" —
  all six carry SPEC→TDD→IPLAN, nothing under-built). Withdraw #6's
  orthogonality ask; THIS entry is the replacement. Stale surfaces that fed
  the misconception: (1) the **public GitHub README** still advertises
  SDD-Lite/Standard/Full — the v0.20-era copy the author originally read
  (this repo's own `README.md:47-48` is already clean, single-flow); (2) two
  Hermes docs still publish the dead tables —
  `platforms/hermes/.../sdd-orchestrator/root-docs/README.md:100-106`
  ("SDD Depth Variants") and `.../governance/CHG_GOVERNANCE_BRIDGE.md:20`
  ("Lite/Standard may use subset gates").
- *Fix shape:* reconcile all stale surfaces to the single-path model (all 8
  layers required per necessary-upstream; CHG is an orthogonal governance
  overlay; only the MVP→PROD→new-MVP loop). (a) Verify/refresh the published
  GitHub README at the released tag (F-11-adjacent — guard against the stale
  public render); (b) refresh the two Hermes docs — cross-reference
  `HERMES-BACKLOG.md` H-11 (the broader sdd-orchestrator v3.2-worldview
  refresh already parked there); this entry is the concrete file:line
  evidence for it. Do not double-track.
- *Status:* OPEN — P2 (small + concrete; README leg + Hermes-side).

### BeeLocal consumer feedback (SDD authoring against v0.23.0) — triaged 2026-06-26

> Source: aidoc-flow BeeLocal feedback log (June 2026), authoring BeeLocal's
> SDD artifacts. The OLDEST of the three consumer logs + the origin of items
> the others extend. Re-checked against v0.23.0:
> **Dropped — OBSOLETE** (pre-migration `ucx_flow_v3/`/`mcp_ucx/`/`ucx_hermes/`
> structure removed at v1.0.0 cutover, preserved only on
> `legacy-ucx-v3.2-read-only`): #3/#37 (duplicate `ucx_flow_v3/`), #4/#38
> (stale template paths — current README correctly points at `framework/layers/`).
> **Dropped — ADDRESSED**: #5/#39 (layer-count drift — single 8-layer model
> is now the only story; no SYS/REQ/CTR/TSPEC/TASKS as current); #8a/#52-pt1
> (per-layer numbering independence + fan-out — closed by CLEANUP-PR-F in
> `ID_NAMING_STANDARDS.md:18-51`).
> **Folded**: #6/#40 → `ENG-PLATFORM-ADR-TIMING` (PRD-layer note added);
> #8b/#52-pt2 (generated matrix) + #10/#54 (backward coverage) →
> `ENG-FWD-COVERAGE` (d)/(e). Remaining open items below.
>
> **Orchestration:** → `plans/CONSUMER-FEEDBACK-001-PLAN.md` realizes the
> sequencing below as child PRs PR-1…PR-12.
>
> **Suggested PR sequencing (author Q5 — small themed PRs, NOT one sweep;
> each ≤3 doc surfaces per governance Rule 1):**
>
> 1. **Trace correctness (first — load-bearing):** `BL-TAG-CHAIN-GATE-SYNC`
>    (`GATE-08-E003` + `TRACEABILITY.md` diagram). Goes first because it
>    changes how everyone reads the chain.
> 2. **Lint hardening:** `BL-REF-GRANULARITY` + `BL-STATUS-SCOPE` — both land
>    in `ID_NAMING_STANDARDS.md` + the taglint; cohesive.
> 3. **BRD lifecycle + authoring pattern:** `BL-BRD-SET-WORDING` +
>    `ENG-BRD-SKETCH-ROADMAP` ("current set full, rest stubbed") —
>    BRD-TEMPLATE + README + BRD-00 index.
> 4. **Template ambiguities + advisory score:** pair `BL-SIZE-UNITS` +
>    `BL-VENDOR-NAME-SCOPE`, with `BL-READY-SCORE-ADVISORY` separate if the
>    pair already hits 3 surfaces.

### `[governance]` `BL-TAG-CHAIN-GATE-SYNC` — stale cumulative-tag docs contradict the necessary-upstream contract

- *Context:* BeeLocal #53. The author flagged that SPEC/TDD carry only
  `@adr,@bdd,@ears` and IPLAN only `@spec,@tdd`, "contradicting GATE-08-E003."
  **The templates are CORRECT** — NECESSARY-UPSTREAM-001 (PR #121) deliberately
  replaced the old cumulative chain (immediate-upstream only; the cumulative
  form caused trace-fabrication). The real defect is the OPPOSITE of the
  author's proposed fix: `GATE-08_IPLAN.md:222-231` (E003 *resolution*
  example) and `TRACEABILITY.md:9-24` (cumulative-tags diagram) are STALE —
  they still show the old full chain, contradicting `LAYER_REGISTRY.yaml`
  `required_tags` + the live templates.
- *Fix shape:* do NOT re-add cumulative tags to SPEC/TDD/IPLAN templates.
  Instead correct the two stale docs to the necessary-upstream contract:
  fix the `GATE-08-E003` resolution example to `[spec, tdd]` and resync the
  `TRACEABILITY.md` chain diagram to immediate-upstream. The corrected
  diagram MUST state the transitive path **explicitly** (PRD/BRD reachable
  by walking ADR/BDD/EARS→PRD→BRD, not via L6+ local tags), and point the
  reverse lookup ("which BRD is SPEC-07?") at the generated `TRACEABILITY.md`
  matrix (`ENG-FWD-COVERAGE` (e)) so nobody re-files it as a gap.
- *Confirmed (author Q1):* BeeLocal's chain verified clean with exactly this
  contract — SPEC `@adr/@bdd/@ears`, TDD `@spec/@bdd/@ears`, IPLAN `@spec/@tdd`
  only, zero dangling refs. GATE-08-E003 requiring `@brd+@prd` is the bug,
  not the templates. Do NOT re-add cumulative tags.
- *Status:* **CLOSED** — 2026-06-27, squash `8e001192` (PR #180), as
  **CFB-PR-1** (CONSUMER-FEEDBACK-001). Expanded during implementation from the
  2 named docs to the **full ~20-surface cumulative→necessary-upstream
  reconciliation** (the V6 grep + independent review surfaced the stale model
  across EARS/BDD templates, GATE-03 + error catalog with FALSE `required_tags`
  claims, 3 layer READMEs, BDD-00 index, DEFINITION_OF_DONE, the ADR + IPLAN
  auditor playbooks, the guides, and the `AI_ASSISTANT_RULES` live author-facing
  bug). Framework spec 0.23.0 → 0.23.1; plugin VERSION unchanged. See
  `plans/CFB-PR-1-TAG-CHAIN-GATE-SYNC-PLAN.md` Pass-4 log.

### `[lint]` `BL-REF-GRANULARITY` — doc-level vs element-level refs interchangeable, silently defeats coverage

- *Context:* BeeLocal #55. Templates allow both `@bdd: BDD-NN` (whole doc)
  and `@bdd: BDD.NN.03.xxxx` (element). A doc-level ref in a *verification*
  context silently defeats element-level coverage computation (BeeLocal
  SPEC-09/TDD-09 cited `BDD-01` though the exact scenario `BDD.01.03.3aa0`
  exists). Nothing in `ID_NAMING_STANDARDS.md`/`TRACEABILITY.md` states a
  granularity rule; lint doesn't enforce it.
- *Fix shape (author Q2):* state the rule via the derivable principle —
  **citing an oracle layer (EARS requirement or BDD scenario) ⇒ element-level
  required; citing an upstream design doc as a unit (ADR/SPEC/TDD) ⇒ doc-level
  permitted** — in `ID_NAMING_STANDARDS.md`, + a `sdd_doc_lint` check that
  **blocks at GATE-06** (a doc-level ref in a verification context silently
  zeroes coverage — a correctness defect, not mid-build incompleteness, so it
  blocks; distinct from the missing-IPLAN=warning case). Element-level fields
  (verification): SPEC `upstream.bdd_references`/`ears_references` + inline
  `source: "@bdd/@ears: …"` in invariants/state_machine/error_handling; TDD
  `scenarios[].bdd_scenario`/`test_cases[].bdd_ref`/`upstream.bdd_references`/
  `ears_references`. Doc-level OK: SPEC `architecture_decision`/
  `upstream.adr_references`; TDD `test_cases[].spec_ref`/`upstream.spec_references`;
  IPLAN `source_spec`/`upstream.spec_references`/`tdd_references` (the principle
  auto-excludes IPLAN→SPEC/TDD). **Derive the exact field list from the live
  SPEC/TDD templates** so it stays in sync. Interacts with `ENG-FWD-COVERAGE`
  (granularity makes element-level coverage computable) + `D54-F07` (same
  taglint surface).
- *Status:* OPEN — P2.

### `[template]` `BL-READY-SCORE-ADVISORY` — `*_ready_score` placeholders read as a required gate

- *Context:* BeeLocal #56 (52 occurrences). Every ADR/SPEC/TDD ships
  `*_ready_score: [Score]/100` + `target_score: ">=90/100"`, which reads as
  a required gate, but the score is **advisory** — the deterministic lint
  floor is the real gate and the score is computed by the auditor lens, not
  hand-authored. A blank field makes a finished set look half-done.
- *Fix shape (author Q4 — mark-advisory, do NOT build a rubric):* mark the
  field explicitly advisory in every template (`_note: "Computed by the
  auditor lens; authoring this is advisory — a blank value is NOT
  incomplete"`) and reword `target_score` so it reads as a readability
  threshold, not a gate. **No offline rubric/tool** — that would contradict
  `D54-F03` (the audit skill IS the rubric; the deterministic floor is
  `sdd_doc_lint`).
- *Status:* OPEN — P3.

### `[template]` `BL-STATUS-SCOPE` — `status:` key overloaded across 3 scopes, unlintable

- *Context:* BeeLocal #57. `status:` carries 3 different legal-value sets:
  document (`Draft|In Review|Approved`), ADR lifecycle
  (`Proposed|Accepted|Deprecated|Superseded`), option (`Selected|Pending`)
  — plus IPLAN (`Draft|In Progress|Completed`). A linter can't validate
  `status` without knowing its scope; a wrong-scope value passes silently.
- *Fix shape (author Q3 — enum, NOT rename):* define per-context `status`
  enums in `ID_NAMING_STANDARDS.md` + teach `sdd_doc_lint` the scope→enum
  map (validate `status` by its scope). Do **not** rename to
  `document_status`/`option_status` — that's a breaking change across every
  artifact + the example corpus for no behavioral gain; a scope-aware linter
  solves the actual problem. Fold a rename in only at a future major break.
- *Status:* OPEN — P3.

### `[docs]` `BL-BRD-SET-WORDING` — "each BRD = one cycle" misreads as one-BRD-per-cycle

- *Context:* BeeLocal #34. `01_BRD/README.md:6,34` says "Each BRD represents
  ONE iteration cycle." Platform/feature BRD typing
  (`BRD-TEMPLATE.yaml:95-109`) + `@depends:` already support a BRD *set* per
  cycle (one platform BRD + child feature BRDs), but the wording hides it —
  caused real BeeLocal planning confusion.
- *Fix shape:* reword to "each BRD *set* (platform + its feature BRDs) = one
  iteration cycle" + add a parent/child tree example. Docs-only; ties to
  `ENG-BRD-SKETCH-ROADMAP` (same BRD-00/cycle area).
- *Status:* OPEN — P3.

### `[docs]` `BL-SIZE-UNITS` — section `_size_target` in words vs document cap in tokens

- *Context:* BeeLocal #41a. Section `_size_target` values are WORDS
  (`BRD-TEMPLATE.yaml:171` `100 # words`, …) and `AUTHORING_STYLE.md:62-69`
  targets are words, but the document split cap is 50,000 TOKENS
  (`BRD-TEMPLATE.yaml:117-118`). Mixed units, no stated relationship.
- *Fix shape:* one clarifying note (in `AUTHORING_STYLE.md` or the template
  size guidance) stating the two units' relationship — section targets are
  authoring guidance in words; the 50k-token cap is the split trigger.
- *Status:* OPEN — P3.

### `[template]` `BL-VENDOR-NAME-SCOPE` — "no vendor names" rule collides with `recommended_selection`

- *Context:* BeeLocal #41b. `adr_topics` guidance
  (`BRD-TEMPLATE.yaml:615-617`) says "use business capability descriptions,
  not vendor names (FAIL: MUST use PostgreSQL)" — yet `recommended_selection`
  is exactly where the chosen vendor goes. The rule's scope is unstated.
- *Fix shape:* clarify the rule applies to titles/`business_driver` (stay
  business-level) but vendor names ARE allowed in `recommended_selection`
  (the decision record). One-line template note.
- *Status:* OPEN — P3.

## Closed

### `[skill]` `MODEL-PRECHECK-ROLLOUT` — autopilots print the per-layer model recommendation (2026-06-23)

- *Context:* `commands/model.md` documented a `model.precheck` mode the
  `doc-*` skills "consult," but no skill did — a documented-but-unimplemented
  behavior introduced by PLUGIN-USER-COMMANDS.
- *Resolution:* MODEL-PRECHECK-ROLLOUT (PR #164, merge `6700301f`). The 8 layer
  autopilots gained a `## Model precheck` section (before `## Workflow`) that
  reads `model.per_layer`/`model.default`/`model.precheck` from
  `.claude/aidoc-flow.config.yaml` and **prints** the recommendation + the
  `/model <rec>` command (no compare — a skill can't read its own session
  model). `warn`/`silent`/`block` modes; Step-1 saga directive reworded to
  "first orchestration action" so the notice runs before the driver. New
  `tests/conformance/platforms/test_model_precheck.py`; `commands/model.md` +
  `docs/CONFIG.md` mode descriptions corrected to print-not-compare. Plugin
  `0.21.0 → 0.22.0`; no framework-spec change. Scope locked autopilots-only
  (D-0035); base/audit/fixer deferred (headless under the driver). Converged
  Pass 1-7 + independent diff review (caught the stale `commands/model.md`
  wording). See `plans/MODEL-PRECHECK-ROLLOUT-PLAN.md`.

### `[skill]` `SAGA-PARITY-001-PHASE-4` — 6 layer autopilots now saga-driven (2026-06-22)

- *Context:* Only `doc-brd/prd/chg-autopilot` invoked `tools/saga_driver.py`;
  the 6 layer autopilots `doc-{ears,bdd,adr,spec,tdd,iplan}-autopilot` still
  described a legacy in-session `## Workflow`. The acceptance harness shells
  the driver directly per layer (`test-acceptance.sh:1139`), masking the
  divergence — a user-invoked `/aidoc-flow:doc-bdd-autopilot` ran an untested
  path. Surfaced 2026-06-21 while reviewing MODEL-PRECHECK-ROLLOUT.
- *Resolution:* SAGA-PARITY-001 Phase 4 (PR #161, merge `f277ea1a`). Each of
  the 6 `## Workflow` sections rewritten to the proven `doc-prd-autopilot`
  two-subsection shape (`### Saga-driven generation loop (team)` invoking
  `saga_driver.py --layer <NN_TYPE>` + `### Linear Pipeline (single_pass)`
  verbatim); `review_mode` added to the 6 SKILLs' `adapts:` + reconciled into
  `doc-prd-autopilot`; new `tests/conformance/platforms/test_autopilot_saga_parity.py`
  (8×3 subtests + a dangling-cross-ref guard). Plugin `0.20.1 → 0.21.0`; no
  framework-spec change. Plan converged Pass 1-3 (independent Pass 2);
  independent diff review caught + fixed a Step-3 dangling cross-reference.
  See `plans/SAGA-PARITY-001-PHASE-4-PLAN.md`.

### `[example-corpus]` url-shortener corpus regen → all 6 layers PASS (2026-06-10)

- *Resolution:* TRACE-RES-FIXUP-001 (PR #125, merge `90f37002`) + IPLAN-RT-001
  (PR #127, merge `c56c386f`). Cascade scores: PRD 92 / EARS 94 / BDD 91 /
  ADR 96 / SPEC 97 / TDD 90 / IPLAN 100. Post-cascade review (2026-06-11)
  surfaced 9 NEW framework-improvement items, captured above as Open
  entries for FRAMEWORK-CLEANUP-001 triage.

### `[harness]` Cascade harness lacks `--skip-lint-smoke` flag for migration scenarios

- *Context:* TRACE-RES-FIXUP-001 cascade (2026-06-10) needed
  `SDD_LINT_SKIP_TRACE_RES=1` env-var bypass to run against the legacy
  url-shortener corpus before the new contract was applied.
- *Fix shape:* add `--skip-lint-smoke` flag to `tests/scripts/test-acceptance.sh`
  Phase 0 so migration runs can defer lint until after the corpus is
  regenerated. Removes the need for per-rule env-var bypasses.
  *Resolution:* CLEANUP-PR-A (PR #TBD, merge SHA TBD) — first child PR of FRAMEWORK-CLEANUP-001. See `plans/CLEANUP-PR-A-HARNESS-LINT-PLAN.md` for impl details.

### `[harness]` Tree-safety check requires `--force` after pre-cleanup; plan templates don't surface this

- *Context:* TRACE-RES-FIXUP-001 first cascade attempt (2026-06-10) aborted
  in 30s at Phase 0 "tree-safety FAIL" because `rm -rf` of legacy artifacts
  created unstaged deletions. Five-pass plan review missed this. Re-run
  with `--force` succeeded.
- *Fix shape:* either (a) document the cleanup-then-`--force` pattern in
  the cascade-rebuild section of plans that touch `examples/<NAME>/`,
  or (b) auto-stage the cleanup in the harness so the safety check sees
  a clean tree.
  *Resolution:* CLEANUP-PR-A (PR #TBD, merge SHA TBD) — first child PR of FRAMEWORK-CLEANUP-001. See `plans/CLEANUP-PR-A-HARNESS-LINT-PLAN.md` for impl details.

### `[lint]` `sync-vendored.sh` and `sync-plugin-framework.sh` are two separate sync mechanisms; easy to confuse

- *Context:* TRACE-RES-FIXUP-001 Task 2 (2026-06-10) and earlier
  NECESSARY-UPSTREAM-001 (PR #121): I edited the vendored lint module,
  ran `sync-plugin-framework.sh`, and the edit was overwritten because
  that script syncs `tools/sdd_doc_lint/` → vendored copies (treating
  `tools/` as canonical), not the reverse. The lint module's canonical
  source is `tools/sdd_doc_lint/__init__.py`; the vendored copies under
  `platforms/<name>/sdd_doc_lint/` are byte-identical mirrors.
- *Fix shape:* either (a) consolidate to one sync script that knows the
  direction per directory, or (b) add a top-of-file comment to each
  vendored module declaring "DO NOT EDIT — synced from tools/...". A
  brief CONTRIBUTING.md note next to the existing sync-script docs
  would also help.
  *Resolution:* CLEANUP-PR-A (PR #TBD, merge SHA TBD) — first child PR of FRAMEWORK-CLEANUP-001. See `plans/CLEANUP-PR-A-HARNESS-LINT-PLAN.md` for impl details.

### `[skill]` Auditor + fixer SKILLs emit unescaped `|` inside backtick code spans in table cells (MD056)

- *Context:* IPLAN-RT-001 live cascade (2026-06-10) produced
  `examples/url-shortener/.aidoc/audit/08_IPLAN-audit.md:105` and
  `.aidoc/review/08_IPLAN/IPLAN-01/IPLAN-01.F_fix_report_v001.md:50`
  containing rows where a `docker compose ps | grep 'Up'` code span
  inside a table cell has its shell pipe treated by markdownlint as a
  column separator, tripping MD056 (column-count mismatch). Pre-commit
  hook blocked impl commits on cascade output.
- *Fix shape:* update audit + fixer SKILL prompts to escape `|` inside
  code spans within markdown table cells (use `\|` or move the code
  span to a paragraph reference). Until then, `examples/<name>/.aidoc/`
  is excluded from the pre-commit markdownlint hook (workflow-gap fix
  landed in IPLAN-RT-001 commit).
  *Resolution:* CLEANUP-PR-A (PR #TBD, merge SHA TBD) — first child PR of FRAMEWORK-CLEANUP-001. See `plans/CLEANUP-PR-A-HARNESS-LINT-PLAN.md` for impl details.

### `[governance]` Iteration cap for the quality loop is implementation-bound, not spec-bound

- *Context:* `REVIEW_REMEDIATION_FLOW.md` defines the quality loop as
  "Draft → Review → (Remediate → Re-review)* → Gate Pass" and states
  *"the loop repeats until the gate passes"* — open-ended. But the cap
  is hard-coded at `tools/saga_driver.py:125` `MAX_ITERATIONS = 3` (and
  default threshold 90). No `ADAPTATION_SURFACE.yaml` knob exposes this;
  the spec gives no guidance on default cap or how to tune it per layer
  / project.
- *Fix shape:* either (a) elevate the iteration cap to spec — declare a
  default in `REVIEW_REMEDIATION_FLOW.md` or `REVIEW_SAGA.md` and expose
  it via `ADAPTATION_SURFACE.yaml` (e.g. `quality_loop.max_iterations:
  3`, tunable per project) — or (b) leave it as a platform implementation
  detail but explicitly document that in the spec so consumers know to
  consult their platform's docs for the cap. Either way, the framework
  shouldn't have a silent implementation-bound cap that the spec is
  unaware of. Discovered while observing the TRACE-RES-FIXUP-001 corpus
  regen cascade (2026-06-10): PRD-01 converged in iter-2 (PASS 92),
  EARS-01 in iter-2 (PASS 94); both ran the loop until gate passed,
  consistent with spec — but the silent 3-iter ceiling means
  near-convergent artifacts (89/90) end up `PARTIAL_TIMEOUT` instead of
  one-more-cycle.
  *Resolution:* CLEANUP-PR-C (PR #TBD, merge SHA TBD) — second child PR of FRAMEWORK-CLEANUP-001. See `plans/CLEANUP-PR-C-SPEC-REGISTRY-PLAN.md` for impl details.

### `[registry]` `@threshold:` 3-segment keys vs element-ID 4-segment pattern

- *Context:* `LAYER_REGISTRY.yaml` `id_patterns.element` regex covers
  the 4-segment hash form `TYPE.NN.SS.xxxx`. But threshold keys use a
  3-segment form `PRD.01.perf.redirectp95`. The current `sdd_doc_lint`
  cannot distinguish a legitimate threshold from a malformed 3-segment
  element ID — a hand-edit introducing `PRD.01.perf.typo` would slip
  past validation.
- *Fix shape:* add a `threshold` ID pattern to `LAYER_REGISTRY.yaml`
  `id_patterns:`; extend `sdd_doc_lint` to validate the new namespace.
  Coordinate with the `[gate] Threshold-binding gate` entry above.
  *Resolution:* CLEANUP-PR-C (PR #TBD, merge SHA TBD) — second child PR of FRAMEWORK-CLEANUP-001. See `plans/CLEANUP-PR-C-SPEC-REGISTRY-PLAN.md` for impl details.

### `[template]` SPEC + IPLAN declare no layer-local element IDs

- *Context:* url-shortener review (2026-06-11) — `SPEC-01.md` and
  `IPLAN-01.md` carry no `SPEC.NN.SS.xxxx` or `IPLAN.NN.SS.xxxx`
  element IDs (only upstream `@adr`/`@tdd` refs + Protocol method
  names). Templates `SPEC-TEMPLATE.yaml` / `IPLAN-TEMPLATE.yaml` do
  not require any. If a downstream consumer ever needs to cite an
  individual SPEC rule (e.g. "the §5 fail-closed rule") or an
  individual IPLAN step, they have no element ID to bind to.
- *Fix shape:* either (a) require element IDs at SPEC §5 rules and
  IPLAN §4 contracts via template + auditor lens, or (b) document the
  deliberate exemption in `ID_NAMING_STANDARDS.md` so future authors
  know it's intentional.
  *Resolution:* CLEANUP-PR-C (PR #TBD, merge SHA TBD) — second child PR of FRAMEWORK-CLEANUP-001. See `plans/CLEANUP-PR-C-SPEC-REGISTRY-PLAN.md` for impl details.

### `[template]` EARS emits per-line `@bdd:` downstream slots — direction-of-flow violation

- *Context:* url-shortener review (2026-06-11) — `EARS-01.md:68, 73, 81 etc.`
  emit per-line `@bdd: BDD-01` slots BEFORE the downstream BDD exists.
  These work as downstream slots but bypass the necessary-upstream
  contract direction (upstream-only).
- *Fix shape:* either (a) drop per-line `@bdd:` slots from EARS and
  rely on BDD's reverse `@ears:` tags for the trace (cleaner direction),
  or (b) declare downstream-slot semantics officially in
  `LAYER_REGISTRY.yaml` so the contract names them.
  *Resolution:* CLEANUP-PR-C (PR #TBD, merge SHA TBD) — second child PR of FRAMEWORK-CLEANUP-001. See `plans/CLEANUP-PR-C-SPEC-REGISTRY-PLAN.md` for impl details.

### `[plan-review]` Plan reviews should cross-check claims against the example corpus, not only test fixtures

- *Context:* NECESSARY-UPSTREAM-001 (PR #121) Pass 4 verified
  TRACE-RES-001 against `tools/sdd_doc_lint/fixtures/` but **not**
  against `examples/url-shortener/docs/`. The latter carried 107 orphan
  `@prd:` tags that broke the TDD-RT-001 cascade. The plan's
  "backwards compatibility" claim was wrong because the corpus
  cross-check was missing.
- *Fix shape:* update the plan-review templates / verified-planning
  skill to require, when a plan changes lint rules or @-tag semantics,
  a `python3 -m sdd_doc_lint examples/<NAME>/docs/` smoke run as a
  mandatory Pass-N check. Catches corpus drift before merge.
  *Resolution:* CLEANUP-PR-B (PR #TBD, merge SHA TBD) — third child PR of FRAMEWORK-CLEANUP-001 (heart). See `plans/CLEANUP-PR-B-REVIEW-CALIBRATION-PLAN.md` for impl details.

### `[skill]` doc-tdd auditor C4 inter-section consistency may be over-strict (or the cascade-produced TDD-01 has a real inconsistency)

- *Context:* TDD-RT-001 live cascade (2026-06-09) finished with
  `content_score 89`; one P2 finding cited "§1 line 30 (cumulative
  upstream tags header) vs §3 lines 89-90 and §7 line 206". The §1 line
  was correctly `@ears | @bdd | @adr | @spec` per the new contract;
  inconsistency was elsewhere. Not investigated.
- *Fix shape:* run a focused diagnostic on the TDD-01.md generated by
  PR #122 + decide whether C4 is the right gate or whether the TDD
  author needs to be tighter about section-level tag consistency. May
  result in a small `doc-tdd/SKILL.md` tightening.
  *Resolution:* CLEANUP-PR-B (PR #TBD, merge SHA TBD) — third child PR of FRAMEWORK-CLEANUP-001 (heart). See `plans/CLEANUP-PR-B-REVIEW-CALIBRATION-PLAN.md` for impl details.

### `[plan-review]` 5-pass plan reviews are paying off; consider codifying minimum-pass count by plan-type

- *Context:* TRACE-RES-FIXUP-001 plan took 5 passes to converge
  (Pass 4 caught a silent-no-op `rm -rf .aidoc/saga/` that would have
  wasted a 6-9 hour cascade). NECESSARY-UPSTREAM-001 took 4 passes;
  TDD-RT-001 took 2; the 8-skill rollout plans typically took 2-3.
- *Fix shape:* not urgent, but worth noting in the verified-planning
  skill: framework-level / cross-cutting plans seem to need 4-5 cycles
  in practice; per-layer rollout plans converge in 2. CLAUDE.md's
  "minimum 2" floor is correct; an advisory upper-bound by plan-type
  would help future estimation.
  *Resolution:* CLEANUP-PR-B (PR #TBD, merge SHA TBD) — third child PR of FRAMEWORK-CLEANUP-001 (heart). See `plans/CLEANUP-PR-B-REVIEW-CALIBRATION-PLAN.md` for impl details.

### `[playbook]` `auditor` + `tech_lead` lens calibration — convergence theater

- *Context:* url-shortener cascade audit trail (2026-06-11) — `auditor`
  lens scored **100 on 4 of 5 cascaded layers** where it ran; `tech_lead`
  scored **100 on 3 of 4** even when `chaos`+`security_engineer` found
  multiple P2/P3 issues in the same sections. The synthesizer's weighted
  mean still surfaces real findings (verdicts 91-97 honest), but 2 of 6
  lenses are giving blank checks. IPLAN-01 scored 100 with 5/6 lenses
  returning zero findings — the strongest convergence-theater signal.
- *Fix shape:* refresh `framework/playbooks/<layer>/auditor.md` and
  `tech_lead.md` for each layer with more falsifiable checks. Specifically
  require tech_lead to cross-check the sections security/chaos flagged.
  Add a "no-lens-scores-100-without-falsifiable-evidence" guard to the
  synthesizer.
  *Resolution:* CLEANUP-PR-B (PR #TBD, merge SHA TBD) — third child PR of FRAMEWORK-CLEANUP-001 (heart). See `plans/CLEANUP-PR-B-REVIEW-CALIBRATION-PLAN.md` for impl details.

### `[skill]` `doc-*-audit` must strip author's self-claimed scores before lens fan-out

- *Context:* url-shortener cascade audit trail (2026-06-11) —
  `02_PRD/PRD-01/verdict.json:AUD-002` flagged that the author's
  `ears_ready_score: 92` self-claim survived into the artifact body
  the lenses see. The synthesizer's final score was **also 92**.
  Coincidence, or anchor-effect from lenses reading the author's claim?
  Either way, the framework should not let author self-assessment leak
  into the review surface.
- *Fix shape:* `doc-*-audit/SKILL.md` step that prepares the lens brief
  must strip fields like `ears_ready_score`, `prd_score`, etc. from the
  artifact text before passing to each lens subagent. Document the
  stripped-field list in `REVIEW_TEAM.md` §Operations.
  *Resolution:* CLEANUP-PR-B (PR #TBD, merge SHA TBD) — third child PR of FRAMEWORK-CLEANUP-001 (heart). See `plans/CLEANUP-PR-B-REVIEW-CALIBRATION-PLAN.md` for impl details.

### `[saga]` Saga lifecycle — no `fixer_introduced_finding` tag

- *Context:* `examples/url-shortener/.aidoc/review/04_BDD/BDD-01/saga.json`
  shows iter-2 fixer rewrote scenario `.9b90`; iter-3 audit found the
  rewrite introduced **two new P2s** at the same location (compound
  `When` + unbounded timeout). The framework has no way to flag findings
  that the fixer itself caused — they appear as "new findings" with no
  link to the change set.
- *Fix shape:* extend `REVIEW_SAGA.md` schema with a
  `fixer_introduced_finding` tag on iter-N findings whose location
  matches a iter-(N-1) "Fixes Applied" table row. Surface in the audit
  report under `## Regressions` (new section in audit report format).
  *Resolution:* CLEANUP-PR-B (PR #TBD, merge SHA TBD) — third child PR of FRAMEWORK-CLEANUP-001 (heart). See `plans/CLEANUP-PR-B-REVIEW-CALIBRATION-PLAN.md` for impl details.

### `[template]` IPLAN sub-types: code-build vs deploy

- *Context:* url-shortener review (2026-06-11) — IPLAN-01 covers Red/Green/
  Refactor with pytest gates but has **no canary, no smoke endpoint, no
  observability dashboard, no rollback procedure** (§5 explicitly defers
  runbook/dashboard to "first to-production session"). It scored 100, but
  it's a code-build plan, not a deploy plan. The crew (operator + chaos
  - integration_lead lenses) is calibrated for deploy concerns; if the
  artifact silently scopes out those concerns, the crew can't catch it.
- *Fix shape:* `IPLAN-TEMPLATE.yaml` gains a `subtype` field with values
  `code_build` | `deploy` | `combined`. Deploy IPLANs are gated on
  rollback/smoke/observability sections; code-build IPLANs are exempt.
  Audit dispatch selects the section set by subtype.
  *Resolution:* CLEANUP-PR-E (PR #TBD, merge SHA TBD) — fourth child PR. See `plans/CLEANUP-PR-E-IPLAN-SUBTYPES-PLAN.md`.

### `[gate]` Component-decomposition gate missing between PRD and ADR

- *Context:* url-shortener review (2026-06-11) — BRD/PRD scoped the **whole
  service** (shorten + redirect + counter + abuse screening); ADR-01 onward
  silently narrowed to **one component** (Mapping Store). ADR §10 mentions
  "five sibling ADRs as future work" but no scope-contraction artifact
  records the decision. Downstream layers (SPEC/TDD/IPLAN) implement only
  the Mapping Store, not the URL shortener.
- *Fix shape:* introduce a `which-containers-from-PRD-§9-get-ADRs-this-cycle`
  artifact (a CHG-like decision record) at the PRD↔ADR boundary. ADR
  authoring SKILL must reference it; auditor must verify scope matches.
  Without it, downstream layers silently shrink scope unobserved.
  *Resolution:* CLEANUP-PR-D (PR #TBD, merge SHA TBD) — fifth and final child PR. Option A chosen; Option B deferred to item #19.

### `[gate]` Threshold-binding gate missing before BDD/TDD PASS

- *Context:* url-shortener review (2026-06-11) — 7 of 11 threshold keys
  in PRD-01 are placeholders (`screeningdeadline`, `countstaleness`,
  `codespacecapacity`, `takedownsla`, `codeentropy`, `resolutionpersource`,
  `resolutionwindow`) with no numeric values bound. BDD scenarios cite
  `WITHIN @threshold:PRD.01.perf.screeningdeadline` and TDD test cases
  cite them too — neither is testable, both passed audit.
- *Fix shape:* extend `sdd_doc_lint` with a `THRESHOLD-RES-001` rule
  (mirror of TRACE-RES-001 for threshold keys): every `@threshold:KEY`
  citation must resolve to a numeric-bound value in the host doc.
  Unbound thresholds fire P1 at BDD/TDD audit.
  *Resolution:* CLEANUP-PR-D (PR #TBD, merge SHA TBD) — fifth and final child PR. Option A chosen; Option B deferred to item #19.

### `[governance]` Doc-number independence across layers not codified anywhere

- *Context:* User clarification (2026-06-11) — document numbers (the
  `NN` in `BRD-01` / `PRD-01` / `EARS-01` / ...) are **per-layer
  sequential and independent**; one BRD MAY drive multiple downstream
  PRDs (PRD-01, PRD-02, ...), one PRD MAY cite multiple BRD upstream
  docs. Framework currently has zero explicit mention of this:
  `ID_NAMING_STANDARDS.md` says *"sequential two-digit number"* (per
  layer, but doesn't say independent across); `TRACEABILITY.md` has
  no cross-layer cardinality discussion; `REVIEW_TEAM.md` +
  `REVIEW_REMEDIATION_FLOW.md` are silent on cardinality. The
  url-shortener example's 1:1 numbering alignment (BRD-01 → PRD-01 →
  ... → IPLAN-01) reinforces the wrong "numbers line up" mental model.
- *Fix shape:* (a) add "Cross-layer cardinality" subsection to
  `ID_NAMING_STANDARDS.md` (or `TRACEABILITY.md`) explicitly stating
  doc numbers are per-layer independent + one-to-many + many-to-one
  both supported; (b) update `doc-<layer>` author SKILL prompts:
  *"the upstream's number is NOT your number — pick next-free in
  YOUR layer's index"*; (c) auditor playbooks: clarify orphan-looking
  downstream docs may be siblings of the same upstream, not actual
  orphans. **Deferred to a follow-up CLEANUP-PR-F (single-item)** —
  cataloged here per Tier-2 pipeline (FRAMEWORK-FEEDBACK-LOG-001
  Principle 9); impl waits until after current cleanup PRs settle.
  *Resolution:* CLEANUP-PR-F (PR #TBD, merge SHA TBD) — single-item follow-up after FRAMEWORK-CLEANUP-001 workstream closed; codified per-layer cardinality independence in ID_NAMING_STANDARDS.md.

### `[legacy]` Scan for v3.2-era anachronisms across the codebase

- *Context:* user-surfaced (2026-06-12) — the `sdd-orchestrator`
  agent-skill still carried `sdd_depth: lite | standard | full` tiers
  from the SDD v3.2 era. The current framework spec has settled on a
  single SDD path (BRD..IPLAN, all 8 required per necessary-upstream)
  with an adaptive loop (MVP → PROD → New MVP → Updated PROD). The
  legacy-sdd-depth follow-up PR removed the depth references but
  surfaced that the orchestrator's broader worldview (15-persona
  model, ucx_hermes templates, SDD v3.2 versioning) is also stale.
- *Fix shape:* dedicated v3.2-residue scan pass: grep across all
  non-`legacy-ucx-v3.2-read-only` paths for: `SDD v3`, `v3.2`,
  `sdd_depth`, `lite|standard|full` triples in SDD context, `15
  personas`, `ucx_hermes/templates`, `sdd_create` / `sdd_validate`
  CLI invocations. Hermes-side scope tracked separately in
  HERMES-BACKLOG H-11.
- *Status:* OPEN — file under `[legacy]` tag.
  *Resolution:* v3.2-residue scan PR (2026-06-12) — scanned 7
  target patterns across the codebase. One purely-dead file deleted:
  `platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/governance/SDD_DEPTH_GUIDE.md`
  (52 lines, entirely about the dead lite/standard/full depth concept).
  The broader sdd-orchestrator v3.2 worldview (SKILL.md framing,
  governance/README.md baseline references, 15-persona dispatch claim)
  stays deferred to HERMES-BACKLOG H-11 — out of scope for the
  bounded scan. References classified as legitimately-current
  (Hermes 15-persona PERSONA_CATEGORY_MAP architecture, current
  Hermes MCP tool names `sdd_create`/`sdd_validate`, CHANGELOG
  historical entries, migration plans/P*-T* files) deliberately
  not touched.
