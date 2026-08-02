---
name: doc-adr
description: Create an Architecture Decision Record (ADR) - Layer 5 of the SDD flow, documenting one architecture decision with Context-Decision-Consequences. Use after BDD when an architectural choice needs recording. Single-document authoring primitive; for end-to-end or batch generation the autopilot (`doc-adr-autopilot`) drives this skill.
metadata:
  tags:
    - sdd-workflow
    - layer-5-artifact
  custom_fields:
    layer: 5
    artifact_type: ADR
    skill_category: core-workflow
    upstream_artifacts: [EARS, BDD]
    downstream_artifacts: [SPEC, TDD, IPLAN]
    version: "0.25.0"
    framework_spec_version: "0.40.0"
    last_updated: "2026-05-23"
    adapts: [section_toggles, glossary]
---

# doc-adr

## Purpose

Create an **Architecture Decision Record (ADR)** — Layer 5 of the SDD flow.
An ADR records **one** architecture decision using the Context-Decision-
Consequences pattern: why the decision is needed, what was chosen, the
alternatives weighed, and the consequences accepted.

**Layer**: 5 — the decision bridge between Container (PRD) and Component (SPEC);
ADR is not itself a C4 level.
**Upstream**: EARS, BDD (per the necessary-upstream contract; upstream PRD/BRD
lineage is reachable transitively via the @-tag chain).
**Downstream**: SPEC → TDD → IPLAN → Code.

Each ADR addresses **exactly one decision**. A new architectural choice gets a
new ADR (`ADR-02`, `ADR-03`, …) rather than expanding an existing one; relate
them with `@depends: ADR-NN`.

## When to Use

Use `doc-adr` when:

- An architectural topic from BRD §8 / PRD §14 needs a recorded decision.
- Choosing a technology, pattern, or integration approach with alternatives.
- Capturing rationale and consequences for a long-lived architectural choice.

For end-to-end generation from an upstream artifact or a prompt, use
`../doc-adr-autopilot/SKILL.md`. To plan the set of ADRs a project needs, see
`../adr-roadmap/SKILL.md`.

## Prerequisites

ADR is Layer 5, so verify the required upstream artifacts (EARS + BDD) exist
and read the spec before writing:

1. **Template (source of truth):** `${CLAUDE_PLUGIN_ROOT}/framework/layers/05_ADR/ADR-TEMPLATE.yaml`
2. **Layer README:** `${CLAUDE_PLUGIN_ROOT}/framework/layers/05_ADR/README.md`
3. **ID & tag standards:** `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
4. **Authoring style:** `${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md`

Confirm required upstream artifacts: `ls docs/0{3,4}_*/ 2>/dev/null` (EARS
and BDD). Reference only documents that already exist; never invent placeholders
like `ADR-XXX` or cite SPEC numbers that do not yet exist. Confirm no ID
collision: `ls docs/05_ADR/ 2>/dev/null`. Upstream PRD/BRD lineage is reachable
transitively via the EARS/BDD @-tag chain.

## Layer Guidance

### Status lifecycle (ADR is different)

ADR uses **Proposed → Accepted → Deprecated → Superseded** — not
Draft/In Review/Approved. The status tracks the SPEC-Ready score:

| Status | SPEC-Ready | Meaning |
|--------|-----------|---------|
| Proposed | 70–89% | Decision under evaluation |
| Accepted | ≥90% | Approved, ready for SPEC |
| Deprecated | — | No longer relevant (kept for history) |
| Superseded | — | Replaced by a newer ADR (link it) |

### Required structure (10 numbered sections + glossary + appendix backmatter)

`document_control` is **Section 1** (status, date, decision-makers, author,
`originating_topic` → PRD §14, `brd_reference`, SPEC-Ready score, revision
history). Then:

2. Context (problem statement, business driver, constraints, technical
context) · 3. Decision (chosen solution, key components, MVP/next-cycle scope) ·
4. Alternatives Considered (2–3 options, each with pros/cons, cost, fit;
rejected options carry a rejection reason) · 5. Consequences (positive
outcomes, trade-offs/risks with severity, cost estimate) · 6. Architecture
Flow (diagrams + integration points) · 7. Implementation Assessment (phases,
rollback, monitoring baseline) · 8. Verification (success criteria, BDD
cross-refs) · 9. Traceability · 10. Related Decisions.

Plus a **Glossary** (`glossary:` key) and **Appendix** (`appendix:` key) as
required backmatter (unnumbered). Section numbers and identifiers come from
`ADR-TEMPLATE.yaml`'s own `# Section N:` numbering — **the template is the
source of truth**.

See `ADR-TEMPLATE.yaml` for per-section content and authoring `_antipatterns`.

### Element IDs and tags

- **Element IDs (inside the ADR):** `ADR.{doc_id}.{section_id}.{hash}` (e.g.
  `ADR.01.03.e5b1`). Emit a **stable 4-hex-char identifier** per element, distinct within its section (`HASH01`); extend to 8 on collision. Do **not** compute SHA-256 in this prompt — the hash form is the canonicalization TARGET produced by a deterministic tool pass, and byte-exact field extraction is defined for BRD §7 only (Phase 2+ for ADR). Authority: `framework/governance/ID_NAMING_STANDARDS.md`.
  There are no numeric type-codes — an element's kind is given by its section.
- **ADR is a DOCUMENT-level artifact.** It is referenced in **dash form**
  `ADR-NN`, never as a dotted element ID. The self-tag is `@adr: ADR-NN`
  (e.g. `@adr: ADR-033`); cross-links use `@depends: ADR-NN` and
  `@discoverability: ADR-NN (rationale)`.
- **Required upstream tags (Layer 5):** `@ears @bdd` — both required (per the
  necessary-upstream contract), using each upstream's element-ID form
  (`@ears: EARS.01.03.5e2a`, `@bdd: BDD.01.03.8f4c`). Upstream PRD/BRD lineage
  is reachable transitively via the EARS/BDD @-tag chain — do not emit
  `@brd:`/`@prd:` on ADR elements.
- **Removed patterns** (do not use): `DEC-XXX`, `ALT-XXX`, `CON-XXX`, the legacy
  3-segment `ADR.NN.xxxx`, numeric type-code segments, and 3-digit `ADR-NNN`.

## Creation Process

1. **Confirm the topic** — one decision, traced to its PRD §14 originating
   topic and BRD §8 driver.
2. **Reserve ID** — next free `ADR-NN` (two digits, expand only as needed:
   `ADR-01`, `ADR-99`, `ADR-102`).
   *Per-layer independence (CLEANUP-PR-F item 18):* pick the next-free
   number in YOUR layer's index — the upstream's number is NOT your number
   (doc numbers are per-layer sequential and independent; see
   `framework/governance/ID_NAMING_STANDARDS.md` §Cross-layer cardinality).
3. **Create the nested folder** — every ADR lives in
   `docs/05_ADR/ADR-NN_{slug}/`. Monolithic: `ADR-NN_{slug}.md` inside it;
   section-based (>25 KB): `ADR-NN.S_{section}.md` + index from
   `${CLAUDE_PLUGIN_ROOT}/framework/layers/05_ADR/ADR-00_index.TEMPLATE.md`.
4. **Document Control (Section 1) first**, then complete §2–§10 plus the
   glossary and appendix backmatter from the template.
5. **Evaluate 2–3 alternatives** with cost and fit; give every rejected option
   a rejection reason. State the decision decisively with rationale.
6. **Add the required upstream tags** `@ears @bdd`; add the `@adr: ADR-NN`
   self-tag and any `@depends:` cross-links.
7. **Update the ADR index** `docs/05_ADR/ADR-00_index.md` in the same change.
8. **Validate** (below) and commit the ADR and index together.

## Validation

**This skill is the validator** (no runtime code). Apply against `${CLAUDE_PLUGIN_ROOT}/framework/layers/05_ADR/README.md` and `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`.

- [ ] Document Control is the first section; status is one of
      Proposed/Accepted/Deprecated/Superseded.
- [ ] All 10 sections present and non-empty; exactly one decision.
- [ ] 2–3 alternatives, each with pros/cons + cost; rejected ones have a reason.
- [ ] Consequences cover positive outcomes, trade-offs (with severity), cost.
- [ ] Element IDs match `ADR.NN.SS.xxxx`; document refs use dash `ADR-NN`; no
      removed patterns.
- [ ] Required upstream tags `@ears @bdd` present (per necessary-upstream
      contract); `@adr: ADR-NN` self-tag.
- [ ] SPEC-Ready score ≥ 90 if status is Accepted.
- [ ] Diagram contract: the Architecture-Flow section carries the decision /
      interaction **sequence** diagram (`@diagram: sequence-*`) per
      `${CLAUDE_PLUGIN_ROOT}/framework/governance/DIAGRAM_STANDARDS.md` — ADR is the decision bridge, so
      no C4 level (use `../charts-flow/SKILL.md`); index updated; no broken links.

| Code | Meaning | Severity |
|------|---------|----------|
| XDOC-002 | Missing required upstream tag | error |
| XDOC-006 | Tag format invalid | error |
| XDOC-008 | Broken internal link | error |
| XDOC-009 | Missing traceability section | error |

**Quality gate (blocking):** SPEC-Ready score ≥ 90/100 before moving on. If
issues are found, fix and re-check; if unfixable, log for manual review.

> **ADR-REF documents** (`ADR-REF-NN_{slug}.md`, via `../doc-ref/SKILL.md`) are
> free-format reference targets — exempt from ready-scores, required upstream
> tags, and quality gates.

## Next Skill

`../doc-spec/SKILL.md` — the SPEC references this ADR (`@adr: ADR-NN`) along
with its own required `@ears @bdd` upstream tags, turning the decision into
component interfaces, data models, and behavior contracts.

## Adaptation

Read `.aidoc/profile.yaml`; honor only this skill's knobs
(`section_toggles`, `glossary`). Ignore unknown keys; absent a profile, use
framework defaults. Authority:
`${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Template / authoring rules: `${CLAUDE_PLUGIN_ROOT}/framework/layers/05_ADR/ADR-TEMPLATE.yaml`
- Layer README: `${CLAUDE_PLUGIN_ROOT}/framework/layers/05_ADR/README.md`
- Index template: `${CLAUDE_PLUGIN_ROOT}/framework/layers/05_ADR/ADR-00_index.TEMPLATE.md`
- ID & tag standards: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
- Quality gate: `../doc-adr-audit/SKILL.md` · Fixes: `../doc-adr-fixer/SKILL.md`
- Generation pipeline: `../doc-adr-autopilot/SKILL.md`
- Decision planning: `../adr-roadmap/SKILL.md`

## Quick Reference

| | |
|---|---|
| **Purpose** | Record one architecture decision (Context-Decision-Consequences) |
| **Layer** | 5 (decision bridge: PRD → SPEC) |
| **Upstream tags** | `@ears @bdd` (per necessary-upstream contract) |
| **Self-reference** | dash form `@adr: ADR-NN` (document-level) |
| **Element IDs** | `ADR.NN.SS.xxxx` (internal elements only) |
| **Status** | Proposed → Accepted → Deprecated → Superseded |
| **Must include** | Document Control (first), 10 sections, 2–3 alternatives |
| **Next** | `doc-spec` |
