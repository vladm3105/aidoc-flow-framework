# OKF-CONFORMANCE-001 Design — native Open Knowledge Format conformance for SDD artifacts

| Field          | Value                                                     |
| -------------- | --------------------------------------------------------- |
| Task           | OKF-CONFORMANCE-001                                         |
| Type           | design (feeds a separate implementation plan)               |
| Status         | Draft — 2026-08-23                                          |
| Depends on     | none                                                        |
| Feeds          | `plans/OKF-CONFORMANCE-001-PLAN.md` (not yet written)       |
| Version impact | framework MINOR + plugin MINOR; see "Version impact" below  |

## Objective

Make the SDD artifacts this framework produces conform to Google Cloud's Open
Knowledge Format (OKF) v0.2, so a docs tree is consumable by any OKF reader
without an export step.

**The review that shaped this design found the real blocker is not OKF.** It is
that `framework/**` declares no normative instance-frontmatter contract at all.
The frontmatter every artifact carries exists only as convention reproduced in
the corpus and in engine authoring surfaces. OKF conformance is impossible until
that contract exists, so authoring it *is* the bulk of this work; `type` is one
field in it.

## Scope

**In:**

- A normative instance-frontmatter contract in `framework/governance/`.
- OKF conformance rule 1 (parseable frontmatter) and rule 2 (non-empty `type`)
  across a consumer `docs/` tree.
- The emitters that actually write frontmatter: the plugin authoring SKILLs and
  the Hermes prompt templates.
- Lint rules and a conformance test that keep it true.

**Out of scope (deferred to a successor design, one line each — not designed here):**

- The `status` / `sdd_status` collision and OKF's lifecycle family. Review showed
  the framework has **five** status vocabularies, not one (see "Corrected
  baseline"); reconciling them is its own problem and is not created by OKF.
- OKF trust family (`generated`, `verified`) and the blind-review reconciliation.
- OKF provenance family (`sources`).
- `stale_after` — depends on the lifecycle work above.
- `okf_version` declaration and a bundle-root `docs/index.md`.
- Markdown-link projection of the `@`-tag graph (`## Upstream` sections).
- One-file-per-element concept identity; Attested Computation; export tooling;
  `framework/**` itself as a bundle; the 52 plugin SKILLs as concept documents.
- Retiring `custom_fields.document_type`.

**Why the cut.** An earlier draft of this design staged all four OKF field
families at once. Three independent reviews returned BLOCKER, and the large
majority of findings traced to that elective scope rather than to conformance
itself. Per `CLAUDE.md` § "Durable conventions" (minimal-and-realistic plans),
the response is to cut to the minimum sufficient design and park the rest as an
enumeration. Conformance needs `type` and parseable frontmatter. Nothing else.

## What OKF is (grounded, v0.2)

A bundle is a directory tree of markdown files with YAML frontmatter.
Conformance is three rules:

1. Every non-reserved `.md` file contains a parseable YAML frontmatter block.
2. Every frontmatter block contains a non-empty `type` field.
3. Reserved filenames (`index.md`, `log.md`) follow their defined structure
   **when present** — both are optional.

Concept ID is the file path minus `.md`. Markdown links assert relationships.
Types are unregistered; consumers must tolerate unknown types, unknown keys, and
broken links.

Sources: [Google Cloud blog](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing/),
[SPEC.md](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md).

## Corrected baseline

Every row below was measured this session. Rows marked **(corrected)** replace a
claim in the first draft that review falsified.

| Fact | Evidence |
| --- | --- |
| Corpus is 11 `.md`; 10 lack `type`; `docs/TRACEABILITY_MATRIX.md` has no frontmatter at all; 0 reserved-name collisions; `title` 10/10, `tags` 3, `description` 0 | `examples/url-shortener/docs/` |
| **No layer template declares instance frontmatter** — `grep -c artifact_type` returns **0** across all 16 `*-TEMPLATE.yaml`; `BRD-TEMPLATE.yaml` opens on a comment banner, not a `---` fence | `framework/layers/*/` |
| Template surface is **26**, not 17: 8 layer + 8 MVP + `CHG-TEMPLATE.yaml` + 9 index **(corrected)** | `framework/layers/`, `framework/governance/chg/` |
| **Five** `status` vocabularies. Four are declared canonically; CHG is a fifth, absent from that declaration **(corrected)** | `ID_NAMING_STANDARDS.md:265-268`; `CHG-TEMPLATE.yaml:82` |
| `fm.get("status")` has **three** read sites, not two — `:1288` is `STALE01` **(corrected)** | `tools/sdd_doc_lint/__init__.py:449,450,1288` |
| `artifact_type` has **five** read sites, not two **(corrected)** | `tools/sdd_doc_lint/__init__.py:1356,1422,1566,1873` (+1 via `_artifact_code`) |
| Index templates nest `artifact_type` under `custom_fields`, and 6 of 7 carry the bare artifact name (`SPEC`, not `SPEC-INDEX`) **(corrected)** | `SPEC-00_index.TEMPLATE.md:9` |
| `artifact_type: REF` is a live in-scope type absent from any vocabulary list **(corrected)** | `platforms/claude-code-plugin/skills/doc-ref/SKILL.md:70` |
| Acceptance goldens are **mixed**: BRD/PRD/EARS/BDD/ADR `.md`; SPEC/TDD/IPLAN `.yaml` **(corrected)** | `tests/acceptance/fixtures/layer_08_iplan/valid/` |
| Plugin scaffolding `touch`es 8 **empty** index files — 7 `.md` with no frontmatter, i.e. OKF rule-1 violations created at project init **(corrected)** | `platforms/claude-code-plugin/skills/project-init/SKILL.md:74-80` |
| Acceptance warning matching is a **bidirectional multiset** — a warning is exactly as fatal as an error **(corrected)** | `tests/acceptance/_harness.py:150-151` |
| Templates fan out to **one** mirror (plugin), not two; only `sdd_doc_lint` goes to both **(corrected)** | `tools/sync-plugin-framework.sh:21`, `tools/sdd_doc_lint/sync-vendored.sh` |
| `examples/sdd-orchestrator/` exists on disk but is **untracked** — `url-shortener` is the only corpus in the repo **(corrected)** | `git ls-files examples/sdd-orchestrator` is empty |

### Two claims this design rejects after checking

- A reviewer read `DOC_GOVERNANCE_CORE.md:41` "Unified YAML only" as mandating
  YAML-authored artifacts. It does not — the bullet sits under `## Template
  Policy` and governs templates. The underlying concern survives on the
  acceptance-golden evidence above instead.
- A reviewer reported `document_fingerprint` has no producer. It has one:
  `platforms/hermes/src/mcp_server/review/saga_orchestrator.py:628` sets
  `f"{doc_type}:{len(sections)}:{len(personas)}"`. **That is worse than no
  producer for our purposes** — it is a shape descriptor, not a content hash, so
  it cannot detect a prose edit. Any future verified-but-modified check needs a
  real fingerprint first. This is why the trust family is deferred.

## Design decisions

### D1 — Author the frontmatter contract; `type` ships inside it

New governance surface `framework/governance/FRONTMATTER_CONTRACT.md`, normative,
declaring for every layer and the CHG overlay: the required top-level keys, their
value domains, which are OKF fields and which are framework extensions, and the
`type` vocabulary.

This is the carrier the first draft assumed already existed. Authoring it is
justified independently of OKF: the linter reads top-level `artifact_type` at
five sites against a shape no spec file declares.

### D2 — `type` mirrors `artifact_type`; `artifact_type` stays canonical

`artifact_type` is read at five linter sites and appears in 19 `framework/` + 80
`platforms/` files. Renaming buys nothing functional. The contract declares
`type` as the OKF-facing projection, `OKF01` asserts equality.

**`OKF01` must name which `artifact_type` it reads.** Index templates carry it
under `custom_fields` while the corpus carries it in *both* places. The rule
reads **top-level** — the same key the linter reads — and a top-level/nested
disagreement is itself a finding, not a pass. No blanket "missing means
satisfied" carve-out: that made the guard vacuous for the entire index class,
which is the one class where the vocabulary is ambiguous.

### D3 — `type` vocabulary is enumerated in the contract, not derived

The first draft derived it from `LAYER_REGISTRY.artifact` and missed three live
classes. The contract enumerates explicitly:

- Instance documents — `BRD`, `PRD`, `EARS`, `BDD`, `ADR`, `SPEC`, `TDD`,
  `IPLAN`, `CHG`.
- Reference documents — `REF`.
- Index documents — one form, chosen in the contract and applied to all nine.
  Today six carry the bare artifact name and one carries `BRD-INDEX`; the bare
  form makes an index indistinguishable from an instance, so `<X>-INDEX` is
  recommended, which makes this a **corpus- and template-affecting change**, not
  a documentation one.
- Generated artifacts — `TRACEABILITY-MATRIX`.
- `.aidoc/` report types (`AUDIT_REPORT`, `REVIEW_REPORT`, `REMEDIATION_REPORT`)
  are **excluded**: `.aidoc/` is not part of the OKF bundle. The contract says so.

### D4 — `status` is not touched

The first draft renamed it to `sdd_status`. Review established: five
vocabularies; `status:` is overloaded four ways *inside* templates (lifecycle,
option status, IPLAN task state, saga state); the rename's measured cost was
counted with a grep that would have corrupted the other three; and omitting
`:1288` makes `STALE01` fail **open** with a green suite.

None of that is caused by OKF, and none of it is needed for conformance. It is
deferred whole. **The successor design must treat "which `status` is this?" as
its first question**, and must carry a test asserting `STALE01` still fires.

### D5 — `custom_fields.document_type` is retained, on corrected grounds

The first draft retained it because dropping it would disarm a Hermes guard.
**That was wrong.** `platforms/hermes/src/mcp_server/validation/runner.py:134`
reads `metadata.get("document_type")` — the YAML `metadata:` block, not markdown
`custom_fields` — it appends a *warning*, and it fires only on the literal
`"template"`, which appears nowhere in the repo. The guard is inert.

It is retained anyway, for a smaller reason: it is out of scope, changing it
touches 26 templates plus the corpus, and nothing in this design needs it gone.
Recorded so a later reader does not inherit the false blocker.

## Stages

### Stage 1 — the contract and the emitters

`FRONTMATTER_CONTRACT.md` + `type` into the 26 templates + the emitters that
write instance frontmatter. **This stage is not platform-free** — the first
draft's central staging claim. The templates declare the contract; the plugin
SKILLs and Hermes prompt templates emit it.

Also here, because each is an OKF rule-1 violation the framework creates itself:

- `project-init` must scaffold index files **with frontmatter**, not `touch`
  them empty.
- `tools/sdd_coverage.py` must write frontmatter onto `TRACEABILITY_MATRIX.md`.

### Stage 2 — enforcement

`OKF01` (`type` present, non-empty, equals top-level `artifact_type`) and
`OKF02` (frontmatter parseable on every non-reserved `.md`). Conformance test.
Fixtures.

**There is no warning-based grace window.** `tests/acceptance/_harness.py:150-151`
matches warnings as a bidirectional multiset, so a warning reddens every
acceptance target exactly as an error would. The rule and its fixture updates
must land in the same PR; grace comes from ordering Stage 1 before Stage 2, not
from severity.

## Open questions for the implementation plan

1. **The `.yaml`-authored layers.** SPEC, TDD and IPLAN goldens are `.yaml`. OKF's
   atom is a `.md` file, so a YAML-authored tree is vacuously conformant — an OKF
   reader sees an empty bundle. Either the contract declares markdown mandatory
   for OKF-conformant trees, or those three layers are declared outside the
   bundle. Not decidable from the spec alone; needs a founder call.
2. **Section-split artifacts.** `doc-brd/SKILL.md:143-146` splits documents over
   25 KB into `BRD-NN.S_{section}.md`. Each split file is an independent OKF
   concept needing its own `type`. The contract must say what it is.
3. **Index `type` form.** `<X>-INDEX` is recommended in D3, but it changes six
   templates' `artifact_type` values and therefore the corpus.

## Version impact

Framework **MINOR** (new governance surface, additive template keys). Plugin
**MINOR** — the emitters change, and per `CLAUDE.md` the plugin bump is a
~60-file fanout needing founder OK. The first draft's "no platform version move"
was false. `GATE-SPEC-E005` applies; a GD entry in
`framework/governance/DECISIONS.md` is warranted.

## Verification

- `python3 -m sdd_doc_lint examples/url-shortener/docs/` — pinned expected delta,
  **not** "zero unexpected findings". Adding frontmatter to
  `TRACEABILITY_MATRIX.md` makes it visible to `build_edge_graph` and every
  frontmatter-keyed check for the first time; `CLAUDE.md` § "Acceptance harness"
  measured an analogous change at 0 → 6 findings.
- `tests/conformance/test_okf_conformance.py` asserting OKF rules 1 and 2.
- `tests/conformance/platforms/test_plugin_framework_bundle.py` stays green —
  any `framework/layers/**` edit requires `tools/sync-plugin-framework.sh`.
- Register new modules in `tests/conformance/test_repo_scripts.py`'s `REGISTERED`
  tuple; `tests/unit/` is executed by no hook and no workflow.

## Risks

| Risk | Likelihood | Mitigation |
| --- | --- | --- |
| Contract codifies today's accidental shape rather than a designed one | High | Derive it from the five linter read sites and the corpus, and state each key's consumer in the contract |
| Emitter drift — templates declare `type`, an engine forgets to write it | Medium | `OKF01` fires on the artifact, not the template; the conformance test runs on corpus output |
| Index `type` change ripples into the corpus | Medium | Sequence behind the contract; regenerate rather than hand-edit (`CLAUDE.md`: never hand-edit example artifacts) |
| `.yaml` layers make the bundle vacuous | High | Open question 1 — resolve before the plan's first review cycle |

## Docs to update

`framework/governance/DECISIONS.md` (GD entry), `framework/governance/LINT_RULES.md`,
`plans/DECISIONS.md`, `CHANGELOG.md`, `plans/HANDOFF.md`, and
`framework/governance/ID_NAMING_STANDARDS.md` if D3's index form is adopted.

## Cross-repo

File an issue on `engramory`: its planned OKF ADR
(`plans/PLAN-004_docs-review-remediation.md:345`, `TODO.md:296`) is written
against OKF **v0.1** while this repo targets **v0.2**. Frame it as anticipatory —
that repo has adopted nothing yet; Phase 6 authors a proposal-only ADR and
`:42` defers implementation. Record the issue number here once filed.

## Review log

**Pass 1 — 2026-08-23.** Three independent reviewers dispatched per OPS-0065
(`code-reviewer`, `documentation-specialist`, `verified-planning-reviewer`) against
the first draft. Two returned BLOCKER, one returned Request-Changes. Findings
folded:

- No frontmatter contract exists — invalidated Stage 1's mechanism. Now D1, and
  the design's central premise.
- Five `status` vocabularies and a fail-open `STALE01` — the rename is deferred
  whole (D4).
- D2's Hermes citation was misread; the guard is inert (now D5).
- Template surface 17 → 26; read-site counts 2 → 5 for both `artifact_type` and
  `status`; one template mirror, not two.
- Index `artifact_type` is nested and mostly bare-valued — the equality carve-out
  was vacuous (D2).
- Missing types `REF`, `TRACEABILITY-MATRIX`; `.aidoc/` explicitly excluded.
- Mixed `.md`/`.yaml` authoring — now open question 1.
- Warning is not a grace window; plugin scaffolds empty index files.
- Two reviewer claims rejected after checking: the "Unified YAML only" reading,
  and "no `document_fingerprint` producer".
- Scope cut to conformance-only per the minimal-and-realistic convention.

**Result:** not ready — three open questions must be resolved before the
implementation plan's first review cycle.

> **Next:** per `CLAUDE.md` § "Development workflow" item 2, the implementation
> plan must clear at least two full gap-review cycles plus the example-corpus
> cross-check before its PR opens.
