# CHANGELOG v0.18.0

**Release Date**: 2026-04-02
**Type**: Minor (Unified Report Naming Standard)

## Summary

mcp_sdd v1.11.0: Unified report naming `{DOC-ID}.{STAGE}.{FORMAT}` across all tools. Sub-framework registry (sdd, gov, kb). Derived copies renamed. 1,089 legacy reports deleted.

## Changes

- New `REPORT_NAMING_STANDARDS.md` framework standard
- Report filenames in 6 runners use doc_id
- Derived copies: `_validate_copy` / `_remediate_copy`
- Detection patterns updated across all tools
- 1,089 legacy reports cleaned from b-local-docs

## References

- [PLAN-021](mcp_sdd/docs/plans/PLAN-021_sdd_reporting_naming_standard.md)
- [mcp_sdd CHANGELOG v1.11.0](mcp_sdd/docs/CHANGELOG/CHANGELOG_v1.11.0.md)
