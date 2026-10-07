# `.aidoc/` — Project Override Layer and Profile

## Document Control

| Field | Value |
|-------|-------|
| Version | 2.4 |
| Status | Approved |
| Last Updated | 2026-10-06 |
| Author | <your name> |
| Framework Version | 0.90.0 |

This directory is the project customization layer for the aidoc-flow-framework.
It holds the project profile (adaptation knobs) and project-specific overrides
that take precedence over the framework's defaults.

## Project tier overview

A consumer project structures files into four explicit tiers (`README.md`, `AIDOC.md`):

```
<project>/
├── seed/                    # Tier 1 Inputs: stakeholder vision & architecture options
│   ├── 00_index.md          # Master seed index (optional)
│   ├── vision/              # Business intent & product goals
│   └── architecture/        # Architecture domains (scaffold: SEED-TEMPLATE.md)
│       └── auth.md
├── docs/                    # Tier 2 AI outputs: modules/ + sdd/ formal chain
├── .aidoc/                  # Tier 3 Project customization layer (this directory)
│   ├── profile.yaml         # project profile — adaptation knobs
│   ├── framework → ...      # symlink to shared framework (canonical path)
│   ├── project/             # project-specific overrides
│   │   ├── governance/      # rule overrides (e.g. CHG_EXECUTION_FLOW.md)
│   │   │   └── CHG_EXECUTION_FLOW.md
│   │   ├── layers/          # template overrides (same structure as framework/)
│   │   │   └── ...
│   │   └── playbooks/       # playbook overrides (same structure as framework/)
│   │       └── ...
│   └── README.md            # this file
└── logs/<TS>/               # Tier 4 Tool internals (gitignored)
```

## Directory structure (`.aidoc/`)

```
.aidoc/
├── profile.yaml             # project profile — adaptation knobs
├── framework → ...          # symlink to shared framework (canonical path)
├── project/                 # project-specific overrides
│   ├── governance/          # rule overrides (same structure as framework/)
│   │   └── ...
│   ├── layers/              # template overrides (same structure as framework/)
│   │   └── ...
│   └── playbooks/           # playbook overrides (same structure as framework/)
│       └── ...
└── README.md                # this file
```

## Discovery rule

When the agent reads a template, rule, or playbook:

1. Check `.aidoc/project/{same-path}` first
2. If the file exists there, use it (project override)
3. If not, fall back to `.aidoc/framework/framework/{same-path}` (or `.aidoc/framework/{same-path}` if pointing directly at the framework root)

## Framework symlink

`.aidoc/framework/` is a symlink to the shared framework directory.
The canonical path is declared in `profile.yaml` as `framework_path`.

## Project profile

`.aidoc/profile.yaml` carries the project's adaptation-knob overrides. See
`framework/governance/ADAPTATION.md` for the full contract and
`framework/governance/ADAPTATION_SURFACE.yaml` for the closed knob registry.

## Project overrides

Project-specific files live in `.aidoc/project/` using the same directory
structure as the framework. See `framework/governance/ADAPTATION.md` §10 for
the override contract and constraints.

## Framework version

This project pins **aidoc-flow-framework X.Y.Z** (declared in
`profile.yaml` as `framework_version`).



## Autonomous Execution & Operational Standards

Autonomous agents operate under six core project governance blueprints initialized under `<project>/.aidoc/project/governance/`:

1. **CHG Execution Flow (`CHG_EXECUTION_FLOW.md`):**
   Copy [`framework/governance/aidoc/AIDOC-CHG-EXECUTION-FLOW-TEMPLATE.md`](AIDOC-CHG-EXECUTION-FLOW-TEMPLATE.md). Codifies the 8-step autonomous change lifecycle, tiered document versioning, and circuit breakers.
2. **CI Smart Routing (`CI_SMART_ROUTING.md`):**
   Copy [`framework/governance/aidoc/AIDOC-CI-SMART-ROUTING-TEMPLATE.md`](AIDOC-CI-SMART-ROUTING-TEMPLATE.md). Codifies the Anti-Deadlock Invariant (zero trigger-level path filtering on required checks) and internal path-filter job routing.
3. **Conflict Resolution (`CONFLICT_RESOLUTION.md`):**
   Copy [`framework/governance/aidoc/AIDOC-CONFLICT-RESOLUTION-TEMPLATE.md`](AIDOC-CONFLICT-RESOLUTION-TEMPLATE.md). Codifies Class 1 additive vs Class 2 semantic conflict handling, zero force-pushes, and mandatory auto-merge re-arming.
4. **Self-Review Loop (`SELF_REVIEW_LOOP.md`):**
   Copy [`framework/governance/aidoc/AIDOC-SELF-REVIEW-LOOP-TEMPLATE.md`](AIDOC-SELF-REVIEW-LOOP-TEMPLATE.md). Codifies the Two-Stage Review & Fix loop (Stage A specs vs Stage B PRs), strict independence (Judge $\neq$ Generator), and the 4-lens rubric.
5. **QA Protocol (`QA_PROTOCOL.md`):**
   Copy [`framework/governance/aidoc/AIDOC-QA-PROTOCOL-TEMPLATE.md`](AIDOC-QA-PROTOCOL-TEMPLATE.md). Codifies the Tripartite Engineering Architecture, the strict non-code-modifying invariant for QA, and post-merge closing reports.
6. **Browser Testing (`BROWSER_TESTING.md`):**
   Copy [`framework/governance/aidoc/AIDOC-BROWSER-TESTING-TEMPLATE.md`](AIDOC-BROWSER-TESTING-TEMPLATE.md). Codifies headless browser execution, multi-worktree port sandboxing, and trace/screenshot artifact retention.

## Seed tier bootstrapping

Initial human-authored requirements live under `<project>/seed/` before the first
BRD is authored (`SEED_CONTRACT.md` R1). Seed documents explore options, trade-offs,
and architectural invariants without carrying formal SDD element IDs. Initialize
substantive architecture domains from [`framework/templates/SEED-TEMPLATE.md`](../../templates/SEED-TEMPLATE.md).
