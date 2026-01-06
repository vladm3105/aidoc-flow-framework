---
title: "Platform vs Feature BRDs - Quick Reference"
tags:
  - framework-guide
  - shared-architecture
custom_fields:
  document_type: guide
  priority: shared
  development_status: active
---

# Platform vs Feature BRDs - Quick Reference

## Overview

BRDs fall into two categories based on their focus. Both use the same template (BRD-TEMPLATE.md) but with different emphasis on technology prerequisites.

## Platform BRDs

**Purpose**: Define infrastructure, architecture, and technology stack requirements

**Characteristics**:
- Focus on **business drivers** for technology decisions
- Include "Technology Stack Prerequisites" section (populated)
- List required ADRs in "Mandatory Technology Conditions"
- Document **why** technology decisions are critical to business success

**Examples**:
- BRD-01: Platform Architecture & Technology Stack
- BRD-34: ML Infrastructure Technology Decisions
- BRD-50: Mobile Architecture Technology Stack

**Workflow**:
```
Platform BRD → PRD → EARS → BDD → ADR → SPEC
```

**Key sections**:
- section 3.6: Technology Stack Prerequisites (REQUIRED)
- section 3.7: Mandatory Technology Conditions (REQUIRED - identify architecture decision topics; do not reference ADR numbers)

## Feature BRDs

**Purpose**: Define business features, user workflows, and functional requirements

**Characteristics**:
- Focus on **business objectives** and **user needs**
- May reference Platform BRD technology prerequisites
- "Technology Stack Prerequisites" section usually empty or references Platform BRD
- Document **what** features deliver business value

**Examples**:
- BRD-06: B2C Progressive Identity Verification Onboarding
- BRD-09: Remittance Transaction Workflow
- BRD-22: Fraud Detection Agent

**Workflow**:
```
Feature BRD → PRD → EARS → BDD → ADR (if needed) → SPEC
```

**Key sections**:
- section 3.6: Technology Stack Prerequisites (OPTIONAL - may reference Platform BRD)
- section 3.7: Mandatory Technology Conditions (Usually empty)

## Decision Tree

**Ask**: What is the primary focus of this BRD?

### Infrastructure/Architecture?
→ **Platform BRD**
- Populate "Technology Stack Prerequisites"
- Identify architecture decision topics (ADRs authored after BDD; no forward ADR references)
- Document business drivers for technology

### Business Functionality?
→ **Feature BRD**
- Reference Platform BRD if technology constraints exist
- Standard workflow: BRD → PRD → EARS → BDD → ADR
- Focus on user value and business outcomes

### Both?
→ **Create Platform BRD first**, then Feature BRDs
- Platform BRD establishes technology foundation
- Feature BRDs reference Platform BRD prerequisites
- Clear separation of concerns

## Naming Conventions

**Platform BRDs**:
- `BRD-01_platform_architecture_technology_stack.md`
- `BRD-34_ml_infrastructure_technology_decisions.md`
- `BRD-50_mobile_platform_architecture.md`

**Feature BRDs**:
- `BRD-06_b2c_progressive_kyc_onboarding.md`
- `BRD-09_remittance_transaction_workflow.md`
- `BRD-22_fraud_detection_agent.md`

## Workflow Comparison

| Aspect | Platform BRD | Feature BRD |
|--------|--------------|-------------|
| **Focus** | Technology/architecture | Business/user features |
| **Prerequisites** | Defines technology requirements | References Platform BRD |
| **ADR Timing** | Before PRD (critical decisions) | After PRD (implementation details) |
| **Example** | BRD-01 | BRD-06 |
| **Next Step** | Create ADRs first | Create PRD first |

## section 3.6 & 3.7 Implementation Guide

### Platform BRD: section 3.6 Example (Technology Stack Prerequisites)

**Required**: Populate with detailed prerequisites organized by category

```markdown
### 3.6 Technology Stack Prerequisites

**Platform BRDs Only** - *Skip this section for Feature BRDs*

**Core Platform Technologies**:

1. **PostgreSQL 14+ Database**
   - **Requirement**: PostgreSQL 14 or later with ACID compliance, replication configured
   - **Rationale**: Required for transactional consistency in user profiles, transaction state, audit logs (ADR-02)
   - **Business Impact**: Without PostgreSQL, data integrity guarantees for financial transactions not possible

2. **Node.js 18+ LTS Runtime**
   - **Requirement**: Node.js 18 LTS or later with TypeScript 5.x support
   - **Rationale**: Required for backend payment orchestrator, funds router, quote service (ADR-01)
   - **Business Impact**: Without Node.js async I/O, <2s API response time targets unachievable

**Partner Integration Prerequisites**:

3. **Partner X API Access**
   - **Requirement**: Active partnership with API credentials, service level agreement signed
   - **Rationale**: Required for critical platform capability Y
   - **Business Impact**: Without Partner X, platform cannot deliver core value proposition
```

### Platform BRD: section 3.7 Example (Mandatory Technology Conditions)

**Required**: Populate with non-negotiable constraints organized by category

```markdown
### 3.7 Mandatory Technology Conditions

**Platform BRDs Only** - *Skip this section for Feature BRDs*

**Regulatory & Compliance Constraints**:

1. **Double-Entry Accounting Ledger**
   - **Condition**: All financial transactions MUST use double-entry accounting with immutable journal entries
   - **Rationale**: Required for SOC 2 Type II compliance, regulatory audit trails, proof-of-reserves validation
   - **Business Impact**: Without double-entry accounting, platform fails financial audits; regulatory penalties apply
   - **Exception Path**: Alternative ledger system allowed if meets same compliance requirements (requires ADR)

**Business Model Constraints**:

2. **Stablecoin Payment Rails**
   - **Condition**: All cross-border transfers MUST use stablecoin as intermediary currency
   - **Rationale**: Stablecoin rails enable 5x cost reduction vs traditional correspondent banking
   - **Business Impact**: Without stablecoin rails, cost reduction target unachievable; business model fails
   - **Exception Path**: None - stablecoin rails fundamental to business value proposition
```

### Feature BRD: section 3.6 Example (Reference Platform BRD)

**Required**: Reference Platform BRD instead of duplicating

```markdown
### 3.6 Technology Stack Prerequisites

**N/A - See Platform BRD-01 section 3.6**

This feature BRD assumes all Platform BRD-01 technology prerequisites are satisfied. Specifically:
- Node.js backend services (Platform BRD-01 section 3.6 Item 2)
- PostgreSQL database (Platform BRD-01 section 3.6 Item 1)
- Partner X API integration (Platform BRD-01 section 3.6 Item 3)

No additional technology prerequisites required for this feature.
```

### Feature BRD: section 3.7 Example (Reference Platform BRD)

**Required**: Reference Platform BRD and note any feature-specific constraints

```markdown
### 3.7 Mandatory Technology Conditions

**N/A - See Platform BRD-01 section 3.7**

This feature must comply with all Platform BRD-01 mandatory technology conditions. No feature-specific mandatory conditions beyond platform requirements.

**Note**: Feature design conflicts with Platform BRD-01 section 3.7 Item 2 (stablecoin payment rails) require Platform BRD amendment - consult architecture team before proceeding.
```

## Quick Reference

**Platform BRD Checklist**:
- [ ] Label sections 3.6 and 3.7 with "**Platform BRDs Only** - *Skip this section for Feature BRDs*"
- [ ] Populate section 3.6 with detailed technology prerequisites organized by category
- [ ] Include Requirement, Rationale, Business Impact for each prerequisite
- [ ] Identify architecture decision topics (no ADR numbers; topics listed in section 7.2 of BRD)
- [ ] Populate section 3.7 with mandatory conditions organized by category
- [ ] Include Condition, Rationale, Business Impact, Exception Path for each condition
- [ ] Document business rationale for each technology requirement
- [ ] Create ADRs after BDD (no forward ADR references in BRD)

**Feature BRD Checklist**:
- [ ] Add "**N/A - See Platform BRD-XXX section 3.6**" to section 3.6
- [ ] Reference specific Platform BRD prerequisites relevant to feature
- [ ] Add "**N/A - See Platform BRD-XXX section 3.7**" to section 3.7
- [ ] Note any feature-specific constraints beyond platform requirements
- [ ] Focus on business value and user workflows (sections 2, 5)
- [ ] Proceed to PRD creation after BRD approval
- [ ] Create ADRs after BDD if needed (no forward ADR references in BRD)

## Common Mistakes to Avoid

### ❌ Platform BRD Mistakes

1. **Empty sections 3.6/3.7**: Platform BRDs must populate both sections
2. **Missing "Platform BRDs Only" Label**: Feature BRD authors won't know to skip
3. **No Business Impact**: Must explain consequence of missing each prerequisite
4. **Missing Exception Paths**: section 3.7 must state exception conditions or "None"

### ❌ Feature BRD Mistakes

1. **Duplicating Prerequisites**: Feature BRDs should reference Platform BRD, not duplicate
2. **Populating sections 3.6/3.7**: Feature BRDs use "N/A - See Platform BRD-XXX"
3. **Not Referencing Platform BRD**: Must explicitly state Platform BRD dependency
4. **Creating ADRs Before PRD**: Feature BRDs create ADRs during implementation, not before

---

**See Also**:
- [BRD-TEMPLATE.md](./BRD/BRD-TEMPLATE.md) - Standard template for both types
- [BRD/README.md](./BRD/README.md) - BRD documentation guidelines
- [ADR/README.md](./ADR/README.md) - Architecture decision record creation
<!-- VALIDATOR:IGNORE-LINKS-START -->
- **Reference Implementation**: [BRD-01](../docs/BRD/BRD-01_platform_architecture_technology_stack.md) - Gold standard Platform BRD with sections 3.6 and 3.7 fully populated
<!-- VALIDATOR:IGNORE-LINKS-END -->
