# aidoc-flow — Claude Code plugin

The native **Claude Code** delivery of the AI Doc Flow framework. Ships a
52-skill SDD (Specification-Driven Development) engine plus 9 agents and 1
command. Claude itself performs validation, generation, and scoring — there's
no MCP backend.

## What's inside

| Component | Count | Source |
|-----------|------:|--------|
| Skills (layer families) | 32 | The 8 SDD layers — `doc-brd`, `doc-prd`, `doc-ears`, `doc-bdd`, `doc-adr`, `doc-spec`, `doc-tdd`, `doc-iplan` — each in 4 variants: base, `-autopilot`, `-audit`, `-fixer`. |
| Skills (change-management) | 4 | The CHG governance overlay — `doc-chg` + `-autopilot` + `-audit` + `-fixer` (governs edits to existing artifacts; not a layer). |
| Skills (utilities) | 18 | `doc-flow`, `doc-naming`, `doc-ref`, `doc-review`, `doc-validator`, `project-init`, `project-adopt`, `project-profile`, `knowledge-extractor`, `gate-check`, `trace-check`, `charts-flow`, `adr-roadmap`, `context-analyzer`, `quality-advisor`, `skill-recommender`, `workflow-optimizer`, `security-audit`. |
| Agents | 9 | AI Team specialist roster — `requirements-analyst`, `pm-orchestrator`, `solutions-architect`, `test-architect`, `software-engineer`, `devops-release-engineer`, `code-reviewer`, `security-engineer`, `traceability-auditor` (SDD lifecycle: spec lane → execution lane → read-only quality gates). See `agents/README.md`. |
| Commands | 1 | `/aidoc-flow:save-plan` — capture current conversation plan to a timestamped file. |
| Hooks | 1 | `hooks/sdd-doc-review.sh` — a `PostToolUse` advisory nudge (see below). |
| **Total skills** | **54** | |

The plugin auto-registers everything via Claude Code's directory
conventions (`skills/`, `agents/`, `commands/`); no per-skill enumeration in
the manifest.

### Review trigger (`on_author`)

`hooks/hooks.json` registers a `PostToolUse` hook on `Write`/`Edit`. When an SDD
instance document (`docs/<NN>_<X>/…` or a `<TYPE>-NN` file) is written, it nudges
you to run the matching `doc-<layer>-audit` and appends deterministic structural
findings from the **vendored `sdd_doc_lint/`** (shipped at the plugin root; the
hook puts it on `PYTHONPATH`, so it runs without any consumer setup — it finds the
project's `framework/registry/` by upward search, and silently skips if none is
present). It is **advisory** — it never blocks the edit. This is the plugin's
binding of the framework's `on_author` trigger point
(`framework/governance/REVIEW_REMEDIATION_FLOW.md`); the blocking `pre_merge`
gate is the shared `doc-review.yml` workflow running the same linter.

The vendored `sdd_doc_lint/` is a byte-identical copy of the canonical
`tools/sdd_doc_lint/` (kept in sync by `tools/sdd_doc_lint/sync-vendored.sh`, a
conformance guard enforces the match).

## Install

This plugin lives in the multi-platform `aidoc-flow-framework` repository,
published through the repo-root marketplace manifest
(`../../.claude-plugin/marketplace.json`). From Claude Code:

```
/plugin marketplace add vladm3105/aidoc-flow-framework
/plugin install aidoc-flow@aidoc-flow-framework
```

See `../../README.md` for the project-level overview.

## Use

Invoke any skill with the plugin's slash-prefix:

```
/aidoc-flow:doc-brd-autopilot       # generate a BRD via the full pipeline
/aidoc-flow:doc-flow                # workflow orchestrator (skill selection)
/aidoc-flow:doc-spec-audit          # unified SPEC quality gate
/aidoc-flow:trace-check             # validate traceability across artifacts
```

`doc-flow` is the entry point for "which skill do I need?" — start there if
you're new to the SDD workflow.

## Framework spec conformance

The plugin consumes the engine-agnostic SDD specification at `../../framework/`
(layer templates, registry, governance). The two version declarations:

```
$ cat VERSION
0.2.0

$ cat FRAMEWORK_SPEC_VERSION
0.1.0
```

The plugin declares conformance to framework spec `0.1.0`; the framework's
own version is at `../../framework/VERSION`. Phase 4 of the project's roadmap
introduces an explicit conformance test that enforces this declaration
matches the framework's published version.

## Platform info

| Field | Value |
|-------|-------|
| Engine | Native Claude Code (skills / agents / commands) |
| Version | `0.2.0` (independent SemVer; tag namespace `claude-code-plugin/v*`) |
| Conforms to | framework spec `0.1.0` (declared in `FRAMEWORK_SPEC_VERSION`) |
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
