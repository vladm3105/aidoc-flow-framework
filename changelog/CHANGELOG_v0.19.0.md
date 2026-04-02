# CHANGELOG — Framework v0.19.0

**Release Date**: 2026-04-02

## Summary

UCX sub-framework v1.12.0 — multi-persona mapping support.

## UCX Sub-Framework (mcp_sdd)

- New `persona_mappings.yaml` configuration for per-doctype, per-phase persona sequences
- All creation/review tools now load multiple persona files based on mapping config
- 15-persona category map (expanded from 7)
- New `content_strategist` persona for PRD workflows
- Token budget tracking and warning system for combined persona text
- YAML schema validation with cross-reference checking
- See `mcp_sdd/docs/CHANGELOG/CHANGELOG_v1.12.0.md` for full details

## Architecture Review Fixes

- Applied 8 post-implementation fixes (2 Critical, 3 Important, 3 Design)
- Added mtime-based caching for persona mapping loading (C-1)
- Removed unused `personas` param from remediation tool schemas (C-2)
- Corrected error types, resolution hints, and lifecycle stage enum
- See `mcp_sdd/docs/CHANGELOG/CHANGELOG_v1.12.0.md` for details

## Documentation

- Updated 6 architecture docs, 7 SPEC files, 3 READMEs
- Updated SDD framework documentation references
- All prompt templates cleaned of hardcoded persona lists
