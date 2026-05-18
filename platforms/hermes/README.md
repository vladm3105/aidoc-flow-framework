# Platform A — Hermes AI

> Status: PLACEHOLDER. Populated in Phase 2 (see `../../ROADMAP.md`).

Hermes AI is the **MCP-server** delivery of the document-flow framework. It is
one of two independent platforms; it shares the `framework/` specification with
the Claude Code plugin but no runtime code.

Phase 2 moves the existing `ucx_hermes/` and `mcp_ucx/` trees here, points them
at `../../framework/`, and validates Hermes against the shared conformance suite
(`../../tests/conformance/`).

| Field | Value |
|-------|-------|
| Engine | MCP server |
| Version | `VERSION` (independent SemVer) |
| Conforms to | `framework_spec_version` — declared once re-homed |
| Changelog | `CHANGELOG.md` (created in Phase 2) |
