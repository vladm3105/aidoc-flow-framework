# Framework Governance Decisions

Durable record of decisions about the **shared specification** and its
governance. The spec is the contract every platform implements, so decisions
that shape it live here — with the spec — not inside any one platform and not
only in a migration-time log. Spec-affecting entries from the project's
migration decision log graduate here once change management governs the spec.

A change to this file is itself a framework-spec change: it passes **GATE-SPEC**
(`chg/gates/GATE-SPEC_FRAMEWORK.md`) like any other change to the spec.

Newest first. Timestamps are ISO 8601 UTC.

---

## GD-22 — Non-C4 diagram kinds are valid on every layer; only C4/DFD levels are policed per layer

- **Status:** Accepted — 2026-08-29 · **SemVer:** framework `0.46.0 → 0.47.0` (MINOR),
  change-level **C2**. Ratified on merge; a `framework/**` normative change — human sign-off per
  GATE-SPEC.
- **Issues:** #552

Six layers declared a `diagram_standard` — BRD, PRD, EARS, BDD, ADR, SPEC — and **two of them,
EARS and BDD, shipped no authoring slot at all**. The other **four** already carried one:
measured on `main`, BRD 2, PRD 1, ADR 2, SPEC 1 `diagram:` keys. (TDD also has a `diagram:` key
but declares no `diagram_standard`, so it is outside this population — see the consequence
below. An earlier draft said "one shipped a slot"; a second said "five, including TDD". Both
were wrong and were corrected on OPS-0065 review before merge.) The blocker was
vocabulary, not effort: `EARS-TEMPLATE.yaml` recommends three diagram kinds and only one
(`sequenceDiagram`) had any `@diagram:` tag form. `DG02` is **error**-severity and EARS, BDD and
ADR have empty C4 allowlists, so a *tagged* slot on any of them emitted a `DG02` error **on the
template's own example content**.

**Decision: `state-*` and `flow-*` join `sequence-*` as kinds valid on every layer.**

**The reasoning generalises, and it is why this is not a per-layer allowlist.** `c4_mapping`
allowlists a layer's C4/DFD **level**, which is exactly what `DG02` exists to police — a BRD may
not carry an L3 component diagram. A state machine or a flowchart **has no level to mismatch**.
A per-layer allowlist for them would encode nothing, and would have to be repeated on every
layer that ever wants one. `sequence-*` was already treated this way; this extends the existing
rule rather than introducing a second mechanism.

`DG02` keeps its teeth, verified rather than asserted: `c4-l3` on EARS or BRD is still rejected,
`c4-l1` on BRD still passes, and an unknown kind (`bogus-kind`) is still rejected.

With the vocabulary settled, **EARS and BDD** gain a `diagram:` authoring slot in the same
**key shape** SPEC already had — `_guidance`, `tags:` and a `mermaid:` block — and each emits
**zero** `DG02` findings on its own template.

⚠️ **Same shape, different placement, deliberately.** SPEC's slot sits inside
`component_overview`, a numbered content section carrying a `_size_target`. These two sit under
`metadata.diagram_standard`, which carries none — which is exactly what keeps GD-21's "no count
moves" true, since `STRUCT01`'s required set is derived from `_size_target` keys. Do not read
this entry as claiming structural parity with SPEC; it claims key-shape parity only. They are the only two layers that genuinely lacked one: of the six that
declare a `diagram_standard`, **four** (BRD, PRD, ADR, SPEC) already shipped a slot.

- **Authority:** `governance/DIAGRAM_STANDARDS.md`; `registry/LAYER_REGISTRY.yaml` `c4_mapping`;
  `tools/sdd_doc_lint` `_DIAGRAM_SEQUENCE` (the precedent this extends)
- **Consequences:**
  - **ADR deliberately gains NO new slot.** It already ships one as the REQUIRED
    `decision_sequence` section. Adding a second would put two REQUIRED declarations of the
    same decision diagram in two different key shapes into one template, telling an author to
    write it twice. An earlier draft of this entry did add it; removed on OPS-0065 review
    before merge. See `layers/05_ADR/ADR-TEMPLATE.yaml`, which states the absence at the site.
  - **PRD, TDD and IPLAN still have no slot**, deliberately. PRD's C4-L2 diagram belongs with
    its container decomposition and is a separate question; TDD and IPLAN declare no
    `diagram_standard` at all, so there is nothing to give them a slot *for*.
  - The tag forms are **open-ended** (`state-<name>`, `flow-<name>`), matching `sequence-*`.
    A closed enumeration would need updating for every new diagram purpose, which is the churn
    `sequence-*` was already designed to avoid.
  - **Nothing existing changes.** The corpus reports byte-identical findings; the new kinds
    widen what is accepted and narrow nothing.
  - This settles the *vocabulary* half of #552. The **registry-as-authority** half shipped
    separately: `DG02` now reads `c4_mapping[*].diagram_tags` instead of a literal, so the field
    the registry declares is finally the field the linter consults.

## GD-21 — `total_sections` counts NUMBERED sections; STRUCT01's required set is derived and may exceed it

- **Status:** Accepted — 2026-08-29 · **SemVer:** rides `0.46.0 → 0.47.0` with GD-20,
  change-level **C2**. Ratified on merge; a `framework/**` normative change — human sign-off per
  GATE-SPEC.
- **Issues:** #557

**Bundled with GD-20 under GD-11's rule**, and the conditions are asserted rather than assumed:
independently correct, independently revertible (disjoint keys — GD-20 touches the linter and
`requirements[]`, this touches `metadata` comments and a governance section), ready at the same
moment, and each would otherwise pay a full ~170-file fanout of its own.

⚠️ **The bundle on `0.47.0` is four-way, not two-way.** GD-19, GD-20, GD-21 and GD-22 share a
single fanout. GD-21 was authored when it expected to ride with GD-20 alone; the pairing above
describes that origin, not the shipped release. See the `0.47.0` CHANGELOG entry for why the
four were combined (`GATE-SPEC-E005` is a path check, so one version cannot span four PRs).

**The defect is an unwritten convention, not a wrong number.** `total_sections` counts the
**numbered** sections; `STRUCT01`'s required set is **derived** — top-level keys carrying
`_size_target`, minus `_required: false` / `_required_when_subtype:` — and additionally
includes required **unnumbered backmatter**. **No surface anywhere stated this**, so four
layers legitimately disagree with their own declaration and every reader who compares the two
concludes there is a bug:

| Layer | derived | `total_sections` | why |
| --- | --- | --- | --- |
| BRD | 17 | 16 | `diagrams` + `appendix` |
| ADR | 12 | 10 | `glossary` + `appendix` |
| EARS | 6 | 5 | `glossary` |
| IPLAN | 2 | 6 | **fewer** — 9 of 11 `_size_target` keys are `_required: false` / `_required_when_subtype:` |

**IPLAN diverges downward, which is why this is stated as two independent counts** rather than
as "declared plus backmatter": that generalisation gets IPLAN exactly backwards. It was omitted
from the first draft of this entry and added on OPS-0065 review.

**#557 is the proof this needed writing down.** It was filed as an EARS defect, proposing
`_required: false` on `glossary`. Both halves of its premise were false: both EARS artifacts
carry a glossary, so the marker would have removed a **live** assertion; and EARS was never the
outlier, since BRD and ADR have the identical shape. Four layers agree — PRD, BDD, SPEC and TDD
— because none carries *unnumbered* backmatter; PRD's and BDD's glossaries are numbered sections
and so are already counted. An earlier draft of this entry said "SPEC and TDD agree only", which
undercounts the agreeing set by half and makes a four-layer class read as a two-layer sample.

**`_required: false` marks OPTIONAL CONTENT.** Its one meaning is that the section may be
absent (`PRD`'s `component_decomposition`: *"only required when downstream cites `@threshold`"*).
It does **not** mean "required but unnumbered", and asking it to carry both senses is what
produced #557.

- **Authority:** `governance/LINT_RULES.md` §"What `STRUCT01` requires";
  `tools/sdd_doc_lint` `_load_section_targets`; `layers/02_PRD/PRD-TEMPLATE.yaml`
  `component_decomposition` (the marker's worked example)
- **Consequences:**
  - Stated in **two** places by design: the governance catalogue, and a comment at each of the
    divergent `total_sections:` declarations — because the reader who trips on this is
    looking at the template, not the catalogue.
  - **No template's structure changes and no count moves.** Verified: BRD 17, ADR 12, EARS 6,
    IPLAN 2, unchanged. This is documentation of an existing contract.
  - `tests/conformance/test_required_section_sets.py` already pins each derived count, so the
    edit #557 proposed cannot be made silently.

---

## GD-20 — The carrier changes where a rule LOOKS, never what it decides

- **Status:** Accepted — 2026-08-29 · **SemVer:** framework `0.46.0 → 0.47.0` (MINOR),
  change-level **C2**. Ratified on merge; a `framework/**` normative change — human sign-off
  per GATE-SPEC. This GD-20 entry + the `VERSION`/`CHANGELOG` bump + both
  `FRAMEWORK_SPEC_VERSION` pins + green conformance are the change record; no separate CHG
  artifact.
- **Issues:** #564 · **Census:** `plans/GD15-CARRIER-CENSUS.md`

`GD-15` made YAML the mandatory instance format and changed no rule; `GD-17` gave that mandate
an effective condition precisely because the rules could not yet read the mandated carrier.
This is the enablement.

**Three designs were refuted before this one**, all on facts rather than judgement, and the
census that replaced the third is what made this tractable. Two of its findings are load-bearing
here and are stated so they are not re-derived:

1. **A `.yaml` instance has three shapes**, not one — no fence, a leading `---`
   document-start marker, and a genuine two-document stream. `yaml.safe_load` **raises** on the
   third, so `safe_load_all` + merge is required. A design using `safe_load` would have turned
   six visible fixtures invisible and dropped seven pinned warnings.
2. **`##` lines appear inside `.yaml` files as comments** — in 15 of 24 fixtures. So a heading
   scan would report a document structurally complete on the strength of its comments.

**Decision 1 — the carrier is selected by SUFFIX, never sniffed.** A `.md` file whose body
happens to parse as a YAML mapping must not acquire a frontmatter it does not have. Suffix is a
fact about the file; parseability is a coincidence.

**Decision 2 — the hash input is a MIRROR, not a new vocabulary.** `norm(title)` ← `title`,
`norm(description)` ← `capability`. The transform and the four-part input are unchanged, so the
same content hashes the same on either carrier and a migration is ID-preserving.
`capability` and not `description` because that is the key the template declares; mapping to an
undeclared key would silently hash an empty description. Full table in
`ID_NAMING_STANDARDS.md` §"Structured (YAML) carrier".

**Decision 3 — `requirements[]` gains an optional `realized_by`.** Without it every
YAML-authored requirement classified `AUTHORED`, so `COV01` became **unconditionally blocking**
on the mandated carrier and an ADR-realized requirement had no way to declare itself. The
markdown band's `realized_by:` token and this key are two surfaces for one value.

**Decision 4 — a section is a `##` heading OR a top-level key.** The same structural unit named
two ways; the *required* set is still derived from the template by `_load_section_targets`, so
only the lookup differs and the contract does not.

- **Authority:** GD-15, GD-17; `governance/ID_NAMING_STANDARDS.md` §"Hash algorithm";
  `layers/01_BRD/BRD-TEMPLATE.yaml` `functional_requirements`; `tools/sdd_doc_lint`
  (`_extract_frontmatter`, `_check_required_template_sections`, `scan_fr_elements_yaml`,
  `_fr_elements`)
- **Consequences:**
  - **`tests/conformance/test_carrier_parity.py` is the per-layer carrier-parity assertion
    GD-17 requires**, and it did not exist before. GD-17 also requires a **successor GD entry**
    recording the effective condition as met — **this entry does NOT claim that**, because
    parity is asserted only for the primitives changed here.
  - **Two seams remain open** and are named rather than left implicit: `FM01` calls
    `_split_frontmatter` **directly** and passes vacuously on a YAML instance, and
    `scan_fr_content` behind `rehash_check` is Markdown-only. Until both close, GD-17's clause
    (b) — *every rule returns the same verdict* — is not satisfied.
  - **`rehash --check` still cannot see a `.yaml` file** (`rehash.py` globs `*.md`). The hash
    contract for the structured carrier is *defined* here and *unverified*.
  - **The Markdown path is unchanged**, asserted rather than assumed: the example corpus
    reports byte-identical findings before and after.
  - `tools/sdd_coverage.py` is a consumer **outside** the linter package and was threaded too;
    it is vendored to no mirror, so no `__init__.py`-scoped sweep would have found it.

## GD-19 — GD-14's 5-FR cap becomes measurable without becoming a gate

- **Status:** Accepted — 2026-08-29 · **SemVer:** framework `0.46.0 → 0.47.0` (MINOR),
  change-level **C2**. Ratified on merge; a `framework/**` normative change — human sign-off
  per GATE-SPEC. This GD-19 entry + the `VERSION`/`CHANGELOG` bump + both
  `FRAMEWORK_SPEC_VERSION` pins + green conformance are the change record; no separate CHG
  artifact.
- **Issues:** #540

`GD-14` makes it normative that a BRD document **SHOULD** carry at most five functional
requirements. Nothing measured it: a twelve-requirement BRD passed `sdd_doc_lint`, the
conformance suite and the BRD auditor lens. The rule was guidance a human reviewer applied,
on the one layer most often authored by an LLM reading `_guidance` blocks.

**`FRCAP01` measures it and does not gate it.** `warning` severity in every run mode, with
**no `gate-code` escalation** — a twelve-requirement BRD still passes. #540 records that the
cap was *requested* as guidance rather than as a gate, so escalating here would overrule a
deliberate scope decision under cover of an implementation detail. The
`tests/conformance/test_fr_cap_advisory.py` case that asserts the severity in **both** run
modes is what keeps that true; `COV01` and `REFGRAN01` both escalate, so the pattern a
contributor would copy is the wrong one.

**What counts, and why the boundary was not chosen freshly.** `FRCAP01` counts through
GD-20's `_fr_elements` seam — `scan_fr_elements` on a Markdown carrier, `scan_fr_elements_yaml`
on a YAML one — i.e. the element IDs under the FR section and **before** that section's
literal `Acceptance criteria:` line. `GD-14`'s counting rule was deliberately written against
that same boundary so the cap counts exactly what the coverage gate counts. Acceptance
criteria are not requirements and do not count.

**Escaped requirements DO count**, and this is the entry's one genuinely new decision. A
`Future`-banded or `realized_by:`-tagged FR escapes `COV01` because it carries no coverage
obligation. It is still a requirement the document carries, and the cap is about document
**size**. The two exemptions therefore do not transfer, and a test asserts it so a later
reader does not "simplify" the count by reusing `covered_state_of`.

- **Authority:** GD-14; `layers/01_BRD/BRD-TEMPLATE.yaml` `functional_requirements`
  (`_guidance` size rule and `_authored_form`); `governance/LINT_RULES.md`;
  `tools/sdd_doc_lint` `_fr_elements` (GD-20's carrier seam; dispatches to
  `scan_fr_elements` / `scan_fr_elements_yaml`)
- **Consequences:**
  - **The rule ships with its own fixture, because it could not otherwise be tested.**
    Measured first: of every BRD in the repository, the example corpus's carried **4** visible
    FRs and no acceptance fixture yielded **any**. There was no document a cap check could fire
    on, so it would have been born untestable and green.
    `tests/acceptance/fixtures/negative/brd-fr-cap-exceeded.md` carries seven, two of them
    escaped, and three acceptance criteria that must not count.
  - The example corpus is at 4 of 5 and stays silent — verified, not assumed.
  - `FRCAP01` runs **unconditionally**, not behind `--skip-coverage-gate`: it is a
    document-size advisory, not a coverage gate, so skipping coverage must not hide it.
  - This does **not** make the SHOULD binding. `governance/REVIEW_TEAM.md` still defines the
    pass/fail floor as the deterministic structural check plus "no unresolved P0/P1"; an
    advisory sits above that floor, as `playbooks/01_BRD/auditor.md`'s C3/C4 already do.

## GD-18 — Three independent template gaps and one erratum ship as one MINOR: derived test paths (#550), threshold carriers (#551), IPLAN status ownership (#569), GD-13's figures (#532)

- **Status:** Accepted — 2026-08-28 · **SemVer:** framework `0.44.0 → 0.46.0` (MINOR),
  change-level **C2**. Ratified on merge; a `framework/**` normative change — human
  sign-off per GATE-SPEC. This GD-18 entry + the `VERSION`/`CHANGELOG` bump + both
  `FRAMEWORK_SPEC_VERSION` pins + green conformance are the change record; no separate
  CHG artifact.
- **Issues:** #550, #551, #532, #569

Three verified spec gaps and one erratum to a prior entry, shipped as one release. Each independently trips
`GATE-SPEC-E005`, so shipping them apart would cost five version bumps, five
fanouts and five per-bump founder grants. Bundling is the whole reason they are
one entry; they are otherwise unrelated.

**1. The framework prescribes no test-file layout (#550).** `TDD-TEMPLATE.yaml`
and `SPEC-TEMPLATE.yaml` hardcoded **ten** Python test paths (`tests/unit/test_[module].py`
and siblings) and **seven** pytest-shaped function names. Every other surface in
the chain had already been genericized — `SPEC-TEMPLATE.yaml`'s `language:`,
both of `IPLAN-TEMPLATE.yaml`'s do-not-re-pin statements, and `TDD-MVP-TEMPLATE.yaml`
— so the full TDD template was the one place a language survived, and its own MVP
variant was ahead of it.

The **decision is not "support more languages"**, which is what the consumer report
that surfaced this asked for (per-case `language:` and `test_framework:` fields).
That would re-pin the language one layer down and give the toolchain two owners.
SPEC owns `language:`; TDD and IPLAN derive from it. Placeholders take
`TDD-MVP-TEMPLATE.yaml`'s bare angle-bracket form, one form and not two — the
`# example (Python):` device works in `IPLAN-TEMPLATE.yaml` only because those
entries are list-of-string commands rather than mapping values.

`framework/TESTING_STRATEGY_TDD.md` was **silent** on the subject, so the template
change would have pointed at nothing; it now states the derivation and gives
Python, Go and TypeScript forms as equally conformant. The per-tier distinction
(unit / integration / e2e / security) is language-independent and is retained.

**2. SPEC and TDD gain a `threshold_references` carrier (#551).**
`THRESHOLD_NAMING_RULES.md` normatively designates five layers as threshold
*consumers* and gives TDD a worked example, but two of the five had nowhere to put
the citation. EARS's block is copied in shape, under the same name.

`TDD-TEMPLATE.yaml`'s existing `thresholds:` section is **untouched** and is a
different concept — it holds coverage gates (`unit.coverage_target`, `fail_action`),
not `@threshold:` citations resolving to a PRD or ADR declaration. That name
collision is why this gap survived, and it is the reason the new block is named
`threshold_references` rather than folded into it.

**Neither addition carries `_size_target`**, so `STRUCT01`'s derived required-section
set is unchanged — verified: SPEC stays at 8, TDD at 7.

**3. GD-13's title and its reach claim (#532).** The title said "Two governance
documents" while its own body said "Six authoring surfaces" and enumerated them;
the narrower figure had survived in the most prominent position after review
expanded the sweep. Separately, its successor sentence claimed a governance-prose
guard "would have caught all six" — it reaches **two**. Both corrected in place.
The `0.41.3` CHANGELOG entry is a **published release** and is left unedited; the
correction is stated forward in the `0.46.0` entry.

**4. #557 was in this bundle and was REMOVED on measurement — its premise is
false.** Recorded here rather than dropped silently, because the issue is still
open and the next reader will otherwise re-attempt the same change.

#557 reports that `STRUCT01` derives **six** required EARS sections while
`total_sections`, the five numbered headers and the plugin skill all say five, and
proposes marking `glossary:` `_required: false`. It states the change is latent
because "neither [EARS artifact] has a `glossary` section at all".

**Both do** — `tests/acceptance/fixtures/layer_03_ears/valid/EARS-01_golden.md:54`
and `examples/url-shortener/docs/03_EARS/EARS-01.md:259`. So the marker would not
have been latent: it would have **removed a live assertion**. The acceptance
harness's `template_sections()` applies `_required: false` through a second,
independent derivation, so `tests/acceptance/deterministic/test_layer_ears.py`
would have gone on passing while asserting less — the "a fix can silently disarm
an existing regression test" trap.

**And EARS was never the outlier.** `total_sections` counts **numbered** sections;
the derived set is required sections, which includes required *unnumbered*
backmatter. Measured across all eight layers:

| Layer | derived required | `total_sections` |
| --- | --- | --- |
| BRD | **17** | 16 |
| ADR | **12** | 10 |
| EARS | **6** | 5 |
| PRD / BDD / SPEC / TDD | 15 / 5 / 8 / 7 | 15 / 5 / 8 / 7 |

ADR and BRD have exactly the shape #557 calls a defect, for the same reason
(`glossary` + `appendix`, `diagrams` + `appendix`). SPEC and TDD agree only
because they carry no backmatter. Marking EARS optional would have made it the
one layer of three where required backmatter is unenforced, and put the template
in direct conflict with `platforms/claude-code-plugin/skills/doc-ears/SKILL.md:75`,
which calls the glossary **required**.

`_required: false` means *optional content* — `PRD`'s `component_decomposition`
is "only required when downstream cites `@threshold`". It does not mean
"required but unnumbered", and #557 asked it to carry both senses.

The real defect, if any, is that no surface states that `total_sections` counts
numbered sections only. That is a documentation gap across three layers, not an
EARS marker bug, and it is left to #557 to re-scope.

**5. An IPLAN's `status` is a write target, not a report field (#569).** Real
consumer feedback: an executor created 97 files across 8 IPLANs, reported COMPLETE,
and left every `file_manifest.files[].status` at `NOT_STARTED` — while the
`IPLAN-00_index` registry showed `files_done == files_declared`, which masked it.

**The framework had no contract to violate**, which is the actual defect. The
template declared the fields and the session-startup protocol read them, but
nothing said who writes them or when. `file_manifest._guidance` now states it:
the transitions, that `verified: true` is a separate assertion from `status: DONE`
("the file exists" is not verification), and that an index MAY aggregate these
values but is never where they are recorded first — an index over stale entries
hides drift rather than surfacing it.

This is a **contract**, not enforcement. Nothing yet checks a manifest against the
filesystem, and a stale entry still lints clean.

- **Authority:** `layers/06_SPEC/SPEC-TEMPLATE.yaml` §2 `component_overview.language`
  and §7 `tdd_contracts`; `layers/07_TDD/TDD-TEMPLATE.yaml`;
  `layers/03_EARS/EARS-TEMPLATE.yaml`; `layers/08_IPLAN/IPLAN-TEMPLATE.yaml`
  §2 `file_manifest`; `TESTING_STRATEGY_TDD.md`;
  `governance/THRESHOLD_NAMING_RULES.md`; `governance/AUTHORING_STYLE.md`
  §"Size targets"; `tools/sdd_doc_lint` `_load_section_targets`;
  `AI_ASSISTANT_RULES.md` §"Development Completion Rule"; GD-11 (the bundling
  precedent this entry follows); GD-13 (corrected here)
- **Bundling, against GD-11's four conditions.** GD-11 sets the bar and warns that
  *"the gate made me do it" is not available as a justification*, so the conditions are
  asserted rather than the cost alone: each of the five is **independently correct**
  (none depends on another landing), **independently revertible** (they touch disjoint
  keys — three templates, one governance entry, one strategy doc), **ready at the same
  moment** (all five evidence-complete on the tracker before this bump), and each
  **would otherwise pay a full fanout** of its own.
- **Consequences:**
  - `TDD-TEMPLATE.yaml` and `SPEC-TEMPLATE.yaml` no longer illustrate a concrete
    toolchain. An author copying the template gets a placeholder they must fill,
    which is louder than a wrong default and is the intent.
  - The example corpus is Python and remains conformant — it declares Python in
    its SPEC. It is regenerated wholesale, so no hand-edit follows from this.
  - **`STRUCT01` becomes reachable on EARS the moment a YAML EARS instance
    exists**, and item 4 is what makes it demand five sections rather than six at
    that point. GD-17's effective condition still gates when that is.
  - Item 5 leaves a gap it deliberately does not close: an executor that ignores
    the contract is still undetected. A manifest-vs-filesystem check is the
    successor and needs its own entry. Item 5 also changed **one** authoring
    surface of four — `layers/08_IPLAN/README.md`, `AI_ASSISTANT_RULES.md` and this
    template's own §5 protocol step list still say "update status after completion
    or session end", which is laxer than "write it as you go". Reconciling them is
    successor work, not done here.
  - **Scope is the spec tree only.** `TESTING_STRATEGY_TDD.md` is **not vendored**
    to the plugin bundle (which carries `governance/`, `layers/`, `playbooks/`,
    `registry/` and the guide) — so the templates carrying the new placeholders are
    synced while the document explaining *why* they are placeholders is not.
    Platform authoring surfaces are out of scope here and must add their own, per
    the caveat GD-09 and GD-17 record for their guards.
  - **`IPLAN-MVP-TEMPLATE.yaml` is NOT reconciled and this entry does not decide
    it.** Its manifest declares `not_started|in_progress|completed|blocked` —
    different case, `completed` for `DONE`, an extra `blocked`, no `PARTIAL`. That
    divergence is #438's territory, which GD-16 likewise declined to settle. Item 1
    praises the MVP set for being *ahead* of the full templates on test paths; item
    5 must not be read as claiming the same for status.

---

## GD-17 — Instance format has exactly one normative source, and its mandate takes effect on a testable outcome rather than a component list

- **Status:** Accepted — 2026-08-28 (ratified on merge; a `framework/**` normative change —
  human sign-off per GATE-SPEC. This GD-17 entry + the `VERSION`/`CHANGELOG` bump + both
  `FRAMEWORK_SPEC_VERSION` pins + green conformance are the change record, per the GD-05..GD-16
  precedent — no separate CHG artifact). SemVer **minor** (`0.43.0 → 0.44.0`), change-level
  **C2**. *(GD-15 and GD-16 omitted their version pairs; stating this one explicitly is part of
  what this entry repairs.)*
- **Context.** GD-15 made YAML the mandatory **instance** format for layers 1-8 and, in the same
  entry, recorded that it "does not adopt the frontmatter contract (that design's D1 owns it)".
  The spec therefore mandated a format that no rule could read. **Measured** on a BRD authored
  exactly as `BRD-TEMPLATE.yaml` prescribes: **17 `STRUCT01` errors** — including for sections
  physically present as YAML keys — while the identical content as Markdown produced **zero**
  findings, and `scan_fr_elements` discovered **0** gated FRs against 1, so `COV01` passed
  vacuously. The gate was simultaneously unpassable and blind on the mandated format.
- **The mandate was also diffuse.** Seven spec surfaces asserted it: `DOC_GOVERNANCE_CORE.md`
  Principle 2 and §Template Policy, `LAYER_REGISTRY.yaml`'s header + `extensions`, GD-15 itself,
  `layers/01_BRD/README.md` §Document Formats, `governance/ID_NAMING_STANDARDS.md`'s File-Naming
  table, and `layers/04_BDD/BDD-00_index.TEMPLATE.md` §File Format. Two of them contradicted the
  registry outright, and one — the BDD index — states the value in prose with no filename token,
  so no mechanical check could ever have seen it drift.
- **Decision.** Three rules, ratified together.
  1. **One normative source.** `LAYER_REGISTRY.yaml` `extensions` is the **authority** for
     instance format. Every surface that **asserts the format as a rule** states the value and
     cross-references it; none re-specifies it. Surfaces that merely *use* a filename in an
     example or a naming table are not required to carry the cross-reference — they are held to
     the registry mechanically by `test_instance_format_ssot.py`, which is the stronger guarantee.
     This bound is deliberate: requiring a prose cross-reference on every filename mention would
     grow the obligation without adding a check. This applies **GD-09 rule 2** — *"every mandating layer states its contract
     in-layer"* — rather than GD-09 rule 1 alone: the layer keeps its statement, and only the
     *authority* is centralized. Deleting the in-layer statements would remove the text an author
     actually reads.
  2. **The effective condition is an outcome, stated once, here.** The instance-format mandate
     takes normative effect when, for every layer, a reference instance authored in that layer's
     `extensions` format satisfies **rule-applicability parity** with the equivalent Markdown
     form: (a) it lints with **zero** findings, and (b) **every rule that applies to the Markdown
     form applies to it and returns the same verdict**. Clause (b) is deliberately stated as
     applicability rather than as a list of result classes — "element and coverage results" would
     omit `BDD-SCHEMA-001` (schema validation) and `SEED01` (silently skipped when its carrier is
     absent), both of which satisfy clause (a) *vacuously*, which is the failure this condition
     exists to exclude.
     **Evaluator and state carrier.** The condition is evaluated by a per-layer carrier-parity
     assertion in the conformance or acceptance tier — the same shape as
     `tests/conformance/test_instance_format_ssot.py`, comparing a YAML reference instance against
     its Markdown counterpart rule by rule. The condition's *state* is carried by a successor GD
     entry that records it as met; **no surface may infer it from an issue being closed**, since
     closing #564 updates nothing a reader consults. Operationally this is the completion of the carrier-aware work in
     [#564](https://github.com/vladm3105/aidoc-flow-framework/issues/564).
     **Why an outcome and not a list:** three successive enumerations were each short. `doc_id`
     alone leaves 17 `STRUCT01` errors, because `STRUCT01` resolves sections from `##` headings
     and never reads frontmatter. Adding a carrier-aware structural check still leaves `COV01`
     vacuous, because FR discovery is a third primitive. `BDD-SCHEMA-001` and the EARS→BDD edges
     (fence matcher) and `SEED01` (silently skipped) are a fourth and fifth. An outcome cannot be
     under-enumerated.
  3. **The negative property is guarded.** `tests/conformance/test_instance_format_ssot.py`
     asserts that no spec surface names a layer instance whose extension is absent from that
     layer's `extensions`, with two exemptions carrying their own mutation tests: index-doc
     mentions (exempt **at the mention level**, since two of the nine sit outside index files)
     and `DECISIONS.md`, whose `IPLAN-01.md` reference describes a real corpus artifact inside a
     ratified record.
- **Security (GATE-SPEC-W003).** Agent-facing governance guidance changes. Assessed against
  `SECURITY_REVIEW.md`: no credentials or personal data introduced (T1); no instruction is taken
  from external or untrusted content — every edit derives from the repo's own registry and
  measured linter behaviour (T2); provenance is recorded for each carrier (T3); the change
  **narrows** rather than broadens authority, since it removes an in-effect mandate that no rule
  could enforce and gates its return on a testable outcome (Rule 4); no active content is
  introduced (T4). No blocking finding.
- **Consequences.** `framework/VERSION` `0.43.0 → 0.44.0`; both `FRAMEWORK_SPEC_VERSION` pins
  re-declare; the vendored plugin bundle is re-synced. The example corpus and acceptance goldens
  remain `.md` and are **conformant**, because the mandate is not yet in effect — which is what
  unblocks [#555](https://github.com/vladm3105/aidoc-flow-framework/issues/555) from a
  regeneration that would otherwise have produced ~17 errors per BRD.
  **Scope is the spec only** — platform authoring surfaces state their own filenames and must add
  their own lock, the same caveat GD-09 recorded.
- **Authority:** `registry/LAYER_REGISTRY.yaml` `extensions` + header; `DOC_GOVERNANCE_CORE.md`
  Principle 2 and §Template Policy; GD-09 rules 1-2; GD-15;
  `plans/INSTANCE-FORMAT-SSOT-001-PLAN.md`.

## GD-16 — An IPLAN file-manifest entry carries its TDD test cases in a line-local `tdd_ref` field, not in the traceability block

- **Status:** Accepted — 2026-08-26 (ratified on merge; a `framework/**` normative
  change — human sign-off per GATE-SPEC. This GD-16 entry + the `VERSION`/`CHANGELOG`
  bump + both `FRAMEWORK_SPEC_VERSION` pins + green conformance are the change record,
  per the GD-05..GD-15 precedent — no separate CHG artifact). SemVer **minor**,
  change-level **C2**.
- **Context:** the element-level trace chain is enforced BRD→PRD (`COV01`),
  EARS/BDD→SPEC/TDD (`COV02`) and BDD-scenario→TDD-case (`ACC01`), then stops.
  `REALIZING_LAYERS` has no IPLAN key, so nothing asks whether a TDD test case reached
  an IPLAN. Measured on the example corpus: `TDD-01` declares 35 test-case elements and
  `IPLAN-01` cites **7** of them in the trace graph — while the IPLAN audit returned
  PASS at 100/100 with zero blocking findings (issue #543).
- **The naive fix does not work, and that is why this GD exists.** A coverage rule built
  on the document-scoped realization primitive (`_element_realizing_citers`, which
  returns citer *documents*) is silenceable by one line: `IPLAN-01.md` already carries a
  §6 traceability bullet with five `@tdd:` tokens self-described as "representative
  anchors" for the 35-case contract, and expanding that bullet to 35 would satisfy such
  a rule with **no change to what the IPLAN builds**. `ACC01` documents this same
  vacuous-pass loophole for BDD scenarios and closes it with a **line-local carrier**
  parse — a key whose *value* is the tag (`bdd_scenario:` / `bdd_ref:`), so the citation
  and its carrier share one line.
- **Decision:** an IPLAN file-manifest entry carries `tdd_ref`, whose value is a `@tdd:`
  tag. Normative properties:
  1. **The value is the tag and MUST be quoted** — `@` is a YAML reserved indicator, so
     an unquoted value fails to parse. Several cases may share one scalar,
     pipe-delimited.
  2. **The key and the tag share one line.** A citation appearing only in the
     traceability block is **not** a build record.
  3. **Optional per entry.** Completeness is judged from the TDD side, not by requiring
     every entry to name a case.
  4. The carrier is a **field-name token**, so it is serialization-independent — the
     same rule holds wherever the manifest is rendered.
- **What this does NOT decide.** It does not add the coverage rule (`COV04`), which is a
  successor change and must be carrier-scoped per the reasoning above; it does not
  reconcile `IPLAN-MVP-TEMPLATE.yaml`'s bare-list manifest shape with the canonical
  `files:` shape (issue #438) — the carrier is line-local and attaches to either; and it
  does not touch `file_manifest`'s existing status/verified semantics.
- **Consequences:** **MINOR** — additive template keys and a new governance rule; no
  existing artifact becomes non-conformant, because the field is optional. A prerequisite
  linter defect had to land first: a `@tdd:` tag ending a quoted YAML scalar was silently
  discarded from the trace graph because the value capture did not terminate on a quote
  (issue #542) — without that fix the carrier is unusable in the normative format.
- **Authority:** `layers/08_IPLAN/IPLAN-TEMPLATE.yaml` §2 `file_manifest`,
  `layers/08_IPLAN/IPLAN-MVP-TEMPLATE.yaml`, `layers/08_IPLAN/README.md`
  §"TDD-case carrier"; guarded by `tests/conformance/test_iplan_carrier.py`;
  `plans/IPLAN-TDDREF-001-PLAN.md`; `plans/IPLAN-LAYER-REVIEW-001-DESIGN.md`.

---

## GD-15 — YAML is the mandatory format and the source of truth for layer artifacts; Markdown is optional, descriptive, and generated

- **Amended by GD-17 (2026-08-28).** The instance-format mandate below is **not unconditionally
  in force**: GD-17 gives it an effective condition and makes `LAYER_REGISTRY.yaml` `extensions`
  its single normative authority. Read GD-17 before acting on this entry.
- **Status:** Accepted — 2026-08-26 (ratified on merge; a `framework/**` normative
  change — human sign-off per GATE-SPEC. This GD-15 entry + the `VERSION`/`CHANGELOG`
  bump + both `FRAMEWORK_SPEC_VERSION` pins + green conformance are the change record,
  per the GD-05..GD-14 precedent — no separate CHG artifact). SemVer **minor**,
  change-level **C2**.
- **Context:** the spec constrained template format and left instance format
  undeclared, and three surfaces disagreed about what an artifact actually is:
  - `DOC_GOVERNANCE_CORE.md` Principle 2 — "All templates are `.yaml`. MD is for
    indexes and reference docs only." Scoped to **templates**; silent on instances,
    and its second clause is contradicted by every artifact the corpus ships.
  - `DOC_GOVERNANCE_CORE.md` §Template Policy "Unified YAML only" — also
    template-scoped. `OKF-CONFORMANCE-001-DESIGN.md` records a reviewer reading this
    bullet as an instance-format mandate; it was not one, and nothing else was.
  - `LAYER_REGISTRY.yaml` — `extensions: [.yaml]` on **all eight** layers (the
    normative field), under a header comment asserting "Layers 01-07 use Markdown
    (.md)". The comment was about the `<X>-00_index.TEMPLATE.*` docs and read as a
    statement about instances, contradicting the file's own data.

  The measured state was a three-way disagreement: registry all-`.yaml`, acceptance
  goldens mixed (5 `.md` + 3 `.yaml`), example corpus all-`.md`. Under that spread no
  engine, lint rule, or conformance test could be written against "the artifact format",
  because there was no declared one.
- **Decision:** YAML is the **mandatory format and the source of truth** for every
  artifact of layers 1-8 and for the templates that produce them. **Markdown is
  optional and descriptive** — a rendering of the YAML, or additional explanatory
  material around it. Three normative consequences:
  1. Markdown never carries a fact the YAML does not. A fact existing only in
     markdown is a defect of the same class as two records of one count.
  2. A `.md` file restating YAML content is **generated, not authored**. Hand-editing
     it is destroyed by the next generation run; a stale rendering is a drift defect
     and needs a guard, not a convention.
  3. `LAYER_REGISTRY.yaml` `extensions` is the normative instance-format field, and
     its `<X>-00_index.TEMPLATE.*` header comment is scoped to index docs only.
- **What this does NOT decide.** It does not settle the five `status` vocabularies
  (`OKF-CONFORMANCE-001-DESIGN.md` D4 defers those whole), does not adopt the
  frontmatter contract (that design's D1 owns it), and does not itself make any tree
  OKF-conformant — see Consequences.
- **Consequences:** **MINOR, not patch.** The prior guidance was not wrong, it was
  **absent** at the instance scope; declaring a contract where none existed is
  additive, and it re-grades surfaces that were previously unconstrained rather than
  non-conformant.
  - The example corpus is inverted with respect to this decision (all `.md`, no `.yaml`
    sources). Per `CLAUDE.md`, correct it by **regeneration**, never by hand-editing
    the artifacts.
  - Acceptance goldens for layers 1-5 are `.md` and become non-conformant instances.
  - **OKF interaction.** Google Cloud's Open Knowledge Format v0.2 addresses `.md`
    files, so a YAML-normative tree violates no OKF rule and contributes **zero
    concepts** — conformant and empty. OKF conformance therefore requires a generated
    `.md` projection carrying the OKF frontmatter, with the YAML remaining the source.
    This decision resolves `OKF-CONFORMANCE-001-DESIGN.md` open question 1 with an
    option that document did not list; its Stage 1 instruction to put `type` into the
    26 templates is superseded — templates carry `artifact_type` and `title`, and the
    OKF-facing `type` is emitted by the projection generator and never enters the YAML.
- **Authority:** `DOC_GOVERNANCE_CORE.md` Principle 2 and §Template Policy;
  `registry/LAYER_REGISTRY.yaml` `extensions` + header;
  `plans/OKF-CONFORMANCE-001-DESIGN.md`; `plans/IPLAN-LAYER-REVIEW-001-DESIGN.md` F-0.

---

## GD-14 — A BRD document SHOULD carry at most 5 functional requirements; the iteration cycle keeps its 5-15 and may span several documents

- **Status:** Accepted — 2026-08-25 (ratified on merge; a `framework/**` normative
  change — human sign-off per GATE-SPEC. This GD-14 entry + the `VERSION`/`CHANGELOG`
  bump + both `FRAMEWORK_SPEC_VERSION` pins + green conformance are the change record,
  per the GD-05..GD-13 precedent — no separate CHG artifact). SemVer **minor**
  (`0.41.3 → 0.42.0`), change-level **C2**.
- **Context:** the BRD layer had no requirement-count ceiling — the only split trigger
  was `file_organization`'s 50,000-token threshold, and token count is a poor proxy for
  how much distinct capability one document commits to. **Six** surfaces described a
  BRD's size or its relationship to a cycle, and they did not agree:
  - `layers/01_BRD/README.md` — "5-15 requirements **per BRD**" (per document).
  - `layers/01_BRD/BRD-TEMPLATE.yaml` §7 — "5-15 requirements total **per MVP cycle**".
  - `layers/01_BRD/BRD-TEMPLATE.yaml` `document_scope` — "(5-15 requirements)", unit unstated.
  - `layers/01_BRD/BRD-TEMPLATE.yaml` `lifecycle` — "Each BRD represents ONE iteration cycle".
  - `platforms/hermes/agent-skills/.../sdd-orchestrator/root-docs/README.md` — a lifecycle
    diagram reading "MVP BRD-01 … 5-15 features", plus "Each BRD represents one iteration cycle".
  - `platforms/claude-code-plugin/skills/doc-brd/SKILL.md` — "One BRD = one MVP iteration
    (5–15 focused requirements)", the operative authoring instruction on Platform B.
- **Rationale — and what it is NOT.** The cost of an oversized BRD is **author attention
  and review surface**: one document bundling fifteen capabilities is authored in one
  pass, reviewed as one artifact, and versioned as one unit, so a change to any one
  capability re-opens all fifteen. It is **not** a traceability argument. Coverage in
  this framework is element-level (`governance/TRACEABILITY.md` COV01/COV02, the linter's
  `doc_index`/`element_index`), so document count does not affect fan-out granularity at
  all — verified in review, and recorded here because the first draft of this entry
  argued the opposite and was self-refuting.
- **Decision:** a BRD document **SHOULD** carry at most 5 functional requirements. Beyond
  five, start a new document of the same type (BRD-02, BRD-03) and register it in the
  `BRD-00` index. This is a second split trigger beside the token threshold, whichever is
  reached first. The **cycle total is 5-15 per cycle**; the cap implies a floor of
  ceil(N/5) documents, which is a floor and **not** a ceiling on set size — a set may hold
  more documents for reasons unrelated to size (one platform BRD plus several feature
  BRDs), each independently subject to the cap. Splitting a single BRD into sectioned
  files remains forbidden; the unit of splitting is the document.
- **Linking.** Use `@depends: BRD-NN` **only** for a genuine hard prerequisite —
  `TRACEABILITY.md` defines it as "downstream cannot exist without upstream". A document
  created purely because the previous one reached the cap is a **sibling** within one
  cycle, not a dependent; record that in the `BRD-00` index and in prose.
- **Counting rule (normative, because a cap nobody can count cannot be applied).** One
  requirement, stated per authored shape because the layer has three: in the **authored
  markdown** form, the element IDs under `## 7. Functional Requirements` and before that
  section's literal `Acceptance criteria:` line — the boundary already ratified in
  `BRD-TEMPLATE.yaml` `_authored_form` rule 2 and implemented by `sdd_doc_lint`'s
  `scan_fr_elements`, so the cap counts exactly what the coverage gate counts; in the
  **full structured template**, the entries of `requirements[]`; in the **MVP skeleton**,
  the entries of `functional_requirements[]`, whose `acceptance_criteria` is a field of
  the requirement. Worked example: `examples/url-shortener`'s BRD-01 carries **8**
  `BRD.01.07.*` element IDs but **4** requirements — the other four follow its
  `Acceptance criteria:` line. Compliant, and it would not have been under an
  ID-counting rule.
- **Consequences:** **MINOR, not patch.** The prior guidance was not wrong, it was a
  different policy, so this changes what the spec instructs authors to produce rather
  than correcting an error — the GD-03 shape, not GD-13's erratum shape. Note it is
  *restrictive* normative where GD-03's minor rested on additive; pre-1.0 makes minor
  right either way. Two scope limits, stated so they are not read as oversights:
  - **Existing documents over the cap are not required to split retroactively.** The
    triggers govern new authoring.
  - **No other layer is capped.** PRD in particular still says "List 5-15 must-have
    features for MVP" per document, and the attention argument above would apply there
    too; extending it was out of scope for this change and is deliberately not done here.
  - **Not enforced, by decision rather than by oversight.** `sdd_doc_lint` has no
    FR-count check and none was added, because this was scoped as guidance a reviewer
    applies. No auditor check was added either. ⚠️ The first draft of this entry
    justified that by claiming a C-numbered check "would make the SHOULD binding"; that
    is **false** — `governance/REVIEW_TEAM.md` makes the gate structural plus "no
    unresolved P0/P1", and `playbooks/01_BRD/auditor.md` already ships non-blocking P2
    and P3 checks, so a P3 check would not bind. The absent enforcement is tracked as
    [#540](https://github.com/vladm3105/aidoc-flow-framework/issues/540) rather than
    argued away.
- **Authority:** `layers/01_BRD/BRD-TEMPLATE.yaml` §7 `functional_requirements` and
  `file_organization`; `layers/01_BRD/README.md`; `chg/gates/GATE-SPEC_FRAMEWORK.md`.

---

## GD-13 — Six authoring surfaces had drifted from GD-03's ratified citation granularity, so reconciling them is an erratum, not a rule change

- **Status:** Accepted — 2026-08-23 (ratified on merge; a `framework/**` normative
  change — human sign-off per GATE-SPEC. This GD-13 entry + the `VERSION`/`CHANGELOG`
  bump + both `FRAMEWORK_SPEC_VERSION` pins + green conformance are the change record,
  per the GD-05..GD-12 precedent — no separate CHG artifact). SemVer **patch**
  (`0.41.2 → 0.41.3`), change-level **C2**.
- **Context:** GD-03 (Accepted 2026-06-27) ratified that every `@<layer>:` trace
  citation to an **element-declaring** layer (`@brd @prd @ears @bdd @adr @tdd`) MUST
  be element-level, that only `@spec:` / `@iplan:` remain document-level (those two
  layers being element-ID-exempt), and that **self-tags and downstream
  forward-pointers are exempt** because they are not trace citations. `REFGRAN01`
  has enforced this since — `tools/sdd_doc_lint/__init__.py`
  `_REFGRAN_ELEMENT_DECLARING`, a warning in `build` and an **error** in `gate-code`.
  Six authoring surfaces had never been reconciled to it and went on telling authors
  the opposite:
  - `ID_NAMING_STANDARDS.md` §"Reference granularity" — GD-03's own named
    **authority** — listed ADR and TDD among the layers a document-level citation may
    name, contradicting the bullet immediately below it in the same file.
  - `TRACEABILITY.md` carried the identical proposition, citing GD-03 while stating
    its inverse.
  - `playbooks/05_ADR/auditor.md` C5 and `playbooks/07_TDD/auditor.md` C5 *mandated*
    the dash form for whole-document pointers, penalty P3 — so an auditor obeying the
    playbook produced artifacts `REFGRAN01` flags.
  - `layers/08_IPLAN/IPLAN-TEMPLATE.yaml` declared `@spec` **and** `@tdd`
    document-level "by design"; the `@spec` half is correct, the `@tdd` half is not.
  - `platforms/claude-code-plugin/agents/requirements-analyst.md` presented
    `@adr: ADR-NN` as the canonical cumulative-upstream form.
- **Decision:** reconcile all six to GD-03. The dash form survives only where GD-03
  already exempts it — a document's own self-tag, a downstream forward-pointer, and
  `@depends: TYPE-NN` — and a genuine whole-document dependency is stated in prose,
  never as a document-level trace tag. GD-03 itself is unchanged and is not amended:
  this records that its authority text had drifted from it.
- **Consequences:** **PATCH, not MINOR.** GD-03's own MINOR grade covered
  *introducing* the rule; nothing here changes what the linter accepts, what a
  conformant document may contain, or any consumer-visible behaviour — six documents
  stop disagreeing with a rule that was already ratified and already enforced. The
  drift is the same shape GD-12 was written about, one layer up: a rule stated in
  several documents where only some get corrected. **Not yet guarded** — there is no
  conformance test asserting the document-level-permitted set is `{SPEC, IPLAN}`
  across `ID_NAMING_STANDARDS.md`, `TAG_SYNTAX.md`, `TRACEABILITY.md` and
  `_REFGRAN_ELEMENT_DECLARING`; it is the obvious successor to this entry and is
  tracked as #531. Such a guard **would catch two** of the six above, not all six
  — an earlier form of this sentence claimed all six, which over-reports its
  reach. The other four
  are two auditor playbooks, a layer template and a plugin agent, none of which a
  governance-prose guard reads. A class-wide scan over those surfaces was measured
  and rejected: 51 token hits across 29 files, overwhelmingly exempt (self-tags,
  downstream forward-pointers, `FAIL:` counter-examples), so an exemption model at
  that ratio either false-positives and blocks CI or under-covers and reads as
  complete. Those surfaces are covered by `REFGRAN01` on the artifacts they
  generate — a downstream detector with regeneration latency, which is how the
  surviving drift in #563 was found.
- **Authority:** `ID_NAMING_STANDARDS.md` §"Reference granularity"; GD-03;
  `chg/gates/GATE-SPEC_FRAMEWORK.md`.

---

## GD-12 — The gate approval form is the executed surface, so its agreement with the gate definitions is a conformance invariant, not editorial care

- **Status:** Accepted — 2026-08-16 (ratified on merge; a `framework/**` normative
  change — human sign-off per GATE-SPEC. This GD-12 entry + the `VERSION`/`CHANGELOG`
  bump + both `FRAMEWORK_SPEC_VERSION` pins + green conformance are the change record,
  per the GD-05..GD-11 precedent — no separate CHG artifact). SemVer **patch**
  (`0.41.0 → 0.41.1`), change-level **C2**.
- **Context:** three defects filed from a downstream audit
  ([#433](https://github.com/vladm3105/aidoc-flow-framework/issues/433),
  [#434](https://github.com/vladm3105/aidoc-flow-framework/issues/434),
  [#445](https://github.com/vladm3105/aidoc-flow-framework/issues/445)) all land on
  `chg/templates/GATE_APPROVAL_FORM.md`. Each gate's checks are stated in three
  documents — the gate definition, `chg/gates/GATE_ERROR_CATALOG.md`, and the form —
  and **only the third is filled in**. #434 records the observed cost: a downstream
  project produced two change records from the form alone, concluding "no second CHG
  record is minted", the inverse of what `GATE-CODE_IMPLEMENTATION.md` §6.2 requires.
  The three documents had drifted in three ways:
  - **Omission.** `GATE-03-E008` is defined and catalogued but absent from the form,
    so a GATE-03 review driven from the form never considers it. It is one of the
    gate's two Security-category ERRORs and the only one the form omits (`E002` is
    the other and is present). The form does carry `GATE-03-W001: CVE reference
    added` four lines below, which reads as CVE coverage and masks the absence — but
    W001 is a non-blocking nudge and E008 is blocking.
  - **Stale restatement.** The form restated tag *counts* (EARS 2 / BDD 3 / ADR 4)
    that match neither `LAYER_REGISTRY.yaml` (`[prd]`, `[ears]`, `[ears, bdd]` — 1/1/2)
    nor the gate's own check table.
  - **No routing.** The form presents every gate as a section of one document,
    which is right for an `Upstream` entry and wrong for a `Feedback` entry whose
    root cause is upstream — that becomes a separate, dependent CHG under §6.2.
    Neither document referenced the other, and the form collects the deciding datum
    (§1.1 Entry Gate) without using it. This is #434: the §2 note within bundle
    item 1, plus items 4 and 5, exist for it.
  **Two of the three defects were larger than filed, and the fixing session's
  censuses are what found the remainder.** #433 compared **five** gates; there are
  six, and `GATE-SPEC-W003` (also Security, also defined and catalogued) is likewise
  missing from the form. #445 named two carriers of the over-stated ADR requirement
  and there are three: `GATE_ERROR_CATALOG.md` §9.1/§9.2 carries it too. That one was
  missed by **phrasing, not by absence of a count** — an earlier draft of this entry
  claimed the catalog stated the chain with no count anywhere, which is false (`:206`
  "Add 4 traceability tags to ADR", `:215` "Add all 4 upstream traceability tags"),
  and it also claimed two carriers were missed when #445 names `GATE-03:233`
  explicitly. The accurate lesson is narrower and is the one `CLAUDE.md`
  § "Durable traps → Process" already states: a sweep anchored on one phrasing of a
  fact under-covers, because the same fact has many spellings. Define the class as
  *the requirement statement*, not as the string searched for.
- **Decision:** correct all six statements (enumerated in the `CHANGELOG` entry with
  the counting unit named, because the figure is otherwise not re-derivable), add the
  two missing form rows, wire the cross-references that route a bubble-up correctly,
  and **lock the omission class in conformance** —
  `tests/conformance/test_governance.py::GateCheckIdParity` asserts set equality of
  check ids across all six gates × `{E, W}` × the three surfaces, comparing the form's
  **fillable items** rather than its mentions. The guard is stated as an invariant
  with a direction, because the two directions are different defects: a code in the
  definition but not the form is a check nobody performs; a code in the form but not
  the definition is a check with no criteria.
- **What is in the bundle:**
  1. `chg/templates/GATE_APPROVAL_FORM.md` — adds the `GATE-03-E008` and
     `GATE-SPEC-W003` rows; corrects §2.2's tag counts to 1/1/2 naming the actual
     tags; adds a §2 note routing a GATE-CODE-entry change with an upstream root
     cause to `GATE-CODE_IMPLEMENTATION.md` §6.2 rather than onto this form.
  2. `chg/gates/GATE-03_REQUIREMENTS_ARCHITECTURE.md` — E007's resolution template
     states the 2-tag rule, and states what E007 does **not** fail on.
  3. `chg/gates/GATE_ERROR_CATALOG.md` — the same correction at its §9.1
     quick-reference row and its §9.2 resolution template (the third carrier).
  4. `chg/gates/GATE-CODE_IMPLEMENTATION.md` — §6.2 step 2 names the artifact the
     new CHG carries, closing the loop the form's new note opens.
  5. `chg/CHG-TEMPLATE.yaml` — the Feedback routing cell stopped at `SPEC`, which
     read as a floor; extended to the reach `GATE-CODE_IMPLEMENTATION.md:151` and
     `GATE_INTERACTION_DIAGRAM.md:109` already state, including ADR, which §6.1
     routes to GATE-03 alongside BDD and EARS.
  6. `tests/conformance/test_governance.py` — the parity guard.
- **A near-miss worth keeping, because it inverts this entry's own thesis.** The
  first draft of items 2 and 3 wrote *"do NOT add `@brd` or `@prd` — those are
  transitive"*. That is a **new prohibition on a blocking ERROR**, and four spec
  surfaces contradict it: `ADR-TEMPLATE.yaml` ("optional provenance … not
  required"), `TRACEABILITY.md` (`required_tags` is the *minimum* set; a layer MAY
  carry provenance tags), `REVIEW_TEAM.md` ("decorative lineage … are permitted"),
  `playbooks/05_ADR/auditor.md`. `AI_ASSISTANT_RULES.md` forbids *fabrication* —
  tags for **absent** upstream layers — not a resolvable provenance tag. Fixing a
  document that disagreed with the registry by making it disagree with four other
  documents is the same defect one layer down; it was caught in pre-push review, not
  by any test, and no test would have caught it.
- **Why PATCH.** Every item restores agreement with a normative source that already
  said the correct thing — the registry, the gate check tables, §6.2,
  `GATE-CODE:151`. Nothing here asks an author for anything that was not already
  required, which is what separates this from GD-11's MINOR (where `@chg:` gained a
  definition it had never had). The near-miss above is the counter-example that
  makes the test meaningful rather than rhetorical: had it shipped, PATCH would have
  been the wrong level.
- **Rule 1 (≤3 doc surfaces per governance PR) is exceeded here, deliberately and on
  GD-11's ratified reasoning.** GATE-SPEC-E005 binds every concurrent `framework/**`
  edit to one `VERSION`, so a spec release cannot split below `VERSION` +
  `CHANGELOG` + this entry + the corrected documents. The commit message carries the
  audit-trail line the rule requires. Splitting would produce three releases of one
  correction, each paying a ~170-file fanout — the cost argument GD-11 sets out,
  applied to surfaces rather than to PRs.
- **Consequences:** platforms re-pin to `0.41.1`; the vendored plugin bundle is
  regenerated by `tools/sync-plugin-framework.sh`. **Propagation order is
  load-bearing** — `framework/VERSION` → `scripts/sync-version-refs.sh` →
  `tools/sync-plugin-framework.sh`; reversing it lands drifted bundled playbooks and a
  red bundle guard.
- **Known limits of the new guard, established by mutation and not by assumption.**
  (i) On the *definition and catalog* sides it compares the set of ids a document
  mentions, not table structure. Each names a code more than once — check table,
  error-catalog section, resolution heading — so deleting `GATE-03-E008`'s row from
  GATE-03's §3.1 leaves the id present at its §7.1 row and its resolution heading,
  and the guard stays green. Out of scope deliberately: anchoring on rows would make
  the check positional across six heterogeneous documents, and this direction is
  benign — the code still resolves in the catalog and the form, so the check is
  still performed. (ii) Only `E` and `W` are compared, and the id pattern
  matches exactly three digits; `GATE_ERROR_CATALOG.md:24` also defines `I` (Info).
  Neither exists today, so nothing is unguarded now.
  **A third limit was found by review, not by us, and is now closed.** The first
  draft compared the form's *mentions*. Deleting `GATE-03-E008`'s row and adding a
  prose sentence naming it left the guard green — #433's own failure mode surviving
  in the direction the guard claimed to cover. The form side now compares fillable
  items (a line carrying `[ ]`), which matches both the E-code table cell and the
  W-code checkbox without anchoring on either. The general lesson: a guard written
  beside its fix inherits the fix's framing, and "present in the document" was the
  framing that let the original defect exist.
- **Precedent set.** Where the spec states one fact in more than one document and
  one of them is the surface actually executed, the agreement is a conformance
  invariant. The drift here is undetectable by reading any one of the three
  documents, because each is internally consistent — and it did not need years of
  accumulation. `817d9a1a` added **both** `GATE-03-E008` and `GATE-SPEC-W003` to
  their gate definitions and to the catalog in one commit, and did not touch the
  form. That same commit edited `tests/conformance/test_governance.py` — to add
  `SECURITY_REVIEW.md` to `EXPECTED_FILES`, an exact-set guard over *filenames*. So
  the suite was extended in the very change that introduced the drift and still
  could not see it: a file-existence list is not a cross-document check. One edit to
  a document set with no cross-document check is sufficient to produce this.

---

## GD-11 — Four independent spec corrections ship as one MINOR because GATE-SPEC binds them to a single `VERSION`, not because they are one change

- **Status:** Accepted — 2026-08-16 (ratified on merge; a `framework/**` normative
  change — human sign-off per GATE-SPEC. This GD-11 entry + the `VERSION`/`CHANGELOG`
  bump + both `FRAMEWORK_SPEC_VERSION` pins + green conformance are the change record,
  per the GD-05..GD-10 precedent — no separate CHG artifact). SemVer **minor**
  (`0.40.0 → 0.41.0`), change-level **C2**.
- **Context:** Four defects were fixed as four separate PRs
  ([#460](https://github.com/vladm3105/aidoc-flow-framework/pull/460)/[#444](https://github.com/vladm3105/aidoc-flow-framework/issues/444),
  [#461](https://github.com/vladm3105/aidoc-flow-framework/pull/461)/[#448](https://github.com/vladm3105/aidoc-flow-framework/issues/448),
  [#462](https://github.com/vladm3105/aidoc-flow-framework/pull/462)/[#450](https://github.com/vladm3105/aidoc-flow-framework/issues/450),
  [#463](https://github.com/vladm3105/aidoc-flow-framework/pull/463)/[#446](https://github.com/vladm3105/aidoc-flow-framework/issues/446)),
  each correct and each independently reviewable. All four were **red on GATE-SPEC
  E005**: they touch `framework/**` without bumping `framework/VERSION`.
  **They *could* have merged independently, and an earlier draft of this entry wrongly
  said they could not.** E005 as implemented (`tests/chg/spec_gate.py:84`) requires only
  that `framework/VERSION` appear in the diff; it does not constrain the value. Four
  sequential merges at `0.41.0`/`0.42.0`/`0.43.0`/`0.44.0` would each pass, and this
  repo already serialises doc PRs that way. The argument for folding is therefore
  **cost, not impossibility**: four rebases, four version bumps, four ~170-file
  fanouts and four sets of platform re-pins, to ship four corrections that are ready
  at the same moment. Stating it as a blocker was the error D-0068 names — an
  unverified blocker stalls work on a decision nobody needs to make.
- **Decision:** fold the four into one PR carrying the `0.41.0` bump, this entry, both
  `FRAMEWORK_SPEC_VERSION` pins and the sync fanout. The four fixes are **not**
  re-litigated here; each keeps its own `CHANGELOG` entry and its own issue, so the
  per-defect record survives the fold and `git log` still shows four authored commits.
  What this entry ratifies is the *bundle* and its version.
- **What is in the bundle:**
  1. `governance/saga.schema.json` — `artifact_id` pattern `^[A-Z]+-[0-9]{2}$` →
     `^[A-Z]+-[0-9]{2,}$`. A **correction**: `LAYER_REGISTRY.yaml`
     `id_patterns.document` and `ID_NAMING_STANDARDS.md` §"Format" already allow
     three-plus digits, so the schema rejected registry-valid IDs such as `BRD-100`.
     The description now names all three surfaces as the lockstep set.
  2. `governance/TAG_SYNTAX.md` — **defines `@chg: CHG-NN`**. This is the one
     *additive normative* change, and it is why the bundle is MINOR rather than PATCH:
     the CHG auditor's check **C1** made the tag a P1 requirement while the tag was
     defined in no spec surface — a requirement with no definition. It is documented
     as a **provenance back-reference, not a trace tag**: CHG is a governance overlay,
     not one of the eight registry layers, and appears in no layer's `required_tags`
     or `can_reference`.
  3. `AI_ASSISTANT_RULES.md` — generation-order `from` clauses corrected to match the
     registry's `required_tags` and the necessary-upstream doctrine (ADR from EARS+BDD;
     SPEC from EARS+BDD+ADR; TDD from EARS+BDD+ADR+SPEC; IPLAN from SPEC+TDD). The old
     clauses contradicted the same document's own doctrine.
  4. `playbooks/02_PRD/{auditor,chaos_engineer}.md` — the auditor's C3 mandatory-section
     list realigned to `PRD-TEMPLATE.yaml` (the template declares no NFR section, so the
     check demanded sections the template does not define).
- **Consequences:** platforms re-pin to `0.41.0`; the vendored plugin bundle is
  regenerated by `tools/sync-plugin-framework.sh`. **Propagation order is load-bearing**
  — `framework/VERSION` → `scripts/sync-version-refs.sh` → `tools/sync-plugin-framework.sh`;
  reversing it lands drifted bundled playbooks and a red bundle guard.
- **Precedent set — narrower than it first read, because the premise was cost rather
  than impossibility.** A fold is *permitted* when every folded item is independently
  correct, independently revertible, ready at the same moment, and would otherwise
  each pay a full spec-release fanout. It is not *required*, and it is not a general
  licence to batch: nothing in GATE-SPEC forces one version, so "the gate made me do
  it" is not available as a justification. The per-issue record still lives in the
  issue and its own `CHANGELOG` entry — the GD entry ratifies only the version. When
  in doubt, ship separately and pay the rebase; the cost argument is weakest exactly
  when the items are not ready together.

---

## GD-10 — A backlog file is a capture queue, not a publication channel: Tier-2 gaps that meet the bar also get a tracker issue

- **Status:** Accepted — 2026-07-26 (ratified on merge; a `framework/**` normative
  change — human sign-off per GATE-SPEC. This GD-10 entry + the `VERSION`/`CHANGELOG`
  bump + both `FRAMEWORK_SPEC_VERSION` pins + green conformance are the change record,
  per the GD-05..GD-09 precedent — no separate CHG artifact). SemVer **minor**
  (additive: a second Tier-2 surface with an explicit bar; the existing queue and its
  lifecycle are unchanged), change-level **C2**.
- **Context:** Principle 9 defined **one** capture surface for the framework's own
  gaps — the Tier-2 backlog file — and no rule that ever opened a tracker issue for
  them. Issues were mandated only for defects owned by *another* repo, so by
  construction that rule never fired for a framework-owned gap. The result was
  measurable rather than theoretical: a ~1,376-line backlog holding ~40 entries
  against a single open issue, on a tracker already provisioned with eleven issue
  templates and a complete area-label taxonomy that nothing ever routed anything to.
  The failure mode is the same one the cross-repo rule was written to fix — *"those
  files are read by sessions entering this repo, never by the people or agents who
  own the fix, so the defect stays latent"* — and it applies unchanged to consumers
  of the framework, who cannot see the backlog file at all.
- **Decision:** Tier 2 has **two surfaces with distinct roles**, not one.
  1. **The backlog file stays the triage queue**, unchanged: every gap gets an entry,
     appended inline as discovered, and the entry IS the capture moment. Its
     triage → promote-to-plan → ship → Closed-with-merge-SHA lifecycle is untouched.
  2. **An issue is opened for an entry that meets ANY of three tests** — actionable
     by someone other than its finder; reproducible at `file:line` with a concrete fix
     shape; or user-visible / blocking a consumer. Purely local, speculative, or
     already-planned entries stay queue-only. The bar exists because the tracker must
     not become a second copy of the backlog — replacing one surface with the other
     would trade a latency problem for a duplication problem.
  3. **The issue carries evidence, not a symptom** — reproduction at `file:line` plus
     the command that exercised it, blast radius (checked, not assumed), why it was
     hard to diagnose where the symptom misnames the cause, a concrete suggested fix,
     and what is **NOT** broken where that was verified. The last two are what make an
     issue actionable by a non-finder, which is the entire reason to open one.
  4. **Linked both ways and closed together** on the same merge SHA; one issue per
     defect; new evidence on an existing issue goes in a **comment**, not a second
     issue. **Read the filed artifact back** — filing tools can exit 0 while
     publishing an empty body, and an empty issue discharges nothing.
- **Consequences:** Principle 9 gains the queue-vs-channel sentence and points at the
  new `FRAMEWORK_FEEDBACK_LOG.md` §"Tier 2 → the tracker" for the bar. Tier 1 is
  untouched: a consumer project's own log still surfaces upstream by PR, issue, or
  direct addition, at its own cadence. The rule is deliberately written against "the
  framework's tracker" rather than a named host, so a consumer running the framework
  on any tracker can satisfy it. No lint rule or conformance check enforces this —
  it is a governance obligation on the maintainer, like the rest of Principle 9.

---

## GD-09 — The element-ID hash algorithm has exactly one source; a layer cross-references it and never re-specifies it

- **Status:** Accepted — 2026-07-26 (ratified on merge; a `framework/**` normative
  change — human sign-off per GATE-SPEC. This GD-09 entry + the `VERSION`/`CHANGELOG`
  bump + both `FRAMEWORK_SPEC_VERSION` pins + green conformance are the change record,
  per the GD-05/GD-06/GD-07/GD-08 precedent — no separate CHG artifact). SemVer
  **minor** (additive: TDD gains an element-ID contract and four `id_standard` keys a
  platform may read; no existing behavior changes), change-level **C2**.
- **Context:** D-0062 (PROVISIONAL-IDS-002 Phase 1, spec `0.35.0`) made a six-step
  normalization transform normative for element-ID hash inputs and named
  `ID_NAMING_STANDARDS.md` its single source. Within the spec that change reached
  exactly **one** surface, `01_BRD/BRD-TEMPLATE.yaml`. Four layer templates (PRD,
  EARS, BDD, ADR) and three layer READMEs (BRD, PRD, EARS) went on publishing the
  *pre*-normalization input `"{doc_id}:{section_id}:{title}:{description}"`, so a
  reader following a layer template — which is what templates are for — computed a
  different hash than `compute_element_hash()` does for the same content, for any
  title or description containing uppercase or punctuation. The one layer with a
  verifier (`rehash --check`, BRD §7) was precisely the one already corrected, so
  nothing could catch it. Separately, TDD — one of the six layers
  `ID_NAMING_STANDARDS.md` says **MUST** carry element IDs — documented neither
  format nor algorithm in its README or template, leaving the only written statement
  of its contract on a *platform* authoring surface — inverting the rule that
  `framework/` is the engine-agnostic contract and platforms consume it.
- **Decision:** Three rules, ratified together.
  1. **Single source, enforced by deletion.** A layer surface states the *shape*
     (`sha256("{doc_id}:{section_id}:{norm(title)}:{norm(description)}")[:4]`) and
     cross-references `ID_NAMING_STANDARDS.md` for the byte-exact assembly, the
     `norm()` transform, and the field-extraction boundary. It does **not** restate
     the algorithm. Re-specifying per layer is what allowed the drift; updating the
     seven stale copies would only reset the drift clock.
  2. **Every mandating layer states its contract in-layer.** TDD gains an
     `## Element IDs` README section and the four `id_standard` keys, matching its
     five siblings, including that test cases live in Section 4 (so authored IDs
     carry `04`). It also states explicitly what it does *not* define: a TDD case
     declares `name`/`spec_ref`/`target`/`test_file`/`test_function` and carries
     neither `title` nor `description`, so which field supplies each hash input is
     deferred to Phase 2+ — naming one would be a new normative contract smuggled
     into a documentation fix. PRD, EARS, BDD and ADR are in the identical position
     and are labelled the same way.
  3. **`placeholder` is deleted, not redefined.** All five templates declared
     `placeholder: "0000"` while using `.xxxx` throughout their own bodies. The key
     matched neither available meaning — the prose called it the *template*
     placeholder (contradicted in the same file), and the documented
     *produced-document* provisional form is the section ordinal `0001`, not `0000`.
     `0000` appears nowhere in `framework/governance/`, and no code reads
     `id_standard.placeholder`. `ID_NAMING_STANDARDS.md` already governs both
     notations, so the key is removed rather than given a referent it never had.
- **Consequences:** `tests/conformance/test_element_id_layer_contract.py` locks all
  three rules over `framework/layers/**` — no raw input string, the four keys plus a
  cross-reference on each of the six mandating templates, an `## Element IDs` section
  on each of the six READMEs, and no re-introduced `placeholder`. Its scope is the
  spec only — platform authoring surfaces that also state a hash input are out of
  scope here and must add their own lock. SPEC (06) and IPLAN (08) remain
  the two documented exemptions and are deliberately excluded from the hardcoded
  layer list.

---

## GD-08 — The `seed/` tier is frozen historical input; every seed claim gets a total disposition (absorbed / rejected / deferred) recorded in the BRD

- **Status:** Accepted — 2026-07-24 (ratified on merge; a `framework/**` normative
  change — human sign-off per GATE-SPEC. This GD-08 entry + the `VERSION`/`CHANGELOG`
  bump + both `FRAMEWORK_SPEC_VERSION` pins + green conformance are the change record,
  per the GD-05/GD-06/GD-07 precedent — no separate CHG artifact). SemVer **minor**
  (additive: a new `_required: false` carrier + two additive lint rules; no existing
  behavior changes), change-level **C2**.
- **Context:** The spec named the `seed/` input tier three times, all descriptively
  (`README.md` inputs row; `docs/AIDOC.md` tier diagram + tier table), but defined no
  contract over it. `layers/01_BRD/README.md` — the doc governing the layer the seed
  feeds — never mentioned it, and BRD carries `required_tags: []`
  (`registry/LAYER_REGISTRY.yaml`), so the layer had no declared upstream of any kind.
  Two failure modes followed: seed content that never reaches the chain is invisible,
  and the cheapest way to "resolve" an audit finding is to edit the seed until the gap
  disappears — destroying the record of what was asked for.
- **Decision:** Ratify `SEED_CONTRACT.md`'s three rules as conformance requirements:
  (1) **frozen input** — once a cycle's first BRD is authored, seed files are not
  edited to resolve findings; new human input arrives through the gated `chg/` tier;
  (2) **total disposition** — every seed claim has exactly one disposition in the BRD
  set (`absorbed` names ≥1 BRD element ID; `rejected` gives a rationale; `deferred`
  gives a rationale + target cycle); (3) **BRD is the absorption point** — a claim
  first appearing at PRD or later with no BRD row is a gap. The disposition ledger is
  carried in a new BRD `seed_disposition:` section shipped **`_required: false`**, so
  the contract is normative for new BRDs (via business-analyst lens C8) while the lint
  stays silent on BRDs authored before it. Making the section *required* is a separate,
  breaking change, deliberately deferred.
- **Enforcement split (stated so the gate is not read as stronger than it is):**
  `SEED01` (deterministic lint) checks that every ledger row is well-formed and each
  `absorbed` row's target element resolves; it **cannot** know whether the ledger
  missed a claim the seed prose makes — completeness is a reading judgement owned by
  the BRD auditor lens (check C8).
- **Consequences:** new `SEED_CONTRACT.md`, a `governance/README.md` index row,
  and the `test_governance.py` `EXPECTED_FILES` registration; `SEED01` in the
  reference linter plus its `LINT_RULES.md` row; the BRD `seed_disposition:` §16
  carrier, the BRD-MVP skeleton row, and the `01_BRD/README.md` "Seed input"
  section; playbook checks C8 (business_analyst and auditor). Additive
  throughout: SemVer **minor**, change-level **C2**.
- **Security (GATE-SPEC-W003).** Parts A and C inject agent-facing authoring
  guidance (playbook C8 checks, BRD/TDD template `_guidance`). `SECURITY_REVIEW.md`
  checklist assessment: the added text only instructs an agent to author a
  disposition ledger and to pair scenarios to test cases — it grants no
  capability/tool/permission, introduces no secret-bearing surface (T-secrets),
  and adds no active content or external fetch (T-active-content). Injection risk
  (T2) is unchanged: the guidance is static spec prose, not consumed input.
  Trivially safe — the GD-05 precedent for advisory-W003 agent-instruction text.
- **Authority:** `SEED_CONTRACT.md`; `layers/01_BRD/BRD-TEMPLATE.yaml`
  (`seed_disposition:`); `LINT_RULES.md` (`SEED01`); `playbooks/01_BRD/{business_analyst,auditor}.md`;
  `SECURITY_REVIEW.md` (W003); `chg/gates/GATE-SPEC_FRAMEWORK.md`.

---

## GD-07 — The reference lint honors the `active_layers` adaptation cascade; implementing an already-specified enforcement rule is a framework MINOR under GATE-SPEC

- **Status:** Accepted — 2026-07-10 (founder-ratified governance decision A over B;
  a `framework/`-versioned change — human sign-off per GATE-SPEC. This GD-07 entry +
  the `VERSION`/`CHANGELOG` bump + both `FRAMEWORK_SPEC_VERSION` pins + green
  conformance are the change record, per the GD-05/GD-06 precedent — no separate CHG
  artifact). SemVer **minor** (`0.36.2 → 0.37.0`; new *enforced* behavior),
  change-level **C2**.
- **Context:** The `active_layers` knob (`ADAPTATION_SURFACE.yaml`) lets a project
  disable a skippable layer (BDD/ADR), and the `cascade_rule` already *specifies*
  that traceability/audit consumers must then stop demanding that layer's upstream
  tag downstream. But the reference linter `tools/sdd_doc_lint` was profile-blind —
  it never read `.aidoc/profile.yaml`, so a project legitimately skipping BDD still
  got TAG01 "requires upstream tag `@bdd:`" failures on ADR/SPEC/TDD
  (ACTIVE-LAYERS-CASCADE-001, the framework-tier remainder of the adaptation-surface
  enforcement work tracked in the platform backlog as H-16).
  A governance fork arose: the change edits `tools/` (outside `framework/`), so does
  implementing an *unchanged* rule warrant a framework-VERSION bump + GATE-SPEC, or is
  it tooling-only? `ADAPTATION.md` §6 ties a bump specifically to *changing the
  surface* (adding/renaming/removing a knob, or changing the mandatory/skippable
  split) — which this does NOT do — so §6 alone did not settle it.
- **Decision (A — bump + GATE-SPEC):** treat it as a framework MINOR under GATE-SPEC.
  **Rationale:** a new *enforced* conformance behavior shipped under a *fixed*
  framework version is a silent behavior change for consumers pinned to that version;
  a version signal + a GATE-SPEC audit record is the conservative, auditable choice —
  even though only `tools/` + the vendored copies change and no `framework/` spec text
  moves. This does not amend §6 (no surface change occurred); it establishes that
  **first-time enforcement of an existing normative rule in the reference tooling is a
  versioned framework change**, distinct from a pure bug-fix in the tooling.
- **Implementation:** the cascade is TAG01-only (the sole demand site;
  `can_reference` is unused, COV02/TRACE-RES-001/REFGRAN01 are no-ops/defensive on the
  disabled path). The lint reads `active_layers` via `.aidoc/profile.yaml`
  auto-discovery (+ `--active-layers` override), computes the disabled skippable set,
  and lints against an *effective* registry view (a copy with disabled tags removed —
  the module registry is never mutated). Re-vendored byte-identically to both
  platforms. Plan + review: `plans/ACTIVE-LAYERS-CASCADE-001-PLAN.md`.

---

## GD-06 — Engine-agnosticism boundary: the spec neutralizes generic platform vocabulary but sanctions a small set of load-bearing engine bindings as documented exceptions

- **Status:** Accepted — 2026-07-09 (ratified on merge; a `framework/**` normative
  change — human sign-off per GATE-SPEC. This GD-06 entry + the `VERSION`/`CHANGELOG`
  bump + both `FRAMEWORK_SPEC_VERSION` pins + green conformance are the change record,
  per the GD-01/GD-05 precedent — no separate CHG artifact). SemVer **patch**
  (`0.36.0 → 0.36.1`; documentation clarification, no behavior change),
  change-level **C1**.
- **Context:** The engine-agnostic spec (durable convention: "carries no platform
  names or runtime code") had leaked engine-specific tokens found in the
  FRWK-REVIEW-002 review: (a) `doc-*`/"SKILL" plugin vocabulary in governance/layer
  docs; (b) a direct Claude Code CLI reference (`claude -p`) and a plugin-skill table
  in `docs/AIDOC.md`; (c) the playbook `agent:` frontmatter field, which names the
  executor and pointed into `platforms/claude-code-plugin/`; (d) a workspace-CI
  section in `REVIEW_REMEDIATION_FLOW.md` pinning `aidoc-flow-ci@ci/vX`; (e)
  repo-root tool paths (`tools/trace_walk.py`, `tools/sdd_coverage.py`) referenced
  normatively though the spec neither contains nor vendors them. A pure "remove
  everything" sweep is one option; but some of these are **load-bearing** — an
  engine-agnostic spec still needs *some* way to name the executor a lens maps to,
  and workspace process legitimately rides alongside the vendored spec. D-0022 set
  the precedent that a load-bearing platform coupling can be an **explicitly
  documented exception** rather than a defect.
- **Decision (hybrid):**
  1. **Neutralize (must carry no platform-specific token):** replace `doc-*`/"SKILL"
     vocabulary with engine-neutral terms ("the audit engine", "the layer-audit
     capability"); make the `claude -p` reference engine-neutral; mark the AIDOC
     plugin-skill table an explicit Platform-B *illustration*; and describe the
     repo-root tools as a **reference implementation outside the spec** (state the
     capability normatively, mark the tool path non-normative).
  2. **Sanctioned exceptions (a load-bearing binding, documented, not a defect —
     the D-0022 pattern):**
     - The playbook `agent:` frontmatter field stays: it names the engine-defined
       executor a platform maps each lens to. Its inline comment is softened from a
       hard `platforms/claude-code-plugin/...` pointer to "the engine maps lens →
       executor; see the platform's own docs" — the field is engine-defined, the
       pointer is not normative.
     - The `REVIEW_REMEDIATION_FLOW.md` "Mechanical author-side pre-push gate
       (aidoc-flow workspace layer)" section stays: it is workspace-layer process,
       already scoped by its heading; it gains a one-line note that it is a
       workspace convention, not part of the engine-agnostic contract.
- **Consequences:** the neutralization edits ship as scoped follow-up PRs citing
  this GD-06 (≤3 doc surfaces each per governance PR-discipline). The two sanctioned
  exceptions are conformance-neutral and remain in the spec with their documented
  rationale. Engine-agnosticism conformance (e.g. `test_spec_hygiene`) may later be
  extended to allow-list exactly the two sanctioned bindings; until then they are
  covered by this decision. No behavior change; SemVer **patch**, change-level **C1**.
- **Authority:** this decision; `framework/README.md` (engine-agnostic convention);
  D-0022 (the vendored-bundle exception precedent); `chg/gates/GATE-SPEC_FRAMEWORK.md`.

---

## GD-05 — The author-self-claim strip MUST is satisfied by physical removal where the engine curates the lens input, or by a disregard instruction where the lens reads the artifact directly

- **Status:** Accepted — 2026-07-04 (ratified on merge; a `framework/**` normative
  change — human sign-off per GATE-SPEC. The GD-05 entry + the `VERSION`/`CHANGELOG`
  bump + both `FRAMEWORK_SPEC_VERSION` pins + green conformance are the change record,
  per the GD-01 precedent — no separate CHG artifact). SemVer **minor** (`0.32.7 →
  0.33.0`), change-level **C2**.
- **Context:** `REVIEW_TEAM.md` §"Strip author self-claim" requires engines to keep
  author self-assessment fields (`*_ready_score`/`*_score`/`readiness_score`/
  `audit_score`) out of a lens's view so the lens's `lens_score` is not anchored to the
  author's claim. Its mechanism clause said "the brief that goes to the lens has the
  stripped body" — which presumes the engine **controls the lens input**. That holds for
  an engine whose lens is fed a separately-assembled body (a curated input). It does
  **not** hold for an engine whose review lens **reads the artifact directly** (an
  agentic reviewer handed the artifact path, or a reviewer that reads the artifact into
  its own review context). Once the score is in the lens context there is no separate
  actor to remove it — so a "strip the body" instruction is inert there. Such a lens
  cannot be handed a stripped-only input (it needs filesystem access to resolve
  cross-document links), and a stripped working copy is bypassable (the lens can locate
  and read the original). The only de-anchor available to that engine class is an
  explicit instruction to disregard the fields — materially **weaker** than physical
  removal, so it must be a constrained fallback, not a general escape.
- **Decision:** The de-anchor requirement is unchanged; a **second, weaker compliance
  mechanism** is sanctioned, selected by a **structural fact about the engine**, not the
  review mode and not a self-declaration:
  1. **Primary (physical removal):** an engine that **curates the lens input** (a
     separate actor assembles the body the lens receives, so the lens context never held
     the score) MUST strip the fields.
  2. **Constrained fallback (disregard instruction):** where **the lens reads the
     artifact directly** (handed a path, or sharing the reading context — so the engine
     cannot keep the score out of the lens context), the engine MUST instead include, in
     the lens brief, an **explicit, strong instruction**: the lens MUST NOT read, cite,
     or weight the author self-assessment fields when forming its `lens_score`. Permitted
     **only** under the reads-directly condition. The canonical field list is unchanged.
- **Consequences:** `REVIEW_TEAM.md` gains the two-mechanism clause. A curated-input
  engine stays conformant unchanged (primary/physical). A direct-read engine becomes
  conformant by issuing the disregard instruction in every lens brief. The change
  injects agent-facing instruction text (advisory **GATE-SPEC-W003**) that is trivially
  safe — it only tells a lens to ignore a numeric self-claim; no capability/tool/
  permission change. Additive standard clarification: SemVer **minor**, change-level
  **C2**. (Per-platform implementation is tracked in the project decision log.)
- **Authority:** `REVIEW_TEAM.md` §"Strip author self-claim"; `chg/gates/
  GATE-SPEC_FRAMEWORK.md`.

---

## GD-04 — IPLAN-ASSURANCE L1 is ratified as an aidoc-flow conformance requirement

- **Status:** Accepted — 2026-06-28 (ratified on merge; a validator never grants
  approval, only a human signs). Pins `iplan/v0.4.0`. **Merge precondition:** the
  founder tags `iplan/v0.4.0` on `aidoc-flow-iplan-standard` first (PRs #4 §9, #5
  envelope+vectors, #6 R3-amend are all merged to that repo's main).
- **Context:** The IPLAN-ASSURANCE standard (verifiable provenance + transparency;
  L0/L1/L2 — not a blockchain) lives in the neutral `aidoc-flow-iplan-standard`
  repo. Its **L1** tier (signed-initiator provenance) is design-complete: §9
  resolved (R1 inline-allowlist baseline / IdP-ready; R2 witness OPTIONAL /
  REQUIRED-ready; R3 IPLAN-native in-toto predicate), the additive
  `intake_control.provenance` envelope landed on `iplan-document` (no
  `schema_version` bump, per the `dispatch_token_id` precedent), and L1 golden
  vectors (`accept_ed25519` / `accept_hmac` / `reject_tampered`) pin schema-validity
  + signature verification. Until ratified here, nothing in the standard is a
  conformance requirement (the standard's own §0 gate clause). This is the GATE-SPEC
  ratification the standard's `GOVERNANCE.md` points to.
- **Decision:** Ratify **IPLAN-ASSURANCE L1 at `iplan/v0.4.0`** as a conformance
  requirement for aidoc-flow consumers. A consumer that declares `assurance ≥ L1`
  MUST verify the initiator signature over the canonical IPLAN (with
  `intake_control` excluded) against an authorized-initiator keyring **before
  approval/execution**, per §2 + the §9 resolutions. **L0** (byte integrity) stays
  the default; **L1** is opt-in via the consumer's declared minimum-accept. The §3
  evidence-attestation predicate is **IPLAN-native** (R3, amended) — not
  `slsa.dev/provenance/v1` (SLSA provenance subject-inverts: its `subject` is the
  build output, but §3's subject is the IPLAN input); the first conformant producer
  is iplanic A4 / D-0109.
- **Consequences:** Consumers (iplanic, iplan-runner) may pin `iplan/v0.4.0` and
  build L1 (iplanic A1–A3: re-pin schema → initiator keyring → import verify;
  iplan-runner intake gate). Recording this decision is itself a framework-spec
  change and passes **GATE-SPEC** (its `VERSION`/`CHANGELOG` bump + both platforms'
  `FRAMEWORK_SPEC_VERSION` + green conformance are the evidence). **L2** (transparency
  log) and **REQUIRED** witness cosigning (R2) remain future higher-tier work, not
  ratified here.
- **Authority:** `aidoc-flow-iplan-standard` `docs/standards/IPLAN-ASSURANCE.md`
  (§2 L1, §9 R1–R3), `schemas/iplan-document.schema.json`
  (`intake_control.provenance`), `tests/contract/provenance/` (golden vectors);
  `chg/gates/GATE-SPEC_FRAMEWORK.md`. Tracking: `aidoc-flow-operations`
  `ops/iplans/IPLAN-0028`.

---

## GD-03 — Trace citations to element-declaring layers are element-level (ref-granularity)

- **Status:** Accepted — 2026-06-27 (per CFB-PR-3 / `BL-REF-GRANULARITY`;
  ratified on merge — a spec change, GATE-SPEC human sign-off).
- **Context:** Functionality is specified in **elements** (each FR / EARS
  statement / BDD scenario / ADR decision / TDD case has its own id); the
  document is a container. The `ID_NAMING_STANDARDS.md` Tag-Format table already
  shows element-level forms for the element-declaring layers, but it did NOT
  state explicitly whether a layer's **necessary-upstream / feature-level** tag
  (vs. an inline body citation) must also be element-level. That gap let an
  instance author a **coarse document-level** feature tag (the url-shortener
  BDD-01 Feature carries `@ears: EARS-01`) while its scenarios carry precise
  element-level tags — which keeps the coverage engine (`COV01`/`COV02`)
  document-level, because a doc-level edge makes the *whole* upstream document
  look realized. Element-precise coverage is the goal of CFB-PR-2; it is only
  computable once trace data is element-precise.
- **Decision:** Every `@<layer>:` **trace citation** to an **element-declaring**
  layer (`@brd @prd @ears @bdd @adr @tdd`) MUST be **element-level**
  (`TYPE.NN.SS.xxxx`) — in **all** contexts, including the necessary-upstream /
  feature-level tag, not only inline body citations. A unit realizing multiple
  upstream elements **pipe-delimits** them (the union of its sub-units' element
  citations); a true whole-document dependency is stated in **prose**, never as a
  document-level trace tag. `@spec:`/`@iplan:` citations remain **document-level**
  (those layers are element-ID-exempt). **Self-tags** and **downstream
  forward-pointers** are document-level and exempt (not trace citations).
- **Consequences:** `ID_NAMING_STANDARDS.md` gains the normative "Reference
  granularity" clause; `sdd_doc_lint` gains the deterministic enforcement
  `REFGRAN01` (CFB-PR-3); the doc-form necessary-upstream/feature examples in the
  layer templates + the url-shortener corpus are reconciled to element-level
  (fan-out) in CFB-PR-3. This unblocks the element-level `COV01`/`COV02` upgrade.
  Additive standard clarification: SemVer **minor**, change-level **C2**.
- **Authority:** `ID_NAMING_STANDARDS.md` §"Reference granularity";
  `chg/gates/GATE-SPEC_FRAMEWORK.md`.

---

## GD-02 — Independent automated review at `pre_merge`, with a tiered human-in-loop

- **Status:** Accepted — 2026-06-15 (per `aidoc-flow-operations` IPLAN-0011;
  ratified on merge — a validator never grants approval, only a human signs).
- **Context:** The spec already names `pre_merge` as an automatable review
  trigger (`REVIEW_REMEDIATION_FLOW.md`) and treats self-approval as failure code
  **C1** across the CHG gates, but it did not define *how strong* an automated
  `pre_merge` review must be, nor when it suffices vs. when a human must still
  sign. As AI agents both generate and could review changes, an independent
  (judge ≠ generator) gate is needed so routine changes move without a human
  bottleneck while spec-shaping changes keep explicit human approval (GD-01 /
  GATE-SPEC).
- **Decision:** An automated `pre_merge` review gate, when used, MUST be
  **independent of the generator** (reviewer ≠ author; different model/vendor
  where available), **review-only** (remediation is a separate step), classify
  findings by severity (`critical`/`medium` block; `low`/`acknowledged`
  advisory), and run the **iteration-capped** remediation loop, **escalating to a
  human at the cap**. Human sign-off is **tiered by risk**: routine changes are
  cleared by the gate + escalation; **changes to the spec (`framework/**`) or any
  governance standard always also require human approval** (GATE-SPEC / GD-01).
  Pre-cutover, the automated gate + escalation is the operative enforcement for
  routine work; the GATE-SPEC human-approval requirement for spec changes remains
  in force and the heavier CHG ceremony returns post-cutover.
- **Consequences:** The `pre_merge` trigger gains an engine-agnostic *strength*
  contract (`REVIEW_REMEDIATION_FLOW.md` §"Independent review at `pre_merge`") and
  a *completion* contract (`DEFINITION_OF_DONE.md`). Self-approval (C1) is
  enforced at merge, not only at the CHG gates. Each platform binds the gate to
  its own runtime (runner, model, protected-branch rules) — those bindings are
  not part of this spec. The change is **additive**: SemVer **minor**,
  change-level **C2**.
- **Authority:** `REVIEW_REMEDIATION_FLOW.md`, `DEFINITION_OF_DONE.md`,
  `chg/gates/GATE-SPEC_FRAMEWORK.md`, GD-01.

---

## GD-01 — Change management is implemented as authoring/validation tooling + CI/CD

- **Status:** Accepted — 2026-05-23. (Originated as the project's migration
  decision D-0020; formalized here per the change-management plan, "CHG-D2".)
- **Context:** Post-cutover, the gated change-management (CHG) process governs
  changes to the `framework/` spec, because the spec has multiple downstream
  consumers and real breaking-change risk. The five original gates
  (GATE-01/03/06/08/CODE) govern a project's **artifact instances** along the
  BRD→Code chain; none governed a change to the **spec itself**. CHG must also be
  *runnable* — a monolithic, manual process would not hold.
- **Decision:** CHG is implemented as **per-platform authoring/validation tooling
  plus CI/CD**, against this one shared spec. Its spec-governance entry point is
  **GATE-SPEC**, a *meta* gate that governs changes to the spec
  (templates, governance, registry, `VERSION`) and is **orthogonal** to the
  artifact-cascade gates: it has no downstream gate successor; a passed spec
  change instead obliges **every platform** to re-declare its
  `FRAMEWORK_SPEC_VERSION` and re-pass the shared conformance suite. The gate's
  checks split three ways by enforcer:
  - **record-level** (provenance; SemVer impact with `major ⇒ C3`; never C1; C3
    approval preparation) — each platform's record validator;
  - **diff-aware + static** (`VERSION` bumped on a spec change; `CHANGELOG`
    updated; both `FRAMEWORK_SPEC_VERSION` match; the conformance suite is
    green) — continuous integration;
  - **human approval** — the platform's protected-branch review.

  Two invariants hold: a validator **never grants approval** (only a human
  signs), and **`major ⇒ C3` is one-directional** — a breaking spec change must
  be C3, but an additive (`minor`/`patch`) change may be C2, so a new optional
  capability is not forced to the heaviest gate.
- **Consequences:** Spec changes are governed uniformly and machine-checkably
  without a central runtime — the spec stays declarative; each platform supplies
  the enforcement. Promotion of a proven local adaptation *into* the spec now has
  a real gate to pass (it had none before). Recording this decision was itself a
  spec change and passed GATE-SPEC (its `VERSION`/`CHANGELOG` bump + green
  conformance are the evidence), the first exercise of the process.
- **Authority:** `chg/gates/GATE-SPEC_FRAMEWORK.md`,
  `chg/gates/GATE_ERROR_CATALOG.md` (GATE-SPEC codes), `chg/README.md`,
  `chg/CHG-TEMPLATE.yaml` (the `spec` change-source + `semver_impact` field),
  `README.md` (CHG overlay).

---

## Pending graduation

Spec-affecting decisions still recorded only in the project's migration log,
candidates to graduate into this register as it matures:

- **Templates are the single source of truth.** Platforms consume
  `framework/layers/<NN>_<X>/` and never ship their own copies (migration D-0013).
- **Project adaptation surface.** A closed, declarative knob set lets a project
  adapt the flow without forking — `ADAPTATION.md` + `ADAPTATION_SURFACE.yaml`
  (migration D-0019).
