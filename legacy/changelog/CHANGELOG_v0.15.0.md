# CHANGELOG v0.15.0

**Release Date**: 2026-04-02
**Type**: Minor (YAML Parity and API Consistency)

## Summary

mcp_ucx v1.8.0: All tools handle YAML documents on par with MD. Categorized scoring weights (structural vs cross-section errors). Result class API aliases for uniform access. YAML structure validation in remediation. Shared source file collector.

## Changes

### mcp_ucx Server (v1.8.0)

- `sdd_consistency`: YAML source + derived artifact detection
- `sdd_next_action`: YAML lifecycle stage tracking
- `sdd_score_show/validate`: Categorized weights (structural=20, cross-section=10, warning=5)
- `sdd_remediate`: YAML structure validation (required keys, empty sections, element IDs)
- Result class API: `.report`/`.is_valid`/`.is_ready` property aliases on 6 classes
- New `utils/source_files.py`: Shared source file collector

### Tests

24 new tests (187 total, 0 regressions)

## Backward Compatibility

All changes additive. Old report formats use original scoring formula. Existing `payload`/`passed` attributes unchanged.

## References

- [PLAN-018](mcp_ucx/docs/plans/PLAN-018_yaml_parity_and_api_consistency.md)
- [mcp_ucx CHANGELOG v1.8.0](mcp_ucx/docs/CHANGELOG/CHANGELOG_v1.8.0.md)
