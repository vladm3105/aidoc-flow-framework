# BRD Creation Rules

**Version**: 1.1
**Date**: 2025-11-19
**Last Updated**: 2025-11-19
**Source**: Extracted from BRD-TEMPLATE.md, BRD-VALIDATION_RULES.md, README.md, and BRD-000_index.md
**Purpose**: Complete reference for creating BRD files according to doc-flow SDD framework
**Changes**: Clarified Platform vs Feature BRD section requirements, standardized Document Control positioning

---

## Table of Contents

1. [File Organization and Directory Structure](#1-file-organization-and-directory-structure)
2. [Document Structure (17 Required Sections)](#2-document-structure-17-required-sections)
3. [Document Control Requirements](#3-document-control-requirements)
4. [ID and Naming Standards](#4-id-and-naming-standards)
5. [Business Requirements Principles](#5-business-requirements-principles)
6. [Platform vs Feature BRD Distinctions](#6-platform-vs-feature-brd-distinctions)
7. [ADR Relationship Guidelines](#7-adr-relationship-guidelines)
8. [Traceability Requirements](#8-traceability-requirements)
9. [Architecture Decision Requirements](#9-architecture-decision-requirements)
10. [Business Objectives and Success Criteria](#10-business-objectives-and-success-criteria)
11. [Quality Gates](#11-quality-gates)
12. [Additional Requirements](#12-additional-requirements)

---

## 1. File Organization and Directory Structure

- **Location**: `docs/BRD/` within project docs directory
- **Platform BRDs**: `BRD-NNN_platform_*` or `BRD-NNN_infrastructure_*` (e.g., `BRD-001_platform_architecture_technology_stack.md`)
- **Feature BRDs**: `BRD-NNN_{feature_name}` (e.g., `BRD-006_b2c_progressive_kyc_onboarding.md`)
- **Naming**: `BRD-NNN_descriptive_title.md` (NNN = 3-digit sequential number, snake_case slug)
- **Subdocuments**: For complex business requirements: `BRD-NNN-YY_additional_detail.md` (YY = 2-digit sub-number)

---

## 2. Document Structure (17 Required Numbered Sections)

**Document Control Section**: Located at the very beginning (before all numbered sections)

Every BRD must contain these exact numbered sections in order:

1. **Introduction** - Purpose, scope, audience, conventions, references
2. **Business Objectives** - Background/context, business problem, goals, objectives, strategic alignment, expected benefits
3. **Project Scope** - Scope statement, in-scope/out-of-scope items, future considerations, business process scope
4. **Functional Requirements** - Overview, requirements by category, business rules, user roles/permissions
5. **Non-Functional Requirements** - Overview, performance, security, availability, scalability, usability, compatibility, compliance
6. **Assumptions and Constraints** - Assumptions with validation methods, budget/schedule/resource/technical constraints, dependencies
7. **Acceptance Criteria** - Business acceptance, functional acceptance, success metrics/KPIs, UAT criteria, go-live readiness
8. **Risk Management** - Risk register with assessment, risk categories, monitoring/review
9. **Implementation Approach** - Strategy, phases, rollout plan, data migration plan, integration plan
10. **Training and Change Management** - Training strategy/plan/materials, change management strategy/communication/impact assessment
11. **Support and Maintenance** - Support model/services/SLAs, maintenance plan
12. **Cost-Benefit Analysis** - One-time/recurring costs, quantifiable/qualitative benefits, ROI, payback NPV
13. **Project Governance** - Governance structure, decision-making authority, status reporting, change control
14. **Quality Assurance** - Quality standards, testing strategy, defect management
15. **Glossary** - Business and domain-specific terms
16. **Appendices** - References, supporting documentation, process flow diagrams, data requirements, UI mockups, integration specifications, stakeholder interview notes


## 3. Document Control Requirements

**Position**: Must be the first section at the very top of the BRD (before all numbered sections)

**Required Fields** (6 mandatory):
- Project Name: [Enter project name]
- Document Version: [e.g., 1.0] (semantic versioning X.Y)
- Date: [Current date in YYYY-MM-DD format]
- Document Owner: [Name and title of responsible business executive]
- Prepared By: [Business Analyst name who authored document]
- Status: [Draft / In Review / Approved]

**Also Required**: Document Revision History table with at least one initial entry

**Template**:
```markdown
| Item | Details |
|------|---------|
| **Project Name** | [Enter project name] |
| **Document Version** | [e.g., 1.0] |
| **Date** | [Current date] |
| **Document Owner** | [Name and title] |
| **Prepared By** | [Business Analyst name] |
| **Status** | [Draft / In Review / Approved] |

### Document Revision History

| Version | Date | Author | Changes Made | Approver |
|---------|------|--------|--------------|----------|
| 1.0 | [Date] | [Name] | Initial draft | |
| | | | | |
```

---

## 4. ID and Naming Standards

- **Filename**: `BRD-NNN_descriptive_title.md` (e.g., `BRD-001_platform_architecture_technology_stack.md`)
- **H1 Header**: `# Business Requirements Document (BRD)` (static for all BRDs)
- **Document Title**: Include in H1 as subtitle (e.g., "Business Requirements Document (BRD)" with project name in Introduction)
- **ID Format**: BRD-NNN (3-digit sequential), BRD-NNN-YY for multi-part documents
- **Uniqueness Rule**: Each NNN number unique across Platform and Feature BRDs

---

## 5. Business Requirements Principles

- **Business-First Focus**: Business needs drive requirements, not technical solutions
- **Measurable Objectives**: All business objectives follow SMART criteria (Specific, Measurable, Achievable, Relevant, Time-bound)
- **Strategic Alignment**: Requirements trace back to organizational strategy documents
- **Stakeholder Validation**: Acceptance criteria verifiable by business stakeholders without technical knowledge
- **BDD-Ready**: Business requirements formulated for executable behavior-driven development

---

## 6. Platform vs Feature BRD Distinctions

### Platform BRDs (e.g., BRD-001, BRD-034)
- **Purpose**: Define foundational capabilities, technology stacks, prerequisites
- **Sections 3.6 & 3.7**: ALWAYS PRESENT - Define foundational technology stacks and mandatory constraints
- **ADR Timing**: ADRs created BEFORE PRD to validate architectural decisions
- **Technology Focus**: Infrastructure, security, compliance foundations
- **Interdependencies**: Establish foundation for Feature BRDs

### Feature BRDs (e.g., BRD-006, BRD-009)
- **Purpose**: Define business features and user workflows
- **Sections 3.6 & 3.7**: ALWAYS PRESENT - Reference Platform BRD dependencies and feature-specific conditions
- **ADR Timing**: Standard workflow (BRD → PRD → SYS → EARS → REQ → ADR)
- **Business Focus**: User problems, business processes, acceptance criteria
- **Dependencies**: Reference Platform BRDs for technology foundations

---

## 7. ADR Relationship Guidelines

**CRITICAL DISTINCTION**: BRDs are created BEFORE ADRs in SDD workflow

❌ **NEVER** reference specific ADR numbers (ADR-012, ADR-033) in BRD documents

✅ **DO** include "Architecture Decision Requirements" section identifying topics for architectural decisions

**Workflow Order**:
1. BRD identifies architecture topics needing decisions
2. ADRs document which option was chosen and WHY
3. This separation maintains workflow integrity and prevents forward references

**Section 6.1: Architecture Decision Requirements**
```markdown
| Topic Area | Decision Needed | Business Driver | Key Considerations |
|------------|-----------------|---------------|-------------------|
| Database Selection | Choose data storage technology | NFR: Data persistence requirements | SAS 70 Type II compliance, horizontal scaling |
```

---

## 8. Traceability Requirements (MANDATORY - Layer 1)

- **Upstream Sources**: Link to business strategy documents (`option_strategy/` sections)
- **Downstream Artifacts**: Map to PRD, SYS, EARS, BDD, REQ sequences
- **Strategy References**: Include specific sections from integrated_strategy_algo_v5.md, etc.
- **Business Rationale**: Each requirement includes business justification
- **Acceptance Criteria**: Verifiable by business stakeholders

**Required Traceability Fields**:
- **Upstream Sources**: Business strategy documents
- **Downstream Artifacts**: PRD, EARS, BDD, REQ
- **Anchors/IDs**: `BO-XXX`, `FR-XXX`, `NFR-XXX` for each requirement
- **Code Path(s)**: Strategic impact area

---

## 9. Architecture Decision Requirements

Every BRD must include Section 6.1: "Architecture Decision Requirements"

| Field | Description | Example |
|-------|-------------|---------|
| **Topic Area** | Technology or architecture domain | "Multi-Agent Framework", "Data Storage", "Authentication Protocol" |
| **Decision Needed** | What architectural choice is required | "Select orchestration mechanism for agent coordination" |
| **Business Driver** | Which BRD requirement necessitates this | "BO-003: Autonomous trading execution" |
| **Key Considerations** | Technologies/patterns to evaluate | "Google ADK, n8n workflow engine, custom orchestration" |

**Purpose**: Identifies architectural topics requiring formal evaluation BEFORE PRD creation (for critical decisions) or standard workflow timing (for feature decisions)

---

## 10. Business Objectives and Success Criteria

### SMART Objectives Format
All business objectives in Section 2.4 must follow SMART criteria:

| Component | Description | Example |
|-----------|-------------|---------|
| **Specific** | Clear, explicit goal | "Reduce transaction processing time by 50%" |
| **Measurable** | Quantifiable metrics | "from 10 seconds to 5 seconds" |
| **Achievable** | Realistic within constraints | "based on current 95th percentile performance" |
| **Relevant** | Aligns with business strategy | "matches performance targets in integrated_strategy_algo_v5.md" |
| **Time-bound** | Specific deadline | "within 6 months of implementation" |

### Success Criteria Requirements
- **Quantifiable**: Include specific targets and metrics
- **Business-Focused**: Verifiable without technical expertise
- **Multi-Level**: Organization, department, individual stakeholder metrics
- **Baseline Included**: Current state measurement for comparison

---

## 11. Quality Gates (Pre-Commit Validation)

- **12 Validation Checks**: Run `./scripts/validate_brd_template.sh filename.md`
- **Blockers**: Missing sections, invalid formats, broken traceability
- **Warnings**: Missing references, incomplete criteria, unverified assumptions
- **Platform Feature Validation**: Different requirements for Platform vs Feature BRDs
- **Link Resolution**: All traceability links must resolve to existing files

---

## 12. Additional Requirements

- **Business Language**: Use business terminology over technical jargon
- **Financial Quantification**: Include ROI calculations, cost-benefit analysis
- **Stakeholder Engagement**: Define roles, responsibilities, communication plans
- **Risk Management**: Comprehensive risk register with mitigation strategies
- **Compliance Validation**: Include regulatory requirements and audit considerations

---

## Quick Reference

**Pre-Commit Validation**:
```bash
# Validate single file
./scripts/validate_brd_template.sh docs/BRD/BRD-001_platform_architecture.md

# Validate all BRD files
find docs/BRD -name "BRD-*.md" -exec ./scripts/validate_brd_template.sh {} \;
```

**Template Location**: [BRD-TEMPLATE.md](BRD-TEMPLATE.md)
**Validation Rules**: [BRD-VALIDATION-RULES.md](BRD-VALIDATION-RULES.md)
**Index**: [BRD-000_index.md](BRD-000_index.md)

---

**Framework Compliance**: 100% doc_flow SDD framework aligned (Layer 1 - Business Requirements)
**Maintained By**: Business Analyst Team, SDD Framework Team
**Review Frequency**: Updated with template and validation rule enhancements

---

# task_progress List (Optional - Plan Mode)

While in PLAN MODE, if you've outlined concrete steps or requirements for the user, you may include a preliminary todo list using the task_progress parameter.

Reminder on how to use the task_progress parameter:


1. To create or update a todo list, include the task_progress parameter in the next tool call
2. Review each item and update its status:
   - Mark completed items with: - [x]
   - Keep incomplete items as: - [ ]
   - Add new items if you discover additional steps
3. Modify the list as needed:
		- Add any new steps you've discovered
		 - Reorder if the sequence has changed
4. Ensure the list accurately reflects the current state

**Remember:** Keeping the task_progress list updated helps track progress and ensures nothing is missed.
