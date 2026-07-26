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
