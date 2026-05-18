# CHANGELOG v0.14.0

**Release Date**: Planned
**Type**: Minor (Cross-Section Validation)

## Summary

Adds two-tier cross-section validation to mcp_ucx `sdd_validate` tool (v1.7.0). Generic rules (SDD-XS-001/002/003) validate traceability ID existence, readiness score plausibility, and diagram registry across all 11 SDD layers. BRD-specific rules (BRD-XS-001/002/004/005) validate ADT decision propagation, phase alignment, entity consistency, and currency scope. Introduces YAML document support in validation pipeline. Updates BRD template with `diagrams` section and `cross_section_rules` metadata.

## Changes

### mcp_ucx Server (v1.7.0)

- New `validation/cross_section.py`: Generic cross-section rules for all layers
- New `validation/brd_rules.py`: BRD-specific cross-section rules
- Modified `validation/runner.py`: YAML/MD decision fork, YAML metadata validation
- New `templates/BRD-MD-TEMPLATE.md`: YAML-to-MD rendering standard

### Templates

- `BRD-TEMPLATE.yaml`: Added `diagrams` section and `cross_section_rules` metadata
- `ucx_flow_v3/01_BRD/BRD-TEMPLATE.yaml`: Synced

### Standards

- `DIAGRAM_STANDARDS.md`: BRD required diagram list (Platform: 3, Feature: 2), DFD-L1 fix

### Tests

- `test_cross_section.py`: Generic rule tests
- `test_brd_rules.py`: BRD-specific rule tests

## Backward Compatibility

All changes additive. No existing validation behavior removed. YAML fork opt-in. Template additions do not affect existing BRDs.

## References

- [PLAN-016](mcp_ucx/docs/plans/PLAN-016_cross_section_validation.md)
- [mcp_ucx CHANGELOG v1.7.0](mcp_ucx/docs/CHANGELOG/CHANGELOG_v1.7.0.md)
