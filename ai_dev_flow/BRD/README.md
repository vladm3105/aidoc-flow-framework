---
title: "Business Requirements Documents (BRD)"
tags:
  - index-document
  - layer-1-artifact
  - shared-architecture
custom_fields:
  document_type: readme
  artifact_type: BRD
  layer: 1
  priority: shared
---

# Business Requirements Documents (BRD)

Business Requirements Documents (BRDs) serve as the highest-level business requirements that establish the strategic foundation for all downstream development. BRDs capture business objectives, stakeholder needs, and success criteria before any product or technical considerations.

## Purpose

BRDs transform strategic business goals into concrete, actionable requirements that:
- Define business problems and market opportunities
- Establish business objectives with measurable success criteria
- Set organizational scope and stakeholder alignment
- Identify architectural topics requiring decisions
- Provide traceability to downstream product and technical artifacts
- Create the authoritative source for business validation

## [RESOURCE_INSTANCE - e.g., database connection, workflow instance] in Development Workflow

**⚠️ See [../index.md](../index.md#traceability-flow) for the authoritative workflow visualization.**


BRDs are the **first step** in specification-driven development within the complete SDD workflow:

**⚠️ See for the full document flow: /opt/data/docs_flow_framework/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md**

## ADR References in BRD

**⚠️ CRITICAL - Workflow Order**: BRDs are created BEFORE ADRs in the SDD workflow. Therefore:

❌ **Do NOT** reference specific ADR numbers (ADR-001, ADR-011, etc.) in BRD documents

✅ **DO** include "Architecture Decision Requirements" section describing what decisions are needed

**Correct Workflow Order**: **BRD** → PRD → SYS → EARS → REQ → **ADR** → BDD → IMPL → CTR → SPEC → TASKS

**Rationale**:
- BRD/PRD identify **WHAT** architectural decisions are needed
- ADRs document **WHICH** option was chosen and **WHY**
- This separation maintains clear workflow phases and prevents broken references

**Architecture Decision Requirements section**:
Every BRD should include a section (typically section 5.2) that lists architectural topics requiring decisions:

```markdown
## 5.2 Architecture Decision Requirements

| Topic Area | Decision Needed | Business Driver (BRD Reference) | Key Considerations |
|------------|-----------------|--------------------------------|-------------------|
| Multi-Agent Framework | Select orchestration framework | BO-XXX (automated operations) | Google ADK, LangGraph, custom |
| State Management | Define persistence strategy | NFR-XXX (99.99% reliability) | Cloud SQL, Firestore, Redis |
| Communication Protocol | Choose messaging pattern | NFR-XXX (<50ms latency) | Pub/Sub, gRPC, REST |

**Example Topics**:
- Multi-Agent Framework, State Management, Communication Protocol
- Data Storage, [EXTERNAL_INTEGRATION - e.g., third-party API, service provider] Integration, Risk Calculation Engine

**Purpose**: Identify architectural topics requiring decisions. Specific ADRs created AFTER this BRD.
**Timing**: ADRs created after BRD → PRD → SYS → EARS → REQ in SDD workflow.
```

## BRD Categories: Platform vs Feature

### Platform BRDs

**Purpose**: Define infrastructure, architecture, and technology stack requirements

**Characteristics**:
- Focus on business drivers for technology decisions
- Populate "Technology Stack Prerequisites" section (section 3.6)
- List required ADRs in "Mandatory Technology Conditions" (section 3.7)
- ADRs created BEFORE PRD

**Workflow**: Platform BRD → **ADRs (critical)** → PRD → ADRs (remaining) → SPEC

**Examples**:
- BRD-001: Platform Architecture & Technology Stack
- BRD-034: ML Infrastructure Technology Decisions
- BRD-050: Mobile Platform Architecture

**Key Template sections**:
- section 3.6: Technology Stack Prerequisites (REQUIRED)
- section 3.7: Mandatory Technology Conditions (REQUIRED)

### Feature BRDs

**Purpose**: Define business features, user workflows, functional requirements

**Characteristics**:
- Focus on business objectives and user needs
- May reference Platform BRD technology prerequisites
- Technology decisions deferred to PRD/ADR phase
- Standard workflow

**Workflow**: Feature BRD → PRD → ADRs (if needed) → SPEC

**Examples**:
- BRD-006: B2C Progressive KYC Onboarding
- BRD-009: Remittance Transaction Workflow
- BRD-022: Fraud Detection Agent

**Key Template sections**:
- section 3.6: Technology Stack Prerequisites (OPTIONAL - may reference Platform BRD)
- section 3.7: Mandatory Technology Conditions (Usually empty)

### Naming Conventions

**Platform BRDs**:
- Pattern: `BRD-NNN_platform_*` or `BRD-NNN_infrastructure_*`
- Examples: `BRD-001_platform_architecture_technology_stack.md`

**Feature BRDs**:
- Pattern: `BRD-NNN_{feature_name}`
- Examples: `BRD-006_b2c_progressive_kyc_onboarding.md`

### Decision Guide

**Use Platform BRD when**:
- Building platform/infrastructure
- Defining technology stack
- Technology decisions constrain product features
- ADRs needed before PRD creation

**Use Feature BRD when**:
- Building user features
- Defining business workflows
- Technology is already decided (reference Platform BRD)
- Can proceed to PRD immediately

**See**: [PLATFORM_VS_FEATURE_BRD.md](../PLATFORM_VS_FEATURE_BRD.md) for complete guide

## BRD Structure

### Document Control
Standard metadata including version, date, owner, status, revision history

### Introduction
- **Purpose**: Document objectives and intended use
- **Scope**: What this BRD covers (business perspective: objectives, requirements, success criteria, Architecture Decision Requirements)
- **Audience**: Executive sponsors, project managers, technical teams, stakeholders
- **Conventions**: Requirements phrasing (shall), MoSCoW prioritization, ID scheme
- **References**: Supporting business documents (strategy, policies, standards)

### Business Objectives
- **Background and Context**: Business environment, market conditions, organizational drivers
- **Business Problem Statement**: Current state issues, impact, affected stakeholders
- **Business Goals**: Strategic outcomes and objectives
- **Business Objectives**: Measurable objectives with success metrics and target dates
- **Strategic Alignment**: How this aligns with organizational strategy
- **Expected Benefits**: Quantifiable and qualitative benefits

### Project Scope
- **Scope Statement**: High-level deliverables summary
- **In-Scope Items**: Included functionality and capabilities
- **Out-of-Scope Items**: Explicitly excluded items with rationale
- **Future Considerations**: Potential future enhancements
- **Business Process Scope**: Current vs future state processes, impacted areas

### Functional Requirements
- **Overview**: High-level functional capabilities
- **Detailed Requirements**: FR-XXX IDs with MoSCoW priority, risk level, acceptance criteria
- **Business Rules**: Operational rules and constraints
- **User Roles and Permissions**: Stakeholder roles and access levels

### Non-Functional Requirements
- **Overview**: Quality attributes (performance, security, availability)
- **Detailed Requirements**: NFR-XXX IDs with metrics, targets, priorities
- **Architecture Decision Requirements**: Architectural topics needing decisions (section 5.2)

### Assumptions and Constraints
- **Assumptions**: Assumed conditions with validation methods
- **Budget Constraints**: Financial limitations and allocations
- **Schedule Constraints**: Timeline restrictions and milestones
- **Technical Constraints**: Technology limitations and dependencies
- **Resource Constraints**: People, tools, infrastructure availability
- **Regulatory Constraints**: Compliance and legal requirements

### Acceptance Criteria
- **Business Acceptance**: High-level business validation criteria
- **Functional Acceptance**: Functional requirement validation
- **Success Metrics and KPIs**: Measurable performance indicators

### [RESOURCE_MANAGEMENT - e.g., capacity planning, quota management]
- **Identified Risks**: Risk ID, description, probability, impact, mitigation
- **Risk Register**: Comprehensive risk tracking

### Implementation Approach
- **Implementation Phases**: Phased delivery plan with milestones
- **Rollout Plan**: Deployment strategy and user adoption plan

### Glossary and Appendices
- **Glossary**: Business term definitions
- **Appendices**: Detailed supporting information

## Available Templates

This directory provides the **BRD-TEMPLATE.md** for business requirements documentation:

> **Note**: BRD does not have a schema file (`BRD_SCHEMA.yaml`) by design. Business requirements
> are inherently flexible and domain-specific; rigid schema validation would be counterproductive
> for capturing diverse business needs across different project types.

**BRD-TEMPLATE.md** - Comprehensive business requirements template
- Full-featured template with all sections
- Suitable for all project types
- Includes business objectives, functional/non-functional requirements, architecture decision requirements, and acceptance criteria

**Usage**: Use BRD-TEMPLATE.md as the foundation for all Business Requirements Documents.

## File Naming Convention

```
BRD-NNN_descriptive_title.md        # Atomic document
BRD-NNN-YY_descriptive_title.md     # Multi-part document group
```

Where:
- `BRD` is the constant prefix
- `NNN` is the three-digit sequence number (001, 002, 003, etc.)
- `YY` is the optional two-digit sub-document number (01, 02, 03, etc.)
- `descriptive_title` uses snake_case for clarity

**Examples:**
- `BRD-001_foundation_overview.md` (atomic document)
- `BRD-009-01_provider_integration_prerequisites.md` (multi-part document)
- `BRD-009-02_provider_integration_pilot.md` (multi-part document)

**Important**: Each XXX number must be unique. Cannot have both `BRD-009.md` AND `BRD-009-01.md` (collision).

## Writing Guidelines

### 1. Focus on Business Value
- Start with business problems and market opportunities
- Emphasize strategic benefits and organizational impact
- Avoid premature technical implementation details
- Reference business strategy materials from domain-specific business logic documents where applicable

### 2. Define Scope Clearly
- Use Out-of-Scope to explicitly exclude tempting features
- Document assumptions and dependencies
- Clarify stakeholder responsibilities and ownership

### 3. Make Requirements Measurable
- Include specific business objectives with quantified targets
- Define acceptance criteria in business terms
- Provide success metrics and KPIs with thresholds

### 4. Identify Architectural Topics Early
- Use "Architecture Decision Requirements" section to identify topics
- Do NOT reference specific ADR numbers (they don't exist yet)
- Describe WHAT decisions are needed and WHY they're important
- List technologies/approaches to be evaluated in ADRs

### 5. Maintain Traceability
- Link to business strategy documents (domain-specific business logic)
- Reference existing systems, policies, and standards
- Update traceability sections when downstream artifacts are created
- Note: ADR links added AFTER ADRs are created

### 6. Enable Stakeholder Validation
- Write acceptance criteria verifiable by business stakeholders
- Avoid vague terms like "user-friendly" or "efficient"
- Define clear success conditions for each objective

## PRD-Ready Scoring System

BRDs now include PRD-ready scoring (mirroring REQ SPEC-ready scoring) to ensure business requirements are mature enough to proceed to PRD creation.

### Purpose and Usage

**PRD-Ready Score** evaluates if a BRD is complete enough to proceed to Product Requirements Document (PRD) creation in the SDD workflow:

```markdown
| **PRD-Ready Score** | ✅ 95% (Target: ≥90%) |
```

- **Format**: `✅ emoji + percentage (Target: ≥90%)`
- **Validation**: Required in Document Control table (blocking validation)
- **Warnings**: Scores below 90% trigger validation warnings

### Scoring Criteria

**Business Requirements Completeness (40%)**:
- All 17 sections present and populated: 10%
- Business objectives follow SMART criteria: 10%
- Acceptance criteria quantifiable and verifiable: 10%
- Stakeholder analysis complete: 10%

**Technical Readiness (30%)**:
- section 3.6 & 3.7 properly populated by BRD type: 10%
- section 5.2 Architecture Decision Requirements table: 10%
- No forward ADR references: 10%

**Quality Standards (20%)**:
- Document control complete: 5%
- Strategic alignment with domain-specific business logic documents: 5%
- Cross-references resolve correctly: 5%
- Out-of-scope clearly defined: 5%

**Traceability (10%)**:
- Proper ID formats and links: 5%
- Business rationale provided: 5%

### How to Calculate Score

1. **Self-Assessment**: Manually calculate based on completeness criteria
2. **Validation Check**: Run `./scripts/validate_brd_template.sh` - includes format validation
3. **Required ≥90%**: Scores below 90% block progression to PRD creation
4. **Continuous Improvement**: Update score as BRD matures during development

### Integration with Validation

**New Validation Check**: `CHECK 13: PRD-Ready Score Validation`
- Verifies format: `✅ NN% (Target: ≥90%)`
- Enforces ≥90% threshold for progression
- Blocking validation - must pass before PRD creation

### Workflow Integration

```
BRD (with PRD-Ready Score ≥90%) → PRD Creation → SYS → EARS → REQ → ADR → BDD → IMPL → CTR → SPEC → TASKS → Code
```

**Quality Gate**: BRD documents must achieve ≥90% PRD-ready score before proceeding to PRD phase, ensuring business requirements are sufficiently mature for product implementation planning.

## BRD Quality Gates

**Every BRD must include:**
- Clear business problem statement with strategic context
- Specific, achievable business objectives
- Explicit out-of-scope items defining boundaries
- Measurable success criteria and KPIs
- **PRD-Ready Score ≥90%** in Document Control
- Architecture Decision Requirements section (section 5.2)
- Business-focused acceptance criteria
- Comprehensive risk assessment

**BRD content standards:**
- Business language over technical jargon
- Links resolve to existing documents or include placeholders
- Assumptions and constraints explicitly documented
- Stakeholder roles and responsibilities defined
- All requirements have unique IDs (BO-XXX, FR-XXX, NFR-XXX)

## Common Patterns

### Strategic Initiative BRDs
```markdown
## Business Problem Statement
Market opportunity [description] creates competitive pressure to [outcome].

## Business Objectives
Capture [market share] by enabling [capability] within [timeframe].
Achieve [revenue target] through [strategic approach].
```

### System Integration BRDs
```markdown
## Business Problem Statement
Manual [process] across [systems] creates operational inefficiency costing [amount].

## Business Objectives
Automate [process] to reduce [cost] by [percentage].
Enable [business capability] with [quality metric].
```

### Operational Improvement BRDs
```markdown
## Business Problem Statement
Current [constraint] prevents [business growth] above [current limit].

## Business Objectives
Extend capacity to support [target scale] with [reliability standard].
Reduce [operational cost] by [percentage] through automation.
```

## Benefits of Strong BRDs

1. **Strategic Alignment**: Ensures all downstream work supports business objectives
2. **Stakeholder Clarity**: Single source of truth for business requirements
3. **Scope Control**: Clear boundaries prevent feature creep
4. **Investment Justification**: Business case for resource allocation
5. **Success Validation**: Measurable criteria for project completion
6. **Architectural Planning**: Early identification of technical decision points

## Avoiding Common Pitfalls

1. **Technical Overload**: Don't include implementation details in BRDs
2. **Vague Objectives**: Always quantify success metrics
3. **Missing Non-Goals**: Use Out-of-Scope liberally
4. **Forward References**: Don't reference ADRs that don't exist yet
5. **Orphaned Requirements**: Maintain traceability as development progresses
6. **Unclear Stakeholders**: Define roles, responsibilities, ownership

## Integration with Project Management

BRDs serve as:
- **Project Charter**: Foundation for project approval and funding
- **Stakeholder Agreement**: Signed-off requirements for project initiation
- **Success Baseline**: Acceptance criteria for project closure
- **Change Control**: Baseline for scope changes and change requests

## Version Control and Collaboration

- BRD commits should include issue/PR references
- Major changes require stakeholder re-approval
- Include BRD references in downstream artifact reviews
- Archive superseded BRDs while maintaining links to replacements

## Example BRDs

See existing BRD documents in `docs/BRD/` for complete examples:
- `BRD-001-01_foundation_overview.md` - Multi-agent system strategic overview
- `BRD-009-02_provider_integration_pilot.md` - [EXTERNAL_SERVICE_GATEWAY] integration pilot

These demonstrate well-structured BRDs following these conventions with proper Architecture Decision Requirements sections.
