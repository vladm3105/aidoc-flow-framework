# `.aidoc/` — Project Override Layer and Profile

## Document Control

| Field | Value |
|-------|-------|
| Version | 2.0 |
| Status | Approved |
| Last Updated | 2026-09-07 |
| Author | Framework Maintainer |
| Framework Version | 0.53.0 |

`.aidoc/` is the **project customization layer** for every project that uses the
framework. It holds the project profile (adaptation knobs) and project-specific
overrides that take precedence over the framework's defaults.

The question `.aidoc/` answers: **"what is different about THIS project?"**

## The four tiers at a glance

```
<project>/
├── seed/, chg/              — human inputs (committed)
├── docs/                    — AI outputs, the produced chain (committed)
├── .aidoc/                  — project overrides + profile (committed) ← this tier
└── logs/<TS>/               — tool internals (gitignored)
```

| Tier | What | Lifecycle |
|------|------|-----------|
| Inputs | human-authored seeds + change requests | committed |
| Outputs | the produced 10-layer chain (BRD → IPLAN + CHG + EVAL) | committed |
| Project (`.aidoc/`) | profile, project-specific templates/rules/playbooks | committed |
| Tool internals (`logs/`) | execution metadata, raw engine/CLI stdout, timing | gitignored |

## What `.aidoc/` contains

```
.aidoc/
├── profile.yaml             # project profile — adaptation knobs
├── framework → ...          # symlink to shared framework/ (canonical path)
├── project/                 # project-specific overrides (same structure as framework/)
│   ├── layers/              # template overrides
│   │   └── 06_SPEC/
│   │       └── SPEC-TEMPLATE.yaml
│   ├── governance/          # rule overrides
│   │   ├── GOVERNANCE_RULES.md
│   │   └── ...
│   └── playbooks/           # playbook overrides
│       └── 01_BRD/
│           └── auditor.md
└── README.md
```

### `profile.yaml` — the project profile

Per [`framework/governance/ADAPTATION.md`](../governance/ADAPTATION.md):

> The project profile (`.aidoc/profile.yaml`) is the single input an
> engine reads when authoring or auditing. Version-controlled, so audits
> are reproducible in CI.

Effective precedence: `framework defaults < user-global seed < project
profile`.

The profile carries the **project's adaptation-knob overrides only** — the
closed knob set defined in
[`ADAPTATION_SURFACE.yaml`](../governance/ADAPTATION_SURFACE.yaml)
(`active_layers`, `section_toggles`, `audit_threshold`, `glossary`,
`review_mode`, `quality_loop_max_iterations`). It is an override-only delta;
absent keys fall through to the framework default. **Per-layer review crews and
persona weights are framework-defined** (`REVIEW_CREWS.yaml`) and are **not**
project-overridable through this surface. If a project has no `profile.yaml`, an
engine bootstraps one from
[`PROFILE-TEMPLATE.yaml`](../governance/PROFILE-TEMPLATE.yaml).

### `framework/` — the shared framework symlink

`.aidoc/framework/` is a symlink to the shared framework directory. This is the
**canonical path** that new files should reference. The project root `framework/`
is a backward-compat symlink chain:

```
framework → .aidoc/framework → <shared-framework-location>
```

### `project/` — project-specific overrides

A project may place files in `.aidoc/project/` using the same directory
structure as `framework/`. When an engine reads a template, rule, or playbook,
it checks `.aidoc/project/` first. If the file exists there, it replaces the
framework version. If not, the framework version applies.

Override structure mirrors `framework/`:

| Override path | Replaces |
|---------------|----------|
| `.aidoc/project/layers/06_SPEC/SPEC-TEMPLATE.yaml` | `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml` |
| `.aidoc/project/governance/GOVERNANCE_RULES.md` | `framework/governance/GOVERNANCE_RULES.md` |
| `.aidoc/project/playbooks/01_BRD/auditor.md` | `framework/playbooks/01_BRD/auditor.md` |

**Project overrides are project-local** — they never modify the shared
`framework/` directory. Each project carries its own overrides.

### Why project overrides exist

Projects adopt the framework at different versions and have different
constraints. A project may need:

- A modified template (extra section, different structure)
- Additional governance rules (Docker conventions, migration strategy)
- Custom playbooks (different review lens for the project's domain)

These live in `.aidoc/project/` — never in `framework/` itself. The
framework stays engine-agnostic; projects customize without forking.

## Discovery rule

When an engine reads a template, rule, or playbook:

1. Check `.aidoc/project/{same-path}` first
2. If the file exists there, use it (project override)
3. If not, fall back to `.aidoc/framework/{same-path}` (shared framework)

This is the same pattern as software: project-local config overrides
global defaults (e.g., `.eslintrc` vs `node_modules/.eslintrc`).

## Symlink convention

`.aidoc/framework/` is a symlink to the shared framework directory. The project
root `framework/` is a backward-compat symlink chain:

```
framework → .aidoc/framework → <shared-framework-location>
```

New files use `.aidoc/framework/` as the canonical path. The root symlink
exists only for backward compatibility with existing references. It will be
removed when zero active files reference `framework/`.

## Migration from provenance model

The original `.aidoc/` contract defined it as "AI provenance" with `audit/`,
`review/`, `remediation/`, `validation/`, `security/`, `quality/`
subdirectories. These were not used in practice — they remained empty in
every project. The new model repurposes `.aidoc/` as the project override
layer (GD-25).

## See also

- [`governance/ADAPTATION.md`](../governance/ADAPTATION.md) — profile semantics + §10 project overrides
- [`governance/ADAPTATION_SURFACE.yaml`](../governance/ADAPTATION_SURFACE.yaml) — closed knob registry
- [`README.md`](../README.md) — framework layout and four-tier model
