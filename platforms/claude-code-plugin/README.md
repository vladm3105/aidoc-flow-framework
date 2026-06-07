# aidoc-flow — Claude Code plugin

> **Status: Pre-1.0 preview.** APIs and surfaces may change before 1.0.

The native **Claude Code** delivery of the AI Doc Flow framework: a
Specification-Driven Development (SDD) engine that drives a project from a
Business Requirements Document down to an implementation plan through eight
traceable layers — **BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN**.
Claude itself performs generation, validation, and scoring — there is no MCP
backend and nothing to run separately.

The plugin is **self-contained**: it bundles a copy of the framework spec it
needs, so it installs and runs from a marketplace with no external checkout.

## Install

Published through the repo-root marketplace manifest
(`../../.claude-plugin/marketplace.json`). From Claude Code:

```
/plugin marketplace add vladm3105/aidoc-flow-framework
/plugin install aidoc-flow@aidoc-flow-framework
```

## Quickstart

```
/aidoc-flow:doc-flow                # "which skill do I need?" — start here
/aidoc-flow:project-init            # scaffold the docs/ layer tree for a project
/aidoc-flow:doc-brd-autopilot       # draft the first layer (BRD) end-to-end
/aidoc-flow:doc-brd-audit           # score it against the layer's quality gate
/aidoc-flow:doc-validator           # validate cross-doc references & traceability
```

Work down the layers (`doc-prd`, `doc-ears`, … `doc-iplan`), running each
layer's `-audit` before promoting to the next. A seed prompt that drives
this flow lives at
[`../../examples/url-shortener/seed/initial-requirements.md`](../../examples/url-shortener/seed/initial-requirements.md);
the worked output chain it produces is regenerated for each plugin release
by driving the `doc-{layer}-autopilot` skills from a Claude Code session.
See [`../../examples/url-shortener/README.md`](../../examples/url-shortener/README.md)
for the walkthrough.

`doc-flow` is the orchestrator: describe your goal and it routes you to the
right skill. The deeper authoring guidance is in
[`docs/`](docs/).

## What's inside

| Component | Count | Source |
|-----------|------:|--------|
| Skills (layer families) | 32 | The 8 SDD layers — `doc-brd`, `doc-prd`, `doc-ears`, `doc-bdd`, `doc-adr`, `doc-spec`, `doc-tdd`, `doc-iplan` — each in 4 variants: base, `-autopilot`, `-audit`, `-fixer`. |
| Skills (change-management) | 4 | The CHG governance overlay — `doc-chg` + `-autopilot` + `-audit` + `-fixer` (governs edits to existing artifacts; not a layer). |
| Skills (utilities) | 14 | `doc-flow`, `doc-naming`, `doc-ref`, `doc-validator`, `review-team`, `project-init`, `project-adopt`, `project-profile`, `knowledge-extractor`, `gate-check`, `charts-flow`, `adr-roadmap`, `quality-advisor`, `security-audit`. |
| Agents | 11 | AI Team specialist roster — `requirements-analyst`, `pm-orchestrator`, `solutions-architect`, `test-architect`, `software-engineer`, `devops-release-engineer`, `code-reviewer`, `security-engineer`, `traceability-auditor`, plus the two review-team lenses `chaos-engineer` and `synthesizer`. See `docs/AGENTS.md`. |
| Commands | 1 | `/aidoc-flow:save-plan` — capture the current conversation plan to a timestamped file. |
| Hooks | 1 | `hooks/sdd-doc-review.sh` — a `PostToolUse` advisory nudge (see below). |
| **Total skills** | **52** (50 active + 2 deprecated stubs scheduled for removal in v0.7.0) | |

The plugin auto-registers everything via Claude Code's directory
conventions (`skills/`, `agents/`, `commands/`); no per-skill enumeration in
the manifest.

## Self-contained framework bundle

Claude Code copies only the plugin directory to its cache on install, so the
plugin **vendors** the framework spec it consumes at `framework/`
(`layers/`, `governance/`, `registry/`, plus the SDD guide). Skills and agents
reference it via `${CLAUDE_PLUGIN_ROOT}/framework/…`, the install-time anchor.

The bundle is a **byte-identical, generated** copy of the canonical
`../../framework/` — the monorepo spec stays the single source of truth
(decision **D-0022**). Re-sync after a spec change with
`tools/sync-plugin-framework.sh`; a conformance drift-guard
(`tests/conformance/platforms/test_plugin_framework_bundle.py`) fails CI if the
bundle and canonical spec diverge. Never hand-edit the bundle.

### Review trigger (`on_author`)

`hooks/hooks.json` registers a `PostToolUse` hook on `Write`/`Edit`. When an SDD
instance document (`docs/<NN>_<X>/…` or a `<TYPE>-NN` file) is written, it nudges
you to run the matching `doc-<layer>-audit` and appends deterministic structural
findings from the **vendored `sdd_doc_lint/`** (shipped at the plugin root; the
hook puts it on `PYTHONPATH`, so it runs without any consumer setup — it finds the
bundled `framework/registry/` by upward search, and silently skips if none is
present). It is **advisory** — it never blocks the edit. This is the plugin's
binding of the framework's `on_author` trigger point
(`framework/governance/REVIEW_REMEDIATION_FLOW.md`); the blocking `pre_merge`
gate is the shared `doc-review.yml` workflow running the same linter.

The vendored `sdd_doc_lint/` is a byte-identical copy of the canonical
`tools/sdd_doc_lint/` (kept in sync by `tools/sdd_doc_lint/sync-vendored.sh`, a
conformance guard enforces the match).

## Framework spec conformance

The two version declarations:

```
$ cat VERSION
0.6.2

$ cat FRAMEWORK_SPEC_VERSION
0.13.0
```

The plugin declares conformance to framework spec `0.13.0`; the bundled spec's
own version is at `framework/VERSION` (byte-identical to `../../framework/VERSION`).
A conformance test enforces that `FRAMEWORK_SPEC_VERSION` matches the framework's
published version.

## Platform info

| Field | Value |
|-------|-------|
| Engine | Native Claude Code (skills / agents / commands) |
| Version | `0.6.2` (independent SemVer; tag namespace `claude-code-plugin/v*`) |
| Conforms to | framework spec `0.13.0` (declared in `FRAMEWORK_SPEC_VERSION`) |
| License | MIT |
| Repository | <https://github.com/vladm3105/aidoc-flow-framework> |
| Project changelog | [../../CHANGELOG.md](../../CHANGELOG.md) |
| Project roadmap | [../../ROADMAP.md](../../ROADMAP.md) |
| Tagging policy | [../../docs/TAGGING.md](../../docs/TAGGING.md) |

## Review crews & lens → agent mapping

The framework spec defines a closed set of **review lenses** (e.g.
`architect`, `business_analyst`, `auditor`, `chaos_engineer`,
`security_engineer`). Each lens is a
viewpoint a reviewer applies to an artifact. The plugin binds these
engine-agnostic lenses to its own Claude Code agents in `agents/` via the
table below.

In `team` mode (default at gates), the layer's audit skill (`doc-<layer>-audit`)
reads the per-layer crew from `framework/governance/REVIEW_CREWS.yaml`,
maps each lens to its agent via this table, then dispatches one `Task`
subagent per lens in parallel. Each subagent writes its persona-output
record (`persona`, `findings[]`, `lens_score`) to a slot on the
blackboard at `.aidoc/review/<NN>_<LAYER>/<artifact-id>/<lens>.json`;
the `synthesizer` agent then reduces the slots deterministically per
`framework/governance/REVIEW_TEAM.md`.

### Lens → agent mapping

| Framework lens | Plugin agent (`subagent_type=`) | Agent file |
|---|---|---|
| `business_analyst`, `requirements_specialist`, `product_owner` | `requirements-analyst` | [`agents/requirements-analyst.md`](agents/requirements-analyst.md) |
| `architect`, `tech_lead`, `integration_lead` | `solutions-architect` | [`agents/solutions-architect.md`](agents/solutions-architect.md) |
| `qa_lead` | `test-architect` | [`agents/test-architect.md`](agents/test-architect.md) |
| `operator` | `devops-release-engineer` | [`agents/devops-release-engineer.md`](agents/devops-release-engineer.md) |
| `auditor` | `traceability-auditor` | [`agents/traceability-auditor.md`](agents/traceability-auditor.md) |
| `chaos_engineer` (internal stability) | `chaos-engineer` | [`agents/chaos-engineer.md`](agents/chaos-engineer.md) |
| `security_engineer` (external threats) | `security-engineer` | [`agents/security-engineer.md`](agents/security-engineer.md) |
| `synthesizer` (deterministic reduce + narrative) | `synthesizer` | [`agents/synthesizer.md`](agents/synthesizer.md) |
| `drafter` (Create operation; per-layer) | the layer's author agent — for BRD/PRD/EARS that is `requirements-analyst`; for ADR/SPEC, `solutions-architect`; etc. | (see Create assignments below) |
| `fixer` (Remediate operation) | `software-engineer` and/or the layer's `doc-<layer>-fixer` skill | [`agents/software-engineer.md`](agents/software-engineer.md) |

Some lenses share an agent because the agent carries multiple
review-lens briefs and switches role based on which lens the dispatcher
asks it to apply. The conformance test
`tests/conformance/test_review_team.py` enforces that every lens in
`REVIEW_CREWS.yaml` has a binding here.

### Per-layer review crews (weights from `REVIEW_CREWS.yaml`)

Weights sum to 100 per crew; the readiness score is the weighted
average of `lens_score`s, capped per `REVIEW_TEAM.md` §"Scoring,
conflicts & the gate".

| Layer | Author lens | Review crew (lens → weight) |
|---|---|---|
| BRD | `business_analyst` | `architect: 30`, `business_analyst: 30`, `auditor: 20`, `chaos_engineer: 12`, `security_engineer: 8` |
| PRD | `product_owner` | `product_owner: 30`, `architect: 25`, `tech_lead: 20`, `chaos_engineer: 8`, `security_engineer: 7`, `auditor: 10` |
| EARS | `requirements_specialist` | `requirements_specialist: 35`, `tech_lead: 25`, `qa_lead: 20`, `chaos_engineer: 12`, `security_engineer: 8` |
| BDD | `qa_lead` | `qa_lead: 35`, `tech_lead: 25`, `chaos_engineer: 14`, `security_engineer: 6`, `operator: 10`, `auditor: 10` |
| ADR | `architect` | `architect: 35`, `tech_lead: 25`, `chaos_engineer: 8`, `security_engineer: 12`, `operator: 10`, `auditor: 10` |
| SPEC | `architect` | `architect: 30`, `tech_lead: 30`, `integration_lead: 20`, `chaos_engineer: 10`, `security_engineer: 10` |
| TDD | `qa_lead` | `qa_lead: 35`, `tech_lead: 25`, `chaos_engineer: 10`, `security_engineer: 10`, `operator: 10`, `auditor: 10` |
| IPLAN | `tech_lead` | `tech_lead: 30`, `architect: 25`, `operator: 15`, `integration_lead: 12`, `auditor: 10`, `chaos_engineer: 8` |

### Project overrides via `.aidoc/profile.yaml`

A consuming project can override review behaviour by editing its own
`.aidoc/profile.yaml`:

- `review_mode: team | single_pass` — `team` fans out per-lens `Task`
  subagents; `single_pass` runs one model context applying every lens.
  Defaults to `team` at gates.
- `audit_threshold: <int>` — raise the gate score floor (raise-only —
  cannot lower below the framework default of 90).
- `section_toggles: {<section>: <bool>}` — toggle optional template
  sections (e.g. BRD §2 Executive Summary).
- `active_layers: [<layer>, …]` — restrict the cascade to a subset of
  the 8 layers.

The acceptance suite (`tests/scripts/test-acceptance.sh`) bootstraps an
empty project's `.aidoc/profile.yaml` from `REVIEW_CREWS.yaml` as the
default. The closed adaptation surface is defined in
`framework/governance/ADAPTATION_SURFACE.yaml`.

### Single source of truth

- Engine-agnostic: `framework/governance/REVIEW_CREWS.yaml` (crews +
  weights), `framework/governance/REVIEW_TEAM.md` (model contract).
- Plugin binding: `skills/review-team/SKILL.md` (lens → agent table —
  this README mirrors it for discoverability; the SKILL is authoritative).
- Per-layer wiring: each `doc-<layer>-audit` / `-fixer` /
  `-autopilot` SKILL has a `## Review Mode` / `## Remediate Mode`
  branch that dispatches the crew. Currently wired for BRD only
  (BRD-RT-001); PRD-RT, EARS-RT, BDD-RT, ADR-RT, SPEC-RT, TDD-RT,
  IPLAN-RT will follow.

## Relationship to the Hermes platform

`platforms/hermes/` is the **other** independent delivery of the same
framework spec — an MCP-server implementation. The two platforms share the
`framework/` specification and **nothing else** (different engines, no
runtime code overlap). Pick the plugin if you want Claude Code to be the
engine; pick Hermes if you want an MCP server.

Both platforms pass the same shared conformance suite at
`../../tests/conformance/`.

## Contributing

Hooks and workflow live in the framework repo. From the repo root:

```bash
pip install pre-commit && pre-commit install
```

Open issues and pull requests at <https://github.com/vladm3105/aidoc-flow-framework/issues>.

## Reporting bugs and security issues

- Functional bugs: file an issue at <https://github.com/vladm3105/aidoc-flow-framework/issues>.
- Security vulnerabilities: see [`../../SECURITY.md`](../../SECURITY.md) for the disclosure protocol.
