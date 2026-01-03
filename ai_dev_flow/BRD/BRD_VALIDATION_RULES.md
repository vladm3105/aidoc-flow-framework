# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of BRD-TEMPLATE.md
# - Authority: BRD-TEMPLATE.md is the single source of truth for BRD structure
# - Purpose: AI checklist after document creation (derived from template)
# - Scope: Includes all rules from BRD_CREATION_RULES.md plus validation extensions
# - On conflict: Defer to BRD-TEMPLATE.md
# =============================================================================
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

> **📋 Document Role**: This is the **POST-CREATION VALIDATOR** for BRD documents.
> - Apply these rules after BRD creation or modification
> - **Authority**: Validates compliance with `BRD-TEMPLATE.md` (the primary standard)
> - **Scope**: Use for quality gates before committing BRD changes

# BRD Validation Rules Reference

**Version**: 1.4.0
**Date**: 2025-11-19
**Last Updated**: 2025-12-19
**Purpose**: Complete validation rules for BRD documents
**Script**: `scripts/validate_brd_template.sh`
**Primary Template**: `BRD-TEMPLATE.md`
**Framework**: AI Dev Flow SDD (100% compliant)
**Changes**: Added Section Classification (MANDATORY/OPTIONAL/CONDITIONAL); Section 15 (Quality Assurance) now MANDATORY; 18 total sections

---

## Design Decision: Human-Centric Validation (Optional Schema)

> **Intentional Design Choice**: BRD validation is script-first and human-centric. An optional `BRD_SCHEMA.yaml` exists for non-blocking, machine-readable checks.
>
> **Why Schema is Optional**:
> - **Business Content Diversity**: Business requirements span multiple domains with varying terminology, structure, and emphasis
> - **Judgment-Based Quality**: BRD quality depends on business stakeholder comprehension, not technical schema compliance
> - **Flexibility Over Rigidity**: A fixed schema would reject legitimate business expressions that don't fit a predefined mold
>
> **Validation Philosophy**:
> - **Structural Checks**: Verify required sections exist (CHECK 1-6)
> - **Content Quality**: Warn on potential issues without blocking (CHECK 7-12, warnings)
> - **PRD-Ready Scoring**: Quantify business-level content quality (CHECK 13-18)
> - **Human Review**: Final validation by business stakeholders, not automated tools
>
> **Script vs Schema Validation**:
> | Validation Type | BRD Approach | Other Layers |
> |-----------------|--------------|--------------|
> | Structure | `validate_brd_template.sh` | `*_SCHEMA.yaml` |
> | Content | Human review + PRD-Ready Score | Schema field validation |
> | Quality Gate | ≥90/100 PRD-Ready Score | Schema compliance + tests |

---

## Table of Contents

1. [Overview](#overview)
2. [Validation Checks](#validation-checks)
3. [Error Fix Guide](#error-fix-guide)
4. [Quick Reference](#quick-reference)
5. [Common Mistakes](#common-mistakes)

---

## Overview

Note: Some examples in this guide show a portable `docs/` root. In this repository, artifact folders live at the ai_dev_flow root without the `docs/` prefix; see README → “Using This Repo” for path mapping.

The BRD validation script (`validate_brd_template.sh`) performs **24 validation checks** to ensure compliance with:

- **BRD-TEMPLATE.md**: Complete business requirements structure
- **AI Dev Flow SDD Framework**: Business-driven SDD methodology
- **Platform vs Feature BRD**: Different validation requirements by type
- **Business Requirements Quality**: Measurable objectives, acceptance criteria, strategic alignment

### BRD Document Categories

| Category | Filename Pattern | Validation Level | Description |
|----------|------------------|------------------|-------------|
| **Platform BRD** | `BRD-NN_platform_*` or `BRD-NN_infrastructure_*` | Full (24 checks) | Foundational technology stacks and prerequisites |
| **Feature BRD** | `BRD-NN_{feature_name}` | Full (24 checks) | Business capability requirements |
| **BRD-REF** | `BRD-REF-NN_{slug}.md` | Reduced (4 checks) | Supplementary reference documents |

### BRD-REF Reduced Validation (Deprecated)

**Purpose**: Legacy support for `BRD-REF` documents as supplementary references. Prefer using `REF` artifacts (`REF-TEMPLATE.md`) instead. Validation remains reduced for backward compatibility.

**Applicable Checks** (4 total):
- CHECK 2: Document Control Fields (required)
- CHECK 3: Document Revision History (required)
- CHECK 1 (partial): Introduction section only (required)
- CHECK 4 (partial): H1 ID match with filename (required)

**Exempted Checks** (20 total):
- CHECK 1 (full): 18 sections (exempt - only Introduction required)
- CHECK 5-6: Platform/Feature type validation (exempt)
- CHECK 7-12: Content quality warnings (exempt)
- CHECK 13-18: PRD-Ready Score and FR validation (exempt)
- CHECK 19-21: Executive Summary, User Stories, Workflows (exempt)
- CHECK 22: Traceability Matrix (exempt)
- CHECK 23-24: Approval and Glossary (exempt)

**Reference**: See `REF-TEMPLATE.md` for reference document structure and requirements.

### Validation Tiers

| Tier | Type | Exit Code | Description |
|------|------|-----------|-------------|
| **Tier 1** | Errors | 1 | Blocking issues - must fix before commit |
| **Tier 2** | Warnings | 0 | Quality issues - recommended to fix |
| **Tier 3** | Info | 0 | Informational - no action required |

### Reserved ID Exemption (BRD-00_*)

**Scope**: Documents with reserved ID `000` are FULLY EXEMPT from validation.

**Pattern**: `BRD-00_*.md`

**Document Types**:
- Index documents (`BRD-00_index.md`)
- Traceability matrix templates (`BRD-00_TRACEABILITY_MATRIX-TEMPLATE.md`)
- Glossaries (`BRD-00_GLOSSARY.md`)
- Registries, checklists

**Rationale**: Reserved ID 000 documents are framework infrastructure (indexes, templates, reference materials), not project artifacts requiring traceability or quality gates.

**Validation Behavior**: Skip all checks when filename matches `BRD-00_*` pattern.

---

## Validation Checks

### CHECK 1: Required sections

**Purpose**: Verify all mandatory sections exist (18 mandatory sections)
**Type**: Error (blocking for mandatory sections)

**Section Classification**:

| Section | Status | Validation |
|---------|--------|------------|
| 1-14 | MANDATORY | Error if missing |
| 15. Quality Assurance | MANDATORY | Error if missing |
| 16. Traceability | MANDATORY | Error if missing |
| 17. Glossary | MANDATORY | Error if missing |
| 18. Appendices | MANDATORY | Error if missing |
| Document Control | MANDATORY | Error if missing (must be at top) |

**Required sections (MANDATORY)**:
```markdown
## Document Control (must be at top)
## 1. Introduction
## 2. Business Objectives
## 3. Project Scope
## 4. Stakeholders
## 5. User Stories
## 6. Functional Requirements
## 7. Quality Attributes
## 8. Business Constraints and Assumptions
## 9. Acceptance Criteria
## 10. Business Risk Management
## 11. Implementation Approach
## 12. Support and Maintenance
## 13. Cost-Benefit Analysis
## 14. Project Governance
## 15. Quality Assurance
## 16. Traceability
## 17. Glossary
## 18. Appendices
```

**Conditional Subsections**:
- **16.2 Same-Type References**: Only required if cross-BRD dependencies exist
- **Appendix H: Fee Schedule**: Only required for financial/transactional BRDs

> **Note**: For technical QA standards, testing strategy, and defect management, see PRD-TEMPLATE.md Section 21.

**Error Message**:
```
❌ MISSING: ## 2. Business Objectives
```

**Fix**:
1. Add missing section header
2. Ensure exact spelling and numbering
3. Sections 1-18 must be in order (Document Control at top)

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
| **PRD-Ready Score** | 95/100 (Target: ≥90/100)
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
- `BRD-01_platform_architecture_technology_stack.md` ✅ (Platform BRD)
- `BRD-06_b2c_progressive_kyc_onboarding.md` ✅ (Feature BRD)
- `BRD-09.1_provider_integration_prerequisites.md` ✅ (Feature BRD section file)
- `BRD-REF-01_glossary_financial_terms.md` ✅ (Reference document)
- `BRD-REF-02_regulatory_standards_matrix.md` ✅ (Reference document)

**Invalid Examples**:
- `BRD-01.md` ❌ (missing description)
- `brd-001_platform.md` ❌ (wrong case)
- `BRD001_platform.md` ❌ (missing hyphen)
- `BRD-01_Platform_Architecture.md` ❌ (uppercase in slug)
- `BRD-REF001_glossary.md` ❌ (missing hyphen after REF)

**Patterns**:
- Platform/Feature BRD: `BRD-[0-9]{2,}(-[0-9]{2,3})?_[a-z0-9_]+\.md`
- Reference Document: `BRD-REF-[0-9]{3}_[a-z0-9_]+\.md`

**Error Messages**:
```
❌ ERROR: Invalid filename format: brd-001_platform.md
         Expected: BRD-NN_descriptive_title.md or BRD-NN-YY_descriptive_title.md

❌ ERROR: Filename doesn't match Platform, Feature, or Reference BRD pattern
         Platform: BRD-NN_platform_* or BRD-NN_infrastructure_*
         Feature: BRD-NN_{feature_name}
         Reference: BRD-REF-NN_{descriptive_slug}
```

**Fix**:
1. Rename file to match appropriate pattern:
   - Platform: `BRD-NN_platform_*` or `BRD-NN_infrastructure_*`
   - Feature: `BRD-NN_{feature_name}`
   - Reference: `BRD-REF-NN_{descriptive_slug}`
2. Use lowercase with underscores for descriptive title

**Reference**: `BRD_CREATION_RULES.md` section 4 (ID and Naming Standards), `REF-TEMPLATE.md` for reference documents

---

### CHECK 5: Platform vs Feature vs Reference BRD Type Validation

**Purpose**: Validate BRD follows correct template for its type
**Type**: Error (blocking for Platform/Feature), Reduced (for Reference)

**Platform BRD Requirements**:
- Filename contains "platform" or "infrastructure"
- section 3.6: MUST exist and define foundational technology stacks/prerequisites
- section 3.7: MUST exist and define mandatory technical constraints

**Feature BRD Requirements**:
- Filename does NOT contain "platform", "infrastructure", or "REF"
- section 3.6: MUST exist and reference Platform BRD dependencies
- section 3.7: MUST exist and include platform-inherited conditions plus feature-specific requirements

**Reference Document (BRD-REF) Requirements**:
- Filename matches pattern: `BRD-REF-NN_{slug}.md`
- Validation mode: REDUCED (only 4 checks apply)
- Required: Document Control, Revision History, Introduction, H1 ID match
- Exempt: All other checks (sections 3.6, 3.7, PRD-Ready Score, Traceability, etc.)

**General Requirements** (Platform and Feature types only):
- section 3.6: MUST be present and populated with appropriate content
- section 3.7: MUST be present and populated with appropriate content

**Error Message**:
```
❌ ERROR: Platform BRD missing required section 3.6 (Technology Stack Prerequisites)
❌ ERROR: Platform BRD missing required section 3.7 (Mandatory Technology Conditions)
❌ ERROR: Feature BRD missing required section 3.6 (Technology Stack Prerequisites)
❌ ERROR: Feature BRD missing required section 3.7 (Mandatory Technology Conditions)
```

**Info Message** (for BRD-REF):
```
ℹ️  INFO: BRD-REF document detected - applying reduced validation
         Checks 5-24 exempt for reference documents
         Validating: Document Control, Revision History, Introduction, H1 ID match
```

**Fix**:
1. For Platform/Feature BRD: Ensure both sections 3.6 and 3.7 exist
2. For BRD-REF: Ensure Document Control, Revision History, and Introduction exist
---

### CHECK 6: Architecture Decision Requirements section

**Purpose**: Verify section 7.2 exists and has required structure
**Type**: Error (blocking)

**Requirements**:
1. section 7.2 "Architecture Decision Requirements" exists
2. Contains table with columns: Topic Area, Decision Needed, Business Driver, Key Considerations
3. At least 3 architectural topics identified

**Error Message**:
```
❌ MISSING: section 7.2 Architecture Decision Requirements
❌ ERROR: section 7.2 missing required table structure (Topic Area, Decision Needed, Business Driver, Key Considerations)
❌ ERROR: section 7.2 must identify at least 3 architectural topics
```

**Fix**:
```markdown
## 7.2 Architecture Decision Requirements

| Topic Area | Decision Needed | Business Driver | Key Considerations |
|------------|-----------------|---------------|-------------------|
| Multi-Agent Framework | Select orchestration approach | BRD.NN.23.03: Autonomous execution | Google ADK, n8n, custom |
| Data Storage | Choose persistence technology | QA: High availability | PostgreSQL, Cloud SQL, Firestore |
| Communication Protocol | Select inter-system messaging | BRD.NN.015: Real-time updates | Pub/Sub, gRPC, REST WebSocket |
```

**Reference**: `BRD_CREATION_RULES.md` section 9 (Architecture Decision Requirements)

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
BRD.NN.23.03: Reduce transaction processing time from 10 seconds to 5 seconds (50% improvement) within 6 months of implementation, enabling <2-second competitive response times as specified in integrated_strategy_algo_v5.md section 4.2.
```

**Reference**: `BRD_CREATION_RULES.md` section 10 (Business Objectives and Success Criteria)

---

### CHECK 8: Acceptance Criteria Format

**Purpose**: Verify acceptance criteria are measurable and business-focused
**Type**: Warning

**Requirements**:
1. Business Acceptance Criteria (8.1) includes quantifiable success measures
2. Functional Acceptance Criteria (8.2) maps to specific BRD.NN.EE.SS requirements
3. Success Metrics and KPIs (8.7) include baseline, target, measurement frequency, owner

**Warning Messages**:
```
⚠️  WARNING: Business acceptance criteria missing quantifiable measures
⚠️  WARNING: Functional acceptance criteria not mapped to specific BRD.NN.EE.SS IDs
⚠️  WARNING: Success metrics table missing owners or measurement frequency
```

**Fix**:
```markdown
**BRD.NN.06.01:** System must process 1,000 transactions per minute with <5% error rate, measured over 30-day production period.

| KPI | Baseline | Target | Measurement Frequency | Method | Owner |
|-----|----------|--------|----------------------|---------|-------|
| Transaction Throughput | 500/min | 1,000/min | Daily | Monitoring dashboard | Operations Manager |
| Error Rate | 10% | <5% | Hourly | Error logs | QA Manager |
```

**Reference**: `BRD_TEMPLATE.md` section 8 (Acceptance Criteria)

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
         BRDs are created BEFORE ADRs - only identify decision topics in section 7.2
         Found: ADR-033_risk_architecture.md
```

**Fix**:
1. Remove any ADR-NN references
2. Ensure ADR references are only in section 7.2 as topic identification
3. Add ADR references AFTER BRD approval when ADRs are created

**Reference**: `BRD_CREATION_RULES.md` section 7 (ADR Relationship Guidelines)

---

### CHECK 10: Strategy Document Traceability

**Purpose**: Verify BRD includes strategic business references
**Type**: Warning

**Requirements**:
1. References to domain-specific business logic documents
2. Specific sections in strategy documents
3. Business rationale for each major requirement

**Warning Messages**:
```
⚠️  WARNING: Business objective missing strategy document reference
⚠️  WARNING: No references to domain-specific business logic documents found
⚠️  WARNING: Strategic alignment references should include specific sections
```

**Fix**:
```markdown
- **Strategic Context**: Aligns with objectives in `{domain_strategy}/business_logic.md` section 4.2 (collection Risk Management)
- **Performance Targets**: Matches targets defined in `{domain_strategy}/README.md` section 2.1 (Benchmark Performance Goals)
- **Business Rationale**: Enables business execution as specified in `{domain_strategy}/strategy_description.md` section 3.4
```

**Reference**: `BRD_CREATION_RULES.md` section 8 (Traceability Requirements)

---

### CHECK 11: Markdown Link Resolution

**Purpose**: Validate all cross-reference links resolve to existing files
**Type**: Error + Warning

**Valid Link Format**:
```markdown
[PRD-01 Product Requirements](../PRD/PRD-01_product_requirements.md)
[BRD-01 Platform Architecture](./BRD-01_platform_architecture.md)
```

**Invalid Examples**:
```markdown
[PRD-01](../../PRD/PRD-01.md) ❌ (missing relative path)
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
⚠️  WARNING: Link exists but anchor missing: #BRD.NN.23.01 not found in target document
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
1. section 3.3 Out-of-Scope Items exists and is non-empty
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
2. **Mobile Application Development**: Native iOS/Android apps - excluded as desktop application capabilities sufficient for initial release
3. **Multi-Mode Operation Support**: Additional modes - excluded to focus on core operations
```

**Reference**: `BRD_TEMPLATE.md` section 3.3 (Out-of-Scope Items)

---

### CHECK 13: PRD-Ready Score Validation ⭐ NEW

**Purpose**: Validate PRD-Ready Score format and threshold (BRD v1.1 enhancement)
**Type**: Error (blocking) - Required for BRD documents

**Valid Examples**:
- `95/100 (Target: ≥90/100)` ✅
- `✅ 92/100 (Target: ≥90/100)` ✅

**Invalid Examples**:
- `95%` ❌
- `65/100` with missing target clause ❌
- `High` ❌

**Error Message** (format):
```
❌ MISSING: PRD-Ready Score in format: [Score]/100 (Target: ≥90/100)
```

**Warning Message** (threshold):
```
⚠️  WARNING: PRD-Ready Score below 90/100: 85/100
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
- **Deduction**: -10 points per code block found in section 4
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
- **Gold Standard**: BRD-09 has 0 deductions (100% business-level content)

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
- **Invalid Conditions**: Non-existent BRD file, incorrect ID format (BRD-2 instead of BRD-02)
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

**Required sections** (CHECK 1):
- **Deduction**: -1 point per missing section (max -10 points)
- **Required**: All 18 mandatory sections from BRD-TEMPLATE.md

**Revision History** (CHECK 3):
- **Deduction**: -3 points if Document Revision History table missing or empty

**Category 3 Calculation**:
- Minimum deduction: 0 points (complete document structure)
- Maximum deduction: 20 points (significant structural gaps)

---

### PRD-Ready Score Calculation Example

**Example BRD Analysis**:
- **Code blocks found**: 2 in section 4 FRs → -20 points
- **API terms found**: 8 instances (GET, POST, JSON, endpoint) → -16 points
- **UI terms found**: 4 instances (button, modal, click, screen) → -8 points
- **Missing subsections**: 2 FRs each missing Complexity subsection → -10 points
- **Invalid cross-references**: 1 reference to non-existent BRD-099 → -2 points
- **Document Control**: All fields present → 0 points
- **Required sections**: All 18 mandatory sections present → 0 points
- **Revision History**: Table present → 0 points

**Total Deductions**: 20 + 16 + 8 + 10 + 2 = 56 points

**PRD-Ready Score**: 100 - 56 = **44/100** ❌

**Validation Result**: **FAIL** (Target: ≥90/100)

---

**Example Gold Standard (BRD-09)**:
- **Code blocks**: 0 → -0 points
- **API terms**: 0 → -0 points
- **UI terms**: 0 → -0 points
- **Missing subsections**: 0 → -0 points
- **Invalid cross-references**: 0 → -0 points
- **Document Control**: Complete → -0 points
- **Required sections**: Complete → -0 points
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

**Scan Pattern**: Search for triple backticks (```) within section 4 (Functional Requirements)

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
❌ ERROR: Code block found in Functional Requirements (section 4)
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

**Scan Pattern**: Search for technical keywords in section 4 (Functional Requirements)

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

**Reference**: BRD-TEMPLATE.md Appendix B (REMOVE/KEEP Rules), BRD_CREATION_RULES.md section 6.5 (Edge Cases)

---

### CHECK 16: UI-Specific Language in Functional Requirements ⭐ NEW

**Purpose**: Prevent UI implementation details from appearing in business-level FRs
**Type**: Warning (non-blocking) - UI terms indicate potential PRD-level contamination

**Scan Pattern**: Search for UI-specific keywords in section 4 (Functional Requirements)

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
- Line X: "Customer initiates a transaction"
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
### BRD.NN.001: [Requirement Title - Business Capability Name]

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
- Platform BRDs: [BRD-01, BRD-02, etc.]
- Feature BRDs: [BRD-XXX, BRD-YYY, etc.]

**Complexity**: X/5 ([Business-level rationale with partner count, regulatory scope, dependencies])
```

**Error Message**:
```
❌ ERROR: Functional Requirement BRD.NN.005 missing required subsections
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

Fix: Add missing subsections per BRD-TEMPLATE.md section 7.2 format
```

**Fix**:
1. Verify each FR has all 6 subsections in correct order
2. Add missing subsections using BRD-TEMPLATE.md section 7.2 as reference
3. Ensure subsection headers match exactly (case-sensitive)

**Reference**: BRD-TEMPLATE.md section 7.2, BRD_CREATION_RULES.md section 5.5 (Complexity Rating)

---

### CHECK 18: Related Requirements Cross-Reference Validation ⭐ NEW

**Purpose**: Ensure all Platform/Feature BRD cross-references in FRs are valid and exist
**Type**: Warning (non-blocking) - Invalid cross-references reduce traceability

**Validation Rules**:
1. All BRD-NN references must follow correct ID format (BRD-01, BRD-34, etc.)
2. Referenced BRD files must exist in `docs/BRD/` directory
3. Platform BRDs should reference BRD-01 through BRD-05 (foundational)
4. Feature BRDs should reference both Platform BRDs and related Feature BRDs

**Valid Related Requirements Example**:
```markdown
**Related Requirements**:
- Platform BRDs: BRD-01 (Platform Architecture), BRD-02 (Partner Ecosystem), BRD-03 (Compliance)
- Feature BRDs: BRD-NN (Feature Example A), BRD-NN (Feature Example B), BRD-NN (Feature Example C)
```

**Warning Message**:
```
⚠️  WARNING: Invalid BRD cross-references in BRD.NN.005 Related Requirements
- BRD-099: File not found (docs/BRD/BRD-099_*.md does not exist)
- BRD-2: Invalid ID format (should be BRD-02)
- BRD-01 referenced but file path broken

Valid cross-references:
✅ BRD-01 (Platform Architecture) - exists
✅ BRD-NN (Wallet Funding) - exists

Fix: Verify all BRD references exist and use correct ID format (BRD-NN)
```

**Fix**:
1. Scan all Related Requirements subsections for BRD-NN pattern
2. Verify each referenced BRD file exists: `docs/BRD/BRD-NN_*.md`
3. Correct invalid ID formats (BRD-2 → BRD-02, BRD-99 → BRD-099)
4. Remove references to non-existent BRDs or create placeholder BRD if needed

**Reference**: BRD-TEMPLATE.md Appendix C (FR Examples with cross-references)

---

### CHECK 19: Executive Summary Structure ⭐ NEW

**Purpose**: Validate Executive Summary contains 6 required quantitative elements for business impact assessment
**Type**: Warning (non-blocking) - Quantitative Executive Summary improves stakeholder comprehension

**Location**: section 1.1 (Executive Summary) within Introduction

**Required 6 Elements**:
1. **Problem Statement with Market Data**: Market size, volume, or quantified gap
2. **Proposed Solution Overview**: Scope with numbers (corridors, transaction types, user segments)
3. **Expected Business Outcomes**: Quantified targets (% cost reduction, revenue opportunity, efficiency gain)
4. **Target User Segments**: Sized segments (number of users, transaction volume)
5. **Implementation Timeline**: High-level phases with duration estimates
6. **Investment Required**: Budget range or cost category (if available at BRD stage)

**Validation Checks**:
- [ ] Executive Summary paragraph contains at least one market data point ($ amount, user count, % metric)
- [ ] Solution scope includes quantitative elements (X corridors, Y transaction types)
- [ ] Business outcomes are measurable (% improvement, $ value, time savings)
- [ ] Target segments include sizing data
- [ ] Timeline mentions phases or duration
- [ ] Investment level mentioned (even if approximate)

**Valid Example** (BRD-09):
```markdown
### 1.1 Executive Summary

The target market segment represents a **$X market** with approximately **Y potential customers**
in the United States sending an average of **$500 per month** to family members. Current solutions charge **5-8% all-in fees**
with delivery times of 24-48 hours.

Our solution enables customers to complete transactions **within [target time]** at an all-in cost of
approximately **[Z]%** ([flat fee] + [conversion margin]). The solution leverages external providers for funding,
conversion, and delivery to achieve reliable outcomes.

This BRD defines business requirements for **Phase 1: Core Remittance Platform**, targeting **$10M GMV in Year 1**
with **5,000 active senders**. Implementation will occur over **4 phases** (Q1-Q4 2025) with an estimated investment
of **$500K-$750K** for platform development and regulatory compliance.
```

**Warning Message**:
```
⚠️  WARNING: Executive Summary missing quantitative elements
Missing elements:
- Market data (no $ amount, user count, or % metric found)
- Target segments sizing (no user or transaction volume mentioned)
- Investment required (no budget range or cost estimate)

Recommendation: Add quantitative data for better stakeholder impact assessment
Reference: BRD-TEMPLATE.md lines 76-111 for Executive Summary pattern
```

**Fix**:
1. Add market sizing data with sources ($X market, Y users, Z% growth)
2. Include measurable business outcomes (% reduction, $ value, time savings)
3. Specify target segment sizes (number of users, transaction volumes)
4. Mention implementation timeline (phases, quarters, duration)
5. Reference investment level if known at BRD stage

**Reference**: BRD-TEMPLATE.md section 1.1, BRD_CREATION_RULES.md section 2.2

---

### CHECK 20: User Stories section ⭐ UPDATED 2025-11-26

**Purpose**: Verify section 5 (User Stories) exists as HIGH-LEVEL SUMMARY (detailed user stories in PRD)
**Type**: Error (blocking) - User Stories section mandatory in BRD, but simplified format

**Updated Guidance (2025-11-26)**: BRD section 5 now contains only a high-level summary of key user story categories. Detailed user story tables, acceptance criteria, and role definitions have been moved to PRD.

**Location**: section 5 (User Stories - High-Level Summary)

**Required Structure** (Simplified):
```markdown
## 5. User Stories (High-Level Summary)

📚 Complete User Stories: For detailed user stories with acceptance criteria, permissions, and user roles, see:
- [PRD Template - User Stories & User Roles section](../PRD/PRD-TEMPLATE.md#user-stories--user-roles)

### Key User Story Categories
[List 2-3 primary user categories with 3-5 sample stories]

### User Story Summary Statistics
[Aggregate counts only - no detailed tables]
- Primary User Stories: [XX] total ([YY] P1, [ZZ] P2)
- Operational User Stories: [XX] total ([YY] P1, [ZZ] P2)

### Business Objective Alignment
[High-level mapping only]
```

**Validation Checks** (Simplified):
- [ ] section 5 header exists: `## 5. User Stories`
- [ ] Reference link to PRD exists
- [ ] At least 2-3 key user story categories listed (bullet format)
- [ ] Aggregate summary statistics present (counts only, no detailed tables)
- [ ] High-level business objective alignment mentioned

**Error Message**:
```
❌ MISSING: section 5 (User Stories)
Required in BRD template (simplified format as of 2025-11-26)

Add section with high-level summary:
- Key user story categories (3-5 bullet points per category)
- Aggregate counts (Primary, Operational, Total)
- Reference link to PRD for complete details

Reference: BRD-TEMPLATE.md section 5 (lines 453-488)
```

**Warning Message** (quality issues):
```
⚠️  WARNING: section 5 should be high-level summary only
Issues found:
- Contains detailed user story tables (belongs in PRD)
- Contains acceptance criteria (belongs in PRD)
- Missing reference link to PRD

Fix: Simplify to high-level summary and add PRD reference link
```

**Fix**:
1. Replace detailed user story tables with 3-5 bullet points per category
2. Replace detailed statistics tables with aggregate counts only
3. Add reference link to PRD-TEMPLATE.md User Stories section
4. Keep only business-level summary (detailed content belongs in PRD)

**Reference**: BRD-TEMPLATE.md section 5 (simplified), BRD_CREATION_RULES.md section 5.6, PRD-TEMPLATE.md User Stories & User Roles

---

### CHECK 21: Workflow Diagrams ⭐ NEW

**Purpose**: Validate sections 3.5.4-3.5.5 contain required Mermaid workflow diagrams
**Type**: Warning (non-blocking) - Workflow diagrams improve business process clarity

**Location**: section 3.5.4 (End-to-End Workflow Diagram), section 3.5.5 (Exception Handling Workflow)

**Required Elements**:
- [ ] section 3.5.4 exists with Mermaid sequence diagram
- [ ] section 3.5.5 exists with exception handling workflow
- [ ] Mermaid diagrams use correct syntax (```mermaid sequenceDiagram)
- [ ] Workflow summary table documents each step
- [ ] Participants represent business actors (not technical components)

**Valid Mermaid Structure**:
```markdown
### 3.5.4 End-to-End Workflow Diagram

**Mermaid Diagram**:
\`\`\`mermaid
sequenceDiagram
    participant User
    participant App
    participant Partner

    User->>App: Initiate business action
    App->>Partner: Process request
    Partner-->>App: Confirmation
    App->>User: Display outcome
\`\`\`

**Workflow Summary**:
| Step | Actor | Action | Business Outcome |
|------|-------|--------|------------------|
| 1 | User | Initiate action | Request submitted |
| 2 | App | Process request | Validation complete |
| 3 | Partner | Confirm action | Transaction processed |
| 4 | User | Receive confirmation | Business goal achieved |
```

**Warning Message**:
```
⚠️  WARNING: Workflow diagrams missing or incomplete
Missing sections:
- section 3.5.4 (End-to-End Workflow) not found
- section 3.5.5 (Exception Handling) not found

Recommendation: Add Mermaid sequence diagrams to visualize business processes
Reference: BRD-TEMPLATE.md lines 173-254
```

**Quality Checks**:
- [ ] Participants are business-level (Sender, Recipient, Partner) not technical (API, Database, Service)
- [ ] Steps describe business actions (Submit request, Verify identity) not technical operations (POST /api/users, INSERT INTO table)
- [ ] Workflow summary table documents business outcomes, not technical results

**Fix**:
1. Add section 3.5.4 within section 3 (Project Scope)
2. Create Mermaid sequence diagram showing happy path business workflow
3. Add workflow summary table documenting each step
4. Add section 3.5.5 for exception handling workflows
5. Ensure participants and actions are business-level (no technical implementation)

**Reference**: BRD-TEMPLATE.md sections 3.5.4-3.5.5, BRD_CREATION_RULES.md section 2.3

---

### CHECK 22: Traceability Matrix ⭐ NEW

**Purpose**: Verify section 15 (Traceability) contains complete bidirectional requirements mapping
**Type**: Error (blocking) - Traceability mandatory in BRD v1.1

**Location**: section 15 (Traceability)

**Required Subsections**:
- [ ] 15.1 Requirements Traceability Matrix
  - [ ] 15.1.1 Business Objectives → Functional Requirements
  - [ ] 15.1.2 Functional Requirements → Technical Specifications
  - [ ] 15.1.3 Quality Attributes → Technical Specifications
- [ ] 15.2 Cross-BRD Dependencies
- [ ] 15.3 Test Coverage Traceability
- [ ] 15.4 Traceability Summary (with Health Score)

**Validation Checks**:
- [ ] section 15 header exists
- [ ] All 4 subsections present (15.1-15.4)
- [ ] Business Objectives table includes Coverage Status column
- [ ] Functional Requirements table includes downstream SPEC/IMPL references
- [ ] Cross-BRD Dependencies table lists all dependencies
- [ ] Traceability Summary includes Health Score calculation
- [ ] Health Score target documented (≥90%)

**Error Message**:
```
❌ MISSING: section 15 (Traceability)
Required in BRD v1.1 template

Add section with structure:
- 15.1 Requirements Traceability Matrix
  - 15.1.1 Business Objectives → FRs
  - 15.1.2 FRs → Technical Specs
  - 15.1.3 QAs → Technical Specs
- 15.2 Cross-BRD Dependencies
- 15.3 Test Coverage Traceability
- 15.4 Traceability Summary (Health Score)

Reference: BRD-TEMPLATE.md section 15
```

**Warning Message** (orphan detection):
```
⚠️  WARNING: Traceability orphans detected
Orphaned Requirements:
- BRD.NN.23.03: No related BRD.NN.EE.SS requirements (Coverage Status = "Gap")
- BRD.NN.012: Not linked to any Business Objective
- PRD.NN.09.07: Not linked to any Functional Requirement

Traceability Health Score: 78/100 (Target: ≥90/100)

Fix: Ensure bidirectional links for all objectives, BRD requirements, and user stories
```

**Orphan Prevention Checks**:
- [ ] Zero orphaned Business Objectives (all have Coverage Status = "Complete" or "Partial")
- [ ] Zero orphaned Functional Requirements (all appear in BO→BRD.NN table)
- [ ] Zero orphaned User Stories (all have Related BRD.NN.EE.SS links)
- [ ] All BRD.NN.EE.SS requirements have planned downstream SPEC references

**Fix**:
1. Add section 15 with all 4 subsections
2. Create Business Objectives → FRs table listing all BOs from section 2.4
3. Create FRs → Technical Specs table with planned SPEC-XXX-NN references
4. Document Cross-BRD Dependencies if any exist
5. Map requirements to planned test artifacts (TEST-XXX-UNIT, TEST-XXX-INT, etc.)
6. Calculate Traceability Health Score: Average of all coverage percentages
7. Ensure score ≥90% by eliminating orphans

**Reference**: BRD-TEMPLATE.md section 15, BRD_CREATION_RULES.md section 8

---

### CHECK 23: Approval and Sign-off section ⭐ NEW

**Purpose**: Verify section 14.5 (Approval and Sign-off) contains approval workflow and change control
**Type**: Error (blocking) - Approval process mandatory in BRD v1.1

**Location**: section 14.5 (Approval and Sign-off) within Project Governance

**Required Subsections**:
- [ ] 14.5.1 Document Approval Table
- [ ] 14.5.2 Approval Criteria
- [ ] 14.5.3 Change Control Process
- [ ] 14.5.4 Approval Status Tracking (optional)

**Validation Checks**:
- [ ] section 14.5 exists within section 14 (Project Governance)
- [ ] Document Approval Table includes minimum 4 roles: Executive Sponsor, Product Owner, Business Lead, Technology Lead
- [ ] Approval Criteria lists at least 5 conditions for BRD approval
- [ ] Change Control Process table defines Minor/Moderate/Major changes with version impact

**Error Message**:
```
❌ MISSING: section 14.5 (Approval and Sign-off)
Required in BRD v1.1 template

Add subsection within section 14 (Project Governance):
- 14.5.1 Document Approval Table (stakeholders)
- 14.5.2 Approval Criteria (conditions for approval)
- 14.5.3 Change Control Process (version management)

Reference: BRD-TEMPLATE.md section 14.5
```

**Required Approval Table Structure**:
```markdown
| Role | Name | Title | Approval Date | Signature |
|------|------|-------|---------------|-----------|
| Executive Sponsor | [TBD] | [Title] | [Pending] | |
| Product Owner | [TBD] | [Title] | [Pending] | |
| Business Lead | [TBD] | [Title] | [Pending] | |
| Technology Lead | [TBD] | [Title] | [Pending] | |
```

**Required Change Control Structure**:
```markdown
| Change Type | Approval Required | Process | Version Impact |
|-------------|------------------|---------|----------------|
| Minor (clarifications, typos) | Product Owner | Update + review | Patch (1.2.1) |
| Moderate (new requirements, scope changes) | Product Owner + Tech Lead | Impact assessment | Minor (1.3) |
| Major (business model changes, new partners) | All stakeholders | Full BRD review | Major (2.0) |
```

**Warning Message** (incomplete approval table):
```
⚠️  WARNING: Incomplete approval workflow in section 14.5
Issues found:
- Approval table missing Compliance Lead (required for regulatory projects)
- Approval Criteria lists only 3 conditions (minimum 5 required)
- Change Control missing version impact definitions

Fix: Complete all required subsections per BRD-TEMPLATE.md section 14.5
```

**Fix**:
1. Add section 14.5 within section 14 (Project Governance)
2. Create Document Approval Table with minimum 4 roles (add Compliance/Finance if applicable)
3. List approval criteria (minimum 5 conditions):
   - All stakeholders approved
   - Critical risks have mitigation strategies
   - Regulatory compliance validated
   - Required dependencies confirmed
   - Budget allocation approved
4. Define Change Control Process table with version impact rules
5. Use semantic versioning: major.minor.patch

**Reference**: BRD-TEMPLATE.md section 14.5, BRD_CREATION_RULES.md section 11.5

---

### CHECK 24: Glossary Subsections ⭐ NEW

**Purpose**: Verify section 17 (Glossary) contains all 6 required subsections for comprehensive terminology documentation
**Type**: Warning (non-blocking) - Complete glossary improves document clarity and reduces ambiguity

**Location**: section 17 (Glossary)

**Required Subsections**:
- [ ] 17.1 Business Terms
- [ ] 17.2 Technical Terms
- [ ] 17.3 Domain-Specific Terms
- [ ] 17.4 Acronyms
- [ ] 17.5 Cross-References
- [ ] 17.6 External Standards

**Validation Checks**:
- [ ] section 17 header exists: `## 17. Glossary`
- [ ] All 6 subsections present (17.1-17.6)
- [ ] Each subsection contains at least one term definition
- [ ] Business Terms (17.1) defines business-level concepts (ROI, KPI, SLA, etc.)
- [ ] Technical Terms (17.2) defines technical concepts mentioned in BRD
- [ ] Domain-Specific Terms (17.3) defines industry/domain terminology
- [ ] Acronyms (17.4) expands all abbreviations used in document
- [ ] Cross-References (17.5) links to related BRDs or external documents
- [ ] External Standards (17.6) references regulatory/industry standards

**Warning Message**:
```
⚠️  WARNING: Incomplete Glossary structure in section 17
Missing subsections:
- 17.3 Domain-Specific Terms not found
- 17.5 Cross-References not found
- 17.6 External Standards not found

Recommendation: Add all 6 subsections for comprehensive terminology coverage
Reference: BRD-TEMPLATE.md section 17
```

**Required Structure**:
```markdown
## 17. Glossary

### 17.1 Business Terms
| Term | Definition | Related section |
|------|------------|-----------------|
| KPI | Key Performance Indicator - measurable value demonstrating effectiveness | section 7 (Acceptance Criteria) |

### 17.2 Technical Terms
| Term | Definition | Related section |
|------|------------|-----------------|
| API | Application Programming Interface - defines interactions between software | section 4.3 (Integration Requirements) |

### 17.3 Domain-Specific Terms
| Term | Definition | Related section |
|------|------------|-----------------|
| Remittance | Transfer of money by foreign worker to home country | section 1 (Introduction) |

### 17.4 Acronyms
| Acronym | Full Form | First Use |
|---------|-----------|-----------|
| GMV | Gross Merchandise Value | section 2.4 (Business Objectives) |

### 17.5 Cross-References
| Term | Referenced Document | section |
|------|---------------------|---------|
| Platform Architecture | BRD-01_platform_architecture_technology_stack.md | section 16.2 |

### 17.6 External Standards
| Standard | Organization | Relevance | section |
|----------|--------------|-----------|---------|
| PCI-DSS | Payment Card Industry | Payment security compliance | section 7.3 (security Requirements) |
```

**Quality Checks**:
- [ ] No duplicate terms across subsections
- [ ] All acronyms used in document are defined
- [ ] Related section column populated for key terms
- [ ] Cross-references link to existing documents
- [ ] External standards include organization and relevance

**Fix**:
1. Add section 17 if missing, or enhance existing section
2. Create all 6 subsections (17.1-17.6)
3. Populate Business Terms with business-level concepts from document
4. Define Technical Terms mentioned in Functional Requirements
5. Document Domain-Specific terminology (industry jargon, specialized concepts)
6. Expand all acronyms used in document (minimum 1 per subsection)
7. List Cross-References to related BRDs and documents
8. Document External Standards referenced (regulatory, industry, technical)

**Reference**: BRD-TEMPLATE.md section 17, BRD_CREATION_RULES.md section 2 (line 76)

---

### CHECK 25: Element ID Format Compliance ⭐ NEW

**Purpose**: Verify element IDs use unified 4-segment format, flag removed patterns.
**Type**: Error

| Check | Pattern | Result |
|-------|---------|--------|
| Valid format | `### BRD.NN.TT.SS:` | ✅ Pass |
| Removed pattern | `### AC-XXX` | ❌ Fail - use BRD.NN.06.SS |
| Removed pattern | `### FR-XXX` | ❌ Fail - use BRD.NN.01.SS |
| Removed pattern | `### BC-XXX` | ❌ Fail - use BRD.NN.03.SS |
| Removed pattern | `### BO-XXX` | ❌ Fail - use BRD.NN.23.SS |
| Removed pattern | `### QA-XXX` | ❌ Fail - use BRD.NN.02.SS |

**Regex**: `^###\s+BRD\.[0-9]{2,}\.[0-9]{2,}\.[0-9]{2,}:\s+.+$`

**Common Element Types for BRD**:
| Element Type | Code | Example |
|--------------|------|---------|
| Functional Requirement | 01 | BRD.02.01.01 |
| Quality Attribute | 02 | BRD.02.02.01 |
| Constraint | 03 | BRD.02.03.01 |
| Assumption | 04 | BRD.02.04.01 |
| Dependency | 05 | BRD.02.05.01 |
| Acceptance Criteria | 06 | BRD.02.06.01 |
| Risk | 07 | BRD.02.07.01 |
| Business Objective | 23 | BRD.02.23.01 |

**Fix**: Replace `### AC-01: Criterion` with `### BRD.02.06.01: Criterion`

**Reference**: BRD_CREATION_RULES.md Section 4.1, [ID_NAMING_STANDARDS.md — Cross-Reference Link Format](../ID_NAMING_STANDARDS.md#cross-reference-link-format-mandatory)

---

## Error Fix Guide

### Quick Fix Matrix

| Error Check | Quick Fix |
|-------------|-----------|
| **CHECK 1** | Add missing section: `## N. section Title` |
| **CHECK 2** | Add all 6 required fields to Document Control table |
| **CHECK 3** | Add initial entry to Document Revision History table |
| **CHECK 4** | Rename file to Platform (`BRD-NN_platform_*`), Feature (`BRD-NN_{feature_name}`), or Reference (`BRD-REF-NN_{slug}`) pattern |
| **CHECK 5** | For Platform/Feature: Ensure section 3.6 & 3.7 exist; For BRD-REF: Only Document Control, Revision History, Introduction required |
| **CHECK 6** | Add section 7.2 with table structure and at least 3 architectural topics |
| **CHECK 9** | Remove ADR-NN references; ensure ADRs only identified as topics in section 7.2 |
| **CHECK 11** | Fix broken links, use relative paths, verify target files exist |
| **CHECK 13** | Add PRD-Ready Score to Document Control: `✅ [Score]/100 (Target: ≥90/100)` |
| **CHECK 14** | Remove all code blocks (```) from section 4 FRs; replace with business-level descriptions |
| **CHECK 15** | Replace API/technical terms (POST, GET, JSON, database, query) with business-level language |
| **CHECK 16** | Replace UI terms (button, modal, click, screen) with business action descriptions |
| **CHECK 17** | Add missing FR subsections: Business Capability, Business Requirements, Business Rules, Business Acceptance Criteria, Related Requirements, Complexity |
| **CHECK 18** | Fix invalid BRD cross-references in Related Requirements; verify BRD files exist |
| **CHECK 19** | Add quantitative elements to Executive Summary (market data, outcomes, segments, timeline, investment) |
| **CHECK 20** | Add section 5 (User Stories) with standard format and FR traceability |
| **CHECK 21** | Add sections 3.5.4-3.5.5 with Mermaid workflow diagrams and summary tables |
| **CHECK 22** | Add section 16 (Traceability) with complete bidirectional mapping and Health Score ≥90% |
| **CHECK 23** | Add section 14.5 (Approval and Sign-off) with approval table, criteria, and change control process |
| **CHECK 24** | Add section 17 subsections 17.1-17.6 for complete Glossary (Business Terms, Technical Terms, Domain-Specific, Acronyms, Cross-References, External Standards) |
| **CHECK 25** | Replace legacy element IDs (AC-XXX, FR-XXX, BC-XXX, BO-XXX, QA-XXX) with unified format `BRD.NN.TT.SS` |

---

## Quick Reference

### Pre-Commit Validation

```bash
# Validate single BRD (nested folder structure - DEFAULT)
./scripts/validate_brd_template.sh docs/BRD/BRD-01_platform_architecture/BRD-01.0_platform_architecture_index.md

# Validate all BRD files (section-based structure)
find docs/BRD -type f -name "BRD-*.md" -exec ./scripts/validate_brd_template.sh {} \;

# Validate monolithic BRD (optional for <25KB)
./scripts/validate_brd_template.sh docs/BRD/BRD-01_platform_architecture.md

# Validate all BRD files (legacy pattern)
**Business Requirements Completeness (40%)**:
- All 18 mandatory sections present and populated: 10%
- Business objectives follow SMART criteria: 10%
- Acceptance criteria quantifiable and verifiable: 10%
- Stakeholder analysis complete: 10%

**Technical Readiness (30%)**:
- section 3.6 & 3.7 properly populated by BRD type: 10%
- section 7.2 Architecture Decision Requirements table: 10%
- No forward ADR references: 10%

**Quality Standards (20%)**:
- Document control complete: 5%
- Strategic alignment with domain-specific business logic documents: 5%
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
| **Project Name** | Service Platform Enhancement |
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
❌ ERROR: Invalid filename format: BRD-01.md
         Expected: BRD-NN_descriptive_title.md
```

**Cause**: Missing descriptive title slug or Platform/Feature pattern

**Fix**: Rename file to match appropriate pattern:
- Platform: `BRD-01_platform_architecture_technology_stack.md`
- Feature: `BRD-06_b2c_progressive_kyc_onboarding.md`

---

### Mistake #3: Missing Architecture Decision Requirements

**Error**:
```
❌ MISSING: section 7.2 Architecture Decision Requirements
❌ ERROR: section 7.2 must identify at least 3 architectural topics
```

**Cause**: Missing required section or empty/inadequate table

**Fix**:
```markdown
## 7.2 Architecture Decision Requirements

| Topic Area | Decision Needed | Business Driver | Key Considerations |
|------------|-----------------|---------------|-------------------|
| Database Technology | Select data storage solution | BRD.NN.921: High availability requirements | PostgreSQL, Cloud SQL, DynamoDB |
| Authentication | Choose identity management | BRD.NN.003: Secure user access | OAuth2, SAML, Firebase Auth |
| API Architecture | Define service communication | BRD.NN.015: System integration | REST APIs, gRPC, GraphQL |
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
1. Remove ADR-NN references
2. Convert to topic identification in section 7.2
3. Add ADR links AFTER BRD approval when ADRs are created

---

### Mistake #5: Platform BRD Missing Technology sections

**Error**:
```
❌ ERROR: Platform BRD missing required section 3.6 (Technology Stack Prerequisites)
❌ ERROR: Platform BRD missing required section 3.7 (Mandatory Technology Conditions)
```

**Cause**: Platform BRD filename pattern but missing required technology sections

**Fix**:
1. Add section 3.6 with technology prerequisites
2. Add section 3.7 with mandatory technology conditions
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
BRD.NN.23.03: Reduce average order processing time from current 10 seconds to 5 seconds (50% improvement), measured by 95th percentile response time, within 6 months of implementation to match competitive service platforms.
```

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2025-11-19 | Initial validation rules for BRD documents | System Architect |
| 1.3.0 | 2025-12-12 | Added BRD-REF as third document category with reduced validation; Updated CHECK 4 and CHECK 5 for reference documents | Claude Code |

---

**Maintained By**: Business Analyst Team, Quality Assurance Team
**Review Frequency**: Updated with BRD template enhancements
**Support**: See [BRD-TEMPLATE.md](../BRD/BRD-TEMPLATE.md) for comprehensive template guidance
