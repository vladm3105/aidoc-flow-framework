# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of PRD-TEMPLATE.md
# - Authority: PRD-TEMPLATE.md is the single source of truth for PRD structure
# - Purpose: AI guidance for document creation (derived from template)
# - On conflict: Defer to PRD-TEMPLATE.md
# =============================================================================
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

> **📋 Document Role**: This is a **CREATION HELPER** for PRD-TEMPLATE.md.
> - **Authority**: `PRD-TEMPLATE.md` is the single source of truth for PRD structure
> - **Validation**: Use `PRD_VALIDATION_RULES.md` after PRD creation/changes
>
> **⚠️ Numbering Note**: This document's Table of Contents uses rule category numbers (0-15),
> which are different from PRD section numbers (1-21). Always refer to PRD-TEMPLATE.md for
> actual PRD section structure.

# PRD Creation Rules

**Version**: 2.1
**Date**: 2025-11-26
**Last Updated**: 2025-11-30
**Source**: Extracted from PRD-TEMPLATE.md, PRD-VALIDATION_RULES.md, README.md, and PRD-000_index.md
**Purpose**: Complete reference for creating PRD files according to doc-flow SDD framework
**Changes**: Updated to 21-section structure (1-21) with Section 20 (EARS Enhancement Appendix) and Section 21 (Quality Assurance & Testing Strategy). Previous: 19-section structure (0-18)

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
16. [Upstream Artifact Verification Process](#16-upstream-artifact-verification-process)
17. [Template Variant Selection](#17-template-variant-selection)
18. [EARS-Ready Requirements](#18-ears-ready-requirements)
19. [Threshold Registry Integration](#19-threshold-registry-integration)
20. [Feature ID Naming Standard](#20-feature-id-naming-standard)

---

## 1. Document Control

Note: Some examples in this guide show a portable `docs/` root. In this repository, artifact folders live at the ai_dev_flow root without the `docs/` prefix; see README → “Using This Repo” for path mapping.

**Purpose**: Establishes document metadata, versioning, and dual scoring requirements for PRD quality gates.

**Position**: Must be section 1 at the very beginning of PRD (before all numbered sections)

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
| BRD Reference | @brd: BRD.NN.EE.SS tag | MANDATORY |
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
## 1. Document Control

| Item | Details |
|------|---------|
| **Status** | Draft / Review / Approved / Implemented |
| **Version** | [Semantic version, e.g., 1.0.0] |
| **Date Created** | YYYY-MM-DD |
| **Last Updated** | YYYY-MM-DD |
| **Author** | [Product Manager/Owner Name] |
| **Reviewer** | [Technical Reviewer Name] |
| **Approver** | [Stakeholder Name] |
| **BRD Reference** | @brd: BRD.NN.EE.SS |
| **SYS-Ready Score** | ✅ 95% (Target: ≥90%) |
| **EARS-Ready Score** | ✅ 95% (Target: ≥90%) |
```

### Status and Ready Score Mapping

| Ready Score | Required Status |
|-------------|-----------------|
| >= 90% | Approved |
| 70-89% | In Review |
| < 70% | Draft |

**Note**: For PRD documents with dual scores (SYS-Ready + EARS-Ready), use the lower score to determine status.

---

## 1. File Organization and Directory Structure

- **Location**: `docs/PRD/PRD-NN_{slug}/` within project docs directory (nested folder per document with descriptive slug)
- **Folder Naming**: `PRD-NN_{slug}/` where slug MUST match the index file slug
- **Folder Structure** (DEFAULT): `docs/PRD/PRD-NN_{slug}/PRD-NN.S_{slug}.md`
  - Index file: `docs/PRD/PRD-NN_{slug}/PRD-NN.0_{slug}_index.md`
  - Section files: `docs/PRD/PRD-NN_{slug}/PRD-NN.1_{slug}_executive_summary.md`, etc.
- **Section Files**: Section-based structure is DEFAULT for all PRD documents. Use format: `PRD-NN.S_{slug}_section_title.md` (S = section number). See `ID_NAMING_STANDARDS.md` for metadata tags.
- **Monolithic** (OPTIONAL for <25KB): `docs/PRD/PRD-NN_{slug}/PRD-NN.0_{slug}.md` (single file in folder)
- **Subdocuments**: For complex business features: `PRD-NN-YY_{additional_detail}.md` (YY = 2-digit sub-number)

---

## 2. Document Structure (Required sections)

Every PRD must contain these exact 21 sections (1-21) in order. Section numbering must be explicit in all headers.

#### Required Sections in Order (21 total):

1. **Document Control** - Metadata, versioning, dual scoring (SYS-Ready + EARS-Ready ≥90%)
2. **Executive Summary** - Business value and timeline overview
3. **Problem Statement** - Current state, business impact, opportunity assessment
4. **Target Audience & User Personas** - Primary users, secondary users, business stakeholders
5. **Success Metrics (KPIs)** - Primary KPIs, secondary KPIs, success criteria by phase
6. **Goals & Objectives** - Primary business goals, secondary objectives, stretch goals
7. **Scope & Requirements** - In scope features, out of scope items, dependencies, assumptions
8. **User Stories & User Roles** - Role definitions, story summaries (PRD-level only, no EARS/BDD detail)
9. **Functional Requirements** - User journey mapping, capability requirements
10. **Customer-Facing Content & Messaging (MANDATORY)** - Product positioning, messaging, user-facing content
11. **Acceptance Criteria** - Business acceptance, technical acceptance, quality assurance
12. **Constraints & Assumptions** - Business/technical/external constraints, key assumptions
13. **Risk Assessment** - High-risk items, risk mitigation plan
14. **Success Definition** - Go-live criteria, post-launch validation, measurement timeline
15. **Stakeholders & Communication** - Core team, stakeholders, communication plan
16. **Implementation Approach** - Development phases, testing strategy
17. **Budget & Resources** - Development/operational budget, resource requirements
18. **Traceability** - Upstream sources, downstream artifacts, traceability tags, validation evidence
19. **References** - Internal documentation, external standards, domain references, technology references
20. **EARS Enhancement Appendix** - EARS pattern templates and requirement syntax guidance
21. **Quality Assurance & Testing Strategy** - QA standards, testing strategy (moved from BRD)

**Critical Notes**:
- All 21 sections are MANDATORY with explicit numbering (## 1. Title, ## 2. Title, etc.)
- Section 10 (Customer-Facing Content) is blocking requirement - must contain substantive content
- Section 8 (User Stories) must include layer separation scope note
- Section 21 (QA & Testing Strategy) moved from BRD-TEMPLATE.md as technical QA belongs at product level

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
- BRD Reference: @brd: BRD.NN.EE.SS tag
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
| **BRD Reference** | @brd: BRD.NN.EE.SS |
| **SYS-Ready Score** | ✅ 95% (Target: ≥90%) |
| **EARS-Ready Score** | ✅ 95% (Target: ≥90%) |

### Document Revision History

| Version | Date | Author | Changes Made | Approver |
|---------|------|--------|--------------|----------|
| 1.0.0 | [Date] | [Name] | Initial draft | |
```

---

## 4. ID and Naming Standards

- **Filename**: `PRD-NN_descriptive_title.md` (e.g., `PRD-01_external_api_integration.md`)
- **H1 Header**: `# PRD-NN: [Descriptive Product Name/Feature Name]`
- **Document Title**: Include in H1 as subtitle (e.g., "PRD-01: External API Integration")
- **ID Format**: PRD-NN (3-digit sequential), PRD-NN-YY for multi-part documents
- **Uniqueness Rule**: Each NN number unique across all PRDs

### 4.1 Element ID Format (MANDATORY)

**Pattern**: `PRD.{DOC_NUM}.{ELEM_TYPE}.{SEQ}` (4 segments, dot-separated)

| Element Type | Code | Example |
|--------------|------|---------|
| Functional Requirement | 01 | PRD.02.01.01 |
| Quality Attribute | 02 | PRD.02.02.01 |
| Constraint | 03 | PRD.02.03.01 |
| Assumption | 04 | PRD.02.04.01 |
| Dependency | 05 | PRD.02.05.01 |
| **Acceptance Criteria** | **06** | **PRD.02.06.01** |
| Risk | 07 | PRD.02.07.01 |
| Metric | 08 | PRD.02.08.01 |
| User Story | 09 | PRD.02.09.01 |
| Use Case | 11 | PRD.02.11.01 |
| Feature Item | 22 | PRD.02.22.01 |
| Stakeholder Need | 24 | PRD.02.24.01 |

> ⚠️ **REMOVED PATTERNS** - Do NOT use:
> - `AC-XXX` → Use `PRD.NN.06.SS`
> - `FR-XXX` → Use `PRD.NN.01.SS`
> - `BC-XXX` → Use `PRD.NN.03.SS`
> - `BA-XXX` → Use `PRD.NN.04.SS`
> - `QA-XXX` → Use `PRD.NN.02.SS`
> - `RISK-XXX` → Use `PRD.NN.07.SS`
> - `METRIC-XXX` → Use `PRD.NN.08.SS`
> - `Feature F-XXX` → Use `PRD.NN.09.SS`
>
> **Reference**: `ai_dev_flow/ID_NAMING_STANDARDS.md` lines 783-793

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

**MANDATORY**: Include this note in PRD section 8:

> This section provides role definitions and story summaries. Detailed behavioral requirements are captured in EARS; executable test specifications are in BDD feature files.

---

## 7. Architecture Decision Requirements

Every PRD must include Section 18 (Traceability) with "Architecture Decision Requirements" subsection that **elaborates** BRD Section 7.2 topics with technical content.

**Purpose**: PRD adds **technical evaluation details** to business-only topics defined in BRD Section 7.2

### 7.1 Layer Separation Principle

```
BRD Section 7.2          →    PRD Section 18         →    ADR
(WHAT & WHY)                  (HOW to evaluate)          (Final decision)
─────────────────────────────────────────────────────────────────────────
Business drivers              Technical options          Selected option
Business constraints          Evaluation criteria        Trade-off analysis
                              Product constraints        Consequences
```

### 7.2 PRD Elaboration Workflow

**Step 1**: Read BRD Section 7.2 topics (format: `{DOC_TYPE}.NN.EE.SS`)

**Step 2**: For each BRD topic, create corresponding PRD subsection:

| PRD Section 18 Field | Content Source | Example |
|---------------------|----------------|---------|
| **Upstream** | BRD reference | "BRD-01 §7.2.3" |
| **Technical Options** | Product team research | "1. Modern Treasury (SaaS), 2. Custom PostgreSQL, 3. TigerBeetle" |
| **Evaluation Criteria** | Measurable targets | "Throughput ≥10K TPS, Latency <100ms P99" |
| **Product Constraints** | Integration/technical limits | "Must support Python SDK" |
| **Decision Timeline** | Milestone reference | "Before Phase 2 start" |
| **ADR Requirements** | Guidance for ADR | "Select option based on evaluation. Document trade-offs." |

### 7.3 Required Subsection Structure

```markdown
##### {DOC_TYPE}.NN.EE.SS: [Topic Name]

**Upstream**: BRD-NN §7.2.X

**Technical Options**:
1. **[Option A]**: [Description]
2. **[Option B]**: [Description]
3. **[Option C]**: [Description]

**Evaluation Criteria**:
- **[Criterion 1]**: [Measurable target]
- **[Criterion 2]**: [Measurable target]

**Product Constraints**:
- [Constraint 1]
- [Constraint 2]

**Decision Timeline**: [Milestone reference]

**ADR Requirements**: [What ADR must decide for THIS topic]
```

### 7.4 Content Guidelines

**Include in PRD Section 18** (Technical Content):

| Content Type | Description | Example |
|--------------|-------------|---------|
| Technical options | Technology alternatives | "Modern Treasury, Custom PostgreSQL, TigerBeetle" |
| Evaluation criteria | Measurable targets | "≥10,000 TPS sustained" |
| Product constraints | Integration requirements | "Must support existing Python codebase" |
| Technical timelines | Decision milestones | "Before Phase 2 development" |

**Exclude from PRD Section 18** (Keep in BRD §7.2):

| Content Type | Why | Where It Is |
|--------------|-----|-------------|
| Business drivers | Business justification | BRD §7.2 "Business Driver" |
| Business constraints | Non-negotiable rules | BRD §7.2 "Business Constraints" |
| Regulatory constraints | Compliance requirements | BRD §7.2 "Business Constraints" |
| Budget constraints | Financial limits | BRD §7.2 "Business Constraints" |

### 7.5 Example (Full Elaboration)

**BRD Section 7.2 (Business-Only)**:
```markdown
#### BRD.01.01.03: Ledger System Selection

**Business Driver**: Real-time position visibility for treasury management (BRD.01.01.04)
**Business Constraints**:
- Multi-currency support (e.g., multiple currencies) per Section 3.2
- 5-year audit retention per compliance requirements
- Max [Budget] annual licensing
```

**PRD Section 18 (Technical Elaboration)**:
```markdown
##### BRD.01.01.03: Ledger System Selection

**Upstream**: BRD-01 §7.2.3

**Technical Options**:
1. **Modern Treasury**: Managed SaaS, REST API, SOC 2 certified
2. **Custom PostgreSQL**: Double-entry schema, pgaudit, self-managed
3. **TigerBeetle**: High-performance financial DB, ACID guarantees

**Evaluation Criteria**:
- **Throughput**: ≥10,000 TPS sustained
- **Latency**: <100ms P99 for balance queries
- **Compliance**: SOC 2 Type II or equivalent

**Product Constraints**:
- Must integrate with existing FastAPI payment service
- Must support Python SDK or REST API

**Decision Timeline**: Before Phase 2 development start (Q1 2026)

**ADR Requirements**: [What ADR must decide for THIS topic - e.g., "Select one option based on evaluation. Document trade-offs and rollback strategy."]
```

**Reference**: See `ai_dev_flow/PRD/PRD-TEMPLATE.md` Section 18 for template

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

### 9.1 Forward Reference Validation (FWDREF)

PRD (Layer 2) documents are subject to automated forward reference validation. The validator prevents references to specific downstream document IDs.

**SDD Layer Hierarchy**:

| Layer | Artifact | PRD Can Reference |
|-------|----------|-------------------|
| 1 | BRD | ✅ Yes |
| 2 | PRD | ✅ Yes (same layer) |
| 3 | EARS | ❌ No - created after PRD |
| 4 | BDD | ❌ No - created after PRD |
| 5 | ADR | ❌ No - created after PRD |
| 6+ | SYS, REQ, etc. | ❌ No - created after PRD |

**Validation Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| FWDREF-E001 | Error | PRD references specific downstream ID (e.g., ADR-01) that doesn't exist |
| FWDREF-E002 | Error | Referenced downstream document does not exist in filesystem |
| FWDREF-W001 | Warning | PRD claims count of downstream documents (e.g., "5 ADRs required") |

**Examples**:

❌ **INCORRECT** (triggers FWDREF-E001):
```markdown
See ADR-01 through ADR-05 for implementation details.
@adr: ADR-01, ADR-02
The database selection is documented in ADR-003.
```

✅ **CORRECT** (describes needs without specific IDs):
```markdown
Architecture decisions required for:
- Database technology selection (PostgreSQL vs MongoDB vs TimescaleDB)
- Caching strategy (Redis vs in-memory vs hybrid)
- API versioning approach (URL path vs header vs query parameter)

Section 18 identifies topics requiring formal ADR documentation.
```

**Running Validation**:
```bash
# Validate single PRD
python ai_dev_flow/scripts/validate_forward_references.py docs/PRD/PRD-01_slug.md

# Validate all PRDs
python ai_dev_flow/scripts/validate_forward_references.py docs/PRD/
```

**Reference**: See [VALIDATION_STANDARDS.md](../VALIDATION_STANDARDS.md) for complete error code registry.

---

## 10. SYS-Ready Scoring System

### Overview
SYS-ready scoring measures PRD maturity and readiness for progression to System Requirements (SYS) phase in SDD workflow. Minimum score of 90% required to advance to SYS creation.

**Format**: `✅ NN% (Target: ≥90%)`
**Location**: Document Control table (required field)
**Validation**: Enforced before commit via validation checks

### Scoring Criteria

**Product Requirements Completeness (40%)**:
- All 21 sections present and populated: 10%
- Business goals include measurable KPIs: 10%
- Acceptance criteria with business stakeholder validation: 10%
- Stakeholder analysis and communication plan complete: 10%

**Technical Readiness (30%)**:
- System boundaries and integration points defined: 10%
- Quality attributes quantified (performance, security, etc.): 10%
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
- Quality attributes quantified (performance, reliability): 10%

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
@brd: BRD.NN.EE.SS
```

**Same-Type References (Conditional)**:

Include ONLY if relationships exist between PRD documents sharing domain context or implementation dependencies.

| Relationship | Document ID | Document Title | Purpose |
|--------------|-------------|----------------|---------|
| Related | PRD-NN | [Related PRD title] | Shared domain context |
| Depends | PRD-NN | [Prerequisite PRD title] | Must complete before this |

**Tags**:
```markdown
@related-prd: PRD-NN
@depends-prd: PRD-NN
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

- **Multiple Validation Checks**: Run `python scripts/validate_prd.py filename.md`
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
python scripts/validate_prd.py docs/PRD/PRD-01_product_requirements.md

# Validate all PRD files
find docs/PRD -name "PRD-*.md" -exec python scripts/validate_prd.py {} \;
```

**Template Location**: [PRD-TEMPLATE.md](PRD-TEMPLATE.md)
**Validation Rules**: [PRD-VALIDATION_RULES.md](PRD-VALIDATION_RULES.md)
**Index**: [PRD-000_index.md](PRD-000_index.md)

---

**Framework Compliance**: 100% AI Dev Flow SDD framework aligned (Layer 2 - Product Requirements)
**Maintained By**: Product Management Team, SDD Framework Team
**Review Frequency**: Updated with template and validation rule enhancements

---


## 16. Upstream Artifact Verification Process

### Before Creating This Document

**Step 1: Inventory Existing Upstream Artifacts**

```bash
# List existing upstream artifacts for this layer
ls -la docs/BRD/    # Layer 1
ls -la docs/PRD/    # Layer 2
ls -la docs/EARS/   # Layer 3
ls -la docs/BDD/    # Layer 4
ls -la docs/ADR/    # Layer 5
ls -la docs/SYS/    # Layer 6
ls -la docs/REQ/    # Layer 7
# ... continue for applicable layers
```

**Step 2: Map Existing Documents to Traceability Tags**

| Tag | Required for This Layer | Existing Document | Action |
|-----|------------------------|-------------------|--------|
| @brd | Yes/No | BRD-01 or null | Reference/Create/Skip |
| @prd | Yes/No | PRD-01 or null | Reference/Create/Skip |
| ... | ... | ... | ... |

**Step 3: Decision Rules**

| Situation | Action |
|-----------|--------|
| Upstream exists | Reference with exact document ID |
| Upstream required but missing | Skip that functionality - do NOT implement |
| Upstream optional and missing | Use `null` in traceability tag |
| Upstream not applicable | Omit tag entirely |

### Traceability Tag Rules

- **NEVER** use placeholder IDs like `BRD-XXX` or `TBD`
- **NEVER** reference documents that don't exist
- **ALWAYS** verify document exists before adding reference
- **USE** `null` only when artifact type is genuinely not applicable

---

## 17. Template Variant Selection

**Purpose**: Guide PRD authors to select the appropriate template variant based on the domain and complexity of the product requirements.

### Template Variants

PRDs vary in structure based on domain. Select the appropriate variant at PRD creation time.

| Variant | Section Count | Primary Use Case | Key Differences |
|---------|---------------|------------------|-----------------|
| **Standard** | 21 sections (1-21) | Business features, core platform, user-facing products | Full template with comprehensive business analysis |
| **Agent-Based** | 12-15 sections | ML/AI agents, intelligent systems, autonomous processes | Extended ML metrics, state machine focus, A2A protocol |
| **Automation-Focused** | 9-12 sections | n8n workflows, event processing, integrations | Webhook-focused, workflow states, trigger/action pairs |

### Selection Criteria Flowchart

```
START: What is the primary domain of this PRD?
│
├─► ML/AI Agent or Intelligent System?
│   └─► YES → Use **Agent-Based** template
│
├─► n8n Workflow or Event-Driven Automation?
│   └─► YES → Use **Automation-Focused** template
│
└─► Business Feature, Core Platform, or User-Facing Product?
    └─► YES → Use **Standard** template (default)
```

### Template Variant Field

Add template variant to Document Control:

```markdown
| **Template Variant** | Standard / Agent-Based / Automation-Focused |
```

### Variant-Specific Sections

**Standard Template (21 sections)**:
- Sections 1-21 as defined in PRD-TEMPLATE.md
- Full EARS Enhancement Appendix (Section 20)
- Quality Assurance & Testing Strategy (Section 21)

**Agent-Based Template (15 sections)**:
- Sections 0-14: Core PRD structure
- Agent-specific additions:
  - Agent State Machine (extended beyond standard)
  - ML Model Requirements (training data, inference, drift)
  - A2A Protocol Requirements (agent communication)
  - Confidence/Threshold Metrics (ML-specific scoring)
- May omit: Budget & Resources (Section 16) if agent is part of larger system

**Automation-Focused Template (12 sections)**:
- Sections 0-11: Core PRD structure focused on workflows
- Automation-specific additions:
  - Trigger/Event Documentation (webhook schemas)
  - Workflow State Machine (n8n node flow)
  - Integration Mapping (connected services)
- May omit: User Stories (Section 8) if no direct user interaction
- May omit: Customer-Facing Content (Section 9) if internal automation

### Migration Notes

**Converting between variants**:
- To expand: Add missing sections from Standard template
- To simplify: Archive (not delete) sections not applicable to variant
- Always maintain: Document Control, Traceability, References

---

## 18. EARS-Ready Requirements

**Purpose**: Define the requirements for achieving EARS-Ready status (≥90% score), ensuring PRDs contain sufficient detail for EARS (Engineering Requirements Specification) creation.

### EARS Readiness Criteria

For a PRD to be EARS-Ready, it must contain:

| Criterion | Requirement | Weight |
|-----------|-------------|--------|
| **Timing Profiles** | All operations have p50/p95/p99 specifications | 25% |
| **Boundary Values** | All thresholds have explicit ≥/>/</<= operators | 25% |
| **State Machine** | Complete state diagram with error transitions | 25% |
| **Fallback Paths** | All external dependencies have failure modes | 15% |
| **Threshold Registry** | Numeric values reference centralized registry | 10% |

### Timing Profile Requirements (25%)

**Mandatory for EARS-Ready**:
- Every operation that has a timing expectation must specify p50, p95, p99
- Replace vague terms with precise specifications:

| Vague Term | EARS-Compliant Alternative |
|------------|---------------------------|
| "real-time" | p50 <100ms, p95 <300ms, p99 <1000ms |
| "immediately" | <500ms from trigger event |
| "quickly" | <2 seconds response time |
| "fast" | Specify latency percentiles |

**Template**:
```markdown
| Operation | p50 | p95 | p99 | Unit | Notes |
|-----------|-----|-----|-----|------|-------|
| [name] | [value] | [value] | [value] | ms | [constraints] |
```

### Boundary Value Requirements (25%)

**Mandatory for EARS-Ready**:
- Every threshold must specify inclusive/exclusive boundary
- No ambiguous range notation

| Ambiguous | EARS-Compliant |
|-----------|---------------|
| ">$500" (what about ==$500?) | "≥$500" or ">$500 (exclusive)" |
| "between 30-70" | "[30, 70]" (inclusive) or "(30, 70)" (exclusive) |
| "up to 5 attempts" | "≤5 attempts" (inclusive) |

**Boundary Notation**:
- `≥`: greater than or equal (inclusive)
- `>`: greater than (exclusive)
- `[a, b]`: closed interval (a and b included)
- `(a, b)`: open interval (neither included)

### State Machine Requirements (25%)

**Mandatory for EARS-Ready**:
- Complete state diagram covering all possible states
- Error state transitions documented
- Recovery paths defined

**Required Transitions**:
1. Happy path → Success state
2. Happy path → Error state (failure scenarios)
3. Error state → Recovery/Retry
4. Recovery exhausted → Terminal state (manual review, cancellation)

**Anti-pattern** (causes EARS-Ready failure):
- Only documenting happy path states
- Missing timeout transitions
- No error recovery paths

### Fallback Path Requirements (15%)

**Mandatory for EARS-Ready**:
- Every external dependency has failure mode documentation
- Degraded operation behavior defined

**Required Documentation per Dependency**:
1. Failure mode (how it fails)
2. Detection method (how failure is detected)
3. Fallback behavior (what system does instead)
4. Recovery procedure (how to return to normal)

### Threshold Registry Requirements (10%)

**Mandatory for EARS-Ready**:
- Numeric thresholds reference centralized registry where applicable
- Use format: `@threshold: PRD.NN.{category}.{key}`

**When to Reference Registry**:
- KYC/KYB velocity limits
- Risk score thresholds
- Performance timing targets
- Timeout configurations
- Rate limits

---

## 19. Threshold Registry Integration

**Purpose**: Define rules for creating and referencing centralized threshold registries to prevent threshold conflicts across PRDs.

### When to Create a Threshold Registry

Create a dedicated Threshold Registry PRD when:
- 3+ PRDs reference the same threshold type (e.g., risk scores)
- Threshold conflicts have been identified during review
- Thresholds require multi-stakeholder approval (Product, Risk, Compliance)
- Centralized configuration management is required

### Threshold Registry Structure

**Registry PRD Structure** (see PRD-NN as example):
```markdown
## N. [Threshold Category]

### N.1 [Subcategory]

| Key | Value | Unit | Notes |
|-----|-------|------|-------|
| `category.subcategory.key` | [value] | [unit] | [description] |
```

### Reference Format

**In consuming PRDs**, reference registry thresholds using:

```markdown
@threshold: PRD.NN.{category}.{key}

Example: @threshold: PRD.035.kyc.l1.daily
```

### Key Naming Convention

| Level | Format | Example |
|-------|--------|---------|
| Category | lowercase, no spaces | `kyc`, `risk`, `perf`, `timeout` |
| Subcategory | lowercase, dot-separated | `kyc.l1`, `risk.high`, `perf.api` |
| Key | lowercase, dot-separated | `kyc.l1.daily`, `risk.high.min` |

### Benefits of Registry Pattern

1. **Single Source of Truth**: One location for all threshold values
2. **Conflict Prevention**: Eliminates discrepancies between PRDs
3. **Change Management**: Centralized updates propagate to all consumers
4. **Audit Trail**: Version-controlled threshold changes
5. **Cross-Team Visibility**: Risk, Compliance, Product see same values

### Registry Maintenance Rules

| Rule | Description |
|------|-------------|
| **Authority** | Registry PRD is authoritative for all threshold values |
| **Updates** | Changes require Product + Risk + Compliance approval |
| **Versioning** | Semantic versioning (MAJOR.MINOR.PATCH) |
| **No Duplicates** | Never define same threshold in multiple PRDs |
| **Reference Only** | Consumer PRDs reference, not duplicate |

---

## 20. Feature ID Naming Standard

**Purpose**: Establish consistent Feature ID naming convention across all PRDs to enable accurate traceability and cross-PRD references.

### Standard Format (Simple Numeric)

**Format**: `NN` (variable-length sequential number, minimum 2 digits)

| Component | Format | Description |
|-----------|--------|-------------|
| Feature ID | `NN` | 2+ digit sequential (01-99, then 100-999, 1000+) |
| Document Context | `PRD-NN` | PRD number provides namespace |

**Rationale**: The document context (PRD-01) already provides the namespace. Embedding the PRD number in the feature ID is redundant. Feature IDs match document ID numbering convention.

**Examples**:
- `01`: First feature (in any PRD)
- `15`: 15th feature
- `99`: 99th feature
- `100`: 100th feature (auto-expands)
- `1000`: 1000th feature

### Validation Regex

```regex
^\d{2,}$
```

### Cross-PRD Reference Format

When referencing features from other PRDs, use the cross-reference format:

```markdown
@prd: PRD.22.01.15
```

**Components**:
- `@prd:` - Tag prefix
- `PRD-NN` - Document ID (NN in element ID)
- `.01` - Element type (01 = Functional Requirement)
- `.15` - Sequence ID within document

**Uniqueness**: `PRD.22.01.15` is globally unique (PRD-022, Feature 015)

### Invalid Formats (Do NOT Use)

| Invalid Format | Issue | Correct Format |
|----------------|-------|----------------|
| `Feature-022-001` | Deprecated format | `PRD.22.01.01` |
| `FR-AGENT-001` | Non-standard prefix | `PRD.NN.01.01` |
| `Feature 3.1` | Text format | `PRD.25.01.03` |
| `PRD.1.1` | Not zero-padded | `PRD.01.01.01` |
| `F-01` | Deprecated F- format | `PRD.NN.01.01` |

### Common Mistakes to Avoid

| Mistake | Correct |
|---------|---------|
| `Status: Approved` (with 70% score) | `Status: In Review` (match status to score) |
| `@adr: ADR-012` (referencing ADR before it exists) | Omit ADR references in PRD (ADRs created after PRD) |
| Missing section numbering | Use explicit `## N. Section Title` format |
| Placeholder scores `✅ TBD%` | Calculate actual score before committing |
| Section 9 with only "TBD" | Substantive customer-facing content required |

### Migration Guide

For PRDs with non-standard Feature IDs:

1. **Inventory**: List all current Feature IDs
2. **Map**: Create mapping table (old → new)
3. **Update**: Replace old IDs with simple format
4. **Cross-Reference**: Update all documents using `@prd: PRD.NN.EE.SS` format
5. **Validate**: Run Feature ID validation script

**Mapping Example**:
| Old ID | New Unified ID | Cross-Reference |
|--------|----------------|-----------------|
| Feature-022-001 | PRD.22.01.01 | @prd: PRD.22.01.01 |
| FR-AGENT-001 | PRD.22.01.01 | @prd: PRD.22.01.01 |
| Feature 3.1 | PRD.25.01.03 | @prd: PRD.25.01.03 |
| F-01 | PRD.NN.01.01 | @prd: PRD.NN.01.01 |

### Benefits

1. **Simpler IDs**: Cleaner, shorter feature identifiers
2. **Namespace Separation**: Document context provides uniqueness
3. **Cross-Reference Clarity**: `@prd: PRD.22.01.15` format is explicit
4. **Validation**: Simple regex enables automated checking
5. **Consistency**: Aligns with ID_NAMING_STANDARDS.md

---

## 21. Cross-Document Validation (MANDATORY)

**CRITICAL**: Execute cross-document validation IMMEDIATELY after creating any PRD document. Do NOT proceed to downstream artifacts until validation passes.

### Automatic Validation Loop

```
LOOP:
  1. Run: python scripts/validate_cross_document.py --document {doc_path} --auto-fix
  2. IF errors fixed: GOTO LOOP (re-validate)
  3. IF warnings fixed: GOTO LOOP (re-validate)
  4. IF unfixable issues: Log for manual review, continue
  5. IF clean: Mark VALIDATED, proceed to next layer
```

### Validation Command

```bash
# Per-document validation (Phase 1)
python scripts/validate_cross_document.py --document docs/PRD/PRD-NN_slug.md --auto-fix

# Layer validation (Phase 2) - run when all PRD documents complete
python scripts/validate_cross_document.py --layer PRD --auto-fix
```

### Layer-Specific Upstream Requirements

| This Layer | Required Upstream Tags | Tag Count |
|------------|------------------------|-----------|
| PRD (Layer 2) | @brd | 1 |

### Auto-Fix Actions (No Confirmation Required)

| Issue | Fix Action |
|-------|------------|
| Missing @brd tag | Add with upstream BRD document reference |
| Invalid tag format | Correct to TYPE.NN.TT.SS or TYPE-NN format |
| Broken link | Recalculate path from current location |
| Missing traceability section | Insert from template |

### Validation Codes Reference

| Code | Description | Severity |
|------|-------------|----------|
| XDOC-001 | Referenced requirement ID not found | ERROR |
| XDOC-002 | Missing cumulative tag (@brd) | ERROR |
| XDOC-003 | Upstream document not found | ERROR |
| XDOC-006 | Tag format invalid | ERROR |
| XDOC-007 | Gap in cumulative tag chain | ERROR |
| XDOC-009 | Missing traceability section | ERROR |

### Quality Gate

**Blocking**: YES - Cannot proceed to EARS creation until Phase 1 validation passes with 0 errors.

---

## 22. BRD Input Document Handling (MANDATORY)

### Purpose

Define rules for consuming BRD documents as upstream input for PRD creation.

### Sectioned BRD Handling

BRD documents may be split into 19 section files (0-18) for AI context window management:

| Section | Content |
|---------|---------|
| 0 | Index |
| 1-18 | Introduction through Appendices |

**Critical Rules:**
1. Read ALL section files as ONE logical document
2. Sections are for AI context window management only
3. No BRD section → PRD section mapping exists
4. Extract information holistically across all sections

### Discovery Pattern

```
docs/BRD/BRD-NN_{slug}/
├── BRD-NN.0_index.md          <- Read first
├── BRD-NN.1_introduction.md    <- Read in order
├── ...
└── BRD-NN.18_appendices.md     <- Read last
```

### Extraction Guidelines

From BRD sections, extract for PRD:
- Business objectives → PRD Goals & Objectives
- User stories → PRD User Stories (summary level)
- Functional requirements → PRD Functional Requirements
- Quality attributes → PRD Quality Attributes
- Constraints → PRD Constraints & Assumptions
- Acceptance criteria → PRD Acceptance Criteria

### Traceability

- Reference entire BRD: `@brd: BRD-01`
- Reference specific elements: `@brd: BRD.01.01.05`
