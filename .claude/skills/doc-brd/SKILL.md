---
name: doc-brd
description: Create Business Requirements Documents (BRD) following SDD methodology - Layer 1 artifact defining business needs and objectives
tags:
  - sdd-workflow
  - layer-1-artifact
  - shared-architecture
  - documentation-skill
custom_fields:
  layer: 1
  artifact_type: BRD
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  skill_category: core-workflow
  upstream_artifacts: []
  downstream_artifacts: [PRD, EARS, BDD]
---

# doc-brd

## Purpose

Create **Business Requirements Documents (BRD)** - Layer 1 artifact in the SDD workflow that defines high-level business needs, strategic objectives, and success criteria.

**Layer**: 1 (Entry point - no upstream dependencies)

**Downstream Artifacts**: PRD (Layer 2), EARS (Layer 3), BDD (Layer 4)

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


Before creating a BRD, read:

1. **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`
2. **Template**: `ai_dev_flow/BRD/BRD-TEMPLATE.md` (3 templates available)
3. **Creation Rules**: `ai_dev_flow/BRD/BRD_CREATION_RULES.md`
4. **Validation Rules**: `ai_dev_flow/BRD/BRD_VALIDATION_RULES.md`
5. **Platform vs Feature Guide**: `ai_dev_flow/PLATFORM_VS_FEATURE_BRD.md`

**For New Projects**: Use `project-init` skill first to initialize project structure.

## When to Use This Skill

Use `doc-brd` when:
- Starting a new project or feature
- Defining business requirements and objectives
- Documenting strategic alignment and market context
- Establishing success criteria and stakeholder needs
- You are at Layer 1 of the SDD workflow

## BRD Categorization: Platform vs Feature

**CRITICAL DECISION**: Before creating a BRD, determine if it's a **Platform BRD** or **Feature BRD**.

### Questionnaire

1. Does this BRD define infrastructure, technology stack, or cross-cutting concerns?
   - Yes → Likely Platform BRD
   - No → Continue

2. Does this BRD describe a specific user-facing workflow or feature?
   - Yes → Likely Feature BRD
   - No → Continue

3. Will other BRDs depend on or reference this BRD's architectural decisions?
   - Yes → Likely Platform BRD
   - No → Likely Feature BRD

4. Does this BRD establish patterns, standards, or capabilities used across multiple features?
   - Yes → Platform BRD
   - No → Feature BRD

5. Does this BRD implement functionality on top of existing platform capabilities?
   - Yes → Feature BRD
   - No → Platform BRD

### Auto-Detection Logic

- Title contains "Platform", "Architecture", "Infrastructure", "Integration" → Platform BRD
- Title contains specific workflow names, user types (B2C, B2B), or feature names → Feature BRD
- References/depends on BRD-001 or foundation ADRs → Feature BRD
- Establishes technology choices or system-wide patterns → Platform BRD

### Workflow Differences

**Platform BRD Path:**
```
1. Create Platform BRD (populate sections 3.6 and 3.7)
2. Create ADRs for critical technology decisions (identified in BRD sections 3.6/3.7)
3. Create PRD referencing Platform BRD and ADRs
4. Create additional ADRs for implementation details
5. Continue to SPEC
```

**Feature BRD Path:**
```
1. Create Feature BRD (reference Platform BRD in sections 3.6 and 3.7)
2. Create PRD for feature
3. Create ADRs for implementation decisions (if needed)
4. Continue to SPEC
```

### Section 3.6 & 3.7 Rules

**Platform BRD**:
- **MUST populate** Section 3.6 (Technology Stack Prerequisites) with detailed technology choices
- **MUST populate** Section 3.7 (Mandatory Technology Conditions) with non-negotiable constraints

**Feature BRD**:
- **MUST mark** Section 3.6 as "N/A - See Platform BRD-XXX Section 3.6" and reference specific items
- **MUST mark** Section 3.7 as "N/A - See Platform BRD-XXX Section 3.7" and reference specific conditions

**Reference**: `ai_dev_flow/PLATFORM_VS_FEATURE_BRD.md` for detailed guidance

## BRD-Specific Guidance

### 1. Template Selection (3 Available)

**Choose the appropriate template**:

1. **BRD-TEMPLATE.md** - Comprehensive business requirements (general purpose)
   - Use for: Most business requirements
   - Sections: Complete 17-section structure
   - Best for: Complex projects, regulatory compliance needs

2. **BRD-template-2.md** - Alternative format (simplified structure)
   - Use for: Simpler projects, faster iteration
   - Sections: Streamlined structure
   - Best for: Internal tools, MVP features

3. **BRD-trading-template.md** - Trading-specific requirements
   - Use for: Options trading, financial applications
   - Sections: Trading-focused with market context
   - Best for: Trading strategies, risk management features

### 2. Required Sections (17 Total)

**Document Control** (MANDATORY - First section before all numbered sections):
- Project Name
- Document Version
- Date (YYYY-MM-DD)
- Document Owner
- Prepared By
- Status (Draft, In Review, Approved, Superseded)
- Document Revision History table

**Core Sections**:
1. Executive Summary
2. Business Context
3. Stakeholder Analysis
4. Business Requirements
5. Success Criteria
6. Constraints and Assumptions
7. **Architecture Decision Requirements** (topics needing ADRs, NOT specific ADR numbers)
8. Risk Assessment
9. Traceability (Section 7 format from SHARED_CONTENT.md)

**Platform BRD Additional Sections**:
- **3.6 Technology Stack Prerequisites** (MUST populate for Platform BRD)
- **3.7 Mandatory Technology Conditions** (MUST populate for Platform BRD)

### 3. Strategy References (MANDATORY)

**ALWAYS START WITH STRATEGY**: Read relevant `option_strategy/` documents FIRST

**Reading Order**:
1. `option_strategy/README.md` - Performance targets, strategy goals
2. `option_strategy/Integrated_strategy_desc.md` - Strategic framework
3. `option_strategy/integrated_strategy_algo_v5.md` - Bot-executable algorithm
4. `option_strategy/delta_hedging.md` + `greeks_adjustment.md` - Risk management
5. `option_strategy/stock_selection/` - Entry criteria

**Every BRD MUST cite specific strategy document sections in Traceability section.**

### 4. Architecture Decision Requirements Section

**Purpose**: Identify architectural topics requiring decisions; do NOT reference specific ADR numbers (ADRs created in later phase)

**Format**:
```markdown
## Architecture Decision Requirements

The following architectural topics require decision-making:

1. **Technology Stack Selection**: Need to decide on programming language, frameworks, and core libraries
2. **Data Storage Architecture**: Need to decide on database technology and data modeling approach
3. **API Design Patterns**: Need to decide on REST vs GraphQL vs gRPC
4. **Authentication & Authorization**: Need to decide on security implementation approach

**Note**: Specific ADRs will be created to document these decisions in Layer 5 (ADR phase).
```

**Do NOT write**: "See ADR-033" or "Reference ADR-045" (ADRs don't exist yet)

### 5. Document Control Section Positioning

**CRITICAL**: Document Control MUST be the **first section** at the very top of the BRD (before all numbered sections).

**Correct Structure**:
```markdown
# BRD-001: Project Name

## Document Control
[All metadata fields here]

## 1. Executive Summary
[Content here]
```

## Cumulative Tagging Requirements

**Layer 1 (BRD)**: No upstream tags required (entry point)

**Tag Count**: 0 tags

**Format**: BRD has no `@` tags since it's Layer 1 (top of hierarchy)

**Downstream artifacts will tag BRD**:
- PRD will include: `@brd: BRD-001:section-name`
- EARS will include: `@brd: BRD-001:section-name`
- All downstream artifacts inherit BRD tags

## Upstream/Downstream Artifacts

**Upstream Sources** (what drives BRD creation):
- Strategy documents (`option_strategy/`)
- Business owner requirements
- Market analysis
- Stakeholder inputs

**Downstream Artifacts** (what BRD drives):
- **PRD** (Layer 2) - Product requirements derived from BRD
- **EARS** (Layer 3) - Formal requirements from BRD business needs
- **BDD** (Layer 4) - Test scenarios validating BRD objectives
- **ADR** (Layer 5) - Architecture decisions for topics identified in BRD Section "Architecture Decision Requirements"

## Creation Process

### Step 1: Determine BRD Type

Use questionnaire above to determine Platform vs Feature BRD.

### Step 2: Read Strategy Documents

Read relevant `option_strategy/` sections to understand business logic.

### Step 3: Select Template

Choose appropriate template (comprehensive, simplified, or trading-specific).

### Step 4: Reserve ID Number

Check `docs/BRD/` for next available ID number (e.g., BRD-001, BRD-002).

### Step 5: Create BRD File

**File naming**: `docs/BRD/BRD-NNN_{slug}.md`

**Example**: `docs/BRD/BRD-001_ib_mcp_server_platform.md`

### Step 6: Fill Document Control Section

Complete all required metadata fields and initialize Document Revision History table.

### Step 7: Complete Core Sections

Fill all 17 required sections following template structure.

**Platform BRD**: Populate sections 3.6 and 3.7 with technology details
**Feature BRD**: Mark sections 3.6 and 3.7 as "N/A - See Platform BRD-XXX"

### Step 8: Document Architecture Decision Requirements

List topics needing architectural decisions (do NOT reference specific ADR numbers).

### Step 9: Add Strategy References

In Traceability section, link to specific `option_strategy/` sections.

### Step 10: Create/Update Traceability Matrix

**MANDATORY**: Create or update `docs/BRD/BRD-000_TRACEABILITY_MATRIX.md`
- Use template: `ai_dev_flow/BRD/BRD-000_TRACEABILITY_MATRIX-TEMPLATE.md`
- Add BRD entry with upstream sources and downstream artifacts
- Update traceability matrix in same commit after BRD validation passes (see SHARED_CONTENT.md Traceability Matrix Update Workflow)

### Step 11: Validate BRD

Run validation scripts:
```bash
# BRD structure validation
./ai_dev_flow/scripts/validate_brd_template.sh docs/BRD/BRD-001_*.md

# Link integrity
./ai_dev_flow/scripts/validate_links.py --path docs/BRD/
```

### Step 12: Commit Changes

Commit BRD file and traceability matrix together.

## Validation

### Automated Validation

**BRD-Specific Validation**:
```bash
./ai_dev_flow/scripts/validate_brd_template.sh docs/BRD/BRD-001_platform.md
```

**Quality Gates Validation**:
```bash
./scripts/validate_quality_gates.sh docs/BRD/BRD-001_platform.md
```

### Manual Checklist

- [ ] Document Control section at top (before all numbered sections)
- [ ] All required metadata fields completed
- [ ] Document Revision History table initialized
- [ ] BRD type determined (Platform vs Feature)
- [ ] Sections 3.6 & 3.7 handled correctly for BRD type
- [ ] Architecture Decision Requirements listed (no ADR numbers referenced)
- [ ] Strategy references in Traceability section
- [ ] All 17 sections completed
- [ ] Traceability matrix created/updated
- [ ] No broken links
- [ ] File size <50,000 tokens (standard) or <100,000 tokens (maximum)

## Common Pitfalls

1. **Referencing ADR numbers**: Don't write "See ADR-033" in Architecture Decision Requirements section (ADRs don't exist yet)
2. **Wrong sections 3.6/3.7 treatment**: Platform BRD must populate, Feature BRD must reference Platform BRD
3. **Missing strategy references**: Every BRD must cite `option_strategy/` sections
4. **Document Control not first**: Must be at very top before all numbered sections
5. **Skipping traceability matrix**: MANDATORY to create/update matrix

## Next Skill

After creating BRD, use:

**`doc-prd`** - Create Product Requirements Document (Layer 2)

The PRD will:
- Reference this BRD as upstream source
- Include `@brd: BRD-NNN:section` tags
- Define product features and KPIs
- Inherit Architecture Decision Requirements topics

## Related Resources

- **Main Guide**: `ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`
- **Platform vs Feature Guide**: `ai_dev_flow/PLATFORM_VS_FEATURE_BRD.md`
- **BRD Creation Rules**: `ai_dev_flow/BRD/BRD_CREATION_RULES.md`
- **BRD Validation Rules**: `ai_dev_flow/BRD/BRD_VALIDATION_RULES.md`
- **BRD README**: `ai_dev_flow/BRD/README.md`
- **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`

## Quick Reference

**BRD Purpose**: Define business needs and objectives

**Layer**: 1 (Entry point)

**Tags Required**: None (0 tags)

**Key Decision**: Platform vs Feature BRD

**Critical Sections**:
- 3.6 Technology Stack Prerequisites (Platform BRD populates, Feature BRD references)
- 3.7 Mandatory Technology Conditions (Platform BRD populates, Feature BRD references)
- Architecture Decision Requirements (list topics, NOT ADR numbers)

**Next**: doc-prd
