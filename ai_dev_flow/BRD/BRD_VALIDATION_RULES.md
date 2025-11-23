---
title: "BRD Validation Rules Reference"
tags:
  - validation-rules
  - layer-1-artifact
  - shared-architecture
custom_fields:
  document_type: validation-rules
  artifact_type: BRD
  layer: 1
  priority: shared
  development_status: active
---

# BRD Validation Rules Reference

**Version**: 1.1.0
**Date**: 2025-11-19
**Last Updated**: 2025-11-19
**Purpose**: Complete validation rules for BRD documents
**Script**: `scripts/validate_brd_template.sh`
**Primary Template**: `BRD-TEMPLATE.md`
**Framework**: doc_flow SDD (100% compliant)
**Changes**: Updated Platform vs Feature validation logic, clarified section requirements

---

## Table of Contents

1. [Overview](#overview)
2. [Validation Checks](#validation-checks)
3. [Error Fix Guide](#error-fix-guide)
4. [Quick Reference](#quick-reference)
5. [Common Mistakes](#common-mistakes)

---

## Overview

The BRD validation script (`validate_brd_template.sh`) performs **12 validation checks** to ensure compliance with:

- **BRD-TEMPLATE.md**: Complete business requirements structure
- **doc_flow SDD Framework**: Business-driven SDD methodology
- **Platform vs Feature BRD**: Different validation requirements by type
- **Business Requirements Quality**: Measurable objectives, acceptance criteria, strategic alignment

### Validation Tiers

| Tier | Type | Exit Code | Description |
|------|------|-----------|-------------|
| **Tier 1** | Errors | 1 | Blocking issues - must fix before commit |
| **Tier 2** | Warnings | 0 | Quality issues - recommended to fix |
| **Tier 3** | Info | 0 | Informational - no action required |

---

## Validation Checks

### CHECK 1: Required Sections

**Purpose**: Verify all 17 mandatory sections exist
**Type**: Error (blocking)

**Required Sections**:
```markdown
## 1. Introduction
## 2. Business Objectives
## 3. Project Scope
## 4. Functional Requirements
## 5. Non-Functional Requirements
## 6. Assumptions and Constraints
## 7. Acceptance Criteria
## 8. [RESOURCE_INSTANCE - e.g., capacity planning, quota management]
## 9. Implementation Approach
## 10. Training and Change Management
## 11. Support and Maintenance
## 12. Cost-Benefit Analysis
## 13. Project Governance
## 14. Quality Assurance
## 15. Glossary
## 16. Appendices
## Document Control (must be at top)
```

**Note**: Section 8 is "[RESOURCE_INSTANCE - e.g., capacity planning, quota management]" - replace with project-specific resource type

**Error Message**:
```
❌ MISSING: ## 2. Business Objectives
```

**Fix**:
1. Add missing section header
2. Ensure exact spelling and numbering
3. Sections 1-16 must be in order (Document Control at top)

---

### CHECK 2: Document Control Fields

**Purpose**: Validate metadata table at top of document (before numbered sections)
**Type**: Error (blocking)

**Required Fields** (7 total - BRD v1.1 enhancement):
- Project Name
- Document Version
- Date
- Document Owner
- Prepared By
- Status
- PRD-Ready Score (⭐ NEW - v1.1)

**Error Message**:
```
❌ MISSING: Document Owner
❌ MISSING: Prepared By
❌ MISSING: PRD-Ready Score
❌ MISSING: Status
❌ MISSING: PRD-Ready Score
```

**Fix**:
```markdown
| Item | Details |
|------|---------|
| **Project Name** | [Enter project name] |
| **Document Version** | [e.g., 1.0] |
| **Date** | [Current date] |
| **Document Owner** | [Name and title] | |
| **PRD-Ready Score** | ✅ 95% (Target: ≥90%)
```

---

### CHECK 3: Document Revision History

**Purpose**: Verify revision history table exists and has initial entry
**Type**: Error (blocking)

**Requirements**:
1. At least 1 entry in revision history table
2. Table includes Version, Date, Author, Changes Made, Approver columns

**Error Message**:
```
❌ MISSING: Document Revision History entries
```

**Fix**:
```markdown
### Document Revision History

| Version | Date | Author | Changes Made | Approver |
|---------|------|--------|--------------|----------|
| 1.0 | [Current date] | [Author name] | Initial draft | |
```

---

### CHECK 4: Filename/ID Format Validation

**Purpose**: Validate filename matches BRD naming standards
**Type**: Error (blocking)

**Valid Examples**:
- `BRD-001_platform_architecture_technology_stack.md` ✅
- `BRD-006_b2c_progressive_kyc_onboarding.md` ✅
- `BRD-009-01_broker_integration_prerequisites.md` ✅

**Invalid Examples**:
- `BRD-001.md` ❌ (missing description)
- `brd-001_platform.md` ❌ (wrong case)
- `BRD001_platform.md` ❌ (missing hyphen)
- `BRD-001_Platform_Architecture.md` ❌ (uppercase in slug)

**Pattern**: `BRD-[0-9]{3,4}(-[0-9]{2,3})?_[a-z0-9_]+\.md`

**Error Messages**:
```
❌ ERROR: Invalid filename format: brd-001_platform.md
         Expected: BRD-NNN_descriptive_title.md or BRD-NNN-YY_descriptive_title.md

❌ ERROR: Filename doesn't match Platform or Feature BRD pattern
         Platform: BRD-NNN_platform_* or BRD-NNN_infrastructure_*
         Feature: BRD-NNN_{feature_name}
```

**Fix**:
1. Rename file to match Platform (`BRD-NNN_platform_*`) or Feature (`BRD-NNN_{feature_name}`) pattern
2. Use lowercase with underscores for descriptive title

**Reference**: `BRD_CREATION_RULES.md` Section 4 (ID and Naming Standards)

---

### CHECK 5: Platform vs Feature BRD Type Validation

**Purpose**: Validate BRD follows correct template for its type
**Type**: Error (blocking)

**Platform BRD Requirements**:
- Filename contains "platform" or "infrastructure"
- Section 3.6: MUST exist and define foundational technology stacks/prerequisites
- Section 3.7: MUST exist and define mandatory technical constraints

**Feature BRD Requirements**:
- Filename does NOT contain "platform" or "infrastructure"
- Section 3.6: MUST exist and reference Platform BRD dependencies
- Section 3.7: MUST exist and include platform-inherited conditions plus feature-specific requirements

**General Requirements** (Both types):
- Section 3.6: MUST be present and populated with appropriate content
- Section 3.7: MUST be present and populated with appropriate content

**Error Message**:
```
❌ ERROR: Platform BRD missing required Section 3.6 (Technology Stack Prerequisites)
❌ ERROR: Platform BRD missing required Section 3.7 (Mandatory Technology Conditions)
❌ ERROR: Feature BRD missing required Section 3.6 (Technology Stack Prerequisites)
❌ ERROR: Feature BRD missing required Section 3.7 (Mandatory Technology Conditions)
```

**Fix**:
1. Ensure both sections 3.6 and 3.7 exist for all BRD types
---

### CHECK 6: Architecture Decision Requirements Section

**Purpose**: Verify Section 5.2 exists and has required structure
**Type**: Error (blocking)

**Requirements**:
1. Section 5.2 "Architecture Decision Requirements" exists
2. Contains table with columns: Topic Area, Decision Needed, Business Driver, Key Considerations
3. At least 3 architectural topics identified

**Error Message**:
```
❌ MISSING: Section 5.2 Architecture Decision Requirements
❌ ERROR: Section 5.2 missing required table structure (Topic Area, Decision Needed, Business Driver, Key Considerations)
❌ ERROR: Section 5.2 must identify at least 3 architectural topics
```

**Fix**:
```markdown
## 5.2 Architecture Decision Requirements

| Topic Area | Decision Needed | Business Driver | Key Considerations |
|------------|-----------------|---------------|-------------------|
| Multi-Agent Framework | Select orchestration approach | BO-003: Autonomous execution | Google ADK, n8n, custom |
| Data Storage | Choose persistence technology | NFR: High availability | PostgreSQL, Cloud SQL, Firestore |
| Communication Protocol | Select inter-system messaging | FR-015: Real-time updates | Pub/Sub, gRPC, REST WebSocket |
```

**Reference**: `BRD_CREATION_RULES.md` Section 9 (Architecture Decision Requirements)

---

### CHECK 7: Business Objectives SMART Validation

**Purpose**: Verify business objectives follow SMART criteria
**Type**: Warning

**SMART Criteria**:
- **Specific**: Clear, explicit goals
- **Measurable**: Quantifiable metrics and targets
- **Achievable**: Realistic within constraints
- **Relevant**: Aligns with strategy
- **Time-bound**: Specific completion dates

**Validation Pattern**: Each objective must include quantifiable elements

**Warning Messages**:
```
⚠️  WARNING: Business objective missing measurable target: "Improve system performance"
⚠️  WARNING: Business objective missing time-bound criteria: "Increase revenue"
⚠️  WARNING: Business objectives should include quantifiable metrics (e.g., "50%", "$5M", "5 seconds")
```

**Fix**:
```markdown
BO-003: Reduce transaction processing time from 10 seconds to 5 seconds (50% improvement) within 6 months of implementation, enabling <2-second competitive response times as specified in integrated_strategy_algo_v5.md Section 4.2.
```

**Reference**: `BRD_CREATION_RULES.md` Section 10 (Business Objectives and Success Criteria)

---

### CHECK 8: Acceptance Criteria Format

**Purpose**: Verify acceptance criteria are measurable and business-focused
**Type**: Warning

**Requirements**:
1. Business Acceptance Criteria (8.1) includes quantifiable success measures
2. Functional Acceptance Criteria (8.2) maps to specific FR-XXX requirements
3. Success Metrics and KPIs (8.7) include baseline, target, measurement frequency, owner

**Warning Messages**:
```
⚠️  WARNING: Business acceptance criteria missing quantifiable measures
⚠️  WARNING: Functional acceptance criteria not mapped to specific FR-XXX IDs
⚠️  WARNING: Success metrics table missing owners or measurement frequency
```

**Fix**:
```markdown
**AC-001:** System must process 1,000 transactions per minute with <5% error rate, measured over 30-day production period.

| KPI | Baseline | Target | Measurement Frequency | Method | Owner |
|-----|----------|--------|----------------------|---------|-------|
| Transaction Throughput | 500/min | 1,000/min | Daily | Monitoring dashboard | Operations Manager |
| Error Rate | 10% | <5% | Hourly | Error logs | QA Manager |
```

**Reference**: `BRD_TEMPLATE.md` Section 8 (Acceptance Criteria)

---

### CHECK 9: ADR Reference Validation

**Purpose**: Ensure BRD does NOT reference specific ADR numbers (forward reference prevention)
**Type**: Error (blocking)

**Prohibited References**:
- `ADR-XXX`, `ADR-012`, `ADR-033` ❌
- Links to ADR files ❌
- Specific ADR numbers in any context ❌

**Allowed References**:
- "Architecture Decision Requirements" section ✅
- Generic references to future ADR process ✅

**Error Message**:
```
❌ ERROR: BRD must not reference specific ADR numbers (ADR-XXX)
         BRDs are created BEFORE ADRs - only identify decision topics in Section 5.2
         Found: ADR-033_risk_architecture.md
```

**Fix**:
1. Remove any ADR-NNN references
2. Ensure ADR references are only in Section 5.2 as topic identification
3. Add ADR references AFTER BRD approval when ADRs are created

**Reference**: `BRD_CREATION_RULES.md` Section 7 (ADR Relationship Guidelines)

---

### CHECK 10: Strategy Document Traceability

**Purpose**: Verify BRD includes strategic business references
**Type**: Warning

**Requirements**:
1. References to `option_strategy/` documents
2. Specific sections in strategy documents
3. Business rationale for each major requirement

**Warning Messages**:
```
⚠️  WARNING: Business objective missing strategy document reference
⚠️  WARNING: No references to option_strategy/ documents found
⚠️  WARNING: Strategic alignment references should include specific sections
```

**Fix**:
```markdown
- **Strategic Context**: Aligns with objectives in `option_strategy/integrated_strategy_algo_v5.md` Section 4.2 (Portfolio Risk Management)
- **Performance Targets**: Matches targets defined in `option_strategy/README.md` Section 2.1 (Benchmark Performance Goals)
- **Business Rationale**: Enables algorithmic trading execution as specified in `option_strategy/Integrated_strategy_desc.md` Section 3.4
```

**Reference**: `BRD_CREATION_RULES.md` Section 8 (Traceability Requirements)

---

### CHECK 11: Markdown Link Resolution

**Purpose**: Validate all cross-reference links resolve to existing files
**Type**: Error + Warning

**Valid Link Format**:
```markdown
[PRD-001 Product Requirements](../PRD/PRD-001_product_requirements.md)
[BRD-001 Platform Architecture](./BRD-001_platform_architecture.md)
```

**Invalid Examples**:
```markdown
[PRD-001](../../PRD/PRD-001.md) ❌ (missing relative path)
[BRD-999](../../BRD/BRD-999.md) ❌ (file doesn't exist)
```

**Error Message** (blocking):
```
❌ ERROR: Broken link - file not found
         Link: ../../PRD/PRD-999_product_requirements.md
         Resolved: /opt/data/docs_flow_framework/docs/PRD/PRD-999_product_requirements.md
```

**Warning Message**:
```
⚠️  WARNING: Link exists but anchor missing: #BO-001 not found in target document
```

**Fix**:
1. Verify file exists at specified path
2. Use correct relative path from current BRD location
3. Ensure anchors (#ID) exist in target document

---

### CHECK 12: Out-of-Scope Clarity

**Purpose**: Verify project boundaries are clearly defined
**Type**: Warning

**Requirements**:
1. Section 3.3 Out-of-Scope Items exists and is non-empty
2. Includes rationale for exclusion
3. Prevents scope creep expectations

**Warning Messages**:
```
⚠️  WARNING: Out-of-scope items section is minimal or empty
⚠️  WARNING: Out-of-scope items missing clear rationale
⚠️  WARNING: Critical business functions not explicitly included/excluded
```

**Fix**:
```markdown
### 3.3 Out-of-Scope Items

1. **Legacy System Migration**: Complete replacement of existing IB Gateway infrastructure - excluded due to 6-month migration timeline conflict with phased rollout approach
2. **Mobile Application Development**: Native iOS/Android apps - excluded as desktop trading terminal capabilities sufficient for initial release
3. **Multi-Asset Trading Support**: Crypto, forex, options - excluded to focus on cash equities as core competency
```

**Reference**: `BRD_TEMPLATE.md` Section 3.3 (Out-of-Scope Items)

---

### CHECK 13: PRD-Ready Score Validation ⭐ NEW

**Purpose**: Validate PRD-Ready Score format and threshold (BRD v1.1 enhancement)
**Type**: Error (blocking) - Required for BRD documents

**Valid Examples**:
- `✅ 95% (Target: ≥90%)` ✅
- `✅ 92% (Target: ≥90%)` ✅

**Invalid Examples**:
- `95%` ❌
- `✓ 95%` ❌
- `High` ❌

**Error Message** (format):
```
❌ MISSING: PRD-Ready Score with ✅ emoji and percentage
```

**Warning Message** (threshold):
```
⚠️  WARNING: PRD-Ready Score below 90%: 85%
```

**Scoring Criteria** (PRD Readiness Assessment):

**Business Requirements Completeness (40%)**:
- All 17 sections present and populated: 10%
- Business objectives follow SMART criteria: 10%
- Acceptance criteria quantifiable and verifiable: 10%
- Stakeholder analysis complete: 10%

**Technical Readiness (30%)**:
- Section 3.6 & 3.7 properly populated by BRD type: 10%
- Section 5.2 Architecture Decision Requirements table: 10%
- No forward ADR references: 10%

**Quality Standards (20%)**:
- Document control complete: 5%
- Strategic alignment with option_strategy/ documents: 5%
- Cross-references resolve correctly: 5%
- Out-of-scope clearly defined: 5%

**Traceability (10%)**:
- Proper ID formats and links: 5%
- Business rationale provided: 5%

**Fix**: Calculate and update score based on readiness criteria

---

## Error Fix Guide

### Quick Fix Matrix

| Error Check | Quick Fix |
|-------------|-----------|
| **CHECK 1** | Add missing section: `## N. Section Title` |
| **CHECK 2** | Add all 6 required fields to Document Control table |
| **CHECK 3** | Add initial entry to Document Revision History table |
| **CHECK 4** | Rename file to Platform (`BRD-NNN_platform_*`) or Feature (`BRD-NNN_{feature_name_name}`) pattern |
| **CHECK 5** | Enssctod 3.7 exit wtand h apexistpwith apprtpriat cten B  type
| **CHECK 6** | Add Section 5.2 with table structure and at least 3 architectural topics |
| **CHECK 9** | Remove ADR-NNN references; ensure ADRs only identified as topics in Section 5.2 |
| **CHECK 11** | Fix broken links, use relative paths, verify target files exist |

---

## Quick Reference

### Pre-Commit Validation

```bash
# Validate single file
./scripts/validate_brd_template.sh docs/BRD/BRD-001_platform_architecture.md

# Validate all BRD files
**Business Requirements Completeness (40%)**:
- All 17 sections present and populated: 10%
- Business objectives follow SMART criteria: 10%
- Acceptance criteria quantifiable and verifiable: 10%
- Stakeholder analysis complete: 10%

**Technical Readiness (30%)**:
- Section 3.6 & 3.7 properly populated by BRD type: 10%
- Section 5.2 Architecture Decision Requirements table: 10%
- No forward ADR references: 10%

**Quality Standards (20%)**:
- Document control complete: 5%
- Strategic alignment with option_strategy/ documents: 5%
- Cross-references resolve correctly: 5%
- Out-of-scope clearly defined: 5%

**Traceability (10%)**:
- Proper ID formats and links: 5%
- Business rationale provided: 5%

**Failure**:
```
❌ FAILED: 3 critical errors found

Errors: 3
Warnings: 1
```

### Validation Tiers Summary

| Tier | Checks | Type | Action |
|------|--------|------|--------|
| **Tier 1** | 1, 2, 3, 4, 5, 6, 9, 11 | Error | Must fix before commit |
| **Tier 2** | 7, 8, 10, 12 | Warning | Recommended to fix |
| **Tier 3** | - | Info | No action required |

---

## Common Mistakes

### Mistake #1: Missing Document Control Fields

**Error**:
```
❌ MISSING: Document Owner
❌ MISSING: Prepared By
❌ MISSING: Status
```

**Cause**: Incomplete Document Control table

**Fix**:
```markdown
| Item | Details |
|------|---------|
| **Project Name** | Trading Platform Enhancement |
| **Document Version** | 1.0 |
| **Date** | 2025-11-19 |
| **Document Owner** | Jane Smith, VP Product Management |
| **Prepared By** | Business Analyst Team |
| **Status** | Draft |
```

---

### Mistake #2: Invalid Filename Format

**Error**:
```
❌ ERROR: Invalid filename format: BRD-001.md
         Expected: BRD-NNN_descriptive_title.md
```

**Cause**: Missing descriptive title slug or Platform/Feature pattern

**Fix**: Rename file to match appropriate pattern:
- Platform: `BRD-001_platform_architecture_technology_stack.md`
- Feature: `BRD-006_b2c_progressive_kyc_onboarding.md`

---

### Mistake #3: Missing Architecture Decision Requirements

**Error**:
```
❌ MISSING: Section 5.2 Architecture Decision Requirements
❌ ERROR: Section 5.2 must identify at least 3 architectural topics
```

**Cause**: Missing required section or empty/inadequate table

**Fix**:
```markdown
## 5.2 Architecture Decision Requirements

| Topic Area | Decision Needed | Business Driver | Key Considerations |
|------------|-----------------|---------------|-------------------|
| Database Technology | Select data storage solution | NFR-001: High availability requirements | PostgreSQL, Cloud SQL, DynamoDB |
| Authentication | Choose identity management | FR-003: Secure user access | OAuth2, SAML, Firebase Auth |
| API Architecture | Define service communication | FR-015: System integration | REST APIs, gRPC, GraphQL |
```

---

### Mistake #4: Forward ADR References

**Error**:
```
❌ ERROR: BRD must not reference specific ADR numbers (ADR-XXX)
         Found: ADR-033_risk_architecture.md
```

**Cause**: BRD referencing ADRs that don't exist yet

**Fix**:
1. Remove ADR-NNN references
2. Convert to topic identification in Section 5.2
3. Add ADR links AFTER BRD approval when ADRs are created

---

### Mistake #5: Platform BRD Missing Technology Sections

**Error**:
```
❌ ERROR: Platform BRD missing required Section 3.6 (Technology Stack Prerequisites)
❌ ERROR: Platform BRD missing required Section 3.7 (Mandatory Technology Conditions)
```

**Cause**: Platform BRD filename pattern but missing required technology sections

**Fix**:
1. Add Section 3.6 with technology prerequisites
2. Add Section 3.7 with mandatory technology conditions
3. Include business impact analysis for each prerequisite

---

### Mistake #6: Business Objectives Not SMART

**Warning**:
```
⚠️  WARNING: Business objective missing measurable target: "Improve system performance"
⚠️  WARNING: Business objective missing time-bound criteria: "Increase revenue"
```

**Cause**: Business objectives not following SMART criteria

**Fix**:
```markdown
BO-003: Reduce average order processing time from current 10 seconds to 5 seconds (50% improvement), measured by 95th percentile response time, within 6 months of implementation to match competitive trading platforms.
```

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2025-11-19 | Initial validation rules for BRD documents | System Architect |

---

**Maintained By**: Business Analyst Team, Quality Assurance Team
**Review Frequency**: Updated with BRD template enhancements
**Support**: See [BRD-TEMPLATE.md](../BRD/BRD-TEMPLATE.md) for comprehensive template guidance
