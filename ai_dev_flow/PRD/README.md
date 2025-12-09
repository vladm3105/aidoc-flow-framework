---
title: "Product Requirements Documents (PRD)"
tags:
  - index-document
  - layer-2-artifact
  - shared-architecture
custom_fields:
  document_type: readme
  artifact_type: PRD
  layer: 2
  priority: shared
---

# Product Requirements Documents (PRD)

Product Requirements Documents (PRDs) serve as the foundational business requirements that drive all downstream technical development. PRDs capture "what" needs to be built before any consideration of "how," establishing the product contract between business goals and technical implementation.

## Purpose

PRDs transform high-level business objectives into concrete, measurable product requirements that:
- Define the problem and business value propositions
- Set clear scope boundaries with goals and non-goals
- Establish measurable success criteria through KPIs
- Provide traceability to downstream technical artifacts
- Create the authoritative source for all implementation decisions

## resource in Development Workflow

**⚠️ See [../index.md](../index.md#traceability-flow) for the authoritative workflow visualization.**


PRDs are the **starting point** of specification-driven development within the complete SDD workflow:

**⚠️ See for the full document flow: /opt/data/docs_flow_framework/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md**

## ADR References in PRD

**⚠️ CRITICAL - Workflow Order**: PRDs are created BEFORE ADRs in the SDD workflow. Therefore:

❌ **Do NOT** reference specific ADR numbers (ADR-001, ADR-011, etc.) in PRD documents

✅ **DO** include "Architecture Decision Requirements" section describing what decisions are needed

**Correct Workflow Order**: BRD → PRD → SYS → EARS → REQ → **ADR** → BDD → IMPL → CTR → SPEC → TASKS

**Rationale**:
- BRD/PRD identify **WHAT** architectural decisions are needed
- ADRs document **WHICH** option was chosen and **WHY**
- This separation maintains clear workflow phases and prevents broken references

**Architecture Decision Requirements section**:
Every PRD should include a section that lists architectural topics requiring decisions:

```markdown
#### Architecture Decision Requirements

| Topic Area | Decision Needed | Business Driver (PRD Reference) | Key Considerations |
|------------|-----------------|--------------------------------|-------------------|
| Agent Framework | Select orchestration framework | FR-XXX (multi-agent coordination) | Google ADK, LangGraph, custom |
| Database Technology | Choose operational database | FR-XXX (data persistence) + NFR-XXX (performance) | Cloud SQL, Firestore, BigQuery |
| Caching Strategy | Define cache architecture | NFR-XXX (<100ms latency) | Redis, in-memory, CDN |

**Purpose**: Identify architectural topics requiring decisions. Specific ADRs created AFTER this PRD.
**Timing**: ADRs created after BRD → PRD → SYS → EARS → REQ in SDD workflow.
```

## PRD Structure

### Header with Traceability Tags

All PRDs include traceability links to related artifacts (note: ADR links added AFTER ADRs are created):

```markdown
@requirement:[REQ-NNN](../REQ/.../REQ-NNN_...md#REQ-NNN)
@SYS:[SYS-NNN](../SYS/SYS-NNN_...md)
@EARS:[EARS-NNN](../EARS/EARS-NNN_...md)
@spec:[SPEC-NNN](../SPEC/.../SPEC-NNN_...yaml)
@bdd:[BDD-NNN:scenarios](../BDD/BDD-NNN_....feature#scenarios)

Note: @adr tags added to PRD AFTER ADRs are created (not during initial PRD creation)
```

### Problem Statement
Clearly define the business problem or opportunity:

```markdown
## Problem
[Concise description of the current state problem and its business impact]
```

### Goals
Define what success looks like:

```markdown
## Goals
- [Specific, achievable business outcomes]
- [Measurable goals that drive implementation decisions]
- [Clear success criteria for stakeholders]
```

### Non-Goals
Explicitly define what is **not** included (critical for scope management):

```markdown
## Non-Goals
- [Functionality explicitly excluded from this initiative]
- [Out-of-scope features that might seem related]
- [Technical implementation decisions made elsewhere]
```

### KPIs (Key Performance Indicators)
Quantifiable metrics defining success:

```markdown
## KPIs
- [Business metric] ≥ [target value] within [timeframe]
- [Performance benchmark] < [threshold] during [conditions]
- [Quality measure] maintained at [level] across [scenarios]
```

### Functional Requirements (Optional)
High-level functional capabilities (may be moved to EARS for detailed requirements):

```markdown
## Functional Requirements
- [High-level capability descriptions]
- [Business-oriented feature descriptions]
- [Integration requirements with existing systems]
```

### Acceptance (High-Level)
Business-focused acceptance criteria:

```markdown
## Acceptance (High-Level)
- [Business-verifiable outcomes]
- [Stakeholder acceptance criteria]
- [Integration validation requirements]
```

### Traceability
Link to upstream and downstream artifacts:

```markdown
## Traceability
- Downstream Artifacts: [SYS-NNN](../SYS/SYS-NNN_...md), [EARS-NNN](../EARS/EARS-NNN_...md), [REQ-NNN](../REQ/.../REQ-NNN_...md#REQ-NNN)
- Anchors/IDs: `# PRD-NNN`
- Code Path(s): `src/component/module.py`
```

### Platform vs Feature Categorization

PRDs inherit categorization context from their source BRDs:

**Platform BRDs → Foundation PRDs**:
- Platform BRDs (e.g., BRD-001 Platform Architecture) drive foundation-level PRDs
- These PRDs define core capabilities, infrastructure components, and cross-cutting concerns
- Typically created early in the development workflow
- Referenced by multiple feature-specific PRDs

**Feature BRDs → Feature PRDs**:
- Feature BRDs (e.g., BRD-006 B2C KYC Onboarding) drive feature-specific PRDs
- These PRDs detail user-facing functionality and workflows
- Build upon platform capabilities defined in Platform BRDs
- Reference foundation PRDs for infrastructure dependencies

**Cross-Referencing**:
- Feature PRDs should explicitly reference the Platform BRD(s) they depend on
- Include references in the "Dependencies" or "Technical Context" sections
- Link to relevant foundation PRDs that provide required capabilities

**Reference**: See [PLATFORM_VS_FEATURE_BRD.md](../PLATFORM_VS_FEATURE_BRD.md) for BRD categorization methodology

## SYS-Ready Scoring System ⭐ NEW

**Purpose**: SYS-ready scoring measures PRD maturity and readiness for progression to System Requirements (SYS) phase in SDD workflow. Minimum score of 90% required to advance to SYS creation.

**Quality Gate Requirements**:
- **SYS-Ready Score**: Must be ≥90% to pass validation and progress to SYS phase
- **Format**: `✅ NN% (Target: ≥90%)` in Document Control table
- **Location**: Required field in Document Control metadata
- **Validation**: Enforced before commit via `validate_prd_template.sh`

**Scoring Criteria**:

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

**Usage Examples**:

**High Scoring PRD (95%)**:
```markdown
| **SYS-Ready Score** | ✅ 95% (Target: ≥90%) |
```

**Marginal PRD (85%) - Requires Improvement**:
```markdown
| **SYS-Ready Score** | ⚠️ 85% (Below 90% target) |
```

**Workflow Integration**:
1. **PRD Creation**: Include SYS-ready and EARS-ready scores in Document Control section
2. **Quality Check**: Run `./scripts/validate_prd_template.sh docs/PRD/PRD-001_name.md`
3. **EARS Readiness**: EARS-ready score ≥90% enables progression to EARS artifact creation
4. **SYS Readiness**: SYS-ready score ≥90% enables progression to SYS artifact creation

**Scoring Calculation Process**:
1. Assess each criteria category against PRD content
2. Calculate points earned vs. available points
3. Compute percentage: (points earned / total points) × 100
4. Update score in Document Control table
5. Re-run validation to confirm quality gate passage

**Purpose in SDD Workflow**: Ensures PRD quality meets SYS phase requirements, preventing immature product requirements from progressing to technical specification phases.

## File Naming Convention

```
PRD-NNN_descriptive_title.md
```

Where:
- `PRD` is the constant prefix
- `NNN` is the three-digit sequence number (001, 002, 003, etc.)
- `descriptive_title` uses snake_case for clarity

**Examples:**
- `PRD-001_external_api_integration.md`
- `PRD-035_resource_limit_enforcement.md`
- `PRD-042_ml_model_serving.md`

## Writing Guidelines

### 1. Focus on Business Value
- Start with business problems, not technical solutions
- Emphasize user/business benefits and market needs
- Avoid premature technical implementation details

### 2. Define Scope Clearly
- Use Non-Goals to explicitly exclude tempting but out-of-scope features
- Document assumptions and dependencies
- Clarify stakeholder responsibilities

### 3. Make Requirements Measurable
- Include specific KPIs and success metrics
- Define acceptance criteria in business terms
- Provide quantitative thresholds where possible

### 4. Maintain Traceability
- Include complete header tags linking to related artifacts
- Reference existing systems, contracts, and dependencies
- Update traceability sections when related artifacts are created

**PRD Traceability Rules**:
- **Upstream Traceability**: REQUIRED - All PRDs MUST reference at least one existing BRD business requirement
- **Downstream Traceability**: OPTIONAL - Only add links to downstream documents (SYS, EARS, SPEC, etc.) that already exist. Do NOT use placeholder IDs (TBD, XXX, NNN)

### 5. Enable Testability
- Write acceptance criteria that can be verified by business stakeholders
- Avoid vague terms like "user-friendly" or "reliable"
- Define clear success conditions for each goal

## PRD Quality Gates

**Every PRD must include:**
- Clear problem statement with business context
- Specific, achievable goals
- Explicit non-goals defining scope boundaries
- Measurable KPIS with quantified targets
- Traceability tags linking to downstream artifacts
- Business-focused acceptance criteria

**PRD content standards:**
- Business language over technical jargon where possible
- Links resolve to existing artifacts or include placeholders for planned work
- Assumptions and constraints are explicitly documented
- Stakeholder acceptance criteria are verifiable

## PRD Evolution and Maintenance

### Initial Draft
Focus on capturing business requirements without over-constraining solutions:

```markdown
## Problem
Users struggle with [pain point], resulting in [business impact].

## Goals
Enable users to [business outcome] safely and efficiently.
Measure success by [quantifiable metric].
```

### Technical Alignment
Add technical context as system requirements emerge:

```markdown
## Goals
Enable users to [business outcome] with [technical constraint].
Maintain [performance target] during [conditions].
```

### Production Ready
Include complete traceability and acceptance criteria:

```markdown
## Traceability
- SRC: [SYS-NNN](../SYS/SYS-NNN_component.md)
- EARS: [EARS-NNN](../EARS/EARS-NNN_component.md)
- Implementation: src/component/
```

## Common Patterns

### Integration PRDs
```markdown
## Problem
Manual [process] creates operational friction and limits scalability.

## Goals
Seamlessly integrate [system A] with [system B] with comprehensive error handling.
Ensure [critical business process] completes within [timeframe].
```

### Feature PRDs
```markdown
## Problem
Customers cannot [desired capability], requiring workarounds with [cost].

## Goals
Provide [capability] through [user interaction].
Enable [business benefit] with [quantified improvement].
```

### Infrastructure PRDs
```markdown
## Problem
[System constraint] prevents [business growth] above [current limit].

## Goals
Extend platform to support [target scale] with [reliability standard].
Maintain [SLA] during peak usage periods.
```

## Example PRD Template

See `PRD-001_external_api_integration.md` for a complete example of a well-structured PRD that follows these conventions.

## Benefits of Strong PRDs

1. **Alignment**: Ensures technical work directly supports business objectives
2. **Clarity**: Eliminates ambiguity in scope and acceptance criteria
3. **Efficiency**: Reduces rework by establishing requirements before design
4. **Communication**: Provides single source of truth for stakeholder questions
5. **Traceability**: Maintains links from business needs through implementation

## Avoiding Common Pitfalls

1. **Technical Overload**: Don't write PRDs that read like technical specifications
2. **Scope Creep**: Use Non-Goals liberally to prevent feature requests
3. **Vague Metrics**: Always quantify KPIs with specific, measurable targets
4. **Orphaned Requirements**: Maintain traceability links as development progresses
5. **Implementation Details**: Focus on "what" not "how" (save technical details for SRC/EARS)

## Integration with Product Management

PRDs serve as:
- **Product Backlog Items**: Connected to business objectives and KPIs
- **Stakeholder Agreements**: Signed-off requirements for project approval
- **Success Validation**: Acceptance criteria for project completion
- **Change Control**: Baselines for scope changes and change requests

## Version Control and Collaboration

- PRD commits should include issue/PR references
- Major changes require stakeholder re-approval
- Include PRD references in specification reviews
- Archive superseded PRDs while maintaining links to replacements
