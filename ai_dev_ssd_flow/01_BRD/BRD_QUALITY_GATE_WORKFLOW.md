---
title: "BRD Quality Gate Workflow"
tags:
  - brd
  - layer-1-artifact
  - workflow
  - quality-gate
  - validation
  - review
custom_fields:
  document_type: framework-guide
  artifact_type: BRD
  layer: 1
  priority: shared
  version: "1.0.0"
  created_date: "2026-02-28"
  last_updated: "2026-02-28"
---

# BRD Quality Gate Workflow

## Overview

This document defines the complete quality gate workflow for Business Requirements Documents (BRD). The workflow ensures BRDs meet both structural/schema requirements and content quality standards before proceeding to PRD generation.

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BRD Quality Gate Workflow                           │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │   BRD Created   │
                              │  (doc-brd or    │
                              │   autopilot)    │
                              └────────┬────────┘
                                       │
                                       ▼
                      ┌────────────────────────────────┐
           ┌────────▶│     GATE 1: Validator          │
           │         │     (Schema/Structural)        │
           │         │                                │
           │         │  • YAML metadata compliance    │
           │         │  • 18-section structure        │
           │         │  • Element ID format           │
           │         │  • ADR topic categories        │
           │         │  • File naming convention      │
           │         │  • Hash format validation      │
           │         └───────────────┬────────────────┘
           │                         │
           │                    PASS │ FAIL
           │                         │   │
           │                         │   ▼
           │                         │ ┌─────────────────────┐
           │                         │ │  Fixer              │
           │                         │ │  (structural fixes) │
           │                         │ │                     │
           │                         │ │  • Add missing      │
           │                         │ │    sections         │
           │                         │ │  • Fix ID formats   │
           │                         │ │  • Correct metadata │
           └─────────────────────────┼─┴─────────────────────┘
                                     │
                                     ▼
                      ┌────────────────────────────────┐
           ┌────────▶│     GATE 2: Reviewer           │
           │         │     (Content/Quality)          │
           │         │                                │
           │         │  • Link integrity              │
           │         │  • Requirement completeness    │
           │         │  • Placeholder detection       │
           │         │  • ADR topic coverage depth    │
           │         │  • Strategic alignment         │
           │         │  • Cross-BRD references        │
           │         │  • Upstream drift detection    │
           │         └───────────────┬────────────────┘
           │                         │
           │                    PASS │ FAIL
           │                         │   │
           │                         │   ▼
           │                         │ ┌─────────────────────┐
           │                         │ │  Fixer              │
           │                         │ │  (content fixes)    │
           │                         │ │                     │
           │                         │ │  • Fix broken links │
           │                         │ │  • Replace          │
           │                         │ │    placeholders     │
           │                         │ │  • Add missing      │
           │                         │ │    content          │
           └─────────────────────────┼─┴─────────────────────┘
                                     │
                                     ▼
                           ┌─────────────────┐
                           │  PRD-Ready      │
                           │  (Both gates    │
                           │   passed)       │
                           └────────┬────────┘
                                    │
                                    ▼
                           ┌─────────────────┐
                           │ PRD Generation  │
                           │ (doc-prd-       │
                           │  autopilot)     │
                           └─────────────────┘
```

---

## Workflow Stages

### Stage 1: BRD Creation

| Method | Skill | Use Case |
|--------|-------|----------|
| Manual | `doc-brd` | Interactive BRD authoring with guidance |
| Automated | `doc-brd-autopilot` | Generate from reference documents or IPLAN |

**Output**: Draft BRD document in `docs/01_BRD/BRD-NN_{slug}/` (portable path convention)

In this repository, equivalent paths are under `ai_dev_ssd_flow/01_BRD/`.

---

### Stage 2: Gate 1 - Validator (Schema/Structural)

**Skill**: `doc-brd-validator`

**Purpose**: Verify document structure matches BRD_MVP_SCHEMA.yaml

| Check | Description | Error Code Prefix |
|-------|-------------|-------------------|
| Metadata | YAML frontmatter fields | BRD-E001 to BRD-E005 |
| Structure | 18 mandatory sections present | BRD-E006 to BRD-E008 |
| Document Control | Required fields in table | BRD-E009 |
| Element IDs | `BRD.NN.TT.SS` format + section-code semantic match | BRD-E019 to BRD-E022 |
| ADR Topics | 7 mandatory categories | BRD-E013 to BRD-E018 |
| Upstream Config | `upstream_mode` validation | VAL-U001 to VAL-U005 |
| Hash Format | Drift cache hash integrity | VAL-H001 to VAL-H002 |
| File Naming | `BRD-NN_{slug}.md` pattern | BRD-W006 |

**Pass Threshold**: PRD-Ready Score ≥ 90%

**On FAIL**: Route to Fixer for structural corrections, then re-validate.

---

### Stage 3: Gate 1 Fix Loop

**Skill**: `doc-brd-fixer`

**Input Preference Order**:

1. Latest audit report (`BRD-NN.A_audit_report_vNNN.md`)
2. Latest review report (`BRD-NN.R_review_report_vNNN.md`) (legacy fallback)
3. Latest validation report (`BRD-NN.V_validation_report_vNNN.md`) (structural fallback)

| Fix Type | Auto-Fixable | Manual Required |
|----------|--------------|-----------------|
| Missing metadata fields | ✅ | |
| Invalid element ID format | ✅ | |
| Missing sections | ✅ (from template) | |
| Deprecated ID patterns | ✅ | |
| Missing Document Control fields | ✅ | |
| PRD-Ready Score calculation | ✅ | |
| Business content | | ✅ |
| ADR decision content | | ✅ |

**Loop**: Fixer → Validator → (repeat until PASS)

---

### Stage 4: Gate 2 - Reviewer (Content/Quality)

**Skill**: `doc-brd-reviewer`

**Purpose**: Deep content analysis beyond structural validation

| Check | Description | Error Code Prefix |
|-------|-------------|-------------------|
| Structure Compliance | Nested folder rule | REV-STR001 to REV-STR003 |
| Link Integrity | Internal/external links resolve | REV-L001 to REV-L003 |
| Requirement Completeness | Acceptance criteria, metrics | REV-R001 to REV-R005 |
| Diagram Contracts | C4-L1, DFD-L0 tags | REV-DC001 to REV-DC004 |
| ADR Coverage | Topic depth, decision completeness | REV-ADR001 to REV-ADR005 |
| Placeholder Detection | [TODO], [TBD], template text | REV-P001 to REV-P005 |
| Traceability Tags | Cross-references, element IDs | REV-TR001 to REV-TR004 |
| Section Completeness | Word count, MVP subsections | REV-S001 to REV-S004, REV-MVP001 to REV-MVP010 |
| Strategic Alignment | Business objectives traceability | REV-SA001 to REV-SA005 |
| Naming Compliance | doc-naming standards + section-code semantic match | REV-N001 to REV-N007 |
| Upstream Drift | Hash comparison, content changes | REV-D001 to REV-D009 |

**Pass Threshold**: Review Score ≥ 90/100

**Diagram Contract Mode**: Advisory (non-blocking) for BRD by default. Strict diagram blocking applies only when explicitly enabled.

**On FAIL**: Route to Fixer for content corrections, then re-review.

---

### Stage 5: Gate 2 Fix Loop

**Skill**: `doc-brd-fixer`

**Input Preference Order**:

1. Latest audit report (`BRD-NN.A_audit_report_vNNN.md`)
2. Latest review report (`BRD-NN.R_review_report_vNNN.md`) (legacy fallback)
3. Latest validation report (`BRD-NN.V_validation_report_vNNN.md`) (structural fallback)

| Fix Type | Auto-Fixable | Manual Required |
|----------|--------------|-----------------|
| Broken internal links | ✅ | |
| Template placeholders | ✅ | |
| Date/timestamp updates | ✅ | |
| Empty comment removal | ✅ | |
| Move to nested folder | ✅ | |
| Missing content | | ✅ |
| Strategic alignment | | ✅ |
| Business decisions | | ✅ |

**Loop**: Fixer → Reviewer → (repeat until PASS)

---

### Stage 6: Corpus Quality Gate (Cross-BRD)

**Specification**: `BRD_MVP_QUALITY_GATE_VALIDATION.md`

**Purpose**: Validate the complete BRD corpus before Layer 2 handoff.

| Check | Description | Blocking |
|-------|-------------|----------|
| Placeholder consistency | Detect stale `(future BRD)` and related placeholders | Yes |
| Downstream reference hygiene | Prevent premature numbered Layer 2+ references | Yes |
| Index synchronization | Ensure index status aligns with files | Yes |
| Corpus consistency | Cross-document terminology/count consistency | Warning |
| Diagram contract coverage | C4/DFD/sequence advisory checks | No (advisory) |

**On FAIL**: Fix issues in affected BRDs, then re-run corpus gate.

---

### Stage 7: PRD Generation

**Skill**: `doc-prd-autopilot`

**Prerequisites**:

- Gate 1 (Validator): PASS
- Gate 2 (Reviewer): PASS
- Gate 3 (Corpus): PASS
- PRD-Ready Score: ≥ 90%

---

## Alternative Workflows

### Unified Audit Workflow (Recommended for Automation)

For CI/CD or automated pipelines, use the combined audit approach:

```
BRD Created
    → doc-brd-audit (Validator + Reviewer combined)
        → IF FAIL: doc-brd-fixer → doc-brd-audit (loop until PASS)
    → PRD Generation
```

**Skill**: `doc-brd-audit`

**Output**: Combined report (`BRD-NN.A_audit_report_vNNN.md`)

| Advantage | Description |
|-----------|-------------|
| Single command | One invocation for both gates |
| Combined report | Unified issue list for fixer |
| Efficient | Reduces context switching |
| CI/CD friendly | Single pass/fail status |

**Usage**:
```bash
/doc-brd-audit docs/01_BRD/BRD-01_platform/BRD-01_platform.md
```

---

### Quick Check Workflow (Development)

For rapid feedback during authoring:

```
BRD Draft → Validator only (fast structural check) → Continue editing
```

Use when:
- Actively editing BRD
- Need quick schema compliance feedback
- Content not yet complete

---

## Workflow Selection Guide

| Use Case | Workflow | Skills Used |
|----------|----------|-------------|
| **Manual/Interactive** | Two-gate sequential | Validator → Fixer → Reviewer → Fixer |
| **Automated/CI** | Unified audit | Audit → Fixer loop |
| **Quick Check** | Validator only | Validator |
| **Pre-PRD Final** | Reviewer only | Reviewer (assumes Validator passed) |
| **Full Autopilot** | End-to-end | doc-brd-autopilot (includes all gates) |

---

## Report Files

Each stage produces reports stored alongside the BRD:

| Report Type | Pattern | Producer |
|-------------|---------|----------|
| Validation | `BRD-NN.V_validation_report_vNNN.md` | doc-brd-validator |
| Review | `BRD-NN.R_review_report_vNNN.md` | doc-brd-reviewer |
| Audit | `BRD-NN.A_audit_report_vNNN.md` | doc-brd-audit |
| Fix | `BRD-NN.F_fix_report_vNNN.md` | doc-brd-fixer |

**Location**: `docs/01_BRD/BRD-NN_{slug}/`

**Versioning**: Each run increments version (v001, v002, v003...)

---

## Drift Cache

The reviewer maintains a drift cache for upstream document tracking:

**File**: `docs/01_BRD/BRD-NN_{slug}/.drift_cache.json`

**Purpose**:
- Track upstream document hashes
- Detect content drift between reviews
- Maintain review history

**Updated by**: doc-brd-reviewer (mandatory after each review)

---

## Pass/Fail Thresholds

| Gate | Skill | Threshold | Blocking |
|------|-------|-----------|----------|
| Gate 1 | Validator | PRD-Ready ≥ 90% | Yes |
| Gate 2 | Reviewer | Score ≥ 90/100 | Yes |
| Gate 3 | Corpus quality gate | All blocking checks PASS | Yes |

**All three gates must PASS** before PRD generation can proceed.

---

## Validator Integration (Element Type Codes)

Standardized element type code checks are enforced in local and CI workflows.

| Execution Point | Command | Purpose |
|-----------------|---------|---------|
| Local pre-commit | `bash ai_dev_ssd_flow/01_BRD/scripts/validate_brd_wrapper.sh ai_dev_ssd_flow/01_BRD --skip-advisory` | Block commits using canonical BRD core checks |
| CI validation | `bash ai_dev_ssd_flow/01_BRD/scripts/validate_brd_wrapper.sh ai_dev_ssd_flow/01_BRD --skip-advisory` | Enforce same canonical BRD core checks in pull requests |
| Full orchestration | `python3 ai_dev_ssd_flow/scripts/validate_all.py ai_dev_ssd_flow --all` | Include cross-validator execution in aggregate validation |

Validation source of truth: `ID_NAMING_STANDARDS.md` (Standardized Element Type Codes) plus BRD section-element mapping rules.

---

## Error Recovery

### Gate 1 Failures

| Issue | Recovery |
|-------|----------|
| Missing sections | Fixer inserts from template |
| Invalid IDs | Fixer converts to unified format |
| Metadata errors | Fixer corrects YAML frontmatter |

### Gate 2 Failures

| Issue | Recovery |
|-------|----------|
| Broken links | Fixer updates paths |
| Placeholders | Fixer replaces or flags for manual |
| Missing content | Manual intervention required |
| Strategic misalignment | Manual business review required |

---

## Integration with Downstream

```
BRD (Layer 1)
    ↓ [Both gates PASS]
PRD (Layer 2)
    ↓
EARS (Layer 3)
    ↓
BDD (Layer 4)
    ↓
ADR (Layer 5)
    ↓
...downstream artifacts
```

---

## Related Documents

| Document | Purpose |
|----------|---------|
| `BRD_MVP_SCHEMA.yaml` | Schema definition for validator |
| `BRD_MVP_VALIDATION_RULES.md` | Detailed validation rules |
| `BRD_MVP_CREATION_RULES.md` | BRD authoring rules |
| `BRD-MVP-TEMPLATE.md` | Standard BRD template |
| `README.md` | BRD layer overview |

## Related Skills

| Skill | Purpose |
|-------|---------|
| `doc-brd` | Manual BRD creation |
| `doc-brd-autopilot` | Automated BRD generation |
| `doc-brd-validator` | Gate 1: Schema validation |
| `doc-brd-reviewer` | Gate 2: Content review |
| `doc-brd-fixer` | Fix issues from reports |
| `doc-brd-audit` | Combined validator + reviewer |
| `doc-prd-autopilot` | Downstream PRD generation |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1.0 | 2026-02-28 | Added Gate 3 corpus quality gate; aligned fixer input precedence with audit-first contract; expanded naming/error ranges (BRD-E022, REV-N007); clarified advisory diagram semantics; documented pre-commit/CI element type code validation integration |
| 1.0.0 | 2026-02-28 | Initial workflow documentation |

---

*Generated from BRD quality gate workflow analysis*
*Framework: AI Dev SSD Flow*
