---
name: project-adopt
description: Adopt the SDD flow into an existing (brownfield) codebase - detect code and docs, infer the domain, scaffold the 8-layer structure, and reverse-engineer draft baseline artifacts. Use once on an existing project; then hand off to doc-flow and the per-layer audits.
metadata:
  tags:
    - sdd-workflow
    - utility
  custom_fields:
    skill_category: utility
    upstream_artifacts: []
    downstream_artifacts: [BRD]
    version: "0.20.1"
    framework_spec_version: "0.22.0"
    last_updated: "2026-05-23"
    adapts: [active_layers]
---

# project-adopt

## Purpose

Onboard an **existing codebase** (brownfield) into the SDD flow: detect the
current code and any docs, infer the domain, scaffold the 8-layer `docs/`
structure, and **reverse-engineer baseline artifacts** from the code at
`draft` status — the one-time setup that gives a running system its SDD
backbone. It is the brownfield counterpart to `../project-init/SKILL.md`.

**Layer**: cross-cutting utility (precedes BRD).

## When to Use

The greenfield/brownfield boundary is the deciding factor:

**Use `project-adopt` when** (brownfield):

- Source code already exists, but there is no `docs/` SDD structure.
- You need baseline SDD artifacts derived from the running system.

**Use `../project-init/SKILL.md` instead when** (greenfield):

- No code and no docs yet — a brand-new project to be built SDD-first.

**Do NOT use** when `docs/01_BRD/` etc. already exist — go straight to
`../doc-flow/SKILL.md`.

## Behavior

Run the steps in order; mirror the greenfield setup, then add the
reverse-engineering pass. Every derived artifact starts at **`draft`** status —
adoption seeds the baseline; the layer skills raise it to ready.

### 1. Detect existing code and docs (first)

Survey the repository: source modules, public interfaces, configuration,
existing READMEs/ADRs/design notes, and any tests. Record what exists so the
reverse-engineering pass has sources to cite. Note tests as evidence for
BDD/TDD baselines.

### 2. Infer the domain

Infer the domain from the code and docs (Financial / Software-SaaS /
Healthcare / E-commerce / IoT / Generic) and confirm with the user; this drives
the same terminology mappings `project-init` applies. Default to Generic if
ambiguous.

### 3. Scaffold the 8-layer structure

Create the artifact directories plus support folders (same as greenfield):

```bash
mkdir -p docs/{01_BRD,02_PRD,03_EARS,04_BDD,05_ADR,06_SPEC,07_TDD,08_IPLAN}
mkdir -p docs/08_IPLAN/tmp plans
```

### 4. Reverse-engineer baseline artifacts (the brownfield step)

Derive a baseline for each of the 8 artifacts from the existing system, working
**from the code upward and downward**, all at `draft` status. Use the layer
registry (`${CLAUDE_PLUGIN_ROOT}/framework/registry/LAYER_REGISTRY.yaml`) for the artifact set and
each template under `${CLAUDE_PLUGIN_ROOT}/framework/layers/NN_<X>/`:

| Layer | Artifact | Reverse-engineered from |
|-------|----------|-------------------------|
| 6 | SPEC | Module/interface signatures, data models, contracts in code |
| 5 | ADR | Existing design notes; decisions implied by the architecture |
| 3-4 | EARS, BDD | Observable behavior; existing tests → scenarios |
| 1-2 | BRD, PRD | Product behavior and capabilities the system delivers |
| 7-8 | TDD, IPLAN | Existing test suites and the as-built file layout |

Mark inferred content explicitly and never invent placeholder IDs for gaps —
leave them for the audits to surface. Add upstream `@` tags only where the
real upstream artifact now exists; record unknowns as gaps, not fabricated
references.

### 5. Register indexes

Create the per-layer index files so derived artifacts are discoverable:

```bash
touch docs/01_BRD/BRD-00_index.md docs/02_PRD/PRD-00_index.md \
      docs/03_EARS/EARS-00_index.md docs/04_BDD/BDD-00_index.md \
      docs/05_ADR/ADR-00_index.md docs/06_SPEC/SPEC-00_index.md \
      docs/07_TDD/TDD-00_index.md docs/08_IPLAN/IPLAN-00_index.yaml
```

### 6. Validate

Confirm all 8 directories, the index files, `plans/`, and one draft baseline
artifact per layer exist. If anything is missing, re-run the relevant step.

### 7. Hand off to gap-closing

Report adoption complete with the list of draft artifacts and known gaps, then
direct the user to:

- `../doc-flow/SKILL.md` to drive the layers forward, and
- the per-layer `-audit` skills (`../doc-brd-audit/SKILL.md` …
  `../doc-iplan-audit/SKILL.md`) to score each draft and produce fix reports
  for the matching `-fixer` skills,

so the drafts close their gaps and rise from `draft` to ready. Run
`../doc-validator/SKILL.md` once baselines link up to confirm traceability.

## Adaptation

Before scaffolding, read the project adaptation profile
(`.aidoc/profile.yaml`). Honor `active_layers`: create structure for the
active layers only — do not scaffold a disabled skippable layer. Ignore any
unknown or out-of-surface key.
Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Greenfield counterpart: `../project-init/SKILL.md`
- Next: `../doc-flow/SKILL.md` · per-layer `-audit` skills (e.g.
  `../doc-spec-audit/SKILL.md`)
- Layer registry (the 8 artifacts): `${CLAUDE_PLUGIN_ROOT}/framework/registry/LAYER_REGISTRY.yaml`
- Templates & READMEs: `${CLAUDE_PLUGIN_ROOT}/framework/layers/NN_<X>/`
- Traceability check: `../doc-validator/SKILL.md`
- Diagrams: `../charts-flow/SKILL.md`
