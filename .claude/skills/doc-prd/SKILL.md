---
name: "doc-prd: Create Product Requirements Documents (Layer 2)"
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
  downstream_artifacts: [EARS,BDD,ADR]
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

### 1. Required Sections (21 Total)

PRD documents require exactly **21 numbered sections** (1-21). See `ai_dev_flow/PRD/PRD-TEMPLATE.md` for complete structure.

**Section 1. Document Control** (MANDATORY - First section):
- Project Name
- Document Version
- Date (YYYY-MM-DD)
- Document Owner
- Prepared By
- Status (Draft, In Review, Approved, Superseded)
- **SYS-Ready Score**: ≥90% required (format: `✅ NN% (Target: ≥90%)`)
- **EARS-Ready Score**: ≥90% required (format: `✅ NN% (Target: ≥90%)`)
- Document Revision History table

**All 21 Sections**:
1. **Document Control**: Metadata, version, scores, revision history
2. **Executive Summary**: 3-5 sentence overview
3. **Problem Statement**: What problem are we solving?
4. **Goals**: What do we want to achieve? (Prioritized: P0, P1, P2)
5. **Non-Goals**: What are we explicitly NOT doing?
6. **Target Audience and User Personas**: Who are the users?
7. **User Stories and Use Cases**: User narratives (As a... I want... So that...)
8. **Product Features and Capabilities**: Specific features and functionality
9. **Quality Attributes and Non-Functional Requirements**: Performance, reliability, scalability
10. **Customer-Facing Content**: User-visible text, messaging, UI copy
11. **Data Requirements**: Data models, storage, retention policies
12. **Integration Requirements**: External systems, APIs, dependencies
13. **Security Requirements**: Authentication, authorization, compliance
14. **Analytics and Success Metrics (KPIs)**: Measurable success criteria
15. **Architecture Decision Requirements**: Topics needing ADRs (NOT specific ADR numbers)
16. **Technology Stack Reference**: Reference Platform BRD sections 3.6/3.7
17. **Risk Assessment**: Technical and business risks with mitigation
18. **Acceptance Criteria**: Business-verifiable outcomes
19. **Traceability**: Cumulative tags and upstream/downstream links
20. **EARS Enhancement Appendix**: Structured requirements for EARS transformation
21. **Quality Assurance & Testing Strategy**: QA standards, testing scope, acceptance procedures (moved from BRD)

### 2. Technology Stack Reference

**Feature PRD**:
- Mark as "N/A - See Platform BRD-XXX Section 3.6/3.7"
- Reference specific technology items if relevant to feature

**Platform PRD** (rare):
- May elaborate on technology choices from Platform BRD
- Still references Platform BRD as source of truth

### 3. Architecture Decision Requirements Section (18)

**Purpose**: Elaborate on BRD Section 7.2 architecture topics with **technical content** (options, evaluation criteria).

**Layer Separation Principle**:
```
BRD Section 7.2          →    PRD Section 18         →    ADR
(WHAT & WHY)                  (HOW to evaluate)          (Final decision)
─────────────────────────────────────────────────────────────────────────
Business drivers              Technical options          Selected option
Business constraints          Evaluation criteria        Trade-off analysis
```

**PRD Elaboration Workflow**:
1. Read BRD Section 7.2 topic (`{DOC_TYPE}.NN.EE.SS`)
2. Create corresponding PRD Section 18 subsection
3. Add technical options NOT present in BRD
4. Add evaluation criteria NOT present in BRD
5. Reference upstream BRD topic

**Format** (technical elaboration):
```markdown
## 18. Architecture Decision Requirements

### 18.1 BRD.001.001: API Communication Protocol

**Upstream**: BRD-01 §7.2.1

**Technical Options**:
1. **WebSocket**: Full-duplex, low overhead, native reconnection
2. **REST + Polling**: Stateless, cacheable, higher latency
3. **gRPC Streaming**: Efficient binary, requires HTTP/2

**Evaluation Criteria**:
- **Latency**: Target <100ms (business constraint from BRD)
- **Reconnection**: Auto-reconnect <5s (business constraint from BRD)
- **Complexity**: Development effort for implementation
- **Compatibility**: Broker API support and restrictions

**Product Constraints**:
- Must work through corporate firewalls (port 443)
- Must support mobile app integration (future roadmap)

**Decision Timeline**: Before SPEC-01 creation (blocks implementation)
**ADR Requirements**: [What ADR must decide for THIS topic]
```

**Technical Content Rules**:
- **Technical Options**: Implementation approaches with trade-offs
- **Evaluation Criteria**: Measurable factors for comparing options
- **Product Constraints**: Product-level restrictions (not business constraints - those are in BRD)
- **Decision Timeline**: When decision is needed relative to project milestones

**Cross-Reference Flow**:
1. BRD Section 7.2 → Defines business need (`{DOC_TYPE}.NN.EE.SS`)
2. PRD Section 18 → Elaborates with technical options (references `{DOC_TYPE}.NN.EE.SS`)
3. ADR Section 4.1 → Records final decision (references both)

**Do NOT write**: "See ADR-033" or "Reference ADR-045" (ADRs don't exist yet)

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

### 6. EARS Enhancement Appendix (Section 20)

**Purpose**: Section 20 provides structured requirements ready for EARS transformation in Layer 3.

**Why Required**: The appendix bridges PRD (business language) to EARS (formal requirements), ensuring smooth workflow progression.

**Structure**:
```markdown
## 20. EARS Enhancement Appendix

### 20.1 EARS-Ready Requirements Summary

| PRD Section | Requirement Category | EARS Pattern | Count |
|-------------|---------------------|--------------|-------|
| 8. Features | Functional | WHEN-THE-SHALL | 15 |
| 9. Quality Attributes | Non-Functional | THE-SHALL-WITHIN | 8 |
| 12. Integration | Interface | WHEN-THE-SHALL | 5 |

### 20.2 Pre-Structured Requirements

#### Category: [Feature Name]
**Source**: Section 8.1
**EARS Pattern**: WHEN-THE-SHALL
**Pre-formatted**:
- WHEN [trigger condition] THE [system] SHALL [action]
- WHEN [condition] THE [component] SHALL [response] WITHIN [time constraint]
```

**Key Points**:
- Groups PRD requirements by EARS pattern type
- Provides count of requirements per category
- Pre-formats requirements using EARS syntax
- Enables direct extraction for EARS document creation

## Tag Format Convention (By Design)

The SDD framework uses two distinct notation systems for cross-references:

| Notation | Format       | Artifacts                               | Purpose                                                             |
|----------|--------------|----------------------------------------|---------------------------------------------------------------------|
| Dash     | TYPE-NN     | ADR, SPEC, CTR, IPLAN, ICON            | Technical artifacts - references to files/documents                 |
| Dot      | TYPE.NN.TT.SS | BRD, PRD, EARS, BDD, SYS, REQ, IMPL, TASKS | Hierarchical artifacts - DOC_NUM.ELEM_TYPE.SEQ format |

**Key Distinction**:
- `@adr: ADR-033` → Points to the document `ADR-033_risk_limit_enforcement.md`
- `@brd: BRD.17.01.01` → Points to element 01.01 inside document `BRD-017.md`

## Unified Element ID Format (MANDATORY)

**For hierarchical requirements (BRD, PRD, EARS, BDD, SYS, REQ)**:
- **Always use**: `TYPE.NN.TT.SS` (dot separator, 4-segment unified format)
- **Never use**: `TYPE-NN:NNN` (colon separator - DEPRECATED)
- **Never use**: `TYPE.NN.TT` (3-segment format - DEPRECATED)

Examples:
- `@brd: BRD.17.01.01` ✅
- `@brd: BRD.017.001` ❌ (old 3-segment format)


## Cumulative Tagging Requirements

**Layer 2 (PRD)**: Must include tags from Layer 1 (BRD)

**Tag Count**: 1 tag (@brd)

**Format**:
```markdown
## Traceability

**Required Tags** (Cumulative Tagging Hierarchy - Layer 2):
```markdown
@brd: BRD.01.01.03, BRD.01.01.10
```

- BRD.01.01.03 - Business requirements driving this product
- BRD.01.01.10 - Success criteria from business case

**Upstream Sources**:
- [BRD-01](../BRD/BRD-01_platform.md#BRD-01) - Parent business requirements

**Downstream Artifacts**:
- EARS-NN (to be created) - Formal requirements
- BDD-NN (to be created) - Test scenarios
```

## Upstream/Downstream Artifacts

**Upstream Sources** (what drives PRD creation):
- **BRD** (Layer 1) - Business requirements and objectives

**Downstream Artifacts** (what PRD drives):
- **EARS** (Layer 3) - Formal WHEN-THE-SHALL-WITHIN requirements from PRD features
- **BDD** (Layer 4) - Test scenarios validating PRD functionality
- **ADR** (Layer 5) - Architecture decisions for topics identified in PRD

**Same-Type Document Relationships** (conditional):
- `@related-prd: PRD-NN` - PRDs sharing product domain context
- `@depends-prd: PRD-NN` - PRD that must be implemented first

## Creation Process

### Step 1: Read Parent BRD

Read and understand the BRD that drives this PRD.

### Step 2: Reserve ID Number

Check `docs/PRD/` for next available ID number (e.g., PRD-01, PRD-02).

**ID Matching**: PRD ID does NOT need to match BRD ID (PRD-009 may implement BRD-016).

### Step 3: Create PRD Folder and Files

**Folder structure** (DEFAULT - nested folder per document with descriptive slug):
1. Create folder: `docs/PRD/PRD-NN_{slug}/` (folder slug MUST match index file slug)
2. Create index file: `docs/PRD/PRD-NN_{slug}/PRD-NN.0_{section_type}.md` (shortened, PREFERRED)
3. Create section files: `docs/PRD/PRD-NN_{slug}/PRD-NN.S_{section_type}.md` (shortened, PREFERRED)

**Example (Shortened Pattern - PREFERRED)**:
```
docs/PRD/PRD-01_user_authentication/
├── PRD-01.0_index.md
├── PRD-01.1_overview.md
├── PRD-01.2_features.md
└── PRD-01.3_requirements.md
```

**Note**: Folder contains descriptive slug, so filenames can omit it. Full pattern (`PRD-01.0_user_authentication_index.md`) also accepted for backward compatibility.

**OPTIONAL** (for small documents <25KB): `docs/PRD/PRD-NN_{slug}.md` (monolithic)

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

**MANDATORY**: Create or update `docs/PRD/PRD-00_TRACEABILITY_MATRIX.md`
- Use template: `ai_dev_flow/PRD/PRD-00_TRACEABILITY_MATRIX-TEMPLATE.md`
- Add PRD entry with upstream BRD and downstream artifacts
- Update within same commit as PRD creation

### Step 10: Validate PRD

Run validation scripts:
```bash
# PRD validation (manual validation using template - automated script planned)
# Use PRD-TEMPLATE.md and PRD_VALIDATION_RULES.md for manual validation checklist

# Link integrity
python ai_dev_flow/scripts/validate_links.py --path docs/PRD/

# Cumulative tagging validation
python ai_dev_flow/scripts/validate_tags_against_docs.py --artifact PRD-01 --expected-layers brd --strict
```

### Step 11: Commit Changes

Commit PRD file and traceability matrix together.

## Validation

### Automated Validation

**Quality Gates Validation**:
```bash
./scripts/validate_quality_gates.sh docs/PRD/PRD-NN_slug.md
```

**Tag Validation**:
```bash
# Validate cumulative tags (must have @brd)
python ai_dev_flow/scripts/validate_tags_against_docs.py \
  --artifact PRD-01 \
  --expected-layers brd \
  --strict
```

### Manual Checklist

**Structure (21 Sections)**:
- [ ] All 21 numbered sections present (1-21)
- [ ] Document Control (Section 1) at top with all required fields
- [ ] EARS Enhancement Appendix (Section 20) completed
- [ ] Quality Assurance & Testing Strategy (Section 21) completed

**Document Control Required Fields**:
- [ ] Project Name, Version, Date, Owner, Prepared By, Status
- [ ] SYS-Ready Score ≥90% (format: `✅ NN% (Target: ≥90%)`)
- [ ] EARS-Ready Score ≥90% (format: `✅ NN% (Target: ≥90%)`)
- [ ] Document Revision History table initialized

**Content Quality**:
- [ ] Parent BRD identified and referenced
- [ ] Problem-Goals-Non-Goals framework completed
- [ ] User personas and user stories defined
- [ ] Product features specified with priority levels
- [ ] Quality attributes quantified (performance, reliability)
- [ ] KPIs quantified (measurable metrics with targets)
- [ ] Security requirements documented
- [ ] Risk assessment with mitigation strategies
- [ ] Architecture Decision Requirements listed (NO ADR numbers)
- [ ] Technology Stack reference (Platform BRD sections 3.6/3.7)

**Traceability**:
- [ ] Cumulative tags: @brd included
- [ ] Traceability matrix created/updated
- [ ] No broken links

**Size Limits**:
- [ ] File size <50,000 tokens (standard) or <100,000 tokens (maximum)

## Common Pitfalls

1. **Missing KPIs**: PRD must have quantitative success metrics
2. **Vague goals**: Goals must be specific and measurable
3. **Referencing ADR numbers**: Don't write "See ADR-033" (ADRs don't exist yet)
4. **Missing @brd tags**: Layer 2 must include Layer 1 tags
5. **ID number confusion**: PRD-NN does NOT need to match BRD-NN

## Post-Creation Validation (MANDATORY - NO CONFIRMATION)

**CRITICAL**: Execute this validation loop IMMEDIATELY after document creation. Do NOT proceed to next document until validation passes.

### Automatic Validation Loop

```
LOOP:
  1. Run: python ai_dev_flow/scripts/validate_cross_document.py --document {doc_path} --auto-fix
  2. IF errors fixed: GOTO LOOP (re-validate)
  3. IF warnings fixed: GOTO LOOP (re-validate)
  4. IF unfixable issues: Log for manual review, continue
  5. IF clean: Mark VALIDATED, proceed
```

### Validation Command

```bash
# Per-document validation (Phase 1)
python ai_dev_flow/scripts/validate_cross_document.py --document docs/PRD/PRD-NN_slug.md --auto-fix

# Layer validation (Phase 2) - run when all PRD documents complete
python ai_dev_flow/scripts/validate_cross_document.py --layer PRD --auto-fix
```

### Layer-Specific Upstream Requirements

| This Layer | Required Upstream Tags | Count |
|------------|------------------------|-------|
| PRD (Layer 2) | @brd | 1 tag |

### Auto-Fix Actions (No Confirmation Required)

| Issue | Fix Action |
|-------|------------|
| Missing @brd tag | Add with upstream BRD reference |
| Invalid tag format | Correct to TYPE.NN.TT.SS or TYPE-NN format |
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
# Automated PRD validation script (planned - not yet available)
# Use manual validation with PRD_VALIDATION_RULES.md checklist for now

# Link validation
python ai_dev_flow/scripts/validate_links.py --path docs/PRD/

# Cumulative tag validation
python ai_dev_flow/scripts/validate_tags_against_docs.py --artifact PRD-NN --expected-layers brd --strict
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

**Section Templates** (DEFAULT for all PRD documents):
- **Structure**: `docs/PRD/PRD-NN_{slug}/PRD-NN.S_{slug}.md` (nested folder per document with descriptive slug)
- **Folder Naming**: `PRD-NN_{slug}/` where slug MUST match the index file slug
- Index template: `ai_dev_flow/PRD/PRD-SECTION-0-TEMPLATE.md`
- Content template: `ai_dev_flow/PRD/PRD-SECTION-TEMPLATE.md`
- Reference: `ai_dev_flow/ID_NAMING_STANDARDS.md` (Section-Based File Splitting)
- **Note**: Monolithic template is OPTIONAL for small documents (<25KB)

## Quick Reference

**PRD Purpose**: Define product features and user needs

**Layer**: 2

**Tags Required**: @brd (1 tag)

**Key Sections**:
- Problem-Goals-Non-Goals framework
- KPIs (quantitative metrics)
- Architecture Decision Requirements (topics, NOT ADR numbers)

**Next**: doc-ears
