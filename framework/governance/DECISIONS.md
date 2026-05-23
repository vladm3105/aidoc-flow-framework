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
