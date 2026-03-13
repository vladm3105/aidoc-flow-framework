# UCX Scoring Troubleshooting

Common issues and solutions for category-weighted scoring.

---

## Score Variance Between Runs

### Symptom
Same document produces different scores across reviews (e.g., 72 vs 64).

### Causes

1. **AI non-determinism**: AI models produce different finding counts each run
2. **Category assignment variance**: Different categorization of similar findings
3. **Manifest parsing differences**: Chairperson manifest format variations

### Solutions

| Approach | Impact |
|----------|--------|
| Use category caps | Limits variance impact |
| Review Chairperson manifest | Consistent category distribution |
| Run `ucx scan` | Pre-analysis of findings |
| Enable `--multi-turn` | More consistent review |

### Expected Variance

Target: ≤5 points standard deviation across 3 runs.

---

## Findings Not Categorized Correctly

### Symptom
Findings appear in wrong category or fall to "other".

### Diagnosis

```bash
# Check categorization in scan output
ucx scan docs/01_BRD/BRD-01.UCR_review_report_v002.md

# Look for "uncategorized" count
```

### Solutions

| Issue | Solution |
|-------|----------|
| Missing element code in ID | Add element code (e.g., `BRD.01.xx.xx`) |
| No keyword match | Add relevant keywords to finding text |
| Wrong persona assignment | Update persona primary categories |
| Missing explicit tag | Add `[CAT:xxx]` tag to finding |

### Improving Category Coverage

1. Update persona prompts with category tagging requirements
2. Add project-specific keywords to compliance
3. Ensure finding IDs include element codes

---

## Score Lower Than Expected

### Symptom
Document gets FAIL (< 70) when expecting PASS.

### Diagnosis

Check the category summary table in the Chairperson manifest:

```markdown
| Category | P0 | P1 | P2 | Raw | Capped | Weighted |
|----------|----|----|----|----|--------|----------|
| functional | 10 | 5 | 2 | 117 | -25 | -6.25 |
```

### Common Causes

| Cause | Indicator | Solution |
|-------|-----------|----------|
| Many P0 findings | High P0 counts | Address critical issues |
| One category dominates | Single category maxed | Review category distribution |
| Wrong weights | Weights sum ≠ 100% | Fix config validation error |
| All findings uncategorized | High "other" count | Improve categorization |

---

## Config Validation Errors

### Symptom
```
ScoringConfigError: BRD weights sum to 105.0%, must be 100%
```

### Cause
Partial weight override doesn't balance to 100%.

### Solution

When overriding one category, adjust another to compensate:

```yaml
# WRONG - increases total to 105%
categories:
  functional:
    weight: 0.30  # +0.05 from default 0.25

# CORRECT - balanced
categories:
  functional:
    weight: 0.30  # +0.05
  compliance:
    weight: 0.15  # -0.05 from default 0.20
```

### Validation Command

```bash
ucx scoring validate docs/UCX/scoring_weights.yaml
```

---

## Backward Compatibility Issues

### Symptom
Old reports produce errors or unexpected scores.

### Cause
Reports created before v1.12.0 lack category tags in manifest.

### Solution

Category-weighted scoring falls back to persona-based extraction for old reports:

```python
# Fallback chain
1. Try manifest categories → Not present in old reports
2. Try persona prefix extraction → ARCH-P0-001 → architect → architecture
3. Use persona default category
4. Fall back to "other"
```

### Legacy Scoring Mode

**Note**: Legacy scoring (`--scoring legacy`) was removed in v1.12.0. All reviews now use category-weighted scoring exclusively. The `calculate_legacy_score()` function remains available for backward compatibility testing but emits a deprecation warning.

---

## Industry Template Not Applied

### Symptom
Compliance keywords don't match industry-specific terms.

### Cause
Industry template not configured in project config.

### Solution

Add `extends` directive:

```yaml
# docs/UCX/scoring_weights.yaml
extends: healthcare_compliance

categories:
  compliance:
    keywords_append:
      - "ProjectSpecificTerm"
```

### Available Templates

- `fintech_compliance`
- `healthcare_compliance`
- `general_compliance`
- `government_compliance`

---

## CLI Scoring Commands Not Working

### Symptom
`ucx scoring show brd` command not recognized.

### Cause
UCX version < 1.12.0 doesn't have scoring CLI.

### Solution

Update UCX:

```bash
pip install --upgrade ucx
ucx --version  # Should show 1.12.0+
```

---

## Weight Matrix Questions

### Q: Why do different document types have different weights?

Each document type has a different focus:

| Doc Type | Focus | Weight Emphasis |
|----------|-------|-----------------|
| BRD | Business | compliance (20%), functional (25%) |
| BDD | Testing | acceptance (25%), integration (15%) |
| ADR | Decisions | architecture (15%), risk (15%) |

### Q: Can I use different max_deductions?

Yes, but caps should be proportional to weights:

```yaml
categories:
  functional:
    weight: 0.30
    max_deduction: 30  # Proportional to weight
```

---

## Debug Commands

### View Current Weights

```bash
ucx scoring show brd
ucx scoring show prd
```

### Validate Config

```bash
ucx scoring validate docs/UCX/scoring_weights.yaml
```

### Compare Scoring Methods

```bash
ucx scoring compare docs/01_BRD/BRD-01.UCR_review_report_v002.md
```

### Analyze Report Categories

```bash
ucx scan docs/01_BRD/BRD-01.UCR_review_report_v002.md --verbose
```

---

## Getting Help

1. Check this troubleshooting guide
2. Review [SCORING_GUIDE.md](SCORING_GUIDE.md)
3. Inspect Chairperson manifest in report
4. Run `ucx scan` for pre-analysis
5. Check UCX logs for categorization warnings

---

*Version: 1.12.0 | Created: 2026-03-12*
