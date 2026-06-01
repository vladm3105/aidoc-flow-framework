# aidoc-flow — Claude Code plugin

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
layer's `-audit` before promoting to the next. A complete, gate-clean example
chain — initial requirements through to an IPLAN — lives in
[`../../examples/url-shortener/`](../../examples/url-shortener/).

`doc-flow` is the orchestrator: describe your goal and it routes you to the
right skill. The deeper authoring guidance is in
[`docs/`](docs/).

## What's inside

| Component | Count | Source |
|-----------|------:|--------|
| Skills (layer families) | 32 | The 8 SDD layers — `doc-brd`, `doc-prd`, `doc-ears`, `doc-bdd`, `doc-adr`, `doc-spec`, `doc-tdd`, `doc-iplan` — each in 4 variants: base, `-autopilot`, `-audit`, `-fixer`. |
| Skills (change-management) | 4 | The CHG governance overlay — `doc-chg` + `-autopilot` + `-audit` + `-fixer` (governs edits to existing artifacts; not a layer). |
| Skills (utilities) | 14 | `doc-flow`, `doc-naming`, `doc-ref`, `doc-validator`, `review-team`, `project-init`, `project-adopt`, `project-profile`, `knowledge-extractor`, `gate-check`, `charts-flow`, `adr-roadmap`, `quality-advisor`, `security-audit`. |
| Agents | 11 | AI Team specialist roster — `requirements-analyst`, `pm-orchestrator`, `solutions-architect`, `test-architect`, `software-engineer`, `devops-release-engineer`, `code-reviewer`, `security-engineer`, `traceability-auditor`, plus the two review-team lenses `adversary` and `synthesizer`. See `docs/AGENTS.md`. |
| Commands | 1 | `/aidoc-flow:save-plan` — capture the current conversation plan to a timestamped file. |
| Hooks | 1 | `hooks/sdd-doc-review.sh` — a `PostToolUse` advisory nudge (see below). |
| **Total skills** | **50** | |

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
0.4.0

$ cat FRAMEWORK_SPEC_VERSION
0.10.0
```

The plugin declares conformance to framework spec `0.10.0`; the bundled spec's
own version is at `framework/VERSION` (byte-identical to `../../framework/VERSION`).
A conformance test enforces that `FRAMEWORK_SPEC_VERSION` matches the framework's
published version.

## Platform info

| Field | Value |
|-------|-------|
| Engine | Native Claude Code (skills / agents / commands) |
| Version | `0.4.0` (independent SemVer; tag namespace `claude-code-plugin/v*`) |
| Conforms to | framework spec `0.10.0` (declared in `FRAMEWORK_SPEC_VERSION`) |
| License | MIT |
| Repository | <https://github.com/vladm3105/aidoc-flow-framework> |
| Project changelog | [../../CHANGELOG.md](../../CHANGELOG.md) |
| Project roadmap | [../../ROADMAP.md](../../ROADMAP.md) |
| Tagging policy | [../../docs/TAGGING.md](../../docs/TAGGING.md) |

## Relationship to the Hermes platform

`platforms/hermes/` is the **other** independent delivery of the same
framework spec — an MCP-server implementation. The two platforms share the
`framework/` specification and **nothing else** (different engines, no
runtime code overlap). Pick the plugin if you want Claude Code to be the
engine; pick Hermes if you want an MCP server.

Both platforms pass the same shared conformance suite at
`../../tests/conformance/`.
