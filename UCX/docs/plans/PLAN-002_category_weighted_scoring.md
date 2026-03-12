# PLAN-002: Category-Weighted Scoring System

## Overview

Implement a unified category-weighted scoring system for UCX review that maps persona findings to standardized element type categories, applying consistent weights with per-category caps.

**Problem Statement**: UCX v1.11.0 review scoring produces inconsistent results:
- v001 review: 72/100 (weighted score)
- v002 review: 15/100 (PRD-Ready formula)
- Same document, no changes between reviews

**Root Causes**:
1. AI non-determinism produces different finding counts between runs
2. Current formula `100 - (P0×10) - (P1×3) - (P2×1)` has no caps → negative scores
3. Scoring methodology changed between versions
4. No alignment with `BRD_MVP_VALIDATION_RULES.md` category-based approach

**Solution**: Category-weighted scoring with:
- Per-category caps preventing runaway deductions
- Persona-to-category mapping for domain expertise alignment
- Consistent weights across all document types
- Alignment with ID_NAMING_STANDARDS.md element type codes

**Status**: Planning
**Target Version**: UCX 1.12.0
**Estimated Effort**: Medium-High complexity

---

## Design

### Category Definitions

Based on `ID_NAMING_STANDARDS.md` standardized element type codes (01-99):

| Category | ID | Name | Element Codes | Weight | Max Deduction |
|----------|-----|------|---------------|--------|---------------|
| CAT-01 | `functional` | Functional Completeness | 01, 22, 24 | 25% | -25 |
| CAT-02 | `quality` | Quality Attributes | 02, 91-99 | 15% | -15 |
| CAT-03 | `compliance` | Compliance & Regulatory | (cross-cutting) | 20% | -20 |
| CAT-04 | `constraints` | Constraints & Assumptions | 03, 04 | 10% | -10 |
| CAT-05 | `integration` | Dependencies & Integration | 05, 16, 20 | 10% | -10 |
| CAT-06 | `acceptance` | Acceptance & Testability | 06, 14, 40-45 | 10% | -10 |
| CAT-07 | `risk` | Risk Management | 07 | 5% | -5 |
| CAT-08 | `architecture` | Architecture & Decisions | 10, 12, 13, 32 | 5% | -5 |
| | | **Total** | | 100% | -100 |

### Persona → Category Mapping

| Persona | Primary Categories | Secondary | Finding Prefix |
|---------|-------------------|-----------|----------------|
| Architect | CAT-08, CAT-02, CAT-05 | CAT-01 | `ARCH-` |
| Auditor | CAT-03, CAT-04, CAT-07 | - | `AUD-` |
| Tech Lead | CAT-01, CAT-02, CAT-05 | CAT-06 | `TL-` |
| Strategist | CAT-04, CAT-07, CAT-08 | CAT-01 | `STRAT-` |
| Devil's Advocate | All (validation) | - | `DA-` |
| Operator | CAT-02 (91,92,93,98), CAT-07 | - | `OPS-` |
| Integration Lead | CAT-05, CAT-06 | CAT-01 | `INT-` |
| Product Owner | CAT-01, CAT-06 | CAT-04 | `PO-` |
| Business Analyst | CAT-04, CAT-01 | CAT-07 | `BA-` |
| Fact Checker | Cross-validation | - | `FC-` |
| Chairperson | Synthesis only | - | - |

### Score Formula

```python
def calculate_category_score(findings: dict, category: str) -> float:
    """Calculate score for a single category."""
    p0_count = findings.get(category, {}).get('P0', 0)
    p1_count = findings.get(category, {}).get('P1', 0)
    p2_count = findings.get(category, {}).get('P2', 0)

    # Raw deduction (uncapped)
    raw_deduction = (p0_count * 10) + (p1_count * 3) + (p2_count * 1)

    # Cap at category maximum
    max_deduction = CATEGORY_WEIGHTS[category]['max_deduction']
    capped_deduction = min(raw_deduction, abs(max_deduction))

    return capped_deduction

def calculate_weighted_score(findings: dict) -> float:
    """Calculate final weighted score across all categories."""
    total_deduction = 0.0

    for category, config in CATEGORY_WEIGHTS.items():
        category_deduction = calculate_category_score(findings, category)
        weighted_deduction = category_deduction * config['weight']
        total_deduction += weighted_deduction

    # Final score: 100 - weighted deductions
    final_score = max(0, min(100, 100 - total_deduction))
    return round(final_score, 1)
```

### Document-Type Weight Variations

**All document types** with category weights (must sum to 100%):

| Category | BRD | PRD | EARS | BDD | ADR | SYS | REQ | SPEC | CTR | TASKS | TSPEC |
|----------|----:|----:|-----:|----:|----:|----:|----:|-----:|----:|------:|------:|
| functional | 25 | 30 | 35 | 20 | 10 | 30 | 40 | 25 | 15 | 30 | 25 |
| quality | 15 | 15 | 10 | 15 | 15 | 20 | 15 | 20 | 10 | 10 | 20 |
| compliance | 20 | 15 | 10 | 10 | 10 | 10 | 10 | 10 | 20 | 5 | 10 |
| constraints | 10 | 10 | 10 | 10 | 15 | 10 | 5 | 5 | 15 | 10 | 5 |
| integration | 10 | 10 | 10 | 15 | 15 | 10 | 10 | 15 | 20 | 15 | 15 |
| acceptance | 10 | 10 | 15 | 25 | 5 | 10 | 15 | 15 | 10 | 15 | 20 |
| risk | 5 | 5 | 5 | 2.5 | 15 | 5 | 2.5 | 5 | 5 | 10 | 2.5 |
| architecture | 5 | 5 | 5 | 2.5 | 15 | 5 | 2.5 | 5 | 5 | 5 | 2.5 |
| **Total** | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |

**Weight Rationale**:
- **BRD**: Higher compliance (20%) for business-level regulatory requirements
- **PRD/EARS**: Higher functional (30-35%) for product feature focus
- **BDD**: Higher acceptance (25%) for testability scenarios
- **ADR**: Higher architecture/risk (15% each) for decision impact analysis
- **CTR**: Higher integration/compliance (20% each) for contract boundaries
- **TASKS**: Higher functional/integration (30/15%) for implementation planning
- **TSPEC**: Higher quality/acceptance (20% each) for test coverage

---

## Implementation Plan

### Phase 1: Core Scoring Module (UCX 1.12.0)

**Task 1.1: Create scoring module**
- File: `ucx/scoring/__init__.py`
- File: `ucx/scoring/categories.py` - Category definitions and element code mappings
- File: `ucx/scoring/weights.py` - Per-document-type weight configurations
- File: `ucx/scoring/calculator.py` - Score calculation logic

**Task 1.2: Create category weight configuration**
- File: `ucx/config/scoring_weights.yaml` - YAML config for weights
- Support per-project overrides via `docs/UCX/scoring_weights.yaml`
- Include ALL document types (BRD, PRD, EARS, BDD, ADR, SYS, REQ, SPEC, CTR, TASKS, TSPEC)

**Task 1.3: Unit tests**
- File: `tests/scoring/test_categories.py`
- File: `tests/scoring/test_calculator.py`
- Test edge cases: zero findings, max findings, category caps

**Task 1.4: Weight validation (GAP FIX)**
- Validate `sum(weights) == 1.0` per document type on config load
- Raise `ScoringConfigError` if weights don't sum to 100%
- Log warning if document-type override changes fewer than all categories
- Validation in `weights.py:load_weights()`:
```python
def validate_weights(doc_type: str, weights: dict) -> None:
    total = sum(cat['weight'] for cat in weights['categories'].values())
    if abs(total - 1.0) > 0.001:
        raise ScoringConfigError(
            f"{doc_type} weights sum to {total*100}%, must be 100%"
        )
```

**Task 1.5: Uncategorized finding handling (GAP FIX)**
- Define fallback category assignment rules:
  1. Try element code match (from finding ID)
  2. Try keyword match (from finding text)
  3. Fall back to persona's primary category
  4. Last resort: assign to `other` category
- Add `other` category with 0% weight (no score impact, tracking only)
- Log warning for each uncategorized finding
- Include uncategorized count in scan output

**Task 1.6: Category conflict resolution (GAP FIX)**
- Finding may match multiple categories (e.g., compliance keyword + element code)
- Resolution order: Element code > Keyword > Persona default
- Log info when conflict resolved
- Track conflict count in metrics

### Phase 2: Persona Prompt Updates (UCX 1.12.0)

**Task 2.1: Update Chairperson manifest format**
- Add `category` field to each finding
- Add category summary table to manifest
- Add weighted score calculation section

**Task 2.2: Update UCR_PROMPT templates**
- Framework: `UCX/review/UCR_PROMPT_{TYPE}.md`
- Project: `docs/UCX/review/UCR_PROMPT_{TYPE}_PROJECT.md`

**Task 2.3: Update ALL persona prompts (GAP FIX)**

Each non-Chairperson persona prompt must include category tagging instructions:

| Persona | Primary Categories | Prompt Addition |
|---------|-------------------|-----------------|
| Architect | architecture, quality, integration | Tag findings with `[CAT:architecture]` or `[CAT:quality]` |
| Auditor | compliance, constraints, risk | Tag findings with `[CAT:compliance]` or `[CAT:risk]` |
| Tech Lead | functional, quality, integration | Tag findings with `[CAT:functional]` or `[CAT:integration]` |
| Strategist | constraints, risk, architecture | Tag findings with `[CAT:constraints]` or `[CAT:risk]` |
| Devil's Advocate | (all - validation) | Tag with most relevant category |
| Operator | quality, risk | Tag findings with `[CAT:quality]` (ops-focused) |
| Integration Lead | integration, acceptance | Tag findings with `[CAT:integration]` |
| Product Owner | functional, acceptance | Tag findings with `[CAT:functional]` or `[CAT:acceptance]` |
| Business Analyst | constraints, functional | Tag findings with `[CAT:constraints]` |
| Fact Checker | (cross-validation) | Verify category tags from other personas |

Update persona skill files in `UCX/skills/`:
- `architect.md`, `auditor.md`, `tech_lead.md`, etc.
- Add "Category Tagging" section with primary/secondary categories
- Add output format showing category field

**Task 2.4: Chairperson output schema**
```markdown
## Chairperson Manifest

### Category Summary
| Category | P0 | P1 | P2 | Raw Deduction | Capped | Weighted |
|----------|----|----|----|--------------:|-------:|--------:|
| functional | 2 | 3 | 1 | -30 | -25 | -6.25 |
| quality | 1 | 2 | 0 | -16 | -15 | -2.25 |
| compliance | 3 | 2 | 0 | -36 | -20 | -4.00 |
| ... | ... | ... | ... | ... | ... | ... |
| **Total** | | | | | | **-XX.XX** |

### Weighted Score: XX.X/100
### PRD-Ready Status: [PASS/FAIL] (threshold: ≥85)

### Finding Details
| ID | Category | Priority | Finding | Assigned Fixer |
|----|----------|----------|---------|----------------|
| AUD-P0-001 | compliance | P0 | SAR human review mandate | auditor |
| ARCH-P0-006 | architecture | P0 | Custody failover criteria | architect |
```

### Phase 3: Scanner & CLI Integration (UCX 1.12.0)

**Task 3.1: Update prescreening module**
- File: `ucx/prescreening.py`
- Extract category from manifest
- Calculate weighted score from manifest

**Task 3.2: Update `ucx scan` command**
- Display category breakdown
- Show weighted vs raw score comparison
- Show uncategorized findings count (if any)

**Task 3.3: Update remediation fixer routing**
- Route by category instead of persona prefix
- Support category-based fixer selection

**Task 3.4: Add CLI scoring method flag (GAP FIX)**

Add `--scoring` flag to review and scan commands:

```bash
# New weighted scoring (default)
ucx review brd docs/01_BRD/BRD-01/ --scoring weighted

# Legacy P0/P1/P2 scoring (deprecated, for comparison)
ucx review brd docs/01_BRD/BRD-01/ --scoring legacy
```

Implementation:
- File: `ucx/cli/main.py`
- Add `--scoring` option with choices `['weighted', 'legacy']`
- Default: `weighted`
- When `legacy` used, show deprecation warning:
  ```
  WARNING: Legacy scoring is deprecated and will be removed in UCX v2.0.0.
           Use --scoring weighted (default) for category-weighted scoring.
  ```
- Pass scoring method to review engine and Chairperson prompt

**Task 3.5: Add `ucx scoring` CLI command (GAP FIX)**

New command to inspect scoring configuration:

```bash
# Show default weights for document type
ucx scoring show brd

# Validate project scoring config
ucx scoring validate docs/UCX/scoring_weights.yaml

# Compare scores between methods
ucx scoring compare docs/01_BRD/BRD-01.UCR_review_report_v002.md
```

### Phase 4: Comprehensive Scoring Documentation (UCX 1.12.0)

**Task 4.1: Create UCX Scoring Documentation Suite**

Create centralized scoring documentation in `UCX/docs/scoring/`:

| Document | Purpose |
|----------|---------|
| `SCORING_GUIDE.md` | Primary user guide for understanding and using UCX scoring |
| `CATEGORY_REFERENCE.md` | Complete category definitions, element codes, keywords |
| `WEIGHT_MATRIX.md` | Per-document-type weight matrices with rationale |
| `PERSONA_CATEGORY_MAPPING.md` | Persona → Category assignment rules |
| `SCORING_TROUBLESHOOTING.md` | Common issues, score discrepancies, calibration |
| `SCORING_CUSTOMIZATION.md` | Project-specific weight overrides guide |

**Task 4.2: SCORING_GUIDE.md Structure**

```markdown
# UCX Scoring Guide

## 1. Overview
- What is category-weighted scoring?
- Why it replaces raw P0/P1/P2 counting
- Score interpretation (0-100 scale)

## 2. Categories
- 8 category definitions
- Element code mappings
- Cross-cutting keyword detection

## 3. Weights
- Default weight table
- Document-type variations
- Per-category deduction caps

## 4. Score Calculation
- Formula with examples
- Step-by-step walkthrough
- Edge cases (zero findings, max findings)

## 5. Thresholds
- Pass (≥85), Warn (70-84), Fail (<70)
- Per-document-type variations

## 6. Customization
- Project weight overrides
- Adding custom categories
- Compliance keyword lists

## 7. Troubleshooting
- Score variance between runs
- Category mapping issues
- Backward compatibility
```

**Task 4.3: WEIGHT_MATRIX.md Structure**

```markdown
# UCX Weight Matrix Reference

## Default Weights (All Document Types)
| Category | Weight | Max Deduction | Element Codes |
|----------|--------|---------------|---------------|
| functional | 25% | -25 | 01, 22, 24 |
| ... | ... | ... | ... |

## BRD Weights (Layer 1)
[Matrix with BRD-specific adjustments]

## PRD Weights (Layer 2)
[Matrix with PRD-specific adjustments]

## EARS Weights (Layer 3)
...

## Weight Rationale
[Why each document type has specific weight distribution]
```

**Task 4.4: Update existing docs**
- `docs/HOW_TO_USE.md` - Add scoring section, link to SCORING_GUIDE.md
- `docs/QUICK_START.md` - Update score interpretation
- `README.md` - Add scoring overview, link to docs/scoring/

**Task 4.5: Create industry compliance templates (GAP FIX)**

The default compliance keywords are fintech-specific. Provide industry templates:

| Template | Location | Keywords |
|----------|----------|----------|
| Fintech | `docs/scoring/templates/fintech_compliance.yaml` | FinCEN, OFAC, PCI-DSS, AML, KYC, SAR, CTR, MTL, BSA, FFIEC |
| Healthcare | `docs/scoring/templates/healthcare_compliance.yaml` | HIPAA, PHI, BAA, HITECH, ePHI, FDA, 21CFR, CLIA |
| General/Tech | `docs/scoring/templates/general_compliance.yaml` | GDPR, CCPA, SOC2, ISO27001, PII, encryption, audit |
| Government | `docs/scoring/templates/government_compliance.yaml` | FedRAMP, FISMA, NIST, FIPS, IL4, IL5, ITAR, EAR |

Template format:
```yaml
# docs/scoring/templates/healthcare_compliance.yaml
compliance:
  keywords:
    - HIPAA
    - PHI
    - "Protected Health Information"
    - BAA
    - "Business Associate Agreement"
    - HITECH
    - ePHI
    - FDA
    - "21 CFR Part 11"
    - CLIA
  weight_adjustment: 0.25  # Optional: increase compliance weight for healthcare
```

Usage in project config:
```yaml
# docs/UCX/scoring_weights.yaml
extends: fintech_compliance  # Load industry template
categories:
  compliance:
    keywords_append:  # Add project-specific terms
      - "Bridge custody"
      - "Noah wallet"
```

### Phase 5: Project Prompt Migration (Post-1.12.0)

**Task 5.1: Update BeeLocal project prompts**
- `docs/UCX/review/UCR_PROMPT_BRD_PROJECT.md`
- `docs/UCX/review/UCR_PROMPT_PRD_PROJECT.md`

**Task 5.2: Add project scoring config**
- `docs/UCX/scoring_weights.yaml` (optional overrides)

### Phase 7: Integration Testing (UCX 1.12.0) - GAP FIX

**Task 7.1: End-to-end scoring tests**
- File: `tests/integration/test_scoring_e2e.py`
- Test full flow: review → scan → score calculation
- Test with real documents (BRD-01, BRD-02 fixtures)
- Verify category assignment accuracy

**Task 7.2: Score consistency tests**
- Run same review 3 times, measure score variance
- Target: ≤5 points standard deviation
- Record baseline scores for regression testing

**Task 7.3: Backward compatibility tests**
- Parse old reports (pre-v1.12.0) without categories
- Verify graceful fallback to persona extraction
- Verify legacy scoring flag produces expected output

**Task 7.4: Weight validation tests**
- Test invalid weight configs (sum ≠ 100%)
- Test missing document types
- Test malformed YAML

**Task 7.5: Regression test fixtures**
Create golden test fixtures:
- `tests/fixtures/scoring/brd_01_expected_categories.json`
- `tests/fixtures/scoring/brd_01_expected_score.json`
- `tests/fixtures/scoring/legacy_report_no_categories.md`

---

### Phase 6: Documentation Consolidation & Deprecation (UCX 1.12.0)

**Task 6.1: Deprecate BRD-specific validation docs**

The following documents become **DEPRECATED** and superseded by UCX centralized scoring:

| Deprecated Document | Replacement | Action |
|---------------------|-------------|--------|
| `ai_dev_ssd_flow/01_BRD/BRD_MVP_QUALITY_GATE_VALIDATION.md` | `UCX/docs/scoring/SCORING_GUIDE.md` | Add deprecation notice |
| `ai_dev_ssd_flow/01_BRD/BRD_AI_VALIDATION_DECISION_GUIDE.md` | `UCX/docs/scoring/SCORING_TROUBLESHOOTING.md` | Add deprecation notice |
| `ai_dev_ssd_flow/01_BRD/BRD_MVP_VALIDATION_RULES.md` (CHECK 13-18 scoring) | `UCX/docs/scoring/WEIGHT_MATRIX.md` | Partial deprecation (scoring sections only) |

**Task 6.2: Add deprecation notices**

Add to each deprecated file:

```markdown
---
# DEPRECATED NOTICE
> **⚠️ DEPRECATED as of UCX v1.12.0**
>
> This document is superseded by UCX centralized scoring.
>
> **Migration**: See [UCX Scoring Guide](/opt/data/docs_flow_framework/UCX/docs/scoring/SCORING_GUIDE.md)
>
> **Removal**: Scheduled for UCX v2.0.0
---
```

**Task 6.3: Update cross-references**

Update all documents that reference deprecated files:
- `BRD_QUALITY_GATE_WORKFLOW.md` → Link to UCX scoring
- `BRD_VALIDATION_STRATEGY.md` → Link to UCX scoring
- Pre-commit hook documentation → Reference `ucx validate`

**Task 6.4: Create migration guide**

File: `UCX/docs/scoring/MIGRATION_FROM_BRD_SCORING.md`

```markdown
# Migration from BRD-Specific Scoring to UCX

## What Changed
- BRD_MVP_VALIDATION_RULES.md CHECK 13-18 → UCX category-weighted scoring
- BRD_MVP_QUALITY_GATE_VALIDATION.md → UCX quality gates
- Per-BRD decision guides → UCX SCORING_TROUBLESHOOTING.md

## Migration Steps
1. Remove references to deprecated scoring docs
2. Update prompts to use category-weighted output
3. Configure project-specific weights if needed
4. Validate with `ucx scan` to verify category mapping

## Backward Compatibility
- Old reports without categories remain parseable
- Legacy scoring formula available via `--legacy-scoring` flag (temporary)
```

---

## File Structure

```
UCX/
├── ucx/
│   ├── scoring/
│   │   ├── __init__.py
│   │   ├── categories.py      # Category definitions, element code mapping
│   │   ├── weights.py         # Weight loading, validation (sum=100%)
│   │   ├── calculator.py      # Score calculation, uncategorized handling
│   │   └── conflicts.py       # Category conflict resolution (NEW)
│   ├── cli/
│   │   └── main.py            # Add --scoring flag, ucx scoring commands
│   └── config/
│       └── scoring_weights.yaml  # Default config (11 doc types)
├── docs/
│   ├── scoring/                   # Comprehensive scoring documentation
│   │   ├── SCORING_GUIDE.md       # Primary user guide
│   │   ├── CATEGORY_REFERENCE.md  # Category definitions, codes, keywords
│   │   ├── WEIGHT_MATRIX.md       # Per-doc-type weight matrices
│   │   ├── PERSONA_CATEGORY_MAPPING.md  # Persona → Category rules
│   │   ├── SCORING_TROUBLESHOOTING.md   # Issues, calibration
│   │   ├── SCORING_CUSTOMIZATION.md     # Project overrides guide
│   │   ├── MIGRATION_FROM_BRD_SCORING.md # Migration from deprecated docs
│   │   └── templates/             # Industry compliance templates (NEW)
│   │       ├── fintech_compliance.yaml
│   │       ├── healthcare_compliance.yaml
│   │       ├── general_compliance.yaml
│   │       └── government_compliance.yaml
│   └── plans/
│       └── PLAN-002_category_weighted_scoring.md
├── skills/                        # Update all persona skills
│   ├── architect.md               # Add category tagging section
│   ├── auditor.md
│   ├── tech_lead.md
│   ├── strategist.md
│   ├── devils_advocate.md
│   ├── operator.md
│   ├── integration_lead.md
│   ├── product_owner.md
│   ├── business_analyst.md
│   ├── fact_checker.md
│   └── chairperson.md             # Category manifest output
└── tests/
    ├── scoring/                   # Unit tests
    │   ├── test_categories.py
    │   ├── test_calculator.py
    │   ├── test_weights.py        # Weight validation tests (NEW)
    │   └── test_conflicts.py      # Conflict resolution tests (NEW)
    ├── integration/               # Integration tests (NEW)
    │   └── test_scoring_e2e.py
    └── fixtures/                  # Test fixtures (NEW)
        └── scoring/
            ├── brd_01_expected_categories.json
            ├── brd_01_expected_score.json
            └── legacy_report_no_categories.md

# Deprecated files (to be marked in Phase 6):
ai_dev_ssd_flow/01_BRD/
├── BRD_MVP_QUALITY_GATE_VALIDATION.md  # → UCX scoring
├── BRD_AI_VALIDATION_DECISION_GUIDE.md # → UCX troubleshooting
└── BRD_MVP_VALIDATION_RULES.md         # Scoring sections → UCX
```

---

## Configuration Schema

### scoring_weights.yaml

```yaml
# UCX Category-Weighted Scoring Configuration
# Version: 1.0.0

# Default weights (apply to all document types unless overridden)
defaults:
  categories:
    functional:
      weight: 0.25
      max_deduction: 25
      element_codes: [1, 22, 24]
      description: "Functional requirements completeness"
    quality:
      weight: 0.15
      max_deduction: 15
      element_codes: [2, 91, 92, 93, 94, 95, 96, 97, 98, 99]
      description: "Quality attributes coverage"
    compliance:
      weight: 0.20
      max_deduction: 20
      element_codes: []  # Cross-cutting, matched by keyword
      keywords: ["FinCEN", "OFAC", "PCI-DSS", "AML", "KYC", "SAR", "CTR", "MTL"]
      description: "Regulatory and compliance requirements"
    constraints:
      weight: 0.10
      max_deduction: 10
      element_codes: [3, 4]
      description: "Constraints and assumptions"
    integration:
      weight: 0.10
      max_deduction: 10
      element_codes: [5, 16, 20]
      description: "Dependencies and integrations"
    acceptance:
      weight: 0.10
      max_deduction: 10
      element_codes: [6, 14, 40, 41, 42, 43, 44, 45]
      description: "Acceptance criteria and testability"
    risk:
      weight: 0.05
      max_deduction: 5
      element_codes: [7]
      description: "Risk identification and mitigation"
    architecture:
      weight: 0.05
      max_deduction: 5
      element_codes: [10, 12, 13, 32]
      description: "Architecture decisions"

  thresholds:
    pass: 85
    warn: 70
    fail: 0

# Document-type overrides
document_types:
  brd:
    # Use defaults

  prd:
    categories:
      functional:
        weight: 0.30
      compliance:
        weight: 0.15

  ears:
    categories:
      functional:
        weight: 0.35
      acceptance:
        weight: 0.15
      compliance:
        weight: 0.10

  spec:
    categories:
      functional:
        weight: 0.25
      quality:
        weight: 0.20
      integration:
        weight: 0.15
      acceptance:
        weight: 0.15
```

---

## Acceptance Criteria

### AC-1: Scoring Consistency
- [ ] Same document reviewed twice produces scores within ±5 points
- [ ] Category caps prevent negative scores
- [ ] Weighted score always in range [0, 100]

### AC-2: Category Mapping
- [ ] All persona findings map to exactly one category
- [ ] Element codes correctly parsed from finding IDs
- [ ] Cross-cutting compliance findings detected by keyword

### AC-3: Chairperson Output
- [ ] Manifest includes category summary table
- [ ] Weighted score calculated and displayed
- [ ] PRD-Ready status uses weighted score (not raw)

### AC-4: Scanner Compatibility
- [ ] `ucx scan` extracts categories from manifest
- [ ] Category breakdown displayed in scan output
- [ ] Weighted score used for fixer routing decisions

### AC-5: Configuration
- [ ] Default weights load from `scoring_weights.yaml`
- [ ] Project overrides loaded from `docs/UCX/scoring_weights.yaml`
- [ ] Document-type variations applied correctly

### AC-6: Backward Compatibility
- [ ] Old reports without categories still scannable
- [ ] Graceful fallback to persona-based extraction
- [ ] Warning when using legacy scoring

### AC-7: Documentation Completeness
- [ ] All 7 scoring docs created in `UCX/docs/scoring/`
- [ ] SCORING_GUIDE.md covers all categories and weights
- [ ] WEIGHT_MATRIX.md includes all document types
- [ ] Migration guide covers deprecated files
- [ ] Deprecated files have deprecation notices

### AC-8: Deprecation
- [ ] BRD_MVP_QUALITY_GATE_VALIDATION.md marked deprecated
- [ ] BRD_AI_VALIDATION_DECISION_GUIDE.md marked deprecated
- [ ] Cross-references updated to UCX scoring docs
- [ ] No broken links to deprecated content

### AC-9: Weight Validation (GAP FIX)
- [ ] Config loader validates sum(weights) == 100%
- [ ] ScoringConfigError raised for invalid configs
- [ ] All 11 document types defined in default config
- [ ] Warning logged for partial overrides

### AC-10: Uncategorized Handling (GAP FIX)
- [ ] Fallback category assignment works (element → keyword → persona → other)
- [ ] `other` category tracked but doesn't affect score
- [ ] Warning logged for each uncategorized finding
- [ ] `ucx scan` shows uncategorized count

### AC-11: Persona Prompts (GAP FIX)
- [ ] All 10 non-Chairperson personas updated with category tagging
- [ ] Skill files include category assignment guidelines
- [ ] Finding output includes `[CAT:xxx]` tag

### AC-12: CLI Scoring Flag (GAP FIX)
- [ ] `--scoring weighted|legacy` flag implemented
- [ ] Default is `weighted`
- [ ] Deprecation warning shown for `legacy`
- [ ] `ucx scoring show|validate|compare` commands work

### AC-13: Industry Templates (GAP FIX)
- [ ] 4 industry templates created (fintech, healthcare, general, government)
- [ ] `extends:` directive works in project config
- [ ] `keywords_append:` merges with template keywords

### AC-14: Integration Tests (GAP FIX)
- [ ] E2E tests pass with real document fixtures
- [ ] Score variance ≤5 points across 3 runs
- [ ] Backward compatibility tests pass
- [ ] Weight validation tests pass

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Category mapping ambiguity | Medium | Define clear keywords, element code priority over keywords |
| Weight imbalance | Medium | Validate weights sum to 100% on config load (Task 1.4) |
| AI non-determinism in categorization | High | Explicit category guidelines in ALL persona prompts (Task 2.3) |
| Backward compatibility | Medium | Support both old and new manifest formats, `--scoring legacy` flag |
| Per-project config complexity | Low | Defaults work, industry templates simplify setup (Task 4.5) |
| Uncategorized findings | Medium | Fallback chain: element → keyword → persona → other (Task 1.5) |
| Category conflicts | Low | Resolution order: element code > keyword > persona default (Task 1.6) |
| Integration test flakiness | Medium | Use golden fixtures, allow ±5 point variance (Task 7.2) |
| 11 persona prompts to update | Medium | Batch update with consistent template, verify with tests |

---

## Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| ID_NAMING_STANDARDS.md | Reference | Element type code definitions |
| BRD_MVP_VALIDATION_RULES.md | Reference | Existing scoring methodology (to deprecate scoring sections) |
| UCX v1.11.0 | Baseline | Chairperson manifest format |
| Python 3.12+ | Runtime | Type hints, match statements |
| PyYAML | Library | Config loading |

### Files to Deprecate

| File | Current Purpose | Replacement |
|------|-----------------|-------------|
| `ai_dev_ssd_flow/01_BRD/BRD_MVP_QUALITY_GATE_VALIDATION.md` | Corpus-level quality gates | `UCX/docs/scoring/SCORING_GUIDE.md` |
| `ai_dev_ssd_flow/01_BRD/BRD_AI_VALIDATION_DECISION_GUIDE.md` | AI decision-making guide | `UCX/docs/scoring/SCORING_TROUBLESHOOTING.md` |
| `ai_dev_ssd_flow/01_BRD/BRD_MVP_VALIDATION_RULES.md` (CHECK 13-18) | PRD-Ready scoring formula | `UCX/docs/scoring/WEIGHT_MATRIX.md` |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Score variance between runs | ≤5 points | Run same review 3x, measure std dev |
| Category coverage | 100% | All findings have category assignment |
| Uncategorized findings | <5% | Measure findings falling to `other` category |
| Weight validation | 100% | All configs pass sum=100% validation |
| Backward compatibility | 100% | Old reports parse without error |
| Documentation completeness | 100% | All 7 scoring docs + 4 templates created |
| Deprecated docs migrated | 100% | All references updated, notices added |
| Weight matrix coverage | 100% | All 11 document types have weight definitions |
| Persona prompt coverage | 100% | All 11 personas have category tagging |
| Integration test pass rate | 100% | All E2E and regression tests pass |
| CLI command coverage | 100% | `--scoring`, `ucx scoring show/validate/compare` work |

---

## Timeline

| Phase | Target | Deliverables |
|-------|--------|--------------|
| Phase 1 | UCX 1.12.0 | Scoring module, weight validation, uncategorized handling, conflict resolution |
| Phase 2 | UCX 1.12.0 | ALL persona prompts updated (11 total), category manifest |
| Phase 3 | UCX 1.12.0 | Scanner integration, `--scoring` flag, `ucx scoring` command |
| Phase 4 | UCX 1.12.0 | Scoring docs (7), industry templates (4) |
| Phase 5 | UCX 1.12.1 | Project prompt migration (BeeLocal) |
| Phase 6 | UCX 1.12.0 | Deprecation notices, cross-reference updates |
| Phase 7 | UCX 1.12.0 | Integration tests, regression fixtures, consistency validation |

### Task Summary

| Phase | Tasks | New (Gap Fix) |
|-------|-------|---------------|
| Phase 1 | 6 | 3 (1.4, 1.5, 1.6) |
| Phase 2 | 4 | 1 (2.3) |
| Phase 3 | 5 | 2 (3.4, 3.5) |
| Phase 4 | 5 | 1 (4.5) |
| Phase 5 | 2 | 0 |
| Phase 6 | 4 | 0 |
| Phase 7 | 5 | 5 (all new) |
| **Total** | **31** | **12** |

---

## References

- [ID_NAMING_STANDARDS.md](/opt/data/docs_flow_framework/ai_dev_ssd_flow/ID_NAMING_STANDARDS.md) - Element type codes
- [BRD_MVP_VALIDATION_RULES.md](/opt/data/docs_flow_framework/ai_dev_ssd_flow/01_BRD/BRD_MVP_VALIDATION_RULES.md) - Existing scoring
- [BRD_QUALITY_GATE_WORKFLOW.md](/opt/data/docs_flow_framework/ai_dev_ssd_flow/01_BRD/BRD_QUALITY_GATE_WORKFLOW.md) - Quality gates
- [PLAN-001](/opt/data/docs_flow_framework/UCX/docs/plans/PLAN-001_unified_brd_validation.md) - Unified BRD validation

---

*Created: 2026-03-12*
*Author: Claude Opus 4.5*
*Status: Planning*
