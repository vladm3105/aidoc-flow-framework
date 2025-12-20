---
name: doc-ears
description: Create EARS (Easy Approach to Requirements Syntax) formal requirements - Layer 3 artifact using WHEN-THE-SHALL-WITHIN format
tags:
  - sdd-workflow
  - layer-3-artifact
  - shared-architecture
custom_fields:
  layer: 3
  artifact_type: EARS
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  skill_category: core-workflow
  upstream_artifacts: [BRD, PRD]
  downstream_artifacts: [BDD, ADR, SYS]
---

# doc-ears

## Purpose

Create **EARS (Easy Approach to Requirements Syntax)** documents - Layer 3 artifact in the SDD workflow that formalizes requirements using the WHEN-THE-SHALL-WITHIN syntax.

**Layer**: 3

**Upstream**: BRD (Layer 1), PRD (Layer 2)

**Downstream Artifacts**: BDD (Layer 4), ADR (Layer 5), SYS (Layer 6)

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


Before creating EARS, read:

1. **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`
2. **Upstream BRD and PRD**: Read the BRD and PRD that drive this EARS
3. **Template**: `ai_dev_flow/EARS/EARS-TEMPLATE.md` (Template Version 3.0, includes METADATA CLARIFICATION block)
4. **Schema**: `ai_dev_flow/EARS/EARS_SCHEMA.yaml` (machine-readable validation rules)
5. **Creation Rules**: `ai_dev_flow/EARS/EARS_CREATION_RULES.md`
6. **Validation Rules**: `ai_dev_flow/EARS/EARS_VALIDATION_RULES.md`

### Template Binding (CRITICAL)

**Always use these exact metadata values:**

```yaml
tags:
  - ears                 # NOT 'ears-requirements' or 'ears-formal-requirements'
  - layer-3-artifact
  - shared-architecture  # OR 'ai-agent-primary' for agent docs

custom_fields:
  document_type: ears    # NOT 'engineering-requirements'
  artifact_type: EARS
  layer: 3
  architecture_approaches: [ai-agent-based, traditional-8layer]  # ARRAY format
  priority: shared
  development_status: active
```

**Source Document Format:**
```
| **Source Document** | @prd: PRD.NN.07.SS |
```

**Post-Creation Validation:**
```bash
# EARS validation (under development - use template for manual validation)
# python scripts/validate_ears.py --path docs/EARS/EARS-NN.md
```

## When to Use This Skill

Use `doc-ears` when:
- Have completed BRD (Layer 1) and PRD (Layer 2)
- Need to formalize requirements with precise behavioral statements
- Translating product features into formal requirements
- Establishing event-driven, state-driven, or conditional requirements
- You are at Layer 3 of the SDD workflow

## EARS-Specific Guidance

### 1. WHEN-THE-SHALL-WITHIN Syntax

**Format**: `WHEN [trigger] THE [system] SHALL [response] WITHIN [constraint]`

**Components**:
- **WHEN**: Trigger condition or event
- **THE**: System or component name
- **SHALL**: Required behavior (use SHALL for mandatory, SHOULD for recommended, MAY for optional)
- **WITHIN**: Time, resource, or quality constraint

**Example**:
```
WHEN position limit is exceeded
THE risk management system
SHALL reject the trade
WITHIN 100 milliseconds
```

### 2. Four EARS Statement Types

**1. Event-Driven Requirements**
- Triggered by specific events
- Format: `WHEN [event occurs] THE [system] SHALL [response] WITHIN [time]`
- Example: `WHEN data update received THE calculation engine SHALL recalculate metrics WITHIN 50ms`

**2. State-Driven Requirements**
- Triggered by system state
- Format: `WHEN [system is in state] THE [system] SHALL [maintain/enforce] WITHIN [constraint]`
- Example: `WHEN resource utilization exceeds 80% THE scaling system SHALL initiate rebalance WITHIN 2 minutes`

**3. Unwanted Behavior Requirements**
- Prevents undesired outcomes
- Format: `IF [unwanted condition], THEN THE [system] SHALL [preventive action] WITHIN [constraint]`
- Example: `IF API rate limit exceeded, THEN THE system SHALL queue requests WITHIN 100ms`

**4. Ubiquitous Requirements**
- Always active, no trigger
- Format: `THE [system] SHALL [behavior] WITHIN [constraint]`
- Example: `THE authentication service SHALL encrypt all passwords using bcrypt WITHIN security policy`

### 3. Required Sections

**Document Control** (MANDATORY - First section before all numbered sections):
- Project Name
- Document Version
- Date (YYYY-MM-DD)
- Document Owner
- Prepared By
- Status (Draft, In Review, Approved, Superseded)
- Document Revision History table

**Core Sections**:
1. **Introduction**: Purpose and scope of requirements
2. **Event-Driven Requirements**: WHEN [event] THE SHALL WITHIN
3. **State-Driven Requirements**: WHEN [state] THE SHALL WITHIN
4. **Unwanted Behavior Requirements**: IF [unwanted], THEN THE SHALL WITHIN
5. **Ubiquitous Requirements**: THE SHALL WITHIN (always active)
6. **Traceability**: Section 7 format from SHARED_CONTENT.md

### 4. BDD-Ready Scoring System

**Purpose**: Measures EARS maturity and readiness for progression to Behavior-Driven Development (BDD) phase.

**Format in Document Control**:
```markdown
| **BDD-Ready Score** | ✅ 95% (Target: ≥90%) |
```

**Status and BDD-Ready Score Mapping**:

| BDD-Ready Score | Required Status |
|-----------------|-----------------|
| ≥90% | Approved |
| 70-89% | In Review |
| <70% | Draft |

**Scoring Criteria**:
- **Requirements Clarity (40%)**: EARS statements follow WHEN-THE-SHALL-WITHIN syntax, atomicity, quantifiable constraints
- **Testability (35%)**: BDD translation possible, observable verification methods, edge cases specified
- **Quality Attribute Completeness (15%)**: Performance targets with percentiles, security/compliance complete, reliability measurable
- **Strategic Alignment (10%)**: Links to business objectives, implementation paths documented

**Quality Gate**: Score <90% blocks BDD artifact creation.

### 5. Formal Language Rules

**Mandatory Keywords**:
- **SHALL**: Mandatory requirement (do this)
- **SHALL NOT**: Prohibited requirement (never do this)
- **SHOULD**: Recommended requirement (preferred but not mandatory)
- **MAY**: Optional requirement (allowed but not required)

**Avoid**:
- Ambiguous terms: "fast", "efficient", "user-friendly"
- Use quantifiable metrics: "within 100ms", "with 99.9% uptime", "using bcrypt with 12 rounds"

**Example - Bad**:
```
WHEN trade is placed THE system SHALL process it quickly
```

**Example - Good**:
```
WHEN trade order received THE order management system SHALL validate and route order WITHIN 50 milliseconds
```

## Tag Format Convention (By Design)

The SDD framework uses two distinct notation systems for cross-references:

| Notation | Format        | Artifacts                               | Purpose                                                             |
|----------|---------------|----------------------------------------|---------------------------------------------------------------------|
| Dash     | TYPE-NN      | ADR, SPEC, CTR, IPLAN, ICON            | Technical artifacts - references to files/documents                 |
| Dot      | TYPE.NN.TT.SS | BRD, PRD, EARS, BDD, SYS, REQ, IMPL, TASKS | Hierarchical artifacts - references to elements inside documents |

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

**Layer 3 (EARS)**: Must include tags from Layers 1-2 (BRD, PRD)

**Tag Count**: 2 tags (@brd, @prd)

**Format**:
```markdown
## Traceability

**Required Tags** (Cumulative Tagging Hierarchy - Layer 3):
```markdown
@brd: BRD.01.01.03, BRD.01.01.10
@prd: PRD.01.07.02, PRD.01.07.15
```

- BRD.01.01.03 - Business requirements driving these formal requirements
- BRD.01.01.10 - Success criteria from business case
- PRD.01.07.02 - Product feature being formalized
- PRD.01.07.15 - Performance KPI targets

**Upstream Sources**:
- [BRD-01](../BRD/BRD-01_platform.md#BRD-01) - Business requirements
- [PRD-01](../PRD/PRD-01_integration.md#PRD-01) - Product requirements

**Downstream Artifacts**:
- BDD-NN (to be created) - Test scenarios
- ADR-NN (to be created) - Architecture decisions
- SYS-NN (to be created) - System requirements
```

## Upstream/Downstream Artifacts

**Upstream Sources** (what drives EARS creation):
- **BRD** (Layer 1) - Business objectives
- **PRD** (Layer 2) - Product features and requirements

**Downstream Artifacts** (what EARS drives):
- **BDD** (Layer 4) - Test scenarios validating EARS statements
- **ADR** (Layer 5) - Architecture decisions implementing EARS requirements
- **SYS** (Layer 6) - System requirements derived from EARS

**Same-Type Document Relationships** (conditional):
- `@related-ears: EARS-NN` - EARS sharing domain context (references EARS document)
- `@depends-ears: EARS-NN` - EARS that must be implemented first

## Creation Process

### Step 1: Read Upstream Artifacts

Read and understand BRD and PRD that drive these formal requirements.

### Step 2: Reserve ID Number

Check `ai_dev_flow/EARS/` for next available ID number (e.g., EARS-01, EARS-02).

### Step 3: Create EARS File

**Location**: `docs/EARS/EARS-NN_{slug}.md` (template available at `ai_dev_flow/EARS/`)

**Example**: `docs/EARS/EARS-01_risk_limits.md`

### Step 4: Fill Document Control Section

Complete all required metadata fields and initialize Document Revision History table.

### Step 5: Categorize Requirements

Group requirements into 4 categories:
1. Event-Driven (triggered by events)
2. State-Driven (triggered by system state)
3. Unwanted Behavior (preventive)
4. Ubiquitous (always active)

### Step 6: Write WHEN-THE-SHALL-WITHIN Statements

For each requirement:
- Use formal EARS syntax
- Specify quantifiable constraints (time, accuracy, resource)
- Use SHALL/SHOULD/MAY keywords correctly
- Reference upstream PRD features

**Format**:
```markdown
## Event-Driven Requirements

### EARS.01.24.01: Trade Order Validation
```
WHEN trade order received,
THE order management system SHALL validate order parameters (symbol, quantity, price, account)
WITHIN 50 milliseconds.
```
**Traceability**: @brd: BRD.01.01.05 | @prd: PRD.01.07.03
```

### Step 7: Add Cumulative Tags

Include @brd and @prd tags (Layers 1-2) in Traceability section.

### Step 8: Create/Update Traceability Matrix

**MANDATORY**: Create or update `ai_dev_flow/EARS/EARS-000_TRACEABILITY_MATRIX.md`
- Use template: `ai_dev_flow/EARS/EARS-000_TRACEABILITY_MATRIX-TEMPLATE.md`
- Add EARS entry with upstream BRD/PRD and downstream artifacts
- Update within same commit as EARS creation

### Step 9: Validate EARS

Run validation scripts:
```bash
# EARS validation (under development - use template for manual validation)
# ./ai_dev_flow/scripts/validate_ears_template.sh docs/EARS/EARS-01_*.md

# Link integrity
./ai_dev_flow/scripts/validate_links.py --path ai_dev_flow/EARS/

# Cumulative tagging validation
python ai_dev_flow/scripts/validate_tags_against_docs.py --artifact EARS-01 --expected-layers brd,prd --strict
```

### Step 10: Commit Changes

Commit EARS file and traceability matrix together.

## Validation

### Automated Validation

**Quality Gates Validation**:
```bash
./scripts/validate_quality_gates.sh ai_dev_flow/EARS/EARS-01_risk.md
```

**Tag Validation**:
```bash
# Validate cumulative tags (must have @brd, @prd)
python ai_dev_flow/scripts/validate_tags_against_docs.py \
  --artifact EARS-01 \
  --expected-layers brd,prd \
  --strict
```

### Manual Checklist

- [ ] Document Control section at top (before all numbered sections)
- [ ] All required metadata fields completed
- [ ] Document Revision History table initialized
- [ ] All statements use WHEN-THE-SHALL-WITHIN format
- [ ] Requirements categorized (Event, State, Unwanted, Ubiquitous)
- [ ] SHALL/SHOULD/MAY keywords used correctly
- [ ] Quantifiable constraints specified (time, accuracy, resource)
- [ ] No ambiguous terms ("fast", "efficient", "user-friendly")
- [ ] Cumulative tags: @brd, @prd included
- [ ] Each requirement references upstream PRD feature
- [ ] Traceability matrix created/updated
- [ ] No broken links
- [ ] File size <50,000 tokens (standard) or <100,000 tokens (maximum)

### Diagram Standards
All diagrams MUST use Mermaid syntax. Text-based diagrams (ASCII art, box drawings) are prohibited.
See: `ai_dev_flow/DIAGRAM_STANDARDS.md` and `mermaid-gen` skill.

## Common Pitfalls

1. **Missing WITHIN clause**: Every EARS statement needs a constraint
2. **Ambiguous language**: Use quantifiable metrics, not subjective terms
3. **Wrong keyword**: SHALL for mandatory, SHOULD for recommended, MAY for optional
4. **Missing cumulative tags**: Layer 3 must include Layers 1-2 tags (@brd, @prd)
5. **No categorization**: Requirements must be grouped into 4 EARS types

## Post-Creation Validation (MANDATORY - NO CONFIRMATION)

**CRITICAL**: Execute this validation loop IMMEDIATELY after document creation. Do NOT proceed to next document until validation passes.

### Automatic Validation Loop

```
LOOP:
  1. Run: Validation script (when available) --document {doc_path} --auto-fix
  2. IF errors fixed: GOTO LOOP (re-validate)
  3. IF warnings fixed: GOTO LOOP (re-validate)
  4. IF unfixable issues: Log for manual review, continue
  5. IF clean: Mark VALIDATED, proceed
```

### Validation Command

```bash
# Per-document validation (Phase 1) - scripts under development
# python scripts/validate_cross_document.py --document docs/EARS/EARS-NN_slug.md --auto-fix

# Layer validation (Phase 2) - run when all EARS documents complete
# python scripts/validate_cross_document.py --layer EARS --auto-fix

# Currently available validations:
./scripts/validate_quality_gates.sh docs/EARS/EARS-NN_slug.md
python ai_dev_flow/scripts/validate_tags_against_docs.py --artifact EARS-NN --expected-layers brd,prd --strict
```

### Layer-Specific Upstream Requirements

| This Layer | Required Upstream Tags | Count |
|------------|------------------------|-------|
| EARS (Layer 3) | @brd, @prd | 2 tags |

### Auto-Fix Actions (No Confirmation Required)

| Issue | Fix Action |
|-------|------------|
| Missing @brd/@prd tag | Add with upstream document reference |
| Invalid tag format | Correct to TYPE.NN.TT.SS (4-segment) or TYPE-NN format |
| Broken link | Recalculate path from current location |
| Missing traceability section | Insert from template |

### Validation Codes Reference

| Code | Description | Severity |
|------|-------------|----------|
| XDOC-001 | Referenced requirement ID not found | ERROR |
| XDOC-002 | Missing cumulative tag | ERROR |
| XDOC-003 | Upstream document not found | ERROR |
| XDOC-006 | Tag format invalid | ERROR |
| XDOC-007 | Gap in cumulative tag chain | ERROR |
| XDOC-009 | Missing traceability section | ERROR |

### Quality Gate

**Blocking**: YES - Cannot proceed to next document until Phase 1 validation passes with 0 errors.

---

## Next Skill

After creating EARS, use:

**`doc-bdd`** - Create BDD test scenarios (Layer 4)

The BDD will:
- Reference this EARS as upstream source
- Include `@brd`, `@prd`, `@ears` tags (cumulative)
- Use Gherkin Given-When-Then format
- Validate EARS formal requirements with executable tests

## Reference Documents

For supplementary documentation related to EARS artifacts:
- **Format**: `EARS-REF-NNN_{slug}.md`
- **Skill**: Use `doc-ref` skill
- **Validation**: Minimal (non-blocking)
- **Examples**: Requirements syntax guides, EARS pattern catalogs

## Related Resources

- **Template**: `ai_dev_flow/EARS/EARS-TEMPLATE.md` (Template Version 3.0, primary authority)
- **Schema**: `ai_dev_flow/EARS/EARS_SCHEMA.yaml` (machine-readable validation)
- **Main Guide**: `ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`
- **EARS Creation Rules**: `ai_dev_flow/EARS/EARS_CREATION_RULES.md`
- **EARS Validation Rules**: `ai_dev_flow/EARS/EARS_VALIDATION_RULES.md`
- **EARS README**: `ai_dev_flow/EARS/README.md`
- **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`

**Section Templates** (for documents >25K tokens):
- Index template: `ai_dev_flow/EARS/EARS-SECTION-0-TEMPLATE.md`
- Content template: `ai_dev_flow/EARS/EARS-SECTION-TEMPLATE.md`
- Reference: `ai_dev_flow/ID_NAMING_STANDARDS.md` (Section-Based File Splitting)

## Quick Reference

**EARS Purpose**: Formalize requirements with WHEN-THE-SHALL-WITHIN syntax

**Layer**: 3

**Tags Required**: @brd, @prd (2 tags)

**Syntax**: WHEN [trigger] THE [system] SHALL [response] WITHIN [constraint]

**BDD-Ready Score**: ≥90% required for "Approved" status

**Requirement IDs**: `EARS.NN.24.SS` format (unified 4-segment format)

**4 Types**:
1. Event-Driven (WHEN event)
2. State-Driven (WHEN state)
3. Unwanted Behavior (IF unwanted, THEN)
4. Ubiquitous (THE SHALL - always active)

**Next**: doc-bdd
