# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of SYS-TEMPLATE.md
# - Authority: SYS-TEMPLATE.md is the single source of truth for SYS structure
# - Purpose: AI checklist after document creation (derived from template)
# - Scope: Includes all rules from SYS_CREATION_RULES.md plus validation extensions
# - On conflict: Defer to SYS-TEMPLATE.md
# =============================================================================
---
title: "SYS Validation Rules Reference"
tags:
  - validation-rules
  - layer-6-artifact
  - shared-architecture
custom_fields:
  document_type: validation-rules
  artifact_type: SYS
  layer: 6
  priority: shared
  development_status: active
---

> **📋 Document Role**: This is the **POST-CREATION VALIDATOR** for SYS documents.
> - Apply these rules after SYS creation or modification
> - **Authority**: Validates compliance with `SYS-TEMPLATE.md` (the primary standard)
> - **Scope**: Use for quality gates before committing SYS changes

# SYS Validation Rules Reference

**Version**: 1.0
**Date**: 2025-11-19
**Last Updated**: 2025-11-19
**Purpose**: Complete validation rules for SYS documents
**Script**: `scripts/validate_sys_template.sh`
**Primary Template**: `SYS-TEMPLATE.md`
**Framework**: doc_flow SDD (100% compliant)
**Changes**: Added REQ-ready scoring validation system

---

## Table of Contents

1. [Overview](#overview)
2. [Validation Checks](#validation-checks)
3. [Error Fix Guide](#error-fix-guide)
4. [Quick Reference](#quick-reference)
5. [Common Mistakes](#common-mistakes)

---

## Overview

The SYS validation script ensures system requirements meet quality standards for REQ progression and implement ADR architectural decisions.

### Validation Tiers

| Tier | Type | Exit Code | Description |
|------|------|-----------|-------------|
| **Tier 1** | Errors | 1 | Blocking issues - must fix before commit |
| **Tier 2** | Warnings | 0 | Quality issues - recommended to fix |
| **Tier 3** | Info | 0 | Informational - no action required |

### Reserved ID Exemption (SYS-000_*)

**Scope**: Documents with reserved ID `000` are FULLY EXEMPT from validation.

**Pattern**: `SYS-000_*.md`

**Document Types**:
- Index documents (`SYS-000_index.md`)
- Traceability matrix templates (`SYS-000_TRACEABILITY_MATRIX-TEMPLATE.md`)
- Glossaries, registries, checklists

**Rationale**: Reserved ID 000 documents are framework infrastructure (indexes, templates, reference materials), not project artifacts requiring traceability or quality gates.

**Validation Behavior**: Skip all checks when filename matches `SYS-000_*` pattern.

---

## Validation Checks

### CHECK 1: Required Document Control Fields

**Type**: Error (blocking)

**Required Fields**:
- Status, Version, Date Created/Last Updated, Author, Reviewers, Owner, Priority
- EARS-Ready Score, REQ-Ready Score

### CHECK 2: ADR Compliance Validation

**Purpose**: Ensure SYS requirements are implementable within ADR architectural boundaries
**Type**: Error (blocking)

**Requirements**:
- Technology selections match ADR decisions
- Architectural patterns align with ADR specifications
- Performance targets meet ADR scalability requirements

### CHECK 3: REQ-Ready Score Validation ⭐ NEW

**Purpose**: Validate REQ-ready score format and threshold
**Type**: Error (blocking)

**Valid Examples**: `✅ 95% (Target: ≥90%)`

**Error Message**: `❌ MISSING: REQ-Ready Score with ✅ emoji and percentage`

### CHECK 4: Quality Attribute Quantification

**Purpose**: Verify all quality attributes are measurable
**Type**: Error (blocking)

**Requirements**:
- Performance quality attributes include percentiles and thresholds
- Reliability quality attributes specify uptime/SLA targets
- Security/compliance quality attributes reference specific standards

### CHECK 5: System Boundaries

**Purpose**: Validate system boundaries prevent requirement bleed
**Type**: Warning

**Requirements**:
- Included capabilities clearly defined
- Excluded capabilities explicitly documented
- Acceptance/failure scopes specified

### CHECK 6: Interface Specifications

**Purpose**: Ensure interface contracts are CTR-ready
**Type**: Warning

**Requirements**:
- External APIs defined with contract details
- Internal interfaces specified with data formats
- Data exchange protocols documented

### CHECK 7: Upstream Traceability

**Purpose**: Verify complete traceability to requirements source
**Type**: Warning

**Required Tags**:
```markdown
@brd: BRD.NN.EE.SS
@prd: PRD.NN.EE.SS
@ears: EARS.NN.EE.SS
@bdd: BDD.NN.EE.SS
@adr: ADR-NN
```

---

### CHECK 8: Element ID Format Compliance ⭐ NEW

**Purpose**: Verify element IDs use unified 4-segment format, flag removed patterns.
**Type**: Error

| Check | Pattern | Result |
|-------|---------|--------|
| Valid format | `### SYS.NN.TT.SS:` | ✅ Pass |
| Removed pattern | `### FR-XXX` | ❌ Fail - use SYS.NN.01.SS |
| Removed pattern | `### QA-XXX` | ❌ Fail - use SYS.NN.02.SS |
| Removed pattern | `### UC-XXX` | ❌ Fail - use SYS.NN.11.SS |
| Removed pattern | `### SR-XXX` | ❌ Fail - use SYS.NN.26.SS |

**Regex**: `^###\s+SYS\.[0-9]{2,}\.[0-9]{2,}\.[0-9]{2,}:\s+.+$`

**Common Element Types for SYS**:
| Element Type | Code | Example |
|--------------|------|---------|
| Functional Requirement | 01 | SYS.02.01.01 |
| Quality Attribute | 02 | SYS.02.02.01 |
| Use Case | 11 | SYS.02.11.01 |
| System Requirement | 26 | SYS.02.26.01 |

**Fix**: Replace `### SR-01: System Requirement` with `### SYS.02.26.01: System Requirement`

**Reference**: SYS_CREATION_RULES.md Section 4.1, ID_NAMING_STANDARDS.md lines 783-793

---

## Error Fix Guide

### Quick Fix Matrix

| Error Check | Quick Fix |
|-------------|-----------|
| **CHECK 1** | Add missing Document Control fields |
| **CHECK 2** | Align SYS requirements with ADR decisions |
| **CHECK 3** | Add properly formatted REQ-Ready Score |
| **CHECK 4** | Quantify all quality attributes with measurable thresholds |
| **CHECK 8** | Replace legacy element IDs (FR-XXX, QA-XXX, SR-XXX) with unified format `SYS.NN.TT.SS` |

---

## Quick Reference

### Pre-Commit Validation

```bash
# Validate single SYS document
./scripts/validate_sys_template.sh docs/SYS/SYS-01_system_requirements.md

# Validate all SYS files
find docs/SYS -name "SYS-*.md" -exec ./scripts/validate_sys_template.sh {} \;
```

### REQ-Ready Scoring Criteria ⭐ NEW

**Requirements Decomposition Clarity (35%)**:
- System boundaries with acceptance/failure scopes: 15%
- Functional requirements broken to implementable capabilities: 10%
- Dependencies and prerequisites identified: 5%
- ADR architectural alignment: 5%

**Quality Attribute Quantification (30%)**:
- Performance with percentiles and thresholds: 15%
- Reliability with uptime/SLA targets: 5%
- security with compliance framework references: 5%
- Scalability quantified for growth: 5%

**Interface Specifications (20%)**:
- External API contracts (CTR-ready): 10%
- Internal module interfaces specified: 5%
- Data exchange protocols documented: 5%

**Implementation Readiness (15%)**:
- Testing requirements for all categories: 5%
- Deployment and operational requirements: 5%
- Monitoring and observability quantified: 5%

### Validation Tiers Summary

| Tier | Type | Checks | Action |
|------|------|--------|--------|
| **Tier 1** | Error | 1-4 | Must fix before commit |
| **Tier 2** | Warning | 5-7 | Recommended to fix |
| **Tier 3** | Info | - | No action required |

---

## Common Mistakes

### Mistake #1: ADR Non-Compliance
```
❌ SYS specifies MongoDB when ADR selected PostgreSQL
✅ Align SYS technology selections with ADR decisions
```

### Mistake #2: Unquantified Quality Attributes
```
❌ System shall be highly available
✅ System shall maintain 99.9% uptime during business hours
```

### Mistake #3: REQ-Ready Score Format
```
❌ REQ-Ready Score: 95%
✅ REQ-Ready Score: ✅ 95% (Target: ≥90%)
```

### Mistake #4: Incomplete Traceability
```
❌ @brd: BRD-01
✅ @brd: BRD.01.01.30, @prd: PRD.03.01.02
```

---

**Maintained By**: Systems Architecture Team, Requirements Engineering Team
## Functional Requirements
