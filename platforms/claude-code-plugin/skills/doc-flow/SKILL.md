---
name: doc-flow
description: Orchestrate the 8-layer SDD workflow - guide skill selection, explain the BRD→…→Code flow, and enforce the upstream-artifact policy. Use when unsure which skill to run next.
metadata:
  tags:
    - sdd-workflow
    - utility
  custom_fields:
    skill_category: core-workflow
    upstream_artifacts: []
    downstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN]
    version: "0.2.0"
    framework_spec_version: "0.4.0"
    last_updated: "2026-05-23"
---

# doc-flow

## Purpose

Orchestrate the **Specification-Driven Development (SDD) workflow**. `doc-flow`
does not create artifacts itself; it points you at the right skill, explains
how the layers connect, and enforces the rules that keep the chain coherent.

**Layer**: cross-cutting (no upstream; routes into all 8 layers).
**Use the artifact skills for creation** — `doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}`,
plus `../doc-ref/SKILL.md` for supplementary docs.

Authoritative spec: `framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` and
`framework/registry/LAYER_REGISTRY.yaml`.

## When to Use

- You are unsure which skill applies to the task at hand.
- You need an overview of the 8-layer flow or where you are in it.
- You are starting a brand-new project — run `../project-init/SKILL.md` **first**
  to scaffold folders, then return here.
- You are adopting SDD into an **existing** codebase — run
  `../project-adopt/SKILL.md` to reverse-engineer baseline artifacts first.
- You are changing an already-published artifact — use the CHG overlay
  (`../doc-chg/SKILL.md`), not the linear flow (see *Change management* below).

For end-to-end generation of a single layer, use that layer's `-autopilot`
skill. For intent-based suggestions, use `../skill-recommender/SKILL.md`.

## Behavior

### The 8-layer flow

```
BRD (1) → PRD (2) → EARS (3) → BDD (4) → ADR (5) → SPEC (6) → TDD (7) → IPLAN (8) → Code
```

| Layer | Artifact | Purpose | Base skill |
|-------|----------|---------|-----------|
| 1 | BRD | Business requirements | `doc-brd` |
| 2 | PRD | Product requirements & KPIs | `doc-prd` |
| 3 | EARS | Formal WHEN-THE-SHALL requirements | `doc-ears` |
| 4 | BDD | Gherkin test scenarios | `doc-bdd` |
| 5 | ADR | Architecture decisions | `doc-adr` |
| 6 | SPEC | Technical specifications | `doc-spec` |
| 7 | TDD | Test-case definitions & thresholds | `doc-tdd` |
| 8 | IPLAN | Executable implementation plan | `doc-iplan` |
| — | Code | Implementation output | — |

Each layer family ships four skills: the **base** (create), `-autopilot`
(generate end-to-end), `-audit` (quality gate → report), and `-fixer`
(apply audit fixes).

### Skill selection

| You have | You need | Use |
|----------|----------|-----|
| Nothing | Business requirements | `doc-brd` |
| BRD | Product requirements | `doc-prd` |
| PRD | Formal requirements | `doc-ears` |
| EARS | Test scenarios | `doc-bdd` |
| BDD | Architecture decisions | `doc-adr` |
| ADR | Technical specifications | `doc-spec` |
| SPEC | Test-case definitions | `doc-tdd` |
| TDD | Implementation plan | `doc-iplan` |
| IPLAN | Code | Implement |
| Any stage | Supplementary docs (overview, glossary) | `doc-ref` |
| General guidance | Routing | stay on `doc-flow` |

### Utility skills

- **`../project-init/SKILL.md`** — scaffold a new project (run before any layer).
- **`../project-adopt/SKILL.md`** — adopt SDD into an existing codebase (brownfield).
- **`../project-profile/SKILL.md`** — tailor the flow to this project (optional; sets `.aidoc/profile.yaml`).
- **`../doc-naming/SKILL.md`** — ID / naming authority (`TYPE-NN`, `TYPE.NN.SS.xxxx`).
- **`../doc-ref/SKILL.md`** — free-format reference documents (BRD-REF / ADR-REF).
- **`../doc-review/SKILL.md`** — cross-cutting quality review (typos, links, terms).
- **`../doc-validator/SKILL.md`** — cross-document validation & traceability gaps.
- **`../trace-check/SKILL.md`** — bidirectional traceability validation.
- **`../charts-flow/SKILL.md`** — Mermaid diagrams and file management.
- **`../adr-roadmap/SKILL.md`** — implementation roadmaps from ADRs.
- **`../context-analyzer/SKILL.md`** · **`../quality-advisor/SKILL.md`** ·
  **`../skill-recommender/SKILL.md`** · **`../workflow-optimizer/SKILL.md`** ·
  **`../security-audit/SKILL.md`** — analysis and advisory helpers.

### Change management (editing existing artifacts)

Changes to already-published artifacts use the **CHG overlay**, not the linear
flow:

- **`../doc-chg/SKILL.md`** (+ `-autopilot` / `-audit` / `-fixer`) — author and
  validate a change record; classifies the change level (C1–C3 / Emergency) and
  routes it to the right approval gate.
- **`../gate-check/SKILL.md`** — run the approval gate (GATE-01/03/06/08/CODE,
  or **GATE-SPEC** for a change to the `framework/` spec itself) for the change's
  affected layers and prepare the sign-off form (a human approves — the skill
  never does).

### Upstream-artifact policy (mandatory)

Do **NOT** invent missing upstream artifacts. If a required upstream is absent,
**skip** the downstream functionality and report it — every artifact must trace
to a real business/product justification.

| Situation | Action |
|-----------|--------|
| Upstream exists | Reference with its exact ID |
| Required upstream missing | Skip; report; advise creating it first |
| Optional upstream missing | Use `null` in the tag |
| Not applicable | Omit the tag |

### Validation model

The framework is spec-only — it ships no runtime scripts. Each skill **is** the
validator: it applies a declarative checklist against the layer `README.md` and
`framework/governance/`. After each artifact, run that layer's `-audit`; before
moving on, confirm the cumulative upstream tags are present (PRD→1 … IPLAN→7).

## Related Resources

- Spec guide: `framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`
- Layer registry: `framework/registry/LAYER_REGISTRY.yaml`
- ID standards: `framework/governance/ID_NAMING_STANDARDS.md`
- Traceability: `framework/governance/TRACEABILITY.md`
- Governance core: `framework/governance/DOC_GOVERNANCE_CORE.md`
- Per-layer guidance: `framework/layers/NN_<X>/README.md`
