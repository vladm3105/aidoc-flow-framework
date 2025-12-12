---
title: "doc-prd: Create Product Requirements Documents (Layer 2)"
name: doc-prd
description: Create Product Requirements Documents (PRD) following SDD methodology - Layer 2 artifact defining product features and user needs
tags:
  - sdd-workflow
  - layer-2-artifact
  - shared-architecture
custom_fields:
  layer: 2
  artifact_type: PRD
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  skill_category: core-workflow
  upstream_artifacts: [BRD]
  downstream_artifacts: [EARS,BDD]
---

# doc-prd

## Purpose

Create **Product Requirements Documents (PRD)** - Layer 2 artifact in the SDD workflow that defines product features, user needs, measurable success criteria, and KPIs.

**Layer**: 2

**Upstream**: BRD (Layer 1)

**Downstream Artifacts**: EARS (Layer 3), BDD (Layer 4), ADR (Layer 5)

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


Before creating a PRD, read:

1. **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`
2. **Upstream BRD**: Read the BRD that drives this PRD
3. **Template**: `ai_dev_flow/PRD/PRD-TEMPLATE.md`
4. **Creation Rules**: `ai_dev_flow/PRD/PRD_CREATION_RULES.md`
5. **Validation Rules**: `ai_dev_flow/PRD/PRD_VALIDATION_RULES.md`

## When to Use This Skill

Use `doc-prd` when:
- Have completed BRD (Layer 1)
- Need to define product features and user requirements
- Translating business needs to product specifications
- Establishing KPIs and success metrics
- You are at Layer 2 of the SDD workflow

## PRD-Specific Guidance

### 1. Required Sections

**Document Control** (MANDATORY - First section before all numbered sections):
- Project Name
- Document Version
- Date (YYYY-MM-DD)
- Document Owner
- Prepared By
- Status (Draft, In Review, Approved, Superseded)
- Document Revision History table

**Core Sections**:
1. **Problem Statement**: What problem are we solving?
2. **Goals**: What do we want to achieve?
3. **Non-Goals**: What are we explicitly NOT doing?
4. **User Needs**: Who are the users and what do they need?
5. **Product Features**: Specific features and capabilities
6. **KPIs**: Measurable success criteria (quantitative metrics)
7. **Architecture Decision Requirements**: Topics needing ADRs (NOT specific ADR numbers)
8. **Technology Stack Reference**: Reference Platform BRD sections 3.6/3.7
9. **Traceability**: Section 7 format from SHARED_CONTENT.md

### 2. Technology Stack Reference

**Feature PRD**:
- Mark as "N/A - See Platform BRD-XXX Section 3.6/3.7"
- Reference specific technology items if relevant to feature

**Platform PRD** (rare):
- May elaborate on technology choices from Platform BRD
- Still references Platform BRD as source of truth

### 3. Architecture Decision Requirements Section

**Purpose**: Document what architectural decisions are needed and why; do NOT reference specific ADR numbers (ADRs created in Layer 5)

**Format**:
```markdown
## Architecture Decision Requirements

Based on the product features defined above, the following architectural topics require decision-making:

1. **API Design Pattern**: Feature requires external API; need to decide REST vs GraphQL
2. **State Management**: Complex UI state; need to decide on state management approach
3. **Caching Strategy**: Performance requirements; need to decide on caching implementation

**Note**: Specific ADRs will be created to document these decisions in Layer 5 (ADR phase).
**Inherited from BRD-XXX**: [List any architectural topics from parent BRD]
```

### 4. Problem-Goals-Non-Goals Framework

**Problem Statement** (What we're solving):
- Clear, concise problem definition
- Quantify problem impact where possible
- Reference BRD business needs

**Goals** (What we want to achieve):
- Specific, measurable objectives
- Aligned with BRD success criteria
- Prioritized (P0, P1, P2)

**Non-Goals** (What we're NOT doing):
- Explicit scope limitations
- Features intentionally excluded
- Future considerations (not now)

### 5. KPIs and Success Metrics

**Quantitative Metrics** (MANDATORY):
- Performance targets (latency, throughput)
- User adoption metrics
- Business impact metrics
- Error rates and reliability targets

**Example**:
```markdown
## KPIs

**Performance**:
- P95 latency <500ms for all API calls
- Throughput: 1000 requests/second

**Adoption**:
- 80% of eligible users adopt within 3 months
- Net Promoter Score (NPS) >40

**Business Impact**:
- Reduce manual processing time by 60%
- Decrease error rate from 5% to <1%
```

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


## Cumulative Tagging Requirements

**Layer 2 (PRD)**: Must include tags from Layer 1 (BRD)

**Tag Count**: 1 tag (@brd)

**Format**:
```markdown
## Traceability

**Required Tags** (Cumulative Tagging Hierarchy - Layer 2):
```markdown
@brd: BRD.001.003, BRD.001.010
```

- BRD.001.003 - Business requirements driving this product
- BRD.001.010 - Success criteria from business case

**Upstream Sources**:
- [BRD-001](../BRD/BRD-001_platform.md#BRD-001) - Parent business requirements

**Downstream Artifacts**:
- EARS-NNN (to be created) - Formal requirements
- BDD-NNN (to be created) - Test scenarios
```

## Upstream/Downstream Artifacts

**Upstream Sources** (what drives PRD creation):
- **BRD** (Layer 1) - Business requirements and objectives

**Downstream Artifacts** (what PRD drives):
- **EARS** (Layer 3) - Formal WHEN-THE-SHALL-WITHIN requirements from PRD features
- **BDD** (Layer 4) - Test scenarios validating PRD functionality
- **ADR** (Layer 5) - Architecture decisions for topics identified in PRD

**Same-Type Document Relationships** (conditional):
- `@related-prd: PRD-NNN` - PRDs sharing product domain context
- `@depends-prd: PRD-NNN` - PRD that must be implemented first

## Creation Process

### Step 1: Read Parent BRD

Read and understand the BRD that drives this PRD.

### Step 2: Reserve ID Number

Check `docs/PRD/` for next available ID number (e.g., PRD-001, PRD-002).

**ID Matching**: PRD ID does NOT need to match BRD ID (PRD-009 may implement BRD-016).

### Step 3: Create PRD File

**File naming**: `docs/PRD/PRD-NNN_{slug}.md`

**Example**: `docs/PRD/PRD-001_ib_api_integration.md`

### Step 4: Fill Document Control Section

Complete all required metadata fields and initialize Document Revision History table.

### Step 5: Complete Core Sections

**Problem Statement**: What problem are we solving?
**Goals**: What do we want to achieve? (Prioritized: P0, P1, P2)
**Non-Goals**: What are we NOT doing?
**User Needs**: Who needs this and why?
**Product Features**: Specific capabilities and workflows
**KPIs**: Measurable success metrics

### Step 6: Document Architecture Decision Requirements

List topics needing architectural decisions (do NOT reference specific ADR numbers yet).

### Step 7: Add Technology Stack Reference

- **Feature PRD**: Mark as "N/A - See Platform BRD-XXX Section 3.6/3.7"
- **Platform PRD**: Reference and elaborate on Platform BRD technology choices

### Step 8: Add Cumulative Tags

Include @brd tags (Layer 1) in Traceability section.

### Step 9: Create/Update Traceability Matrix

**MANDATORY**: Create or update `docs/PRD/PRD-000_TRACEABILITY_MATRIX.md`
- Use template: `ai_dev_flow/PRD/PRD-000_TRACEABILITY_MATRIX-TEMPLATE.md`
- Add PRD entry with upstream BRD and downstream artifacts
- Update within same commit as PRD creation

### Step 10: Validate PRD

Run validation scripts:
```bash
# PRD validation (under development - use template for manual validation)
# ./ai_dev_flow/scripts/validate_prd_template.sh docs/PRD/PRD-001_*.md

# Link integrity
./ai_dev_flow/scripts/validate_links.py --path docs/PRD/

# Cumulative tagging validation
python ai_dev_flow/scripts/validate_tags_against_docs.py --artifact PRD-001 --expected-layers brd --strict
```

### Step 11: Commit Changes

Commit PRD file and traceability matrix together.

## Validation

### Automated Validation

**Quality Gates Validation**:
```bash
./scripts/validate_quality_gates.sh docs/PRD/PRD-001_integration.md
```

**Tag Validation**:
```bash
# Validate cumulative tags (must have @brd)
python ai_dev_flow/scripts/validate_tags_against_docs.py \
  --artifact PRD-001 \
  --expected-layers brd \
  --strict
```

### Manual Checklist

- [ ] Document Control section at top (before all numbered sections)
- [ ] All required metadata fields completed
- [ ] Document Revision History table initialized
- [ ] Parent BRD identified and referenced
- [ ] Problem-Goals-Non-Goals framework completed
- [ ] User needs clearly defined
- [ ] Product features specified
- [ ] KPIs quantified (measurable metrics)
- [ ] Architecture Decision Requirements listed (no ADR numbers)
- [ ] Technology Stack reference (Platform BRD sections 3.6/3.7)
- [ ] Cumulative tags: @brd included
- [ ] Traceability matrix created/updated
- [ ] No broken links
- [ ] File size <50,000 tokens (standard) or <100,000 tokens (maximum)

## Common Pitfalls

1. **Missing KPIs**: PRD must have quantitative success metrics
2. **Vague goals**: Goals must be specific and measurable
3. **Referencing ADR numbers**: Don't write "See ADR-033" (ADRs don't exist yet)
4. **Missing @brd tags**: Layer 2 must include Layer 1 tags
5. **ID number confusion**: PRD-NNN does NOT need to match BRD-NNN

## Post-Creation Validation (MANDATORY - NO CONFIRMATION)

**CRITICAL**: Execute this validation loop IMMEDIATELY after document creation. Do NOT proceed to next document until validation passes.

### Automatic Validation Loop

```
LOOP:
  1. Run: python scripts/validate_cross_document.py --document {doc_path} --auto-fix
  2. IF errors fixed: GOTO LOOP (re-validate)
  3. IF warnings fixed: GOTO LOOP (re-validate)
  4. IF unfixable issues: Log for manual review, continue
  5. IF clean: Mark VALIDATED, proceed
```

### Validation Command

```bash
# Per-document validation (Phase 1)
python scripts/validate_cross_document.py --document docs/PRD/PRD-NNN_slug.md --auto-fix

# Layer validation (Phase 2) - run when all PRD documents complete
python scripts/validate_cross_document.py --layer PRD --auto-fix
```

### Layer-Specific Upstream Requirements

| This Layer | Required Upstream Tags | Count |
|------------|------------------------|-------|
| PRD (Layer 2) | @brd | 1 tag |

### Auto-Fix Actions (No Confirmation Required)

| Issue | Fix Action |
|-------|------------|
| Missing @brd tag | Add with upstream BRD reference |
| Invalid tag format | Correct to TYPE.NNN.NNN or TYPE-NNN format |
| Broken link | Recalculate path from current location |
| Missing traceability section | Insert from template |

### Validation Codes Reference

| Code | Description | Severity |
|------|-------------|----------|
| XDOC-001 | Referenced requirement ID not found | ERROR |
| XDOC-002 | Missing cumulative tag | ERROR |
| XDOC-003 | Upstream document not found | ERROR |
| XDOC-006 | Tag format invalid | ERROR |
| XDOC-009 | Missing traceability section | ERROR |

### Quality Gate

**Blocking**: YES - Cannot proceed to next document until Phase 1 validation passes with 0 errors.

---

## Next Skill

After creating PRD, use:

**`doc-ears`** - Create formal EARS requirements (Layer 3)

The EARS will:
- Reference this PRD as upstream source
- Include `@brd` and `@prd` tags (cumulative)
- Use WHEN-THE-SHALL-WITHIN format
- Formalize PRD features into requirements

## Template Binding (MANDATORY)

**When creating PRD documents, use EXACTLY these metadata values:**

```yaml
tags:
  - prd                 # REQUIRED - Use 'prd' NOT 'product-prd', 'feature-prd'
  - layer-2-artifact    # REQUIRED - Layer identifier

custom_fields:
  document_type: prd    # REQUIRED - Use 'prd' NOT 'product-requirements'
  artifact_type: PRD    # REQUIRED - Uppercase
  layer: 2              # REQUIRED - PRD is Layer 2
  architecture_approaches: [ai-agent-based]  # REQUIRED - Array format, NOT singular
```

**FORBIDDEN Values (will fail validation)**:
- Tags: `product-prd`, `feature-prd`, `product-requirements`
- document_type: `product-requirements`, `product_requirements`
- `architecture_approach: value` (singular form)

**Valid architecture_approaches**:
- `[ai-agent-based]` - AI agent primary documents
- `[traditional-8layer]` - Traditional fallback documents
- `[ai-agent-based, traditional-8layer]` - Shared platform documents

**Post-Creation Validation**:
```bash
python scripts/validate_prd.py docs/PRD/PRD-NNN*.md
```

**Schema Reference**: `ai_dev_flow/PRD/PRD_SCHEMA.yaml`

## Reference Documents

For supplementary documentation related to PRD artifacts:
- **Format**: `PRD-REF-NNN_{slug}.md`
- **Skill**: Use `doc-ref` skill
- **Validation**: Minimal (non-blocking)
- **Examples**: Market research, competitive analysis, user personas

## Related Resources

- **Main Guide**: `ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`
- **PRD Schema**: `ai_dev_flow/PRD/PRD_SCHEMA.yaml`
- **PRD Template**: `ai_dev_flow/PRD/PRD-TEMPLATE.md`
- **PRD Creation Rules**: `ai_dev_flow/PRD/PRD_CREATION_RULES.md`
- **PRD Validation Rules**: `ai_dev_flow/PRD/PRD_VALIDATION_RULES.md`
- **PRD README**: `ai_dev_flow/PRD/README.md`
- **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`

## Quick Reference

**PRD Purpose**: Define product features and user needs

**Layer**: 2

**Tags Required**: @brd (1 tag)

**Key Sections**:
- Problem-Goals-Non-Goals framework
- KPIs (quantitative metrics)
- Architecture Decision Requirements (topics, NOT ADR numbers)

**Next**: doc-ears
