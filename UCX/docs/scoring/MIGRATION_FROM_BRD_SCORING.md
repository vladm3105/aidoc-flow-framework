# Migration from BRD-Specific Scoring to UCX

Guide for migrating from legacy BRD scoring to UCX category-weighted scoring.

---

## Overview

UCX v1.12.0 consolidates scoring from multiple BRD-specific documents into a unified category-weighted system.

### What Changed

| Before (Deprecated) | After (UCX 1.12.0) |
|---------------------|-------------------|
| BRD_MVP_VALIDATION_RULES.md CHECK 13-18 | UCX category-weighted scoring |
| BRD_MVP_QUALITY_GATE_VALIDATION.md | UCX quality gates |
| BRD_AI_VALIDATION_DECISION_GUIDE.md | SCORING_TROUBLESHOOTING.md |
| Per-document-type scoring rules | Unified scoring for all 11 document types |

---

## Deprecated Documents

The following documents are **DEPRECATED** as of UCX v1.12.0:

### 1. BRD_MVP_QUALITY_GATE_VALIDATION.md

**Location**: `ai_dev_ssd_flow/01_BRD/BRD_MVP_QUALITY_GATE_VALIDATION.md`

**Status**: Deprecated, scheduled for removal in v2.0.0

**Replacement**: [UCX Scoring Guide](SCORING_GUIDE.md)

**Migration**:
- Quality gate checks remain valid (structural validation)
- Scoring sections superseded by UCX category-weighted scoring
- See UCX quality gate integration for updated workflow

### 2. BRD_AI_VALIDATION_DECISION_GUIDE.md

**Location**: `ai_dev_ssd_flow/01_BRD/BRD_AI_VALIDATION_DECISION_GUIDE.md`

**Status**: Deprecated, scheduled for removal in v2.0.0

**Replacement**: [Scoring Troubleshooting](SCORING_TROUBLESHOOTING.md)

**Migration**:
- AI decision-making guidance consolidated into UCX troubleshooting
- Scoring variance handling covered in new docs
- Category assignment rules formalized

### 3. BRD_MVP_VALIDATION_RULES.md (Partial)

**Location**: `ai_dev_ssd_flow/01_BRD/BRD_MVP_VALIDATION_RULES.md`

**Status**: Scoring sections (CHECK 13-18) deprecated

**Replacement**: [Weight Matrix](WEIGHT_MATRIX.md)

**What's Deprecated**:
- CHECK 13-18: PRD-Ready scoring formula
- Category deduction rules
- Score calculation methodology

**What's Still Valid**:
- CHECK 01-12: Structural validation rules
- Element code formats
- Frontmatter requirements

---

## Migration Steps

### Step 1: Remove Deprecated References

Search your codebase for references to deprecated files:

```bash
grep -r "BRD_MVP_QUALITY_GATE_VALIDATION" docs/
grep -r "BRD_AI_VALIDATION_DECISION_GUIDE" docs/
grep -r "BRD_MVP_VALIDATION_RULES.*CHECK 1[3-8]" docs/
```

### Step 2: Update Prompts

If your prompts reference the old scoring:

**Before**:
```markdown
Calculate PRD-Ready score using BRD_MVP_VALIDATION_RULES.md CHECK 13-18
```

**After**:
```markdown
Calculate weighted score using UCX category-weighted scoring.
See UCX/docs/scoring/SCORING_GUIDE.md
```

### Step 3: Configure Project Weights (Optional)

If you had custom scoring rules, migrate them:

**Before** (in BRD_MVP_VALIDATION_RULES.md):
```markdown
Compliance deduction: max -30
Functional deduction: max -25
```

**After** (in docs/UCX/scoring_weights.yaml):
```yaml
document_types:
  brd:
    categories:
      compliance:
        max_deduction: 30
      functional:
        max_deduction: 25
```

### Step 4: Update Pre-commit Hooks

Pre-commit hooks using old validation should be updated:

**Before**:
```yaml
- repo: local
  hooks:
    - id: brd-scoring
      name: BRD Scoring Validation
      entry: scripts/validate_brd_quality_score.sh
```

**After**:
```yaml
- repo: local
  hooks:
    - id: ucx-validate
      name: UCX Document Validation
      entry: ucx validate
      args: ["--tier1-only"]
```

### Step 5: Verify with UCX Scan

After migration, verify scoring works:

```bash
ucx scan docs/01_BRD/BRD-01/
ucx review brd docs/01_BRD/BRD-01/ --dry-run
```

---

## Backward Compatibility

### Old Reports

Reports created before v1.12.0 remain compatible:

- Manifest without categories → Uses persona-based extraction
- Old finding format → Parsed normally
- Legacy scores → Can be compared with `--scoring legacy`

### Legacy Scoring Mode

For comparison, use `--scoring legacy` (temporary, deprecated):

```bash
ucx review brd docs/01_BRD/BRD-01/ --scoring legacy
# WARNING: Legacy scoring is deprecated and will be removed in UCX v2.0.0
```

### API Compatibility

`calculate_legacy_score()` function available for programmatic access:

```python
from ucx.scoring import calculate_legacy_score

old_score = calculate_legacy_score(p0_count=5, p1_count=10, p2_count=3)
# Returns: 100 - (5*10) - (10*3) - (3*1) = 100 - 50 - 30 - 3 = 17
```

---

## Deprecation Timeline

| Version | Status |
|---------|--------|
| v1.12.0 | Deprecated notices added |
| v1.13.0 | Warning on deprecated doc access |
| v2.0.0 | Deprecated documents removed |

---

## FAQ

### Q: Do I need to update existing BRD documents?

No. The document format hasn't changed. Only scoring methodology changed.

### Q: Will my old review reports still work?

Yes. Old reports are backward compatible with the new scanner.

### Q: What if I prefer the old scoring?

Use `--scoring legacy` temporarily. Plan to migrate before v2.0.0.

### Q: Are BRD validation rules still valid?

Yes. CHECK 01-12 (structural validation) remain valid. Only CHECK 13-18 (scoring) are deprecated.

### Q: Do I need to retrain personas?

Not immediately. Persona prompts should be updated to include category tags for better scoring, but old behavior is supported.

---

## Support

For migration issues:

1. Check [SCORING_TROUBLESHOOTING.md](SCORING_TROUBLESHOOTING.md)
2. Run `ucx scoring validate` to check config
3. Review [SCORING_GUIDE.md](SCORING_GUIDE.md) for new methodology

---

*Version: 1.12.0 | Created: 2026-03-12*
