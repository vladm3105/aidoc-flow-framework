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

## GD-04 — IPLAN-ASSURANCE L1 is ratified as an aidoc-flow conformance requirement

- **Status:** Proposed — 2026-06-28 (ratified on merge; a validator never grants
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

- **Status:** Proposed — 2026-06-27 (per CFB-PR-3 / `BL-REF-GRANULARITY`;
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

- **Status:** Proposed — 2026-06-15 (per `aidoc-flow-operations` IPLAN-0011;
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
