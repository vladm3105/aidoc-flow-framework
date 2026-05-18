# framework/ — Shared Engine-Agnostic Specification

> Status: PLACEHOLDER. Populated in Phase 1 (see `../ROADMAP.md`).

This directory will hold the **engine-agnostic specification** of the document-
flow framework — the single contract that both platforms implement:

- `layers/` — the 8-layer SDD definitions (BRD→PRD→EARS→BDD→ADR→SPEC→TDD→IPLAN),
  with templates and schemas.
- `governance/` — governance rules, the CHG change-management overlay, and gate
  definitions.
- `registry/LAYER_REGISTRY.yaml` — the layer registry.
- `VERSION` — the framework spec SemVer.

It contains **no runtime code**. Hermes AI (`../platforms/hermes/`) and the
Claude Code plugin (`../platforms/claude-code-plugin/`) are independent engines
that each implement this spec and declare the `framework_spec_version` they
conform to.

Content is consolidated here from legacy `ucx_flow_v3/` and `governance/` during
Phase 1 — see `../docs/REPO_STRUCTURE.md` for the legacy → target mapping.
