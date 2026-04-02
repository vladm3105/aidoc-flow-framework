# CHANGELOG v0.16.0

**Release Date**: 2026-04-02
**Type**: Minor (Remediation Build Enhancement)

## Summary

mcp_sdd v1.9.0: `sdd_remediate` parses UCR review reports to produce structured per-finding remediation entries. Executor fix prompts grow from 742 chars to ~10K with actionable instructions.

## Changes

### mcp_sdd Server (v1.9.0)

- New `remediation/review_parser.py`: parses frontmatter + 3 table formats (Section 4 remediations, Sections 2-3 findings, Section 5 P2)
- `run_remediation_build()`: parsed findings, 50-cap, review_summary in report
- `remediate_fix` prompt: ~10K chars with per-finding actions

### Tests

18 new tests (205 total, 0 regressions)

## References

- [PLAN-019](mcp_sdd/docs/plans/PLAN-019_remediation_build_enhancement.md)
- [mcp_sdd CHANGELOG v1.9.0](mcp_sdd/docs/CHANGELOG/CHANGELOG_v1.9.0.md)
