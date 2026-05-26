# UCR Unified Output Format

This document defines the unified output format for UCR (Unified Context Review) reports that combine validation and content review results.

---

## Overview

UCR v2.0 produces a unified report with three sections:

1. **Validation Results** - Automated schema/structure checks
2. **Content Review** - Multi-persona content analysis
3. **Remediation Table** - Combined findings for UCRem

---

## Report Structure

```markdown
---
title: "UCR Report: {DOC_ID}"
doc_id: "{DOC_ID}.UCR"
version: "1.0.0"
tags:
  - ucr
  - review-report
  - {doc_type}
custom_fields:
  document_type: ucr_report
  artifact_type: REVIEW_REPORT
  target_artifact_id: "{DOC_ID}"
  review_date: "{CURRENT_DATE}"
  method: UCR
  phases:
    validation: {PASSED|FAILED|SKIPPED}
    content_review: COMPLETED
  statistics:
    validation_errors: {N}
    validation_warnings: {N}
    p0_findings: {N}
    p1_findings: {N}
    p2_findings: {N}
  # Review-team scoring + coverage (framework REVIEW_TEAM.md). The score is
  # ADVISORY (weighted average of per-lens scores, capped: unresolved P0 -> 0,
  # P1 -> below gate). The gate is the deterministic structural floor + no
  # unresolved P0/P1, NOT this number.
  readiness_score: {SCORE}          # 0-100, advisory
  coverage:
    ran: [{LENSES_RUN}]
    missing: [{LENSES_MISSING}]
    coverage_ratio: {RATIO}         # ran crew-weight / total
    low_confidence: {true|false}    # below quorum -> human review
---

# UCR Report: {DOC_ID}

## Executive Summary

| Metric | Value |
|--------|-------|
| Document | {DOC_ID} |
| Review Date | {DATE} |
| Validation | {PASSED/FAILED/SKIPPED} |
| P0 Findings | {N} |
| P1 Findings | {N} |
| P2 Findings | {N} |
| Readiness Score (advisory) | {SCORE}/100 (weighted, capped) |
| Coverage | {RAN}/{EXPECTED} lenses ({coverage_ratio}); low-confidence: {true/false} |
| Overall Status | {BLOCKING/WARNING/CLEAN} |

> The **Readiness Score** is advisory (weighted average of per-lens scores; an
> unresolved P0 caps it to 0, an unresolved P1 caps it below the gate). The
> **gate** decision is the deterministic structural check **plus** "no unresolved
> P0/P1" — not this number. Below the crew **quorum** the review is
> **low-confidence → human review**, never a silent pass.

---

## Phase 1: Validation Results

### Status: {PASSED|FAILED|SKIPPED}

{Automated validation output}

### Validation Findings

| ID | Type | Check | Result | Details |
|----|------|-------|--------|---------|
| V-001 | ERROR | YAML Frontmatter | FAIL | Missing doc_id field |
| V-002 | WARN | Traceability | WARN | No upstream references |
| V-003 | PASS | Element IDs | PASS | 15 valid IDs found |

---

## Phase 2: Content Review

### Personas Applied

| Persona | Focus | Findings |
|---------|-------|----------|
| Architect | Structure, patterns | P0: 1, P1: 2 |
| Auditor | Compliance | P0: 2, P1: 1 |
| Tech Lead | Implementation | P0: 0, P1: 3 |
| Chaos Engineer | Edge cases | P0: 1, P1: 2 |
| ... | ... | ... |

### Findings by Priority

#### P0 - Critical (Must Fix)

**P0-1**: {Finding Title}
- **Source**: {Persona}
- **Location**: {Section/File}
- **Issue**: {Description}
- **Impact**: {Why critical}
- **Suggested Fix**: {Specific action}

**P0-2**: ...

#### P1 - High (Should Fix)

**P1-1**: {Finding Title}
...

#### P2 - Medium (Consider)

**P2-1**: {Finding Title}
...

---

## Phase 3: Remediation Table

Combined findings for UCRem processing:

| ID | Priority | Source | Target File | Target Section | Suggested Fix | Persona |
|----|----------|--------|-------------|----------------|---------------|---------|
| P0-1 | P0 | Validation | file.md | Frontmatter | Add doc_id field | Validator |
| P0-2 | P0 | Content | file.md | Section 3.1 | Add missing requirement | Auditor |
| P1-1 | P1 | Content | file.md | Section 5 | Clarify acceptance criteria | QA Lead |
| ... | ... | ... | ... | ... | ... | ... |

---

## Cross-Validation Notes

{Any conflicts or confirmations between personas}

### Agreed Findings
- {Finding X confirmed by multiple personas}

### Disputed Items
- {Finding Y needs resolution}

---

## Appendix A: Files Reviewed

| File | Lines | Validation | Review |
|------|-------|------------|--------|
| file1.md | 150 | PASSED | REVIEWED |
| file2.md | 230 | WARNING | REVIEWED |

## Appendix B: Review Metadata

- **UCR Version**: 2.0
- **Validation Scripts**: validate_{type}.sh
- **Skills Loaded**: {list}
- **Model**: {model}
- **Duration**: {time}
```

---

## Priority Classification

| Priority | Criteria | Action |
|----------|----------|--------|
| **P0** | Compliance, security, data integrity, blocking issues | MUST fix before approval |
| **P1** | Missing requirements, unclear specs, testability gaps | SHOULD fix |
| **P2** | Enhancements, optimizations, style improvements | MAY fix |

---

## Integration with UCRem

The remediation table is designed for direct UCRem consumption:

1. UCRem reads the remediation table
2. For each finding, generates fix proposals
3. Classifies as auto-safe, auto-assisted, or manual-required
4. Outputs UCRem report with executable fixes

---

## Validation vs Content Review

| Aspect | Validation | Content Review |
|--------|------------|----------------|
| **Method** | Automated scripts | Multi-persona AI |
| **Speed** | Fast (seconds) | Slower (minutes) |
| **Coverage** | Schema, structure | Semantics, completeness |
| **Output** | Pass/Fail/Warn | Findings with context |

Both phases contribute to the unified report. Validation failures become P0 findings automatically.
