---
name: doc-impl
description: Create Implementation Approach (IMPL) - Optional Layer 8 artifact documenting WHO-WHEN-WHAT implementation strategy
tags:
  - sdd-workflow
  - layer-8-artifact
  - shared-architecture
  - documentation-skill
custom_fields:
  layer: 8
  artifact_type: IMPL
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  skill_category: core-workflow
  upstream_artifacts: [REQ]
  downstream_artifacts: [CTR,SPEC]
---

# doc-impl

## Purpose

Create **Implementation Approach (IMPL)** documents - Optional Layer 8 artifact in the SDD workflow that documents WHO will implement WHAT by WHEN, providing implementation strategy and resource allocation.

**Layer**: 8 (Optional)

**Upstream**: BRD (Layer 1), PRD (Layer 2), EARS (Layer 3), BDD (Layer 4), ADR (Layer 5), SYS (Layer 6), REQ (Layer 7)

**Downstream Artifacts**: CTR (Layer 9), SPEC (Layer 10), TASKS (Layer 11), Code (Layer 13)

## Prerequisites

### Upstream Artifact Verification (CRITICAL)

**Before creating this document, you MUST:**

1. **List existing upstream artifacts**:
   ```bash
   ls docs/BRD/ docs/PRD/ docs/EARS/ docs/BDD/ docs/ADR/ docs/SYS/ docs/REQ/ 2>/dev/null
   ```

2. **Reference only existing documents** in traceability tags
3. **Use `null`** only when upstream artifact type genuinely doesn't exist
4. **NEVER use placeholders** like `BRD-XXX` or `TBD`
5. **Do NOT create missing upstream artifacts** - skip functionality instead


Before creating IMPL, read:

1. **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`
2. **Upstream REQ**: Read atomic requirements to implement
3. **Template**: `ai_dev_flow/IMPL/IMPL-TEMPLATE.md`
4. **Creation Rules**: `ai_dev_flow/IMPL/IMPL_CREATION_RULES.md` (refer to template if not available)
5. **Validation Rules**: `ai_dev_flow/IMPL/IMPL_VALIDATION_RULES.md` (refer to template if not available)
6. **Validation Script**: `./ai_dev_flow/scripts/validate_impl.sh`

## When to Use This Skill

Use `doc-impl` when:
- Have completed BRD through REQ (Layers 1-7)
- Need to document implementation approach before coding
- Planning resource allocation and timeline
- Coordinating multiple developers or teams
- This layer is **OPTIONAL** - skip if not needed

## IMPL-Specific Guidance

### 1. WHO-WHEN-WHAT Format

**Purpose**: Document implementation strategy with assignments

**Format**:
```markdown
## Implementation Approach

### WHO: Team/Developer Assignment
**Primary Developer**: @john.doe
**Code Reviewer**: @jane.smith
**QA Engineer**: @bob.johnson

### WHEN: Timeline and Milestones
**Start Date**: 2025-01-15
**Target Completion**: 2025-01-29
**Milestones**:
- Day 1-3: Interface implementation
- Day 4-7: Business logic
- Day 8-10: Error handling
- Day 11-14: Testing and validation

### WHAT: Implementation Scope
**Requirements**: REQ-data-validation-001, REQ-data-validation-002
**Deliverables**:
- Data validation service
- Data processing module
- Error handling middleware
- Unit tests (>80% coverage)
- Integration tests
```

### 2. Required Sections (4-PART Structure)

**Document Control** (MANDATORY - First section before all numbered sections)

**4-PART Structure**:

**PART 1: Project Context and Strategy**
- 1.1 Overview: What system/feature is being implemented
- 1.2 Business Objectives: Requirements satisfied, success criteria
- 1.3 Scope: In-scope and out-of-scope boundaries

**PART 2: Implementation Strategy (WHO-WHEN-WHAT)**
- 2.1 Phases and Milestones: Implementation timeline
- 2.2 Team and Responsibilities (WHO): Team assignments
- 2.3 Deliverables (WHAT): Per-phase outputs
- 2.4 Dependencies and Blockers

**PART 3: Risk Management**
- 3.1 Risk Assessment: Risks with likelihood, impact, mitigation
- 3.2 Contingency Plans: Backup strategies

**PART 4: Traceability**
- 4.1 Upstream Sources: Links to BRD, PRD, EARS, BDD, ADR, SYS, REQ
- 4.2 Downstream Artifacts: CTR, SPEC, TASKS to be created
- 4.3 Cumulative Tags: @brd through @req (7 tags)

### 3. Technical Approach Section

**Format**:
```markdown
## Technical Approach

### Architecture Pattern
**Pattern**: Layered architecture (Controller → Service → Repository)
**Rationale**: Aligns with ADR-045 (REST API design)

### Technology Choices
**Language**: Python 3.11+ (per ADR-000 Technology Stack)
**Framework**: FastAPI (per ADR-000)
**Database**: PostgreSQL (per ADR-033)
**Testing**: pytest, pytest-cov

### Implementation Strategy
1. **Phase 1**: Define data models and schemas (REQ Section 4)
2. **Phase 2**: Implement API endpoints (REQ Section 3)
3. **Phase 3**: Add error handling (REQ Section 5)
4. **Phase 4**: Implement business logic
5. **Phase 5**: Add configuration (REQ Section 6)
6. **Phase 6**: Write tests (REQ Section 10)
```

### 4. Dependencies Section

**Format**:
```markdown
## Dependencies

### Upstream Dependencies
- REQ-data-validation-001: Data validation requirements
- ADR-033: Database technology decision
- ADR-045: API design pattern

### External Dependencies
- PostgreSQL database instance (required before development)
- Authentication service (OAuth 2.0 provider)
- Market data feed (for price validation)

### Blockers
- [ ] Database schema approved by DBA team
- [ ] OAuth client credentials obtained
- [ ] Market data API access granted
```

### 5. Risk Assessment

**Format**:
```markdown
## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Database performance under load | Medium | High | Load testing, connection pooling |
| OAuth integration complexity | Low | Medium | Use proven library, early prototype |
| Market data API rate limits | High | Medium | Implement caching, request batching |
```

## Cumulative Tagging Requirements

**Layer 8 (IMPL)**: Must include tags from Layers 1-7 (BRD, PRD, EARS, BDD, ADR, SYS, REQ)

**Tag Count**: 7 tags (@brd through @req)

**Format**:
```markdown
## Traceability

**Required Tags** (Cumulative Tagging Hierarchy - Layer 8):
```markdown
@brd: BRD-001:section-3
@prd: PRD-001:feature-2
@ears: EARS-001:E01
@bdd: BDD-001:scenario-validation
@adr: ADR-033, ADR-045
@sys: SYS-001:FR-001
@req: REQ-data-validation-001, REQ-data-validation-002
```

**Upstream Sources**:
- [BRD-001](../BRD/BRD-001_platform.md#BRD-001)
- [PRD-001](../PRD/PRD-001_integration.md#PRD-001)
- [EARS-001](../EARS/EARS-001_risk.md#EARS-001)
- [BDD-001](../BDD/BDD-001_limits.feature)
- [ADR-033](../ADR/ADR-033_database.md#ADR-033)
- [SYS-001](../SYS/SYS-001_order.md#SYS-001)
- [REQ-data-validation-001](../REQ/REQ-data-validation-001_*.md)

**Downstream Artifacts**:
- CTR-NNN (to be created) - Data contracts
- SPEC-NNN (to be created) - Technical specifications
- TASKS-NNN (to be created) - Task breakdown
```

## Upstream/Downstream Artifacts

**Upstream Sources**:
- **BRD** (Layer 1) - Business requirements
- **PRD** (Layer 2) - Product features
- **EARS** (Layer 3) - Formal requirements
- **BDD** (Layer 4) - Test scenarios
- **ADR** (Layer 5) - Architecture decisions
- **SYS** (Layer 6) - System requirements
- **REQ** (Layer 7) - Atomic requirements (PRIMARY SOURCE)

**Downstream Artifacts**:
- **CTR** (Layer 9) - Data contracts (optional)
- **SPEC** (Layer 10) - Technical specifications
- **TASKS** (Layer 11) - Task breakdown
- **Code** (Layer 13) - Implementation

## Creation Process

### Step 1: Read Upstream Artifacts

Focus on REQ (Layer 7) - atomic requirements to implement.

### Step 2: Reserve ID Number

Check `ai_dev_flow/IMPL/` for next available ID number.

### Step 3: Create IMPL File

**File naming**: `ai_dev_flow/IMPL/IMPL-NNN_{slug}.md`

**Example**: `ai_dev_flow/IMPL/IMPL-001_position_validation.md`

### Step 4: Fill Document Control Section

Complete metadata and Document Revision History table.

### Step 5: Complete Implementation Overview

Summarize what will be implemented and why.

### Step 6: Document WHO-WHEN-WHAT

**WHO**: Assign team members
**WHEN**: Define timeline and milestones
**WHAT**: Specify scope and deliverables

### Step 7: Define Technical Approach

- Architecture pattern
- Technology choices (reference ADR-000)
- Implementation strategy (phases)

### Step 8: Identify Dependencies

- Upstream artifacts
- External systems
- Blockers (if any)

### Step 9: Assess Risks

Document risks with likelihood, impact, and mitigation.

### Step 10: Add Cumulative Tags

Include all 7 upstream tags (@brd through @req).

### Step 11: Create/Update Traceability Matrix

**MANDATORY**: Update `ai_dev_flow/IMPL/IMPL-000_TRACEABILITY_MATRIX.md`

### Step 12: Validate IMPL

```bash
./ai_dev_flow/scripts/validate_impl.sh ai_dev_flow/IMPL/IMPL-001_*.md

python ai_dev_flow/scripts/validate_tags_against_docs.py --artifact IMPL-001 --expected-layers brd,prd,ears,bdd,adr,sys,req --strict
```

### Step 13: Commit Changes

Commit IMPL file and traceability matrix.

## Validation

### Automated Validation

```bash
# Quality gates
./scripts/validate_quality_gates.sh ai_dev_flow/IMPL/IMPL-001_*.md

# Cumulative tagging
python ai_dev_flow/scripts/validate_tags_against_docs.py \
  --artifact IMPL-001 \
  --expected-layers brd,prd,ears,bdd,adr,sys,req \
  --strict
```

### Manual Checklist

- [ ] Document Control section at top
- [ ] Implementation Overview clear and concise
- [ ] WHO-WHEN-WHAT framework completed
- [ ] Team assignments documented
- [ ] Timeline and milestones defined
- [ ] Technical approach specified
- [ ] Dependencies identified
- [ ] Blockers documented (if any)
- [ ] Risk assessment completed
- [ ] Cumulative tags: @brd through @req (7 tags) included
- [ ] Traceability matrix updated

## Common Pitfalls

1. **Vague assignments**: WHO must specify actual people/teams
2. **Unrealistic timeline**: WHEN must account for dependencies
3. **Scope creep**: WHAT must align strictly with REQ scope
4. **Missing cumulative tags**: Layer 8 must include all 7 upstream tags
5. **No risk assessment**: Must document implementation risks
6. **Skipping when not needed**: IMPL is optional - skip if not valuable

## Next Skill

After creating IMPL (or skipping this optional layer), use:

**`doc-ctr`** - Create Data Contracts (Layer 9, optional)

Or skip to:

**`doc-spec`** - Create Technical Specifications (Layer 10)

The SPEC will:
- Reference REQ (and optionally IMPL) as upstream source
- Include all 7-8 upstream tags
- Use YAML format
- Define implementation contracts
- Achieve 100% implementation-readiness

## Related Resources

- **IMPL Creation Rules**: `ai_dev_flow/IMPL/IMPL_CREATION_RULES.md`
- **IMPL Validation Rules**: `ai_dev_flow/IMPL/IMPL_VALIDATION_RULES.md`
- **IMPL README**: `ai_dev_flow/IMPL/README.md`
- **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`

## Quick Reference

**IMPL Purpose**: Document WHO-WHEN-WHAT implementation approach

**Layer**: 8 (Optional)

**Tags Required**: @brd through @req (7 tags)

**Format**: 4-PART Structure

**Key Parts**:
- **PART 1**: Project Context and Strategy (Overview, Business Objectives, Scope)
- **PART 2**: Implementation Strategy - WHO-WHEN-WHAT (Phases, Team, Deliverables)
- **PART 3**: Risk Management (Assessment, Contingency)
- **PART 4**: Traceability (Upstream, Downstream, Tags)

**Optional**: Skip this layer if implementation approach is straightforward

**Next**: doc-ctr (optional) or doc-spec
