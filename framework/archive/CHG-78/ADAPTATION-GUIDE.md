# Adapting the Framework to a New Project

## Document Control

| Field | Value |
|---|---|
| Version | 1.3 |
| Status | Approved |
| Last Updated | 2026-10-07 |
| Author | Framework Maintainer |
| Framework Version | 0.90.1 |

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
framework/scripts/install.sh <project-dir> --canon framework/v0.90.1 --kind pin

# Or symlink to a persistent shared framework checkout:
framework/scripts/install.sh <project-dir> --canon framework/v0.90.1 --kind symlink --shared /path/to/framework
```

`install.sh` automates the ordered 5-step procedure from `BOOTSTRAP.md`:

1. Copies `AIDOC-SCAFFOLD-TEMPLATE.md` to `<project>/.aidoc/README.md` and populates author, date, and version placeholders;
2. Copies `PROFILE-TEMPLATE.yaml` to `<project>/.aidoc/profile.yaml`;
3. Attaches the framework: either copies the version-pinned allowlist (`docs/PROJECT.md` §7.1 / `allowlist.txt`, pruning internal archives) or establishes the canonical `.aidoc/framework` symlink;
4. Pins `metadata.framework_version` to the adopted canon version;
5. Runs automated smoke-verification checks over the scaffolded `.aidoc/` directory structure.

### Manual Setup (Fallback)

Alternatively, copy `framework/governance/aidoc/AIDOC-SCAFFOLD-TEMPLATE.md` to `<project>/.aidoc/README.md` and follow its step-by-step instructions.

The resulting shape:

```text
.aidoc/
├── profile.yaml             # project profile — adaptation knobs
├── framework/               # shared framework (symlink or pinned copy, canonical)
├── project/                 # project-specific overrides
│   ├── governance/          # rule overrides (e.g. CHG_EXECUTION_FLOW.md)
│   ├── layers/              # template overrides (e.g. Layer 10 EVAL templates)
│   ├── playbooks/           # playbook overrides
│   ├── scripts/             # script overrides
│   ├── templates/           # template overrides
│   └── registry/            # registry overrides
└── README.md                # project scaffold guide (from AIDOC-SCAFFOLD-TEMPLATE.md)
```

## 2. Attach the framework

Canonical form: `.aidoc/framework/` is a symlink to the shared framework
checkout (`AIDOC.md` § "Symlink convention"). One project in the wild
instead keeps a version-pinned copy. A pinned copy carries only the consumer
allowlist (`docs/PROJECT.md` §7.1: `framework/`, `docs/`, `hooks/`,
`sdd_doc_lint/`, `tests/`, minus `framework/archive/`) — never the whole
canon tree — and is refreshed by repeating that copy, never by pulling
inside `.aidoc/framework/`. Either form works if
you keep these invariants:

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

7. **Automated Evaluation Report Ingestion**:
   For Layer 10 closeouts, projects maintain a deterministic evaluation generator (e.g. `scripts/test/generate_eval_report.py`). It ingests machine-readable test run summaries (e.g. `test-results/summary.json` output by `pytest`, `go-test`, or `playwright`) and BDD tag verifications, outputting the immutable `docs/sdd/10_EVAL/EVAL-{NN}/reports/EVAL-{NN}-RPT-001.yaml` artifact required to advance IPLAN to `Verified` and CHG to `Completed`.

8. **Client Hooks Integration (`hooks/hooks.json`)**:
   Projects bind the framework's advisory hooks into their local agent configurations:
   - `PostToolUse` (matcher: `Write|Edit`): invokes `hooks/sdd-doc-review.sh` to provide immediate feedback on structural SDD requirements.
   - `PreCommit` (matcher: `.*`): invokes `hooks/ch-gate-check.sh` and `hooks/pre_push_check.sh` to enforce the zero `--no-verify` invariant locally before commits reach remote CI.

9. **Durable Multi-Agent Execution Standard (`.aidoc/project/governance/DURABLE_EXECUTION.md`)**:
   Derived from [`framework/governance/DURABLE_EXECUTION_STANDARD.md`](../framework/governance/DURABLE_EXECUTION_STANDARD.md). Codifies the 3-Tier Execution Architecture:
   - **Tier 1 (Durable Workflow / Control Plane)**: Plain deterministic workflow managing control flow, approval gates, durable waits, and SAGA reverse compensations. Never calls LLMs.
   - **Tier 2 (Cognitive Graphs / Reasoning Plane)**: Cyclical reasoning graphs (review, fix, explore) where nodes propose artifacts to external storage without direct filesystem or git mutations.
   - **Tier 3 (Deterministic Effect & Verification Services)**: Idempotent activities managing git workspaces, compilers, linters, and tests.
   Enforces Thin State ($\le 2$ KB payload), zero LLM in rollback, and the Order Guard Invariant (`git worktree remove` before deleting branches).

10. **Graph-Based Review Flows & Review Report Schema (`.aidoc/project/governance/REVIEW_WORKFLOWS.md`)**:
    Derived from [`framework/governance/REVIEW_WORKFLOW_STANDARD.md`](../framework/governance/REVIEW_WORKFLOW_STANDARD.md) and [`framework/governance/review_report.schema.json`](../framework/governance/review_report.schema.json). Codifies structured multi-persona review flows, workflow linting via `sdd_swf_lint`, deterministic quality gate floors (`structural_pass == true && blocking_findings == 0`), and automated `chg_handover` metadata.

## 4.2 Establish the Project Working Agreement (`AGENTS.md`)

Consuming projects must establish a root `AGENTS.md` working agreement so all AI coding agents adhere to the Governance Gate autonomously. Starter template:

```markdown
# AGENTS.md — Working Agreement for AI Coding Agents

## Governance Gate (Non-Negotiable)

Before writing ANY code for a feature, enhancement, or bug fix:
1. Stop: Check if an authorizing Change Request (CHG) exists under `.aidoc/` or `chg/`. If not, create a CHG document first.
2. Complete the §3.4 CHG creation checklist before writing code.
3. Validate CHG via `python3 .aidoc/framework/sdd_doc_lint/chg_lint.py <chg-file.yaml>`.
4. Work in a dedicated per-task git worktree: `git worktree add ../<project>-<slug> -b feature/<branch-slug> origin/dev`. Never work directly on `main` or `dev`.
5. Run automated verification suites and linters locally before pushing. Never bypass hooks (`--no-verify` is forbidden).
```

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
Reserved rows (18: EVAL ×6, GOV-008/009/010/013/015 ×5, IPLAN01, REG01,
TDD-SYNC-A–E ×5) — documented contracts with deliberately no emitting
code. Checklist-gate or IPLAN-substance violations in that set pass
silently; the backstop is reviewer judgment (the review crews and lenses),
not a second lint pass. Do not invent emitters or reclassify Reserved
rows to close this gap — the reservation is the contract.
