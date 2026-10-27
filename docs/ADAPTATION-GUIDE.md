# Adapting the Framework to a New Project

## Document Control

| Field | Value |
|---|---|
| Version | 1.3 |
| Status | Approved |
| Last Updated | 2026-10-07 |
| Author | Framework Maintainer |
| Framework Version | 0.96.21 |

How to consume `aidoc-flow-framework` in a real project without forking
it: link (or clone) the framework, declare adaptation knobs in a profile,
and add project-local overrides. Based on the layout proven in a live
consumer (`.aidoc/` override layer with project profile and mirrored
overrides).

This guide is non-normative. The binding contract is
`framework/governance/ADAPTATION.md` (human-readable) plus
`framework/governance/ADAPTATION_SURFACE.yaml` (machine-readable knob
registry); the `.aidoc/` tier contract is
`framework/governance/aidoc/AIDOC.md`, the onboarding procedure is
`framework/governance/aidoc/BOOTSTRAP.md`, and the per-project starting point
is `framework/governance/aidoc/AIDOC-SCAFFOLD-TEMPLATE.md`. Where this
guide and those files disagree, they win.

## 1. Scaffold `.aidoc/`

### Automated Deployment (Recommended)

Run `framework/scripts/install.sh` from the framework repository or clone:

```bash
# Pinned allowlist copy (default; self-contained for production repositories):
framework/scripts/install.sh <project-dir> --canon framework/v0.96.21 --kind pin

# Or attach via Git submodule (pinned to a release tag, never a moving branch):
git submodule add https://github.com/vladm3105/aidoc-flow-framework.git .aidoc/framework
git -C .aidoc/framework checkout framework/v0.96.21
```

`install.sh` automates the ordered procedure from `BOOTSTRAP.md`:

1. Copies `AIDOC-SCAFFOLD-TEMPLATE.md` to `<project>/.aidoc/README.md` and populates author, date, and version placeholders;
2. Copies `PROFILE-TEMPLATE.yaml` to `<project>/.aidoc/profile.yaml`;
3. Attaches the framework: either copies the version-pinned allowlist (`docs/PROJECT.md` §7.1 / `allowlist.txt`, pruning internal archives) or attaches the framework via Git submodule or pinned copy;
4. Pins `metadata.framework_version` to the adopted canon version;
5. Initializes Layer 05 ADR index: scaffolds `<project>/docs/sdd/05_ADR/` and copies `framework/layers/05_ADR/ADR-00_index.TEMPLATE.yaml` to `ADR-00_index.yaml` (populating version and date; idempotent);
6. Copies `framework/templates/AGENTS-TEMPLATE.md` to `<project>/AGENTS.md` if missing, providing the canonical state-surface table;
7. Runs automated smoke-verification checks over the scaffolded directory structure.

### Manual Setup (Fallback)

Alternatively, copy `framework/governance/aidoc/AIDOC-SCAFFOLD-TEMPLATE.md` to `<project>/.aidoc/README.md` and follow its step-by-step instructions.

The resulting shape:

```text
<project>/
├── AGENTS.md                # working agreement (from AGENTS-TEMPLATE.md)
├── stack-policy.yaml        # tech stack policy (installer-scaffolded at root)
├── Taskfile.yml             # root task orchestration (consumer-authored)
├── docs/sdd/05_ADR/         # Layer 05 ADR index & records
│   └── ADR-00_index.yaml    # technology stack & ADR registry
├── .aidoc/
│   ├── profile.yaml         # project profile — adaptation knobs
│   ├── Taskfile.yml         # workstation SDD task runner
│   ├── contracts/           # integration contracts & schemas
│   ├── ctx-tools/           # context extraction helpers
│   ├── cache/               # deterministic cache artifacts
│   ├── engine/
│   │   └── engine.yaml      # engine configuration
│   ├── framework/           # shared framework (submodule or pinned copy)
│   ├── project/             # project-specific overrides
│   │   ├── governance/      # rule overrides (e.g. CHG_EXECUTION_FLOW.md)
│   │   ├── layers/          # template overrides (e.g. Layer 10 EVAL templates)
│   │   ├── playbooks/       # playbook overrides
│   │   ├── scripts/         # script overrides
│   │   ├── templates/       # template overrides
│   │   └── registry/        # registry overrides
│   └── README.md            # project scaffold guide (from AIDOC-SCAFFOLD-TEMPLATE.md)
```

**Which parts `install.sh` scaffolds vs what you author:** the installer creates `.aidoc/` (`README.md`, `profile.yaml`, `framework/`, `Taskfile.yml`, `engine/engine.yaml`, `cache/`, `bin/sdd-lint`), `docs/sdd/05_ADR/ADR-00_index.yaml`, `docs/sdd/graph/`, root `AGENTS.md`, and root `stack-policy.yaml` (ADR/AGENTS/stack-policy skippable via `--no-adr` / `--no-agents` / `--no-stack-policy`). Everything else above — `project/` overrides, `contracts/`, `ctx-tools/`, root `Taskfile.yml`, root `seed/`, `docs/modules/` — is consumer-authored or arrives with Tier-1 engine adoption. The three `.aidoc/` trees in this repo ([`PROJECT.md`](PROJECT.md) §7.2 minimal, this guide, [`AIDOC_WORKSTATION_STANDARD.md`](AIDOC_WORKSTATION_STANDARD.md) §3 full) describe the same layout at increasing adoption depth — start minimal, extend as needed.

### Proscribed Anti-Patterns

Monolithic files (`DECISIONS.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/HANDOFF.md`) are retired anti-patterns
per framework governance (CHG-40, CHG-80, CHG-94, CHG-95, GD-71, GD-78). All state belongs in structured
SDD layers (`docs/sdd/05_ADR/`), Change Requests (`docs/sdd/09_CHG/archive/`), verified plans (`plans/*-PLAN.md`),
and GitHub milestones/issues.

## 2. Attach the framework

Sanctioned attachment models: Git submodule (recommended for multi-repo environments) or a version-pinned allowlist copy (`install.sh --kind pin`, recommended for standalone checkouts). Raw filesystem symlinks in version control are strictly forbidden per `docs/AIDOC_WORKSTATION_STANDARD.md` §8 (`WORKSTATION_SYM-01`).

A pinned copy carries only the consumer allowlist (`docs/PROJECT.md` §7.1: `framework/`, `docs/`, `hooks/`, `sdd_doc_lint/`, `tests/`, minus `framework/archive/`) — never the whole canon tree — and is refreshed by repeating that copy via `framework/scripts/upgrade.sh`, never by editing inside `.aidoc/framework/`.

Keep these invariants:

- Exactly one framework source per project; never copy framework files
  into `project/` unchanged.
- Record the pinned version in `.aidoc/profile.yaml` and keep it matching
  `framework/VERSION`.
- After an update, re-check every file under `project/` against its new
  upstream counterpart before adopting.

## 3. Declare knobs in `profile.yaml`

Start from `framework/governance/PROFILE-TEMPLATE.yaml`. Every key must
resolve to a knob in `ADAPTATION_SURFACE.yaml` — the surface is closed,
unknown keys are ignored, and no knob may relax a blocking quality gate
(a threshold knob may only go stricter). No profile means framework
defaults; adaptation is purely additive. Precedence:
framework defaults < user-global seed (`~/.aidoc/profile.yaml`,
authoring-time only) < project profile.

## 4. Add overrides that mirror the framework

`project/` MUST mirror the framework's directory structure (`governance/`,
`layers/`, `playbooks/`, `registry/`, `skills/`) so the
discovery rule resolves: when an agent reads a template, rule, or
playbook, it checks `.aidoc/project/{same-path}` first and falls back to
`.aidoc/framework/framework/{same-path}` (or `.aidoc/framework/{same-path}`
if pointing directly at the framework root). Override only what the project
genuinely changes; each override should cite the upstream file and the reason it
diverges.

## 4.1 Concrete Operational Blueprints (#894, #923)

To prevent fragmented or ad-hoc project setups, instantiate the following core governance blueprints under `.aidoc/project/`:

1. **Autonomous Execution Handbook (`.aidoc/project/governance/CHG_EXECUTION_FLOW.md`)**:
   Copy [`framework/governance/aidoc/AIDOC-CHG-EXECUTION-FLOW-TEMPLATE.md`](../framework/governance/aidoc/AIDOC-CHG-EXECUTION-FLOW-TEMPLATE.md). It codifies the deterministic 8-step lifecycle, the 13 core invariants, the Multi-Tier Circuit Breakers (CB-1..CB-6), and deployable vs non-deployable routing tailored to the project's build and test runners.

2. **CI Smart Routing & Anti-Deadlock Protocol (`.aidoc/project/governance/CI_SMART_ROUTING.md`)**:
   Copy [`framework/governance/aidoc/AIDOC-CI-SMART-ROUTING-TEMPLATE.md`](../framework/governance/aidoc/AIDOC-CI-SMART-ROUTING-TEMPLATE.md). Enforces the Anti-Deadlock Invariant (zero top-level trigger filtering on required checks) and establishes internal job/step smart change detection, concentric latency budgets, and fail-closed defaults.

3. **Autonomous PR Conflict Resolution Protocol (`.aidoc/project/governance/CONFLICT_RESOLUTION.md`)**:
   Copy [`framework/governance/aidoc/AIDOC-CONFLICT-RESOLUTION-TEMPLATE.md`](../framework/governance/aidoc/AIDOC-CONFLICT-RESOLUTION-TEMPLATE.md). Standardizes Class 1 (additive/deterministic) vs Class 2 (semantic/architectural) conflict classification, forward merge procedure (`git merge origin/dev`), and mandatory auto-merge re-arming.

4. **Multi-Agent Dual Self-Review Protocol (`.aidoc/project/governance/SELF_REVIEW_LOOP.md`)**:
   Copy [`framework/governance/aidoc/AIDOC-SELF-REVIEW-LOOP-TEMPLATE.md`](../framework/governance/aidoc/AIDOC-SELF-REVIEW-LOOP-TEMPLATE.md). Defines the two-stage review architecture (Stage A Proposal Review vs Stage B Implementation PR Review), strict Judge ≠ Generator independence, and the 4-lens rubric (Correctness, Anti-Mock, Governance, Security).

5. **Quality Assurance & Acceptance Protocol (`.aidoc/project/governance/QA_PROTOCOL.md`)**:
   Copy [`framework/governance/aidoc/AIDOC-QA-PROTOCOL-TEMPLATE.md`](../framework/governance/aidoc/AIDOC-QA-PROTOCOL-TEMPLATE.md). Implements the Tripartite Engineering Architecture (DEV vs SDET vs QA), strict non-code-modifying hard block for QA personas, structured defect reporting, and mandatory post-merge issue closure report contract.

6. **End-to-End Browser Testing & Visual Verification (`.aidoc/project/governance/BROWSER_TESTING.md`)**:
   Copy [`framework/governance/aidoc/AIDOC-BROWSER-TESTING-TEMPLATE.md`](../framework/governance/aidoc/AIDOC-BROWSER-TESTING-TEMPLATE.md). Establishes headless browser automation (Playwright), multi-worktree port and container sandboxing, accessible locator prioritization, and diagnostic artifact collection (traces, videos, screenshots).

7. **Durable Multi-Agent Execution Standard (`.aidoc/project/governance/DURABLE_EXECUTION.md`)**:
   Derived from [`framework/governance/DURABLE_EXECUTION_STANDARD.md`](../framework/governance/DURABLE_EXECUTION_STANDARD.md). Codifies the 3-Tier Execution Architecture:
   - **Tier 1 (Durable Workflow / Control Plane)**: Plain deterministic workflow managing control flow, approval gates, durable waits, and SAGA reverse compensations. Never calls LLMs.
   - **Tier 2 (Cognitive Graphs / Reasoning Plane)**: Cyclical reasoning graphs (review, fix, explore) where nodes propose artifacts to external storage without direct filesystem or git mutations.
   - **Tier 3 (Deterministic Effect & Verification Services)**: Idempotent activities managing git workspaces, compilers, linters, and tests.
   Enforces Thin State ($\le 2$ KB payload), zero LLM in rollback, and the Order Guard Invariant (`git worktree remove` before deleting branches).

8. **Graph-Based Review Flows & Review Report Schema (`.aidoc/project/governance/REVIEW_WORKFLOWS.md`)**:
   Derived from [`framework/governance/REVIEW_WORKFLOW_STANDARD.md`](../framework/governance/REVIEW_WORKFLOW_STANDARD.md) and [`framework/governance/review_report.schema.json`](../framework/governance/review_report.schema.json). Codifies structured multi-persona review flows, workflow linting via `sdd_swf_lint`, deterministic quality gate floors (`structural_pass == true && blocking_findings == 0`), and automated `chg_handover` metadata.

### Operational Automations & Client Integrations

In addition to the eight governance blueprints above, consumer projects instantiate two key operational automations:

- **Automated Evaluation Report Ingestion**:
  For Layer 10 closeouts, projects maintain a deterministic evaluation generator (e.g. `scripts/test/generate_eval_report.py`). It ingests machine-readable test run summaries (e.g. `test-results/summary.json` output by `pytest`, `go-test`, or `playwright`) and BDD tag verifications, outputting the immutable `docs/sdd/10_EVAL/EVAL-{NN}/reports/EVAL-{NN}-RPT-001.yaml` artifact required to advance IPLAN to `Verified` and CHG to `Completed`.

- **Client Hooks Integration (`hooks/hooks.json`)**:
  Projects bind the framework's advisory hooks into their local agent configurations:
  - `PostToolUse` (matcher: `Write|Edit`): invokes `hooks/sdd-doc-review.sh` to provide immediate feedback on structural SDD requirements.
  - `PreCommit` (matcher: `.*`): invokes `hooks/ch-gate-check.sh` and `hooks/pre_push_check.sh` to enforce the zero `--no-verify` invariant locally before commits reach remote CI.
- **Consumer CI gate ([`docs/CONSUMER-CI-STARTER.md`](CONSUMER-CI-STARTER.md))**:
  `.github/` is excluded from the consumer copy, so new projects start with no CI. Adopt the starter workflow (profile-lint + `sdd_doc_lint` + `chg_lint` on PR) so the first PR is already gated.
- **Consumer deployment standard ([`docs/CONSUMER-DEPLOYMENT-STANDARD.md`](CONSUMER-DEPLOYMENT-STANDARD.md))**:
  Docker Compose for dev, OpenTofu Day-0/Day-2 for stage/prod infrastructure. Read before provisioning any hosted tier — stage services stay Compose; tofu owns the infrastructure, never merged modules.

## 4.2 Establish the Project Working Agreement (`AGENTS.md`)

Consuming projects must establish a root `AGENTS.md` so all AI coding agents adhere to the Governance Gate autonomously. The single source is [`framework/templates/AGENTS-TEMPLATE.md`](../framework/templates/AGENTS-TEMPLATE.md) (consumer path: `<project>/.aidoc/framework/framework/templates/AGENTS-TEMPLATE.md`), which `install.sh` copies to `<project>/AGENTS.md` when missing (§1 step 6) — do not maintain a hand-written variant.

### Day-1 minimal scope

Start linter-only: `profile_lint`, `sdd_doc_lint`, and `chg_lint` run on plain Python + `pyyaml` with no engines, no containers, no API keys. Adopt Tier-1 engines (`aidoc-flow-langgraph`, `aidoc-context-tools`) only when you need review crews or context slicing; when you do, start the engine in `verify-only` (CI) or `mock` (pipeline testing) mode and switch to `live` for interactive authoring (modes: [`AIDOC_WORKSTATION_STANDARD.md`](AIDOC_WORKSTATION_STANDARD.md) §6).

## 5. What never goes where

- Project data (profiles, learnings, overrides) never lands under
  `framework/` — the spec ships the contract, never project content
  (enforced by `tests/conformance/test_governance.py`, D-0013).
- Overrides stay declarative (switches, bounds, terms). They never carry
  logic and never rewrite how a skill works.
- Overrides stay engine-agnostic: no stack, tool, path, or port choices
  leak into framework-shaped files.

## 6. Updating the framework

1. Advance the framework source (pull the shared checkout, re-copy the
   allowlist per `docs/PROJECT.md` §7.1, or fetch and fast-forward the
   upstream tag in a pinned clone).
2. Diff the new `framework/VERSION` against the pin in `profile.yaml`;
   bump the pin deliberately, never silently.
3. Re-diff each `project/` override against its upstream counterpart;
   retire overrides the new framework version made redundant.
4. Re-run the project's gates before treating the bump as adopted.

## 7. Green linters do not equal governed (#813)

A green lint run means every *emitted* rule passed — not that every
governance contract holds. `framework/governance/LINT_RULES.md` carries
TDD-SYNC-A–E ×5) — documented contracts with deliberately no emitting
code. Checklist-gate or IPLAN-substance violations in that set pass
silently; the backstop is reviewer judgment (the review crews and lenses),
not a second lint pass. Do not invent emitters or reclassify Reserved
rows to close this gap — the reservation is the contract.

## 8. Recommended Platform Technology Stack

For teams deploying new systems or standardizing runtime execution infrastructure, refer to the authoritative architecture guide:

- [`framework/governance/RECOMMENDED_PLATFORM_STACK.md`](../framework/governance/RECOMMENDED_PLATFORM_STACK.md)
  Authoritative open-source, Docker-native platform stack: Debian 13 (Linux 6.12+), gVisor (`runsc`), Temporal Server, LangGraph Core, PostgreSQL 18, Bytebase, NATS JetStream, ClickHouse, HyperDX, and Langfuse.
- Operational blueprints for this stack are ready to copy into `.aidoc/project/`:
  - Temporal + LangGraph: `framework/governance/aidoc/AIDOC-TEMPORAL-LANGGRAPH-RUNTIME-TEMPLATE.md`
  - PostgreSQL 18 + Bytebase: `framework/governance/aidoc/AIDOC-BYTEBASE-POSTGRES-SCHEMA-TEMPLATE.md`
  - NATS CloudEvents + Protobuf: `framework/governance/aidoc/AIDOC-NATS-CLOUDEVENTS-PROTOBUF-TEMPLATE.md`
  - gVisor Sandbox Profile: `framework/governance/aidoc/AIDOC-GVISOR-SANDBOX-EXECUTION-PROFILE.md`
  - Langfuse + HyperDX: `framework/governance/aidoc/AIDOC-LANGFUSE-HYPERDX-OBSERVABILITY-TEMPLATE.md`
