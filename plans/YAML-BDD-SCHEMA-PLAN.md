# YAML-BDD-SCHEMA — YAML-native BDD scenarios (replace Gherkin-in-markdown)

> **DESIGN / SPEC (brainstorming output) — 2026-06-28.** Migrate the BDD
> layer's produced artifact from Gherkin-embedded-in-markdown to a structured
> **YAML scenarios block inside `BDD-NN.md`**, with an on-demand YAML→Gherkin
> emitter for any future CI runner. Status: **READY** — converged over 3
> independent gap-review passes (2026-06-28); all load-bearing findings folded;
> Pass 3 verdict READY for a plan PR (spec-tier → human sign-off per OPS-0062).

| Field          | Value                                                          |
| -------------- | -------------------------------------------------------------- |
| Task           | YAML-BDD-SCHEMA                                                |
| Type           | feature (framework spec + template + lint + skills + corpus)  |
| Status         | READY — Pass 1/2/3 converged (3 independent passes); plan PR next |
| Origin         | CFB-PR-3 REFGRAN01 surfaced a structural Gherkin/GD-03 collision (the BDD-01:55 26-element feature fan-out); user elected to review the BDD carrier format rather than enforce the fan-out |
| Version impact | framework **MINOR** (BDD template format + governance reconciliation) + tooling; plugin skills update. Bump via `bump_version.py`. |
| Scope          | Plugin **skills/engine** only; Hermes skills/engine deferred. The **shared linter code ships to the Hermes vendored copy** (byte-identity is conformance-enforced — GAP-9). |

## Problem

The BDD produced artifact (`examples/url-shortener/docs/04_BDD/BDD-01.md`)
embeds Gherkin inside ` ```gherkin ` fences. Trace data is carried as Gherkin
tags (`@ears:EARS.01.03.xxxx`), which collides structurally with the framework's
trace-tag standard:

- **GD-03 mandates a pipe-delimited multi-element form** (`@ears: X | @ears: Y`),
  but in Gherkin `|` is the data-table delimiter and tags cannot contain
  whitespace — so the GD-03 form is **physically illegal** on a Gherkin tag line.
  The corpus relies on an *unstated* space-separated carve-out that GD-03 /
  `TAG_SYNTAX.md` never acknowledge.
- One corpus tag (`@ears: EARS-01`, with a space) is in fact **invalid Gherkin**.
- The CFB-PR-3 fix prescribed fanning the feature-level `@ears` out to its 26
  scenarios' elements on one Gherkin tag line — unreadable, and the worst
  expression of the collision.
- Trace metadata is smuggled into Gherkin `#` comments (`# spec_trace: …`,
  rationale notes), which no parser captures structurally.

The BDD template (`framework/layers/04_BDD/BDD-TEMPLATE.yaml`) **already models
scenarios as structured YAML data** (`scenarios:` block, lines 249–297) — the
produced artifact simply drifted to Gherkin. The framework is pre-1.0, so the
artifact format can be realigned with its own template's model.

## Objective

Make **YAML the single source of truth** for BDD scenarios, carried as a fenced
` ```yaml ` block inside `BDD-NN.md`. Trace becomes typed list fields (no
delimiter, no Gherkin collision); REFGRAN for BDD becomes a structural schema
check; element-level coverage (COV02) becomes a direct set computation. Gherkin
is reduced to an **optional, on-demand generated output** for CI runners.

## Implementation reality (grounded — verified against code + corpus)

- **R-a — The BDD template is already YAML and already models scenarios as
  data** (`BDD-TEMPLATE.yaml:249-297`: `scenarios.{success|error|recovery|
  parameterized|optional}` — a **dict keyed by category**, each a list, with
  single-string `given/when/then`). It is too simplistic for the real corpus
  (single strings vs. the corpus's 136 multi-step lines across **31 scenarios** —
  the "26" figure elsewhere is the EARS *element* count, not scenarios). This
  plan **replaces the category-dict with a flat `scenarios:` list + a `type:`
  discriminator** (D-2 / GAP-10) — an explicit template restructure that also
  affects `_load_section_targets` and the acceptance `.yaml` heading parser.
- **R-b — All layers register `extensions: [.yaml]`; `detect_layer` does not
  enforce it.** `detect_layer` (`__init__.py:159`) matches on folder
  (`0N_<ARTIFACT>`) or filename prefix (`<ARTIFACT>-NN`), not extension. So
  there is **no hidden "BDD must be YAML" signal** — and no obstacle to a YAML
  *block* inside the `.md`.
- **R-c — `STRUCT01` requires each template section as a `##` heading; the
  linter is entirely text/regex (it scans every line, fences included).** So the
  artifact must remain a markdown doc with the five `##` sections, and a
  ` ```yaml ` block's contents are reachable by line-scanning — but the linter
  **cannot rely on `@`-tag text for BDD anymore**; it needs a YAML-aware parse
  path forked into the BDD branch of several checks (see Linter changes / GAP-4).
- **R-d — Downstream cites BDD scenarios at element level: 16 distinct IDs, 92
  `@bdd:` occurrences across 41 lines** in ADR-01 / SPEC-01 / TDD-01 (IPLAN-01
  cites none element-level). **Scenario IDs are authored content-hash strings**
  (`BDD.01.03.<hex>`). The linter never recomputes them — it only checks id
  *form* (`_ELEM_DEF_YAML`, ID03) and *uniqueness*. So ID stability across the
  migration depends **solely on the transcoder copying each existing
  `@scenario-id:` value verbatim into the YAML `id:` field** (D-6 / GAP-1 /
  Pass-2 LB-2) — NOT on reproducing the hash from title/description.
  *Qualification:* EARS-01 cites **doc-level** `@bdd: BDD-01` as forward-pointer
  navigation on ~20 lines; those are skipped by `build_edge_graph`
  (downstream-pointer exclusion) + TRACE-RES, so they are unaffected and must
  NOT be "fixed" to element form (GAP-7).
- **R-e — These docs are not CI-executed** (`BDD-TEMPLATE.yaml:45`: "QA STAGING
  ONLY — do NOT run in CI"). Gherkin's unique advantage (direct runner
  execution) is unused here, so it is correctly an optional output, not the
  source.
- **R-f — `yaml` is already a linter dependency** (`__init__.py:28`). YAML
  authoring/linting/emit need no new runtime dependency; the stdlib-only
  constraint holds (the linter only ever *reads* YAML).
- **R-g — `_ELEM_DEF_YAML` already matches `id:` lines** (`__init__.py:637`:
  `^\s*[-]?\s*id:\s*…`), so scenario-ID **declarations** are detected once they
  live as `id:` fields, and `_ELEM_ID.finditer` registers them under host
  `BDD-01` automatically — downstream `@bdd:` resolution then works unchanged
  **provided the IDs are copied verbatim** (R-d / D-6).
- **R-h — Migration fidelity: a deterministic Gherkin→YAML transcode preserves
  the authored `@scenario-id:` strings** (it copies them verbatim into `id:`),
  so every downstream `@bdd:` citation survives. It drops `#` comments + exact
  formatting, which the transcoder lifts into `notes:`/`spec_trace:` fields. An
  **LLM regeneration from EARS is NOT safe** (it re-authors scenarios → new
  `@scenario-id:` strings → broken downstream). This forces D-6.

## Design decisions

**D-1 — Carrier: YAML block inside `BDD-NN.md`.** The artifact stays a markdown
doc with YAML frontmatter + the five `##` sections (`STRUCT01`, size checks,
index conventions untouched; consistent with the other 7 layers). §2 Feature
Definition and §3 Scenario Structure carry ` ```yaml ` blocks. (Alternatives:
standalone `.yaml` artifact — breaks `STRUCT01`/`detect_layer`/index model;
sibling `.scenarios.yaml` — two-file sync complexity. Both rejected.)

**D-2 — Step model: phase lists; thresholds inline in step prose.** Each
scenario carries `given`/`when`/`then` as lists; multiple entries are `And`
continuations. **Thresholds are written inline in the step prose text using the
`@threshold:PRD.NN.cat.key` form** — NOT a structured field. This (a) matches how
the corpus already writes them, (b) supports thresholds on *any* phase incl.
`Given` and *multiple* per step, and (c) keeps `TH-RES-001`/`TH02`/the ID03
`_in_threshold` guard working — a bare `threshold:` field would fire `ID03` and be
invisible to threshold resolution (GAP-2/GAP-3). **One required linter tweak
(Pass-2 LB-1):** `_THRESHOLD` (`__init__.py:66`) currently captures up to the
next whitespace/pipe, so a `@threshold:` at the *end* of a quoted YAML scalar
glues the closing `'`/`"` into the value and false-fires **TH01**. Fix:
`@threshold:\s*([^\s|'"]+)` — a one-line, benign, all-layer tightening (it also
helps any future quoted context). This is a deliberate linter change, not
"unchanged"; it carries its own conformance note. (Alternative: structured
`{text, threshold}` map — rejected; breaks the linter and cannot hold
Given/multi thresholds.)

**D-3 — Coverage: union-of-scenarios, computed.** The Feature carries **no
`ears` field**; its EARS coverage = `union(scenarios[].ears)`, computed by the
linter. This dissolves the fan-out problem at the root. BDD's
`required_tags: [ears]` is satisfied iff ≥1 scenario carries ≥1 element-level
`ears`. (Alternative: explicit feature `ears` validated == union — redundant
data; rejected.)

**D-4 — Gherkin emitter: on-demand, not committed; one-way.** `tools/bdd_to_gherkin.py`
reads `BDD-NN.md`'s YAML and emits a `.feature` to a git-ignored dir. It is
**one-way** — emitted runner tags are `@scenario-type:{type} @p{priority}
@scenario-id:{id}`; trace (`ears`/`spec_trace`) is YAML-only by design, so the
emitted `.feature` deliberately differs from the original Gherkin (it is NOT a
Gherkin→YAML→Gherkin round-trip). It is "lossless for executable content."
(Alternatives: committed `.feature` with drift-guard — re-introduces sync drift;
drop Gherkin — defers executability needlessly. Both rejected.)

**D-5 — Scope: plugin skills/engine only; Hermes skills/engine deferred; shared
linter ships to both.** Migrate the framework spec (BDD template + governance),
the example corpus BDD-01 + the acceptance fixtures, the `doc-bdd*` skills, the
`sdd_doc_lint` BDD parse path + emitter + transcoder, and conformance/unit
tests. The **linter is one canonical copy + two byte-identical vendored mirrors**
(`__init__.py:4-7`; `sync-vendored.sh`) — so the BDD parse-path code **must**
re-vendor into `platforms/hermes/sdd_doc_lint/` too (byte-identity is
conformance-enforced). Only the **Hermes skills/engine** parity is deferred to
`HERMES-BACKLOG.md` (GAP-9).

**D-6 — Migration = a deterministic Gherkin→YAML transcoder built as a framework
tool that COPIES scenario IDs verbatim (NOT skill regeneration).** Because
downstream `@bdd:` citations resolve against the authored `@scenario-id:` strings
(R-d), the transcoder `tools/gherkin_to_bdd_yaml.py` **copies each existing
`@scenario-id:` value verbatim into the scenario `id:` field and never recomputes
a hash**; `name`/steps are carried for fidelity but are not what stabilizes the
ID. It parses the existing `BDD-01.md` Gherkin → emits the new YAML-block `.md`,
lifting `# spec_trace:`/rationale comments into `spec_trace:`/`notes:`. It is
**machine-produced**, satisfying CLAUDE.md's "never hand-edit example artifacts"
rule without an LLM regeneration that would drift the IDs. The transcoder is a
one-time tool but is **committed** (auditable, re-runnable). This supersedes the
earlier "regenerate via `doc-bdd` skill from EARS" idea (GAP-1).

## Schema (normative)

§2 Feature Definition (` ```yaml ` block):

```yaml
feature:
  name: "URL Shortener acceptance behaviour"
  description: |
    As a Link Submitter, Link Visitor, and Service Owner
    I want to shorten public URLs, resolve them quickly, and observe adoption
    So that long links become compact, dependable, abuse-resistant short links
  background:
    steps:
      - "the system is in a ready state"
      - 'the current time is "09:30:00" in "America/New_York"'
# no ears field — feature EARS coverage = union(scenarios[].ears)
```

§3 Scenario Structure (` ```yaml ` block — a **flat list** with a `type:`
discriminator, replacing the template's category-dict, GAP-10):

```yaml
scenarios:
  - id: BDD.01.03.ccd6          # required — copied verbatim from the source @scenario-id; never recomputed
    name: "Shorten a valid public URL"   # required
    type: success               # required — success|error|recovery|parameterized|optional
    priority: p0-critical       # required — p0-critical|p1-high|p2-medium|p3-low
    ears: [EARS.01.03.5066, EARS.01.03.bca8, EARS.01.03.6811]   # required, >=1, ELEMENT-LEVEL only
    spec_trace: ["SPEC §3 (Interfaces)", "SPEC §5 (Behavior)"]  # optional list
    given:                      # >=1; multiple entries = And; thresholds inline as @threshold:
      - 'a Link Submitter with the well-formed public URL "https://example.com/page" within @threshold:PRD.01.quota.urlmaxlen'
    when:                       # >=1
      - 'the submitter posts the URL to the Shorten/Redirect API'
    then:                       # >=1; thresholds inline in the prose (any phase, any count)
      - 'the API SHALL return a unique short code resolving to "https://example.com/page" WITHIN @threshold:PRD.01.perf.screeningdeadline'
      - 'the API SHALL present "Your short link is ready."'
    notes:                      # optional list — absorbs the Gherkin # rationale comments
      - "split from the former combined counting+idempotency scenario"

  - id: BDD.01.03.xxxx
    name: "Validation accepts valid <input_type>"
    type: parameterized
    priority: p2-medium
    ears: [EARS.01.03.xxxx]
    outline: true
    given:
      - 'a valid <input_type> value "<value>"'
    when:
      - 'the value is validated'
    then:
      - 'validation SHALL pass'
    examples:
      headers: [input_type, value]
      rows:
        - [email, "user@example.com"]
        - [phone, "+1-555-123-4567"]
```

Field rules:

- `id`, `name`, `type`, `priority`, `ears` (≥1), `given` (≥1), `when` (≥1),
  `then` (≥1) are **required** per scenario.
- `id` is **copied verbatim** by the migration transcoder from the source
  `@scenario-id:`; the linter never recomputes it (R-d / D-6).
- `ears` items MUST be **element-level** (`EARS.NN.SS.xxxx`); doc-form `EARS-NN`
  is rejected — enforced by **REFGRAN01** via verbatim synthetic edges (see
  Linter §item 3); `BDD-SCHEMA-001` does NOT also flag `ears` granularity
  (no double-report, Pass-2 LB-3).
- Thresholds are written **inline in step prose** as `@threshold:PRD.NN.cat.key`
  (D-2); resolved by `TH-RES-001`/`TH02` (with the `_THRESHOLD` quote fix).
- `spec_trace`, `notes` (both **lists**), `outline`, `examples` are optional.
- `examples` requires `outline: true`; `headers` + `rows` with matching arity.

## Linter changes (`tools/sdd_doc_lint`) — a BDD *fork* of ~5 checks (GAP-4)

The linter is text/regex over `corpus: list[(rel, text)]`. Switching BDD off
`@`-tags forks the BDD branch of these (every other layer stays text-based):

1. **BDD YAML parse path** — when `detect_layer == BDD`, parse the §2/§3
   ` ```yaml ` blocks via the imported `yaml`. Malformed block / missing required
   field → new finding `BDD-SCHEMA-001`. `BDD-SCHEMA-001` owns **structural**
   faults only (not `ears` granularity — REFGRAN01 owns that; no double-report).
2. **`build_edge_graph`** (`:1157`) — emit **one synthetic upstream edge per raw
   `ears` token, verbatim (doc-form `EARS-01` included)**, with
   `cited_doc = doc_id_from_token(token)` (= `EARS-01` for both forms, matching
   `:1202,:1209`) so that REFGRAN01 / COV01 / COV02 all see BDD↔EARS lineage
   identically AND REFGRAN can still fire on a doc-form `ears` (Pass-2 LB-3;
   Pass-3 finding 2). Element **registration** of scenario `id`s is automatic via
   `_ELEM_ID.finditer` over the `id:` lines (no fence-skip; no fork needed,
   Pass-2 M-4) — the genuine fork work is synthesizing the EARS edges. The BDD
   per-line `_TAG` scan is **supplemented, not replaced**, by the YAML `ears`
   fork (Pass-3 finding 1); the `ears:` list carries no `@`, so the residual
   `_TAG` scan finds only the `@bdd: BDD-01` self-tag (dropped) and `@threshold:`
   (not a layer tag) — no phantom edges.
3. **`REFGRAN01`** (`:1493`) — unchanged in mechanism (iterates `graph.edges`,
   tests `_DOC_FORM.match(cited_token)`); because item 2 emits verbatim `ears`
   edges, REFGRAN01 fires on a doc-form `ears` item and is silent on element-form
   — **this is the enforcer of element-level `ears` for BDD**. REFGRAN for
   SPEC/TDD/IPLAN/ADR markdown `@`-tags is unchanged.
4. **`TRACE-RES-001`** (`:1284`) — resolve BDD upstream EARS citations from the
   parsed `ears` lists (the `ears:` list has no `@`, so `_TAG`/TRACE never see it
   without the fork).
5. **`TAG01` required-tags** (`lint_text:543`) — BDD `required_tags:[ears]`
   satisfied from parsed scenario `ears`, not `seen_tags` from `@ears:` matches.

- **`_THRESHOLD` regex tightening** (D-2 / Pass-2 LB-1) — `@threshold:\s*([^\s|'"]+)`
  so a `@threshold:` ending a quoted YAML scalar does not false-fire TH01.
  All-layer, benign.
- **Unchanged:** `STRUCT01` + size checks (sections + ## headings stay);
  `id-uniqueness`/`ID01-03` (operate on `id`s via `_ELEM_DEF_YAML`, already
  matching — R-g); `TH-RES-001`/`TH02` resolution logic (only the `_THRESHOLD`
  capture boundary changes).
- **Conformance/unit-fixture impact (GAP-4 + Pass-3 finding 1):** two test files
  build BDD docs in the `@ears:` tag form and must be migrated to the YAML `ears:`
  form: `tests/conformance/test_coverage_engine.py:122,130` (incl. the
  `RefGranularityContract` doc-form-blocks test) and the **canonical**
  `tests/unit/test_ref_granularity.py:35,44,61,68,82` (six BDD `@ears` fixtures —
  the exact LB-3 mechanism). Both stay green only because item 2 emits a verbatim
  (doc-form) synthetic edge. (Cosmetic, deferrable: `test_sdd_doc_lint_sty03_fences.py`
  uses a ```gherkin fence whose premise goes stale post-migration — Pass-3
  finding 3.) In scope.

## Gherkin emitter (`tools/bdd_to_gherkin.py`)

- Reads `BDD-NN.md` YAML → emits `.feature` to a git-ignored dir (e.g.
  `dist/features/`), deterministic + idempotent.
- Mapping: `feature`→`Feature:`; `background`→`Background:` (steps prefixed
  `Given`/`And`); scenario→`Scenario:` or `Scenario Outline:` (when
  `outline: true`); `given/when/then` lists→`Given/When/Then` + `And` for
  subsequent items; `examples`→`Examples:` table. Runner tags only (one-way,
  D-4).

## Migration (corpus BDD-01 + acceptance fixtures) — GAP-1/GAP-5

- `tools/gherkin_to_bdd_yaml.py` (D-6) transcodes the existing Gherkin →
  YAML-block `.md`, **copying every `@scenario-id:` string verbatim into `id:`**
  so all downstream `@bdd:` citations (16 IDs / 92 occurrences) stay resolvable.
  Lifts `# spec_trace:`/rationale into `spec_trace:`/`notes:`.
- **Acceptance fixtures (Pass-2 M-1):** transcode the **7 `BDD-01_golden.md`**
  Gherkin fixtures (`tests/acceptance/fixtures/fullpath/{golden_chain,broken_chain}`
  - `layer_0{4,5,6,7,8}_*/valid/BDD-01_golden.md`). The **`layer_04_bdd/broken/
  BDD-01_missing_section.md`** fixture has **no Gherkin** (structural-omission
  fixture for STRUCT01) — not a transcode target; verify it still trips STRUCT01.
  **`layer_04_bdd/broken/BDD-01_drift_codes.yaml`** is the harness expectation
  manifest — verify-only (STRUCT01 unchanged). The acceptance harness
  `headings()` (`tests/acceptance/_harness.py:121`) must still normalize the new
  `.md`-with-yaml-block by H2 — verify.
- **Post-migration verification:** 0 BDD REFGRAN; COV01/COV02 pass; **every
  downstream `@bdd: BDD.01.03.*` still resolves** (V4 ID-stability test);
  conformance + acceptance suites green.
- Because the transcoder is a framework tool, no live plugin session is required
  for the corpus migration (GAP-1). A plugin session is still useful to validate
  the rewritten `doc-bdd*` skills end-to-end.

## Skills (plugin: `doc-bdd`, `doc-bdd-audit`, `doc-bdd-fixer`, `doc-bdd-autopilot`)

- Author/audit/fix the YAML scenario block instead of Gherkin fences.
- Audit "Gherkin quality (25%)" sub-score → "Scenario quality" (well-formed
  YAML, atomic scenarios, executable phrasing, element-level `ears`).
- Replace "NO spaces after colon in tags" guidance with the YAML schema contract.
- **Conformance gate (GAP-6):** the skill rewrite must keep
  `tests/conformance/platforms/test_skill_template_alignment.py`,
  `plm_lint.py`, and `test_autopilot_saga_parity.py` passing.

## Spec bump, governance & full surface list

Framework **MINOR** bump (BDD template format + governance reconciliation).
Surfaces (expanded per GAP-6); **governance** surfaces (subject to the ≤3-per-PR
rule) flagged ⚖:

- **Governance ⚖:** `GD-03` note (BDD trace via structured `ears` lists),
  `TAG_SYNTAX.md` (the BDD no-space `@ears:` carve-out **table row + necessary-
  upstream example**), `DECISIONS.md` (D-numbers for D-1…D-6).
- **Spec/template:** `BDD-TEMPLATE.yaml` (category-dict → flat list),
  `BDD-00_index.TEMPLATE.md`, `framework/layers/04_BDD/README.md`,
  `framework/QUICK_REFERENCE.md`, `framework/playbooks/04_BDD/*.md` (qa_lead,
  auditor, chaos_engineer, security_engineer, tech_lead — all reference Gherkin).
- **Tooling:** `bump_version.py`, `sync-plugin-framework.sh`, `sync-vendored.sh`
  (byte-identity into the Hermes copy — GAP-9), new `gherkin_to_bdd_yaml.py` +
  `bdd_to_gherkin.py`.
- **Docs of record:** BDD README, `PARITY.md`, CHANGELOG, ROADMAP, HANDOFF.
- Spec-tier + governance PR → 2-cycle plan review → human sign-off. The
  governance "≤3 *governance* doc surfaces per PR" rule + the breadth above mean
  the work realistically splits into **~6–8 sequential PRs** (Pass-2 M-5), e.g.
  linter+transcoder → template+schema → corpus+fixtures → skills → governance
  docs → version bump + docs-of-record.

## Scope boundary — what this does and does NOT solve (GAP-8 tightened)

- ✅ Resolves the **2 BDD** REFGRAN edges (BDD-01:31 — the §1 `ears_reference`
  row, removed; BDD-01:55 — the feature tag, eliminated by D-3) and the
  Gherkin/GD-03 collision at the root.
- ✅ Provides **forward** EARS coverage as `union(scenarios[].ears)` (D-3), and
  the synthetic-edge data that **enables** the future **backward** element-level
  COV02 upgrade. It does **not deliver** that upgrade — the "15 orphaned BDD
  scenarios" (31 declared − 16 cited downstream) are a *backward* BDD→SPEC/TDD
  gap surfaced only by the COV02 element-level upgrade, which remains a separate
  follow-on. (Forward EARS-coverage and backward orphan-detection are opposite
  directions — do not conflate.)
- ❌ Does **not** touch the **5 SPEC/TDD/IPLAN `@adr`/`@tdd`** REFGRAN edges —
  ordinary markdown doc-level tags, still handled by CORPUS-REFGRAN-RECASCADE
  (3 same-line drops + 1 table-cell + 1 prose). The `REFGRAN --fix` investigation
  still applies to those 5 if auto-fix is wanted.
- **Out of scope:** Hermes skills/engine (deferred); the element-level COV02
  *upgrade itself*; any SPEC/TDD/IPLAN format change.

## Verification (to be expanded in the implementation plan)

| #  | Check | Expected |
| -- | ----- | -------- |
| V1 | Linter parses §3 YAML; `BDD-SCHEMA-001` flags malformed block / missing required field (structural only) | finding |
| V2 | REFGRAN01 fires on a doc-form `ears` item (verbatim synthetic edge), silent on element-form; no BDD-SCHEMA-001 double-report | per mode |
| V3 | `build_edge_graph` emits one verbatim synthetic BDD→EARS edge per `ears` token; scenario IDs auto-registered | edges correct |
| V4 | **ID stability:** after transcode, every downstream `@bdd: BDD.01.03.*` (16 IDs) still resolves | 0 unresolved |
| V5 | Inline `@threshold:` ending a quoted scalar resolves via TH-RES-001/TH02 and does NOT false-fire TH01 (the `_THRESHOLD` fix) | no TH01 |
| V6 | YAML→Gherkin emit is deterministic + idempotent and produces well-formed Gherkin for all constructs (feature/background/scenario/outline/examples); one-way (trace YAML-only) | green |
| V7 | Migrated BDD-01 + the 7 golden fixtures corpus-green (0 BDD REFGRAN, COV01/COV02 pass); `missing_section.md` still trips STRUCT01 | green |
| V8 | `test_coverage_engine.py` BDD fixtures updated to YAML form; conformance green | green |
| V9 | `test_skill_template_alignment.py` / `plm_lint.py` / `test_autopilot_saga_parity.py` pass after skill rewrite | green |
| V10 | Both `FRAMEWORK_SPEC_VERSION` bumped; vendored byte-identity (incl. Hermes copy) | green |
| V11 | Corpus cross-check `python3 -m sdd_doc_lint examples/url-shortener/docs/` shows no NEW findings vs the recorded baseline | green |

> **Recorded corpus baseline (current main, 2026-06-28):** 1× TH-RES-001
> (pre-existing PRD gap, `CORPUS-PRD-TH-RES`), 7× REFGRAN01 (the edges this +
> CORPUS-REFGRAN-RECASCADE address), 6× STY02 (pre-existing size warnings). V11
> compares against this.

## Open questions (for the implementation plan)

- `BDD-SCHEMA-001` severity/run-mode (warning/build, error/gate-code, or
  always-error for a structural schema violation?).
- Whether §2 background steps store bare text (emitter adds the keyword) — the
  schema currently stores bare text; confirm.
- Exact PR split (likely 6–8) and which surfaces count as *governance* surfaces.
- Whether the one-time transcoder lives under `tools/` permanently (recommended:
  keep, committed + auditable).

## Review log

### Pass 0 — 2026-06-28 — brainstorm (design approved)

Design produced via the brainstorming skill; 5 core decisions (D-1…D-5) chosen
by the user. Grounded against code + corpus (R-a…R-g).

### Pass 1 — 2026-06-28 — independent (fresh-context) — 10 gaps folded

5 load-bearing + 5 minor gaps folded: GAP-1 (migration self-contradiction →
D-6 transcoder), GAP-2 (bare `threshold:` breaks ID03/TH-RES → inline
`@threshold:`), GAP-3 (schema couldn't hold Given/multi thresholds + multi notes
→ inline + `notes` list), GAP-4 (linter is a multi-function fork; missed
`test_coverage_engine.py` fixtures), GAP-5 (8 acceptance fixtures), GAP-6
(TAG_SYNTAX row/playbooks/QUICK_REFERENCE/skill-alignment tests), GAP-7 (R-d
overclaim — EARS doc-level `@bdd` pointers fine), GAP-8 (15-orphan overstatement;
forward vs backward), GAP-9 (Hermes vendored-linter byte-identity), GAP-10
(category-dict → flat list). Confirmed sound: `_ELEM_DEF_YAML` matches `id:`
(R-g); YAML carrier + on-demand emitter; not-CI-executed (R-e).

### Pass 2 — 2026-06-28 — independent (fresh-context) + corpus cross-check — 3 load-bearing + 5 minor folded

Pressure-tested the Pass-1 patches against the actual regexes + corpus + tests:

- **LB-1 (load-bearing, real bug):** inline `@threshold:` ending a quoted YAML
  scalar glues the closing quote into `_THRESHOLD`'s capture → spurious **TH01**
  → migrated golden fails `assert_golden_passes_lint`. D-2's "works unchanged"
  was false. → **fix `_THRESHOLD` to `([^\s|'"]+)`** (all-layer, benign); D-2 +
  Linter + V5 updated. (TH-RES-001/TH02 were unaffected — `_THRESHOLD_PARSED`
  stops at the quote.)
- **LB-2 (load-bearing, wrong reasoning):** there is no per-scenario
  title/description in the hash input and **nothing recomputes the hash** — IDs
  are authored strings. Stability comes from the transcoder **copying
  `@scenario-id` verbatim into `id:`**, not from preserving prose. → R-d/R-h/D-6
  - schema field-rules rewritten.
- **LB-3 (load-bearing, contradiction):** for REFGRAN01 to enforce element-form
  `ears` (and keep the conformance test green) the fork must emit a synthetic
  edge per **raw `ears` token verbatim, doc-form included** — item 2's "cited =
  EARS element" said the opposite. → Linter item 2/3 + schema field-rule
  reconciled; BDD-SCHEMA-001 limited to structural faults (no double-report).
- **M-1:** added `BDD-01_drift_codes.yaml` (verify-only); reclassified
  `missing_section.md` (no Gherkin → not a transcode target). Count corrected to
  7 golden transcode targets.
- **M-2:** corrected "~26 scenarios" → **31**; "~40 sites" → **16 IDs / 92
  occurrences across 41 lines** (verified by grep).
- **M-3:** V6 + D-4 "lossless" qualified — the emitter is one-way (trace
  YAML-only), not a true Gherkin round-trip.
- **M-4:** scenario-ID registration is automatic via `_ELEM_ID`; only EARS-edge
  synthesis is genuine fork work. Item 2 tightened.
- **M-5:** PR split is realistically **6–8** PRs; "≤3 doc surfaces" targets
  *governance* docs, not every code file. Surface list marks ⚖ governance
  surfaces.

Corpus cross-check (current main) recorded as the V11 baseline (1 TH-RES, 7
REFGRAN, 6 STY02).

### Pass 3 — 2026-06-28 — independent (fresh-context) — VERDICT: READY

Traced LB-1/LB-2/LB-3 end-to-end through the actual code; all three hold:

- **LB-3 sound:** `EARS ∈ _REFGRAN_ELEMENT_DECLARING` (`:1490`) so a verbatim
  doc-form `EARS-01` synthetic edge fires REFGRAN01 (`_DOC_FORM.match`, `:1528`);
  it does NOT break COV01/COV02/TRACE-RES because `doc_id_from_token` returns
  `EARS-01` for both token forms (`trace_graph.py:40-51`) → identical
  forward-reach + the doc resolves. `DOC_FORM` and `ELEM_FORM` are disjoint
  (`trace_graph.py:35-37`) so a valid element-level token never trips REFGRAN.
  `test_no_double_fire_only_refgran01` already locks single-finding behavior.
- **LB-2 sound:** `_ELEM_ID` scans full text (no fence-skip; fences skipped only
  in frontmatter-extraction + size-counting) → `id:` lines inside the ```yaml
  block register under host `BDD-01` (`:1185-1191`).
- **LB-1 sound + regression-free:** real TH01 false-fire confirmed; grep of all
  `@threshold:` in `examples/` + `tests/` shows zero quote-adjacent values today;
  `_THRESHOLD_PARSED` already stops at a quote so TH-RES-001/TH02 are unaffected
  — only `_THRESHOLD` needs the change.

Folded 2 non-load-bearing nits: finding 1 (add `tests/unit/test_ref_granularity.py`
to the fixture surface; state the BDD `_TAG` scan is *supplemented*, not replaced)

- finding 2 (pin synthetic-edge `cited_doc = doc_id_from_token(token)`). Finding 3
(`test_sdd_doc_lint_sty03_fences.py` cosmetic) deferred. No new contradiction
across D-1..D-6 / schema / linter / V1-V11.

**Result:** READY for a plan PR. Converged over **3 independent passes (1, 2, 3)**

- 1 self (Pass 0 brainstorm). The corpus cross-check (V11) runs at implementation
time against the regenerated corpus per CLAUDE.md.
