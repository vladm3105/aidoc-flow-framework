# `.aidoc/` — Project Override Layer and Workstation Standard

## Document Control

| Field | Value |
|---|---|
| Version | 2.4 |
| Status | Approved |
| Last Updated | 2026-10-24 |
| Author | Framework Maintainer |
| Framework Version | 0.96.17 |
| Authority | [Decision D-0013 / GD-13](../DECISIONS.md) (historical tombstone), [`AIDOC_WORKSTATION_STANDARD.md`](../../../docs/AIDOC_WORKSTATION_STANDARD.md), [`MULTI_PROJECT_FEDERATED_STANDARD.md`](../MULTI_PROJECT_FEDERATED_STANDARD.md) |

---

`.aidoc/` is the **project customization and workstation layer** for every repository adopting the framework. It holds the project profile (adaptation knobs), technical engine bindings, canonical task definitions, enterprise tech stack policies, and project-specific overrides that take precedence over the framework defaults.

The question `.aidoc/` answers: **"what is different about THIS project?"**

## The four tiers at a glance

```text
<project>/
├── seed/                     — Tier 1 Inputs: human-authored briefs & requirements (canonical; peer to docs/ per SEED_CONTRACT.md, CHG-128 / #1024)
├── docs/                     — all project documentation & specifications (committed)
│   ├── modules/              — Tier 2 Architecture: C4-L2 container specifications
│   └── sdd/                  — Tier 2 Process: formal 10-layer SDD chain
│       ├── 01_BRD .. 08_IPLAN
│       └── 09_CHG/           — Change governance & pre-change archives
│           └── archive/{CHG-ID}/{seed|modules|layer}/
├── .aidoc/                   — Tier 3 Project: overrides + profile + workstation tools (committed) ← this tier
└── logs/<TS>/                — Tier 4 Ephemeral: tool internals & execution traces (gitignored)
```

| Tier | Path | What | Lifecycle |
|---|---|---|---|
| **Inputs** | `seed/` (project root) | Human-authored requirements, initial briefs, stakeholder notes | Committed (versioned via CHG) |
| **Domain Specs** | `docs/modules/` | Architectural subsystems & C4-L2 container boundaries | Committed |
| **Process Chain** | `docs/sdd/` | Produced 10-layer chain (`01_BRD` → `08_IPLAN` + `10_EVAL`) | Committed |
| **Governance & Archives** | `docs/sdd/09_CHG/` | Active Change Requests (`CHG-*.yaml`) + pre-change archives (`archive/{CHG-ID}/`) | Committed |
| **Project (`.aidoc/`)** | `.aidoc/` | Profile, task runners, engine config, project-specific templates/rules/playbooks | Committed |
| **Tool Internals (`logs/`)** | `logs/<TS>/` | Execution metadata, raw engine/CLI stdout, timing benchmarks | Gitignored |

## What `.aidoc/` contains

Per the ratified Workstation Standard ([`docs/AIDOC_WORKSTATION_STANDARD.md`](../../../docs/AIDOC_WORKSTATION_STANDARD.md)), `.aidoc/` houses all four Quad-Pillar federated components:

```text
.aidoc/
├── profile.yaml              # project profile — adaptation knobs (closed surface)
├── stack-policy.yaml         # ⭐ Pillar 2: Enterprise Tech Stack Policy (schema 1.0.0)
├── Taskfile.yml              # ⭐ Canonical SDD task runner (sdd:lint, sdd:review, sdd:slice, sdd:check)
├── project/                  # ⭐ Tier 1: Project-specific overrides & specialized governance
│   ├── Taskfile.yml          # Optional project-specific task overrides
│   ├── governance/           # Specialized rules (e.g. CHG_EXECUTION_FLOW.md, WORKTREE_FLOW.md)
│   ├── layers/               # Customized templates (e.g. specialized 10_EVAL)
│   └── playbooks/            # Specialized review crew lenses (e.g. web3 security)
├── framework/                # ⭐ Tier 2: Process Canon defaults (Pillar 1)
│   ├── layers/               # Default templates (01_BRD .. 10_EVAL)
│   ├── playbooks/            # Standard persona playbooks (architect, security, etc.)
│   └── doc_lint/             # Canonical structural linters (sdd_doc_lint alias supported)
├── engine/                   # ⭐ Technical Engine Binding
│   └── engine.yaml           # Active engine config (aidoc-flow-langgraph, modes: live|verify-only|mock)
├── contracts/                # ⭐ Pillar 3: Data Contracts Canon (aidoc-data-contracts schemas)
│   └── contracts-registry.yaml
├── ctx-tools/                # ⭐ Pillar 4: Context Slicing Engine (aidoc-context-tools config)
│   └── config.yaml
└── bin/                      # (Optional / Deprecated) Backward-compatible CLI shims
    └── sdd-lint              # Compatibility shim delegating to task sdd:lint, doc_lint, or sdd_doc_lint
```

### `profile.yaml` — the project profile

Per [`framework/governance/ADAPTATION.md`](../ADAPTATION.md):

> The project profile (`.aidoc/profile.yaml`) is the single input an engine reads when authoring or auditing. Version-controlled, so audits are reproducible in CI.

Effective precedence: `framework defaults < user-global seed < project profile`.

The profile carries the **project's adaptation-knob overrides only** — the closed knob set defined in [`ADAPTATION_SURFACE.yaml`](../ADAPTATION_SURFACE.yaml) (`active_layers`, `section_toggles`, `audit_threshold`, `glossary`, `review_mode`, `quality_loop_max_iterations`, `ci_bindings`). Absent keys fall through to the framework default. If a project has no `profile.yaml`, an engine bootstraps one from [`PROFILE-TEMPLATE.yaml`](../PROFILE-TEMPLATE.yaml).

### `project/` — project-specific overrides

A project may place files in `.aidoc/project/` using the same directory structure as `framework/`. When an engine reads a template, rule, or playbook, it checks `.aidoc/project/` first. If the file exists there, it replaces the framework version. If not, the framework version applies.

Override structure mirrors `framework/`:

| Override path | Replaces |
|---|---|
| `.aidoc/project/layers/06_SPEC/SPEC-TEMPLATE.yaml` | `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml` |
| `.aidoc/project/governance/DOC_GOVERNANCE_CORE.md` | `framework/governance/DOC_GOVERNANCE_CORE.md` |
| `.aidoc/project/playbooks/01_BRD/auditor.md` | `framework/playbooks/01_BRD/auditor.md` |

**Project overrides are project-local** — they never modify the shared `framework/` directory.

## Two-Tier Discovery Protocol (`ENGINE-DISCOV-01`)

When an execution engine or agent reads a template, rule, or playbook:

1. Check `.aidoc/project/{same-path}` first.
2. If the file exists there, use it (**project override**).
3. If not, fall back to `.aidoc/framework/{same-path}` (**canon default**).
4. If absent in both locations, raise `ResourceNotFoundError`.

### Atomic File Shadowing Rule

Discovery enforces **Atomic File Shadowing**: Any file placed in `.aidoc/project/{path}` completely shadows and replaces `.aidoc/framework/{path}` at the file level. **Partial key merging is not performed.** This eliminates non-deterministic inheritance bugs and ensures identical behavior across all execution engines.

### Non-Weakening Invariant (`GATE-FLOOR-01`)

Project overrides in `.aidoc/project/` may tighten quality thresholds or introduce additional review personas, but may **never weaken** the quality gate floor:
- Mandatory SDD layers (`BRD`, `SPEC`, `TDD`, `IPLAN`, `CHG`) cannot be disabled.
- P0/P1 blocking findings cannot be demoted or suppressed.
- Cryptographic hash checks (`reviewed_sha256`) cannot be bypassed.

## Distribution and Attachment Model

> [!IMPORTANT]
> **Raw filesystem symlinks in version control are strictly forbidden.**  
> Symlinks across repositories (`.aidoc/framework -> ../../aidoc-framework`) fail under Docker containerization, CI runner isolation, and cross-platform operating systems.

The framework is attached to consumer repositories through two approved distribution patterns:

1. **Git Submodule:** The project commits `.aidoc/framework/` as a Git submodule pinned to an immutable release tag (e.g. `framework/v0.96.3`).
2. **Dynamic Clone / Pinned Copy:** Managed autonomously by **`aidoc-project-onboarding`**:
   - Greenfield: `onboard greenfield --name <service> --install`
   - Brownfield upgrade: `onboard update --target .`
   - In-repo installer fallback: `framework/scripts/install.sh <project> --kind pin`

## Migration from provenance model

The original `.aidoc/` contract defined it as "AI provenance" with `audit/`, `review/`, `remediation/`, `validation/`, `security/`, `quality/` subdirectories. These were not used in practice — they remained empty in every project. The modern standard repurposes `.aidoc/` as the project customization, task orchestration, and quality enforcement layer (GD-25, CHG-106).

## See also

- [`docs/AIDOC_WORKSTATION_STANDARD.md`](../../../docs/AIDOC_WORKSTATION_STANDARD.md) — canonical workstation directory topology & dual-control flow
- [`MULTI_PROJECT_FEDERATED_STANDARD.md`](../MULTI_PROJECT_FEDERATED_STANDARD.md) — Quad-Pillar federated ecosystem architecture
- [`ADAPTATION.md`](../ADAPTATION.md) — profile semantics, 15-knob surface, and runtime architecture
- [`ADAPTATION_SURFACE.yaml`](../ADAPTATION_SURFACE.yaml) — machine-readable closed knob registry
