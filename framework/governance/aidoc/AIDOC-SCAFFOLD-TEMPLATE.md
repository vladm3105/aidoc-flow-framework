# `.aidoc/` — Project Override Layer and Profile

## Document Control

| Field | Value |
|-------|-------|
| Version | 2.5 |
| Status | Approved |
| Last Updated | 2026-10-09 |
| Author | <your name> |
| Framework Version | 0.91.23 |

This directory is the project customization layer for the aidoc-flow-framework.
It holds the project profile (adaptation knobs) and project-specific overrides
that take precedence over the framework's defaults.

## Project tier overview

A consumer project structures files into four explicit tiers (`README.md`, `AIDOC.md`):

```text
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

```text
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

Autonomous agents operate under eight core project governance blueprints initialized under `<project>/.aidoc/project/governance/` (mirroring `docs/ADAPTATION-GUIDE.md` §4.1):

1. **CHG Execution Flow (`CHG_EXECUTION_FLOW.md`):**
   Copy [`framework/governance/aidoc/AIDOC-CHG-EXECUTION-FLOW-TEMPLATE.md`](https://github.com/vladm3105/aidoc-flow-framework/blob/main/framework/governance/aidoc/AIDOC-CHG-EXECUTION-FLOW-TEMPLATE.md). Codifies the 8-step autonomous change lifecycle, tiered document versioning, and circuit breakers.
2. **CI Smart Routing (`CI_SMART_ROUTING.md`):**
   Copy [`framework/governance/aidoc/AIDOC-CI-SMART-ROUTING-TEMPLATE.md`](https://github.com/vladm3105/aidoc-flow-framework/blob/main/framework/governance/aidoc/AIDOC-CI-SMART-ROUTING-TEMPLATE.md). Codifies the Anti-Deadlock Invariant (zero trigger-level path filtering on required checks) and internal path-filter job routing.
3. **Conflict Resolution (`CONFLICT_RESOLUTION.md`):**
   Copy [`framework/governance/aidoc/AIDOC-CONFLICT-RESOLUTION-TEMPLATE.md`](https://github.com/vladm3105/aidoc-flow-framework/blob/main/framework/governance/aidoc/AIDOC-CONFLICT-RESOLUTION-TEMPLATE.md). Codifies Class 1 additive vs Class 2 semantic conflict handling, zero force-pushes, and mandatory auto-merge re-arming.
4. **Self-Review Loop (`SELF_REVIEW_LOOP.md`):**
   Copy [`framework/governance/aidoc/AIDOC-SELF-REVIEW-LOOP-TEMPLATE.md`](https://github.com/vladm3105/aidoc-flow-framework/blob/main/framework/governance/aidoc/AIDOC-SELF-REVIEW-LOOP-TEMPLATE.md). Codifies the Two-Stage Review & Fix loop (Stage A specs vs Stage B PRs), strict independence (Judge $\neq$ Generator), and the 4-lens rubric.
5. **QA Protocol (`QA_PROTOCOL.md`):**
   Copy [`framework/governance/aidoc/AIDOC-QA-PROTOCOL-TEMPLATE.md`](https://github.com/vladm3105/aidoc-flow-framework/blob/main/framework/governance/aidoc/AIDOC-QA-PROTOCOL-TEMPLATE.md). Codifies the Tripartite Engineering Architecture, the strict non-code-modifying invariant for QA, and post-merge closing reports.
6. **Browser Testing (`BROWSER_TESTING.md`):**
   Copy [`framework/governance/aidoc/AIDOC-BROWSER-TESTING-TEMPLATE.md`](https://github.com/vladm3105/aidoc-flow-framework/blob/main/framework/governance/aidoc/AIDOC-BROWSER-TESTING-TEMPLATE.md). Codifies headless browser execution, multi-worktree port sandboxing, and trace/screenshot artifact retention.
7. **Durable Multi-Agent Execution Standard (`DURABLE_EXECUTION.md`):**
   Derived from [`framework/governance/DURABLE_EXECUTION_STANDARD.md`](https://github.com/vladm3105/aidoc-flow-framework/blob/main/framework/governance/DURABLE_EXECUTION_STANDARD.md). Codifies the 3-Tier Execution Architecture (Tier 1 Durable Workflows, Tier 2 Cognitive Reasoning Graphs, Tier 3 Deterministic Services), Thin-State payload discipline ($\le 2$ KB), SAGA reverse compensations, and deterministic rollback.
8. **Graph-Based Review Flows & Review Report Schema (`REVIEW_WORKFLOWS.md`):**
   Derived from [`framework/governance/REVIEW_WORKFLOW_STANDARD.md`](https://github.com/vladm3105/aidoc-flow-framework/blob/main/framework/governance/REVIEW_WORKFLOW_STANDARD.md) and [`review_report.schema.json`](https://github.com/vladm3105/aidoc-flow-framework/blob/main/framework/governance/review_report.schema.json). Codifies structured multi-persona review flows, workflow linting (`sdd_swf_lint`), deterministic quality gate floors (`structural_pass == true && blocking_findings == 0`), and automated `chg_handover` metadata.

## Seed tier bootstrapping

Initial human-authored requirements live under `<project>/seed/` before the first
BRD is authored (`SEED_CONTRACT.md` R1). Seed documents explore options, trade-offs,
and architectural invariants without carrying formal SDD element IDs. Initialize
substantive architecture domains from [`framework/templates/SEED-TEMPLATE.md`](https://github.com/vladm3105/aidoc-flow-framework/blob/main/framework/templates/SEED-TEMPLATE.md).

## Sanctioned Surfaces & Deprecated Anti-Patterns

Autonomous AI agents frequently default to generic open-source patterns when onboarding.
The framework explicitly prohibits loose monolithic files in favor of structured SDD layers:

- ❌ **`docs/DECISIONS.md` / `plans/DECISIONS.md` (Retired per CHG-80 / CHG-95 / GD-71 / GD-78):**
  Monolithic decision logs cause split-brain context and token saturation.
  - **Architectural decisions** belong strictly in **Layer 05** (`docs/sdd/05_ADR/`) as structured YAML records (`ADR-00_index.yaml`, `ADR-NN.yaml`).
  - **Operational / change decisions** belong strictly in **Layer 09** (`docs/sdd/09_CHG/`) inside authorizing Change Requests (`CHG-NN.yaml` Section 1B `decision:`).
- ❌ **`ROADMAP.md` (Retired):**
  Monolithic roadmaps drift. Feature planning and milestones live in `plans/<NAME>-PLAN.md` and GitHub milestones/issues.
- ❌ **`CHANGELOG.md` (Retired per CHG-40 / CHG-94):**
  Manual markdown changelogs cause merge conflicts. GitHub Releases and structured change records (`docs/sdd/09_CHG/archive/`) serve as the changelog.
- ❌ **`docs/HANDOFF.md` / `plans/HANDOFF.md` (Retired):**
  Active session continuity lives in GitHub issues and verified plans, never in ephemeral markdown files committed to git.

## Repository AGENTS.md Template

Consumer repositories should establish a root `<project>/AGENTS.md` by copying
[`framework/templates/AGENTS-TEMPLATE.md`](https://github.com/vladm3105/aidoc-flow-framework/blob/main/framework/templates/AGENTS-TEMPLATE.md)
to declare explicit non-adoption of legacy files and anchor agent behavior:

```markdown
## Where state lives (this repo owns its own continuity)

| Surface | Path | Status |
|---|---|---|
| Decisions (Architecture) | `docs/sdd/05_ADR/` (Layer 05) | Structured YAML records; `docs/DECISIONS.md` is a retired anti-pattern (GD-78) |
| Decisions (Change) | `docs/sdd/09_CHG/` (Layer 09) | Authored in Section 1B of authorizing Change Requests (`CHG-*.yaml`) |
| Changelog | GitHub Releases + `docs/sdd/09_CHG/archive/` | Structured change requests serve as change records; `CHANGELOG.md` is retired / not adopted |
| Roadmap | GitHub Milestones / Issues + `plans/*-PLAN.md` | Feature planning lives in verified plans and milestones; `ROADMAP.md` is retired / not adopted |
| Session Continuity | GitHub Issues + `plans/*-PLAN.md` | Live handoff lives on the active issue; `docs/HANDOFF.md` is retired / not adopted |
| Lessons Learned | `.aidoc/learning/learnings.md` | Consolidated, PR-reviewed system of record; harness memory is scratch, never the record |
```
