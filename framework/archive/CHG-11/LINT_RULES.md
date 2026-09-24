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

Measured across all ten layers:

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
| `REG01` | New-layer registration: a layer entry is missing a mandatory registration field (`number`, `artifact`, `name`, `folder`, `extensions`, `required_tags`, `can_reference`, `error_prefix`, `optional`, `description`, `template`, `downstream`) or a registration follow-up (`total_layers`, `layer_groups`, `realizing_layers`, `c4_mapping`, upstream `downstream`, new lint rule IDs). The full checklist lives in the `LAYER_REGISTRY.yaml` header comment. | warning (advisory) | `registry/LAYER_REGISTRY.yaml`, `registry/README.md` |
| `CSC01` | Cross-layer cardinality / deliverable-type mismatch between a child doc and its parent. | error | `ID_NAMING_STANDARDS.md` |

## Thresholds

| ID | Meaning | Severity | Contract |
|----|---------|----------|----------|
| `TH01` | Malformed `@threshold:` key (does not match `id_patterns.threshold`). | error | `THRESHOLD_NAMING_RULES.md` |
| `TH02` | A threshold's suffix/value is inconsistent with the corpus's other uses of the same key. | warning | `THRESHOLD_NAMING_RULES.md` |
| `TH-RES-001` | An `@threshold:` reference is unresolved — not declared in the cited source document's threshold section. | error | `THRESHOLD_NAMING_RULES.md`, `TRACEABILITY.md` |

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

## Governance (CHG)

| ID | Meaning | Severity | Contract |
|----|---------|----------|----------|
| `GOV-008` | A CHG document was created without completing the creation checklist (§CHG creation checklist). The checklist is a MANDATORY PROCESS GATE — blocking prerequisite, not post-hoc validation. The "write before read" pattern has caused repeated failures (CHG-04: 16 gaps, CHG-06: 3 bugs). | error | `DOC_GOVERNANCE_CORE.md` §CHG creation checklist MANDATORY PROCESS GATE |
| `GOV-009` | A CHG document's `traceability.upstream.ears_references` or `bdd_references` is empty when the CHG describes a change that affects authenticated or requirement-traced functionality. Checklist item #5 requires citing specific EARS/BDD IDs. TAG01 covers general traceability but not CHG-specific upstream citation. | warning | `DOC_GOVERNANCE_CORE.md` §CHG creation checklist item #5 |
| `GOV-010` | A CHG document's `implementation.steps` contains a step without a `phase` field, or a step with `phase: code_implementation`. Every step MUST have `phase: sdd_lifecycle` or `phase: iplan_creation`. Code implementation steps belong exclusively in IPLAN. Added after CHG-04, CHG-06, CHG-08 violated SDD-first ordering. | error | `CHG-TEMPLATE.yaml` §implementation `_allowed_phases` + checklist item #13 |
| `GOV-011` | A CHG document's `change_control.status` has skipped a lifecycle stage. Status MUST follow: Proposed → Approved → In-Progress → Implemented → Completed. Skipping `Approved` (jumping from `Proposed` to `In-Progress` or later) means implementation started without authorization. `date_approved` must be set before status can be `In-Progress` or later. Added after CHG-10 jumped from `Proposed` to `Implemented` without approval. | error | `CHG-TEMPLATE.yaml` §change_control status lifecycle + `DOC_GOVERNANCE_CORE.md` §3.3 |
| `GOV-012` | A CHG document has `gate_approval.approver: null` or empty when `change_control.status` is not `Proposed` and `change_level` is `C3`. C3 changes require explicit gate approval with a named approver. The approver must be recorded before status can advance beyond `Proposed`. Added after CHG-10 had null approver with `Implemented` status. | error | `CHG-TEMPLATE.yaml` §gate_approval + `DOC_GOVERNANCE_CORE.md` §3.1 |
| `GOV-013` | Code implementation was attempted without an IPLAN. The IPLAN Gate (§3.13) requires an IPLAN with status `In Progress` before any code files may be modified. The IPLAN must reference the authorizing CHG and list the files being modified. Added after CHG-10 had code implemented before IPLAN existed. **Carve-out (0.56.0):** a scoped `bugfix`-subtype IPLAN (`parent_iplan` + `source_chg`, `In Progress`, repair-scoped manifest, C1 CHG allowed) fully satisfies this gate for post-completion repairs — it is the governed path, not an exemption. No issue-thread citation alone satisfies it. | error | `DOC_GOVERNANCE_CORE.md` §3.13 IPLAN Gate |
| `GOV-014` | A CHG document's `sdd_lifecycle` omits an SDD document listed in `artifacts_modified`. Every modified SDD document must appear in the lifecycle list. Added after CHG-32 review found lifecycle/traceability gaps the linter stayed green on. | error | `DOC_GOVERNANCE_CORE.md` §3.4.1 C16 |
| `GOV-015` | A CHG document's `sdd_lifecycle` entry is missing `layer`, `document`, or `action`, carries a null `archive_path` or `new_version` (except `08_IPLAN` + `create`, where there is nothing to archive), or uses a non-CHG-ID archive path. Added after CHG-32 carried 20 null `archive_path`/`new_version` entries with a green lint. | error | `DOC_GOVERNANCE_CORE.md` §3.4.1 C17–C19 |
| `GOV-016` | A CHG document's `change_control.supersedes` omits an archived document recorded in `sdd_lifecycle`. Every archived path must be superseded with its full path. Added after CHG-32 shipped `supersedes: []` alongside 20 lifecycle entries. | error | `DOC_GOVERNANCE_CORE.md` §3.4.1 C20 |
| `GOV-017` | A CHG document cites an EARS/BDD element ID that does not exist in the lifecycle's EARS/BDD documents. Fabricated requirement/scenario IDs break traceability silently. Added after CHG-32 review found lifecycle/traceability gaps the linter stayed green on. | error | `DOC_GOVERNANCE_CORE.md` §3.4.1 D21–D22 |
| `GOV-018` | A CHG document carries a code/script manifest with an empty `sdd_lifecycle` but `change_source` is not `direct`, or references no IPLAN, or repairs closed output without `parent_iplan`. Misclassified flow: the failure names the suspected correct flow (F2/F3/F4). Added with the 0.57.0 request-flows ratification (#673). | error | `DOC_GOVERNANCE_CORE.md` §3.1.3 router + `governance/CHG_REQUEST_FLOWS.md` §3.4 |
| `GOV-019` | A CHG document with code-touching scope carries no IPLAN reference — neither a top-level `sdd_lifecycle` 08_IPLAN entry, nor an `implementation.steps[]` entry with `phase: iplan_creation`, nor an `artifacts_modified` IPLAN id. The failure names the suspected vehicle (F2 scoped IPLAN, F4 bugfix-subtype IPLAN). Added with the STALE T2 remediation, which also retargeted CHG-L004 to the canon steps-scan (#668). | error | `DOC_GOVERNANCE_CORE.md` §3.1.1 SDD-first + `CHG-TEMPLATE.yaml` §implementation |
| `GOV-020` | An F3 (brownfield) CHG touches seed or module docs without covering them in its lifecycle — seed touches need a `seed_scope` record (`no-change` cites checked files; new domains are created, never rewritten) and module touches need a `module_lifecycle` entry (archive → sync → version, affected modules only). Other flows are untouched by this rule. | error | `governance/CHG_REQUEST_FLOWS.md` §4 |
| `CHG-L012` | SDD sync on IPLAN completion: a referenced IPLAN is `Completed` but its `completion_spec_sync:` block does not attest the SPEC/TDD check (`spec_checked`/`tdd_checked` must be true; `diverged: true` must name the follow-up `chg_ref`). The check validates the attestation shape, not the codebase comparison itself. | warning | `DOC_GOVERNANCE_CORE.md` §IPLAN Lifecycle, `IPLAN-TEMPLATE.yaml` (`completion_spec_sync:`) |
| `IPLAN01` | An IPLAN step modifies a function or constructor signature without documenting the current signature, the new signature, that it is a breaking change, and which callers must be updated. Auditor-lens prose — verify the `breaking_change:` block against the declared schema artifact before implementation. | warning (advisory) | `IPLAN-TEMPLATE.yaml` (`execution_commands.breaking_change:`) |
| `BGF-00` | A bugfix IPLAN file is unreadable, empty, or not a YAML mapping — there is no repair to validate. Structural pre-check before BGF-01..07. | error | `sdd_doc_lint/bugfix_lint.py` |
| `BGF-01` | A bugfix IPLAN filename does not match `IPLAN-{NEW}_bugfix_{FIXED}_{slug}.yaml`. The name carries the parentage; an ad-hoc name hides which closed plan is under repair. Added with the 0.56.0 bugfix vehicle (#656/#657). | error | `IPLAN-TEMPLATE.yaml` (`document_control` bugfix guidance) |
| `BGF-02` | A bugfix IPLAN's NEW_ID is not max+1 from the directory listing (counter-derived or colliding ID). The minter is the directory listing, never counters — a reused number forks the DAG. | error | `IPLAN-TEMPLATE.yaml` (`document_control` bugfix guidance) |
| `BGF-03` | A bugfix IPLAN's `iplan_id` / `doc_id` does not match its filename stem (§3.4.1 A1/A3 extended to the pattern). A mismatched ID breaks index and cross-link resolution. | error | `DOC_GOVERNANCE_CORE.md` §3.4.1 A1/A3 |
| `BGF-04` | A bugfix IPLAN's steps violate the normative order fix → regression test → rollback readiness → parent revision entry last (linter-checked for order). A revision entry ahead of a verified fix records repair that has not happened. | error | `IPLAN-TEMPLATE.yaml` (`document_control` bugfix guidance) |
| `BGF-05` | A bugfix IPLAN lacks a rollback procedure, or its resolution note leaves a PENDING marker unresolved (neither DONE nor SKIPPED). An unresolvable repair with no rollback path strands the tree. | error | `IPLAN-TEMPLATE.yaml` (`rollback_procedure`, bugfix-required) |
| `BGF-06` | A bugfix IPLAN's manifest names files outside the repair scope, or a DONE entry names a file missing on disk (manifest accuracy per §3.5-equivalent). Scope creep turns a repair into an unreviewed feature. | error | `DOC_GOVERNANCE_CORE.md` §IPLAN Lifecycle (manifest accuracy) |
| `BGF-07` | A bugfix IPLAN's parent is not an original terminal IPLAN (parent is itself a bugfix, or is still active). Fix-on-fix chains hide thrashing; failed attempts run rollback, then a new sibling cites `prior_attempts`. | error | `IPLAN-TEMPLATE.yaml` (`document_control` bugfix guidance) |

## TDD ↔ IPLAN sync

| ID | Meaning | Severity | Contract |
|----|---------|----------|----------|
| `TDD-SYNC-A` | Status propagation: an IPLAN `file_manifest` entry is marked `DONE` with `verified: true` but the corresponding TDD `test_mapping` entries still read `pending`. IPLAN `DONE` means "file created", not "all test cases inside it implemented" — propagate to `implemented`. | warning (advisory) | `TESTING_STRATEGY_TDD.md` §Bidirectional Status Sync |
| `TDD-SYNC-B` | File ownership: a TDD `test_mapping` references a test file not listed in the owning IPLAN's `file_manifest` (and named in no cross-reference note). Every test file must be owned by an IPLAN entry. | warning (advisory) | `TESTING_STRATEGY_TDD.md` §Bidirectional Status Sync |
| `TDD-SYNC-C` | Function-name consistency: test function names in code do not match the names declared in TDD `test_mapping`. Rename the TDD first, then implement — never leave the TDD stale. | warning (advisory) | `TESTING_STRATEGY_TDD.md` §Bidirectional Status Sync |
| `TDD-SYNC-D` | Language consistency: a TDD and its owning IPLAN reference different test-file languages for the same component. After a language pivot both layers must be updated in the same change. | warning (advisory) | `TESTING_STRATEGY_TDD.md` §Bidirectional Status Sync |
| `TDD-SYNC-E` | Index synchronization: the TDD index and the IPLAN index show inconsistent IPLAN statuses. The IPLAN index is the source of truth; when an IPLAN status changes, both indexes must be updated. | warning (advisory) | `TESTING_STRATEGY_TDD.md` §Bidirectional Status Sync |

## Evaluation (L10)

| ID | Meaning | Severity | Contract |
|----|---------|----------|----------|
| `EVAL-001` | An EVAL document contains placeholder IDs (`xxxx`) in `scenario_id`, `tdd_id`, or `source_id` fields. All element IDs must be real before commit. | error | `EVAL-TEMPLATE.yaml` §test_design |
| `EVAL-002` | An EVAL `coverage_matrix.summary` contradicts the `coverage_matrix.entries` (e.g., summary says `implemented: 0` but entries claim `status: implemented`). Summary must be computed from entries. | error | `EVAL-TEMPLATE.yaml` §coverage_matrix |
| `EVAL-003` | An EVAL `test_design` entry's `test_file` points to a CI workflow YAML (`.github/workflows/*.yml`) without a `_note` field clarifying it is a CI step, not a test file. | warning | `EVAL-TEMPLATE.yaml` §test_design |
| `EVAL-COV-001` | An EVAL `coverage_matrix` is missing entries for upstream scenarios/TDD test cases that exist in the referenced upstream sources. All upstream scenarios must appear in the coverage matrix. Missing entries trigger warning in build, error in deployment gate. | warning→error | `EVAL-TEMPLATE.yaml` §coverage_matrix |
| `EVAL-COV-002` | An EVAL smoke test's command does not match any step in the referenced CI workflow YAML. Smoke tests must cover all CI pipeline steps. Verify against `.github/workflows/*.yml` before finalizing. Added after b-local-privy EVAL-02 referenced non-existent scripts. | error | `EVAL-TEMPLATE.yaml` §test_design (smoke verification) |
| `EVAL-COV-003` | An EVAL `tdd_id` or `scenario_id` field references an ID that does not exist in any source TDD/BDD YAML file. Fabricated IDs (correct format but wrong hash) cause silent traceability breaks. Verify each cross-reference via grep. Added after b-local-privy EVAL-02 had fabricated `TDD.01.04.f19c`. | error | `EVAL-TEMPLATE.yaml` §test_design (ID verification) |
| `EVAL-COV-004` | An EVAL `coverage_matrix.summary.total` does not match the actual count of entries in `coverage_matrix.entries` (parsed via YAML parser). Counts must be recomputed after final YAML write, not set before. Added after b-local-privy EVAL-01/02 both had wrong counts. | error | `EVAL-TEMPLATE.yaml` §coverage_matrix |
| `EVAL-ID-001` | An EVAL test case `id` does not follow the `EVAL.NN.SS.xxxx` element ID format (per `ID_NAMING_STANDARDS.md`). The ID is independent from the source — source type and source document are tracked via `source_type` and `source_id` fields only. The old dash-in-ID format (`EVAL-01.TDD-01.4d64`) is incorrect. | error | `EVAL-TEMPLATE.yaml` §id_standard |
| `EVAL-SRC-001` | An EVAL `test_design` entry has a missing or incomplete source reference. Each test case must have exactly one `source_type` and one `source_id` (or neither for non-source-derived tests). Create separate test cases for each source element. | error | `EVAL-TEMPLATE.yaml` §id_standard, §test_design |
