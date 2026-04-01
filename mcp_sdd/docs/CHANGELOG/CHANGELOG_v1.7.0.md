# CHANGELOG v1.7.0

**Release Date**: Planned
**Type**: Minor (Cross-Section Validation)
**Plan**: [PLAN-016](../plans/PLAN-016_cross_section_validation.md)

## Summary

Adds two-tier cross-section validation to `sdd_validate`. Tier 1 (generic) validates traceability ID existence, readiness score plausibility, and diagram registry presence across all 11 SDD layers. Tier 2 (BRD-specific) validates ADT decision propagation, phase alignment, entity consistency, and currency scope consistency. Introduces YAML document support in the validation pipeline alongside existing MD path.

## Changes

### New Modules

| Module | Purpose |
|--------|---------|
| `validation/cross_section.py` | Generic cross-section rules for all SDD layers (SDD-XS-001/002/003) |
| `validation/brd_rules.py` | BRD-specific cross-section rules (BRD-XS-001/002/004/005) |

### Generic Cross-Section Rules (All Layers)

| Rule | Check | Severity |
|------|-------|----------|
| SDD-XS-001 | Traceability ID existence — referenced IDs must exist in source sections | error |
| SDD-XS-002 | Readiness score plausibility — 100/100 with validation findings flagged | warning |
| SDD-XS-003 | Diagram registry present — layers with diagram contracts must have items | warning |

### BRD-Specific Rules

| Rule | Check | Severity |
|------|-------|----------|
| BRD-XS-001 | ADT selected decisions propagate to implementation and cost sections | warning |
| BRD-XS-002 | Phase names/count match between scope and implementation | error |
| BRD-XS-004 | Entities in executive summary appear in functional requirements | warning |
| BRD-XS-005 | Currency scope consistent across FR-01, mandatory conditions (conditional) | warning |

### Validation Runner

- YAML document support: `_collect_yaml_files()` + decision fork in `run_project_validation_build()`
- YAML metadata validation: maps YAML keys to existing tag/field checks
- MD degraded path: regex-based fallback for cross-section checks on MD documents

### Template Updates

- `BRD-TEMPLATE.yaml`: Added `diagrams` section and `cross_section_rules` metadata
- New `BRD-MD-TEMPLATE.md`: Standardized YAML-to-MD rendering template

### Standards Updates

- `DIAGRAM_STANDARDS.md`: BRD required diagram list (Platform: 3 minimum, Feature: 2 minimum)
- `DIAGRAM_STANDARDS.md`: DFD-L0 vs DFD-L1 discrepancy resolved (standardized to dfd-l1)

### Tests

- `test_cross_section.py`: Generic rule tests across BRD/PRD/SPEC doc types
- `test_brd_rules.py`: BRD-specific rule tests with YAML fixtures

## Backward Compatibility

- All changes are additive; no existing validation behavior removed
- YAML fork is opt-in (only activates when `.yaml` files found)
- MD validation path unchanged except optional cross-section calls
- Template additions (`diagrams`, `cross_section_rules`) do not affect existing BRDs
