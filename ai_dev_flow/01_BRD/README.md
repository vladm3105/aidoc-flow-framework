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

## Generation Rules

- Index-only: maintain `BRD-00_index.md` as the authoritative plan and registry (mark planned items with Status: Planned).
- Templates: default to the MVP template; use the full (sectioned) template only when it is explicitly requested in project settings or clearly stated in the prompt.
- Inputs used for generation: `BRD-00_index.md` + selected template profile; no skeletons are used.
- Example index: `ai_dev_flow/tmp/SYS-00_index.md`.

Business Requirements Documents (BRDs) serve as the highest-level business requirements that establish the strategic foundation for all downstream development. BRDs capture business objectives, stakeholder needs, and success criteria before any product or technical considerations.

## Purpose

BRDs transform strategic business goals into concrete, actionable requirements that:
- Define business problems and market opportunities
- Establish business objectives with measurable success criteria
- Set organizational scope and stakeholder alignment
- Identify architectural topics requiring decisions
- Provide traceability to downstream product and technical artifacts
- Create the authoritative source for business validation

## Position in Document Workflow

**⚠️ See [../index.md](../index.md#traceability-flow) for the authoritative workflow visualization.**


BRDs are the **first step** in specification-driven development within the complete SDD workflow:

**Authoritative flow**: BRD → PRD → EARS → BDD → ADR → SYS → REQ → CTR → SPEC → TASKS → Code. See [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) for details.

## ADR References in BRD

**⚠️ CRITICAL - Workflow Order**: BRDs are created BEFORE ADRs in the SDD workflow. Therefore:

❌ **Do NOT** reference specific ADR numbers (ADR-NN, etc.) in BRD documents

✅ **DO** include "Architecture Decision Requirements" section describing what decisions are needed

**Correct Workflow Order**: **BRD** → PRD → EARS → BDD → **ADR** → SYS → REQ → CTR → SPEC → TASKS

**Rationale**:
- 01_BRD/PRD identify **WHAT** architectural decisions are needed
- ADRs document **WHICH** option was chosen and **WHY**
- This separation maintains clear workflow phases and prevents broken references

### Architecture Decision Requirements Section (7.2) - MANDATORY

Every BRD **MUST** include **Section 7.2: "Architecture Decision Requirements"** addressing all 7 mandatory ADR topic categories.

#### 7 Mandatory ADR Topic Categories

| # | Category | Element ID | Description | When N/A |
|---|----------|------------|-------------|----------|
| 1 | **Infrastructure** | BRD.NN.32.01 | Compute, deployment, scaling | Pure data/analytics project |
| 2 | **Data Architecture** | BRD.NN.32.02 | Database, storage, caching | No persistent data needed |
| 3 | **Integration** | BRD.NN.32.03 | APIs, messaging, external systems | Standalone system |
| 4 | **Security** | BRD.NN.32.04 | Auth, encryption, access control | Internal tool, no sensitive data |
| 5 | **Observability** | BRD.NN.32.05 | Monitoring, logging, alerting | MVP/prototype only |
| 6 | **AI/ML** | BRD.NN.32.06 | Model serving, training, MLOps | No AI/ML components |
| 7 | **Technology Selection** | BRD.NN.32.07 | Languages, frameworks, platforms | Using existing stack |

#### Required Fields Per Topic

Each ADR topic **MUST** include:

| Field | Description | Required For |
|-------|-------------|--------------|
| **Status** | `Selected`, `Pending`, or `N/A` | All topics |
| **Business Driver** | WHY this decision matters to business | Selected/Pending |
| **Business Constraints** | Non-negotiable business rules | Selected/Pending |
| **Alternatives Overview** | Table with Option, Function, Est. Cost, Rationale | Selected |
| **Cloud Provider Comparison** | GCP vs Azure vs AWS comparison table | Selected |
| **Recommended Selection** | Selected option with brief rationale | Selected |
| **PRD Requirements** | What PRD must elaborate for this topic | All topics |

#### Alternatives Overview Table (MANDATORY)

```markdown
| Option | Function | Est. Monthly Cost | Selection Rationale |
|--------|----------|-------------------|---------------------|
| Option A | Brief description | $X-$Y | Selected - reason |
| Option B | Brief description | $X-$Y | Rejected - reason |
| Option C | Brief description | $X-$Y | Rejected - reason |
```

#### Cloud Provider Comparison Table (MANDATORY)

```markdown
| Criterion | GCP | Azure | AWS |
|-----------|-----|-------|-----|
| **Service Name** | Cloud Run | Container Apps | Fargate |
| **Est. Monthly Cost** | $300 | $350 | $400 |
| **Key Strength** | Auto-scaling | AD integration | Ecosystem |
| **Key Limitation** | Fewer features | Higher cost | Complex pricing |
| **Fit for This Project** | High | Medium | Medium |
```

#### Status Indicators

- **Selected**: Decision made, includes full Alternatives Overview and Cloud Provider Comparison
- **Pending**: Awaiting information/decision, includes reason and expected timeline
- **N/A**: Not applicable, includes explicit reason why category doesn't apply

#### Layer Separation Principle

```
BRD Section 7.2          →    PRD Section 18         →    ADR
(WHAT & WHY & HOW MUCH)       (HOW to evaluate)          (Final decision)
─────────────────────────────────────────────────────────────────────────
Business drivers              Technical details          Implementation decision
Business constraints          Deep-dive analysis         Trade-off analysis
Cost estimates                Evaluation criteria        Selected approach
```

**Reference**: See `BRD_MVP_CREATION_RULES.md` Section 9 for detailed guidelines and `examples/BRD-06.0_example_feature.md` for complete demonstration

## BRD Categories: Platform vs Feature

### Platform BRDs

**Purpose**: Define infrastructure, architecture, and technology stack requirements

**Characteristics**:
- Focus on business drivers for technology decisions
- Populate "Technology Stack Prerequisites" section (section 3.6)
- List required ADRs in "Mandatory Technology Conditions" (section 3.7)
  
Note: ADRs are authored after BDD in the SDD workflow; do not create ADRs before PRD.

**Workflow**: Platform BRD → PRD → EARS → BDD → ADR → SPEC

**Examples**:
- BRD-NN: Platform Architecture & Technology Stack
- BRD-NN: ML Infrastructure Technology Decisions
- BRD-NN: Mobile Platform Architecture

**Key Template sections**:
- section 3.6: Technology Stack Prerequisites (REQUIRED)
- section 3.7: Mandatory Technology Conditions (REQUIRED)

### Feature BRDs

**Purpose**: Define business features, user workflows, functional requirements

**Characteristics**:
- Focus on business objectives and user needs
- May reference Platform BRD technology prerequisites
- Technology decisions deferred to 02_PRD/ADR phase
- Standard workflow

**Workflow**: Feature BRD → PRD → EARS → BDD → ADR (if needed) → SPEC

**Examples**:
- BRD-NN: Progressive User Onboarding
- BRD-NN: Multi-Step Request Workflow
- BRD-NN: Anomaly Detection Agent

**Key Template sections**:
- section 3.6: Technology Stack Prerequisites (REQUIRED - may reference Platform BRD)
- section 3.7: Mandatory Technology Conditions (REQUIRED - include platform-inherited and any feature-specific constraints)

### Naming Conventions

**Platform BRDs**:
- Pattern: `BRD-NN_platform_*` or `BRD-NN_infrastructure_*`
- Examples: `BRD-NN_platform_architecture_technology_stack.md`

**Feature BRDs**:
- Pattern: `BRD-NN_{feature_name}`
- Examples: `BRD-06_progressive_user_onboarding.md`

### Decision Guide

**Use Platform BRD when**:
- Building platform/infrastructure
- Defining technology stack
- Technology decisions constrain product features
- Architecture decision topics must be identified early (ADRs will be authored after BDD)

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
- **Detailed Requirements**: Use internal heading IDs `BRD.NN.01.SS` with MoSCoW priority, risk level, acceptance criteria
- **Business Rules**: Operational rules and constraints
- **User Roles and Permissions**: Stakeholder roles and access levels

### Quality Attributes
- **Overview**: Quality attributes (performance, security, availability)
- **Detailed Requirements**: QA-XXX IDs with metrics, targets, priorities
- **Architecture Decision Requirements**: Architectural topics needing decisions (section 7.2)

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

### Business Risk Management
- **Identified Risks**: Risk ID, description, probability, impact, mitigation
- **Risk Register**: Comprehensive risk tracking

### Implementation Approach
- **Implementation Phases**: Phased delivery plan with milestones
- **Rollout Plan**: Deployment strategy and user adoption plan

### Quality Assurance
- **Quality Standards**: Target metrics and measurement methods
- **Testing Strategy**: Test types, scope, automation level
- **Quality Gates**: Criteria and ownership for release gates

> **Note**: Section 15 (Quality Assurance) is mandatory for all BRDs. It defines quality standards, testing strategy, and quality gates to ensure consistent delivery quality.

### Traceability, Glossary and Appendices
- **Traceability**: Requirements traceability matrix and cross-BRD dependencies
- **Glossary**: Business term definitions (6 subsections)
- **Appendices**: Detailed supporting information

> **Note**: Technical QA standards, testing strategy, and defect management are documented in PRD-MVP-TEMPLATE.md (full template archived).

## Available Templates

This directory provides the MVP template for business requirements (full template archived):

> **Schema Policy: Optional BRD_SCHEMA.yaml**
>
> BRD validation is human-centric. An optional schema file (`BRD_SCHEMA.yaml`) exists for non-blocking, machine-readable consistency checks. Primary validation remains script-based and human review.
>
> **Rationale**:
> - Business flexibility and domain variability require flexibility over rigidity
> - Human-centric validation is preferred at Layer 1
> - Sufficient guidance via `BRD_MVP_CREATION_RULES.md` and `BRD_MVP_VALIDATION_RULES.md`
>
> **Validation Approach**: Use `scripts/validate_brd_template.sh` for structural validation; use the optional schema for advisory checks only.

**BRD-MVP-TEMPLATE.md** (default) - Streamlined MVP version in a single file without sectioning
- Focused on core MVP features and rapid development
- Maintains framework compliance while reducing documentation overhead
- Ideal for quick MVP launches and hypothesis validation

Full template is archived; stay on MVP unless an enterprise/full template is explicitly required.

## File Naming Convention

```
BRD-NN_descriptive_title.md        # Atomic document
BRD-NN.S_section_title.md          # Section file (for large documents)
```

Where:
- `BRD` is the constant prefix
- `NNN` is the 2+ digit sequence number (01, 02, 003, etc.)
- `S` is the section number for split documents (0=index, 1, 2, 3, etc.)
- `descriptive_title` uses snake_case for clarity

**Examples:**
- `BRD-01_foundation_overview.md` (atomic document)
- `BRD-09.1_provider_integration_prerequisites.md` (section file)
- `BRD-09.2_provider_integration_pilot.md` (section file)

**Important**: Each NN number must be unique. Section files use `.S` suffix (e.g., `BRD-09.0` for index, `BRD-09.1` for first section). See `ID_NAMING_STANDARDS.md` for metadata tags.

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

**BRD Traceability Rules**:
- **Upstream Traceability**: OPTIONAL - BRDs are top-level business documents; they may reference other BRDs or external business strategy documents, but this is not required
- **Downstream Traceability**: OPTIONAL - Only add links to downstream documents (PRD, ADR, etc.) that already exist. Do NOT use placeholder IDs (TBD, XXX, NNN)

### 6. Enable Stakeholder Validation
- Write acceptance criteria verifiable by business stakeholders
- Avoid vague terms like "user-friendly" or "efficient"
- Define clear success conditions for each objective

## PRD-Ready Scoring System

BRDs now include PRD-ready scoring (mirroring REQ SPEC-ready scoring) to ensure business requirements are mature enough to proceed to PRD creation.

### Purpose and Usage

**PRD-Ready Score** evaluates if a BRD is complete enough to proceed to Product Requirements Document (PRD) creation in the SDD workflow:

```markdown
| **PRD-Ready Score** | 95/100 (Target: ≥90/100) |
```

- **Format**: `[Score]/100 (Target: ≥90/100)` (optional ✅ emoji allowed)
- **Validation**: Required in Document Control table (blocking validation)
- **Warnings**: Scores below 90/100 trigger validation warnings

### Scoring Criteria

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

### How to Calculate Score

1. **Self-Assessment**: Manually calculate based on completeness criteria
2. **Validation Check**: Run `./scripts/validate_brd_template.sh` - includes format validation
3. **Required ≥90%**: Scores below 90% block progression to PRD creation
4. **Continuous Improvement**: Update score as BRD matures during development

### Integration with Validation

**New Validation Check**: `CHECK 13: PRD-Ready Score Validation`
- Verifies format: `[Score]/100 (Target: ≥90/100)`
- Enforces ≥90/100 threshold for progression
- Blocking validation - must pass before PRD creation

### Workflow Integration

```
BRD (with PRD-Ready Score ≥90/100) → PRD → EARS → BDD → ADR → SYS → REQ → CTR → SPEC → TASKS → Code
```

**Quality Gate**: BRD documents must achieve ≥90% PRD-ready score before proceeding to PRD phase, ensuring business requirements are sufficiently mature for product implementation planning.

## BRD Quality Gates

**Every BRD must include:**
- Clear business problem statement with strategic context
- Specific, achievable business objectives
- Explicit out-of-scope items defining boundaries
- Measurable success criteria and KPIs
- **PRD-Ready Score ≥90/100** in Document Control
- Architecture Decision Requirements section (section 7.2)
- Business-focused acceptance criteria
- Comprehensive risk assessment

**BRD content standards:**
- Business language over technical jargon
- Links resolve to existing documents or include placeholders
- Assumptions and constraints explicitly documented
- Stakeholder roles and responsibilities defined
- All requirements have unique IDs using unified format (e.g., `BRD.NN.23.SS` for objectives, `BRD.NN.01.SS` for functional requirements, `BRD.NN.02.SS` for quality)

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

See `01_BRD/examples/` for minimal, validator-compliant examples:
- `BRD-06.0_example_feature.md` (Feature BRD)

Also consult:
- `BRD-MVP-TEMPLATE.md` (primary standard)
- `FR_EXAMPLES_GUIDE.md` (functional requirements patterns)

Note: `BRD-MVP-TEMPLATE.md` is the reference template. For sectioned docs, use `BRD-SECTION-0-TEMPLATE.md` and `BRD-SECTION-TEMPLATE.md` per `../DOCUMENT_SPLITTING_RULES.md`.

These demonstrate well-structured BRDs following these conventions with proper Architecture Decision Requirements sections.
## File Size Limits

- **Target**: 800 lines per file
- **Maximum**: 1200 lines per file (absolute)
- If a file approaches/exceeds limits, split into section files using `BRD-SECTION-TEMPLATE.md` and update the suite index. See `../DOCUMENT_SPLITTING_RULES.md` for core splitting standards.

## Document Splitting Standard

When BRD content grows beyond the target range or becomes hard to navigate:
- Create or update the suite index: `BRD-{NN}.0_index.md`
- Split content into section files using `BRD-SECTION-TEMPLATE.md` (see `../DOCUMENT_SPLITTING_RULES.md` for numbering and required front‑matter):
  - Filenames: `BRD-{NN}.{S}_{section_slug}.md` (S = 1, 2, 3, ...)
  - Maintain Prev/Next navigation and update the index table (section map)
- Update cross-references and any traceability matrices to point to the new section files
- Validate links and run `./scripts/lint_file_sizes.sh`
