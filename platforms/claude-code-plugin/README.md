# aidoc-flow — Claude Code plugin

The native **Claude Code** delivery of the AI Doc Flow framework. Ships a
124-skill SDD (Specification-Driven Development) engine plus 9 agents and 1
command. Claude itself performs validation, generation, and scoring — there's
no MCP backend.

## What's inside

| Component | Count | Source |
|-----------|------:|--------|
| Skills (`doc-*`) | 112 | SDD layer engine — `doc-brd`, `doc-prd`, `doc-ears`, `doc-bdd`, `doc-adr`, `doc-spec`, `doc-tdd`, `doc-iplan` and their `-audit` / `-autopilot` / `-fixer` / `-reviewer` / `-validator` variants, plus subtype skills (CSPEC/DSPEC/UXSPEC/RISKSPEC/PROCSPEC, UTEST/ITEST/STEST/FTEST/PTEST/SECTEST) and orchestrators (`doc-flow`, `doc-naming`, `doc-validator`, `doc-review`, `doc-ref`). |
| Skills (non-doc, SDD-adjacent) | 12 | `adr-roadmap`, `charts-flow`, `context-analyzer`, `contract-tester`, `mermaid-gen`, `project-init`, `quality-advisor`, `security-audit`, `skill-recommender`, `test-automation`, `trace-check`, `workflow-optimizer`. |
| Agents | 9 | AI Team specialist roster — `requirements-analyst`, `pm-orchestrator`, `solutions-architect`, `test-architect`, `software-engineer`, `devops-release-engineer`, `code-reviewer`, `security-engineer`, `traceability-auditor` (SDD lifecycle: spec lane → execution lane → read-only quality gates). See `agents/README.md`. |
| Commands | 1 | `/aidoc-flow:save-plan` — capture current conversation plan to a timestamped file. |
| **Total skills** | **124** | |

The plugin auto-registers everything via Claude Code's directory
conventions (`skills/`, `agents/`, `commands/`); no per-skill enumeration in
the manifest.

## Install

This plugin lives in the multi-platform `aidoc-flow-framework` repository.
See `../../README.md` for the project-level overview and Claude Code's
plugin manager documentation for installation steps.

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
0.1.0

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
| Version | `0.1.0` (independent SemVer; tag namespace `claude-code-plugin/v*`) |
| Conforms to | framework spec `0.1.0` (declared in `FRAMEWORK_SPEC_VERSION`) |
| License | MIT |
| Repository | https://github.com/vladm3105/aidoc-flow-framework |
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
