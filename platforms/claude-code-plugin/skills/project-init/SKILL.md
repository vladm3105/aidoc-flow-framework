---
name: project-init
description: Initialize a new (greenfield) project for the SDD flow - domain selection, folder scaffolding, and index files. Use once, before any artifact creation; then hand off to doc-flow.
metadata:
  tags:
    - sdd-workflow
    - utility
  custom_fields:
    skill_category: core-workflow
    upstream_artifacts: []
    downstream_artifacts: [BRD]
    version: "0.2.0"
    framework_spec_version: "0.1.0"
    last_updated: "2026-05-23"
---

# project-init

## Purpose

Scaffold a brand-new project for the SDD flow: select a domain, create the
8-layer folder structure and index files, and apply domain terminology — the
one-time setup that must happen **before** workflow execution.

**Layer**: cross-cutting utility (precedes BRD).

## When to Use

**Use when**:
- Starting a greenfield project — no `docs/` structure yet.
- The domain has not been selected.

**Do NOT use when**:
- `docs/01_BRD/` etc. already exist — go straight to `../doc-flow/SKILL.md`.

## Behavior

Run the steps in order; create folders before any documents.

### 1. Domain selection (first)

Present the questionnaire (`framework/DOMAIN_SELECTION_QUESTIONNAIRE.md`) and
load the matching config:

| Choice | Domain | Config |
|--------|--------|--------|
| 1 (default) | Financial Services | `FINANCIAL_DOMAIN_CONFIG.md` |
| 2 | Software / SaaS | `SOFTWARE_DOMAIN_CONFIG.md` |
| 3 | Healthcare | `DOMAIN_ADAPTATION_GUIDE.md` |
| 4 | E-commerce | `DOMAIN_ADAPTATION_GUIDE.md` |
| 5 | IoT | `DOMAIN_ADAPTATION_GUIDE.md` |
| 6 | Other / Generic | `GENERIC_DOMAIN_CONFIG.md` |

### 2. Folder structure

Create the 8 artifact directories plus support folders:

```bash
mkdir -p docs/{01_BRD,02_PRD,03_EARS,04_BDD,05_ADR,06_SPEC,07_TDD,08_IPLAN}
mkdir -p docs/08_IPLAN/tmp plans
```

### 3. Domain configuration

Read the selected config and apply its placeholder mappings (e.g. Financial:
`[RESOURCE_ITEM]→Position`, `[USER_ROLE]→Trader`; Software:
`[RESOURCE_ITEM]→Resource`, `[USER_ROLE]→Account Admin`; Generic:
`[RESOURCE_ITEM]→Entity`). Create any domain-specific subdirectories.

### 4. Index files

```bash
touch docs/01_BRD/BRD-00_index.md docs/02_PRD/PRD-00_index.md \
      docs/03_EARS/EARS-00_index.md docs/04_BDD/BDD-00_index.md \
      docs/05_ADR/ADR-00_index.md docs/06_SPEC/SPEC-00_index.md \
      docs/07_TDD/TDD-00_index.md docs/08_IPLAN/IPLAN-00_index.yaml
```

Each artifact created later must complete a **Document Control** section
(name, version, date, owner, status, revision history).

### 5. Validate

Confirm all 8 directories, the index files, the domain subdirectories, and
`plans/` exist. If anything is missing, re-run the relevant step.

### 6. Hand off

Report initialization complete and direct the user to `../doc-flow/SKILL.md`
to begin with `doc-brd`. Templates are referenced from `framework/layers/NN_<X>/`;
copying them into the project is optional.

## Related Resources

- Next: `../doc-flow/SKILL.md` (start with `doc-brd`)
- Domain questionnaire: `framework/DOMAIN_SELECTION_QUESTIONNAIRE.md`
- Domain configs: `framework/FINANCIAL_DOMAIN_CONFIG.md`,
  `framework/SOFTWARE_DOMAIN_CONFIG.md`, `framework/GENERIC_DOMAIN_CONFIG.md`
- Layer registry: `framework/registry/LAYER_REGISTRY.yaml`
- Templates & READMEs: `framework/layers/NN_<X>/`
- Diagrams: `../charts-flow/SKILL.md`
