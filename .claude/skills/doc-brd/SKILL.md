---
name: "doc-brd: Create Business Requirements Documents (Layer 1)"
description: Create Business Requirements Documents (BRD) following SDD methodology - Layer 1 artifact defining business needs and objectives
tags:
  - sdd-workflow
  - layer-1-artifact
  - shared-architecture
custom_fields:
  layer: 1
  artifact_type: BRD
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  skill_category: core-workflow
  upstream_artifacts: []
  downstream_artifacts: [PRD, EARS, BDD, ADR]
---

# doc-brd

## Purpose

Create **Business Requirements Documents (BRD)** - Layer 1 artifact in the SDD workflow that defines high-level business needs, strategic objectives, and success criteria.

**Layer**: 1 (Entry point - no upstream dependencies)

**Downstream Artifacts**: PRD (Layer 2), EARS (Layer 3), BDD (Layer 4), ADR (Layer 5)

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
2. **Template**: `ai_dev_flow/BRD/BRD-TEMPLATE.md`
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
- **MUST mark** Section 3.6 as "N/A - See Platform BRD-NNN Section 3.6" and reference specific items
- **MUST mark** Section 3.7 as "N/A - See Platform BRD-NNN Section 3.7" and reference specific conditions

**Reference**: `ai_dev_flow/PLATFORM_VS_FEATURE_BRD.md` for detailed guidance

## BRD-Specific Guidance

### 1. Template Selection

**Primary Template**:

**BRD-TEMPLATE.md** - Comprehensive business requirements (general purpose)
- Use for: All business requirements documents
- Sections: Complete 18-section structure
- Best for: Complex projects, regulatory compliance needs
- Location: `ai_dev_flow/BRD/BRD-TEMPLATE.md`

**Note**: Use the comprehensive template for all BRD documents. For simpler requirements, complete only the essential sections and mark others as "N/A - Not applicable for this scope".

### 2. Required Sections (18 Total)

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

**ALWAYS START WITH STRATEGY**: Read relevant `{project_root}/strategy/` documents FIRST

**Reading Order**:
1. `{project_root}/strategy/README.md` - Performance targets, strategy goals
2. `{project_root}/strategy/strategy_overview.md` - Strategic framework
3. `{project_root}/strategy/core_algorithm.md` - Primary algorithm specifications
4. `{project_root}/strategy/risk_management.md` - Risk management policies
5. `{project_root}/strategy/selection_criteria/` - Entry criteria

**Every BRD MUST cite specific strategy document sections in Traceability section.**

### 4. Architecture Decision Requirements Section (7.2)

**Purpose**: Identify architectural topics requiring decisions using **business-only content**.

**Layer Separation Principle**:
```
BRD Section 7.2          →    PRD Section 18         →    ADR
(WHAT & WHY)                  (HOW to evaluate)          (Final decision)
─────────────────────────────────────────────────────────────────────────
Business drivers              Technical options          Selected option
Business constraints          Evaluation criteria        Trade-off analysis
```

**Subsection ID Format**: `{DOC_TYPE}.NNN.NNN` (3-digit topic number)

| Component | Description | Example |
|-----------|-------------|---------|
| `{DOC_TYPE}` | Document type | `BRD` |
| `.NNN` | Document number (3-4 digits) | `.001` = BRD-001 |
| `.NNN` | Sequential topic number (3 digits, 001-999) | `.003` = third topic |

**Format** (business-only content):
```markdown
## 7.2 Architecture Decision Requirements

### BRD.001.001: API Communication Protocol

**Business Driver**: Real-time market data integration requires low-latency, bidirectional communication for competitive trading execution.

**Business Constraints**:
- Must maintain <100ms latency for order execution
- Must support reconnection without data loss during market hours
- Must comply with broker API terms of service

**PRD Requirements**: [What PRD must elaborate for THIS topic]
```

**Business-Only Content Rules**:
- **Business Driver**: WHY this decision matters to business outcomes
- **Business Constraints**: Non-negotiable business rules (not technical constraints)
- **Do NOT include**: Technical options, implementation approaches, or evaluation criteria (those belong in PRD Section 18)

**Do NOT write**: "See ADR-033" or "Reference ADR-045" (ADRs don't exist yet)

**Cross-Reference Flow**:
1. BRD Section 7.2 → Defines business need (`{DOC_TYPE}.NNN.NNN`)
2. PRD Section 18 → Elaborates with technical options (references `{DOC_TYPE}.NNN.NNN`)
3. ADR Section 4.1 → Records final decision (references both)

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

**Downstream artifacts will tag BRD** (using unified format):
- PRD will include: `@brd: BRD.001.030` (TYPE.DOC.FEATURE format)
- EARS will include: `@brd: BRD.001.030`
- All downstream artifacts inherit BRD tags

## Tag Format Convention (By Design)

The SDD framework uses two distinct notation systems for cross-references:

| Notation | Format       | Artifacts                               | Purpose                                                             |
|----------|--------------|----------------------------------------|---------------------------------------------------------------------|
| Dash     | TYPE-NNN     | ADR, SPEC, CTR, IPLAN, ICON            | Technical artifacts - references to files/documents                 |
| Dot      | TYPE.NNN.NNN | BRD, PRD, EARS, BDD, SYS, REQ, IMPL, TASKS | Hierarchical artifacts - references to features inside documents |

**Key Distinction**:
- `@adr: ADR-033` → Points to the document `ADR-033_risk_limit_enforcement.md`
- `@brd: BRD.017.001` → Points to feature 001 inside document `BRD-017.md`

## Unified Feature ID Format (MANDATORY)

**For hierarchical requirements (BRD, PRD, EARS, BDD, SYS, REQ)**:
- **Always use**: `TYPE.NNN.NNN` (dot separator)
- **Never use**: `TYPE-NNN:NNN` (colon separator - DEPRECATED)

Examples:
- `@brd: BRD.017.001` ✅
- `@brd: BRD-017:001` ❌


## Upstream/Downstream Artifacts

**Upstream Sources** (what drives BRD creation):
- Strategy documents (`{project_root}/strategy/`)
- Business owner requirements
- Market analysis
- Stakeholder inputs

**Downstream Artifacts** (what BRD drives):
- **PRD** (Layer 2) - Product requirements derived from BRD
- **EARS** (Layer 3) - Formal requirements from BRD business needs
- **BDD** (Layer 4) - Test scenarios validating BRD objectives
- **ADR** (Layer 5) - Architecture decisions for topics identified in BRD Section "Architecture Decision Requirements"

**Same-Type Document Relationships** (conditional):
- `@related-brd: BRD-NNN` - BRDs sharing business domain context
- `@depends-brd: BRD-NNN` - BRD that must be implemented first (e.g., platform BRD before feature BRD)

## Creation Process

### Step 1: Determine BRD Type

Use questionnaire above to determine Platform vs Feature BRD.

### Step 2: Read Strategy Documents

Read relevant `{project_root}/strategy/` sections to understand business logic.

### Step 3: Select Template

Choose appropriate template (comprehensive, simplified, or domain-specific).

### Step 4: Reserve ID Number

Check `docs/BRD/` for next available ID number (e.g., BRD-001, BRD-002).

### Step 5: Create BRD File

**File naming**: `docs/BRD/BRD-NNN_{slug}.md`

**Example**: `docs/BRD/BRD-001_ib_mcp_server_platform.md`

### Step 6: Fill Document Control Section

Complete all required metadata fields and initialize Document Revision History table.

### Step 7: Complete Core Sections

Fill all 18 required sections following template structure.

**Platform BRD**: Populate sections 3.6 and 3.7 with technology details
**Feature BRD**: Mark sections 3.6 and 3.7 as "N/A - See Platform BRD-NNN"

### Step 8: Document Architecture Decision Requirements

List topics needing architectural decisions (do NOT reference specific ADR numbers).

### Step 9: Add Strategy References

In Traceability section, link to specific `{project_root}/strategy/` sections.

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
- [ ] All 18 sections completed
- [ ] Traceability matrix created/updated
- [ ] No broken links
- [ ] File size <50,000 tokens (standard) or <100,000 tokens (maximum)

## Common Pitfalls

1. **Referencing ADR numbers**: Don't write "See ADR-033" in Architecture Decision Requirements section (ADRs don't exist yet)
2. **Wrong sections 3.6/3.7 treatment**: Platform BRD must populate, Feature BRD must reference Platform BRD
3. **Missing strategy references**: Every BRD must cite `{project_root}/strategy/` sections
4. **Document Control not first**: Must be at very top before all numbered sections
5. **Skipping traceability matrix**: MANDATORY to create/update matrix

## Post-Creation Validation (MANDATORY - NO CONFIRMATION)

**CRITICAL**: Execute this validation loop IMMEDIATELY after document creation. Do NOT proceed to next document until validation passes.

### Automatic Validation Loop

```
LOOP:
  1. Run BRD template validation script
  2. IF errors found: Fix issues
  3. IF warnings found: Review and address
  4. IF unfixable issues: Log for manual review, continue
  5. IF clean: Mark VALIDATED, proceed
```

### Validation Command

```bash
# BRD structure validation (primary)
./ai_dev_flow/scripts/validate_brd_template.sh docs/BRD/BRD-NNN_slug.md

# Link integrity validation
./ai_dev_flow/scripts/validate_links.py --path docs/BRD/

# Quality gates validation
./scripts/validate_quality_gates.sh docs/BRD/BRD-NNN_slug.md
```

### Layer-Specific Upstream Requirements

| This Layer | Required Upstream Tags | Count |
|------------|------------------------|-------|
| BRD (Layer 1) | None (entry point) | 0 tags |

### Auto-Fix Actions (No Confirmation Required)

| Issue | Fix Action |
|-------|------------|
| Invalid tag format | Correct to TYPE.NNN.NNN or TYPE-NNN format |
| Broken link | Recalculate path from current location |
| Missing traceability section | Insert from template |

### Validation Codes Reference

| Code | Description | Severity |
|------|-------------|----------|
| XDOC-006 | Tag format invalid | ERROR |
| XDOC-008 | Broken internal link | ERROR |
| XDOC-009 | Missing traceability section | ERROR |

### Quality Gate

**Blocking**: YES - Cannot proceed to next document until Phase 1 validation passes with 0 errors.

---

## Next Skill

After creating BRD, use:

**`doc-prd`** - Create Product Requirements Document (Layer 2)

The PRD will:
- Reference this BRD as upstream source
- Include `@brd: BRD.NNN.NNN` tags (unified format)
- Define product features and KPIs
- Inherit Architecture Decision Requirements topics

## Reference Documents

For supplementary documentation related to BRD artifacts:
- **Format**: `BRD-REF-NNN_{slug}.md`
- **Skill**: Use `doc-ref` skill
- **Validation**: Reduced (4 checks only)
- **Examples**: Project overviews, executive summaries, stakeholder guides

### BRD-REF Ready-Score Exemption

**BRD-REF documents are EXEMPT from ready-scores and quality gates:**

| Standard BRD | BRD-REF |
|--------------|---------|
| PRD-Ready Score: ✅ Required (≥90%) | PRD-Ready Score: **NOT APPLICABLE** |
| Cumulative tags: Required | Cumulative tags: **NOT REQUIRED** |
| Quality gates: Full validation | Quality gates: **EXEMPT** |
| Format: Structured 18 sections | Format: **Free format, business-oriented** |

**Purpose**: BRD-REF documents are **reference targets** that other documents link to. They provide supporting information, context, or external references but do not define formal business requirements.

**Reference**: See `ai_dev_flow/BRD/BRD_VALIDATION_RULES.md` for validation details.

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
