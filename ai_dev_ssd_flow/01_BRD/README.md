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

## Recent Changes

**2026-03-11**: UCX v1.9.7 - Tier 2 Auto-Fix
- Extended `--fix` for count mismatches: GATE-W003, DIAG-W001
- Prose counts auto-corrected to match actual elements/diagram nodes
- Use `ucx validate brd <path> --fix --report --clean-reports`

**2026-03-11**: UCX v1.9.6 - Structural Auto-Fix
- Added `--fix` flag for deterministic structural fixes
- Added `--report` for auto-report generation after fixing
- Combined workflow: `--fix --report --clean-reports`

**2026-03-05**: BRD Framework Updates
- Updated `validate_brd.py` to check 19 sections (§0-18) - was 16 sections
- Re-enabled pre-commit hooks (were disabled since 2026-02-25)
- Added @depends validation (warning level) for platform BRDs (BRD-02 to BRD-35)
- Fixed template-validator section mismatch (Root Cause #1)

## MVP → PROD → NEW MVP Lifecycle

**Key Principle**: Each BRD represents ONE iteration cycle. When current MVP reaches production and new features are needed, create a **new BRD** for the next cycle.

```
BRD-01 (MVP) → Production v1 → User Feedback → BRD-02 (NEW MVP) → Production v2 → ...
```

| Phase | BRD Role | Duration |
|-------|----------|----------|
| **MVP** | Define 5-15 core features | 1-2 weeks |
| **PROD** | Operate, measure, collect feedback | 30-90 days |
| **NEW MVP** | Create NEW BRD for next features | 1-2 weeks |

**Cross-Cycle Traceability**:
- `@depends: BRD-01` — BRD-02 builds on foundation
- `@extends: BRD-01` — BRD-02 adds features to existing system

## Generation Rules

- Index-only: maintain `BRD-00_index.md` as the authoritative plan and registry (mark planned items with Status: Planned).
- Templates: use `BRD-MVP-TEMPLATE.md` for all BRDs (MVP-first approach).
- Inputs used for generation: `BRD-00_index.md` + selected template profile; no skeletons are used.
- Example index: `ai_dev_ssd_flow/tmp/SYS-00_index.md`.
- New features = New BRD (don't expand existing BRDs indefinitely).

Business Requirements Documents (BRDs) serve as the highest-level business requirements that establish the strategic foundation for all downstream development. BRDs capture business objectives, stakeholder needs, and success criteria before any product or technical considerations.

## Purpose

BRDs transform strategic business goals into concrete, actionable requirements that:
- Define business problems and market opportunities
- Establish business objectives with measurable success criteria
- Set organizational scope and stakeholder alignment
- Identify architectural topics requiring decisions
- Provide traceability to downstream product and technical artifacts
- Create the authoritative source for business validation

## Autopilot Generation

Use `doc-brd-autopilot` for automated BRD generation with validation and review cycles.

### How to Run `doc-brd-audit`

Use one command as the standard BRD quality gate:

```bash
/doc-brd-audit BRD-01
```

**Fresh Audit Policy**: Audits ALWAYS run from scratch. Do not reference previous results or skip validation steps.

The unified audit runs all validation scripts, computes PRD-ready score, and writes a report (`BRD-NN.A_audit_report_vNNN.md`) for `doc-brd-fixer`.

**2-Skill Model**:
| Skill | Purpose |
|-------|---------|
| `doc-brd-audit` | All validation + scoring (runs FROM SCRATCH) |
| `doc-brd-fixer` | Apply fixes from audit report |

**Deprecated**: `doc-brd-validator` and `doc-brd-reviewer` are merged into `doc-brd-audit`.

### Input Sources (Priority Order)

| Priority | Source | Location | Content Type |
|----------|--------|----------|--------------|
| 1 | Reference Documents | `docs/00_REF/` | Technical specs, gap analysis, architecture |
| 2 | Reference Documents (alt) | `REF/` | Alternative location |
| 3 | Existing Documentation | `docs/` or `README.md` | Project context |
| 4 | User Prompts | Interactive | Business context, objectives (fallback) |

### Auto-Generated Files

The autopilot automatically creates/updates these files:

| File | Purpose | Location |
|------|---------|----------|
| `BRD-00_index.md` | Master BRD index with registry | `docs/01_BRD/` |
| `BRD-00_GLOSSARY.md` | Master glossary | `docs/01_BRD/` |

### Usage Examples

```bash
# Generate from reference documents
/doc-brd-autopilot docs/00_REF/foundation/F1_IAM_Technical_Specification.md

# Generate from REF directory
/doc-brd-autopilot REF/

# Interactive mode (prompts for input)
/doc-brd-autopilot
```

### Workflow Phases

1. **Phase 1**: Input Analysis - Scan `docs/00_REF/` or `REF/` for source documents
2. **Phase 2**: BRD Type Determination - Platform vs Feature
3. **Phase 3**: BRD Generation - Create content from template
4. **Phase 4**: Audit FROM SCRATCH - Run `doc-brd-audit` (Fresh Audit Policy)
5. **Phase 5**: Fix Cycle - Run `doc-brd-fixer` → `doc-brd-audit` (loop until PASS)
6. **Phase 6**: Summary - Update `BRD-00_index.md`, generate report

See `.claude/skills/doc-brd-autopilot/SKILL.md` for complete documentation.

## Position in Document Workflow

**[WARN] See [../index.md](../index.md#traceability-flow) for the authoritative workflow visualization.**


BRDs are the **first step** in specification-driven development within the complete SDD workflow:

**Authoritative flow**: BRD → PRD → EARS → BDD → ADR → SYS → REQ → CTR → SPEC → TASKS → Code. See [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) for details.

## ADR References in BRD

**[WARN] CRITICAL - Workflow Order**: BRDs are created BEFORE ADRs in the SDD workflow. Therefore:

[FAIL] **Do NOT** reference specific ADR numbers (ADR-NN, etc.) in BRD documents

[PASS] **DO** include "Architecture Decision Requirements" section describing what decisions are needed

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

## BRD Document Structure (18 Sections)

### Document Control (Section 0 - Top of Document)

| Field | Required | Description |
|-------|----------|-------------|
| Project Name | Yes | Project identifier |
| Document Version | Yes | Semantic version (X.Y) |
| Date | Yes | ISO format (YYYY-MM-DD) |
| Document Owner | Yes | Business executive responsible |
| Prepared By | Yes | Business analyst author |
| Status | Yes | Draft / In Review / Approved |
| PRD-Ready Score | Yes | [Score]/100 (Target: ≥90/100) |
| Revision History | Yes | Version table with changes |

### 18 Numbered Sections

| # | Section | Purpose | Key Subsections |
|---|---------|---------|-----------------|
| **1** | **Introduction** | Purpose, scope, audience | 1.1-1.4 |
| **2** | **Business Objectives** | Goals, hypothesis, metrics | 2.1 Hypothesis, 2.2 Problem, 2.3 Goals, 2.4 Metrics, 2.5 Benefits |
| **3** | **Project Scope** | Boundaries, workflows | 3.1-3.3 Scope, 3.4 Workflow, 3.5 Tech Stack |
| **4** | **Stakeholders** | Decision makers | 4.1 Decision Makers, 4.2 Contributors |
| **5** | **User Stories** | High-level needs | 5.1 Primary, 5.2 Summary |
| **6** | **Functional Requirements** | Business capabilities | 6.1 Overview, 6.2+ Requirements (BRD.NN.01.SS), 6.5 Business Rules |
| **7** | **Quality Attributes** | Performance, security, ADR | 7.1 Overview, **7.2 ADR Topics (7 mandatory)**, 7.3-7.5 |
| **8** | **Constraints & Assumptions** | Limitations | 8.1 Constraints, 8.2 Assumptions |
| **9** | **Acceptance Criteria** | Success measures | 9.1 Launch, 9.2 Post-Launch |
| **10** | **Business Risk Management** | Risk register | Risk ID, Description, Likelihood, Impact, Mitigation |
| **11** | **Implementation Approach** | Phases, rollout | 11.1 Phases, 11.2 Support Model |
| **12** | **Support & Maintenance** | Support model | 12.1 Support, 12.2 Maintenance, 12.3 SLTs |
| **13** | **Cost-Benefit Analysis** | ROI, costs | Development costs, ROI hypothesis |
| **14** | **Project Governance** | Decision authority | **14.1 Structure**, **14.2 Matrix**, **14.3 Reporting**, **14.4 Change Control**, **14.5 Approval** |
| **15** | **Quality Assurance** | QA standards | **15.1 Standards**, **15.2 Testing Strategy**, **15.3 Quality Gates** |
| **16** | **Traceability** | Requirements matrix | **16.1 Matrix**, **16.2 Cross-BRD**, **16.3 Test Coverage**, **16.4 Health Score** |
| **17** | **Glossary** | Terms, acronyms | **17.1 Business**, **17.2 Technical**, **17.3 Domain**, **17.4 Acronyms**, **17.5 Cross-Refs**, **17.6 Standards** |
| **18** | **Appendices** | Supporting docs | A-D: Metrics, Roadmap, Migration, Guidelines |

### Section 7.2: 7 Mandatory ADR Topic Categories

| # | Category | Element ID | Purpose |
|---|----------|------------|---------|
| 1 | Infrastructure | BRD.NN.32.01 | Hosting & Deployment |
| 2 | Data Architecture | BRD.NN.32.02 | Database & Storage |
| 3 | Integration | BRD.NN.32.03 | External Systems |
| 4 | Security | BRD.NN.32.04 | Auth & Data Protection |
| 5 | Observability | BRD.NN.32.05 | Monitoring & Logging |
| 6 | AI/ML | BRD.NN.32.06 | If Applicable |
| 7 | Technology Selection | BRD.NN.32.07 | Core Stack |

### Element ID Format

Pattern: `BRD.{DOC_NUM}.{ELEM_TYPE}.{SEQ}`

| Element Type | Code | Example |
|--------------|------|---------|
| Functional Requirement | 01 | BRD.09.01.01 |
| Quality Attribute | 02 | BRD.09.02.01 |
| Constraint | 03 | BRD.09.03.01 |
| Assumption | 04 | BRD.09.04.01 |
| Acceptance Criteria | 06 | BRD.09.06.01 |
| Risk | 07 | BRD.09.07.01 |
| Business Objective | 23 | BRD.09.23.01 |
| ADR Topic | 32 | BRD.09.32.01 |

### Visual Structure

```
BRD-NN_{slug}.md
├── YAML Frontmatter
├── Document Control (Section 0)
├── Sections 1-13: Core Business Content
├── Sections 14-15: Governance & QA
├── Sections 16-17: Traceability & Reference
└── Section 18: Appendices
```

> **Note**: Section 14 (Project Governance) and Section 15 (Quality Assurance) are mandatory for all BRDs. They define decision authority, approval workflows, quality standards, and testing strategy.

## Available Templates

This directory provides the standard BRD template:

> **Schema Policy: Optional BRD_MVP_SCHEMA.yaml**
>
> BRD validation is human-centric. An optional schema file (`BRD_MVP_SCHEMA.yaml`) exists for non-blocking, machine-readable consistency checks. Primary validation remains script-based and human review.
>
> **Rationale**:
> - Business flexibility and domain variability require flexibility over rigidity
> - Human-centric validation is preferred at Layer 1
> - Sufficient guidance via `BRD_MVP_CREATION_RULES.md` and `BRD_MVP_VALIDATION_RULES.md`
>
> **Validation Approach**: Use `01_BRD/scripts/validate_brd_wrapper.sh` as the canonical BRD validator (core blocking checks by default in pre-commit/CI); use component validators for secondary diagnostics when needed.

**BRD-MVP-TEMPLATE.md** (default) - Streamlined MVP version in a single file without sectioning
- Focused on core MVP features and rapid development
- Maintains framework compliance while reducing documentation overhead
- Ideal for quick MVP launches and hypothesis validation

**Lifecycle**: MVP → PROD → NEW MVP. Expansion happens through new iterations (BRD-02, BRD-03, etc.), not template changes.

## Layer Scripts

This layer includes a dedicated `scripts/` directory containing validation and utility scripts specific to this document type.

- **Location**: `01_BRD/scripts/`
- **Primary Validator**: `validate_brd_wrapper.sh`
- **Usage**: Run scripts directly or usage via `validate_all.py`.

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

## Nested Folder Structure

All BRD documents with review/fix workflows use nested folders to keep related files together.

### Folder Naming

**Pattern**: `BRD-{NN}_{slug}/`

**Examples**:
- `BRD-01_f1_iam/`
- `BRD-07_f7_config/`

### Monolithic vs Sectioned Documents

| Type | When | Document File Pattern |
|------|------|----------------------|
| Monolithic | < 20k tokens | `BRD-{NN}_{slug}.md` |
| Sectioned | > 20k tokens | `BRD-{NN}.{S}_{section}.md` |

### Audit/Fix Companion Files

| File | Purpose | Generated By |
|------|---------|--------------|
| `BRD-{NN}.A_audit_report_v{VVV}.md` | Unified validation + scoring | `doc-brd-audit` |
| `BRD-{NN}.F_fix_report_v{VVV}.md` | Applied fixes summary | `doc-brd-fixer` |
| `.drift_cache.json` | Upstream change detection | `doc-brd-audit` |

**Deprecated**: `BRD-{NN}.R_review_report_*.md` and `BRD-{NN}.V_validation_report_*.md` are legacy (doc-brd-reviewer, doc-brd-validator merged into doc-brd-audit)

### Complete Folder Examples

**Monolithic (small document)**:

```text
BRD-07_f7_config/
 BRD-07_f7_config.md
 BRD-07.A_audit_report_v001.md
 BRD-07.F_fix_report_v001.md
 .drift_cache.json
```

**Sectioned (large document)**:

```text
BRD-01_f1_iam/
 BRD-01.0_index.md
 BRD-01.1_core.md
 BRD-01.2_requirements.md
 BRD-01.3_quality_ops.md
 BRD-01.A_audit_report_v001.md
 BRD-01.F_fix_report_v001.md
 .drift_cache.json
```

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

- **Format**: `[Score]/100 (Target: ≥90/100)` (optional [PASS] emoji allowed)
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
2. **Validation Check**: Run `bash ./01_BRD/scripts/validate_brd_wrapper.sh docs/01_BRD --skip-advisory`
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
