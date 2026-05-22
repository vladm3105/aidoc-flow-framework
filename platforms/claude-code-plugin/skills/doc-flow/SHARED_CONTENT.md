# Shared Content for Doc-Flow Skills

This document contains standards and guidelines shared across all document artifact skills (doc-brd, doc-prd, doc-ears, doc-bdd, doc-adr, doc-spec, doc-tdd, doc-iplan).

**Import Reference**: All artifact-specific skills MUST reference this document for ID standards, traceability format, cumulative tagging hierarchy, and quality gates.

---

## 1. Document ID Naming Standards

**Authoritative Reference**: `framework/governance/ID_NAMING_STANDARDS.md`

### Universal Numbering Pattern (All Document Types)

- **Primary Number (NNN)**: 2+ digit sequential number for an atomic logical document (01-99, then 100-999 when needed)
- **Sub-Document Number (YY)**: 2-3 digit sequential number within an atomic document [OPTIONAL] (01-99, then 100-999 when needed)
- **Format**: `TYPE-NNN` or `TYPE-NNN-YY` (e.g., `EARS-001`, `BRD-009-02`, `ADR-100`)
- **Zero-Padding**: Always pad to minimum digit count (001, 01) until exceeding range
- **Uniqueness Rule**: Each NNN number is unique and can be used EITHER as:
  - Atomic document: `TYPE-NNN_{slug}.yaml` (e.g., `BRD-001_foundation.yaml`)
  - Multi-document group: `TYPE-NNN-01_{slug}.yaml`, `TYPE-NNN-02_{slug}.yaml`, etc.
  - ❌ INVALID: Cannot have both `BRD-009_{slug}.yaml` AND `BRD-009-01_{slug}.yaml` (NNN=009 collision)
  - ✅ VALID: Can have `BRD-009-01_{slug}.yaml` AND `BRD-009-02_{slug}.yaml` (same NNN, different YY)

### File Naming Patterns

- BRD: `BRD-NNN_{slug}.yaml` or `BRD-NNN-YY_{slug}.yaml` (Business Requirements Documents) - **Location: docs/01_BRD/**
- PRD: `PRD-NNN_{slug}.yaml` or `PRD-NNN-YY_{slug}.yaml` (Product Requirements) - **Location: docs/02_PRD/**
- EARS: `EARS-NNN_{slug}.yaml` or `EARS-NNN-YY_{slug}.yaml` (Formal Requirements) - **Location: docs/03_EARS/**
- BDD: `BDD-NNN_{slug}.yaml` or `BDD-NNN-YY_{slug}.yaml` (Behavior-Driven Tests) - **Location: docs/04_BDD/**
- ADR: `ADR-NNN_{slug}.yaml` or `ADR-NNN-YY_{slug}.yaml` (Architecture Decisions) - **Location: docs/05_ADR/**
- SPEC: `SPEC-NNN_{slug}.yaml` or `SPEC-NNN-YY_{slug}.yaml` (Technical Specifications) - **Location: docs/06_SPEC/**
- TDD: `TDD-NNN_{slug}.yaml` or `TDD-NNN-YY_{slug}.yaml` (Test-Driven Development guides) - **Location: docs/07_TDD/**
- IPLAN: `IPLAN-NNN_{slug}.yaml` or `IPLAN-NNN-YY_{slug}.yaml` (Implementation Plans) - **Location: docs/08_IPLAN/**

### ID Format Rules

- Document IDs follow `TYPE-NN` (e.g., `BRD-09`, `SPEC-01`, `IPLAN-01`)
- Element IDs follow the 4-segment `TYPE.NN.SS.xxxx` form (e.g., `BRD.01.07.a7f3`)
- SPEC YAML uses `id:` field with lowercase_snake_case: `position_limit_service`
- Categories encoded in folder paths, not ID prefixes
- Sub-numbering (-YY) used ONLY when single logical document requires multiple related files with sequential reading order
- Each NNN number must be unique (no collisions between atomic and multi-doc patterns)

### Document ID Independence

**⚠️ CRITICAL - ID INDEPENDENCE**: Document IDs are independent across artifact types. BRD-09 does NOT need to correspond to PRD-09.

**Why IDs Don't Match**:
- IDs are assigned sequentially within each artifact type based on creation order
- Documents are created as needed, not in lockstep across all types
- Example: BRD-09 covers "Broker Integration" but PRD-09 might cover "Cash-Secured Put Workflow" (completely unrelated)
- The corresponding PRD for broker integration might be PRD-16 or any other number

**Always Use Index Files for Discovery**: To find documents by topic/content:
- Index files use ID `00` in their identifier (e.g., PRD-00, EARS-00, ADR-00)
- Index filenames include "index" in the name
- Index files contain descriptions and summaries of all documents of that artifact type
- Organized by domain, category, or functional area

**Best Practice for AI Assistants**:
1. When searching for related documents, **find and read the index file first** (ID: 00, name contains "index")
2. Search index descriptions for keywords related to your topic
3. Do NOT assume document IDs match across artifact types
4. Use traceability tags within documents to find explicitly linked artifacts
5. Verify document content matches your topic before assuming relationship

---

## 2. Traceability Section Format

**Authoritative Reference**: `framework/governance/TRACEABILITY.md`

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
- **Anchors/IDs**: Primary anchor(s) in this file (e.g., `# EARS-03`)
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

- Use markdown links with standardized paths: `[ADR-033](../05_ADR/ADR-033_risk_architecture.yaml#ADR-033)`
- Include anchors: `#ADR-033`, `#BDD-003`, `#SPEC-001`
- Use relative paths from current file location
- Examples:
  - From docs/01_BRD/: `[ADR-033](../05_ADR/ADR-033_risk_architecture.yaml#ADR-033)`
  - From docs/06_SPEC/: `[ADR-001](../05_ADR/ADR-001_architecture.yaml#ADR-001)`

---

## 3. Cumulative Tagging Hierarchy

**Authoritative Reference**: `framework/governance/TRACEABILITY.md`

### Principle

Each artifact layer must include traceability tags from ALL upstream artifact layers, creating a complete audit trail from business requirements through production code.

### Cumulative Tagging Table (8 Layers)

| Layer | Artifact Type | Required Tags | Tag Count | Format | Notes |
|-------|---------------|---------------|-----------|--------|-------|
| 0 | **Strategy** | None | 0 | External | Business owner documents, no formal artifact |
| 1 | **BRD** | None | 0 | YAML | Top level, no upstream dependencies |
| 2 | **PRD** | `@brd` | 1 | YAML | References parent BRD |
| 3 | **EARS** | `@brd`, `@prd` | 2 | YAML | Cumulative: BRD + PRD |
| 4 | **BDD** | `@brd`, `@prd`, `@ears` | 3 | YAML | Cumulative: BRD through EARS |
| 5 | **ADR** | `@brd` through `@bdd` | 4 | YAML | Cumulative: BRD through BDD |
| 6 | **SPEC** | `@brd` through `@adr` | 5 | YAML (`cumulative_tags`) | Cumulative: BRD through ADR |
| 7 | **TDD** | `@brd` through `@spec` | 6 | YAML | Cumulative: BRD through SPEC |
| 8 | **IPLAN** | `@brd` through `@tdd` | 7 | YAML | Cumulative: BRD through TDD |
| — | **Code** | `@brd` through `@iplan` | 8 | Docstrings | Source code (output target) |

### Tag Count Clarification

**CRITICAL RULE**: Tag Count = Number of UPSTREAM layers (artifacts do NOT tag themselves)

**Calculation Formula**: For Layer N, Tag Count = N - 1

**Examples**:
- **Layer 2 (PRD)**: 1 upstream tag (@brd)
- **Layer 6 (SPEC)**: 5 upstream tags (@brd, @prd, @ears, @bdd, @adr)
- **Layer 8 (IPLAN)**: 7 upstream tags (@brd, @prd, @ears, @bdd, @adr, @spec, @tdd)

**Validation Method**:
1. Count `@artifact:` lines in Traceability section
2. Should equal Layer Number minus 1

### Tag Format

```markdown
@brd: BRD.09.01.0115, BRD.09.01.1901
@prd: PRD.16.07.0703
@ears: EARS.12.24.2402, EARS.12.24.2401
@bdd: BDD.15.13.1301
@adr: ADR-033
@spec: SPEC-018
@tdd: TDD.15.04.2901
@iplan: IPLAN-01
```

### Feature-Level Traceability Tags

Internal feature IDs within documents use simple sequential numbering, while cross-references use the 4-segment element ID:

| Context | Format | Example | Cross-Reference |
|---------|--------|---------|-----------------|
| PRD Features | `NNN` | `001`, `015`, `042` | `@prd: PRD.22.07.0715` |
| BRD Objectives | `NNN` | `030`, `006` | `@brd: BRD.01.01.0130` |
| EARS Statements | `NNN` | `003`, `007` | `@ears: EARS.06.24.2403` |
| TDD Test Cases | `NNN` | `001`, `004` | `@tdd: TDD.01.04.a3c1` |

**Global Uniqueness**: Document ID + Feature ID creates globally unique references.

### Format Rules

- Element IDs: Use the 4-segment `TYPE.NN.SS.xxxx` format (e.g., `BRD.01.01.0130`), where `xxxx` is a 4-char hex content hash
- Document-level (dash) refs: `SPEC-NN`, `ADR-NN`, `IPLAN-NN`
- Multiple refs: Comma-separated list within same tag line
- SPEC format: Use YAML `cumulative_tags:` mapping instead of markdown comments
- BDD format: Tags carried in the BDD YAML scenario metadata

### Validation Rules

1. **No gaps**: Each layer must include ALL upstream tags from previous layers
2. **Format compliance**: Element tags follow `@artifact-type: TYPE.NN.SS.xxxx`; document-level tags follow `@artifact-type: TYPE-NN`
3. **Valid references**: All tagged document IDs must exist and be reachable
4. **SPEC/IPLAN exception**: SPEC and IPLAN use YAML format, not markdown tags

### SPEC YAML Format Example (5 tags)

```yaml
# SPEC-018: Order Placement Service Specification

spec_id: SPEC-018
title: "Order Placement Service Technical Specification"
version: "1.0.0"

# Cumulative Tagging Hierarchy (Layer 6)
cumulative_tags:
  brd: "BRD.09.01.0115, BRD.09.01.1906"
  prd: "PRD.16.07.0703"
  ears: "EARS.12.24.2402, EARS.12.24.2401"
  bdd: "BDD.15.13.1301"
  adr: "ADR-033"
```

### Benefits of Cumulative Tagging

- **Complete Audit Trail**: Every artifact traces back to original business requirements
- **Impact Analysis**: Instantly identify all downstream artifacts affected by upstream changes
- **Regulatory Compliance**: SEC, FINRA, FDA, ISO audit requirements satisfied automatically
- **Automated Validation**: Skills enforce tagging compliance during review
- **Change Management**: Know exactly what breaks when requirements change
- **Coverage Metrics**: Measure traceability completeness across entire codebase

---

## 4. Quality Gates & Validation

### Quality Gates

**Authoritative Reference**: `framework/governance/DOC_GOVERNANCE_CORE.md`

Each artifact layer requires ≥90% ready score before progressing to next layer.
The framework is spec-only and ships no runtime scripts — the artifact skill
itself runs the declarative validation checklist.

### Creation and Validation Rules References

Before creating ANY artifact, consult:

1. **Layer README**: `framework/layers/<NN>_<X>/README.md` - Authoritative creation and validation guidance for that layer
2. **Template**: `framework/layers/<NN>_<X>/{TYPE}-TEMPLATE.yaml` - Starting structure
3. **Governance**: `framework/governance/` - ID, traceability, and quality-gate standards shared by all layers

**Available for artifact types**: BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN

**Note**: Each layer's `README.md` carries the creation rules and validation
requirements for that artifact type. The corresponding `doc-<type>-validator`
skill runs the declarative checklist.

### Validation Approach

The plugin skill **is** the validator. There are no external validation
scripts. To validate an artifact:

1. Run the matching `doc-<type>-validator` skill (e.g. `doc-brd-validator`,
   `doc-spec-validator`, `doc-iplan-validator`).
2. The validator applies the layer's declarative checklist (from
   `framework/layers/<NN>_<X>/README.md`) and the shared governance standards.
3. For cross-document and traceability checks, use `doc-validator` and
   `trace-check`.

### Pre-Commit Checklist

- [ ] Document Control section completed with all required metadata (project name, version, date, owner, preparer, status)
- [ ] Document Revision History table initialized with at least initial version entry
- [ ] IDs comply with `ID_NAMING_STANDARDS.md` (TYPE-NN doc IDs, TYPE.NN.SS.xxxx element IDs, zero-padding)
- [ ] No ID collisions: each NNN number used only once (either atomic TYPE-NNN OR multi-doc TYPE-NNN-YY group, never both)
- [ ] All cross-references use markdown links with valid paths and anchors
- [ ] Cumulative tagging complete for artifact layer (no missing upstream tags)
- [ ] Traceability section includes upstream sources and downstream artifacts
- [ ] Quality attributes defined (where applicable)
- [ ] Validation checklist passes (run the `doc-<type>-validator` skill)
- [ ] No broken links or missing anchors
- [ ] File size under 50,000 tokens (Claude Code standard) or 100,000 tokens (absolute maximum)

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

### Bidirectional Traceability Update Workflow (MANDATORY)

When creating a downstream artifact, you MUST update the upstream document's traceability section to maintain bidirectional linkage.

**Workflow**:

```
1. CREATE downstream artifact
   └─ Example: Create PRD-01 from BRD-01

2. UPDATE downstream artifact
   └─ Add upstream traceability tags:
      @brd: BRD.01.01.0115

3. UPDATE upstream artifact (CRITICAL - often missed)
   └─ Add downstream reference in Traceability section:
      - Downstream Artifacts: [PRD-01](../02_PRD/PRD-01_feature.yaml#PRD-01)

4. VALIDATE both documents
   └─ Run the doc-<type>-validator checklist on both upstream and downstream

5. COMMIT together
   └─ Single commit with descriptive message referencing both artifacts
```

**Bidirectional Update Table**:

| When Creating | Update Upstream | Add to Section |
|---------------|-----------------|----------------|
| PRD | BRD | `Downstream Artifacts: PRD-NNN` |
| EARS | PRD (and BRD) | `Downstream Artifacts: EARS-NNN` |
| BDD | EARS (and PRD, BRD) | `Downstream Artifacts: BDD-NNN` |
| ADR | BDD (and upstream) | `Downstream Artifacts: ADR-NNN` |
| SPEC | ADR (and upstream) | `Downstream Artifacts: SPEC-NNN` |
| TDD | SPEC (and upstream) | `Downstream Artifacts: TDD-NNN` |
| IPLAN | TDD (and upstream) | `Downstream Artifacts: IPLAN-NNN` |

**Practical Guidance**:

1. **Minimum Requirement**: Update immediate upstream document (PRD → update originating BRD)
2. **Recommended**: Update all referenced upstream documents in traceability chain
3. **Tooling**: Run `doc-validator` to detect and auto-fix missing bidirectional links
4. **Manual Process**: Open each upstream document, locate Traceability section, add downstream link

**Example - Creating PRD-01 from BRD-01**:

```markdown
# In PRD-01 (new downstream artifact):
## Traceability
- Upstream Sources: [BRD-01](../01_BRD/BRD-01_platform.yaml#BRD-01)
- Downstream Artifacts: (none yet)
@brd: BRD.01.01.0115

# In BRD-01 (update existing upstream artifact):
## Traceability
- Upstream Sources: (none - BRD is Layer 1)
- Downstream Artifacts: [PRD-01](../02_PRD/PRD-01_feature.yaml#PRD-01)  ← ADD THIS
```

**Why This Matters**:

- **Orphan Prevention**: Ensures no downstream artifacts exist without upstream knowledge
- **Impact Analysis**: When BRD changes, immediately see all dependent artifacts
- **Audit Compliance**: Regulatory audits require bidirectional traceability evidence
- **Navigation**: Users can traverse the artifact chain in either direction

---

## 5. Traceability Matrix Enforcement (MANDATORY)

### Policy

**CRITICAL RULE**: EVERY time you create or update a document of ANY artifact type, you MUST:

1. **Check for existing traceability matrix**: Look for `[TYPE]-00_TRACEABILITY_MATRIX.md`
2. **Create if missing**: Use the matrix structure documented in `framework/layers/<NN>_<X>/README.md`
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
- **Section 4: Downstream Traceability**: Which documents/code derive from this (PRD → EARS → BDD → ADR)
- **Section 5: Cross-Dependencies**: Relationships between documents of same type
- **Section 8: Implementation Status**: Completion percentage and validation status

### Why This Matters

- **Impact Analysis**: When BRD-001 changes, matrix shows affected PRDs, EARS, BDD, SPEC, TDD, IPLAN, Code
- **Coverage Validation**: Ensures no orphaned requirements (100% traceability)
- **Regulatory Compliance**: Audit trails required for SEC, FINRA, FDA, ISO compliance
- **Change Management**: Know exactly what breaks when upstream requirements change
- **Quality Assurance**: Declarative validation prevents missing links

---

## 6. Documentation Standards

**Authoritative Reference**: `framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` (Appendix sections)

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

## 8. Diagram Standards

**Central Authority**: `framework/governance/DIAGRAM_STANDARDS.md`

All diagrams, charts, workflows, and visual representations in SDD artifacts MUST use Mermaid syntax. Text-based diagrams (ASCII art, box drawings) are prohibited.

### Exempted Content

- Directory tree structures (`├── └── │`) - allowed for file/folder representation
- Code blocks (for source code examples)
- ASCII tables (for tabular data)

### Mermaid Diagram Types

| Use Case | Mermaid Type |
|----------|--------------|
| Architecture | `graph`, `flowchart` |
| Sequences | `sequenceDiagram` |
| State machines | `stateDiagram-v2` |
| Data flow | `flowchart` |
| Component relationships | `graph` |

**Diagram Skill**: Use `mermaid-gen` skill for diagram creation.

---

## Usage in Artifact Skills

Each artifact-specific skill (doc-brd, doc-prd, etc.) should include:

```markdown
## Prerequisites

Before creating this artifact, read:
1. **Shared Standards**: `../doc-flow/SHARED_CONTENT.md` (this document)
2. **Template**: `framework/layers/<NN>_<X>/{TYPE}-TEMPLATE.yaml`
3. **Layer README**: `framework/layers/<NN>_<X>/README.md` (creation + validation rules)
4. **Governance**: `framework/governance/` (ID, traceability, quality gates)
```

---

**End of Shared Content**
