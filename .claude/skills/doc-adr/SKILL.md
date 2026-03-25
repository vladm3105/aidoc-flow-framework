---
name: doc-adr
description: Create Architecture Decision Records (ADR) - Layer 5 artifact documenting architectural decisions with Context-Decision-Consequences format
metadata:
  tags:
    - sdd-workflow
    - layer-5-artifact
    - shared-architecture
  custom_fields:
    layer: 5
    artifact_type: ADR
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: core-workflow
    upstream_artifacts: [BRD, PRD, EARS, BDD]
    downstream_artifacts: [SYS, REQ, Code]
    version: "1.3"
    last_updated: "2026-03-06"
  versioning_policy: "tracks ADR-MVP-TEMPLATE schema_version"
---

# doc-adr

## Purpose

Create **Architecture Decision Records (ADR)** - Layer 5 artifact in the SDD workflow that documents architectural decisions with rationale, alternatives, and consequences.

**Layer**: 5

**Upstream**: BRD (Layer 1), PRD (Layer 2), EARS (Layer 3), BDD (Layer 4)

**Downstream Artifacts**: SYS (Layer 6), REQ (Layer 7), Code (Execution Layer)

## Prerequisites

### Upstream Artifact Verification (CRITICAL)

**Before creating this document, you MUST:**

1. **List existing upstream artifacts**:
   ```bash
   ls docs/01_BRD/ docs/02_PRD/ docs/03_EARS/ docs/04_BDD/ docs/05_ADR/ docs/06_SYS/ docs/07_REQ/ 2>/dev/null
   ```

2. **Reference only existing documents** in traceability tags
3. **Use `null`** only when upstream artifact type genuinely doesn't exist
4. **NEVER use placeholders** like `BRD-XXX` or `TBD`
5. **Do NOT create missing upstream artifacts** - skip functionality instead


Before creating ADR, read:

1. **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`
2. **Technology Stack**: `docs/05_ADR/ADR-00_technology_stack.md` (approved technologies)
3. **Upstream BRD, PRD**: Read Architecture Decision Requirements sections
4. **Template**: `ai_dev_ssd_flow/05_ADR/ADR-MVP-TEMPLATE.md`
5. **Creation Rules**: `ai_dev_ssd_flow/05_ADR/ADR-MVP-TEMPLATE.md`
6. **Validation Rules**: `ai_dev_ssd_flow/05_ADR/ADR_MVP_SCHEMA.yaml`
7. **Quality Gate Validation**: `ai_dev_ssd_flow/05_ADR/ADR_MVP_QUALITY_GATE_VALIDATION.md`

## When to Use This Skill

Use `doc-adr` when:
- Have identified architectural topics in BRD/PRD Architecture Decision Requirements sections
- Need to document technology choices with rationale
- Evaluating alternatives for architectural patterns
- Making decisions with long-term impact
- You are at Layer 5 of the SDD workflow

## ADR Document Categories

| Category | Filename Pattern | Validation Level | Description |
|----------|------------------|------------------|-------------|
| **Standard ADR** | `ADR-NN_{decision_topic}.md` | Full (7 checks) | Architecture decision records |
| **ADR-REF** | `ADR-REF-NN_{slug}.md` | Reduced (4 checks) | Supplementary reference documents |

### Reserved ID Exemption (ADR-00_*)

**Scope**: Documents with reserved ID `000` are FULLY EXEMPT from validation.

**Pattern**: `ADR-00_*.md`

**Document Types**: Index, Traceability matrix, Glossaries, Registries, Checklists

**Validation Behavior**: Skip all checks when filename matches `ADR-00_*` pattern.

## ADR-Specific Guidance

### 1. ADR Structure (11 Sections Total)

**MVP Template**: See `ai_dev_ssd_flow/05_ADR/ADR-MVP-TEMPLATE.md` for complete structure.

| # | Section | Purpose |
|---|---------|---------|
| 1 | Document Control | Metadata with SYS-Ready Score |
| 2 | Context | Problem Statement, Technical Context |
| 3 | Decision | Chosen Solution, Key Components, Approach |
| 4 | Alternatives Considered | Options with pros/cons |
| 5 | Consequences | Positive/Negative Outcomes, Costs |
| 6 | Architecture Flow | Mermaid diagrams, Integration Points |
| 7 | Implementation Assessment | Phases, Rollback, Monitoring |
| 8 | Verification | Success Criteria, BDD Scenarios |
| 9 | Traceability | Upstream/Downstream, Tags, Cross-Links |
| 10 | Related Decisions | Dependencies, Supersessions |
| 11 | MVP Lifecycle | Iteration guidance |

### 2. ADR Lifecycle States

**Proposed**: Decision under consideration
- Still evaluating alternatives
- Seeking stakeholder feedback
- Not yet implemented

**Accepted**: Decision approved and active
- Chosen as the path forward
- Implementation can proceed
- Should be followed by all

**Deprecated**: Decision no longer recommended
- Better alternative found
- Context changed
- Not deleted (historical record)

**Superseded by ADR-XXX**: Replaced by newer decision
- Links to replacing ADR
- Explains why replaced
- Maintains audit trail

### 3. SYS-Ready Scoring System

**Purpose**: Measures ADR maturity and readiness for progression to System Requirements (SYS) phase.

**Format in Document Control**:
```markdown
| **SYS-Ready Score** | ✅ 95% (Target: ≥90%) |
```

**Status and SYS-Ready Score Mapping**:

| SYS-Ready Score | Required Status |
|-----------------|-----------------|
| ≥90% | Accepted |
| 70-89% | Proposed |
| <70% | Draft |

**Scoring Criteria**:
- **Decision Completeness (30%)**: Context/Decision/Consequences/Alternatives process
- **Architecture Clarity (35%)**: Mermaid diagrams (REQUIRED - no text-based diagrams), component responsibilities, cross-cutting concerns
- **Implementation Readiness (20%)**: Complexity assessment, dependencies, rollback strategies
- **Verification Approach (15%)**: Testing strategy, success metrics, operational readiness

**Quality Gate**: Score <90% blocks SYS artifact creation.

### 4. Element ID Format (MANDATORY)

**Pattern**: `ADR.{DOC_NUM}.{ELEM_TYPE}.{SEQ}` (4 segments, dot-separated)

| Element Type | Code | Example |
|--------------|------|---------|
| Decision | 10 | ADR.02.10.01 |
| Alternative | 12 | ADR.02.12.01 |
| Consequence | 13 | ADR.02.13.01 |

**REMOVED PATTERNS** - Do NOT use legacy formats:
- ❌ `DEC-XXX` → Use `ADR.NN.10.SS`
- ❌ `ALT-XXX` → Use `ADR.NN.12.SS`
- ❌ `CON-XXX` → Use `ADR.NN.13.SS`

**Reference**: [ID_NAMING_STANDARDS.md](../../ai_dev_ssd_flow/ID_NAMING_STANDARDS.md)

### 5. Threshold Management

**Dual Role**: ADR documents both reference and define thresholds.

**Reference** platform-wide thresholds from PRD threshold registry:
```yaml
performance:
  - "@threshold: PRD.NN.perf.api.p95_latency"
sla:
  - "@threshold: PRD.NN.sla.uptime.target"
```

**Define** architecture-specific thresholds unique to this decision:
```yaml
circuit_breaker:
  - "@threshold: ADR.NN.circuit.failure_threshold"
  - "@threshold: ADR.NN.circuit.recovery_timeout"
retry:
  - "@threshold: ADR.NN.retry.max_attempts"
caching:
  - "@threshold: ADR.NN.cache.ttl_seconds"
```

### 6. File Size Limits

- **Target**: 800 lines per file
- **Maximum**: 1200 lines per file (absolute)
- If document approaches/exceeds limits, split into section files

## Tag Format Convention (By Design)

| Notation | Format        | Artifacts                               | Purpose                                                             |
|----------|---------------|----------------------------------------|---------------------------------------------------------------------|
| Dash     | TYPE-NN      | ADR, SPEC, CTR            | Technical artifacts - references to files/documents                 |
| Dot      | TYPE.NN.TT.SS | BRD, PRD, EARS, BDD, SYS, REQ, IMPL, TASKS | Hierarchical artifacts - references to elements inside documents |

**Key Distinction**:
- `@adr: ADR-033` → Points to the document `ADR-033_risk_limit_enforcement.md`
- `@brd: BRD.17.01.30` → Points to element 01.30 inside document `BRD-017.md`

## Cumulative Tagging Requirements

**Layer 5 (ADR)**: Must include tags from Layers 1-4 (BRD, PRD, EARS, BDD)

**Tag Count**: 4 tags (@brd, @prd, @ears, @bdd)

**Format**:

```markdown
## Traceability

**Required Tags** (Cumulative Tagging Hierarchy - Layer 5):

@brd: BRD.01.01.30
@prd: PRD.01.07.02
@ears: EARS.01.25.01
@bdd: BDD.01.14.01
```

**Upstream Sources**:
- [BRD-01](../BRD/BRD-01_platform.md#BRD-01) - Architecture Decision Requirements
- [PRD-01](../PRD/PRD-01_integration.md#PRD-01) - Product requirements
- [EARS-01](../EARS/EARS-01_risk.md#EARS-01) - Formal requirements (EARS type code: 25)
- [BDD-01](../BDD/BDD-01_limits/) - Test scenarios (BDD scenario type code: 14)

## Upstream/Downstream Artifacts

**Upstream Sources**:
- **BRD** (Layer 1) - Architecture Decision Requirements section
- **PRD** (Layer 2) - Architecture Decision Requirements section
- **EARS** (Layer 3) - Formal requirements constraints
- **BDD** (Layer 4) - Test scenarios validating decision

**Downstream Artifacts**:
- **SYS** (Layer 6) - System requirements implementing decision
- **REQ** (Layer 7) - Atomic requirements following decision
- **Code** (Execution Layer) - Implementation per decision

**Upstream-Only Traceability Policy**:
> The ADR traceability matrix tracks ADRs and their **upstream sources** (BRD, PRD, EARS, BDD) only. Downstream documents (SYS, REQ, SPEC) track their own upstream references to ADRs—the ADR matrix does NOT maintain downstream links.

**Same-Type Document Relationships** (conditional):
- `@related-adr: ADR-NN` - ADRs sharing architectural context
- `@depends-adr: ADR-NN` - ADR that must be decided first

### Cross-Linking Tags (AI-Friendly)

**Purpose**: Establish lightweight, machine-readable hints for AI discoverability and dependency tracing across ADR documents without blocking validation.

**Tags Supported**:
- `@depends: ADR-NN` — Hard prerequisite; this ADR cannot proceed without the referenced ADR
- `@discoverability: ADR-NN (short rationale)` — Related document for AI search and ranking (informational)

**ID Format**: Document-level IDs follow `{DOC_TYPE}-NN` per `ID_NAMING_STANDARDS.md` (e.g., `ADR-01`, `ADR-02`).

**Placement**: Add tags to the Traceability section or inline with decision descriptions.

**Example**:
```markdown
@depends: ADR-01 (Technology Stack)
@discoverability: ADR-02 (Database Strategy - related architecture decision)
```

**Validator Behavior**: Cross-linking tags are recognized and reported as **info-level** findings (non-blocking). They enable AI/LLM tools to infer relationships and improve search ranking without affecting document approval.

**Optional for MVP**: Cross-linking tags are optional in MVP templates and are not required for ADR approval; they are purely informational.

## Creation Process

### Step 1: Identify Decision Topic

From BRD/PRD Architecture Decision Requirements sections, identify topic needing decision.

### Step 2: Read Technology Stack

Check `docs/05_ADR/ADR-00_technology_stack.md` for approved technologies.

### Step 3: Reserve ID Number

Check `docs/05_ADR/` for next available ID number (e.g., ADR-01, ADR-33).

**ID Numbering Convention**: Start with 2 digits and expand only as needed.
- ✅ Correct: ADR-01, ADR-99, ADR-102
- ❌ Incorrect: ADR-001, ADR-033 (extra leading zero not required)

**Special IDs**:
- **ADR-000**: Reserved for Technology Stack reference
- **ADR-01 onwards**: Regular decision records

### Step 4: Create ADR Folder and Files

**Folder structure** (DEFAULT - nested folder per document):
1. Create folder: `docs/05_ADR/ADR-NN_{slug}/` (folder slug MUST match index file slug)
2. Create index file: `docs/05_ADR/ADR-NN_{slug}/ADR-NN.0_{slug}_index.md`
3. Create section files: `docs/05_ADR/ADR-NN_{slug}/ADR-NN.S_{section_type}.md`

**Example (Section-Based Pattern - DEFAULT)**:
```
docs/05_ADR/ADR-033_database_selection/
├── ADR-033.0_database_selection_index.md
├── ADR-033.1_context.md
├── ADR-033.2_decision.md
└── ADR-033.3_consequences.md
```

**Monolithic Option** (for small documents ≤25KB): `docs/05_ADR/ADR-NN_{slug}/ADR-NN_{slug}.md` (still in nested folder)

### Step 5: Fill Document Control Section

Complete all required metadata fields and initialize Document Revision History table.

**Required Fields** (7 mandatory):
- Project Name, Document Version, Date, Document Owner, Prepared By, Status, SYS-Ready Score

### Step 6: Document Context (Section 4)

**Context Section**: Explain the problem and factors:
- What issue are we addressing?
- What constraints exist?
- What requirements drive this decision?
- Reference upstream BRD/PRD sections

**Section 4.1 Problem Statement** includes inherited content:
- Business Driver (from BRD §7.2)
- Business Constraints (from BRD §7.2)
- Technical Options Evaluated (from PRD §18)
- Evaluation Criteria (from PRD §18)

### Step 7: State Decision (Section 5)

**Decision Section**: Clear, concise statement:
- What are we choosing to do?
- How will it be implemented?
- Reference technology stack (ADR-000) if applicable

### Step 8: Analyze Consequences (Section 7)

**Consequences Section**:
- **Positive**: Benefits and advantages
- **Negative**: Drawbacks and limitations
- **Risks**: Potential issues and mitigations

### Step 9: Document Alternatives (Section 12)

**Alternatives Considered**: For each alternative:
- Name and description
- Pros and cons
- Why rejected
- Fit Score (Poor/Good/Better)

### Step 10: Define Verification (Section 11)

**Verification Section**: How to validate decision:
- BDD scenarios that test it
- Success metrics
- Performance benchmarks

### Step 11: Add Relations (Section 14)

**Related Decisions Section**:
- Supersedes: Which ADR this replaces
- Related to: Connected ADRs
- Influences: Which SYS/REQ depend on this

### Step 12: Add Cumulative Tags (Section 16.6)

Include @brd, @prd, @ears, @bdd tags (Layers 1-4).

### Step 13: Create/Update Traceability Matrix

**MANDATORY**: Update `docs/05_ADR/ADR-00_TRACEABILITY_MATRIX.md`
- Add ADR entry with **upstream sources only** (BRD, PRD, EARS, BDD)
- Do NOT add downstream links (SYS, REQ track their own references to ADRs)

### Step 14: Commit Changes

Commit ADR and traceability matrix.

## Validation

### Validation Checks (8 Total)

| Check | Type | Description |
|-------|------|-------------|
| CHECK 1 | Error | Required Document Control Fields (7 fields) |
| CHECK 2 | Error | ADR Structure Completeness (required sections) |
| CHECK 3 | Error | SYS-Ready Score Validation (format, threshold) |
| CHECK 4 | Error | Upstream Traceability Tags (@brd, @prd, @ears, @bdd) |
| CHECK 5 | Warning | Decision Quality Assessment |
| CHECK 6 | Warning | Architecture Documentation (Mermaid diagrams) |
| CHECK 7 | Warning | Implementation Readiness |
| CHECK 8 | Error | Element ID Format Compliance (unified 4-segment) |

### Validation Tiers

| Tier | Type | Exit Code | Action |
|------|------|-----------|--------|
| Tier 1 | Error | 1 | Must fix before commit |
| Tier 2 | Warning | 0 | Recommended to fix |
| Tier 3 | Info | 0 | No action required |

### Pre-Commit Hooks

ADR validation is **automatically enforced** via pre-commit hooks:

```yaml
- id: adr-core-validator
  name: Validate ADR core checks (validator, framework library)
  entry: bash ai_dev_ssd_flow/05_ADR/scripts/adr_core_validator_hook.sh
  stages: [pre-commit]

- id: adr-quality-gate
  name: Validate ADR quality gates
  entry: bash ai_dev_ssd_flow/05_ADR/scripts/adr_quality_gate_hook.sh
  stages: [pre-commit]

- id: adr-sys-ready-score
  name: Validate ADR SYS-Ready score (≥90%)
  entry: bash ai_dev_ssd_flow/05_ADR/scripts/adr_sys_ready_score_hook.sh
  stages: [pre-commit]
```

**Manual execution** (for testing without committing):
```bash
pre-commit run adr-core-validator --all-files
pre-commit run adr-quality-gate --all-files
pre-commit run adr-sys-ready-score --all-files
```

**Quality Gates Enforced**:
- ✅ ADR structure compliance (11 sections MVP)
- ✅ SYS-Ready score ≥90% for Accepted status
- ✅ Metadata and tags (adr, layer-5-artifact)
- ✅ Upstream traceability (@brd, @prd, @ears, @bdd)
- ✅ Element ID format (ADR.NN.TT.SS)
- ✅ No placeholder text in approved documents
- ✅ Architecture diagrams (Mermaid required)
- ✅ Decision quality and alternatives analysis

### Automated Validation

```bash
# Per-document validation (Phase 1)
python ai_dev_ssd_flow/scripts/validate_cross_document.py --document docs/05_ADR/ADR-NN_slug.md --auto-fix

# Layer validation (Phase 2) - run when all ADR documents complete
python ai_dev_ssd_flow/scripts/validate_cross_document.py --layer ADR --auto-fix

# Cumulative tagging validation
python ai_dev_ssd_flow/scripts/validate_tags_against_docs.py --artifact ADR-NN --expected-layers brd,prd,ears,bdd --strict
```

### Manual Checklist

- [ ] Document Control section at top with 7 required fields
- [ ] Status field completed (Proposed/Accepted/Deprecated/Superseded)
- [ ] SYS-Ready Score with ✅ emoji and percentage
- [ ] Context explains problem and constraints
- [ ] Decision clearly stated
- [ ] Consequences analyzed (positive, negative, risks)
- [ ] Alternatives considered and documented with rejection rationale
- [ ] Verification approach defined
- [ ] Relations to other ADRs documented
- [ ] Technology Stack (ADR-000) referenced if applicable
- [ ] Cumulative tags: @brd, @prd, @ears, @bdd included
- [ ] Element IDs use unified format (ADR.NN.TT.SS)
- [ ] No legacy patterns (DEC-XXX, ALT-XXX, CON-XXX)
- [ ] Traceability matrix updated

## Post-Creation Validation (MANDATORY - NO CONFIRMATION)

**CRITICAL**: Execute this validation loop IMMEDIATELY after document creation. Do NOT proceed to next document until validation passes.

### Automatic Validation Loop

```
LOOP:
  1. Run: python ai_dev_ssd_flow/scripts/validate_cross_document.py --document {doc_path} --auto-fix
  2. IF errors fixed: GOTO LOOP (re-validate)
  3. IF warnings fixed: GOTO LOOP (re-validate)
  4. IF unfixable issues: Log for manual review, continue
  5. IF clean: Mark VALIDATED, proceed
```

### Layer-Specific Upstream Requirements

| This Layer | Required Upstream Tags | Count |
|------------|------------------------|-------|
| ADR (Layer 5) | @brd, @prd, @ears, @bdd | 4 tags |

### Auto-Fix Actions (No Confirmation Required)

| Issue | Fix Action |
|-------|------------|
| Missing @brd/@prd/@ears/@bdd tag | Add with upstream document reference |
| Invalid tag format | Correct to TYPE.NN.TT.SS (4-segment) or TYPE-NN format |
| Legacy element ID (DEC-XXX, ALT-XXX, CON-XXX) | Convert to ADR.NN.TT.SS format |
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

**Blocking**: YES - Cannot proceed to SYS creation until Phase 1 validation passes with 0 errors.

## Common Pitfalls

1. **No alternatives**: Must document why other options rejected
2. **Missing technology stack check**: Always check ADR-000 first
3. **Vague consequences**: Be specific about impacts
4. **No verification**: Must define how to validate decision
5. **Missing cumulative tags**: Layer 5 must include Layers 1-4 tags
6. **Legacy element IDs**: Use ADR.NN.TT.SS not DEC-XXX/ALT-XXX/CON-XXX
7. **Wrong SYS-Ready Score format**: Must include ✅ emoji and percentage

---

## ADR-REF Reference Documents

For supplementary documentation related to ADR artifacts:
- **Format**: `ADR-REF-NNN_{slug}.md`
- **Skill**: Use `doc-ref` skill
- **Validation**: Reduced (4 checks only)
- **Examples**: Technology stack summaries, architecture overviews

### ADR-REF Reduced Validation

**Applicable Checks** (4 total):
- CHECK 1 (partial): Document Control Fields (required)
- Document Revision History (required)
- Status/Context sections only (required)
- H1 ID match with filename (required)

**Exempted** (NO SCORES):
- SYS-Ready Score: NOT APPLICABLE
- Cumulative tags: NOT REQUIRED
- CHECK 5-7: Decision quality, architecture, implementation (exempt)
- All quality gates and downstream readiness metrics: EXEMPT

**Purpose**: ADR-REF documents are **reference targets** that other documents link to. They provide supporting information, context, or external references but do not define formal architecture decisions.

---

## Next Skill

After creating ADR, use:

**`doc-sys`** - Create System Requirements (Layer 6)

The SYS will:
- Implement ADR architectural decisions
- Include `@brd`, `@prd`, `@ears`, `@bdd`, `@adr` tags (cumulative)
- Define functional requirements and quality attributes
- Translate ADR decisions into technical requirements

## Related Resources

- **Template**: `ai_dev_ssd_flow/05_ADR/ADR-MVP-TEMPLATE.md` (primary authority)
- **Schema**: `ai_dev_ssd_flow/05_ADR/ADR_MVP_SCHEMA.yaml` (machine-readable validation)
- **Technology Stack**: `docs/05_ADR/ADR-00_technology_stack.md`
- **ADR Creation Rules**: `ai_dev_ssd_flow/05_ADR/ADR-MVP-TEMPLATE.md`
- **ADR Validation Rules**: `ai_dev_ssd_flow/05_ADR/ADR_MVP_SCHEMA.yaml`
- **ADR README**: `ai_dev_ssd_flow/05_ADR/README.md`
- **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`

**Section Templates** (DEFAULT for all ADR documents):
- **Structure**: `docs/05_ADR/ADR-NN/ADR-NN.S_slug.md` (nested folder per document)
- Reference: `ai_dev_ssd_flow/ID_NAMING_STANDARDS.md` (Section-Based File Splitting)
- **Note**: Monolithic format allowed for small documents (≤25KB), but MUST still be in nested folder

## Quick Reference

**ADR Purpose**: Document architectural decisions with rationale

**Layer**: 5

**Tags Required**: @brd, @prd, @ears, @bdd (4 tags)

**Format**: 11-section MVP structure

**SYS-Ready Score**: ≥90% required for "Accepted" status

**Element ID Format**: ADR.NN.TT.SS (Decision=10, Alternative=12, Consequence=13)

**File Size**: 800 lines target, 1200 max

**Lifecycle States**: Proposed → Accepted → Deprecated/Superseded

**Critical**: Always check ADR-000 Technology Stack first

**Next**: doc-sys

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.3 | 2026-03-06 | Added cross-linking tags documentation, quality gate validation reference, and pre-commit hooks section | System |
| 1.2 | 2026-02-27 | Migrated frontmatter to `metadata`; normalized ADR references to `ai_dev_ssd_flow/05_ADR` MVP artifacts and existing validation scripts | System |
| 1.1 | 2026-02-26 | Updated to 11-section MVP structure (aligned with ADR-MVP-TEMPLATE.md v1.1) | System |
| 1.0 | 2026-02-08 | Initial skill definition with YAML frontmatter standardization | System |
