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

**Version**: 1.0
**Date**: 2025-11-19
**Last Updated**: 2025-11-19
**Source**: Extracted from PRD-TEMPLATE.md, PRD-VALIDATION_RULES.md, README.md, and PRD-000_index.md
**Purpose**: Complete reference for creating PRD files according to doc-flow SDD framework
**Changes**: Added SYS-ready scoring system for PRD documents

---

## Table of Contents

1. [File Organization and Directory Structure](#1-file-organization-and-directory-structure)
2. [Document Structure (Required Sections)](#2-document-structure-required-sections)
3. [Document Control Requirements](#3-document-control-requirements)
4. [ID and Naming Standards](#4-id-and-naming-standards)
5. [Product Requirements Principles](#5-product-requirements-principles)
6. [Architecture Decision Requirements](#6-architecture-decision-requirements)
7. [ADR Relationship Guidelines](#7-adr-relationship-guidelines)
8. [SYS-Ready Scoring System](#8-sys-ready-scoring-system)
9. [EARS-Ready Scoring System](#9-ears-ready-scoring-system)
10. [Traceability Requirements](#10-traceability-requirements)
11. [Business Objectives and Success Criteria](#11-business-objectives-and-success-criteria)
12. [Quality Gates](#12-quality-gates)
13. [Additional Requirements](#13-additional-requirements)

---

## 1. File Organization and Directory Structure

- **Location**: `docs/PRD/` within project docs directory
- **Naming**: `PRD-NNN_descriptive_title.md` (NNN = 3-digit sequential number, snake_case slug)
- **Subdocuments**: For complex business features: `PRD-NNN-YY_additional_detail.md` (YY = 2-digit sub-number)

---

## 2. Document Structure (Required Sections)

Every PRD must contain these exact sections in order. Document Control is positioned at the very beginning (before all numbered sections).

**Document Control Section**: Located at the very beginning (before all numbered sections)

#### Required Sections in Order:

1. **Executive Summary** - Business value and timeline overview
2. **Problem Statement** - Current state, business impact, opportunity assessment
3. **Target Audience & User Personas** - Primary users, secondary users, business stakeholders
4. **Success Metrics (KPIs)** - Primary KPIs, secondary KPIs, success criteria by phase
5. **Goals & Objectives** - Primary business goals, secondary objectives, stretch goals
6. **Scope & Requirements** - In scope features, out of scope items, dependencies, assumptions
7. **Functional Requirements** - User journey mapping, capability requirements
8. **Acceptance Criteria** - Business acceptance, technical acceptance, quality assurance
9. **Constraints & Assumptions** - Business/technical/external constraints, key assumptions
10. **Risk Assessment** - High-risk items, risk mitigation plan
11. **Success Definition** - Go-live criteria, post-launch validation, measurement timeline
12. **Stakeholders & Communication** - Core team, stakeholders, communication plan
13. **Implementation Approach** - Development phases, testing strategy
14. **Budget & Resources** - Development/operational budget, resource requirements
15. **Traceability** - Upstream sources, downstream artifacts, traceability tags, validation evidence
16. **References** - Internal documentation, external standards, domain references, technology references

---

## 3. Document Control Requirements

**Position**: Must be the first section at the very top of the PRD (before all numbered sections)

**Required Fields** (7 mandatory):
- Project Name: [Enter project name]
- Document Version: [e.g., 1.0] (semantic versioning X.Y)
- Date: [Current date in YYYY-MM-DD format]
- Author: [Product Manager/Owner Name]
- Approver: [Stakeholder Name]
- Status: [Draft / Review / Approved / Implemented]
- SYS-Ready Score (⭐ NEW - v1.0): Format `✅ NN% (Target: ≥90%)`
- EARS-Ready Score (⭐ NEW - v1.0): Format `✅ NN% (Target: ≥90%)`

**Also Required**: Document Revision History table with at least one initial entry

**Template**:
```markdown
| Item | Details |
|------|---------|
| **Project Name** | [Enter project name] |
| **Document Version** | [e.g., 1.0] |
| **Date** | [Current date] |
| **Author** | [Product Manager/Owner Name] |
| **Approver** | [Stakeholder Name] |
| **Status** | [Draft / Review / Approved / Implemented] |
| **SYS-Ready Score** | ✅ 95% (Target: ≥90%) |

### Document Revision History

| Version | Date | Author | Changes Made | Approver |
|---------|------|--------|--------------|----------|
| 1.0 | [Date] | [Name] | Initial draft | |
| | | | | |
```

---

## 4. ID and Naming Standards

- **Filename**: `PRD-NNN_descriptive_title.md` (e.g., `PRD-001_alpha_vantage_integration.md`)
- **H1 Header**: `# PRD-NNN: [Descriptive Product Name/Feature Name]`
- **Document Title**: Include in H1 as subtitle (e.g., "PRD-001: Alpha Vantage Integration")
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

## 6. Architecture Decision Requirements

Every PRD must include Section 15.2 (Traceability) with "Architecture Decision Requirements" subsection

**Purpose**: Identifies architectural topics requiring formal evaluation BEFORE progression to SYS phase

**Requirements**:
1. Section exists and has table with columns: Topic Area, Decision Needed, Business Driver, Key Considerations
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

## 7. ADR Relationship Guidelines

**CRITICAL DISTINCTION**: PRDs are created BEFORE ADRs in SDD workflow

❌ **NEVER** reference specific ADR numbers (ADR-012, ADR-033, etc.) in PRD documents

✅ **DO** include "Architecture Decision Requirements" subsection listing topics for architectural decisions

**Workflow Order**:
1. BRD identifies architecture topics requiring decisions
2. PRD inherits and refines architectural topics from BRD
3. ADRs document which option was chosen and WHY
4. This separation maintains clear workflow phases and prevents broken references

---

## 8. SYS-Ready Scoring System ⭐ NEW

### Overview
SYS-ready scoring measures PRD maturity and readiness for progression to System Requirements (SYS) phase in SDD workflow. Minimum score of 90% required to advance to SYS creation.

**Format**: `✅ NN% (Target: ≥90%)`
**Location**: Document Control table (required field)
**Validation**: Enforced before commit via validation checks

### Scoring Criteria

**Product Requirements Completeness (40%)**:
- All 16 sections present and populated: 10%
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

## 9. EARS-Ready Scoring System ⭐ NEW

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
- References to option_strategy/ business logic sections: 5%

### Quality Gate Enforcement
- **Blocking Validation**: Score <90% prevents progression to EARS phase
- **Format Validation**: Must follow exact format with ✅ emoji and percentage
- **Threshold Enforcement**: ≥90% required for EARS-ready status

---

## 10. Traceability Requirements (MANDATORY - Layer 2)

- **Upstream Sources**: Must reference BRD business requirements and strategy documents
- **Downstream Artifacts**: Map to SYS, EARS, BDD, REQ sequences
- **Strategy References**: Include specific sections from `option_strategy/` documents
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

## 10. Business Objectives and Success Criteria

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

## 11. Quality Gates (Pre-Commit Validation)

- **Multiple Validation Checks**: Run `./scripts/validate_prd_template.sh filename.md`
- **Blockers**: Missing sections, invalid formats, incomplete SYS-ready score, broken traceability
- **Warnings**: Incomplete sections, missing references, unverified assumptions
- **SYS-Ready Threshold**: ≥90% required for progression to SYS phase
- **Link Resolution**: All traceability links must resolve to existing files

---

## 12. Additional Requirements

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
