# UCX v1.10.0 Changelog

**Release Date**: 2026-03-12

## Summary

This release introduces **Adaptive Remediation with Pre-Screening**, significantly reducing token usage and improving fix quality by loading only the fixer personas needed based on actual UCR findings.

---

## New Features

### Pre-Screening Phase

A new pre-screening step automatically analyzes UCR review reports before remediation:

```bash
# Standalone pre-screening command
ucx prescreen BRD-01.UCR_review_report_v003.md --verbose

# Output:
# ┌─────────────────────────┬──────────────────────────────────────┐
# │ Metric                  │ Value                                │
# ├─────────────────────────┼──────────────────────────────────────┤
# │ Total findings          │ 103                                  │
# │ Actionable (P0/P1 open) │ 17                                   │
# │ Domain fixers needed    │ qa_lead                              │
# │ Mandatory fixers        │ chaos_engineer, chairperson         │
# │ Excluded fixers         │ architect, auditor, integration_lead │
# └─────────────────────────┴──────────────────────────────────────┘
# → Remediation will load 3 fixers (saved 3 from loading)

# Save to JSON
ucx prescreen BRD-01.UCR_review_report_v003.md -o screening.json
```

### Adaptive Fixer Loading

Fixers are now classified into two categories:

| Category | Personas | Loading Rule |
|----------|----------|--------------|
| **Domain Fixers** | architect, auditor, qa_lead, integration_lead | Only loaded if findings exist |
| **Mandatory** | chaos_engineer, chairperson | Always loaded |

### Chairperson as Mandatory Fixer

The Chairperson persona is now **always loaded** to provide:
- De-duplication of overlapping fixes
- Conflict resolution between fixer proposals
- Execution order synthesis
- Final remediation conclusion

### Token Savings

| Scenario | Before | After | Savings |
|----------|--------|-------|---------|
| All findings resolved | 6 skills (~3000 tokens) | 2 mandatory (~1000 tokens) | 67% |
| Only auditor findings | 6 skills | 3 skills | 50% |
| Mixed findings | 6 skills | 4-5 skills | 17-33% |

---

## New Module

### `ucx/prescreening/`

New module for UCR report analysis:

```
ucx/prescreening/
├── __init__.py
└── ucr_analyzer.py    # ScreeningResult, analyze_ucr_report()
```

**Key Functions:**

```python
from ucx.prescreening import analyze_ucr_report, ScreeningResult

# Analyze UCR report
result = analyze_ucr_report(Path("BRD-01.UCR_review_report_v003.md"))

# Access results
print(result.total_findings)           # 103
print(result.actionable_findings)      # 17
print(result.required_fixers)          # ['qa_lead', 'chaos_engineer', 'chairperson']
print(result.domain_fixers_needed)     # ['qa_lead']
print(result.excluded_fixers)          # ['architect', 'auditor', 'integration_lead']
print(result.findings_by_fixer)        # {'qa_lead': ['P1-1', 'P1-7', 'P1-8']}
```

---

## API Changes

### UCRemPhase

New attribute and behavior:

```python
ucrem = UCRemPhase(config)
fixes, report_path = ucrem.generate_fixes(review_report, doc_path)

# NEW: Access pre-screening results
screening = ucrem.last_screening
print(f"Domain fixers: {screening.domain_fixers_needed}")
print(f"Excluded: {screening.excluded_fixers}")
```

### layer_skills.py

New constants:

```python
from ucx.config.layer_skills import (
    DOMAIN_FIXER_SKILLS,    # ['architect', 'auditor', 'qa_lead', 'integration_lead']
    MANDATORY_FIXER_SKILLS, # ['chaos_engineer', 'chairperson']
    FIXER_SKILLS,           # All 6 (backward compatible)
)
```

---

## CLI Changes

### New Command: `ucx prescreen`

```bash
ucx prescreen <review_report> [OPTIONS]

Options:
  -o, --output PATH   Save screening results to JSON
  -v, --verbose       Show detailed findings by fixer
```

### Updated Command: `ucx remediate`

Now displays pre-screening results:

```bash
ucx remediate BRD-01.UCR_review_report_v003.md docs/01_BRD/BRD-01/

# Output includes:
# Pre-Screening:
#   Findings: 103 total, 17 actionable
#   Domain fixers: qa_lead
#   Excluded: architect, auditor, integration_lead
```

---

## File Changes

| File | Change |
|------|--------|
| `ucx/prescreening/__init__.py` | New module |
| `ucx/prescreening/ucr_analyzer.py` | Pre-screening logic |
| `ucx/config/layer_skills.py` | Added `DOMAIN_FIXER_SKILLS`, `MANDATORY_FIXER_SKILLS` |
| `ucx/api/remediation.py` | Integrated pre-screening, adaptive skill loading |
| `ucx/cli/main.py` | Added `prescreen` command, updated `remediate` output |
| `skills/chairperson.md` | Added remediation synthesis responsibilities |
| `skills/integration_lead.md` | Symlink to `integration_expert.md` |
| `remediation/UCRem_PERSONAS.md` | Added Chairperson section, adaptive loading docs |

---

## Persona Mapping

UCR review personas are mapped to fixer personas:

| UCR Review Persona | Fixer Persona |
|-------------------|---------------|
| Architect | architect |
| Auditor | auditor |
| Tech Lead | qa_lead |
| QA Lead | qa_lead |
| Chaos Engineer | chaos_engineer |
| Integration Expert | integration_lead |
| Operator | integration_lead |
| Strategist | *skip* (business-level) |
| Product Owner | *skip* (business-level) |
| Business Analyst | *skip* (business-level) |

---

## Migration Notes

### Backward Compatibility

- `FIXER_SKILLS` constant still exports all 6 fixers
- Existing remediation code continues to work
- Pre-screening is automatic and transparent

### Behavior Changes

1. **Empty Reports**: If no actionable findings exist, an empty report is generated instead of calling AI
2. **Chairperson Always Loaded**: Even with single domain fixer, chairperson provides synthesis
3. **Pre-screening Metadata**: UCRem reports now include pre-screening statistics section

---

## Example Workflow

```bash
# 1. Review document
ucx review brd docs/01_BRD/BRD-01/ --multi-turn

# 2. Pre-screen to see what fixers needed (optional)
ucx prescreen docs/01_BRD/BRD-01/BRD-01.UCR_review_report_v001.md -v

# 3. Run remediation (pre-screening runs automatically)
ucx remediate docs/01_BRD/BRD-01/BRD-01.UCR_review_report_v001.md \
    docs/01_BRD/BRD-01/ \
    --apply-auto-safe

# Output:
# Pre-Screening:
#   Findings: 45 total, 12 actionable
#   Domain fixers: auditor, qa_lead
#   Excluded: architect, integration_lead
#
# Remediation report: docs/01_BRD/BRD-01/BRD-01.UCRem_report.md
# Fixes: auto-safe=8, auto-assisted=3, manual=1
# Applied 8 auto-safe fixes
```
