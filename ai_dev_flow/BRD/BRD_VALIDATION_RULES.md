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

**Error Message** (threshold blocking):
```
❌ ERROR: PRD-Ready Score below minimum threshold: 65/100
Target: ≥90/100
Current score fails to meet business-level content requirements.

See detailed breakdown below for areas requiring improvement.
```

---

**Automated Score Calculation Algorithm**:

The PRD-Ready Score is calculated as: **100 - (Total Deductions)**

**Maximum Possible Deductions: 100 points** (score can go to 0/100)

---

### Scoring Criteria (Deduction-Based System)

#### Category 1: PRD-Level Content Contamination (50 points maximum deduction)

**Code Blocks in FRs** (CHECK 14):
- **Deduction**: -10 points per code block found in Section 4
- **Rationale**: Code blocks (Python, JSON, SQL) are strictly PRD-level implementation
- **Examples**:
  - 1 code block = -10 points
  - 3 code blocks = -30 points
  - 5+ code blocks = -50 points (maximum deduction for this category)

**API/Technical Terminology** (CHECK 15):
- **Deduction**: -2 points per technical term instance (max -20 points)
- **Technical Terms**: POST, GET, JSON, endpoint, request, response, database, query, table, schema
- **Examples**:
  - 5 instances = -10 points
  - 10+ instances = -20 points (maximum)

**UI-Specific Language** (CHECK 16):
- **Deduction**: -2 points per UI term instance (max -20 points)
- **UI Terms**: button, modal, click, dropdown, screen, form, display, panel
- **Examples**:
  - 5 instances = -10 points
  - 10+ instances = -20 points (maximum)

**Category 1 Calculation**:
- Minimum deduction: 0 points (no PRD-level content found)
- Maximum deduction: 50 points (heavy PRD-level contamination)
- **Gold Standard**: BRD-009 has 0 deductions (100% business-level content)

---

#### Category 2: FR Structure Completeness (30 points maximum deduction)

**Missing FR Subsections** (CHECK 17):
- **Deduction**: -5 points per FR missing any required subsection
- **Required Subsections** (6 total):
  1. Business Capability
  2. Business Requirements
  3. Business Rules
  4. Business Acceptance Criteria
  5. Related Requirements
  6. Complexity
- **Examples**:
  - 1 FR missing 2 subsections = -5 points
  - 3 FRs each missing 1 subsection = -15 points
  - 6 FRs with incomplete structure = -30 points (maximum)

**Invalid Cross-References** (CHECK 18):
- **Deduction**: -2 points per invalid BRD reference (max -10 points)
- **Invalid Conditions**: Non-existent BRD file, incorrect ID format (BRD-2 instead of BRD-002)
- **Examples**:
  - 3 invalid references = -6 points
  - 5+ invalid references = -10 points (maximum)

**Category 2 Calculation**:
- Minimum deduction: 0 points (all FRs complete with valid cross-references)
- Maximum deduction: 30 points (incomplete FR structure across multiple requirements)

---

#### Category 3: Document Structure and Quality (20 points maximum deduction)

**Document Control Completeness** (CHECK 2, CHECK 13):
- **Deduction**: -5 points if PRD-Ready Score field missing
- **Deduction**: -3 points if any other Document Control field missing (max -6 points for 2+ missing fields)
- **Required Fields**: Project Name, Document Version, Date, Document Owner, Prepared By, Status, PRD-Ready Score

**Required Sections** (CHECK 1):
- **Deduction**: -1 point per missing section (max -10 points)
- **Required**: All 17 sections from BRD-TEMPLATE.md

**Revision History** (CHECK 3):
- **Deduction**: -3 points if Document Revision History table missing or empty

**Category 3 Calculation**:
- Minimum deduction: 0 points (complete document structure)
- Maximum deduction: 20 points (significant structural gaps)

---

### PRD-Ready Score Calculation Example

**Example BRD Analysis**:
- **Code blocks found**: 2 in Section 4 FRs → -20 points
- **API terms found**: 8 instances (GET, POST, JSON, endpoint) → -16 points
- **UI terms found**: 4 instances (button, modal, click, screen) → -8 points
- **Missing subsections**: 2 FRs each missing Complexity subsection → -10 points
- **Invalid cross-references**: 1 reference to non-existent BRD-099 → -2 points
- **Document Control**: All fields present → 0 points
- **Required Sections**: All 17 sections present → 0 points
- **Revision History**: Table present → 0 points

**Total Deductions**: 20 + 16 + 8 + 10 + 2 = 56 points

**PRD-Ready Score**: 100 - 56 = **44/100** ❌

**Validation Result**: **FAIL** (Target: ≥90/100)

---

**Example Gold Standard (BRD-009)**:
- **Code blocks**: 0 → -0 points
- **API terms**: 0 → -0 points
- **UI terms**: 0 → -0 points
- **Missing subsections**: 0 → -0 points
- **Invalid cross-references**: 0 → -0 points
- **Document Control**: Complete → -0 points
- **Required Sections**: Complete → -0 points
- **Revision History**: Complete → -0 points

**Total Deductions**: 0 points

**PRD-Ready Score**: 100 - 0 = **100/100** ✅

**Validation Result**: **PASS** (Exceeds ≥90/100 target)

---

### Automated Validation Workflow

**Step 1**: Scan BRD document for all CHECK 14-18 violations
**Step 2**: Calculate deductions per category
**Step 3**: Compute final score: 100 - Total Deductions
**Step 4**: Compare against threshold (≥90/100)
**Step 5**: Generate detailed feedback report

**Validation Outcome**:
- **Score ≥90/100**: ✅ PASS - BRD ready for PRD development
- **Score 70-89/100**: ⚠️  WARNING - Moderate PRD-level contamination, refactoring recommended
- **Score <70/100**: ❌ FAIL - Heavy PRD-level contamination, major refactoring required

**Fix**:
1. Run automated validation script: `./scripts/validate_brd.py docs/BRD/BRD-XXX.md`
2. Review detailed deduction report
3. Address violations using BRD-TEMPLATE.md Appendix B (REMOVE/KEEP guidelines)
4. Re-run validation until score ≥90/100
5. Update Document Control with final score

**Reference**: See Phase 5 validation script implementation for automated scoring

---

### CHECK 14: Code Blocks in Functional Requirements ⭐ NEW

**Purpose**: Prevent PRD-level technical implementation from appearing in BRD Functional Requirements
**Type**: Error (blocking) - Code blocks are strictly prohibited in BRD FRs

**Scan Pattern**: Search for triple backticks (```) within Section 4 (Functional Requirements)

**Prohibited Content**:
- ❌ Python/JavaScript/SQL code blocks
- ❌ JSON/YAML/XML schema examples
- ❌ API request/response examples
- ❌ Pseudocode or algorithm implementations
- ❌ Database query examples
- ❌ Configuration file snippets

**Exception**: Business process flowcharts using Mermaid diagrams showing business states only (NOT technical implementation)

**Valid Mermaid Example** (Business States):
```mermaid
graph LR
    A[Customer Initiates] --> B[Compliance Screening]
    B --> C[Transaction Funded]
    C --> D[Delivered to Recipient]
```

**Invalid Code Block Example**:
```python
def calculate_fee(amount):
    if amount > 1000:
        return amount * 0.01
    return amount * 0.02
```

**Error Message**:
```
❌ ERROR: Code block found in Functional Requirements (Section 4)
Line X: ```python (or ```json, ```sql, etc.)

Code blocks are PRD-level content and must be removed from BRDs.
- Business-level alternative: Describe fee structure using table or bullet points
- Technical implementation: Defer to PRD-XXX
```

**Fix**:
1. Remove code block entirely
2. Replace with business-level description (see BRD-TEMPLATE.md Appendix B)
3. Reference technical implementation in Related Requirements (e.g., "Fee calculation algorithm defined in PRD-XXX")

**Reference**: BRD-TEMPLATE.md Appendix B, Edge Case 4 (Code Blocks)

---

### CHECK 15: API/Technical Terminology in Functional Requirements ⭐ NEW

**Purpose**: Prevent technical API/database terminology from appearing in business-level FRs
**Type**: Warning (non-blocking) - Technical terms indicate potential PRD-level contamination

**Scan Pattern**: Search for technical keywords in Section 4 (Functional Requirements)

**Prohibited Technical Terms**:
- **HTTP Methods**: POST, GET, PUT, DELETE, PATCH
- **Data Formats**: JSON, XML, YAML, CSV (when describing API payloads)
- **API Terminology**: endpoint, request, response, payload, header, authentication token
- **Database Terms**: database, table, column, query, INSERT, UPDATE, SELECT, schema
- **Technical Actions**: serialize, deserialize, parse, validate (technical validation)
- **Infrastructure**: transaction (when referring to database transaction vs business transaction)

**Business-Level Alternatives**:
- ✅ "Customer submits transaction details" (NOT "POST /api/v1/transactions")
- ✅ "System validates customer identity" (NOT "Query users table WHERE user_id = X")
- ✅ "Platform receives transaction confirmation" (NOT "API returns 200 OK with JSON response")
- ✅ "Customer provides funding source information" (NOT "Request body contains card_id field")

**Warning Message**:
```
⚠️  WARNING: Technical terminology found in Functional Requirements
Line X: "POST /api/v1/transactions" - API endpoint specification
Line Y: "Query database for recipient status" - Database implementation detail

Suggested business-level rewrites:
- Line X: "Customer initiates cross-border transaction"
- Line Y: "System validates recipient is active and eligible"

See BRD-TEMPLATE.md Appendix B for REMOVE/KEEP guidelines.
```

**Fix**:
1. Identify technical terms using scan pattern
2. Rewrite in business-level language (what business capability, not how technically implemented)
3. Defer technical implementation to PRD Related Requirements

**Reference**: BRD-TEMPLATE.md Appendix B (REMOVE/KEEP Rules), BRD_CREATION_RULES.md Section 6.5 (Edge Cases)

---

### CHECK 16: UI-Specific Language in Functional Requirements ⭐ NEW

**Purpose**: Prevent UI implementation details from appearing in business-level FRs
**Type**: Warning (non-blocking) - UI terms indicate potential PRD-level contamination

**Scan Pattern**: Search for UI-specific keywords in Section 4 (Functional Requirements)

**Prohibited UI Terms**:
- **UI Components**: button, dropdown, modal, dialog, popup, form field, checkbox, radio button, tab
- **UI Actions**: click, tap, swipe, scroll, hover, drag, select (from dropdown)
- **UI Elements**: screen, page, view, panel, sidebar, header, footer, navigation bar
- **UI States**: displayed, shown, hidden, enabled, disabled, highlighted, selected
- **UI Layout**: top-right corner, left sidebar, main panel, above/below element

**Business-Level Alternatives**:
- ✅ "Customer selects recipient from saved list" (NOT "Customer clicks recipient dropdown and selects from list")
- ✅ "Customer confirms transaction details" (NOT "Customer clicks 'Confirm' button in modal")
- ✅ "System displays transaction status" (NOT "Status shown in top-right notification panel")
- ✅ "Customer provides amount and funding source" (NOT "Customer enters amount in form field and selects card from dropdown")

**Warning Message**:
```
⚠️  WARNING: UI-specific language found in Functional Requirements
Line X: "Customer clicks 'Send Money' button" - UI implementation detail
Line Y: "Modal displays recipient selection dropdown" - UI component specification

Suggested business-level rewrites:
- Line X: "Customer initiates remittance transaction"
- Line Y: "Customer selects recipient from saved list"

UI implementation details should be deferred to PRD.
```

**Fix**:
1. Identify UI-specific terms using scan pattern
2. Rewrite focusing on business action/outcome (what customer accomplishes, not which UI element they interact with)
3. Defer UI/UX design to PRD Related Requirements

**Reference**: BRD-TEMPLATE.md Appendix B (REMOVE Category: UI Flows and Screens)

---

### CHECK 17: Functional Requirement 6-Subsection Structure ⭐ NEW

**Purpose**: Ensure all Functional Requirements use the standardized 4-subsection business-level format
**Type**: Error (blocking) - All FRs must have complete subsection structure

**Required Subsections** (6 total):
1. **Business Capability**: One-sentence high-level description
2. **Business Requirements**: Bullet list of business needs
3. **Business Rules**: Policies, constraints, regulatory requirements
4. **Business Acceptance Criteria**: Measurable success criteria with targets
5. **Related Requirements**: Cross-references to Platform/Feature BRDs
6. **Complexity**: X/5 rating with business-level rationale

**Valid FR Structure**:
```markdown
#### FR-001: [Requirement Title - Business Capability Name]

**Business Capability**: [One sentence]

**Business Requirements**:
- [Business need 1]
- [Business need 2]

**Business Rules**:
- [Policy/constraint 1]
- [Policy/constraint 2]

**Business Acceptance Criteria**:
- [Measurable criterion 1 with target]
- [Measurable criterion 2 with target]

**Related Requirements**:
- Platform BRDs: [BRD-001, BRD-002, etc.]
- Feature BRDs: [BRD-XXX, BRD-YYY, etc.]

**Complexity**: X/5 ([Business-level rationale with partner count, regulatory scope, dependencies])
```

**Error Message**:
```
❌ ERROR: Functional Requirement FR-005 missing required subsections
Missing:
- Business Capability
- Complexity

Found structure:
✅ Business Requirements
✅ Business Rules
✅ Business Acceptance Criteria
✅ Related Requirements
❌ Business Capability
❌ Complexity

Fix: Add missing subsections per BRD-TEMPLATE.md Section 5.2 format
```

**Fix**:
1. Verify each FR has all 6 subsections in correct order
2. Add missing subsections using BRD-TEMPLATE.md Section 5.2 as reference
3. Ensure subsection headers match exactly (case-sensitive)

**Reference**: BRD-TEMPLATE.md Section 5.2, BRD_CREATION_RULES.md Section 5.5 (Complexity Rating)

---

### CHECK 18: Related Requirements Cross-Reference Validation ⭐ NEW

**Purpose**: Ensure all Platform/Feature BRD cross-references in FRs are valid and exist
**Type**: Warning (non-blocking) - Invalid cross-references reduce traceability

**Validation Rules**:
1. All BRD-NNN references must follow correct ID format (BRD-001, BRD-034, etc.)
2. Referenced BRD files must exist in `docs/BRD/` directory
3. Platform BRDs should reference BRD-001 through BRD-005 (foundational)
4. Feature BRDs should reference both Platform BRDs and related Feature BRDs

**Valid Related Requirements Example**:
```markdown
**Related Requirements**:
- Platform BRDs: BRD-001 (Platform Architecture), BRD-002 (Partner Ecosystem), BRD-003 (Compliance)
- Feature BRDs: BRD-006 (KYC Onboarding), BRD-008 (Wallet Funding), BRD-011 (Recipient Management)
```

**Warning Message**:
```
⚠️  WARNING: Invalid BRD cross-references in FR-005 Related Requirements
- BRD-099: File not found (docs/BRD/BRD-099_*.md does not exist)
- BRD-2: Invalid ID format (should be BRD-002)
- BRD-001 referenced but file path broken

Valid cross-references:
✅ BRD-001 (Platform Architecture) - exists
✅ BRD-008 (Wallet Funding) - exists

Fix: Verify all BRD references exist and use correct ID format (BRD-NNN)
```

**Fix**:
1. Scan all Related Requirements subsections for BRD-NNN pattern
2. Verify each referenced BRD file exists: `docs/BRD/BRD-NNN_*.md`
3. Correct invalid ID formats (BRD-2 → BRD-002, BRD-99 → BRD-099)
4. Remove references to non-existent BRDs or create placeholder BRD if needed

**Reference**: BRD-TEMPLATE.md Appendix C (FR Examples with cross-references)

---

## Error Fix Guide

### Quick Fix Matrix

| Error Check | Quick Fix |
|-------------|-----------|
| **CHECK 1** | Add missing section: `## N. Section Title` |
| **CHECK 2** | Add all 6 required fields to Document Control table |
| **CHECK 3** | Add initial entry to Document Revision History table |
| **CHECK 4** | Rename file to Platform (`BRD-NNN_platform_*`) or Feature (`BRD-NNN_{feature_name_name}`) pattern |
| **CHECK 5** | Ensure Section 3.6 & 3.7 exist with appropriate content by BRD type |
| **CHECK 6** | Add Section 5.2 with table structure and at least 3 architectural topics |
| **CHECK 9** | Remove ADR-NNN references; ensure ADRs only identified as topics in Section 5.2 |
| **CHECK 11** | Fix broken links, use relative paths, verify target files exist |
| **CHECK 13** | Add PRD-Ready Score to Document Control: `✅ [Score]/100 (Target: ≥90/100)` |
| **CHECK 14** | Remove all code blocks (```) from Section 4 FRs; replace with business-level descriptions |
| **CHECK 15** | Replace API/technical terms (POST, GET, JSON, database, query) with business-level language |
| **CHECK 16** | Replace UI terms (button, modal, click, screen) with business action descriptions |
| **CHECK 17** | Add missing FR subsections: Business Capability, Business Requirements, Business Rules, Business Acceptance Criteria, Related Requirements, Complexity |
| **CHECK 18** | Fix invalid BRD cross-references in Related Requirements; verify BRD files exist |

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
