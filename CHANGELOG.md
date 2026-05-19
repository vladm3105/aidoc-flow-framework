# Changelog

All notable changes to the AI Doc Flow Framework (multi-platform project) are
documented here. Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> Scope: this is the **project-level** changelog tracking the multi-platform
> migration. Once scaffolded, each platform keeps its own changelog at
> `platforms/<name>/CHANGELOG.md`, and `framework/` versions independently.

## [Unreleased]

### Added
- Planning baseline for the multi-platform restructure:
  - `ROADMAP.md` — phased delivery plan (Phase 0 → cutover v1.0.0).
  - `docs/REPO_STRUCTURE.md` — target repository layout and legacy mapping.
  - `docs/PROJECT.md` — versioning, branching, milestones, conformance, and
    interim change-management policy.
  - `platforms/hermes/` and `platforms/claude-code-plugin/` directories.
  - `framework/` directory placeholder for the shared engine-agnostic spec.

- CHG implementation decision recorded as tracked TODO (ROADMAP CHG-D1/D2,
  `docs/PROJECT.md` § CHG implementation model): CHG to be built as
  skills + CI/CD post-Phase 5.

- `CLAUDE.md` — auto-loaded project memory: development workflow
  (plan → review → harden → implement → verify → land), definition of done,
  and session-handoff practice.
- `plans/` workspace — `README.md`, `MIGRATION_TODO.md` (live task tracker),
  `HANDOFF.md` (session continuity), `DECISIONS.md` (decision log).
- `.claude/` automation hooks: `PreCompact` (auto-commit + push a WIP
  snapshot before compaction) and `SessionStart` (inject `plans/HANDOFF.md`
  into context), with scripts under `.claude/hooks/`.
- `plans/P1-AUDIT-ucx_flow_v3.md` — Phase 1 audit (P1-T1) classifying the
  49-file legacy SDD v3.2 tree as engine-agnostic, mixed, instance, or drop,
  with the target `framework/` layout for the Phase 1 extraction steps.
- Plan-review gate (D-0007): plans require a `## Review log` of ≥2 passes;
  `plans/PLAN-TEMPLATE.md` added; non-blocking `PreToolUse(git commit)` hook
  warns when a staged plan file falls short.
- `framework/layers/` (P1-T2) — the 8 engine-agnostic SDD layer specs
  extracted from `legacy/ucx_flow_v3/`: per layer a `*-TEMPLATE.yaml`, a
  `README.md`, and a `*-00_index.TEMPLATE.*` index template (24 files). All
  Hermes/MCP- and Claude-Code-specific content removed; legacy `SDD v3.2`
  version strings neutralized.
- `framework/registry/` (P1-T3) — `LAYER_REGISTRY.yaml`, the authoritative
  machine-readable layer model (layer order, traceability graph, C4 mapping,
  ID patterns), plus a `README.md`. Standalone version field and legacy
  changelog dropped; layer `folder` paths repointed under `layers/`.
- `framework/governance/` (P1-T4) — 5 governance docs (`DOC_GOVERNANCE_CORE`,
  `ID_NAMING_STANDARDS`, `TRACEABILITY`, `DIAGRAM_STANDARDS`,
  `THRESHOLD_NAMING_RULES`) and the CHG overlay (`chg/` — README, template,
  index template, 7 gates, 2 companion templates), 18 files. Engine-specific
  skill references and `MCP` mentions neutralized; CHG extracted spec-only
  (not enforced until post-Phase 5).
- `tests/conformance/` (P1-T5) — the shared conformance suite: 22 stdlib
  `unittest` tests covering registry self-consistency, layer templates,
  governance files, and spec hygiene (no engine tokens in `framework/`), plus
  the documented platform-conformance contract for Phase 4. No `pytest`
  dependency (D-0008).
- `framework/README.md` — the engine-agnostic spec overview (8-layer flow, C4
  alignment, layout, conformance, versioning), replacing the scaffolding
  placeholder.
- `framework/VERSION` (P1-T6) — the framework spec's independent version
  stream, at `0.1.0`. `tests/conformance/test_version.py` covers it.
- `docs/PROJECT.md` §3 — tag-namespace convention: project milestones
  `vX.Y.Z`, framework spec `framework/vX.Y.Z`, platforms `<platform>/vX.Y.Z`
  (D-0009).
- `framework/` root methodology docs (P1-T7) — `SPEC_DRIVEN_DEVELOPMENT_GUIDE`,
  `QUICK_REFERENCE`, `AI_ASSISTANT_RULES`, `TESTING_STRATEGY_TDD`, extracted
  engine-neutral (version strings neutralized, links repointed, legacy
  version-lineage content dropped per D-0010). `framework/` is now fully
  assembled. `tests/conformance/test_root.py` covers the root file set.

### Changed
- **Legacy isolation:** all pre-migration content moved into `legacy/`
  (frozen) — `ucx_flow_v3`, `ucx_hermes`, `mcp_ucx`, `ai_dev_ssd_flow_v2`,
  `governance`, and supporting trees. Repo root now holds only the new
  project (`framework/`, `platforms/`, `docs/`) plus infrastructure.
- Legacy GitHub Actions workflows disabled (parked in
  `legacy/github-workflows-disabled/`).
- Root `README.md` rewritten for the multi-platform project.
- `.mcp.json` Hermes server path repointed to `legacy/ucx_hermes/`.

### Notes
- Forked from `ucx_framework` v0.20.4 (`main`).
- The gated CHG change-management process is intentionally not applied during
  the migration; it is re-introduced post-cutover (see `docs/PROJECT.md`).

[Unreleased]: https://github.com/vladm3105/aidoc-flow-framework/tree/claude/multi-platform-migration-AamWB
