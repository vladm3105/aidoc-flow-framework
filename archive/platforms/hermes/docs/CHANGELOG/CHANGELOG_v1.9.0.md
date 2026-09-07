# CHANGELOG v1.9.0

**Release Date**: 2026-04-02
**Type**: Minor (Remediation Build Enhancement)
**Plan**: [PLAN-019](../plans/PLAN-019_remediation_build_enhancement.md)

## Summary

`sdd_remediate` now parses UCR review reports to produce structured, per-finding remediation entries. The `sdd_remediate_fix` executor prompt grows from 742 chars (bare pointer) to ~10K chars with actionable per-finding instructions.

## Changes

### New Module: `remediation/review_parser.py`

Parses UCR review reports (MD format) using two strategies:

- **Frontmatter extraction**: score, recommendation, P0/P1/P2 counts, false positives
- **Table parsing**: Section 4 remediations (6-column, preferred), Sections 2-3 findings (5-column fallback), Section 5 P2 enhancements (4-column)
- Text cleanup: strips markdown bold/backtick formatting, truncates actions to 300 chars
- Fallback: returns `(None, [])` on any parse failure — caller keeps existing "review linked" finding

### Runner Changes

- `run_remediation_build()`: parsed review findings replace single "review linked" pointer
- 50-finding cap with overflow note when review has >50 findings
- `review_summary` dict added to remediation report output
- `_build_remediate_fix_prompt()` automatically includes all parsed findings (no prompt code changes needed)

### Tests

18 new tests (205 total): frontmatter parsing, three table formats, text cleanup, wiring integration, edge cases.

## Impact

| Metric | Before | After |
|--------|--------|-------|
| Remediation findings | 1 (pointer) | 22+ structured findings |
| Fix prompt size | 742 chars | ~10K chars |
| Review summary | Not available | Score, recommendation, counts |
| Executor context | "read the review report" | Per-finding actions with section refs |

## Backward Compatibility

- Fallback preserves existing behavior when review parsing returns no results
- New `review_summary` key is `None` when no review report provided
- Existing finding categories (`frontmatter`, `placeholder`, `yaml_structure`, `element_id`) unchanged
