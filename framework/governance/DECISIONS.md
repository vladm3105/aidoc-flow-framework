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
