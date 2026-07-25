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
| `FM01` | Frontmatter is missing or unparseable. | error | — |
| `STRUCT01` | A required template section is missing or the document structure is malformed. | error | layer templates |
| `BDD-SCHEMA-001` | The BDD `scenarios:` YAML block is malformed or not a list (structural validation of the YAML-BDD carrier). | error | `../layers/04_BDD/BDD-TEMPLATE.yaml` |
| `EARS01` | An EARS statement uses a `THEN [response]` connective instead of the required `THE … SHALL …` form. | warning | `../layers/03_EARS/` |
| `DG02` | An `@diagram:` tag names a diagram kind not valid for the artifact's layer. | warning | `DIAGRAM_STANDARDS.md` |
| `PH01` | A placeholder / unfilled token (e.g. `TODO`, `XXX`, `{…}`) remains in the body. | warning | `AUTHORING_STYLE.md` |
| `SEED01` | A BRD `seed_disposition:` ledger row is malformed (missing claim, illegal disposition, `absorbed` with no/unresolvable BRD element, `rejected` with no rationale, or `deferred` with no rationale/target cycle). Deterministic half of the seed contract; the auditor lens (C8) owns completeness. Silent when the optional carrier is absent. | error | `SEED_CONTRACT.md` |

## Identifiers

| ID | Meaning | Severity | Contract |
|----|---------|----------|----------|
| `ID01` | Malformed trace-tag id (`@<layer>: <id>` value does not match the id grammar). Rejects the templated `@<layer>: TYPE.NN.SS.xxxx` placeholder in a produced artifact — valid only in templates/snippets. | error | `ID_NAMING_STANDARDS.md`, `TAG_SYNTAX.md` |
| `ID02` | Malformed document id (does not match `id_patterns.document`). | error | `registry/LAYER_REGISTRY.yaml`, `ID_NAMING_STANDARDS.md` |
| `ID03` | Malformed element id (does not match `id_patterns.element`). A produced artifact must carry a real element ID; the templated `TYPE.NN.SS.xxxx` placeholder (valid only in templates/snippets) is rejected here in any authored document — locked by `tests/acceptance/fixtures/negative/brd-templated-ids.md`. | error | `registry/LAYER_REGISTRY.yaml`, `ID_NAMING_STANDARDS.md` |
| `HASH01` | An element id is defined in more than one place (collision / duplicate declaration). | error | `ID_NAMING_STANDARDS.md` |
| `PROV01` | The document declares `id_state: provisional` — its element IDs are placeholders, not verified canonical hashes. | advisory | `ID_NAMING_STANDARDS.md` |
| `IDDRIFT01` | `rehash --check`: an element's content no longer matches its declared ID hash (drift since the ID was minted). | advisory (opt-in) | `ID_NAMING_STANDARDS.md` |

## Traceability & coverage

| ID | Meaning | Severity | Contract |
|----|---------|----------|----------|
| `TAG01` | The artifact is missing a required upstream tag (necessary-upstream / cumulative traceability). | error | `TRACEABILITY.md`, `TAG_SYNTAX.md` |
| `TRACE-RES-001` | A trace tag does not resolve to an existing target document/element. | error | `TRACEABILITY.md` |
| `REFGRAN01` | A document-level trace tag points to an element-declaring layer where an element-level citation is required (GD-03 reference granularity). | warning | `TAG_SYNTAX.md` |
| `COV01` | Forward coverage: an in-scope BRD functional requirement is cited by no PRD, or reaches no downstream SPEC/IPLAN. | warning→error | `TRACEABILITY.md` |
| `COV02` | Backward coverage: an EARS/BDD element is realized by no doc in its realizing set. | warning | `TRACEABILITY.md`, `registry/LAYER_REGISTRY.yaml` (`realizing_layers`) |
| `ACC01` | Acceptance pairing: a BDD scenario is realized (designed/covered) but paired to no TDD **test case** — no test case or §3 mapping entry names it (a citation only in the TDD traceability block does not pair). Case-scoped, stricter than `COV02`. Governs BDD-scenario→TDD-case pairing inside a *project's* chain — **not** the framework's own acceptance harness (`tests/acceptance/`). | warning→error | `SEED_CONTRACT.md`, `registry/LAYER_REGISTRY.yaml` (`acceptance_layers`) |
| `COV03` | Phase-leak advisory: a `Future`-banded (deferred) FR is nonetheless realized downstream. | advisory | `TRACEABILITY.md` |
| `CSC01` | Cross-layer cardinality / deliverable-type mismatch between a child doc and its parent. | warning | `ID_NAMING_STANDARDS.md` |

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
| `STY03` | The document body exceeds its word-count target. | warning | `AUTHORING_STYLE.md` |
| `STALE01` | Status is `Approved` but a required freshness field (e.g. `last_audited_spec`) is missing — the artifact may be stale. | warning | `DEFINITION_OF_DONE.md` |

## Reuse

| ID | Meaning | Severity | Contract |
|----|---------|----------|----------|
| `REUSE01` | The document is satisfied by reference (`reuse: referenced`) — it is not re-audited; the reuse target is named. | advisory | `TRACEABILITY.md` |
| `REUSE02` | A `reuse:` declaration violates its contract — unknown `reuse.state` (expected `authored`/`referenced`), or a missing / URL / malformed / unresolvable-in-repo `reuse.target`. | error | `TRACEABILITY.md` |
