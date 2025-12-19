# Shared Content for Doc-Flow Skills

This document contains standards and guidelines shared across all document artifact skills (doc-brd, doc-prd, doc-ears, doc-bdd, doc-adr, doc-sys, doc-req, doc-impl, doc-ctr, doc-spec, doc-tasks, doc-iplan).

**Import Reference**: All artifact-specific skills MUST reference this document for ID standards, traceability format, cumulative tagging hierarchy, and quality gates.

---

## 1. Document ID Naming Standards

**Authoritative Reference**: `ai_dev_flow/ID_NAMING_STANDARDS.md`

### Universal Numbering Pattern (All Document Types)

- **Primary Number (NNN)**: 3-4 digit sequential number for atomic logical document (001-999, then 1000-9999 when needed)
- **Sub-Document Number (YY)**: 2-3 digit sequential number within atomic document [OPTIONAL] (01-99, then 100-999 when needed)
- **Format**: `TYPE-NNN` or `TYPE-NNN-YY` (e.g., `REQ-001`, `BRD-009-02`, `ADR-1000`)
- **Zero-Padding**: Always pad to minimum digit count (001, 01) until exceeding range
- **Uniqueness Rule**: Each NNN number is unique and can be used EITHER as:
  - Atomic document: `TYPE-NNN_{slug}.md` (e.g., `BRD-001_foundation.md`)
  - Multi-document group: `TYPE-NNN-01_{slug}.md`, `TYPE-NNN-02_{slug}.md`, etc.
  - ❌ INVALID: Cannot have both `BRD-009_{slug}.md` AND `BRD-009-01_{slug}.md` (NNN=009 collision)
  - ✅ VALID: Can have `BRD-009-01_{slug}.md` AND `BRD-009-02_{slug}.md` (same NNN, different YY)

### File Naming Patterns

- BRD: `BRD/BRD-NNN_{slug}.md` or `BRD-NNN-YY_{slug}.md` (Business Requirements Documents) - **Location: docs/BRD/**
- PRD: `PRD/PRD-NNN_{slug}.md` or `PRD-NNN-YY_{slug}.md` (Product Requirements) - **Location: docs/PRD/**
- EARS: `EARS/EARS-NNN_{slug}.md` or `EARS-NNN-YY_{slug}.md` (Formal Requirements) - **Location: docs/EARS/**
- BDD: `BDD/BDD-NNN_{slug}.feature` or `BDD-NNN-YY_{slug}.feature` (Behavior-Driven Tests) - **Location: docs/BDD/**
- ADR: `ADR/ADR-NNN_{slug}.md` or `ADR-NNN-YY_{slug}.md` (Architecture Decisions) - **Location: docs/ADR/**
- SYS: `SYS/SYS-NNN_{slug}.md` or `SYS-NNN-YY_{slug}.md` (System Requirements) - **Location: docs/SYS/**
- REQ: `REQ/REQ-{domain}-{subdomain}-NNN_{slug}.md` or `REQ-NNN-YY_{slug}.md` (Atomic Requirements - flat structure, domain in filename) - **Location: docs/REQ/**
- IMPL: `IMPL/IMPL-NNN_{slug}.md` or `IMPL-NNN-YY_{slug}.md` (Implementation Plans) - **Location: docs/IMPL/**
- CTR: `CTR/CTR-NNN_{slug}.md` + `CTR-NNN_{slug}.yaml` or `CTR-NNN-YY_{slug}.{md,yaml}` (API Contracts - dual-file format) - **Location: docs/CTR/**
- SPEC: `SPEC/SPEC-NNN_{slug}.yaml` or `SPEC-NNN-YY_{slug}.yaml` (Technical Specifications) - **Location: docs/SPEC/**
- TASKS: `TASKS/TASKS-NNN_{slug}.md` or `TASKS-NNN-YY_{slug}.md` (Code Generation Plans) - **Location: docs/TASKS/**
- IPLAN: `IPLAN/IPLAN-NNN_{slug}_YYYYMMDD_HHMMSS.md` (Implementation Plans - session-based) - **Location: docs/IPLAN/**
- ICON: `ICON/ICON-NNN_{slug}.md` (Implementation Contracts) - **Location: docs/ICON/**

### ID Format Rules

- H1 headers contain full document IDs: `# REQ-003: Position Limit Enforcement` or `# BRD-009-01: Prerequisites`
- SPEC YAML uses `id:` field with lowercase_snake_case: `position_limit_service`
- Categories encoded in folder paths, not ID prefixes
- Sub-numbering (-YY) used ONLY when single logical document requires multiple related files with sequential reading order
- Each NNN number must be unique (no collisions between atomic and multi-doc patterns)

### Document ID Independence

**⚠️ CRITICAL - ID INDEPENDENCE**: Document IDs are independent across artifact types. BRD-009 does NOT need to correspond to PRD-009.

**Why IDs Don't Match**:
- IDs are assigned sequentially within each artifact type based on creation order
- Documents are created as needed, not in lockstep across all types
- Example: BRD-009 covers "Broker Integration" but PRD-009 might cover "Cash-Secured Put Workflow" (completely unrelated)
- The corresponding PRD for broker integration might be PRD-016 or any other number

**Always Use Index Files for Discovery**: To find documents by topic/content:
- Index files use ID `000` in their identifier (e.g., PRD-000, REQ-000, ADR-000)
- Index filenames include "index" in the name
- Index files contain descriptions and summaries of all documents of that artifact type
- Organized by domain, category, or functional area

**Best Practice for AI Assistants**:
1. When searching for related documents, **find and read the index file first** (ID: 000, name contains "index")
2. Search index descriptions for keywords related to your topic
3. Do NOT assume document IDs match across artifact types
4. Use traceability tags within documents to find explicitly linked artifacts
5. Verify document content matches your topic before assuming relationship

---

## 2. Traceability Section Format

**Authoritative Reference**: `ai_dev_flow/TRACEABILITY.md`

### Traceability Rules (REQUIRED vs OPTIONAL)

| Document Type | Upstream Traceability | Downstream Traceability |
|---------------|----------------------|------------------------|
| **BRD** | OPTIONAL (to other BRDs) | OPTIONAL |
| **All Other Documents** | REQUIRED | OPTIONAL |

**Key Rules**:
- **Upstream REQUIRED** (except BRD): Document MUST reference its upstream sources
- **Downstream OPTIONAL**: Only link to documents that already exist
- **No-TBD Rule**: NEVER use placeholder IDs (TBD, XXX, NNN) - leave empty or omit section

### Required Traceability Section

Every document must include a `## Traceability` section (typically Section 7):

**Standard fields:**
- **Upstream Sources (REQUIRED except BRD)**: Prior artifacts this document derives from
- **Downstream Artifacts (OPTIONAL)**: Artifacts that depend on this document - only add if they already exist
- **Anchors/IDs**: Primary anchor(s) in this file (e.g., `# REQ-003`)
- **Code Path(s)**: Where related implementation resides

**Traceability Template:**
```markdown
## Traceability
- Upstream Sources: [link], [link]
- Downstream Artifacts: [link], [link]
- Anchors/IDs: `# <PRIMARY-ID-IF-ANY>`
- Code Path(s): `path/to/file.py`
```

### Cross-Reference Link Format (Mandatory)

- Use markdown links with standardized paths: `[ADR-033](../ADR/ADR-033_risk_architecture.md#ADR-033)`
- Include anchors: `#ADR-033`, `#BDD-003`, `#CTR-001`
- Use relative paths from current file location
- Examples:
  - From docs/BRD/: `[ADR-033](../ADR/ADR-033_risk_architecture.md#ADR-033)`
  - From docs/SPEC/: `[CTR-001](../CTR/CTR-001_api_contract.md#CTR-001)`

---

## 3. Cumulative Tagging Hierarchy

**Authoritative Reference**: `ai_dev_flow/TRACEABILITY.md#cumulative-tagging-hierarchy`

### Principle

Each artifact layer must include traceability tags from ALL upstream artifact layers, creating a complete audit trail from business requirements through production code.

### Cumulative Tagging Table (16 Layers)

| Layer | Artifact Type | Required Tags | Tag Count | Format | Notes |
|-------|---------------|---------------|-----------|--------|-------|
| 0 | **Strategy** | None | 0 | External | Business owner documents, no formal artifact |
| 1 | **BRD** | None | 0 | Markdown | Top level, no upstream dependencies |
| 2 | **PRD** | `@brd` | 1 | Markdown | References parent BRD |
| 3 | **EARS** | `@brd`, `@prd` | 2 | Markdown | Cumulative: BRD + PRD |
| 4 | **BDD** | `@brd`, `@prd`, `@ears` | 3+ | Gherkin Tags | Cumulative: BRD through EARS |
| 5 | **ADR** | `@brd` through `@bdd` | 4 | Markdown | Cumulative: BRD through BDD |
| 6 | **SYS** | `@brd` through `@adr` | 5 | Markdown | Cumulative: BRD through ADR |
| 7 | **REQ** | `@brd` through `@sys` | 6 | Markdown | Cumulative: BRD through SYS |
| 8 | **IMPL** | `@brd` through `@req` | 7 | Markdown | Optional layer |
| 9 | **CTR** | `@brd` through `@impl` | 8 | Markdown + YAML | Optional layer |
| 10 | **SPEC** | `@brd` through `@req` + optional | 7-9 | YAML (`cumulative_tags`) | YAML cumulative_tags section |
| 11 | **TASKS** | `@brd` through `@spec` | 8-10 | Markdown | Cumulative: BRD through SPEC |
| 12 | **IPLAN** | `@brd` through `@tasks` | 9-11 | Markdown | Implementation session plans (Format: IPLAN-NNN_{slug}_YYYYMMDD_HHMMSS.md, Tag: @iplan: IPLAN-001 - ID only) |
| 13 | **Code** | `@brd` through `@tasks` | 9-11 | Docstrings | Python/source code |
| 14 | **Tests** | `@brd` through `@code` | 10-12 | Docstrings | Test suites |
| 15 | **Validation** | All upstream | 10-15 | Various | Validation results |

### Optional Layers Impact on Tag Counts

| Development Path | IMPL? | CTR? | SPEC Tags | TASKS Tags | IPLAN Tags |
|------------------|-------|------|-----------|------------|------------|
| Direct path | No | No | 7 | 8 | 9 |
| With IMPL only | Yes | No | 8 | 9 | 10 |
| With CTR only | No | Yes | 8 | 9 | 10 |
| With IMPL + CTR | Yes | Yes | 9 | 10 | 11 |

**Note**: IMPL (Layer 8) and CTR (Layer 9) are optional layers. Include their tags only if you created those artifacts.

### Tag Count Clarification

**CRITICAL RULE**: Tag Count = Number of UPSTREAM layers (artifacts do NOT tag themselves)

**Calculation Formula**: For Layer N with no optional layers, Tag Count = N - 1

**Examples**:
- **Layer 2 (PRD)**: 1 upstream tag (@brd)
- **Layer 7 (REQ)**: 6 upstream tags (@brd, @prd, @ears, @bdd, @adr, @sys)
- **Layer 12 (IPLAN)**: 9-11 upstream tags (varies with optional IMPL, CTR)

**Validation Method**:
1. Count `@artifact:` lines in Traceability section
2. Should equal Layer Number minus 1 for mandatory layers
3. Add +1 for each optional layer (IMPL, CTR) if included

### Tag Format

```markdown
@brd: BRD.09.01.15, BRD.09.01.901
@prd: PRD.16.07.03
@ears: EARS.12.24.02, EARS.12.24.01
@bdd: BDD.15.13.01
@adr: ADR-033
@sys: SYS.12.25.01, SYS.12.25.02
@req: REQ.45.26.01
@impl: IMPL.03.28.02  # Optional - include only if exists
@ctr: CTR-005  # Optional - include only if exists
@spec: SPEC-018
@tasks: TASKS.15.29.01
@iplan: IPLAN-001  # Use ID only (IPLAN-NNN), NOT full filename with timestamp
@icon: TASKS-001:ContractName  # Implementation Contract (optional, Layer 11)
```

### Feature-Level Traceability Tags

Internal feature IDs within documents use simple sequential numbering:

| Context | Format | Example | Cross-Reference |
|---------|--------|---------|-----------------|
| PRD Features | `NNN` | `001`, `015`, `042` | `@prd: PRD.22.07.15` |
| BRD Objectives | `NNN` | `030`, `006` | `@brd: BRD.01.01.30` |
| EARS Statements | `NNN` | `003`, `007` | `@ears: EARS.06.24.03` |
| SYS Requirements | `NNN` | `001`, `015` | `@sys: SYS.08.25.01` |

**Global Uniqueness**: Document ID + Feature ID creates globally unique references.

### Format Rules

- Format: Use unified 4-segment `TYPE.NN.TT.SS` format (e.g., `BRD.01.01.30`)
- Multiple refs: Comma-separated list within same tag line
- Optional layers: Include `@impl` and `@ctr` tags only if those artifacts exist in chain
- SPEC format: Use YAML `cumulative_tags:` mapping instead of markdown comments
- BDD format: Use Gherkin `@` tags at feature/scenario level

### Validation Rules

1. **No gaps**: Each layer must include ALL upstream tags from previous layers
2. **Format compliance**: Tags must follow `@artifact-type: TYPE.NN.TT.SS` pattern (4-segment format)
3. **Valid references**: All tagged document IDs must exist and be reachable
4. **Optional layers**: `@impl` and `@ctr` included only if they exist in chain
5. **SPEC exception**: SPEC uses YAML format, not markdown tags

### SPEC YAML Format Example (7-9 tags)

```yaml
# SPEC-018: Order Placement Service Specification

spec_id: SPEC-018
title: "Order Placement Service Technical Specification"
version: "1.0.0"

# Cumulative Tagging Hierarchy (Layer 10)
cumulative_tags:
  brd: "BRD.09.01.15, BRD.09.01.906"
  prd: "PRD.16.07.03"
  ears: "EARS.12.24.02, EARS.12.24.01"
  bdd: "BDD.15.13.01"
  adr: "ADR-033"
  sys: "SYS.12.25.901, SYS.12.25.921"
  req: "REQ.45.26.01, REQ.45.26.02"
  impl: "IMPL.03.28.02"  # Optional
  ctr: "CTR-005"  # Optional
```

### Benefits of Cumulative Tagging

- **Complete Audit Trail**: Every artifact traces back to original business requirements
- **Impact Analysis**: Instantly identify all downstream artifacts affected by upstream changes
- **Regulatory Compliance**: SEC, FINRA, FDA, ISO audit requirements satisfied automatically
- **Automated Validation**: Scripts enforce tagging compliance in CI/CD pipeline
- **Change Management**: Know exactly what breaks when requirements change
- **Coverage Metrics**: Measure traceability completeness across entire codebase

---

## 4. Quality Gates & Validation

### Quality Gates Automation

**Authoritative Reference**: `ai_dev_flow/TRACEABILITY_VALIDATION.md`

Each artifact layer requires ≥90% ready score before progressing to next layer.

### Creation and Validation Rules References

Before creating ANY artifact, consult:

1. **Creation Rules**: `ai_dev_flow/{TYPE}/{TYPE}_CREATION_RULES.md` - Authoritative creation guidance
2. **Validation Rules**: `ai_dev_flow/{TYPE}/{TYPE}_VALIDATION_RULES.md` - Quality validation requirements
3. **Template**: `ai_dev_flow/{TYPE}/{TYPE}-TEMPLATE.{ext}` - Starting structure

**Available for artifact types**: BRD, PRD, EARS, BDD, ADR, SYS, REQ, SPEC, IMPL, CTR, TASKS, IPLAN, ICON

**Note**: All artifact types have creation/validation rules files in their respective `ai_dev_flow/{TYPE}/` directories. Consult `{TYPE}_CREATION_RULES.md` and `{TYPE}_VALIDATION_RULES.md` for authoritative guidance.

### Validation Script Status

**Available Scripts**:
- BRD: `./ai_dev_flow/scripts/validate_brd_template.sh` ✓
- REQ: `./ai_dev_flow/scripts/validate_req_template.sh` ✓
- CTR: `./ai_dev_flow/scripts/validate_ctr.sh` ✓
- IMPL: `./ai_dev_flow/scripts/validate_impl.sh` ✓
- TASKS: `./ai_dev_flow/scripts/validate_tasks.sh` ✓
- IPLAN: `./ai_dev_flow/scripts/validate_iplan.sh` ✓
- ICON: `./ai_dev_flow/scripts/validate_icon.sh` ✓

**Under Development**:
- PRD: `./ai_dev_flow/scripts/validate_prd.sh` (planned)
- EARS: `./ai_dev_flow/scripts/validate_ears.sh` (planned)
- BDD: `./ai_dev_flow/scripts/validate_bdd.sh` (planned)
- ADR: `./ai_dev_flow/scripts/validate_adr.sh` (planned)
- SYS: `./ai_dev_flow/scripts/validate_sys.sh` (planned)
- SPEC: `./ai_dev_flow/scripts/validate_spec.sh` (planned)

**Note**: If validation script not available, use template and SHARED_CONTENT.md for manual validation.

### Pre-Commit Checklist

- [ ] Document Control section completed with all required metadata (project name, version, date, owner, preparer, status)
- [ ] Document Revision History table initialized with at least initial version entry
- [ ] IDs comply with `ID_NAMING_STANDARDS.md` (NNN or NNN-YY format, H1 anchors, zero-padding)
- [ ] No ID collisions: each NNN number used only once (either atomic TYPE-NNN OR multi-doc TYPE-NNN-YY group, never both)
- [ ] All cross-references use markdown links with valid paths and anchors
- [ ] Cumulative tagging complete for artifact layer (no missing upstream tags)
- [ ] Traceability section includes upstream sources and downstream artifacts
- [ ] Quality attributes defined (where applicable)
- [ ] Validation scripts pass
- [ ] No broken links or missing anchors
- [ ] File size under 50,000 tokens (Claude Code standard) or 100,000 tokens (absolute maximum)

### Validation Commands

**Quality Gates Validation:**
```bash
# Validate artifact meets layer transition requirements
./scripts/validate_quality_gates.sh docs/REQ/risk/lim/REQ-003.md

# Artifact-specific validation
./ai_dev_flow/scripts/validate_brd_template.sh docs/BRD/BRD-001.md
./ai_dev_flow/scripts/validate_req_template.sh docs/REQ/api/ib/REQ-002.md

# Link integrity validation
./ai_dev_flow/scripts/validate_links.py --path docs/ --check-anchors
```

**Tag-Based Traceability Validation:**
```bash
# Extract all tags from codebase
python ai_dev_flow/scripts/extract_tags.py --source src/ docs/ tests/ --output docs/generated/tags.json

# Validate tags against documents
python ai_dev_flow/scripts/validate_tags_against_docs.py --tags docs/generated/tags.json --strict

# Validate cumulative tagging hierarchy
python ai_dev_flow/scripts/validate_tags_against_docs.py --source src/ docs/ tests/ --docs docs/ --validate-cumulative --strict

# Generate bidirectional matrices
python ai_dev_flow/scripts/generate_traceability_matrices.py --tags docs/generated/tags.json --output docs/generated/matrices/

# Complete workflow (extract → validate → generate)
python ai_dev_flow/scripts/generate_traceability_matrices.py --auto
```

### Traceability Matrix Update Workflow

**Timing**: Update matrix in same commit as artifact creation, after validation passes

**Process**:
1. Create artifact file
2. Validate artifact (template compliance, tag format, content completeness)
3. If validation passes:
   - Update traceability matrix with new artifact
   - Commit artifact + matrix together with descriptive message
4. If validation fails:
   - Fix issues
   - Re-validate
   - Then proceed to step 3

**Rationale**: Single commit ensures matrix stays synchronized with artifacts. Validation gate prevents bad data in matrix.

---

## 5. Traceability Matrix Enforcement (MANDATORY)

### Policy

**CRITICAL RULE**: EVERY time you create or update a document of ANY artifact type, you MUST:

1. **Check for existing traceability matrix**: Look for `[TYPE]-000_TRACEABILITY_MATRIX.md`
2. **Create if missing**: Use template from `ai_dev_flow/[TYPE]/[TYPE]-000_TRACEABILITY_MATRIX-TEMPLATE.md`
3. **Update if exists**: Add new document entry with:
   - Document ID and title
   - Upstream sources (documents that drove this artifact)
   - Downstream artifacts (documents/code derived from this)
   - Status and completion percentage
4. **Validate bidirectional links**: Ensure all references resolve correctly

### Quality Gate

**Hard Requirement**: Pull requests will be rejected if traceability matrix is not updated.

**Zero Exceptions**: This applies to ALL artifact types without exception.

### Matrix Contents

Each traceability matrix tracks:

- **Section 2: Complete Inventory**: All documents of this type with status
- **Section 3: Upstream Traceability**: Which documents drove creation (BRD → PRD → EARS, etc.)
- **Section 4: Downstream Traceability**: Which documents/code derive from this (PRD → EARS → BDD → REQ)
- **Section 5: Cross-Dependencies**: Relationships between documents of same type
- **Section 8: Implementation Status**: Completion percentage and validation status

### Why This Matters

- **Impact Analysis**: When BRD-001 changes, matrix shows affected PRDs, EARS, BDD, REQ, SPEC, Code
- **Coverage Validation**: Ensures no orphaned requirements (100% traceability)
- **Regulatory Compliance**: Audit trails required for SEC, FINRA, FDA, ISO compliance
- **Change Management**: Know exactly what breaks when upstream requirements change
- **Quality Assurance**: Automated validation prevents missing links

---

## 6. Documentation Standards

**Authoritative Reference**: `ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` (Appendix sections)

### Language Requirements

- Objective, factual language only
- No promotional content or subjective claims
- Document implementation complexity (scale 1-5)
- Include resource requirements and constraints
- Specify failure modes and error conditions

### Code Separation

- No Python code blocks in markdown documentation
- Use Mermaid flowcharts for logic representation
- Create separate `.py` files for code examples
- Reference format: `[See Code Example: filename.py - function_name()]`

### Token Efficiency (Tool-Optimized)

- Claude Code: Maximum 50,000 tokens (200KB) standard, 100,000 tokens (400KB) absolute maximum
- Gemini CLI: Use file read tool (not `@`) for files >10,000 tokens - no splitting needed
- GitHub Copilot: Keep <30KB or create companion summaries
- Create sequential files only when exceeding 100,000 tokens or logical boundaries
- One sentence per function description maximum
- Use tabular format for parameter specifications
- Employ bullet points for configuration options

---

## 7. Document Control Section

**MANDATORY for all artifacts**: Document Control section must be the **first section** at the very top of the document (before all numbered sections).

### Required Fields

- **Project Name**
- **Document Version** (e.g., v1.0, v2.1)
- **Date** (YYYY-MM-DD format)
- **Document Owner** (responsible person/role)
- **Prepared By** (author name)
- **Status** (Draft, In Review, Approved, Superseded)

### Document Revision History

Must include a table with at least the initial version entry:

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | YYYY-MM-DD | Author Name | Initial version |

---

## Usage in Artifact Skills

Each artifact-specific skill (doc-brd, doc-prd, etc.) should include:

```markdown
## Prerequisites

Before creating this artifact, read:
1. **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md` (this document)
2. **Template**: `ai_dev_flow/{TYPE}/{TYPE}-TEMPLATE.{ext}`
3. **Creation Rules**: `ai_dev_flow/{TYPE}/{TYPE}_CREATION_RULES.md`
4. **Validation Rules**: `ai_dev_flow/{TYPE}/{TYPE}_VALIDATION_RULES.md`
```

---

**End of Shared Content**
