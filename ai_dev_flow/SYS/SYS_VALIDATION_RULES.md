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

### CHECK 4: NFR Quantification

**Purpose**: Verify all non-functional requirements are measurable
**Type**: Error (blocking)

**Requirements**:
- Performance NFRs include percentiles and thresholds
- Reliability NFRs specify uptime/SLA targets
- security/compliance NFRs reference specific standards

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
@brd: BRD-NNN:REQUIREMENT-ID
@prd: PRD-NNN:REQUIREMENT-ID
@ears: EARS-NNN:STATEMENT-ID
@bdd: BDD-NNN:SCENARIO-ID
@adr: ADR-NNN
```

---

## Error Fix Guide

### Quick Fix Matrix

| Error Check | Quick Fix |
|-------------|-----------|
| **CHECK 1** | Add missing Document Control fields |
| **CHECK 2** | Align SYS requirements with ADR decisions |
| **CHECK 3** | Add properly formatted REQ-Ready Score |
| **CHECK 4** | Quantify all NFRs with measurable thresholds |

---

## Quick Reference

### Pre-Commit Validation

```bash
# Validate single SYS document
./scripts/validate_sys_template.sh docs/SYS/SYS-001_system_requirements.md

# Validate all SYS files
find docs/SYS -name "SYS-*.md" -exec ./scripts/validate_sys_template.sh {} \;
```

### REQ-Ready Scoring Criteria ⭐ NEW

**Requirements Decomposition Clarity (35%)**:
- System boundaries with acceptance/failure scopes: 15%
- Functional requirements broken to implementable capabilities: 10%
- Dependencies and prerequisites identified: 5%
- ADR architectural alignment: 5%

**NFR Quantification (30%)**:
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

### Mistake #2: Unquantified NFRs
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
❌ @brd: BRD-001
✅ @brd: BRD-001:FR-030, @prd: PRD-003:FEATURE-002
```

---

**Maintained By**: Systems Architecture Team, Requirements Engineering Team
## Functional Requirements
