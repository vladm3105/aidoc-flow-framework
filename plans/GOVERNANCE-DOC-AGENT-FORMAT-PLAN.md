# Plan: Governance Documentation — Agent-Friendly Format Conversion

## Metadata

| Field | Value |
| --- | --- |
| Author | AI agent (framework maintainer review pending) |
| Date | 2026-10-26 |
| Status | Proposed — implementation starts only after this plan PR merges |
| Framework Version | 0.96.13 |
| Plan type | Migration / rollout, evidence-gated |

## Goal

Make governance documentation reliably consumable by AI agents without losing
human reviewability, by converting only machine-consumed, enumerable governance
fact-blocks to single-source YAML spliced into generated Markdown blocks, and
by making the remaining governance Markdown structured.

Explicitly not a goal: bulk Markdown-to-YAML rewriting, any governance
doc-as-graph sidecar, or converting normative prose and discursive documents.

## Success Criteria

1. A per-file, per-fact-block inventory classifies every Markdown file under
   `framework/governance/` (count measured and recorded in Phase 0) by bucket
   and authority direction: doc-leads, code-leads, or bidirectional guard.
2. A benchmark on one fact-block measures agent accuracy, tokens, and
   retrieval steps for current Markdown vs structured Markdown vs YAML,
   against pre-registered thresholds (Phase 1). Retrieval steps are measured
   and reported; the go/no-go gate is accuracy and tokens.
3. If and only if the benchmark passes, one pilot fact-block is single-source
   YAML with its Markdown block generated in place; the rest of its host
   document stays hand-authored Markdown.
4. No converted fact loses normative content: condition, exception, severity
   context, and version applicability survive as named fields, or the fact
   stays in Markdown.
5. All existing paths, anchors, and permalinks keep resolving, verified by a
   full offline link check over changed files
   (`lychee --config .lychee.toml --offline --no-progress <changed-files>`).
   Full conformance suite stays green.
6. Every executing CHG states its ratified vehicle shape. This plan's spec
   phases follow the controlling precedent for framework self-changes
   (Claims 11–12): flow DIR2C (`iplan_to_code`), `change_source: spec`,
   entry gate GATE-SPEC, level C2 (C3 only when SemVer impact is major),
   `semver_impact: patch`, one `sdd_lifecycle` step per touched artifact
   (archive → rewrite → `supersedes`), human sign-off, GATE-SPEC security
   review, and the `framework/VERSION` bump protocol (bump, append prior
   version to `OLD_VERSIONS` — Claim 8 — run `hooks/sync-version-refs.sh`,
   verify with `spec_gate.py`). Any non-archive `framework/` edit counts as
   a spec change for the bump. Phases 0–1, which touch no `framework/` file,
   ride DIR2C, `change_source: direct`, GATE-CODE, C1 CHG + scoped IPLAN
   (no SemVer impact, no `sdd_lifecycle`, no bump).

## Approach

### Key decisions

- **Decision rule.** A governance fact-block converts to YAML only when all
  three hold: (a) a machine consumes it today (linter, conformance test,
  hook, workflow); (b) it is enumerable without losing normative meaning;
  (c) authority is doc-leads or bidirectional — a doc-leads YAML becomes the
  source code follows; a bidirectional fact keeps one YAML checked by both
  sides through an agreement test modeled on the catalog guard (Claim 2 is
  agreement checking only, not generation — there is no precedent here for
  two sides generated from one YAML).
- **Partial conversion by splice.** Conversion is per fact-block, not per
  document. A converted block lives in a YAML file; a generator splices its
  rendered Markdown between markers in the host `.md` file, leaving prose,
  diagrams, and other sections hand-authored. Agreement projections in other
  files stay validated by existing conformance tests during the pilot;
  generating them is a separate, later decision.
- **Markdown remains the human surface.** Generated blocks render in the
  same file at the same anchors for GitHub PR review by human gate approvers.
- **Ratified vehicle, not router shorthand.** `change_source: spec` makes a
  CHG lifecycle-carrying: IPLAN creation with zero `sdd_lifecycle` steps is
  a CHG-L005 error (Claim 12). The SEED2C row nominally owns `spec` in the
  router table, but its seed→module cascade does not apply to framework
  self-changes; the controlling precedent is the DIR2C + `spec` shape of
  the governance self-change in Claim 11. An executor following the
  "DIR2C carries an empty lifecycle" shorthand would fail pre-commit.
- **Reuse before inventing.** Two existing assets are evaluated before any
  new build: the SDD slicer (Claim 4) and the existing Markdown renderer
  `render_spec_sheet` (Claim 9). Neither serves governance docs today — the
  slicer only accepts `TYPE.NN.SS.hex` element headings in `TYPE-NN`
  documents, and the renderer consumes property graphs — so extension work
  is budgeted as certain, not conditional. The property-graph engine is a
  separate system (Claim 5) and stays untouched.
- **The governance exemption has no cited rationale.** Principle 2 exempts
  governance surfaces (Claim 1) but cites GD-17 only for per-layer
  extensions and the mandate's effective condition; GD-17 itself gives no
  rationale for the exemption (Claim 3). Phase 0 searches provenance
  (decisions register, CHG archives); if none is found, the exemption is
  recorded as an unexplained scope boundary, and extending YAML-first to
  governance requires GATE-SPEC human sign-off on that basis.
- **Tech stack.** No new runtime, dependency, service, or infrastructure is
  proposed. Tooling extends the existing Python `sdd_doc_lint` surface,
  validated per pilot YAML against its new JSON Schema with the
  `jsonschema.validate(yaml.safe_load(...))` one-liner pattern. If a needed
  tool is missing from the Authoritative Platform Technology Stack, work
  halts and the operator is asked; no unapproved package is adopted and no
  insecure option (weakened checks, bypassed verification) is used.

### Buckets (assigned per fact-block in Phase 0)

| Bucket | Treatment | Candidates (pending Phase 0 proof) |
| --- | --- | --- |
| Machine-consumed, enumerable | YAML source, spliced MD block | CHG flow router rows (§1) |
| Already YAML / workflow | Unchanged in this plan | `*.sw.yaml`, CHG templates |
| Normative prose with conditionals | Structured MD only | `SEED_CONTRACT.md`, lint-rule semantics |
| Discursive / human | Markdown unchanged except Phase 2a metadata | `AUTHORING_STYLE.md`, READMEs |
| Tombstone | Never touch | `DECISIONS.md` (retired, frozen) |

## Steps

### Phase 0 — Evidence and inventory (no format change)

Vehicle: DIR2C, `change_source: direct`, GATE-CODE, C1 CHG + scoped IPLAN.

1. Inventory every governance Markdown file per fact-block: bucket, authority
   direction, machine consumers, comment-as-normative guards, inbound
   references (run, not assumed).
2. Search provenance for the governance exemption (Claim 3). Record either
   the found rationale or its absence.
3. Collect recorded agent failures touching governance docs from CHG
   archives and issues, as background only. Historical causation is not a
   gate for any phase; the Phase 1 benchmark is.
4. Deliverable: inventory table in the executing IPLAN.

### Phase 1 — Benchmark (one fact-block, committed evidence)

Vehicle: DIR2C, `change_source: direct`, GATE-CODE, C1 CHG + scoped IPLAN.
Harness, task set, and raw results are committed with the IPLAN (auditable;
no uncommitted scratch evidence). Prototype arms live outside `framework/`.

1. Test block: the §1 router of `framework/governance/CHG_REQUEST_FLOWS.md`,
   including the `spec` → GATE-SPEC route in the task set.
2. Three arms: current Markdown, structured Markdown, YAML. Each arm runs
   isolated — the agent sees only that arm's document, never the repo's
   other restatements of the same contract.
3. Frozen before any run: task set (≥30 tasks: classify change → flow,
   entry gate, verification), exact-match scoring rubric on the
   (flow, gate, verification) triple, one named model, majority vote over
   3 repeats per task. Slicer-query tasks ("return the block governing X")
   are included to size the Phase 2a slicer extension. Median retrieval
   steps per arm are recorded and reported but do not gate.
4. Pre-registered gate. Let `A_y` and `A_s` be the YAML and structured-MD
   accuracies in percentage points. The ≥90% floor applies to **both**
   arms: if either arm scores below 90%, the run is inconclusive and the
   plan ends after Phase 2a (format is not the lever). Otherwise YAML
   proceeds to Phase 2b iff `A_y − A_s ≥ 15`, or `|A_y − A_s| ≤ 2` with
   ≥30% fewer YAML tokens. Claim 7 records this superiority as
   unmeasurable until probed. If the gate fails, the plan ends after
   Phase 2a.

### Phase 2a — Structured Markdown (unconditional)

Vehicle: DIR2C + `change_source: spec` (Claim 11), GATE-SPEC, C2, `patch`,
GATE-SPEC security review, human sign-off, version-bump protocol. One
`sdd_lifecycle` step per touched document (archive → rewrite → `supersedes`).

1. First deliverable is a syntax note in the IPLAN defining: stable section
   IDs, and front-matter restricted to non-duplicated keys (`doc_id`,
   `bucket`, `authority`, `consumers`). Fields `status`, `version`, and
   `last_updated` are forbidden in front-matter — they would duplicate
   Document Control and trigger FM01 consistency obligations.
2. Apply the syntax to normative-prose and discursive docs per inventory.
3. Extend `sdd_doc_lint/slice.py` to the new section-ID grammar (certain
   work, sized by Phase 1 slicer tasks; the `TYPE-NN` document filter needs
   a governance admission rule).

### Phase 2b — YAML pilot, one fact-block (conditional on Phase 1 gate)

Vehicle: as Phase 2a.

1. Evaluate `render_spec_sheet` (Claim 9) for reuse; build only the missing
   splice emitter for YAML-to-Markdown-block rendering. (Reuse risk is
   recorded: the renderer is domain-locked to SDD node types, so the delta
   may be larger than hoped — the emitter-cost risk entry covers this.)
2. Author the pilot block's YAML plus a new JSON Schema for it, under
   `framework/governance/`. Normative guidance goes in `_guidance` fields
   (the layer-template convention), never only in YAML comments. Facts whose
   guards machine-check raw comments are excluded unless their guard is
   migrated in the same PR.
3. Splice the generated block into the host document at the original
   anchors. Update the exact-file-set governance guard (Claim 10) and any
   mirror/agreement tests in the same PR — updated to check generation,
   never weakened to pass.
4. Agreement projections in other files remain test-validated, not
   generated, in this pilot.

### Phase 3 — Scale by bucket (conditional on pilot verdict)

Vehicle per document: as Phase 2a, one document per PR.

1. Entry condition (all three required): the pilot is green including
   updated guards; the Phase 1 benchmark benefit reproduces on the pilot
   document re-run under the same gate; recorded pilot author time does
   not exceed the drift-fix time it replaces. Otherwise the plan ends at
   Phase 2b and the verdict is recorded.
2. Convert further fact-blocks only if they pass all three decision-rule
   tests. Re-run the Phase 1 benchmark tasks after each conversion; stop
   scaling if the benefit does not reproduce.
3. Governance graph work is out of scope for this plan: the current schema
   closes node types and ID patterns to layer artifacts (Claim 6). A graph
   would need its own versioned design and its own plan.

### Rollback

Rollback is forward-only: a new CHG restoring hand-authored Markdown at the
same path, with a fresh `framework/VERSION` bump — a published spec version
is never reused by reverting. No Markdown block is replaced before its
generated replacement is green in CI.

## Validation Plan

- Phase 0: file count by `find framework/governance -name '*.md' | wc -l`;
  inbound references by `rg` per document; both recorded in the IPLAN.
- Phase 1: gate thresholds checked against committed raw results.
- Phase 2a: `python3 -m sdd_doc_lint framework/governance` clean (a path
  argument is required); slicer smoke query per updated document;
  `python3 -m pytest tests/ -q`.
- Phase 2b: new YAML validates against its new JSON Schema; splice
  generation idempotent (second run zero diff);
  `python3 sdd_doc_lint/chg_lint.py <chg>` clean;
  `python3 tests/chg/spec_gate.py --base origin/dev` clean (this script
  checks the VERSION bump only — GATE-SPEC approval itself is the recorded
  human sign-off); `python3 -m pytest tests/conformance -q` green.
- Full offline link check over all changed files
  (`lychee --config .lychee.toml --offline --no-progress <changed-files>`);
  PR watched until required checks settle; no merge while red;
  no `--no-verify`.

## Risks / Open Questions

- **Emitter cost is the swing item.** Even with `render_spec_sheet` reuse,
  the splice emitter plus schema may exceed one block's value. The Phase 1
  gate forces that call before the spend.
- **YAML comment loss.** Parsers drop comments; some guards check them as
  raw text. Mitigation: `_guidance` fields plus the Phase 0 guard inventory;
  un-migratable facts stay in Markdown.
- **Authoring friction under high churn.** If pilot authors report slower
  edits exceeding the drift saving, stop at Phase 3 entry.
- **Open question — blocks Phase 2b:** whether YAML beats structured
  Markdown on the frozen benchmark (Claim 7).

## Out of scope

Bulk MD→YAML conversion; whole-document conversion of any mixed
prose/diagram document; governance doc-as-graph; generating agreement
projections outside the pilot host document; converting `DECISIONS.md`,
playbooks, layer READMEs, or `framework/archive/`; layer instance formats
(governed separately by GD-17's effective condition); any new external
dependency, service, or deployment.

## Claim ledger

| # | Claim | Symbol | Citation |
| --- | --- | --- | --- |
| 1 | YAML-first Principle 2 governs layers 1–10 and explicitly exempts governance surfaces | `YAML is the mandatory format` | framework/governance/DOC_GOVERNANCE_CORE.md:16 |
| 2 | The lint catalog guard checks agreement both ways between the Markdown catalog and linter ID sets | `single source of truth` | tests/conformance/test_lint_catalog.py:3 |
| 3 | GD-17 decides the single source for layer instance format and its effective condition; it gives no rationale for the governance exemption | `GD-17` | framework/governance/DECISIONS.md:2209 |
| 4 | The slicer accepts element headings and drops non-`TYPE-NN` documents, so governance files are not served today | `_MD_HEADING_ELEM` | sdd_doc_lint/slice.py:44 |
| 5 | The property-graph engine is a separate system with a hardcoded closed node-type set | `NODE_TYPES` | sdd_doc_lint/graph_engine.py:18 |
| 6 | The SDD graph schema closes node-type and ID-pattern enumerations to layer artifacts | `seed_intent` | framework/governance/sdd-graph.schema.json:56 |
| 7 | YAML superiority over structured Markdown on agent tasks — **blocks Phase 2b** | `n/a` | PROBE: run the Phase 1 frozen three-arm benchmark (isolated arms, ≥30 exact-match tasks, majority vote over 3 repeats) and compare percentage-point accuracy and tokens against the pre-registered gate |
| 8 | Version bump propagates via the sync script's `OLD_VERSIONS` list, which must first gain the prior version | `OLD_VERSIONS` | hooks/sync-version-refs.sh:128 |
| 9 | NEW@pass1 — a Markdown renderer already exists for SDD graphs and must be evaluated before building a new emitter | `render_spec_sheet` | sdd_doc_lint/observability_adapter.py:22 |
| 10 | NEW@pass1 — conformance asserts the exact governance file set, so any new pilot file must update that guard in the same PR | `test_no_unexpected_files` | tests/conformance/test_governance.py:158 |
| 11 | NEW@pass2 — the controlling precedent for framework self-changes is DIR2C + `spec` + GATE-SPEC + C2 + patch | `change_source` | framework/archive/CHG-74/CHG-74.yaml:33 |
| 12 | NEW@pass2 — IPLAN creation for a `spec`-sourced change with zero `sdd_lifecycle` steps is a CHG-L005 error | `_sdd_lifecycle_steps` | sdd_doc_lint/chg_lint.py:345 |

## Review log

### Pass 1 - 2026-10-25 - independent

- GD-17 is not the exemption rationale → Claim 3 corrected; Phase 0 now
  searches provenance and records absence instead of retrieving a rationale.
- Slicer cannot serve governance files (heading grammar + `TYPE-NN` filter)
  → Phase 2a extension is certain work; Phase 1 gains slicer-query tasks;
  Claim 5 separated as the distinct graph engine.
- Phase 1 tested one section but Phase 2b converted a whole document →
  conversion redefined per fact-block with an in-place splice; projections
  stay test-validated in the pilot; `spec` route added to benchmark tasks.
- "No generator exists" was false → Claim 9 (NEW@pass1) added; Phase 2b
  evaluates `render_spec_sheet` before building the splice emitter.
- Vehicles underspecified vs GATE-SPEC → every phase now states its full
  classification tuple; Phase 1 evidence is committed, not scratch; any
  `framework/` edit triggers the bump; human sign-off and security review
  named; `OLD_VERSIONS` append made explicit via Claim 8.
- Benchmark could not settle its probe → probe re-scoped to benchmark
  superiority; frozen task set, isolation, rubric, repeats, percentage-point
  threshold, and accuracy floor specified.
- Exact-file-set guard unaddressed → Claim 10 (NEW@pass1); guard update is a
  Phase 2b step.
- `_guidance` precedent mis-cited → corrected to the layer-template
  convention; comment-checking guards inventoried in Phase 0.
- Phase 2a syntax unspecified; bare `python3 -m sdd_doc_lint` is a usage
  error → syntax note is the first Phase 2a deliverable with FM01-safe
  field restrictions; validation command now carries its path argument.
- Internal contradictions (discursive treatment, graph scope, "Phase 2"
  citation, rollback reusing a published version, anchor spot-check vs
  full-resolve criterion, unledgered counts) → each narrowed or deleted
  subtractively; rollback is forward-only; anchor validation is a full
  check; churn and file-count figures removed as load-bearing prose.

### Pass 2 - 2026-10-26 - independent

- F1: spec-sourced CHGs need `sdd_lifecycle` or fail CHG-L005 → all spec
  phases now ride the CHG-74 precedent (Claims 11–12, NEW@pass2); the
  "empty lifecycle" shorthand flagged as a pre-commit trap; the SEED2C
  router tension recorded with the precedent named as controlling. SC6
  split per source: full tuple for `spec`, no-SemVer tuple for `direct` C1s.
- F2: Phase 2a omitted security review → added, matching SC6.
- F3: gate ambiguous on floor scope, equality tolerance, repeat
  aggregation → floor binds both arms with an inconclusive-below-90% exit;
  ±2pp equality band; majority vote; percentage-point units.
- F4: Phase 3 entry undefined → three-part entry rubric (green pilot,
  reproduced benefit, author-time bound); non-entry ends the plan.
- F5: Claim 2 overclaimed generation precedent → body now states agreement
  checking only; bidirectional facts need a new agreement test, and there
  is no generation precedent.
- F6: retrieval steps promised but ungated → measured and reported,
  gate stays accuracy/tokens.
- Minors folded: "(Claim 4)" singular; lychee and schema-validate commands
  named; renderer domain-lock risk recorded; Claim 4 note on bold-prefixed
  element items accepted (conclusion unchanged).

### Pass 3 - 2026-10-26 - independent

- All 12 ledger rows verified true in context; Pass 2 folds F1–F6 confirmed
  present and correctly worded in the body; claim refs, vehicle tuples, and
  validation commands internally consistent.
- Non-blocking observations (no body change): Claim 4 wording omits the
  bold-prefixed element form (conclusion unchanged); Phase 3 entry
  condition 3 needs a measurement definition in the executing IPLAN;
  `sdd_doc_lint` on a non-layer path exits 0-skipped (conformance suite
  and slicer smoke remain the real guards); two SC6 phrasing imprecisions
  noted (archive-tier records, one-directional major⇒C3).

**Result:** ready — no further findings.
