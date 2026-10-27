# Project Kickoff Guide

> [!IMPORTANT]
> **Live Framework Version: 0.96.19.** The definitive quickstart for teams initiating new projects with `aidoc-flow-framework`. Docs index: [`docs/README.md`](README.md). The 2026-05 migration brief formerly appended here moved verbatim to [`docs/history/STARTUP-BRIEF-2026-05-20.md`](history/STARTUP-BRIEF-2026-05-20.md) (CHG-128).

---

## 0. Project Kickoff Quickstart (Version 0.96.19)

### 0.1 The Modern SDD Framework at a Glance

The framework defines an engine-agnostic, 10-layer Specification-Driven Development flow:

```text
BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code → EVAL → Verified
```

- **Autonomous Execution**: Routine development is executed by AI agents in isolated git worktrees without human micro-management.
- **Governance Gate**: Any code write requires an authorizing Change Request (`CHG`) and Implementation Plan (`IPLAN`).
- **3-Tier Multi-Agent Execution Architecture** ([`DURABLE_EXECUTION_STANDARD.md`](../framework/governance/DURABLE_EXECUTION_STANDARD.md)):
  - **Tier 1 (Durable Workflows)**: Orchestrates saga compensations, human gates, zero-cost durable waits, and execution timeouts.
  - **Tier 2 (Cognitive Graphs)**: Executes cyclical reasoning, review loops ([`REVIEW_WORKFLOW_STANDARD.md`](../framework/governance/REVIEW_WORKFLOW_STANDARD.md)), and diagnostic patches. Proposes artifacts without direct git mutation.
  - **Tier 3 (Deterministic Services)**: Executes isolated worktrees ([`WORKTREE_FLOW.md`](../framework/governance/WORKTREE_FLOW.md)), compilation, linters (`sdd_doc_lint`, `sdd_swf_lint`), and test suites.
- **The Golden Rule**: *Reasoning in Cognitive Graphs, Effects in Deterministic Services, Control in Durable Workflows.*

### 0.2 Quickstart: 6 Steps to Launch a New Project

#### Prerequisites

- `git` and network access to github.com (or a local canon clone for `--canon-dir` air-gapped installs).
- Python `>=3.11` with `pyyaml` and `jsonschema` (the `sdd_doc_lint` runtime; the canon toolchain pins Python 3.12).
- Recommended: `task` (runs `.aidoc/Taskfile.yml`) and `gh` (PR flow).

#### Step 1: Deploy `.aidoc/` via Automated Installer

From the framework repository or clone, run [`framework/scripts/install.sh`](../framework/scripts/install.sh):

```bash
# Option A: Production deployment from local clone (self-contained pin, offline-capable):
framework/scripts/install.sh <project-dir> --canon-dir /path/to/aidoc-flow-framework --kind pin

# Option B: Production deployment from published git release tag:
framework/scripts/install.sh <project-dir> --canon framework/v0.96.19 --kind pin

# Option C: Git submodule deployment (tracked by git, pinned to a release tag):
git submodule add https://github.com/vladm3105/aidoc-flow-framework.git .aidoc/framework
git -C .aidoc/framework checkout framework/v0.96.19
```

This executes [`BOOTSTRAP.md`](../framework/governance/aidoc/BOOTSTRAP.md) steps 1–5 automatically and verifies directory structure health.

#### Step 2: Configure Project Adaptation (`.aidoc/profile.yaml`)

Review `<project>/.aidoc/profile.yaml` (seeded from `PROFILE-TEMPLATE.yaml`). Tune only the knobs your project needs:

- `review_mode`: `team` (multi-persona crew fan-out) or `single_pass`.
- `active_layers`: `[BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN, EVAL]` (dropping `BDD` or `ADR` applies the cascade rule).
- `audit_threshold`: configure threshold bounds and Binary Topological Validation (BTV).
- `exec_*`: bounds on files (8), diff lines (600), token budgets (200k), and patch attempts (3).

#### Step 3: Establish the Root Working Agreement (`<project>/AGENTS.md`)

`install.sh` scaffolds `<project>/AGENTS.md` from [`framework/templates/AGENTS-TEMPLATE.md`](../framework/templates/AGENTS-TEMPLATE.md) (consumer path: `<project>/.aidoc/framework/framework/templates/AGENTS-TEMPLATE.md`) when missing — the template is the single source; do not maintain a hand-written variant. It binds every AI coding agent to the Governance Gate (authorizing CHG + IPLAN before any code write), the state-surface table, and the per-task worktree flow.

#### Step 4: Instantiate Operational Governance Blueprints

`install.sh` scaffolds the 8 required operational blueprints under `<project>/.aidoc/project/governance/` by default (`--no-blueprints` to skip; the installer smoke-asserts their presence). The commands below are the manual fallback (submodule consumers, opted-out installs); see [`docs/ADAPTATION-GUIDE.md`](ADAPTATION-GUIDE.md) §4.1:

```bash
mkdir -p <project>/.aidoc/project/governance

# Copy blueprints from the vendored framework:
cp <project>/.aidoc/framework/framework/governance/aidoc/AIDOC-CHG-EXECUTION-FLOW-TEMPLATE.md \
   <project>/.aidoc/project/governance/CHG_EXECUTION_FLOW.md
cp <project>/.aidoc/framework/framework/governance/aidoc/AIDOC-CI-SMART-ROUTING-TEMPLATE.md \
   <project>/.aidoc/project/governance/CI_SMART_ROUTING.md
cp <project>/.aidoc/framework/framework/governance/aidoc/AIDOC-CONFLICT-RESOLUTION-TEMPLATE.md \
   <project>/.aidoc/project/governance/CONFLICT_RESOLUTION.md
cp <project>/.aidoc/framework/framework/governance/aidoc/AIDOC-SELF-REVIEW-LOOP-TEMPLATE.md \
   <project>/.aidoc/project/governance/SELF_REVIEW_LOOP.md
cp <project>/.aidoc/framework/framework/governance/aidoc/AIDOC-QA-PROTOCOL-TEMPLATE.md \
   <project>/.aidoc/project/governance/QA_PROTOCOL.md
cp <project>/.aidoc/framework/framework/governance/aidoc/AIDOC-BROWSER-TESTING-TEMPLATE.md \
   <project>/.aidoc/project/governance/BROWSER_TESTING.md
cp <project>/.aidoc/framework/framework/governance/DURABLE_EXECUTION_STANDARD.md \
   <project>/.aidoc/project/governance/DURABLE_EXECUTION.md
cp <project>/.aidoc/framework/framework/governance/REVIEW_WORKFLOW_STANDARD.md \
   <project>/.aidoc/project/governance/REVIEW_WORKFLOWS.md
```

#### Step 5: Author Initial Seed & First Cycle

Scaffold the initial seed document and Layer 1 BRD:

```bash
mkdir -p <project>/seed <project>/docs/sdd/01_BRD/BRD-01
cp <project>/.aidoc/framework/framework/templates/SEED-TEMPLATE.md <project>/seed/SEED-01.md
```

1. Fill out `<project>/seed/SEED-01.md` with stakeholder requirements (`seed/` at project root is the canonical Tier 1 path per `SEED_CONTRACT.md`; CHG-128 / #1024).
2. Decompose seed into architecture domains per [`SEED_TO_MODULE_DECOMPOSITION.md`](../framework/governance/SEED_TO_MODULE_DECOMPOSITION.md).
3. Author Layer 1 `BRD` (`docs/sdd/01_BRD/BRD-01/BRD-01.yaml`) to initiate the formal SDD chain.

#### Step 6: Verify Project Scaffolding Health

Validate the newly scaffolded project environment before creating the initial commit:

```bash
# 1. Profile must validate against the adaptation surface
PYTHONPATH=<project>/.aidoc/framework python3 -m sdd_doc_lint.profile_lint <project>/.aidoc/profile.yaml

# 2. Scaffolded SDD tree must lint clean
PYTHONPATH=<project>/.aidoc/framework python3 -m sdd_doc_lint <project>/docs/sdd

# 3. CHG linting capability
python3 <project>/.aidoc/framework/sdd_doc_lint/chg_lint.py --help
```

---

### Brownfield adoption (existing codebase)

Same installer — it only adds `.aidoc/`, `docs/sdd/`, root `AGENTS.md`, and root `stack-policy.yaml` (each skipped when present or opted out); existing sources are untouched. Then reconcile the standing codebase through a CODE2S (Type-R) change per [`CHG_REQUEST_FLOWS.md`](../framework/governance/CHG_REQUEST_FLOWS.md), which reverse-authors specs from verified code.
