# Lint Rules Catalog

The normative catalog of the deterministic lint rules a conforming platform's
document linter emits over the `@`-tag / element graph and per-artifact
structure. Each rule has a stable **ID**, a one-line **meaning**, a typical
**severity**, and the governance doc that defines its underlying contract (where
one exists). The reference implementation is `sdd_doc_lint` (vendored
byte-identical by each platform); a `tests/conformance/` guard asserts every ID
the linter can emit appears in this catalog.

Severity notes: many rules are context-sensitive (e.g. `COV01` warns in the
`build` phase and errors in `gate-code`); the column gives the common tier.

## Structure & schema

| ID | Meaning | Severity | Contract |
|----|---------|----------|----------|
| `FM01` | Frontmatter status/version/last_updated disagrees with the Document Control block or latest revision-history entry. | error | — |
| `STRUCT01` | A required template section is missing or the document structure is malformed. The required set is **derived**, not declared — see §"What `STRUCT01` requires, and why it can exceed `total_sections`" below. | error | layer templates |
| `BDD-SCHEMA-001` | The BDD `scenarios:` YAML block is malformed or not a list (structural validation of the YAML-BDD carrier). | error | `../layers/04_BDD/BDD-TEMPLATE.yaml` |
| `EARS01` | An EARS statement uses a `THEN [response]` connective instead of the required `THE … SHALL …` form. | error | `../layers/03_EARS/` |
| `EARS02` | An EARS document uses nested category keys (`event_driven:`, `continuous:`, `state_based:`) instead of a flat list with a `type` field. Duplicate YAML keys silently drop requirements — 16 requirements were lost in EARS-10 due to this pattern. EARS must use ONE flat list per category. | error | `../layers/03_EARS/EARS-TEMPLATE.yaml`, `LEARNED_LESSONS.md` §5.1 |
| `DG02` | An `@diagram:` tag names a diagram kind not valid for the artifact's layer. | error | `DIAGRAM_STANDARDS.md` |
| `PH01` | A placeholder / unfilled token (e.g. `TODO`, `XXX`, `{…}`) remains in the body. | error | `AUTHORING_STYLE.md` |
| `SEED01` | A BRD `seed_disposition:` ledger row is malformed (missing claim, illegal disposition, `absorbed` with no/unresolvable BRD element, `rejected` with no rationale, or `deferred` with no rationale/target cycle). Deterministic half of the seed contract; the auditor lens (C8) owns completeness. Silent when the optional carrier is absent. | error | `SEED_CONTRACT.md` |

## What `STRUCT01` requires, and why it can exceed `total_sections`

**These are two different counts, and four layers disagree by design.** Reading them as the
same number is why #557 was filed against a template that was correct.

- **`total_sections`** (declared in each `<TYPE>-TEMPLATE.yaml` `metadata:`) counts the
  **numbered** sections — the ones rendered `# Section 1:` … `# Section N:`.
- **`STRUCT01`'s required set** is **derived**, never declared: every top-level template key
  carrying `_size_target`, minus those marked `_required: false` or `_required_when_subtype:`.
  It therefore also includes required **unnumbered backmatter**.

Measured across all eight layers:

| Layer | `STRUCT01` requires | `total_sections` | why they differ |
| --- | --- | --- | --- |
| BRD | **17** | 16 | `diagrams` + `appendix` backmatter |
| ADR | **12** | 10 | `glossary` + `appendix` backmatter |
| EARS | **6** | 5 | `glossary` backmatter |
| IPLAN | **2** | 6 | *fewer*, not more — see below |
| PRD / BDD / SPEC / TDD | 15 / 5 / 8 / 7 | 15 / 5 / 8 / 7 | no unnumbered backmatter |

So a layer whose two numbers differ is **not** defective. Three of the four differ **upward**,
because the derived set also picks up required unnumbered backmatter. The **four** layers whose
numbers agree — PRD, BDD, SPEC and TDD — do so because they have no *unnumbered* backmatter:
PRD's and BDD's glossaries are numbered sections (`# Section 15` and `# Section 5`), so they are
already inside `total_sections`.

⚠️ **`IPLAN` differs DOWNWARD, and it is the reason this rule is stated as two independent
counts rather than as "declared plus backmatter".** Nine of its eleven `_size_target` keys carry
`_required: false` or `_required_when_subtype:`, so the derivation subtracts where the other
three add. A reader who generalises "differs ⇒ has backmatter" gets IPLAN exactly backwards.
`tests/conformance/test_required_section_sets.py` pins all eight derived sets, IPLAN's `2`
included, so the direction cannot drift unnoticed.

### `_required: false` marks OPTIONAL CONTENT, not "unnumbered"

The marker's one meaning is that the section may be **absent**. `PRD`'s
`component_decomposition` is the worked example: *"OPTIONAL — only required when downstream
cites `@threshold`"*.

It does **not** mean "required but unnumbered". Applying it to backmatter that is genuinely
required — EARS's `glossary`, which every EARS artifact in the corpus carries and which the
layer's authoring guidance calls required — **removes a live assertion** and makes that layer the only one of three
where required backmatter is unenforced. `tests/conformance/test_required_section_sets.py` pins
each layer's derived count so that edit cannot be made silently.

## Identifiers

| ID | Meaning | Severity | Contract |
|----|---------|----------|----------|
| `ID01` | Malformed trace-tag id (`@<layer>: <id>` value does not match the id grammar). Rejects the templated `@<layer>: TYPE.NN.SS.xxxx` placeholder in a produced artifact — valid only in templates/snippets. | error | `ID_NAMING_STANDARDS.md`, `TAG_SYNTAX.md` |
| `ID02` | Malformed document id (does not match `id_patterns.document`). | error | `registry/LAYER_REGISTRY.yaml`, `ID_NAMING_STANDARDS.md` |
| `ID03` | Malformed element id (does not match `id_patterns.element`). A produced artifact must carry a real element ID; the templated `TYPE.NN.SS.xxxx` placeholder (valid only in templates/snippets) is rejected here in any authored document — locked by `tests/acceptance/fixtures/negative/brd-templated-ids.md`. | error | `registry/LAYER_REGISTRY.yaml`, `ID_NAMING_STANDARDS.md` |
| `HASH01` | An element id is defined in more than one place (collision / duplicate declaration). | error | `ID_NAMING_STANDARDS.md` |
| `PROV01` | The document declares `id_state: provisional` — its element IDs are placeholders, not verified canonical hashes. | warning (advisory) | `ID_NAMING_STANDARDS.md` |
| `IDDRIFT01` | `rehash --check`: an element's content no longer matches its declared ID hash (drift since the ID was minted). | warning (advisory opt-in) | `ID_NAMING_STANDARDS.md` |
| `FRCAP01` | A BRD carries more functional requirements than GD-14's SHOULD cap of 5. Counts the element IDs under the FR section and BEFORE its literal `Acceptance criteria:` line — the same boundary `COV01` grades — so acceptance criteria do not count. Escaped (`Future` / `realized_by:`) requirements DO count: the cap is about document size, not coverage obligation. **Never escalates** — GD-14 states the cap as a SHOULD. | warning (advisory) | GD-14, `../layers/01_BRD/BRD-TEMPLATE.yaml` |

## Traceability & coverage

| ID | Meaning | Severity | Contract |
|----|---------|----------|----------|
| `TAG01` | The artifact is missing a required upstream tag (necessary-upstream / cumulative traceability). | error | `TRACEABILITY.md`, `TAG_SYNTAX.md` |
| `TRACE-RES-001` | A trace tag does not resolve to an existing target document/element. | error | `TRACEABILITY.md` |
| `REFGRAN01` | A document-level trace tag points to an element-declaring layer where an element-level citation is required (GD-03 reference granularity). | warning | `TAG_SYNTAX.md` |
| `COV01` | Forward coverage: an in-scope BRD functional requirement is cited by no PRD, or reaches no downstream SPEC/IPLAN. | warning→error | `TRACEABILITY.md` |
| `COV02` | Backward coverage: an EARS/BDD element is realized by no doc in its realizing set. | warning | `TRACEABILITY.md`, `registry/LAYER_REGISTRY.yaml` (`realizing_layers`) |
| `ACC01` | Acceptance pairing: a BDD scenario is realized (designed/covered) but paired to no TDD **test case** — no test case or §3 mapping entry names it (a citation only in the TDD traceability block does not pair). Case-scoped, stricter than `COV02`. Governs BDD-scenario→TDD-case pairing inside a *project's* chain — **not** the framework's own acceptance harness (`tests/acceptance/`). | warning→error | `SEED_CONTRACT.md`, `registry/LAYER_REGISTRY.yaml` (`acceptance_layers`) |
| `COV03` | Phase-leak advisory: a `Future`-banded (deferred) FR is nonetheless realized downstream. | warning (advisory) | `TRACEABILITY.md` |
| `CSC01` | Cross-layer cardinality / deliverable-type mismatch between a child doc and its parent. | error | `ID_NAMING_STANDARDS.md` |

## Thresholds

| ID | Meaning | Severity | Contract |
|----|---------|----------|----------|
| `TH01` | Malformed `@threshold:` key (does not match `id_patterns.threshold`). | error | `THRESHOLD_NAMING_RULES.md` |
| `TH02` | A threshold's suffix/value is inconsistent with the corpus's other uses of the same key. | warning | `THRESHOLD_NAMING_RULES.md` |
| `TH-RES-001` | An `@threshold:` reference is unresolved — not declared in the cited source document's threshold section. | error | `THRESHOLD_NAMING_RULES.md`, `TRACEABILITY.md` |

## TDD↔IPLAN Cross-Layer Consistency

| ID | Meaning | Severity | Contract |
|----|---------|----------|----------|
| `TDD-SYNC-001` | A TDD `test_mapping` function name does not exist as `def test_*` / `function test_*` in the declared `test_file`. The test was specified in the TDD but never implemented. | warning→error | `AI_ASSISTANT_RULES.md` §Validation Workflow |
| `TDD-SYNC-002` | An IPLAN `file_manifest` test file path does not match any `test_file` declared in the upstream TDD `test_mapping` or `test_cases`. Cross-layer path drift. | warning | `AI_ASSISTANT_RULES.md` §Validation Workflow |
| `TDD-SYNC-003` | An IPLAN `file_manifest` entry for a test file has `status: DONE` but the corresponding TDD `test_mapping` test cases still show `status: pending`. Status not propagated upstream. | warning | `AI_ASSISTANT_RULES.md` §Validation Workflow |
| `TDD-SYNC-004` | A TDD `test_file` path declared in `test_mapping` does not exist on disk. The test file was never created. | error | `AI_ASSISTANT_RULES.md` §Validation Workflow |
| `TDD-SYNC-005` | A TDD `test_file` path is not listed in the owning IPLAN's `file_manifest`. Cross-IPLAN ownership gap — the IPLAN claims completion without covering this file. | error | `AI_ASSISTANT_RULES.md` §Validation Workflow |
| `TDD-SYNC-006` | A TDD and its owning IPLAN reference different test file languages (e.g. Python vs Go) for the same component. Language mismatch after pivot. | error | `AI_ASSISTANT_RULES.md` §Validation Workflow |
| `TDD-SYNC-007` | `TDD-00_index.md` and `IPLAN-00_index.yaml` show different statuses for the same IPLAN. Index drift. `IPLAN-00_index.yaml` is the source of truth. | error | `AI_ASSISTANT_RULES.md` §Validation Workflow |
| `TDD-SYNC-008` | An IPLAN `session_handoff` entry has `validation_results.tests_passing: false` but `file_manifest` entries are marked `DONE`. Incomplete validation. | error | `layers/08_IPLAN/IPLAN-TEMPLATE.yaml` §5 |
| `TDD-SYNC-009` | An IPLAN `session_handoff` entry has `validation_results.lint_clean: false` but `file_manifest` entries are marked `DONE`. Incomplete validation. | warning | `layers/08_IPLAN/IPLAN-TEMPLATE.yaml` §5 |
| `TDD-SYNC-010` | A newly added IPLAN is not registered in all four required locations in `IPLAN-00_index.yaml`: `registry.plans`, `dependency_graph`, parent IPLAN's `blocks` list, and `execution_path.tiers`. Partial registration leaves the IPLAN invisible to dependency resolution. | error | `LEARNED_LESSONS.md` §4.2 |
| `TDD-SYNC-011` | A TDD coverage table TOTAL row does not match the sum of individual test case entries. TDD coverage arithmetic is error-prone — totals are hand-computed by LLMs and consistently wrong. The TOTAL must equal the count of entries in `test_mapping` or `test_cases`. | error | `LEARNED_LESSONS.md` §3.4 |

## Style

| ID | Meaning | Severity | Contract |
|----|---------|----------|----------|
| `STY01` | An authoring-style violation (banned phrasing / promotional or subjective language). | warning | `AUTHORING_STYLE.md` |
| `STY02` | A section exceeds its word-count target. | warning | `AUTHORING_STYLE.md` |
| `STY03` | The document body exceeds its word-count target. | error | `AUTHORING_STYLE.md` |
| `STALE01` | Status is `Approved` but a required freshness field (e.g. `last_audited_spec`) is missing — the artifact may be stale. | warning | `DEFINITION_OF_DONE.md` |

## Reuse

| ID | Meaning | Severity | Contract |
|----|---------|----------|----------|
| `REUSE01` | The document is satisfied by reference (`reuse: referenced`) — it is not re-audited; the reuse target is named. | warning (advisory) | `TRACEABILITY.md` |
| `REUSE02` | A `reuse:` declaration violates its contract — unknown `reuse.state` (expected `authored`/`referenced`), or a missing / URL / malformed / unresolvable-in-repo `reuse.target`. | error | `TRACEABILITY.md` |

## Governance

| ID | Meaning | Severity | Contract |
|----|---------|----------|----------|
| `GOV-001` | A CHG document does not track the mandatory status lifecycle (Proposed → Approved → In-Progress → Implemented → Completed). Status must never regress. | error | `DOC_GOVERNANCE_CORE.md` §CHG Rules |
| `GOV-002` | A CHG modifies SDD documents but the FIRST implementation steps are not SDD document updates (archive → rewrite → supersedes → version bump). SDD-first ordering is mandatory. | error | `DOC_GOVERNANCE_CORE.md` §CHG Rules |
| `GOV-003` | A CHG's `implementation.steps` contains detailed code implementation steps instead of deferring to IPLAN. The CHG authorizes scope; the IPLAN executes. | warning | `DOC_GOVERNANCE_CORE.md` §CHG Rules |
| `GOV-004` | An IPLAN is marked `Completed` without a corresponding SPEC/TDD version check. Mandatory SDD sync required. | error | `DOC_GOVERNANCE_CORE.md` §CHG Rules |
| `GOV-005` | An upstream SDD document is not "Approved" before its downstream layer is started. Status propagation violated. | error | `DOC_GOVERNANCE_CORE.md` §Status Propagation Rules |
| `GOV-006` | An SDD document was not archived to `docs/sdd/09-CHG/archive/` before being rewritten. Clean rewrites require archival. | error | `DOC_GOVERNANCE_CORE.md` §SDD Document Management |
| `GOV-007` | An SDD document contains stale content from previous versions (appendices, "added by CHG-XX" annotations, unused sections). Clean rewrites required. | warning | `DOC_GOVERNANCE_CORE.md` §SDD Document Management |
| `GOV-008` | A CHG document was created without completing the creation checklist (§CHG creation checklist). The checklist is a MANDATORY PROCESS GATE — blocking prerequisite, not post-hoc validation. The "write before read" pattern has caused repeated failures (CHG-04: 16 gaps, CHG-06: 3 bugs). | error | `DOC_GOVERNANCE_CORE.md` §CHG creation checklist MANDATORY PROCESS GATE |
| `GOV-009` | A CHG document's `traceability.upstream.ears_references` or `bdd_references` is empty when the CHG describes a change that affects authenticated or requirement-traced functionality. Checklist item #5 requires citing specific EARS/BDD IDs. TAG01 covers general traceability but not CHG-specific upstream citation. | warning | `DOC_GOVERNANCE_CORE.md` §CHG creation checklist item #5 |

## Evaluation (L10)

| ID | Meaning | Severity | Contract |
|----|---------|----------|----------|
| `EVAL-001` | An EVAL document contains placeholder IDs (`xxxx`) in `scenario_id`, `tdd_id`, or `source_id` fields. All element IDs must be real before commit. | error | `EVAL-TEMPLATE.yaml` §test_design |
| `EVAL-002` | An EVAL `coverage_matrix.summary` contradicts the `coverage_matrix.entries` (e.g., summary says `implemented: 0` but entries claim `status: implemented`). Summary must be computed from entries. | error | `EVAL-TEMPLATE.yaml` §coverage_matrix |
| `EVAL-003` | An EVAL `test_design` entry's `test_file` points to a CI workflow YAML (`.github/workflows/*.yml`) without a `_note` field clarifying it is a CI step, not a test file. | warning | `EVAL-TEMPLATE.yaml` §test_design |
| `EVAL-COV-001` | An EVAL `coverage_matrix` is missing entries for upstream scenarios/TDD test cases that exist in the referenced upstream sources. All upstream scenarios must appear in the coverage matrix. Missing entries trigger warning in build, error in deployment gate. | warning→error | `EVAL-TEMPLATE.yaml` §coverage_matrix |
