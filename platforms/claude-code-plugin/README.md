# Platform B — Claude Code Plugin

> Status: PLACEHOLDER. Populated in Phase 3 (see `../../ROADMAP.md`).

The Claude Code plugin is the **native Claude Code** delivery of the document-
flow framework. It has **no MCP backend** — Claude itself performs the
validation, generation, and scoring that Hermes performs as a server.

Phase 3 scaffolds the plugin and ports the framework engine into it:

```
.claude-plugin/plugin.json   plugin manifest
skills/                      doc-* skill set (the engine)
commands/                    slash commands (e.g. /doc-flow, /trace-check)
agents/                      subagents (e.g. requirements-analyst)
hooks/                       lifecycle hooks
```

It shares the `framework/` specification with Hermes AI but no runtime code,
and passes the same conformance suite (`../../tests/conformance/`).

| Field | Value |
|-------|-------|
| Engine | Native Claude Code (skills/agents/commands/hooks) |
| Version | `VERSION` (independent SemVer) |
| Conforms to | `framework_spec_version` — declared once built |
| Changelog | `CHANGELOG.md` (created in Phase 3) |
