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

### Notes
- Forked from `ucx_framework` v0.20.4 (`main`).
- The gated CHG change-management process is intentionally not applied during
  the migration; it is re-introduced post-cutover (see `docs/PROJECT.md`).

[Unreleased]: https://github.com/vladm3105/aidoc-flow-framework/tree/claude/multi-platform-migration-AamWB
