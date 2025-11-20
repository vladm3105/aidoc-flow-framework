# ADR Validation Rules Reference

**Version**: 1.0
**Date**: 2025-11-19
**Last Updated**: 2025-11-19
**Purpose**: Complete validation rules for ADR documents
**Script**: `scripts/validate_adr_template.sh`
**Primary Template**: `ADR-TEMPLATE.md`
**Framework**: doc_flow SDD (100% compliant)
**Changes**: Added SYS-ready scoring validation system

---

## Table of Contents

1. [Overview](#overview)
2. [Validation Checks](#validation-checks)
3. [Error Fix Guide](#error-fix-guide)
4. [Quick Reference](#quick-reference)
5. [Common Mistakes](#common-mistakes)

---

## Overview

The ADR validation script ensures architecture decisions follow quality standards for SYS progression and meet SDD quality gates.

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
- Project Name, Document Version, Date, Document Owner, Prepared By, Status, SYS-Ready Score

### CHECK 2: ADR Structure Completeness

**Type**: Error (blocking)

**Required Sections**: Status, Context, Decision, Consequences, Architecture Flow, Alternatives Considered

### CHECK 3: SYS-Ready Score Validation ⭐ NEW

**Purpose**: Validate SYS-ready score format and threshold
**Type**: Error (blocking)

**Valid Examples**: `✅ 95% (Target: ≥90%)`

**Error Message**: `❌ MISSING: SYS-Ready Score with ✅ emoji and percentage`

### CHECK 4: Upstream Traceability Tags

**Purpose**: Verify complete tag chain through BDD layer
**Type**: Error (blocking)

**Required Tags**:
```markdown
@brd: BRD-NNN:REQUIREMENT-ID
@prd: PRD-NNN:REQUIREMENT-ID
@ears: EARS-NNN:STATEMENT-ID
@bdd: BDD-NNN:SCENARIO-ID
```

### CHECK 5: Decision Quality Assessment

**Purpose**: Ensure decision rationale is comprehensive
**Type**: Warning

**Requirements**:
- Context clearly establishes the problem
- Decision explains chosen solution
- Consequences cover positive and negative outcomes
- Alternatives considered with rejection rationale

### CHECK 6: Architecture Documentation

**Purpose**: Verify technical architecture is well-defined
**Type**: Warning

**Requirements**:
- Architecture flow includes Mermaid diagram
- Component responsibilities specified
- Impact analysis covers affected systems

### CHECK 7: Implementation Readiness

**Purpose**: Assess practical implementability
**Type**: Warning

**Requirements**:
- Complexity assessment provided
- Resource estimates documented
- Migration and rollback strategies included

---

## Error Fix Guide

### Quick Fix Matrix

| Error Check | Quick Fix |
|-------------|-----------|
| **CHECK 1** | Add missing Document Control fields |
| **CHECK 2** | Add required ADR structure sections |
| **CHECK 3** | Add properly formatted SYS-Ready Score |
| **CHECK 4** | Complete traceability tag chain |

---

## Quick Reference

### Pre-Commit Validation

```bash
# Validate single ADR document
./scripts/validate_adr_template.sh docs/ADR/ADR-001_architecture_decision.md

# Validate all ADR files
find docs/ADR -name "ADR-*.md" -exec ./scripts/validate_adr_template.sh {} \;
```

### SYS-Ready Scoring Criteria ⭐ NEW

**Decision Completeness (30%)**:
- Complete decision process (Context/Decision/Consequences/Alternatives): 15%
- Requirements mapping and traceability: 10%
- Impact analysis (positive/negative consequences): 5%

**Architecture Clarity (35%)**:
- Architecture flow with Mermaid diagrams: 15%
- Component responsibilities defined: 10%
- Cross-cutting concerns addressed: 10%

**Implementation Readiness (20%)**:
- Complexity and resource estimates: 10%
- Dependencies identified: 5%
- Rollback/migration strategies: 5%

**Verification Approach (15%)**:
- Testing strategy alignment: 5%
- Success metrics and validation criteria: 5%
- Operational readiness assessment: 5%

### Validation Tiers Summary

| Tier | Type | Checks | Action |
|------|------|--------|--------|
| **Tier 1** | Error | 1-4 | Must fix before commit |
| **Tier 2** | Warning | 5-7 | Recommended to fix |
| **Tier 3** | Info | - | No action required |

---

## Common Mistakes

### Mistake #1: Incomplete Decision Process
```
❌ Missing alternatives considered section
✅ Document evaluated alternatives with rejection rationale
```

### Mistake #2: Vague Architecture Documentation
```
❌ "Use microservices architecture"
✅ "Use event-driven microservices with CQRS pattern for order processing, deployed on Kubernetes with Istio service mesh"
```

### Mistake #3: SYS-Ready Score Format
```
❌ SYS-Ready Score: 95%
✅ SYS-Ready Score: ✅ 95% (Target: ≥90%)
```

### Mistake #4: Missing Traceability Tags
```
❌ @brd: BRD-001
✅ @brd: BRD-001:FR-030, BRD-001:NFR-006
```

---

**Maintained By**: Architecture Team, Quality Assurance Team
**Review Frequency**: Updated with ADR template enhancements
