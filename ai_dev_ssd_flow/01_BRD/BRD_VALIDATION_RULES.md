---
title: "BRD Validation Rules - Single Source of Truth"
tags:
  - validation-rules
  - single-source-of-truth
  - shared-architecture
custom_fields:
  document_type: validation-rules
  applies_to: [doc-brd-audit, doc-brd-fixer, pre-commit]
  version: "2.1"
  last_updated: "2026-03-01"
---

# BRD Validation Rules - Single Source of Truth

This document defines validation rules for BRD documents. Both **Claude skills** and **pre-commit hooks** MUST use these rules via the unified Python scripts.

---

## 1. Two-Skill Architecture

| Skill | Purpose |
|-------|---------|
| `doc-brd-audit` | All validation + scoring |
| `doc-brd-fixer` | Apply fixes from audit report |

**Deprecated**: `doc-brd-validator` and `doc-brd-reviewer` are merged into `doc-brd-audit`.

---

## 2. Validation Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Python Scripts (Single Source)                  │
│  • validate_standardized_element_codes.py                   │
│  • detect_legacy_element_ids.py                             │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
     ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
     │ Pre-commit  │ │ doc-brd-    │ │    CI/CD    │
     │   Hooks     │ │   audit     │ │  Pipeline   │
     └─────────────┘ └─────────────┘ └─────────────┘
```

---

## 3. Validation Scripts (Single Source)

| Script | Purpose | Exit Codes |
|--------|---------|------------|
| `validate_standardized_element_codes.py` | Validate compliant BRD.NN.TT.SS IDs | 0=pass, 2=fail |
| `detect_legacy_element_ids.py` | Detect legacy patterns (FR-*, ADR-*, etc.) | 0=pass, 2=fail |

**Location**: `ai_dev_ssd_flow/scripts/`

---

## 4. Execution Contract for doc-brd-audit

### 4.0 Fresh Audit Policy (MANDATORY)

**ALWAYS run the audit from scratch.** Do NOT:
- Reference previous audit reports for scoring decisions
- Skip validation steps based on drift cache history
- Assume compliance from prior fix history
- Use cached results from previous runs

**ALWAYS**:
- Run all validation scripts fresh every time
- Re-check all structure/schema compliance
- Re-compute PRD-ready score independently
- Generate a new audit report with incremented version

This ensures audit integrity and catches any regressions or new issues.

### 4.1 Two Execution Modes

| Mode | Use Case | Command |
|------|----------|---------|
| **Single BRD** | Skills targeting one document | Direct script calls |
| **All BRDs** | Pre-commit, CI | `pre-commit run` |

### 4.2 Single BRD Validation (doc-brd-audit)

For validating a specific BRD, call scripts directly with the BRD path:

```bash
# Validate element IDs
python3 ai_dev_ssd_flow/scripts/validate_standardized_element_codes.py <BRD_FOLDER> --verbose

# Detect legacy patterns
python3 ai_dev_ssd_flow/scripts/detect_legacy_element_ids.py <BRD_FOLDER> --verbose --summary
```

**Example**:
```bash
python3 ai_dev_ssd_flow/scripts/validate_standardized_element_codes.py docs/01_BRD/BRD-63_project_governance --verbose
python3 ai_dev_ssd_flow/scripts/detect_legacy_element_ids.py docs/01_BRD/BRD-63_project_governance --verbose --summary
```

### 4.3 All BRDs Validation (Pre-commit/CI)

For validating all BRDs (commits, CI pipeline):

```bash
pre-commit run brd-standardized-element-codes
pre-commit run brd-legacy-pattern-detection
```

### 4.4 Result Integration

Skills MUST:
1. Capture script stdout/stderr
2. Parse issue counts and patterns
3. Include in report section: `## Pre-commit Script Results`
4. Apply exit codes to overall PASS/FAIL status

### 4.5 Status Determination

| Script Exit | Overall Status |
|-------------|----------------|
| 0 | Continue to score calculation |
| 2 | FAIL (violations detected) |

### 4.6 Single Source of Truth

The Python scripts are the single source of truth:
- `validate_standardized_element_codes.py` - element ID format validation
- `detect_legacy_element_ids.py` - legacy pattern detection

Pre-commit hooks wrap these scripts. Skills call them directly for single-BRD validation.

---

## 5. Legacy Pattern Rules

### 5.1 Invalid Patterns (MUST detect)

| Pattern | Regex | Replacement |
|---------|-------|-------------|
| Compound FR | `FR-[A-Z]+-\d+` | `BRD.NN.01.SS` |
| Compound ADR | `ADR-[A-Z]+-\d+` | `BRD.NN.32.SS` |
| Compound NFR | `NFR-[A-Z]+-\d+` | `BRD.NN.02.SS` |
| Simple AC | `AC-\d+` | `BRD.NN.06.SS` |
| Simple BC | `BC-\d+` | `BRD.NN.03.SS` |
| Simple BA | `BA-\d+` | `BRD.NN.04.SS` |
| Simple BO | `BO-\d+` | `BRD.NN.23.SS` |
| Simple QA | `QA-\d+` | `BRD.NN.02.SS` |
| Simple R | `R-\d+` | `BRD.NN.05.SS` |

### 5.2 Element Type Code Mapping

| Code | Element Type | BRD Section |
|------|--------------|-------------|
| 01 | Functional Requirement | 6.x |
| 02 | Quality Attribute | 7.x |
| 03 | Constraint | 8.1 |
| 04 | Assumption | 8.2 |
| 05 | Risk | 10.x |
| 06 | Acceptance Criteria | 9.x |
| 07 | Dependency | - |
| 09 | User Story | 5.x |
| 23 | Business Objective | 2.x |
| 32 | Architecture Topic | 7.1 |

---

## 6. Section-Code Semantic Rules

Section 6 (Functional Requirements) MUST use code `01`.
Section 7.1 (Architecture Topics) MUST use code `32`.
Section 5 (User Stories) MUST use code `09`.
Section 10 (Risk Management) MUST use code `05` or `07`.

Violations produce `BRD-E022` errors.

---

## 7. doc-brd-audit Integration Examples

### 7.1 Script Execution in Audit

```markdown
## Element ID Validation

### Script Execution
```bash
python3 ai_dev_ssd_flow/scripts/validate_standardized_element_codes.py docs/01_BRD/BRD-63_project_governance --verbose
```

### Results
[Include script stdout here]

### Legacy Pattern Check
```bash
python3 ai_dev_ssd_flow/scripts/detect_legacy_element_ids.py docs/01_BRD/BRD-63_project_governance --verbose --summary
```

### Results
[Include script stdout here]
```

### 7.2 doc-brd-fixer Integration

Fixer MUST:
1. Read legacy patterns from script output
2. Apply conversions per Section 5.1 mapping
3. Re-run scripts to verify fixes
4. Loop until exit code 0

---

## 8. Pre-commit Hook Reference

The same scripts are used by pre-commit hooks:

```yaml
# .pre-commit-config.yaml
- id: brd-standardized-element-codes
  entry: bash ai_dev_ssd_flow/01_BRD/scripts/brd_standardized_element_codes_hook.sh docs/01_BRD

- id: brd-legacy-pattern-detection
  entry: bash ai_dev_ssd_flow/01_BRD/scripts/brd_legacy_pattern_hook.sh docs/01_BRD
```

---

## 9. Error Codes Reference

| Code | Source | Description |
|------|--------|-------------|
| BRD-E020 | validate_standardized_element_codes.py | Invalid element type code |
| BRD-E022 | validate_standardized_element_codes.py | Section-code mismatch |
| LEGACY-E001 | detect_legacy_element_ids.py | Legacy pattern detected |

---

## 10. Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.1 | 2026-03-01 | Added Fresh Audit Policy (Section 4.0); audits must always run from scratch |
| 2.0 | 2026-02-28 | Simplified to 2-skill model (doc-brd-audit + doc-brd-fixer); deprecated validator/reviewer |
| 1.0 | 2026-02-28 | Initial unified rules; script execution contract; skill integration |
