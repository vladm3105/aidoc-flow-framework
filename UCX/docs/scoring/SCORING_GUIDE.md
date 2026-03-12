# UCX Scoring Guide

## Overview

UCX v1.12.0 introduces **category-weighted scoring**, a unified scoring system that maps review findings to standardized categories with per-category weights and caps.

### Why Category-Weighted Scoring?

The legacy scoring formula (`100 - (P0×10) - (P1×3) - (P2×1)`) had limitations:

| Problem | Impact |
|---------|--------|
| No category weighting | All findings weighted equally regardless of domain |
| No deduction caps | Scores could go negative with many findings |
| AI non-determinism | Different finding counts produced inconsistent scores |
| No alignment with element codes | Scoring didn't reflect ID_NAMING_STANDARDS categories |

Category-weighted scoring solves these issues by:
- Grouping findings into 8 standardized categories
- Applying per-category weights based on document type
- Capping maximum deduction per category
- Aligning with ID_NAMING_STANDARDS element type codes

---

## Score Interpretation

| Score Range | Status | Meaning |
|-------------|--------|---------|
| 85-100 | PASS | PRD-Ready, proceed to next layer |
| 70-84 | WARN | Needs attention, review findings |
| 0-69 | FAIL | Not ready, address critical issues |

---

## Categories

UCX defines 8 scoring categories mapped to ID_NAMING_STANDARDS element type codes:

| Category | ID | Element Codes | Description |
|----------|-----|---------------|-------------|
| functional | CAT-01 | 01, 22, 24 | Functional requirements completeness |
| quality | CAT-02 | 02, 91-99 | Quality attributes coverage |
| compliance | CAT-03 | (keywords) | Regulatory and compliance requirements |
| constraints | CAT-04 | 03, 04 | Constraints and assumptions |
| integration | CAT-05 | 05, 16, 20 | Dependencies and integrations |
| acceptance | CAT-06 | 06, 14, 40-45 | Acceptance criteria and testability |
| risk | CAT-07 | 07 | Risk identification and mitigation |
| architecture | CAT-08 | 10, 12, 13, 32 | Architecture decisions |

### Category Detection

Findings are categorized using this priority order:

1. **Explicit tag**: `[CAT:xxx]` tag in finding text
2. **Element code**: Code extracted from finding ID (e.g., `BRD.01.xx.xx` → functional)
3. **Keyword match**: Category keywords in finding text
4. **Persona default**: Persona's primary category (e.g., auditor → compliance)
5. **Fallback**: Assigned to "other" (0% weight, tracking only)

---

## Weights

### Default Weights (BRD)

| Category | Weight | Max Deduction |
|----------|--------|---------------|
| functional | 25% | -25 |
| quality | 15% | -15 |
| compliance | 20% | -20 |
| constraints | 10% | -10 |
| integration | 10% | -10 |
| acceptance | 10% | -10 |
| risk | 5% | -5 |
| architecture | 5% | -5 |
| **Total** | **100%** | **-100** |

Weights vary by document type. See [WEIGHT_MATRIX.md](WEIGHT_MATRIX.md) for complete matrices.

### Per-Category Caps

Each category has a maximum deduction cap that prevents runaway scores:

- A category with 50 P0 findings (raw deduction = 500) caps at its max (e.g., -25 for functional)
- This ensures scores remain in a usable range even with many findings
- The weighted deduction is: `min(raw_deduction, max_deduction) × weight`

---

## Score Calculation

### Formula

```python
# Per-category deduction
raw_deduction = (P0_count × 10) + (P1_count × 3) + (P2_count × 1)
capped_deduction = min(raw_deduction, max_deduction)
weighted_deduction = capped_deduction × category_weight

# Final score
total_weighted_deduction = sum(weighted_deduction for each category)
final_score = max(0, 100 - total_weighted_deduction)
```

### Example

Document with findings:
- Functional: 2 P0, 1 P1, 0 P2
- Compliance: 1 P0, 2 P1, 1 P2

**Functional calculation (BRD)**:
- Raw: (2×10) + (1×3) + (0×1) = 23
- Capped: min(23, 25) = 23
- Weighted: 23 × 0.25 = 5.75

**Compliance calculation (BRD)**:
- Raw: (1×10) + (2×3) + (1×1) = 17
- Capped: min(17, 20) = 17
- Weighted: 17 × 0.20 = 3.40

**Final score**: 100 - 5.75 - 3.40 = 90.85 → **PASS**

---

## Thresholds

### Default Thresholds

| Threshold | Score | Status |
|-----------|-------|--------|
| Pass | ≥85 | PRD-Ready |
| Warn | 70-84 | Needs review |
| Fail | <70 | Not ready |

### Document-Type Variations

Some document types may have adjusted thresholds based on their position in the SDD layer hierarchy.

---

## Customization

### Project Weight Overrides

Create `docs/UCX/scoring_weights.yaml` in your project to override defaults:

```yaml
# Increase functional weight for a feature-heavy project
document_types:
  brd:
    categories:
      functional:
        weight: 0.30  # Increase from 0.25
      compliance:
        weight: 0.15  # Decrease to maintain 100%
```

**Important**: Weights must sum to 100% (1.0) for each document type.

### Industry Templates

UCX provides industry-specific compliance keyword templates:

| Template | Industry |
|----------|----------|
| `fintech_compliance` | Financial technology, banking, payments |
| `healthcare_compliance` | Healthcare, medical devices, life sciences |
| `general_compliance` | General technology, SaaS |
| `government_compliance` | Government, defense, federal |

Usage:

```yaml
extends: healthcare_compliance
categories:
  compliance:
    keywords_append:
      - "ProjectSpecificTerm"
```

### Adding Custom Keywords

Append project-specific compliance keywords:

```yaml
defaults:
  categories:
    compliance:
      keywords_append:
        - "BridgeCustody"
        - "NoahWallet"
        - "B-LocalCustom"
```

---

## Troubleshooting

### Score Variance Between Runs

Category-weighted scoring reduces but does not eliminate variance caused by AI non-determinism. Expected variance: ±5 points.

**Mitigations**:
- Use category caps to limit impact of finding count variance
- Review Chairperson manifest for consistent category distribution
- Run `ucx scan` to analyze pre-remediation state

### Category Mapping Issues

If findings are miscategorized:

1. Check finding IDs contain valid element codes
2. Verify category keywords in finding text
3. Review persona → category mapping
4. Use explicit `[CAT:xxx]` tags in persona prompts

### Backward Compatibility

Old reports without category tags remain parseable. The system falls back to persona-based extraction when manifest categories are unavailable.

Use `--scoring legacy` flag (deprecated) to see legacy score for comparison:

```bash
ucx review brd docs/01_BRD/BRD-01/ --scoring legacy
# WARNING: Legacy scoring is deprecated
```

---

## CLI Commands

### Review with Scoring

```bash
# Default weighted scoring
ucx review brd docs/01_BRD/BRD-01/

# Legacy scoring (deprecated)
ucx review brd docs/01_BRD/BRD-01/ --scoring legacy
```

### Inspect Scoring Configuration

```bash
# Show weights for document type
ucx scoring show brd

# Validate project config
ucx scoring validate docs/UCX/scoring_weights.yaml

# Compare scoring methods
ucx scoring compare docs/01_BRD/BRD-01.UCR_review_report_v002.md
```

### Scan for Categories

```bash
# Analyze report categories
ucx scan docs/01_BRD/BRD-01.UCR_review_report_v002.md
```

---

## Related Documentation

- [CATEGORY_REFERENCE.md](CATEGORY_REFERENCE.md) - Complete category definitions
- [WEIGHT_MATRIX.md](WEIGHT_MATRIX.md) - Per-document-type weight matrices
- [PERSONA_CATEGORY_MAPPING.md](PERSONA_CATEGORY_MAPPING.md) - Persona → Category rules
- [SCORING_TROUBLESHOOTING.md](SCORING_TROUBLESHOOTING.md) - Common issues
- [SCORING_CUSTOMIZATION.md](SCORING_CUSTOMIZATION.md) - Project overrides
- [MIGRATION_FROM_BRD_SCORING.md](MIGRATION_FROM_BRD_SCORING.md) - Migration guide

---

*Version: 1.12.0 | Created: 2026-03-12*
