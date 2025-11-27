---
title: "PRD Creation Rules"
tags:
  - creation-rules
  - layer-2-artifact
  - shared-architecture
custom_fields:
  document_type: creation-rules
  artifact_type: PRD
  layer: 2
  priority: shared
  development_status: active
---

# PRD Creation Rules

**Version**: 2.0
**Date**: 2025-11-26
**Last Updated**: 2025-11-26
**Source**: Extracted from PRD-TEMPLATE.md, PRD-VALIDATION_RULES.md, README.md, and PRD-000_index.md
**Purpose**: Complete reference for creating PRD files according to doc-flow SDD framework
**Changes**: Implemented 19-section structure (0-18), added section 6 (User Stories), section 8 (Customer-Facing Content MANDATORY), dual scoring requirements

---

## Table of Contents

0. [Document Control](#0-document-control)
1. [File Organization and Directory Structure](#1-file-organization-and-directory-structure)
2. [Document Structure (Required sections)](#2-document-structure-required-sections)
3. [Document Control Requirements](#3-document-control-requirements)
4. [ID and Naming Standards](#4-id-and-naming-standards)
5. [Product Requirements Principles](#5-product-requirements-principles)
6. [User Stories & User Roles](#6-user-stories--user-roles)
7. [Architecture Decision Requirements](#7-architecture-decision-requirements)
8. [Customer-Facing Content & Messaging (MANDATORY)](#8-customer-facing-content--messaging-mandatory)
9. [ADR Relationship Guidelines](#9-adr-relationship-guidelines)
10. [SYS-Ready Scoring System](#10-sys-ready-scoring-system)
11. [EARS-Ready Scoring System](#11-ears-ready-scoring-system)
12. [Traceability Requirements](#12-traceability-requirements)
13. [Business Objectives and Success Criteria](#13-business-objectives-and-success-criteria)
14. [Quality Gates](#14-quality-gates)
15. [Additional Requirements](#15-additional-requirements)

---

## 0. Document Control

**Purpose**: Establishes document metadata, versioning, and dual scoring requirements for PRD quality gates.

**Position**: Must be section 0 at the very beginning of PRD (before all numbered sections)

**Required Fields** (11 mandatory + 4 optional):

| Field | Description | Requirement |
|-------|-------------|-------------|
| Document ID | PRD-XXX format in H1 header | MANDATORY |
| Version | Semantic versioning (X.Y.Z) | MANDATORY |
| Status | Draft/Review/Approved/Implemented | MANDATORY |
| Author | Product Manager/Owner Name | MANDATORY |
| Reviewer | Technical reviewer name | MANDATORY |
| Approver | Final approver name | MANDATORY |
| Created Date | YYYY-MM-DD | MANDATORY |
| Last Updated | YYYY-MM-DD | MANDATORY |
| BRD Reference | @brd: BRD-XXX tag | MANDATORY |
| SYS-Ready Score | ✅ XX% (Target: ≥90%) | MANDATORY |
| EARS-Ready Score | ✅ XX% (Target: ≥90%) | MANDATORY |
| Priority | High / Medium / Low | OPTIONAL |
| Target Release | Release version/Quarter | OPTIONAL |
| Estimated Effort | Story Points or Person-Months | OPTIONAL |

**Note**: Optional fields are recommended but not validation-blocking. Document Revision History table is also optional but recommended for tracking changes.

**Dual Scoring Requirements**:
- Both SYS-Ready Score and EARS-Ready Score must be present
- Both scores must be ≥90% for progression to EARS/SYS
- Scores reflect readiness for downstream artifact generation
- Use exact format: `✅ XX% (Target: ≥90%)`

**Template**:
```markdown
## 0. Document Control

| Item | Details |
|------|---------|
| **Status** | Draft / Review / Approved / Implemented |
| **Version** | [Semantic version, e.g., 1.0.0] |
| **Date Created** | YYYY-MM-DD |
| **Last Updated** | YYYY-MM-DD |
| **Author** | [Product Manager/Owner Name] |
| **Reviewer** | [Technical Reviewer Name] |
| **Approver** | [Stakeholder Name] |
| **BRD Reference** | @brd: BRD-NNN |
| **SYS-Ready Score** | ✅ 95% (Target: ≥90%) |
| **EARS-Ready Score** | ✅ 95% (Target: ≥90%) |
```

---

## 1. File Organization and Directory Structure

- **Location**: `docs/PRD/` within project docs directory
- **Naming**: `PRD-NNN_descriptive_title.md` (NNN = 3-digit sequential number, snake_case slug)
- **Subdocuments**: For complex business features: `PRD-NNN-YY_additional_detail.md` (YY = 2-digit sub-number)

---

## 2. Document Structure (Required sections)

Every PRD must contain these exact 19 sections (0-18) in order. section numbering must be explicit in all headers.

#### Required sections in Order (19 total):

0. **Document Control** - Metadata, versioning, dual scoring (SYS-Ready + EARS-Ready ≥90%)
1. **Executive Summary** - Business value and timeline overview
2. **Problem Statement** - Current state, business impact, opportunity assessment
3. **Target Audience & User Personas** - Primary users, secondary users, business stakeholders
4. **Success Metrics (KPIs)** - Primary KPIs, secondary KPIs, success criteria by phase
5. **Goals & Objectives** - Primary business goals, secondary objectives, stretch goals
6. **Scope & Requirements** - In scope features, out of scope items, dependencies, assumptions
7. **User Stories & User Roles** - Role definitions, story summaries (PRD-level only, no EARS/BDD detail)
8. **Functional Requirements** - User journey mapping, capability requirements
9. **Customer-Facing Content & Messaging (MANDATORY)** - Product positioning, messaging, user-facing content
10. **Acceptance Criteria** - Business acceptance, technical acceptance, quality assurance
11. **Constraints & Assumptions** - Business/technical/external constraints, key assumptions
12. **Risk Assessment** - High-risk items, risk mitigation plan
13. **Success Definition** - Go-live criteria, post-launch validation, measurement timeline
14. **Stakeholders & Communication** - Core team, stakeholders, communication plan
15. **Implementation Approach** - Development phases, testing strategy
16. **Budget & Resources** - Development/operational budget, resource requirements
17. **Traceability** - Upstream sources, downstream artifacts, traceability tags, validation evidence
18. **References** - Internal documentation, external standards, domain references, technology references

**Critical Notes**:
- All 19 sections are MANDATORY with explicit numbering (## 0. Title, ## 1. Title, etc.)
- section 9 (Customer-Facing Content) is blocking requirement - must contain substantive content
- section 7 (User Stories) must include layer separation scope note

---

## 3. Document Control Requirements

**Position**: Must be the first section at the very top of the PRD (before all numbered sections)

**Required Fields** (11 mandatory):
- Document ID: PRD-XXX format in H1 header
- Version: Semantic versioning (X.Y.Z)
- Status: Draft / Review / Approved / Implemented
- Date Created: YYYY-MM-DD format
- Last Updated: YYYY-MM-DD format
- Author: [Product Manager/Owner Name]
- Reviewer: [Technical Reviewer Name]
- Approver: [Stakeholder Name]
- BRD Reference: @brd: BRD-XXX tag
- SYS-Ready Score: Format `✅ NN% (Target: ≥90%)`
- EARS-Ready Score: Format `✅ NN% (Target: ≥90%)`

**Also Required**: Document Revision History table with at least one initial entry

**Template**:
```markdown
| Item | Details |
|------|---------|
| **Status** | Draft / Review / Approved / Implemented |
| **Version** | [Semantic version, e.g., 1.0.0] |
| **Date Created** | YYYY-MM-DD |
| **Last Updated** | YYYY-MM-DD |
| **Author** | [Product Manager/Owner Name] |
| **Reviewer** | [Technical Reviewer Name] |
| **Approver** | [Stakeholder Name] |
| **BRD Reference** | @brd: BRD-NNN |
| **SYS-Ready Score** | ✅ 95% (Target: ≥90%) |
| **EARS-Ready Score** | ✅ 95% (Target: ≥90%) |

### Document Revision History

| Version | Date | Author | Changes Made | Approver |
|---------|------|--------|--------------|----------|
| 1.0.0 | [Date] | [Name] | Initial draft | |
```

---

## 4. ID and Naming Standards

- **Filename**: `PRD-NNN_descriptive_title.md` (e.g., `PRD-001_external_api_integration.md`)
- **H1 Header**: `# PRD-NNN: [Descriptive Product Name/Feature Name]`
- **Document Title**: Include in H1 as subtitle (e.g., "PRD-001: External API Integration")
- **ID Format**: PRD-NNN (3-digit sequential), PRD-NNN-YY for multi-part documents
- **Uniqueness Rule**: Each NNN number unique across all PRDs

---

## 5. Product Requirements Principles

- **Business-Value Focused**: Product needs drive requirements, not technical solutions
- **Measurable Outcomes**: All requirements include quantifiable success measures
- **User-Centered**: Requirements based on user needs and business objectives
- **Testable Acceptance**: Business stakeholder-verifiable acceptance criteria
- **Implementation-Agnostic**: Requirements don't dictate specific technical approaches

---

## 6. User Stories & User Roles

**Purpose**: Define PRD-level user roles and story summaries. Detailed behavioral scenarios belong in EARS (Layer 3) and BDD tests (Layer 4).

**Layer Separation**:
- **PRD (Layer 2)**: User role definitions, story titles, capability requirements
- **EARS (Layer 3)**: Detailed behavioral scenarios with technical specifications
- **BDD (Layer 4)**: Executable test cases with Given-When-Then format

### User Roles

Define who the users are (personas):
- User characteristics and demographics
- User needs and goals
- Pain points and motivations
- NO technical implementation details

### User Stories

**Format**: "As a [role], I want [capability] so that [benefit]"

**PRD-Level Content** (✅ INCLUDE):
- High-level story titles
- Story summaries (2-3 sentences max)
- Product-level acceptance criteria (what, not how)
- Business value justification

**NOT PRD-Level** (❌ EXCLUDE):
- EARS-level specifications (WHEN-THE-SHALL-WITHIN format) → belongs in EARS
- BDD-level test scenarios (Given-When-Then) → belongs in BDD
- Technical implementation details → belongs in SYS/REQ
- System architecture decisions → belongs in ADR

### Scope Note

**MANDATORY**: Include this note in PRD section 7:

> This section provides role definitions and story summaries. Detailed behavioral requirements are captured in EARS; executable test specifications are in BDD feature files.

---

## 7. Architecture Decision Requirements

Every PRD must include section 17 (Traceability) with "Architecture Decision Requirements" subsection

**Purpose**: Identifies architectural topics requiring formal evaluation BEFORE progression to SYS phase

**Requirements**:
1. section exists and has table with columns: Topic Area, Decision Needed, Business Driver, Key Considerations
2. Table includes decision topics that will become formal ADRs in later workflow phase
3. Topics must have clear business rationale linked to PRD requirements

**Example**:
```markdown
#### Architecture Decision Requirements

| Topic Area | Decision Needed | Business Driver (PRD Reference) | Key Considerations |
|------------|-----------------|--------------------------------|-------------------|
| [Topic 1] | [What decision is needed] | [Which PRD requirements drive this] | [Technologies, patterns, approaches] |
| [Topic 2] | [What decision is needed] | [Which PRD requirements drive this] | [Technologies, patterns, approaches] |
```

---

## 8. Customer-Facing Content & Messaging (MANDATORY)

**Status**: MANDATORY - blocking error if missing or contains only placeholder text

**Purpose**: Define all customer-visible content, messaging, and communication materials.

### Required Content Categories

At least 3 of the following categories must be addressed with substantive content:

1. **Product Positioning Statements** - Core value proposition, competitive differentiation
2. **Key Messaging Themes** - Primary messaging pillars, supporting points
3. **Feature Descriptions for Marketing** - Customer-facing names and benefit-focused descriptions
4. **User-Facing Documentation Requirements** - User guides, tutorials, FAQs
5. **Help Text and Tooltips** - In-application guidance, contextual help
6. **Error Messages (User-Visible)** - Error templates, user-friendly explanations, recovery actions
7. **Success Confirmations** - Completion messages, progress indicators
8. **Onboarding Content** - Welcome messages, feature discovery flows
9. **Release Notes Template** - Format for new features, bug fixes, known issues

### Quality Standards

All customer-facing content must meet:
- **Clear, concise language**: Avoid jargon and technical terms
- **Consistent tone and voice**: Align with brand guidelines
- **Accessible to target audience**: Match user comprehension level
- **Measurable impact on user experience**: Define success metrics

### Validation Requirements

- section 9 header must include (MANDATORY) designation
- Content must be substantive (no "TBD", "TODO", or placeholder-only text)
- Minimum 3 content categories addressed
- Quality standards applied to all content

---

## 9. ADR Relationship Guidelines

**CRITICAL DISTINCTION**: PRDs are created BEFORE ADRs in SDD workflow

❌ **NEVER** reference specific ADR numbers (ADR-012, ADR-033, etc.) in PRD documents

✅ **DO** include "Architecture Decision Requirements" subsection listing topics for architectural decisions

**Workflow Order**:
1. BRD identifies architecture topics requiring decisions
2. PRD inherits and refines architectural topics from BRD
3. ADRs document which option was chosen and WHY
4. This separation maintains clear workflow phases and prevents broken references

---

## 10. SYS-Ready Scoring System

### Overview
SYS-ready scoring measures PRD maturity and readiness for progression to System Requirements (SYS) phase in SDD workflow. Minimum score of 90% required to advance to SYS creation.

**Format**: `✅ NN% (Target: ≥90%)`
**Location**: Document Control table (required field)
**Validation**: Enforced before commit via validation checks

### Scoring Criteria

**Product Requirements Completeness (40%)**:
- All 19 sections present and populated: 10%
- Business goals include measurable KPIs: 10%
- Acceptance criteria with business stakeholder validation: 10%
- Stakeholder analysis and communication plan complete: 10%

**Technical Readiness (30%)**:
- System boundaries and integration points defined: 10%
- Non-functional requirements quantified (performance, security, etc.): 10%
- Architecture Decision Requirements table populated: 10%

**Business Alignment (20%)**:
- ROI and business case validated with metrics: 5%
- Competitive and market analysis complete: 5%
- Success metrics tied to business objectives: 5%
- Risk mitigation strategies documented: 5%

**Traceability (10%)**:
- Upstream BRD references with specific sections: 5%
- Downstream links to planned artifacts: 5%

### Quality Gate Enforcement
- **Blocking Validation**: Score <90% prevents progression to SYS phase
- **Format Validation**: Must follow exact format with ✅ emoji and percentage
- **Threshold Enforcement**: ≥90% required for SYS-ready status

---

## 11. EARS-Ready Scoring System

### Overview
EARS-ready scoring measures PRD maturity and readiness for progression to Engineering Requirements (EARS) phase in SDD workflow. Minimum score of 90% required to advance to EARS creation.

**Format**: `✅ NN% (Target: ≥90%)`
**Location**: Document Control table (required field)
**Validation**: Enforced before commit via validation checks

### Scoring Criteria

**Business Requirements Clarity (40%)**:
- Business objectives follow SMART criteria with measurable targets: 15%
- Functional requirements provide capability definitions for EARS statements: 15%
- Acceptance criteria are quantifiable and business-focused: 10%

**Requirements Maturity (35%)**:
- System boundaries and integration points clearly defined: 15%
- Stakeholder requirements and success criteria specified: 10%
- Problem statement and business impact clearly articulated: 10%

**EARS Translation Readiness (20%)**:
- User journeys and workflows documented for behavioral requirements: 10%
- Non-functional requirements quantified (performance, reliability): 10%

**Strategic Alignment (5%)**:
- References to domain-specific business logic documents: 5%

### Quality Gate Enforcement
- **Blocking Validation**: Score <90% prevents progression to EARS phase
- **Format Validation**: Must follow exact format with ✅ emoji and percentage
- **Threshold Enforcement**: ≥90% required for EARS-ready status

---

## 12. Traceability Requirements (MANDATORY - Layer 2)

- **Upstream Sources**: Must reference BRD business requirements and strategy documents
- **Downstream Artifacts**: Map to SYS, EARS, BDD, REQ sequences
- **Strategy References**: Include specific sections from domain-specific business logic documents
- **Business Rationale**: Each requirement includes business justification
- **Acceptance Criteria**: Verifiable by business stakeholders

**Required Traceability Elements**:
- **Upstream Sources**: Business strategy documents
- **Downstream Artifacts**: SYS, EARS, BDD, REQ, ADR (topics only)
- **Anchors/IDs**: Unique identifiers within document
- **Code Path(s)**: Strategic impact area

**Traceability Tags (Cumulative Tagging Hierarchy - Layer 2)**:
```markdown
@brd: BRD-NNN:REQUIREMENT-ID
```

---

## 13. Business Objectives and Success Criteria

### Business Goals Format
All business objectives follow SMART criteria and include:
- Specific, measurable outcomes
- Clear success metrics and KPIs
- Time-bound delivery dates
- Business value justification

### Acceptance Criteria Standards
- **Business-Focused**: Verifiable by product owners and business stakeholders
- **Quantifiable**: Include specific thresholds and measurements
- **Comprehensive**: Cover success paths and failure scenarios
- **Testable**: Enable validation without technical implementation details

---

## 14. Quality Gates (Pre-Commit Validation)

- **Multiple Validation Checks**: Run `./scripts/validate_prd_template.sh filename.md`
- **Blockers**: Missing sections, invalid formats, incomplete SYS-ready score, broken traceability
- **Warnings**: Incomplete sections, missing references, unverified assumptions
- **SYS-Ready Threshold**: ≥90% required for progression to SYS phase
- **Link Resolution**: All traceability links must resolve to existing files

---

## 15. Additional Requirements

- **Business Language**: Use business terminology over technical jargon
- **Financial Quantification**: Include cost-benefit analysis and ROI calculations
- **Stakeholder Validation**: Define clear communication and approval processes
- **Scope Management**: Explicit in-scope and out-of-scope definitions
- **Implementation Planning**: High-level development phases and testing strategies

---

## Quick Reference

**Pre-Commit Validation**:
```bash
# Validate single file
./scripts/validate_prd_template.sh docs/PRD/PRD-001_product_requirements.md

# Validate all PRD files
find docs/PRD -name "PRD-*.md" -exec ./scripts/validate_prd_template.sh {} \;
```

**Template Location**: [PRD-TEMPLATE.md](PRD-TEMPLATE.md)
**Validation Rules**: [PRD-VALIDATION_RULES.md](PRD-VALIDATION_RULES.md)
**Index**: [PRD-000_index.md](PRD-000_index.md)

---

**Framework Compliance**: 100% doc_flow SDD framework aligned (Layer 2 - Product Requirements)
**Maintained By**: Product Management Team, SDD Framework Team
**Review Frequency**: Updated with template and validation rule enhancements

---
