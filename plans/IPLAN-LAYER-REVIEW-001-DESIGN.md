# IPLAN-LAYER-REVIEW-001 Design — Layer 8 execution fidelity and OKF conformance under a YAML-normative format

| Field          | Value                                                          |
| -------------- | -------------------------------------------------------------- |
| Task           | IPLAN-LAYER-REVIEW-001                                           |
| Type           | design (feeds a separate implementation plan)                    |
| Status         | Draft — 2026-08-26; amended 2026-08-27 (A2 discarded)            |
| Review cycles  | **0** — no gap-review pass has run against this draft            |
| Depends on     | `plans/OKF-CONFORMANCE-001-DESIGN.md` (Draft; owns D1 contract)  |
| Feeds          | `plans/IPLAN-LAYER-REVIEW-001-PLAN.md` (not yet written)         |
| Version impact | framework MINOR + plugin MINOR; see "Version impact"             |

## Objective

Two problems in Layer 8, recorded together because their fixes touch the same
files:

1. **Execution fidelity.** An IPLAN cannot be shown to implement every upstream
   requirement. The element-level trace chain that runs BRD → TDD stops at TDD;
   nothing binds a TDD test case to an IPLAN, and nothing binds an IPLAN to code.
   A dropped requirement is invisible at every gate from L8 to merge.
2. **OKF conformance.** Google Cloud's Open Knowledge Format v0.2 addresses `.md`
   files. Layer 8 is authored in YAML, carries no frontmatter contract, and
   asserts its relationships as `@`-tag scalars rather than markdown links, so an
   OKF reader sees no IPLAN concepts at all.

## Format decision (F-0) — normative, founder-set 2026-08-26

**YAML is the mandatory format and the source of truth. Markdown is optional and
descriptive** — a rendering of the YAML, or additional explanatory material
around it. Markdown never carries a fact the YAML does not.

This resolves `OKF-CONFORMANCE-001-DESIGN.md` open question 1 with an answer that
document did not list. Its two options were "declare markdown mandatory for
OKF-conformant trees" or "declare those three layers outside the bundle". F-0 is
a third: **YAML normative, with a generated `.md` projection that is the OKF
concept.** Every OKF decision below follows from F-0, and the recommendation in
this repository's earlier review round — move IPLAN to markdown — is withdrawn.

## Scope

**In:**

- Element-level TDD → IPLAN coverage, and a work unit that can carry acceptance.
- The IPLAN template set: `IPLAN-TEMPLATE.yaml`, `IPLAN-MVP-TEMPLATE.yaml`,
  `IPLAN-00_index.TEMPLATE.yaml`, and the layer README.
- The IPLAN review crew (`framework/playbooks/08_IPLAN/`) for the `code_build`
  subtype.
- The fields the YAML must carry so an OKF `.md` projection is a pure function of
  it, and the projection generator plus its drift guard.
- The IPLAN-specific rows the frontmatter contract (OKF D1) must hold.

**Out of scope (one line each, not designed here):**

- The frontmatter contract itself — `OKF-CONFORMANCE-001-DESIGN.md` D1 owns it.
- The five `status` vocabularies — deferred whole by OKF D4; not created here.
- OKF trust (`generated`, `verified`) and provenance (`sources`) families.
- `okf_version`, a bundle-root `docs/index.md`, and `stale_after`.
- The `.md` projection for layers 1-7 — the same mechanism, different owner.
- Reconciling the framework L8 shape with iplanic's 13-section standard beyond
  keeping a normalization path open.
- Retiring `custom_fields.document_type`.

## Corrected baseline

Every row was measured this session against the working tree at
`framework/VERSION` 0.42.0.

| Fact | Evidence |
| --- | --- |
| `REALIZING_LAYERS` has entries for BDD, EARS, BRD only — **no IPLAN key** | `tools/sdd_doc_lint/__init__.py:2162-2166` |
| `COV01`'s IPLAN leg is document-level and transitive: one IPLAN anywhere downstream of the host BRD satisfies every FR in it | `tools/sdd_doc_lint/__init__.py:2044`, `_doc_forward_reach` |
| Corpus `TDD-01` declares **35** test-case elements; `IPLAN-01` **cites 7** of them in the trace graph and **mentions 26** as bare backticked text — so a graph-based check reports **28** uncovered, not 9 | `build_edge_graph` over `examples/url-shortener/docs/`; corrected 2026-08-26 |
| A trace edge requires a literal `@<layer>:` token — a bare element id in a table cell produces **no edge**, which is why the text-grep figure and the graph figure differ | `tools/sdd_doc_lint/trace_graph.py:32` |
| The corpus IPLAN's §6 Traceability carries **one bullet with five `@tdd:` tokens** called "representative anchors" for the 35-case contract — a document-scoped coverage check is silenced by expanding that single line | `examples/url-shortener/docs/08_IPLAN/IPLAN-01.md:288` |
| That IPLAN audited **PASS, 100/100, 6/6 lenses, 0 blocking findings** | `examples/url-shortener/.aidoc/audit/08_IPLAN-audit.md` |
| The corpus IPLAN cites `@ears` **0** times and `@bdd` **0** times — correct per `can_reference`, but unchecked | `examples/url-shortener/docs/08_IPLAN/IPLAN-01.md` |
| **All 30** lens checks across the six IPLAN playbooks are deploy-oriented; none addresses `code_build` | `framework/playbooks/08_IPLAN/*.md`, grep of `**C[0-9]` |
| `STRUCT01` **skips** every section carrying `_required_when_subtype:`; 9 of IPLAN's 11 sections carry it, leaving a deterministic floor of **2** | `tools/sdd_doc_lint/__init__.py:535` |
| `IPLAN-TEMPLATE.yaml` declares `total_sections: 6` with **11** top-level sections; header numbering skips 7 (6 → 8) | `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:16`, `:228` |
| `IPLAN-TEMPLATE.yaml` has **no** `artifact_type`, **no** `title`, **no** `glossary` (`grep -c glossary` → 0) | same file |
| `IPLAN-MVP-TEMPLATE.yaml` has **no `metadata:` block at all**; carries `title` and `glossary` the main template lacks | `framework/layers/08_IPLAN/IPLAN-MVP-TEMPLATE.yaml` |
| `IPLAN-01_golden.yaml` has one **leading** `---` (a YAML document-start marker, not a frontmatter fence), **0** `artifact_type`, and **6** `## Heading` lines that are YAML **comments** | `tests/acceptance/fixtures/layer_08_iplan/valid/IPLAN-01_golden.yaml` |
| `LAYER_REGISTRY.yaml` declares `extensions: [.yaml]` for **all eight** layers, not three | lines 24, 37, 50, 70, 83, 96, 109, 122 |
| The corpus ships **all `.md`**; the acceptance goldens are **mixed** (5 `.md`, 3 `.yaml`) — a three-way disagreement with the registry | `examples/`, `tests/acceptance/fixtures/` |
| IPLAN and BRD are the only two layers whose README mandates a **slug** in the filename | `08_IPLAN/README.md`, `01_BRD/README.md` |
| iplanic models work as `step → work_order → todo` with **TODO-level acceptance criteria** | `iplanic/docs/standards/IPLAN-STANDARD.md:112-115` |
| `realizing_layers` is **hard-pinned by exact equality** in a conformance test, and the registry warns that mutating it re-grades every consumer corpus. `acceptance_layers` was added as an **additive sibling** rather than mutating it | `tests/conformance/test_acceptance_pairing.py:169-172`; `LAYER_REGISTRY.yaml:236-238` |

## Part A — Execution fidelity

### A1 — No element-level TDD → IPLAN coverage rule (P0)

Element-level realization is enforced BRD → PRD (`COV01`), EARS/BDD → SPEC/TDD
(`COV02`), and BDD scenario → TDD test case (`ACC01`). It then stops. `REALIZING_LAYERS`
has no IPLAN key, so no rule asks whether a TDD test case reached an IPLAN, and
none asks whether a SPEC contract did — IPLAN cites SPEC at document level
(`@spec: SPEC-NN`) by design.

`COV01`'s IPLAN leg does not close this. It is document-level and transitive: the
host BRD's forward reach is computed once, and any IPLAN in that reach marks
every one of the BRD's FRs as built.

**Measured impact (corrected 2026-08-26).** Round-1 review reported "9 of 35 cited
nowhere" from a text grep. That figure counted *mentions*. The trace graph records
an edge only from a literal `@<layer>:` token, so the machine-visible state is
**7 of 35 cited, 28 uncovered** — the defect is materially worse than first
reported. Both numbers are true about different things: 26 case ids appear as
backticked text, 7 are cited. The audit returned PASS at 100/100 with 0 blocking
findings either way.

**A second-order trap, found in plan review.** A coverage check built on the
document-scoped realization primitive would be silenceable by one line: the
corpus IPLAN's §6 Traceability already carries five `@tdd:` tokens labelled
"representative anchors", and expanding that bullet to 35 would satisfy such a
check without changing what the IPLAN builds. `ACC01` documents this same
vacuous-pass loophole for BDD scenarios and closes it with a carrier co-location
parse. `COV04` must do the same — see `plans/IPLAN-TDDREF-001-PLAN.md` and its successor `IPLAN-COV04-002`.

**Failure mode:** a test never authored is never red. The gap does not surface at
GATE-CODE (A6).

**Implementation constraint:** `realizing_layers` cannot simply gain an IPLAN
key. `tests/conformance/test_acceptance_pairing.py:169-172` pins the block by
exact equality, and `LAYER_REGISTRY.yaml:236-238` records that mutating it breaks
a second pinned assertion in `tests/conformance/test_coverage_engine.py` and
re-grades every consumer corpus. `ACC01` faced the same constraint and resolved
it by adding `acceptance_layers` as an additive sibling. `COV04` follows that
precedent (R1).

### A2 — DISCARDED 2026-08-27 (founder decision): per-requirement work unit

**Withdrawn, with the reasoning, so it is not re-derived from the same observation.**

The finding was that `file_manifest.files[]` (`framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:102-108`)
carries one `status`/`verified` per **file**, while a file realizes many test cases — so the structure cannot say which
cases in a file are done, and `partial_work` carries mid-file state as prose.

The observation is accurate. It is not a defect the framework needs to fix:

- **No consumer observes the imprecision.** The linter never reads `file_manifest`;
  Hermes' validator checks only that the fields exist and that `status` is one of four
  strings (`platforms/hermes/src/mcp_server/validation/iplan_rules.py:70,83`) and never
  acts on the value. Nothing else reads `status` or `verified`.
- **The ecosystem argument ran the wrong way.** `IPLAN-ECOSYSTEM.md` recommends
  **option 2** — L8 stays canonical for *authoring* and iplanic imports into its richer
  `step → work_order → todo` model. Adding tasks to L8 moves toward option 1, which that
  document declined. The original draft cited it as support; it is the opposite.
- **`tdd_ref` (GD-16) removed the need.** An importer now has the (file → test case)
  mapping, so a todo per pair is derivable at the boundary that owns execution.
- **It was speculative scope** by this repo's own test: no named issue, no consumer
  friction, discovered by reading the template rather than by use.

**What would reopen it:** a consumer whose executor needs per-case completion state in
the *authored* artifact, or a measured case where prose `partial_work` loses a session's
progress. **Open a GitHub issue on this repo** — per `CLAUDE.md` § "Own-repo gaps", which retired
the Tier-1/Tier-2 split for repository-owned gaps. Do not re-derive the asymmetry as a
fresh finding; cite this tombstone and `plans/DECISIONS.md` D-0077.

### A3 — The review crew has no `code_build` checks (P1)

| Lens | Weight | Check subject |
| --- | --- | --- |
| tech_lead | 30 | rollback pairing, cutover thresholds, phase pre/post-conditions |
| architect | 25 | deploy topology vs ADR, new infrastructure, DAG order, NFR capacity |
| operator | 15 | smoke tests, canary thresholds, observability, runbook |
| integration_lead | 12 | contract pinning, flag defaults, backward-compatibility window |
| auditor | 10 | trace and ID conformance |
| chaos_engineer | 8 | rollback dress rehearsal |

All 30 checks address deploy. None asks whether the file manifest covers the TDD,
whether the implementation contracts cover the SPEC interfaces, whether the
execution commands are expressible in the `@spec` toolchain, or whether the
Red/Green gate is present. `integration_lead.md:63-68` explicitly authorizes
`lens_score: 100` with `findings: []` for the `code_build` subtype.

`code_build` is the `IPLAN-MVP-TEMPLATE.yaml` default and the subtype that
produces source code. It is reviewed by a crew where 82 of 100 weight points have
no applicable check.

### A4 — The deterministic floor is two sections (P1)

`_load_section_targets` skips any section whose body carries
`_required_when_subtype:`, deferring the subtype-aware check to the layer audit
SKILL. Nine of IPLAN's eleven sections carry that marker, so `STRUCT01` enforces
the presence of `document_control` and `traceability` only. `file_manifest`,
`execution_commands`, `session_handoff`, and all five deploy sections are
enforced solely by an LLM reading prose instructions.

### A5 — GATE-08-E001 names completeness with no mechanism (P2)

`GATE-08-E001` blocks on "IPLAN must have complete file manifest", validated as
"File list matches SPEC component scope". The requirement is correct. Nothing
implements it, and no lens check corresponds to it.

### A6 — GATE-CODE does not close the gap (P2)

`GATE-CODE-E003` is "Code must pass TDD test suite / Test suite green". A TDD
case the IPLAN never listed is never authored as a test, so the suite is green.
The dropped requirement is invisible from L8 through merge.

## Part B — Template and contract defects

| ID | Defect | Evidence |
| --- | --- | --- |
| B1 | `auditor.md` C1 demands `@spec: SPEC.NN…` element form against a template mandating `SPEC-NN`; C2 demands every step ID match `IPLAN.NN.SS.xxxx`, which `doc-iplan/SKILL.md` forbids outright; C3 requires a "deployment-step matrix at the top of the IPLAN" present in no template | `framework/playbooks/08_IPLAN/auditor.md:59,65,71` |
| B2 | `glossary` is listed as a required section for both subtypes, but no glossary exists in `IPLAN-TEMPLATE.yaml`; the same skill's step 1 enumerates required sections *from* that template | `doc-iplan-audit/SKILL.md:372,376` |
| B3 | The Structure check is satisfied only when each section "appears as a `##` heading" — applied to a YAML artifact | `doc-iplan-audit/SKILL.md:382` |
| B4 | The autopilot's linear pipeline instructs cumulative tags `@brd @prd @ears @bdd @adr @spec @tdd`, contradicting `doc-iplan/SKILL.md` and `can_reference: [SPEC, TDD]`; the same step says "all 6 sections" against the 11-section subtype model | `doc-iplan-autopilot/SKILL.md:142` |
| B5 | `total_sections: 6` with 11 sections; header numbering skips Section 7 while the SKILL calls the same five sections 7-11 | `IPLAN-TEMPLATE.yaml:16`, `:228`; `doc-iplan/SKILL.md` |
| B6 | MVP template drift: `IPLAN-001` vs `IPLAN-NN`; `document_type: "iplan"` vs `iplan-document`; `status: "draft"` vs `Draft`; `file_manifest` as a bare list vs `{files: [...]}`; an unrelated `traceability.upstream` shape; carries `title` and `glossary` the main template lacks; no `metadata:` block at all | `IPLAN-MVP-TEMPLATE.yaml` |
| B7 | `document_control` and `traceability` carry no `_required_when_subtype:` marker, so "every section with any marker" enumerates 9; the audit SKILL hardcodes the other two by name. The marker mechanism does not cover the section set it is described as selecting | `IPLAN-TEMPLATE.yaml:42,198`; `doc-iplan-audit/SKILL.md:372` |
| B8 | The registry declares layer 8 `.yaml` while the corpus ships `.md` and the goldens ship `.yaml` | `LAYER_REGISTRY.yaml:122` |

B1 is the most consequential: the lens whose entire subject is trace conformance
scores against a document shape the framework does not define, and it returned
100 on the corpus.

## Part C — OKF conformance under F-0

OKF v0.2 conformance is three rules: every non-reserved `.md` carries parseable
YAML frontmatter; every frontmatter carries a non-empty `type`; reserved
filenames (`index.md`, `log.md`) follow their structure when present. Concept ID
is the file path minus `.md`. Markdown links assert relationships.

### C1 — A YAML-normative tree is conformant and empty

OKF constrains `.md` files and ignores everything else, so a `docs/08_IPLAN/`
holding only `.yaml` violates no rule and contributes **zero concepts**. Under
F-0 the YAML cannot itself become the OKF surface. Conformance therefore requires
a **`.md` projection per IPLAN**, which is the OKF concept, while the YAML remains
the source of truth.

### C2 — The projection must be generated and drift-guarded

A hand-authored projection is a second record of the same truth, which this
repository has already measured failing twice (the retired `FRAMEWORK-TODO.md`
queue against the issue tracker; the plugin and framework version tokens against
`CLAUDE.md`). `CLAUDE.md` additionally forbids hand-editing example artifacts.

The projection must therefore be produced by a generator and verified by a drift
guard. Both patterns exist in-repo and are reuse, not authoring:
`tools/sdd_coverage.py` writes `TRACEABILITY_MATRIX.md`; the
`tools/sync-plugin-framework.sh` plus `test_plugin_framework_bundle.py` pair is
the mirror-and-guard shape.

### C3 — The YAML template cannot currently source an OKF frontmatter block

The projection's frontmatter must be a pure function of the YAML, or the
generator invents values and they drift. `IPLAN-TEMPLATE.yaml` carries
`metadata.document_type: "iplan-document"` and `document_control.iplan_id` but
**no `artifact_type` and no `title`**. `IPLAN-MVP-TEMPLATE.yaml` carries `title`
and no `metadata:` block.

The OKF-facing key `type` **never enters the YAML**. It is a projection-only
field, emitted alongside `artifact_type` per OKF D2's mirroring rule. This keeps
format-specific keys out of the source of truth.

### C4 — Relationships do not survive the projection

OKF asserts relationships through markdown links. IPLAN's entire upstream lineage
is `@spec:` and `@tdd:` scalars inside YAML. `OKF-CONFORMANCE-001-DESIGN.md`
defers markdown-link projection of the `@`-tag graph to a successor.

For seven layers that deferral is cosmetic. For IPLAN it is not: IPLAN is the
terminal document layer, so an OKF reader would receive an IPLAN concept with
**zero outbound relationships**, and — combined with A1 — the OKF projection of
the SDD graph terminates at TDD with the layer that names the delivered files
hanging unlinked. A minimal `@spec` / `@tdd` link projection is in scope here even
though the general case is not.

### C5 — Concept identity is coupled to the filename slug

Concept ID is path minus `.md`, so `IPLAN-NN_{slug}` puts the slug in the
identity. IPLAN and BRD are the only layers whose README mandates a slug. The
README fixes `NN` as never-reused and says nothing about slug stability, so a
rename silently reassigns the concept and breaks every inbound link.

The contract must declare the slug immutable once assigned, on the same footing
as the number.

### C6 — `tmp/` produces disappearing concepts

`TMP-IPLAN-YYYY-MM-DD_{slug}` puts a date in the concept ID, and the README
mandates deletion within 7 days of DONE or ABANDONED. IPLAN is the only layer
with a disposable-document class, so no other layer surfaces this. Recommended:
exclude `tmp/` from the bundle explicitly, as OKF D3 already excludes `.aidoc/`.

### C7 — The index is a distinct schema needing its own type

`IPLAN-00_index.yaml` is `document_type: iplan-registry`, carries no
`document_control`, and declares no element IDs. Its projection would be
`IPLAN-00_index.md`, which is **not** OKF's reserved `index.md`, so rule 3 does
not bind — but it still needs a non-empty `type`, and OKF D3's open question 3
(`<X>-INDEX` versus the bare artifact name) decides which. IPLAN's index is the
only one that is both `.yaml` and a genuinely different schema.

### C8 — The golden is shaped for a check that should not apply to it

`IPLAN-01_golden.yaml` has the right extension under F-0. Its problems are
elsewhere: the leading `---` is a YAML document-start marker rather than a
frontmatter fence, there is no `artifact_type` at any level, and six
`## Heading` lines are YAML **comments** imitating markdown headings. Those
comment-headings exist only to satisfy B3. Removing B3 removes their reason to
exist.

### C9 — The corpus is inverted with respect to F-0

`examples/url-shortener/docs/` is entirely `.md` with no `.yaml` sources, so
today the corpus treats markdown as the source of truth. Under F-0 this is
backwards. Per `CLAUDE.md`, correct it by regeneration, never by hand-editing the
artifacts.

## Corrections to OKF-CONFORMANCE-001-DESIGN

| # | Correction |
| --- | --- |
| 1 | Open question 1 states that "SPEC, TDD and IPLAN goldens are `.yaml`". The **registry** declares `extensions: [.yaml]` for **all eight** layers. Per the normative surface the whole bundle is vacuous, not three layers of it; the baseline row measured the goldens, not the registry |
| 2 | The format state is a **three-way** disagreement, not a split: registry all-`.yaml`, goldens mixed 5 `.md` + 3 `.yaml`, corpus all-`.md`. Any resolution moves two of the three |
| 3 | Open question 1 is resolved by F-0 with an option the document did not list — YAML normative plus a generated `.md` projection |
| 4 | Stage 1's "`type` into the 26 templates" is wrong under F-0. Templates receive `artifact_type` and `title`; `type` goes into the projection generator and never into the YAML |
| 5 | `tmp/` is uncovered by the design. It is IPLAN-only and produces concepts that are deleted on a 7-day rule |
| 6 | The risk table needs a projection-drift row: templates declare the source fields, the generator emits the concept, and nothing yet detects a stale projection |
| 7 | `OKF02` ("frontmatter parseable on every non-reserved `.md`") becomes a check on **generated** files for layers authored in YAML. Its fixture set must include a projection, not only a hand-authored artifact |

## Recommendations

Ordered so each step is usable on its own. Complexity is 1 (minimal config) to 5
(architectural).

| ID | Change | Addresses | Complexity |
| --- | --- | --- | --- |
| R1 | Ship `COV04`: every TDD test-case element is cited element-level by at least one IPLAN. Gate on corpus-has-IPLAN as `COV01` does; warning in `build`, error in `gate-code`. **Do not mutate `realizing_layers`** — add an additive sibling block (`building_layers: {TDD: [IPLAN]}`) following the `acceptance_layers` precedent, with the same registry-versus-constant sync guard | A1 | 3 |
| R2 | **Amended 2026-08-26.** Add a line-local `tdd_ref:` field to the existing `file_manifest.files[]` entries — a key whose *value* is the `@tdd:` tag, mirroring `bdd_ref`. The first draft proposed a top-level `coverage_map:` block; three review passes established a block header is invisible to a line-local matcher and that the nested field reddens no golden and moves no section count. Owned by `IPLAN-TDDREF-001` | A1, A5 | 1 |
| R3 | *(VOID — A2 discarded 2026-08-27; see the A2 tombstone. Row retained so R-numbering stays stable, matching F-3)* | — | — |
| R4 | *(VOID — A2 discarded 2026-08-27; see the A2 tombstone)* | — | — |
| R5 | Author `code_build` checks for tech_lead, architect and integration_lead — manifest-versus-TDD completeness, contracts-versus-SPEC-interfaces completeness, Red/Green gate presence, execution commands expressible in the `@spec` toolchain — or introduce a separate `code_build` crew | A3 | 4 |
| R6 | Rewrite `auditor.md` C1-C3 against the actual IPLAN contract: dash-form document IDs, no dotted element IDs, no deployment-step matrix | B1 | 2 |
| R7 | Make `STRUCT01` read `document_control.subtype` and enforce the matching section set deterministically, rather than deferring the whole set to a SKILL; add the missing markers to `document_control` and `traceability` | A4, B7 | 3 |
| R8 | Add `artifact_type: IPLAN` and `title` to `IPLAN-TEMPLATE.yaml`'s `metadata:`, per the OKF D1 contract. Do **not** add `type` | C3 | 1 |
| R9 | Reconcile `IPLAN-MVP-TEMPLATE.yaml` with the main template: add the `metadata:` block, fix the ID width, `document_type`, `status` casing, `file_manifest` shape and `traceability` shape | B6, C3 | 2 |
| R10 | Build the `.md` projection generator plus its drift guard **across layers 1-8** (F-1), emitting projections **beside their sources** with a generated-file header (F-2) and rendering `@`-tags as markdown links so concepts are not link-isolated | C1, C2, C4 | 5 |
| R11 | Fix `LAYER_REGISTRY.yaml` extensions to match F-0 and the projection, and drop the `##`-heading language from `doc-iplan-audit/SKILL.md`, the `glossary` requirement, the autopilot's cumulative-tag line, `total_sections`, and the Section 7 gap. Remove the golden's comment-headings and add its `artifact_type` and `title` | B2, B3, B4, B5, B8, C8 | 2 |
| R12 | Add the IPLAN-specific rows to the frontmatter contract: slug immutability, `tmp/` exclusion, and a statement that `file_manifest` paths and `code_inventory` entries are opaque values rather than concept references. The index type form defers to OKF D3 (F-4) | C5, C6, C7 | 1 |

R1 and R2 are the pair that would have caught all 28 uncovered test cases. R10 cannot
start before the OKF D1 contract exists, and under F-1 it is framework-wide rather
than IPLAN-scoped. R12's index row waits on OKF D3; its other three rows do not.

## Resolved decisions (founder, 2026-08-26)

The four questions this design opened are answered. Each is normative for the
implementation plan.

### F-1 — The projection covers all eight layers

Not IPLAN alone. A single-layer projection would emit IPLAN concepts pointing at
SPEC and TDD concepts that do not exist; OKF tolerates broken links, but shipping
them by construction is not the intent. R10 therefore widens: one generator over
layers 1-8, and the OKF concept graph is complete on first delivery.

**Effect on scope.** The projection generator leaves this design's IPLAN-only
boundary and becomes framework-wide. It is still the same mechanism, so it stays
one work item, but its owner is arguably `OKF-CONFORMANCE-001` rather than this
design — see "Docs to update".

### F-2 — The projection lives beside its source

`IPLAN-01_{slug}.yaml` and `IPLAN-01_{slug}.md` sit together in `docs/08_IPLAN/`.
The OKF concept ID then equals the authored path minus `.md`, the bundle root is
`docs/`, and inter-layer links are plain relative paths.

**Required consequence.** Generated files now share a directory with authored
ones, so each projection carries a generated-file header naming its source and
the generator. Without it, the "never hand-edit" rule has no visible carrier at
the point of editing.

### F-3 — VOID (A2 discarded 2026-08-27)

Resolved the nesting shape for a `tasks[]` block that is no longer proposed. Retained
only so the numbering of F-1/F-2/F-4 stays stable.

### F-4 — The index type form follows OKF D3

`IPLAN-00_index` takes whatever form D3 settles for the index class rather than
being decided here, so one rule governs all nine indexes. This design records the
dependency and stops. R12 drops the index-type row and gains a pointer.

**Sequencing consequence:** R12 cannot fully land before OKF D3's open question 3
is answered. Its other three rows (slug immutability, `tmp/` exclusion, code
paths as opaque values) are independent and can land first.

### Design inputs carried forward to `IPLAN-COV04-002`

Two independent review passes over the first `COV04` draft produced facts the rule
must be built on. They are recorded here so the successor plan does not re-derive
them:

- **The rule must be carrier-scoped, not document-scoped.** `_element_realizing_citers`
  returns citer *documents*; `ACC01`'s source rejects it for this exact shape, and the
  corpus §6 traceability bullet is a live instance of the loophole.
- **The corpus delta must be re-derived under the carrier predicate.** The figure 28
  measured the rejected document-scoped primitive. Under a carrier rule the corpus
  currently satisfies nothing, because it carries no `path:` keys and no `tdd_ref` field.
- **Activation is per TDD document, via `citers_of_doc` filtered to IPLAN** — not
  `doc_layer`, which answers only which docs exist, and not a corpus-wide gate, which
  over-fires on a one-IPLAN-per-component layer. IPLAN's `required_tags: [spec, tdd]`
  plus `TAG01` is the backstop that stops evasion-by-omission.
- **Findings anchor on the host TDD**, as `COV02`/`ACC01` do, so acceptance-manifest
  entries take the TDD's path, not the IPLAN's.
- **`fullpath/golden_chain` cannot both carry a covering carrier and pin new findings.**
  Whichever is intended must be stated. `IPLAN-TDDREF-001` Phase B chooses covering.
- **The broken fixture is a TDD+IPLAN pair with its own `*_drift_codes.yaml`**, and its
  IPLAN must cite doc-level so the TDD activates while carrying no carrier-borne
  element citation.

## Staging — which plan owns what

R1-R12 are not one change. Each stage below is a separate plan that must clear its
own gap-review cycles before its PR opens. Only Stage 1 is drafted.

| Stage | Owns | Plan | State |
| --- | --- | --- | --- |
| 0 | The `_TAG` quote-termination fix — a prerequisite discovered in review; without it a quoted `@tdd:` tag is silently discarded from the trace graph | `plans/LINT-TAG-QUOTE-001-PLAN.md` | **IMPLEMENTED** 2026-08-26 — suites green, blast radius zero as predicted. Issue #542 |
| 1a | R2 — the `tdd_ref` line-local carrier | `plans/IPLAN-TDDREF-001-PLAN.md` | **IMPLEMENTED** 2026-08-26 — GD-16; guarded by `tests/conformance/test_iplan_carrier.py`. **Shipped in framework `0.43.0`** as GD-16 (`272d964d`, PR #549) — the bump was NOT withheld |
| 1b | R1 — the `COV04` rule | `IPLAN-COV04-002`, not written | blocked on 1a. **Founder decision 2026-08-26: Stages 1a and 1b ship as separate PRs**, accepting a second framework MINOR + fanout (`LINT_RULES.md` is a `framework/` path) |
| 2 | *(vacated — A2 discarded 2026-08-27; see the A2 tombstone)* | — | **VACATED** — no successor planned |
| 3 | R5, R6 — `code_build` lens checks, `auditor.md` rewrite | not written | independent of Stage 1 |
| 4 | R7, R11 — subtype-aware `STRUCT01`, the consistency fixes (`total_sections`, Section 7 gap, `glossary`, `##`-heading, autopilot tags, registry extensions) | not written | independent |
| 5 | R8, R9, R10, R12 — OKF template fields, MVP reconciliation, the layers 1-8 projection generator, contract rows | not written | blocked on `OKF-CONFORMANCE-001` D1; R12's index row also on D3 |

**Stage 4 absorbs `total_sections`**, which Stage 1 carried in an early draft and
cut: it is read by no code relevant to `COV04`. The nested-`tdd_ref` shape adds no
`# Section N:` header, so the count stays **11** and the skill/template alignment guard
is untouched — the value **12** applied only to the abandoned `coverage_map` block.

## Version impact

Framework **MINOR** — new lint rule, additive template keys, new governance rows,
playbook rewrites. Plugin **MINOR** — the audit and autopilot SKILLs change, and
per `CLAUDE.md` a plugin bump is a roughly 60-file fanout requiring founder OK.
`GATE-SPEC-E005` applies (version bump plus fanout), and a GD entry in
`framework/governance/DECISIONS.md` is warranted for F-0 and for `COV04`.

Every recommendation touches `framework/**`, so this design must reach an
implementation plan that clears at least two full gap-review cycles plus the
example-corpus cross-check before its PR opens.

## Verification

- `python3 -m sdd_doc_lint examples/url-shortener/docs/` against a **pinned
  expected delta**, not "zero unexpected findings". `COV04` on the current corpus
  produces 28 findings by construction; the corpus is regenerated wholesale after
  framework changes, so the delta is the measurement, not the count.
- A conformance test asserting the new additive block and its `sdd_doc_lint`
  constant stay in sync, mirroring the existing `ACCEPTANCE_LAYERS` guard. The
  `realizing_layers` exact-equality pin must stay green **unchanged** — if a
  change makes it fail, the design has mutated the wrong block.
- `tests/conformance/platforms/test_plugin_framework_bundle.py` stays green: any
  `framework/layers/**` edit requires `tools/sync-plugin-framework.sh`, and the
  propagation order `framework/VERSION` → `scripts/sync-version-refs.sh` →
  `tools/sync-plugin-framework.sh` is load-bearing.
- Editing `tools/sdd_doc_lint/*.py` requires re-copying both vendored platform
  mirrors via `tools/sdd_doc_lint/sync-vendored.sh`.
- Register any new test module in `tests/conformance/test_repo_scripts.py`'s
  `REGISTERED` tuple — `tests/unit/` is executed by no hook and no workflow.
- Acceptance goldens: warning matching is a bidirectional multiset, so a warning
  reddens a target exactly as an error does. Golden edits and rule landing must
  be in the same change.

## Risks

| Risk | Likelihood | Mitigation |
| --- | --- | --- |
| `COV04` lands before the corpus is regenerated and reddens the acceptance tier | High | Sequence R1 behind the corpus regen, or land the rule at `warning` in `build` with the golden delta pinned in the same PR |
| The projection goes stale against its YAML source | High | R10 ships the guard with the generator, never after |
| `COV04` is implemented by mutating `realizing_layers`, re-grading every consumer corpus | Medium | R1 mandates an additive sibling block; the exact-equality pin failing is the signal that this happened |
| `code_build` lens checks are written beside the fix and inherit its misconception | Medium | Derive the checks from the TDD and SPEC contracts, not from the corpus IPLAN that already passed at 100 |
| The template gains `artifact_type` while the emitters keep omitting it | Medium | `OKF01` fires on the artifact, not the template |
| F-0 is read as forbidding markdown anywhere | Low | The decision is about the source of truth; descriptive and explanatory markdown remains permitted, and the projection is generated markdown |

## Docs to update

`framework/governance/DECISIONS.md` (GD entry for F-0 and `COV04`),
`framework/governance/LINT_RULES.md`, `framework/governance/TRACEABILITY.md`,
`framework/registry/LAYER_REGISTRY.yaml`, `framework/layers/08_IPLAN/README.md`,
`plans/DECISIONS.md`, `plans/OKF-CONFORMANCE-001-DESIGN.md` (the seven
corrections), `CHANGELOG.md`, `plans/HANDOFF.md`.

## Review log

**Pass 0 — 2026-08-26.** Draft authored from a two-round review of the layer.
**No independent gap-review cycle has run against this document.** Per
`CLAUDE.md` § "Development workflow" item 2, at least two full cycles plus the
example-corpus cross-check are required before any PR opens, and implementation
begins only after the plan PR merges.

**Amendment — 2026-08-27 — founder decision (NOT a review pass).** A2 discarded;
R3 and R4 voided; F-3 voided; Stage 2 vacated. Reasoning in the A2 tombstone. The
`Review cycles` count above is unchanged — a discard is not a gap-review cycle.

Findings not yet filed on the tracker. Parts A, B and C are repository-owned
defects; per `CLAUDE.md` § "Own-repo gaps" each belongs on GitHub issues at
one-issue-per-defect granularity, with the analysis moved verbatim rather than
summarised.
