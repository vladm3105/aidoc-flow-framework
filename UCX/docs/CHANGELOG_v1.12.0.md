# UCX v1.12.0 - Category-Weighted Scoring

**Release Date**: 2026-03-12

## Summary

UCX v1.12.0 introduces **category-weighted scoring**, replacing the legacy scoring formula with a unified system that maps findings to 8 standardized categories with per-category weights and deduction caps.

## Key Changes

### Category-Weighted Scoring

The legacy scoring formula (`100 - (P0×10) - (P1×3) - (P2×1)`) is replaced with:

```python
# Per-category deduction
raw_deduction = (P0_count × 10) + (P1_count × 3) + (P2_count × 1)
capped_deduction = min(raw_deduction, max_deduction)
weighted_deduction = capped_deduction × category_weight

# Final score
final_score = max(0, 100 - sum(weighted_deductions))
```

### 8 Scoring Categories

| Category | Weight (BRD) | Max Deduction | Element Codes |
|----------|--------------|---------------|---------------|
| functional | 25% | -25 | 01, 22, 24 |
| quality | 15% | -15 | 02, 91-99 |
| compliance | 20% | -20 | (keywords) |
| constraints | 10% | -10 | 03, 04 |
| integration | 10% | -10 | 05, 16, 20 |
| acceptance | 10% | -10 | 06, 14, 40-45 |
| risk | 5% | -5 | 07 |
| architecture | 5% | -5 | 10, 12, 13, 32 |

### Category Detection Priority

1. **Explicit tag**: `[CAT:xxx]` tag in finding text
2. **Element code**: Extracted from finding ID (e.g., `BRD.01.xx.xx` → functional)
3. **Keyword match**: Category keywords in finding text
4. **Persona default**: Persona's primary category (e.g., auditor → compliance)
5. **Fallback**: Assigned to "other" (0% weight, tracking only)

### Manifest Format Update

Review reports now include category scoring in the Chairperson manifest:

```markdown
<!-- UCX-MANIFEST-START -->

### Category Summary

| Category | P0 | P1 | P2 | Raw Deduction | Capped | Weighted |
|----------|----|----|----|--------------:|-------:|---------:|
| functional | 2 | 3 | 1 | -29 | -25 | -6.25 |
| compliance | 1 | 2 | 0 | -16 | -16 | -3.20 |
| ... | ... | ... | ... | ... | ... | ... |

### Weighted Score: 84.8/100
### PRD-Ready Status: WARN

<!-- UCX-MANIFEST-END -->
```

### Thresholds

| Score Range | Status | Meaning |
|-------------|--------|---------|
| 85-100 | PASS | PRD-Ready |
| 70-84 | WARN | Needs attention |
| 0-69 | FAIL | Not ready |

## Breaking Changes

### Legacy Scoring Removed

- The `--scoring legacy` CLI option has been removed
- All reviews now use category-weighted scoring exclusively
- `calculate_legacy_score()` function emits deprecation warning (will be removed in v2.0.0)

## New Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `ScoringCalculator` | `ucx/scoring/calculator.py` | Core weighted score calculator |
| `Category` enum | `ucx/scoring/categories.py` | 8 scoring categories |
| `CategoryConflictResolver` | `ucx/scoring/conflicts.py` | Multi-source category resolution |
| `DocumentTypeWeights` | `ucx/scoring/weights.py` | Per-doc-type weight configuration |
| `scoring_weights.yaml` | `ucx/scoring/` | Default weight matrices |

## Files Changed

| File | Change |
|------|--------|
| `ucx/scoring/calculator.py` | New: ScoringCalculator, Finding, ScoringResult dataclasses |
| `ucx/scoring/categories.py` | New: Category enum, detection functions |
| `ucx/scoring/conflicts.py` | New: CategoryConflictResolver |
| `ucx/scoring/weights.py` | New: DocumentTypeWeights, load_weights() |
| `ucx/core/review_memory.py` | Updated: calculate_weighted_score(), _format_scoring_summary() |
| `ucx/models/review.py` | Updated: ReviewResult with weighted_score field |
| `ucx/api/review.py` | Updated: logging with weighted_score |
| `ucx/cli/main.py` | Updated: removed legacy scoring option |
| `skills/chairperson.md` | Updated: category summary table format |

## Documentation Updates

| Document | Description |
|----------|-------------|
| [SCORING_GUIDE.md](scoring/SCORING_GUIDE.md) | Primary scoring user guide |
| [WEIGHT_MATRIX.md](scoring/WEIGHT_MATRIX.md) | Per-document-type weight matrices |
| [CATEGORY_REFERENCE.md](scoring/CATEGORY_REFERENCE.md) | Category definitions |
| [PERSONA_CATEGORY_MAPPING.md](scoring/PERSONA_CATEGORY_MAPPING.md) | Persona → Category rules |
| [SCORING_TROUBLESHOOTING.md](scoring/SCORING_TROUBLESHOOTING.md) | Common issues |
| [MIGRATION_FROM_BRD_SCORING.md](scoring/MIGRATION_FROM_BRD_SCORING.md) | Migration guide |

## Test Coverage

- 10 new integration tests in `tests/ssd_scoring/test_review_integration.py`
- All 142 tests pass

## Benefits

1. **Consistent scores**: Per-category caps prevent runaway negative scores
2. **Aligned with ID_NAMING_STANDARDS**: Categories match element type codes
3. **Reduced variance**: Category weighting reduces AI non-determinism impact
4. **Customizable**: Project-specific weight overrides supported
5. **Backward compatible**: Old reports parsed with persona-based fallback

## Migration

No migration required for reports. Old reports without category tags are handled via fallback to persona-based category assignment.

## Related Documentation

- [PLAN-002: Category-Weighted Scoring](plans/PLAN-002_category_weighted_scoring.md)
- [UCX README](../README.md)
