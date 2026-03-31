---
title: "Document ID & Tagging Standards"
tags:
  - framework-guide
  - shared-architecture
  - required-both-approaches
  - active
custom_fields:
  document_type: naming-standards
  priority: shared
  development_status: active
  applies_to: [all-artifacts, documentation]
  version: "3.0"
  scope: documentation-only
---

# Document ID & Tagging Standards — ai_dev_ssd_flow

Status: Authoritative for this `ai_dev_ssd_flow` example set. These rules reflect the naming and linking already used here and supersede repo-wide norms within this directory (do not change existing files to match other guides).

Purpose
- Provide a single, practical guide for IDs, tags, links, file layout, and validation within this example.
- Eliminate duplication while preserving mandatory rules and quick-reference tips.

## Scope Clarification: Documentation Only

**IMPORTANT**: This naming standard applies ONLY to Specification-Driven Development (SDD) **documentation artifacts**. It does NOT apply to source code files.

### [PASS] Apply ID_NAMING_STANDARDS To:
- Documentation files in `docs/` directories:
  - `01_BRD/` - Business Requirements Documents
  - `02_PRD/` - Product Requirements Documents
  - `03_EARS/` - EARS Requirements
  - `04_BDD/` - BDD Requirements (unified YAML, Gherkin in `_example` fields)
  - `05_ADR/` - Architecture Decision Records
  - `06_SYS/` - System Requirements
  - `07_REQ/` - Requirements
  - `08_CTR/` - API Contracts (CTR)
  - `09_SPEC/` - Technical Specifications (YAML)
  - `10_TSPEC/` - Test Specifications (UTEST, ITEST, STEST, FTEST)
  - `11_TASKS/` - AI Task Lists
  - `REF/` - Reference Documents (supplementary, non-workflow documentation)


### [FAIL] Do NOT Apply ID_NAMING_STANDARDS To:
- **Python source code**: Follow PEP 8 naming conventions
  - Modules: `snake_case.py`
  - Classes: `PascalCase`
  - Functions/methods: `snake_case()`
  - Constants: `UPPER_SNAKE_CASE`
- **Python test files**: Follow pytest conventions
  - Test modules: `test_*.py` or `*_test.py`
  - Test functions: `test_*()`
  - Fixtures: `snake_case()`
- **Other source files**: Follow language-specific conventions
  - JavaScript/TypeScript: Per ESLint/TSLint rules
  - Java: Per Java naming conventions
  - Go: Per Go style guide

### Exception: BDD Test Files
BDD test scenarios located in `tests/bdd/` or similar directories **SHOULD** follow ID_NAMING_STANDARDS:

```
tests/bdd/gateway/BDD-01_connection_management.yaml
tests/bdd/gateway/BDD-02_error_handling.yaml
```

---

## ID Notation Clarification (CRITICAL)

The SDD framework uses **two distinct notations** that serve different purposes. Understanding this distinction is essential:

| Purpose | Notation | Format | Example | References |
|---------|----------|--------|---------|------------|
| **Document Reference** | Dash | `TYPE-NN` | `ADR-01`, `BRD-07` | Whole document/file |
| **Element Reference** | Dot | `TYPE.NN.TT.SS` | `BRD.07.eb7f` | Specific element within document |

### Document Reference (Dash Notation)

**Format**: `TYPE-NN` (hyphen separator)

**Purpose**: References the complete document file. Use when pointing to an entire document.

**Examples**:
- `ADR-33` → References the document file `ADR-33_risk_limit_enforcement.md`
- `SPEC-01` → References `SPEC-01_api_client.yaml`
- `CTR-05` → References `CTR-05_data_service.md` + `CTR-05_data_service.yaml`

**Tag Usage**: `@adr: ADR-33`, `@spec: SPEC-01`, `@ctr: CTR-05`

### Element Reference (Dot Notation)

**Format**: `TYPE.NN.TT.SS` (dot separator, 4 segments)

**Purpose**: References a specific element (requirement, feature, constraint) inside a document.

**Components**:
- `TYPE`: Document type (BRD, PRD, REQ, etc.)
- `NN`: Document number (matching filename digits)
- `TT`: Element type code (01=Functional Req, 06=Acceptance Criteria, etc.)
- `SS`: Sequential number within element type

**Examples**:
- `BRD.07.eb7f` → Functional Requirement #1 inside BRD-07
- `PRD.02.c603` → User Story #5 inside PRD-02
- `EARS.04.3ce6` → EARS Requirement #8 inside EARS-04

**Tag Usage**: `@brd: BRD.07.eb7f`, `@prd: PRD.02.c603`

### Which Artifacts Use Which Notation?

| Notation | Document Types | Rationale |
|----------|---------------|-----------|
| **Dash** (Document-level) | ADR, SPEC, CTR | Referenced as complete units |
| **Dot** (Element-level) | BRD, PRD, EARS, BDD, SYS, REQ, TASKS | Contain multiple numbered elements |

### Common Mistakes to Avoid

| Incorrect | Correct | Explanation |
|-----------|---------|-------------|
| `@brd: BRD-07` | `@brd: BRD.07.eb7f` | BRD uses element notation (dot) |
| `@adr: ADR.33.22e3` | `@adr: ADR-33` | ADR uses document notation (dash) |
| `BRD.7.01.01` | `BRD.07.eb7f` | Element DOC_NUM must match filename digits |

---

Scope & Authority
- Applies to: PRD, SYS, REQ, ADR, BDD, SPEC, EARS, CTR, AI-TASKS in this example.
- One document per file.
- Filenames use sequential numeric prefixes for ordering; the full document IDs live in the H1 headings and tags.
- Categories are expressed by folder paths (e.g., `07_REQ/api/av`, `07_REQ/risk/lim`).
<!-- VALIDATOR:IGNORE-LINKS-START -->
- All cross-references use markdown link format: `[ID](relative/path.md#ANCHOR)`.
<!-- VALIDATOR:IGNORE-LINKS-END -->
- **Exception**: CTR (API Contracts) uses dual-file format: both .md and .yaml files required per contract.

Note on paths: Examples may show a top-level `docs/` prefix; in this ai_dev_ssd_flow directory, type folders live at the ai_dev_ssd_flow root (e.g., `01_BRD/`, `02_PRD/`, `05_ADR/`). Adjust relative links accordingly.

## General Utility Documents (`{DOC_TYPE}-00_*`)

Definition and Purpose
- `{DOC_TYPE}-000` is reserved across all artifact types to group general-purpose, cross-project, or utility documents that are not directly tied to a specific numbered project document.
- Typical uses: indexes, templates, traceability matrix templates, validation checklists, and reference guides.

Format
- Pattern: `{DOC_TYPE}-00_{slug}.{ext}` (e.g., `REQ-00_TRACEABILITY_MATRIX-TEMPLATE.md`, `TASKS-00_index.md`).
- These do not participate in the sequential DOC_NUM series and are globally recognizable as general/utility artifacts.

## Default Directory Model (All Types)

**Monolithic Document Policy**: All SDD documents are single, self-contained files up to 50,000 tokens. If a document exceeds 50,000 tokens, create a new document of the same type with its own scope (e.g., BRD-02 instead of splitting BRD-01). Do NOT split documents into sectioned files.

| Structure | Trigger | Format |
|-----------|---------|--------|
| **Flat** (Monolithic) | Default for all documents | `{TYPE}/{TYPE}-{ID}_{Slug}.{ext}` |
| **Nested** (Folder) | Review/fix companion files OR >1 file per ID | `{TYPE}/{TYPE}-{ID}_{Slug}/{TYPE}-{ID}_{Slug}.{ext}` |

### Flat Structure (Monolithic Documents)

- **Format**: `{TYPE}/{TYPE}-DOC_NUM_{slug}.md` (no folder, no section suffix)
- **H1 Title**: `# TYPE-DOC_NUM: Document Title`
- **Examples**:
  - `docs/01_BRD/BRD-01_platform_architecture.md`
  - `docs/02_PRD/PRD-02_user_authentication.md`
  - `docs/05_ADR/ADR-15_database_selection.md`
- **Rule**: Do NOT create a folder for monolithic files. The file lives directly in the type directory.

### Nested Folders (Companion Files Only)

- **Use for**: Documents with review/fix companion files, or types requiring multiple files per ID (CTR dual-file, BDD suites)
- **Format**: `{TYPE}/{TYPE}-DOC_NUM_{slug}/` folder containing the monolithic document and companion files
- **The document itself remains monolithic** (single file) inside the folder

### Type-Specific Exceptions

- **BDD**: Unified YAML format (`BDD-DOC_NUM_{slug}.yaml`), Gherkin syntax embedded in `_example` fields.
- **CTR**: Dual-file format (both `.md` and `.yaml`) stored together; use nested folder for multi-file contracts.


Universal Numbering Pattern (All Document Types)
- **Primary Number (DOC_NUM)**: Variable-length sequential number starting at 2 digits (01-99, then 100-999, 1000+)
  - **Notation**: "DOC_NUM" represents actual numeric digits (e.g., 01, 42, 99, 100, 1000)
  - **NOT**: Placeholder text like "NN" or "XXX"
  - **Minimum**: 2 digits (01)
  - **Growth**: Automatically expands when needed (99 → 100, 999 → 1000)
  - **Numbering Policy (explicit)**: Document numbers start at `01` and increase sequentially. As the sequence grows, the digit width MAY expand (e.g., `01…99` → `100…999` → `1000…`). Previously created documents keep their original width; new documents adopt the width required by the next number in sequence.
- **Format**:
  - **All Document Types** - monolithic, flat structure:
    - **Pattern**: `TYPE-DOC_NUM_{slug}.md` (e.g., `BRD-01_platform_architecture.md`)
    - **H1 Title**: `# TYPE-DOC_NUM: Title`
    - **Location**: Directly in type directory, or in nested folder if companion files exist
- **Zero-Padding**: Start with 2 digits (01), expand as needed
  - **Index/General Utility Files Use Zeros**: Use all-zero `DOC_NUM` to separate indexes and general utility artifacts from numbered documents.
    - This repository: uses 3 zeros (`-00_index.md`) consistently; do not rename historical files.
    - New repositories: choose `00` or `000` and keep it consistent across types.
    - General utility files follow `{DOC_TYPE}-00_{slug}.{ext}`.
- **Element ID DOC_NUM**: MUST match filename digit count exactly
  - Filename `BRD-01_platform.md` → Element ID `BRD.01.ae5c`
  - Filename `ADR-100_cloud_migration.md` → Element ID `ADR.100.0309`
- **Uniqueness Rule**: Each DOC_NUM is unique within its type
  - Format: `TYPE-DOC_NUM_{slug}.md` (e.g., `BRD-01_platform.md`)
- **Size Policy**: Documents are monolithic up to 50,000 tokens. If a document exceeds 50,000 tokens, create a new document of the same type with its own scope (e.g., BRD-02) rather than splitting BRD-01.
- **Vertical ID Alignment (Unified)**:
  - **Rule**: All downstream artifacts (`ADR`, `EARS`, `BDD`, `SYS`, `REQ`, `CTR`, `SPEC`) MUST match the ID of their parent `PRD` (or `BRD` if no PRD exists). **Exception**: `TASKS` have independent sequential numbering.
  - **Mapping**: `PRD-12` → `ADR-12`, `EARS-12`, `BDD-12`, `SPEC-12`, `SYS-12`, `REQ-12`, `CTR-12`.
  - **One-to-One (Flat Structure)**: 
    - Single artifact per PRD uses flat structure without decimal suffix.
    - **Examples**:
      - **ADR**: `PRD-05` → `ADR-05_caching_strategy.md` (single file, flat structure)
      - **SYS**: `PRD-02` → `SYS-02_session_memory.md` (single file, flat structure)
      - **BDD**: `PRD-04` → `BDD-04_authentication.yaml` (single file, flat structure)
      - **EARS**: `PRD-06` → `EARS-06_notifications.md` (single file, flat structure)
  - **One-to-Many (Nested Structure)**: 
    - Multiple artifacts of the same type per PRD use decimal suffixes starting from `.01` and increasing sequentially.
    - **MUST use nested folder structure** when one-to-many mapping exists.
    - **Examples**:
      - **ADR**: `PRD-12` → `ADR-12_{slug}/` folder containing `ADR-12.01.md`, `ADR-12.02.md`
      - **SYS**: `PRD-08` → `SYS-08_{slug}/` folder containing `SYS-08.01.md`, `SYS-08.02.md`, `SYS-08.03.md`
      - **BDD**: `PRD-05` → `BDD-05_{slug}/` folder containing `BDD-05.01.yaml`, `BDD-05.02.yaml`
  - **Roots**: `BRD` and `PRD` maintain independent sequential numbering starting from `01` and increasing sequentially.
  - **Exceptions**: 
    - `REF` and `*-00` utility files remain independent.
    - **TASKS** have independent sequential numbering (not PRD-aligned). TASKS are special document types that provide AI code generation instructions and audit trail of code generation steps.

Document ID Standards (ai_dev_ssd_flow)
- Requirements (REQ)
  - **H1 ID**: `REQ-DOC_NUM` (e.g., `# REQ-12: [LEARNING_GOV] ...`).
  - **Directory**: `07_REQ/REQ-{PRD_ID}_{Slug}/` (Vertical Slice Grouping).
  - **Files**: `REQ-{PRD_ID}_{Slug}.md` or `REQ-{TotalSequence}_{Slug}.md` inside.
  - **Alignment Rule**: REQ folder ID MUST match the parent PRD ID (e.g., `07_REQ/REQ-12_learning/` matches `PRD-12`).
  - **Variable Length**: DOC_NUM = 2+ digits (01-99, 100-999, 1000+)
  - **Notes**: Legacy category folders are not used. Use PRD-based vertical slice folders.
- ADRs
  - H1 ID: `ADR-DOC_NUM` (e.g., `# ADR-33: Risk Limit Enforcement Architecture`).
  - **Format**: `docs/05_ADR/ADR-DOC_NUM_{slug}.md`
  - **ID Alignment**: DOC_NUM MUST match the parent PRD ID (e.g., `PRD-33` -> `ADR-33`).
  - One-to-Many: `ADR-33.01`, `ADR-33.02` if multiple ADRs needed for one PRD.
  - Examples:
    - `docs/05_ADR/ADR-01_database_selection.md`
    - `docs/05_ADR/ADR-100_cloud_migration.md`
- BDD Requirements
  - **File Format**: Unified YAML (same as all other layers). Gherkin syntax embedded in `_example` fields.
    - **BDD Documents**: `BDD-DOC_NUM_{slug}.yaml` (unified YAML format)
    - **Index**: `BDD-00_index.md` (Markdown format)
    - **Template**: `BDD-TEMPLATE.yaml` (unified YAML template)

  **File Organization**:
  - Monolithic: single `.yaml` file per BDD document, up to 50,000 tokens
  - If >50,000 tokens: create a new BDD document with its own scope (e.g., BDD-03)
  - **ID Alignment**: DOC_NUM MUST match the parent PRD ID (e.g., `PRD-02` -> `BDD-02`)
  - Variable Length: DOC_NUM matches parent PRD
  - Tags (mandatory):
    - `@brd:BRD.NN.EE.SS` (upstream BRD element)
    - `@prd:PRD.NN.EE.SS` (upstream PRD element)
    - `@ears:EARS.NN.SS.RR` (upstream EARS requirement)
  - Tags appear before `Scenario:` using valid relative paths + anchors
- Technical Specifications (SPEC)
  - **Vertical ID Alignment**: SPEC ID MUST match the parent PRD ID (e.g., `PRD-12` -> `SPEC-12`).
  - **Format**: `09_SPEC/SPEC-DOC_NUM_{slug}.yaml`
  - **One-to-Many**: Use decimal suffixes for multiple micro-SPECs (e.g., `SPEC-12.01_{slug}.yaml`, `SPEC-12.02_{slug}.yaml`).
  - Variable Length: DOC_NUM matches parent PRD.
  - **Traceability**: Each SPEC independently validates REQ coverage.
- API Contracts (CTR)
  - H1 ID: `CTR-DOC_NUM` (e.g., `# CTR-01: resource Risk Validation Contract`).
  - Filename (Dual Format): `CTR-DOC_NUM_{slug}.md` + `CTR-DOC_NUM_{slug}.yaml` (both required)
  - Organization: Optional subdirectories by service type: `08_CTR/{agents,mcp,infra}/CTR-DOC_NUM_{slug}.{md,yaml}`
  - **ID Alignment**: DOC_NUM MUST match the parent PRD ID.
  - Variable Length: DOC_NUM matches parent PRD.
  - YAML `contract_id:` uses lowercase_snake_case (e.g., `contract_id: position_risk_validation`)
  - Notes: Both .md and .yaml must exist for each CTR-DOC_NUM; slugs must match exactly.

- AI Tasks (TASKS)
  - H1 ID: `TASKS-DOC_NUM` (e.g., `# TASKS-03: [RESOURCE_LIMIT] Service Implementation`)
  - Filename: `11_TASKS/TASKS-DOC_NUM_{slug}.md` with a tasks index at `11_TASKS/TASKS-00_index.md`.
  - **ID Alignment**: DOC_NUM MUST match the parent PRD ID (and associated SPEC ID).
  - Variable Length: DOC_NUM matches parent PRD.
  - Notes: SPEC implementation plans with exact TODOs for code generation. Each TASKS corresponds to one SPEC.
  - Allocation: ID matched to parent PRD.
- Reference Documents (REF)
  - H1 ID: `{TYPE}-REF-DOC_NUM` (e.g., `# BRD-REF-01: Project Overview`)
  - Filename: `{TYPE}-REF-DOC_NUM_{slug}.md` (e.g., `BRD-REF-01_project_overview.md`)
  - Location: Within parent TYPE directory (e.g., `docs/01_BRD/BRD-REF-01_project_overview.md`)
  - Variable Length: DOC_NUM = 2+ digits (01-99, 100-999, 1000+)
  - Numbering: Independent sequence per parent TYPE (BRD-REF-01, ADR-REF-01 are separate sequences)
  - Traceability: Optional (encouraged but not required)
  - Validation: Minimal (non-blocking)
  - Required Sections: Document Control, Revision History, Introduction
  - Use Cases:
    - General project descriptions from business perspective
    - Infrastructure requirements documentation
    - Strategic vision descriptions
    - Dictionaries and glossaries
    - Reference material and guides
  - Notes: REF documents are supplementary and do not participate in formal traceability chain. Similar exemption treatment as `{TYPE}-00` index documents.
- Business Requirements Documents (BRD)
  - H1 ID: `BRD-DOC_NUM` (e.g., `# BRD-09: [EXTERNAL_INTEGRATION] Integration`)
  - **Format**: `docs/01_BRD/BRD-DOC_NUM_{slug}.md`
  - Variable Length: DOC_NUM = 2+ digits (01-99, 100-999, 1000+).
  - **Sequential**: Independent sequential numbering starting from `01`.
  - Examples: `docs/01_BRD/BRD-01_platform_architecture.md`

PRD, SYS, and EARS Document Types
- Product Requirements Documents (PRD)
  - H1 ID: `PRD-DOC_NUM` (e.g., `# PRD-03: resource Risk Limits`)
  - **Format**: `docs/02_PRD/PRD-DOC_NUM_{slug}.md`
  - Variable Length: DOC_NUM = 2+ digits (01-99, 100-999, 1000+).
  - **Sequential**: Independent sequential numbering starting from `01`.
  - Examples: `docs/02_PRD/PRD-01_user_authentication.md`
- System Architecture Documents (SYS)
  - H1 ID: `SYS-DOC_NUM` (e.g., `# SYS-03: resource Risk Limits`)
  - **Format**: `06_SYS/SYS-DOC_NUM_{slug}.md`
  - **One-to-Many**: `06_SYS/SYS-DOC_NUM_{slug}/` folder containing `SYS-DOC_NUM.01_{slug}.md`, `SYS-DOC_NUM.02_{slug}.md`, etc.
  - **ID Alignment**: DOC_NUM MUST match the parent PRD ID.
  - Variable Length: DOC_NUM matches parent PRD.
  - **Examples**:
    - Flat: `06_SYS/SYS-02_Session_Memory.md` (one SYS for PRD-02)
    - One-to-Many: `06_SYS/SYS-08_trading_intelligence/` containing `SYS-08.01_LLM_Context.md`, `SYS-08.02_LLM_Ensemble.md`, `SYS-08.03_Agent_Swarm.md` (three SYS for PRD-08)
- EARS Requirements (EARS)
  - H1 ID: `EARS-DOC_NUM` (e.g., `# EARS-03: [RESOURCE_LIMIT] Enforcement`)
  - Filename: `03_EARS/EARS-DOC_NUM_{slug}.md`
  - **ID Alignment**: DOC_NUM MUST match the parent PRD ID.
  - Variable Length: DOC_NUM matches parent PRD.
  - Notes: If document exceeds 50,000 tokens, create a new EARS document with its own scope.

One-to-Many Structure Examples (Vertical ID Alignment)

When a single PRD requires multiple downstream artifacts of the same type, ALL artifacts must use decimal suffixes starting from `.01` and must be organized in nested folders.

**Pattern**: `{LAYER}_DIR/{TYPE}-{PRD_ID}_{slug}/` containing `{TYPE}-{PRD_ID}.01_{slug}.md`, `{TYPE}-{PRD_ID}.02_{slug}.md`

**Complete Examples by Artifact Type**:

- **ADR (Architecture Decision Records)**
  ```
  PRD-01 → 05_ADR/ADR-01_iam/
     ADR-01.01_Authentication_Architecture.md
     ADR-01.02_4D_Authorization_Matrix.md
  ```

- **SYS (System Requirements)**
  ```
  PRD-08 → 06_SYS/SYS-08_trading_intelligence/
     SYS-08.01_LLM_Context_Automation.md
     SYS-08.02_LLM_Ensemble.md
     SYS-08.03_Trading_Agent_Swarm.md
  ```

- **BDD (Behavior-Driven Development)**
  ```
  PRD-03 → 04_BDD/BDD-03_risk_management/
     BDD-03.01_position_limits.yaml
     BDD-03.02_margin_requirements.yaml
     BDD-03.03_circuit_breakers.yaml
  ```

- **EARS (Event-Action-Response-State)**
  ```
  PRD-05 → 03_EARS/EARS-05_data_feeds/
     EARS-05.01_market_data_ingestion.md
     EARS-05.02_historical_data_sync.md
  ```

**Key Rules**:
1. **Folder naming**: Use descriptive slug that encompasses all child artifacts
2. **File naming**: Use decimal suffixes `.01`, `.02`, `.03` with specific descriptive slugs
3. **Consistency**: ALL artifacts of same type for same PRD use this pattern
4. **No mixing**: Don't mix flat and nested for same PRD-artifact type combination

**Note**: TASKS documents are NOT part of Vertical ID Alignment. They have independent sequential numbering (TASKS-01, TASKS-02, etc.) and serve as special document types that provide AI code generation instructions and audit trail of code generation steps.

File Organization Rules
- One document per file (PRD, SYS, REQ, ADR, SPEC, BDD, EARS, CTR, AI-TASKS, BRD).
- **Exception**: CTR (API Contracts) requires dual files: .md + .yaml per contract.
- Filenames use variable-length `DOC_NUM` numbering (2+ digits); H1 contains the full ID where applicable.
- All documents are monolithic (single self-contained file) up to 50,000 tokens. If a document exceeds 50,000 tokens, create a new document of the same type with its own scope.
- Structure (this example):
  - **Standard Pattern**:
    - Pattern: `TYPE/TYPE-DOC_NUM_{slug}.md`
    - Example: `01_BRD/BRD-01_platform.md`, `05_ADR/ADR-33_risk.md`
  - **Special Cases**:
    - `09_SPEC/SPEC-{PRD_ID}_{Slug}/SPEC-{PRD_ID}-{Seq}_{Slug}.yaml`
    - `08_CTR/CTR-DOC_NUM_{slug}.md` + `CTR-DOC_NUM_{slug}.yaml`
    - `04_BDD/BDD-DOC_NUM_{suite}/` (Always Nested for Suites)

## Nested Folder Organization

Documents with review/fix workflows use nested folders to keep the monolithic document and its companion files together.

### When to Use Nested Folders

| Trigger | Example |
|---------|---------|
| Document has review/fix workflow | BRD with `doc-brd-reviewer` cycle |
| Multiple related files | Document + companion files |
| Type requires multiple files per ID | CTR dual-file (.md + .yaml) |

### Folder Naming

**Pattern**: `{TYPE}-{NN}_{slug}/`

**Examples**:
- `BRD-01_f1_iam/`
- `BRD-07_f7_config/`
- `PRD-03_user_auth/`

### Document Pattern Within Folders

**Monolithic only** - single document file plus companion files:
- Document file: `{TYPE}-{NN}_{slug}.md`
- Example: `BRD-07_f7_config/BRD-07_f7_config.md`

## Companion Document Patterns

When documents go through review/fix cycles, companion files are generated and stored in the same nested folder.

### Review Reports

**Pattern**: `{TYPE}-{NN}.R_review_report_v{VVV}.md`

| Component | Description | Example |
|-----------|-------------|---------|
| `{TYPE}` | Document type | BRD, PRD, ADR |
| `{NN}` | Document number | 01, 02, 03 |
| `.R` | Review suffix (literal) | `.R` |
| `_review_report` | Report type (literal) | `_review_report` |
| `v{VVV}` | Version (3-digit, zero-padded) | v001, v002, v015 |

**Examples**:
- `BRD-01.R_review_report_v001.md`
- `PRD-03.R_review_report_v002.md`

### Fix Reports

**Pattern**: `{TYPE}-{NN}.F_fix_report_v{VVV}.md`

| Component | Description | Example |
|-----------|-------------|---------|
| `.F` | Fix suffix (literal) | `.F` |
| `_fix_report` | Report type (literal) | `_fix_report` |

**Examples**:
- `BRD-01.F_fix_report_v001.md`
- `ADR-05.F_fix_report_v002.md`

### Drift Cache

**Pattern**: `.drift_cache.json` (hidden file, exact name)

**Purpose**: Tracks upstream document hashes for drift detection.

**Location**: Inside the nested folder alongside document files.

### Complete Nested Folder Example

**Monolithic Document with Review Cycle**:

```text
BRD-07_f7_config/
 BRD-07_f7_config.md              # Single complete document
 BRD-07.R_review_report_v001.md   # Review report v1
 BRD-07.F_fix_report_v001.md      # Fix report v1
 .drift_cache.json                 # Drift detection
```

### Companion File Lifecycle

1. **First review**: Creates `.R_review_report_v001.md` and `.drift_cache.json`
2. **Fix cycle**: Creates `.F_fix_report_v001.md`
3. **Re-review**: Creates `.R_review_report_v002.md`, updates `.drift_cache.json`
4. **Subsequent cycles**: Increment version numbers sequentially

## Document Size Policy

**Monolithic documents**: All SDD documents are single, self-contained files up to 50,000 tokens. Do NOT split documents into sectioned files (index files, section files, etc.).

**When a document exceeds 50,000 tokens**: Create a new document of the same type with its own scope. For example, if BRD-01 exceeds the limit, create BRD-02 with a distinct scope rather than splitting BRD-01 into sections.

### Two Coexisting ID Patterns

The framework uses two distinct ID patterns for different purposes:

| Pattern | Format | Example | Purpose |
|---------|--------|---------|---------|
| **Document ID** | `TYPE-DOC_NUM` | `BRD-03` | Complete document reference |
| **Element ID** | `TYPE.DOC_NUM.TT.SS` | `BRD.03.debc` | Internal element (all dots, 4-segment) |

**Key Distinction**:
- `BRD-03` → Document reference (dash notation)
- `BRD.03.debc` → Element ID (all dots, 4-segment format for internal references)
- Element ID DOC_NUM MUST match filename digit count (e.g., `BRD-03` → `BRD.03.xx.xx`)

### Common Confusion: When to Use Each Format

**Question**: "Is the 4-segment format only for external traceability references?"

**Answer**: NO. The 4-segment format is used for **ALL element references**, both:
- Internal element headings: `### BRD.01.92d8: Feature Name`
- External traceability tags: `@brd: BRD.01.92d8`

**Rule Summary**:

| What You're Referencing | Format | Example |
|------------------------|--------|---------|
<!-- VALIDATOR:IGNORE-LINKS-START -->
| A **document file** | Dash format | `BRD-01`, `[BRD-01](../01_BRD/BRD-01.md)` |
<!-- VALIDATOR:IGNORE-LINKS-END -->
| A **specific element** (requirement, feature, constraint) | 4-segment dot format | `BRD.01.92d8`, `@brd: BRD.01.92d8` |

**Key Insight**: The 4-segment format unifies internal and external element references to avoid confusion. Use it consistently everywhere you reference a specific element. Element ID DOC_NUM MUST match filename digit count.

### Hyperlinked Traceability References (RECOMMENDED)

For enhanced navigability, traceability tags MAY be converted to clickable hyperlinks. This is **optional but recommended** for improved documentation usability.

**Tag-Only Format** (Primary - Always Valid):
```markdown
@brd: BRD.01.a341
```

**Hyperlinked Format** (Enhanced - Recommended for Published Docs):
```markdown
[@brd: BRD.01.a341](../../01_BRD/BRD-01_platform_architecture.md#brd010901-feature-name)
```

**Anchor ID Convention**: Convert element ID to lowercase, remove dots, append slug:
- Element: `BRD.01.a341` → Anchor: `#brd010901-feature-name`

**Format Comparison**:

| Aspect | Tag-Only | Hyperlinked |
|--------|----------|-------------|
| **Validation** | [PASS] Easy regex parsing | [WARN] Requires link checker |
| **Maintainability** | [PASS] No path breakage | [FAIL] Breaks when files move |
| **Navigation** | [FAIL] Manual search required | [PASS] One-click access |
| **Automation** | [PASS] Script-friendly extraction | [WARN] Complex link parsing |
| **Recommended For** | Working drafts, automation | Published documentation |

**Hybrid Approach** (Best Practice):
1. Use tag-only format during active development
2. Convert to hyperlinked format before documentation release
3. Run link validation after conversion: mcp_sdd `sdd_validate_links` --path docs/

**Cross-Document Hyperlink Patterns**:

| Reference Type | Pattern | Example |
|----------------|---------|---------|
| Same folder | Example only | `BRD.01.ae5c -> ./BRD-01_platform.md#brd010101` |
| Parent folder | Example only | `BRD.01.ae5c -> ../01_BRD/BRD-01_platform.md#brd010101` |
| Nested folder | Example only | `BRD.01.ae5c -> ../01_BRD/BRD-01_platform/BRD-01_platform.md#brd010101` |

**Cross-Document Links**:

| Link Type | Format | Example |
|-----------|--------|---------|
| Same type | Example only | `PRD-01 -> ./PRD-01_user_auth.md` |
| Cross-type | Example only | `PRD-02 -> ../02_PRD/PRD-02_knowledge_engine.md` |

### Document File Naming Pattern

**All Types** - monolithic documents:
- **Pattern**: `{TYPE}-{DOC_NUM}_{slug}.md`
- **Regex**: `^[A-Z]{2,5}-[0-9]{2,}_[a-z0-9_]+\.(md|yaml|feature)$`
- **Examples**: `BRD-01_platform_architecture.md`, `REQ-01_api_auth.md`, `TASKS-99_service.md`

#### Document Number Width Policy (Unified)

- Start with 2 digits and expand only as needed. Do not use unnecessary leading zeros beyond the active width of the current number.
- Correct examples: `BRD-01`, `BRD-99`, `BRD-102`, `BRD-999`, `BRD-1000`.
- Incorrect examples: `BRD-001`, `BRD-009` (extra leading zero not required by the number).
- This rule is unified across all document types: `BRD`, `PRD`, `EARS`, `BDD`, `ADR`, `SYS`, `REQ`, `CTR`, `SPEC`, `TASKS`.
- Element IDs MUST match filename digit width exactly (e.g., `BRD-06` ⇄ `BRD.06.xx.xx`; `PRD-22` ⇄ `PRD.22.xx.xx`).
- Exception: Reserved infrastructure artifacts use `-000` (e.g., `BRD-00_index.md`, `PRD-00_index.md`) by design.
- Note: Source code and unit test files follow coding standards for their languages and are excluded from this document ID filename policy.

#### Sequential vs Non-Sequential Element IDs

**Document Numbers**: MUST be sequential (01, 02, 03...). No gaps allowed in document numbering.

**Element IDs within Documents**: MAY be non-sequential. Gaps are permitted when:

| Reason | Example | Recommendation |
|--------|---------|----------------|
| Deprecation | `EARS.04.1d91` deprecated, `009` remains | Document deprecation in revision history |
| Historical removal | Requirements removed during review | Add note: "IDs 010-015 removed per review" |
| Logical grouping | IDs 001-050 for auth, 100-150 for data | Document grouping convention |
| Reserved ranges | IDs 900-999 reserved for future use | Document reservation in index |

**Policy Summary**:

| ID Type | Sequential Required | Gaps Allowed | Re-numbering |
|---------|---------------------|--------------|--------------|
| Document numbers (TYPE-NN) | YES | NO | Avoid (breaks references) |
| Element IDs (TYPE.NN.TT.SS) | NO | YES | Avoid (breaks traceability) |

**Re-numbering Risks**:

1. **Breaks traceability**: Downstream artifacts reference specific IDs
2. **Invalidates history**: Git history and reviews reference old IDs
3. **Requires impact analysis**: All referencing documents must be updated
4. **Coordination overhead**: Multiple team members may have local changes

**Recommendation**: Avoid gaps when possible, but accept them when they occur. Do NOT re-number existing IDs unless absolutely necessary (e.g., major document restructure with full impact analysis).

**Documentation Requirement**: When gaps exist, document the reason in:
- Document revision history
- Index file notes
- YAML frontmatter `custom_fields.id_gaps` (optional)

| Component | Format | Description |
|-----------|--------|-------------|
| `TYPE` | 2-5 uppercase letters | Document type (BRD, PRD, REQ, etc.) |
| `-` | Dash separator | Separates type from document number |
| `DOC_NUM` | 2+ digits | Document number (01, 99, 100, 1000) - grows as needed |
| `_` | Underscore separator | Separates ID from descriptive slug |
| `slug` | lowercase_snake_case | Human-readable description |

### Document Size Limits

| Token Count | Action | Rationale |
|-------------|--------|-----------|
| Up to 50,000 tokens | Keep as single monolithic file | Standard for all AI tools |
| Exceeds 50,000 tokens | Create a new document of the same type with its own scope | Maintain tool compatibility |

Cross-Reference Link Format (MANDATORY)
- Universal rule: use markdown links for all references.
- Use atomic (DOC_NUM) patterns for document references.
- DOC_NUM: Variable-length, starts at 2 digits (01, 99, 100, 1000).
- Formats:
  - REQ in ADR: `[REQ-DOC_NUM](../07_REQ/.../REQ-DOC_NUM_{slug}.md#REQ-DOC_NUM)`
  - ADR in BDD: `@adr:[ADR-DOC_NUM](../05_ADR/ADR-DOC_NUM_{slug}.md#ADR-DOC_NUM)`
  - REQ in BDD: `@requirement:[REQ-DOC_NUM](../07_REQ/.../REQ-DOC_NUM_{slug}.md#REQ-DOC_NUM)`
  - 07_REQ/ADR in CTR:
    - `[REQ-DOC_NUM](../07_REQ/.../REQ-DOC_NUM_{slug}.md#REQ-DOC_NUM)` in Traceability section
    - `[ADR-DOC_NUM](../05_ADR/ADR-DOC_NUM_{slug}.md#ADR-DOC_NUM)` in Traceability section
  - CTR in SPEC:
    - `contract_ref: CTR-DOC_NUM_{slug}` (YAML field)
    - `[CTR-DOC_NUM](../../08_CTR/CTR-DOC_NUM_{slug}.md#CTR-DOC_NUM)` (markdown reference)
    - `[CTR-DOC_NUM Schema](../../08_CTR/CTR-DOC_NUM_{slug}.yaml)` (schema reference)
  - 07_REQ/ADR in SPEC:
    - `requirements_source:
      - "[REQ-DOC_NUM](../../07_REQ/.../REQ-DOC_NUM_{slug}.md#REQ-DOC_NUM)"`
    - `architecture:
      - "[ADR-DOC_NUM](../../05_ADR/ADR-DOC_NUM_{slug}.md#ADR-DOC_NUM)"`
  - BDD in SPEC verification:
    - `verification:
<!-- VALIDATOR:IGNORE-LINKS-START -->
      - BDD: "`04_BDD/BDD-DOC_NUM_{slug}.yaml`"`
<!-- VALIDATOR:IGNORE-LINKS-END -->
  - BRD in BRD:
    - `[BRD-DOC_NUM](BRD-DOC_NUM_{slug}.md)` (same directory)
  - BRD in other docs:
    - `[BRD-DOC_NUM](../01_BRD/BRD-DOC_NUM_{slug}.md#BRD-DOC_NUM)`

Traceability Requirements

- ADR: list addressed REQ(s) via markdown links.
- CTR: link upstream 07_REQ/ADR (Traceability section), downstream 09_SPEC/Code (Traceability section).
- BDD: include `@requirement` (mandatory) and `@adr` (when applicable).
- SPEC: include `requirements_source` (07_REQ/EARS), `architecture` (ADR), `contract_ref` (CTR if applicable), `verification` (BDD); all as markdown links.
- TASKS: include `@spec` (mandatory - which SPEC being implemented).
- BRD: link downstream 07_REQ/CTR (if applicable), related BRD sub-documents via markdown links.
- Code: reference SPEC, CTR (if contract implementation), and TASKS in docstrings or header comments using relative paths.


Validation Rules & Aids
- Run before commit:
  - mcp_sdd `sdd_validate` (requirement ID validation)
  - Optional: mcp_sdd `sdd_validate_links` (broken references)
  - Optional: mcp_sdd `sdd_validate` (matrix compliance)
- Quick regexes (conceptual):
  - **Unified Element ID** (all document types): `^[A-Z]{2,5}\.[0-9]{2,9}\.[0-9]{2,9}\.[0-9]{2,9}$`
  - **Internal Heading**: `^###\s+[A-Z]{2,5}\.[0-9]{2,9}\.[0-9]{2,9}\.[0-9]{2,9}:\s+.+$`
  - **Cross-Reference Tag**: `^@[a-z]+:\s+[A-Z]{2,5}\.[0-9]{2,9}\.[0-9]{2,9}\.[0-9]{2,9}$`
- Document filename regexes (atomic documents - dash format for files):
  - REQ H1 ID: `^#\sREQ-\d{2,}:.+$`
  - REQ filename: `REQ-\d{2,}_.+\.md$`
  - ADR H1 ID: `^#\sADR-\d{2,}:.+$`
  - ADR filename: `ADR-\d{2,}_.+\.md$`
  - BDD filename: `BDD-\d{2,}_.+\.yaml$`
  - BDD tag: `^@requirement:\[REQ-\d{2,}\]\(.+\.md#REQ-\d{2,}\)$`
  - SPEC id: `^[a-z][a-z0-9_]*[a-z0-9]$`.
  - SPEC filename: `SPEC-\d{2,}_.+\.ya?ml$`
  - CTR H1 ID: `^#\sCTR-\d{2,}:.+$`
  - CTR filename: `CTR-\d{2,}_.+\.(md|yaml)$`
  - TASKS H1 ID: `^#\sTASKS-\d{2,}:.+$`
  - TASKS filename: `TASKS-\d{2,}_.+\.md$`
  - BRD H1 ID: `^#\sBRD-\d{2,}:.+$`
  - BRD filename: `BRD-\d{2,}_.+\.md$`
  - PRD H1 ID: `^#\sPRD-\d{2,}:.+$`
  - PRD filename: `PRD-\d{2,}_.+\.md$`
  - SYS H1 ID: `^#\sSYS-\d{2,}:.+$`
  - SYS filename: `SYS-\d{2,}_.+\.md$`
  - EARS H1 ID: `^#\sEARS-\d{2,}:.+$`
  - EARS filename: `EARS-\d{2,}_.+\.md$`
  - REF H1 ID: `^#\s[A-Z]{2,5}-REF-\d{2,}:.+$`
  - REF filename: `[A-Z]{2,5}-REF-\d{2,}_.+\.md$`

Examples (ai_dev_ssd_flow) - Monolithic Documents (DOC_NUM)
- **Standard Types**:
  - SYS: `06_SYS/SYS-03_position_risk_limits.md` (H1: `# SYS-03: resource Risk Limits`)
  - EARS: `03_EARS/EARS-03_resource_limit_enforcement.md` (H1: `# EARS-03: [RESOURCE_LIMIT - e.g., request quota, concurrent sessions] Enforcement`)
  - REQ: `07_REQ/risk/lim/REQ-03_resource_limit_enforcement.md` (H1: `# REQ-03: [RESOURCE_LIMIT - e.g., request quota, concurrent sessions] Enforcement`)
- CTR: `08_CTR/CTR-01_position_risk_validation.md` + `CTR-01_position_risk_validation.yaml` (H1: `# CTR-01: resource Risk Validation Contract`, YAML: `contract_id: position_risk_validation`)
- SPEC: `09_SPEC/SPEC-03_resource_limit_service.yaml` (id: `resource_limit_service`)
- TASKS: `11_TASKS/TASKS-03_resource_limit_service.md` (H1: `# TASKS-03: [RESOURCE_LIMIT - e.g., request quota, concurrent sessions] Service Implementation`)


Component Abbreviations (examples)
- SVC (Service), CL (Client), SRV (Server), GW (Gateway), AGG (Aggregator), MGR (Manager), CTRL (Controller), ADPT (Adapter), REPO (Repository), PROC (Processor), VAL (Validator), ORCH (Orchestrator), PROV (Provider)
- IB ([EXTERNAL_SERVICE - e.g., Payment Gateway, CRM System]), AV ([EXTERNAL_DATA_PROVIDER - e.g., Weather API, item Data API]), MKT (Market), ORD (Order), EXEC (Execution), POS (resource), LIM (Limit), RISK (Risk), ACCT (Account), PFOL (resource collection), CFG (Configuration), AUTH (Authentication), AUTHZ (Authorization), REDIS, PUBSUB, BQ (BigQuery), CSQL (Cloud SQL), GCR (Cloud Run), GSM (Secrets Manager)

BDD Tag Examples
```gherkin
# Document-level references (dash format for file links)
@requirement:[REQ-03](../07_REQ/risk/lim/REQ-03_resource_limit_enforcement.md#REQ-03)
@adr:[ADR-33](../05_ADR/ADR-33_risk_enforcement.md#ADR-33)

# Internal element references (dot format for element IDs)
# Format: TYPE.DOC_NUM.ELEM_TYPE.SEQ
# DOC_NUM in element ID MUST match filename digit count
@brd: BRD.01.92d8    # BRD doc 01, Functional Requirement #5
@brd: BRD.01.fe7c    # BRD doc 01, Constraint #2
@prd: PRD.02.1a5d    # PRD doc 02, User Story #15
@adr: ADR-03          # ADR doc 03 (dash notation for documents)
```

Anchors & Linking
- Use ID anchors where applicable (e.g., `#REQ-01`, `#ADR-32`).
- Prefer stable ID anchors over line anchors. If a line anchor (e.g., `#L28`) is used, revalidate after edits.

Local Clarifications (ai_dev_ssd_flow)
- Variable-length numeric filename prefixes (DOC_NUM) are required here for readability and ordering; do not rename to match other directories' styles.
- DOC_NUM starts at 2 digits (01) and grows as needed (100, 1000).
- SPEC filenames keep `SPEC-DOC_NUM_{slug}.yaml`; the YAML `id:` is the stable spec identifier used by tags and prose.
- Keep tag headers at top of files (first non-empty lines) for machine-readability as shown in TRACEABILITY.md.
- Documents are monolithic up to 50,000 tokens. If a document exceeds this limit, create a new document of the same type with its own scope.

---

## Unified Element ID Format (MANDATORY)

The SDD framework uses a **single unified format** for all internal element references across all document types. This format is optimized for AI-first workflows where AI assistants write documentation and humans query AI about specific elements.

### Format Specification

```
{DOC_TYPE}.{DOC_NUM}.{ELEM_TYPE}.{SEQ}
```

**Validation Regex**: `^[A-Z]{2,5}\.[0-9]{2,9}\.[0-9]{2,9}\.[0-9]{2,9}$`

| Segment | Min Digits | Max Digits | Start Value | Purpose |
|---------|------------|------------|-------------|---------|
| DOC_TYPE | 2 chars | 5 chars | - | Document type (BRD, PRD, REQ, SPEC, etc.) |
| DOC_NUM | 2 | 9 | 01 | Document instance number |
| ELEM_TYPE | 2 | 9 | 01 | Element category code (see table below) |
| SEQ | 2 | 9 | 01 | Sequential within element type |

### Standardized Element Type Codes

> [WARN] **REMOVED PATTERNS**: The following formats are INVALID:
> - `AC-XXX` → Use `TYPE.NN.06.SS` (Acceptance Criteria)
> - `FR-XXX` → Use `TYPE.NN.01.SS` (Functional Requirement)
> - `BC-XXX` → Use `TYPE.NN.03.SS` (Constraint)
> - `BA-XXX` → Use `TYPE.NN.04.SS` (Assumption)
> - `QA-XXX` → Use `TYPE.NN.02.SS` (Quality Attribute)
> - `BO-XXX` → Use `TYPE.NN.23.SS` (Business Objective)
> - `RISK-XXX` → Use `TYPE.NN.07.SS` (Risk)
> - `METRIC-XXX` → Use `TYPE.NN.08.SS` (Metric)
>
> See full migration table in Removed Patterns section below.

Consistent across ALL document types:

| Code | Element Type | Common In |
|------|--------------|-----------|
| 01 | Functional Requirement | BRD, PRD, SYS, REQ |
| 02 | Quality Attribute | BRD, PRD, SYS |
| 03 | Constraint | BRD, PRD |
| 04 | Assumption | BRD, PRD |
| 05 | Dependency | BRD, PRD, REQ |
| 06 | Acceptance Criteria | BRD, PRD, REQ |
| 07 | Risk | BRD, PRD |
| 08 | Metric | BRD, PRD |
| 09 | User Story | PRD, BRD |
| 10 | Decision | ADR, BRD |
| 11 | Use Case | PRD, SYS |
| 12 | Alternative | ADR |
| 13 | Consequence | ADR |
| 14 | Test Scenario | BDD |
| 15 | Step | BDD, SPEC |
| 16 | Interface | SPEC, CTR |
| 17 | Data Model | SPEC, CTR |
| 18 | Task | TASKS |
| 19 | Command | TASKS (Section 4) |
| 20 | Contract Clause | CTR |
| 21 | Validation Rule | SPEC |
| 22 | Feature Item | BRD, PRD |
| 23 | Business Objective | BRD |
| 24 | Stakeholder Need | BRD, PRD |
| 25 | EARS Statement | EARS |
| 26 | System Requirement | SYS |
| 27 | Atomic Requirement | REQ |
| 28 | Specification Element | SPEC |
| 29 | Task Breakdown | TASKS |
| 30 | Task Item | TASKS |
| 31 | Plan Step | TASKS (Section 4) |
| 32 | Architecture Topic (Legacy Compatibility) | BRD |
| 33-39 | Reserved for future use | - |
| 40 | Unit Test | TSPEC (UTEST) |
| 41 | Integration Test | TSPEC (ITEST) |
| 42 | Smoke Test | TSPEC (STEST) |
| 43 | Functional Test | TSPEC (FTEST) |
| 44 | Performance Test | TSPEC (PTEST) - Reserved |
| 45 | Security Test | TSPEC (SECTEST) - Reserved |
| 46-49 | Reserved for future use | - |
| 50 | Code Specification | SPEC (CSPEC) - code deliverables |
| 51 | Documentation Specification | SPEC (DSPEC) - document deliverables |
| 52 | UX Specification | SPEC (UXSPEC) - ux deliverables |
| 53 | Risk Specification | SPEC (RISKSPEC) - risk deliverables |
| 54 | Process Specification | SPEC (PROCSPEC) - process deliverables |
| 55-58 | DSPEC Element Types | DSPEC internal elements |
| 60-63 | UXSPEC Element Types | UXSPEC internal elements |
| 65-68 | RISKSPEC Element Types | RISKSPEC internal elements |
| 70-73 | PROCSPEC Element Types | PROCSPEC internal elements |
| 74-90 | Reserved for future use | - |
| 91 | Performance Requirement | BRD (Section 7.3), PRD, SYS |
| 92 | Reliability Requirement | BRD (Section 7.4), PRD, SYS |
| 93 | Availability Requirement | BRD, PRD, SYS (reserved) |
| 94 | Scalability Requirement | BRD (Section 7.5), PRD, SYS |
| 95 | Usability Requirement | BRD, PRD, SYS (reserved) |
| 96 | Security Requirement | BRD (Section 7.6), PRD, SYS |
| 97 | Compatibility Requirement | BRD, PRD, SYS (reserved) |
| 98 | Observability Requirement | BRD (Section 7.7), PRD, SYS |
| 99 | Maintainability Requirement | BRD (Section 7.8), PRD, SYS |

**Note**: Codes 91-99 are Quality Attribute (QA) subcategories that provide self-documenting element IDs for traceability. Code 02 (generic Quality Attribute) remains valid for legacy documents and overview sections.

### Examples

| ID | Length | Meaning |
|----|--------|---------|
| `BRD.01.ae5c` | 12 | BRD #1, Functional Requirement #1 |
| `BRD.01.e9cc` | 12 | BRD #1, Constraint #5 |
| `BRD.02.dc6a` | 12 | BRD #2, Security Requirement #3 |
| `BRD.02.d4c1` | 12 | BRD #2, Performance Requirement #1 |
| `PRD.02.3ca9` | 12 | PRD #2, User Story #42 |
| `ADR.01.e354` | 12 | ADR #1, Decision #1 |
| `TASKS.01.f680` | 15 | TASKS #1, Task #128 |
| `TASKS.01.46b8` | 14 | TASKS #1, Task Breakdown #3 |
| `BRD.99.9999` | 15 | BRD #99, Functional Requirement #9999 |
| `SPEC.01.588f` | 13 | SPEC #1, Interface #3 |
| `BRD.01.88b9` | 12 | BRD #1, Architecture Topic #1 (Legacy compatibility) |

### Canonical Source-of-Truth and Compatibility Policy

**Canonical authority for element type codes**: This table in `ID_NAMING_STANDARDS.md` is the authoritative source for:
- Valid element type codes per artifact type
- Element type semantics (`05=Dependency`, `07=Risk`, `10=Decision`)
- Per-artifact usage restrictions (for example, `23` is BRD-only)

**Conflict resolution order**:
1. `ID_NAMING_STANDARDS.md` element type table (this section) for code semantics and per-type allowance
2. Artifact schema files for document structure and required sections
3. Validator scripts and pre-commit hooks (must implement rules 1 and 2)

**Compatibility policy (transitional)**:
- `BRD.NN.10.SS` is canonical for BRD Section 7.2 architecture decision topics.
- `BRD.NN.32.SS` remains accepted for legacy documents and migration continuity.
- `PRD.NN.23.SS` (Business Objective) is non-canonical and MUST be migrated to BRD ownership over time.

### Growth Pattern

IDs automatically expand as needed without schema changes:

```text
BRD.01.ae5c      → Start (minimum)
BRD.01.90db      → Approaching 2-digit limit
BRD.01.783a     → Auto-expand to 3 digits
BRD.01.9999    → Still valid (4 digits)
BRD.99.999999  → Maximum practical scale
```

### Cross-Reference Tag Format

| Tag Format | Example | Meaning |
|------------|---------|---------|
| `@brd: BRD.01.ae5c` | BRD doc 1, FR #1 | Functional requirement reference |
| `@prd: PRD.02.529a` | PRD doc 2, User Story #5 | User story reference |
| `@adr: ADR.03.257b` | ADR doc 3, Decision #1 | Architecture decision reference |
| `@spec: SPEC.01.eeeb` | SPEC doc 1, Interface #2 | Interface specification reference |

### AI-First Design Rationale

This format is optimized for AI-assisted documentation workflows:

1. **Token efficiency**: 12 chars minimum vs 15+ for human-readable formats
2. **AI translation**: Human asks "what is BRD.01.e9cc?", AI responds "Constraint #5: Budget limit $50K"
3. **Single regex pattern**: `[A-Z]{2,5}\.[0-9]{2,9}\.[0-9]{2,9}\.[0-9]{2,9}` validates all types
4. **Zero capacity planning**: Grows automatically without range management
5. **Consistent parsing**: Same pattern across all 12+ document types

---

## Internal Feature Heading Format (MANDATORY)

**Purpose**: All internal feature/requirement headings within documents MUST use the unified 4-segment format for:

1. Direct searchability across all documents
2. Consistency between internal headings and external cross-references
3. Element type identification without lookup

**Internal Heading Pattern**:

| Document Type | Heading Format | Example |
|---------------|----------------|---------|
| BRD | `### BRD.NN.TT.SS: Name` | `### BRD.01.ae5c: Market Data Feed` |
| PRD | `### PRD.NN.TT.SS: Name` | `### PRD.02.8dcf: User Dashboard` |
| EARS | `### EARS.NN.TT.SS: Name` | `### EARS.01.6c50: Data Validation` |
| BDD | `### BDD.NN.TT.SS: Name` | `### BDD.01.c284: Login Scenario` |
| SYS | `### SYS.NN.TT.SS: Name` | `### SYS.01.b4d5: API Gateway` |
| ADR | `### ADR.NN.TT.SS: Name` | `### ADR.01.e354: Database Selection` |

**Format Breakdown**:

| Component | Description | Example |
|-----------|-------------|---------|
| `TYPE` | Document type in SDD framework | `BRD`, `PRD`, `ADR`, `SPEC` |
| `.NN` | Document number (2+ digits) | `.01` = document 1 |
| `.TT` | Element type code (see table above) | `.01` = Functional Requirement |
| `.SS` | Sequential within element type | `.01` = first item of this type |

**Example**: `BRD.01.e9cc` = BRD document 01, Constraint (type 03), item #5

**Validation Regex**:

```python
INTERNAL_HEADING_PATTERN = r'^###\s+[A-Z]{2,5}\.[0-9]{2,9}\.[0-9]{2,9}\.[0-9]{2,9}:\s+.+$'
# Matches: ### BRD.01.ae5c: Feature Name
```

**REMOVED Patterns (v3.0 - No Backward Compatibility)**:

The following patterns are **REMOVED** and MUST NOT be used:

| Removed Pattern | Previous Usage | Migration Path |
|-----------------|----------------|----------------|
| `FR-XXX` | BRD feature headings | Use `### BRD.NN.01.SS: Feature` |
| `BC-XXX` | Business Constraints | Use `### BRD.NN.03.SS: Constraint` |
| `BA-XXX` | Business Assumptions | Use `### BRD.NN.04.SS: Assumption` |
| `QA-XXX` | Quality Attributes | Use `### BRD.NN.02.SS: Quality` |
| `BO-XXX` | Business Objectives | Use `### BRD.NN.23.SS: Objective` |
| `AC-XXX` | Acceptance Criteria | Use `### BRD.NN.06.SS: Criteria` |
| `RISK-XXX` | Risk Items | Use `### BRD.NN.07.SS: Risk` |
| `METRIC-XXX` | Success Metrics | Use `### BRD.NN.08.SS: Metric` |
| `TYPE.NN.TT` | 3-segment format | Use `TYPE.NN.TT.SS` (4-segment) |
| `Feature F-XXX` | PRD feature headings | Use `### PRD.NN.09.SS: User Story` |

**Migration Examples**:

| Before (REMOVED) | After (MANDATORY) |
|------------------|-------------------|
| `### BRD.017.001: Feature` | `### BRD.17.a381: Feature` |
| `### Feature F-01: User Dashboard` | `### PRD.01.1dbc: User Dashboard` |

---

## BRD Section-to-Element-Code Mapping

**Purpose**: Define which element type codes are valid for each BRD section. This mapping enables validators to enforce semantic consistency between section content and element IDs.

**Scope**: This mapping is **BRD-specific**. Each document type has a unique section structure requiring its own Section-to-Code mapping:

| Document Type | Section Structure | Mapping Status |
|---------------|-------------------|----------------|
| **BRD** | 18 sections (Introduction, Business Objectives, Stakeholders, etc.) | Defined below |
| **PRD** | Product-focused sections (Features, User Stories, Metrics) | Future: PRD validator |
| **ADR** | Decision records (Context, Decision, Consequences) | Uses codes 10, 32 |
| **EARS** | EARS template sections (Requirement categories) | Future: EARS validator |

> **Note**: Element type codes (01-99) are **universal** across all document types. Only the section-to-code enforcement logic is document-specific.

| BRD Section | Section Title | Valid Codes | Canonical Code | Notes |
|-------------|---------------|-------------|----------------|-------|
| 2 | Business Objectives | 23 | 23 | Business Objective |
| 3 | Project Scope | 22 | 22 | Feature Item |
| 4 | Stakeholders | 24 | 24 | Stakeholder Need |
| 5 | User Stories | 09 | 09 | User Story |
| 6 | Functional Requirements | 01, 06 | 01 | FR + embedded Acceptance Criteria |
| 7.1 | Quality Attributes (Overview) | 02 | 02 | Generic QA |
| 7.2 | Architecture Decision Requirements | 10, 32 | 10 | Decision (32 legacy) |
| 7.3 | Performance Requirements | 02, 05, 91 | 91 | Performance |
| 7.4 | Reliability Requirements | 02, 05, 92 | 92 | Reliability |
| 7.5 | Scalability Requirements | 02, 05, 94 | 94 | Scalability |
| 7.6 | Security Requirements | 02, 05, 96 | 96 | Security |
| 7.7 | Observability Requirements | 02, 05, 98 | 98 | Observability |
| 7.8 | Maintainability Requirements | 02, 05, 99 | 99 | Maintainability |
| 8.1 | Constraints | 03 | 03 | Constraint |
| 8.2 | Assumptions | 04 | 04 | Assumption |
| 9 | Acceptance Criteria | 06 | 06 | Acceptance Criteria |
| 10 | Business Risk Management | 05, 07 | 07 | Risk (05 legacy) |

**Validation Rules**:
- Elements MUST use a code from the "Valid Codes" column for their section
- New documents SHOULD use the "Canonical Code" where available
- Legacy codes (02, 05, 32) are tolerated for backward compatibility but should not be used in new documents
- Validators enforce `GATE-W008` warnings for non-canonical code usage

**Traceability Benefit**: Using hierarchical codes 91-99 enables pattern-based search across documents (e.g., `grep -r "\.96\."` finds all Security requirements).

---

## Architecture Decision Topic Subsection Format

**Purpose**: Document Section 7.2 "Architecture Decision Requirements" contains numbered subsections identifying architectural topics requiring formal ADR decisions. These use the standard 4-segment format with element type code `10` (Decision).

**Subsection ID Pattern**: `{DOC_TYPE}.NN.10.SS` (using Decision element type)

**Compatibility Note**:
- Canonical: `BRD.NN.10.SS` for Section 7.2 architecture decision topics.
- Backward-compatible legacy: `BRD.NN.32.SS` is still valid for existing content, but new content SHOULD use `.10`.

| Component | Description | Example |
|-----------|-------------|---------|
| `{DOC_TYPE}` | Document type (BRD, PRD, etc.) | `BRD` |
| `.NN` | Document number (2+ digits) | `.01` = BRD-01 |
| `.10` | Element type code for Decision | `.10` = Decision type |
| `.SS` | Sequential topic number | `.03` = third topic |

**Heading Format**:

```markdown
#### BRD.01.fb92: [Topic Name]

**Business Driver**: [Why this decision matters to business - reference upstream requirements]
**Business Constraints**:
- [Non-negotiable business rule 1]
- [Non-negotiable business rule 2]
**PRD Requirements**: [What PRD must elaborate for THIS topic - technical options, evaluation criteria, performance benchmarks]
```

**Note**: Heading level varies by context (H3-H5) depending on document structure. The pattern uses H4 (`####`) in BRD Section 7.2 as subsections.

**Examples**:

| Document | Topic # | Full ID | Meaning |
|----------|---------|---------|---------|
| BRD-01 | 3 | `BRD.01.fb92` | Third architecture decision topic in BRD-01 |
| BRD-17 | 1 | `BRD.17.9229` | First architecture decision topic in BRD-17 |
| BRD-03 | 12 | `BRD.03.9e3f` | Twelfth architecture decision topic in BRD-03 |

**Content Rules (Business-Only)**:

| Include in Section 7.2 | Exclude from Section 7.2 |
|------------------------|--------------------------|
| Business objectives | Technology options |
| Regulatory constraints | Performance specifications |
| Non-negotiable business rules | Evaluation criteria |
| Business impact statements | Implementation patterns |

**Cross-Reference Flow**:

```text
BRD Section 7.2 (BRD.NN.10.SS)  →  PRD Section 18           →  ADR
Business drivers/constraints        Technical options/criteria    Final decision
```

**PRD Reference**: PRD Section 18 elaborates each BRD Section 7.2 topic with:

- `**Upstream**: BRD.NN.10.SS` - Reference to originating BRD topic
- Technical options and evaluation criteria
- `**ADR Requirements**: [guidance]` - What ADR must decide for this topic

**ADR Reference**: ADR Section 4.1 includes:

- `**Originating Topic**: BRD.NN.10.SS - [Topic Name]`
- Business driver and constraints from BRD
- Technical options evaluated from PRD

**Validation Regex**:

```python
ARCHITECTURE_TOPIC_PATTERN = r'^#{3,5}\s+[A-Z]{2,5}\.[0-9]{2,9}\.[0-9]{2,9}\.[0-9]{2,9}:\s+.+$'
# Matches: ### BRD.01.fb92: ... OR #### PRD.17.0416: ...
# Heading level (H3-H5) varies by document section context
```

---

## Complete Tag Reference

For the complete list of valid traceability tags, see [TRACEABILITY.md - Complete Tag Reference](./TRACEABILITY.md#complete-tag-reference).

**Quick Reference:**

- **Document Type Tags**: `@brd`, `@prd`, `@ears`, `@bdd`, `@adr`, `@sys`, `@req`, `@ctr`, `@spec`, `@tasks`
- **Non-Document Tags**: `@test`, `@code`, `@threshold`, `@entity`, `@priority`, `@component`, `@supersedes`
- **Same-Type Tags**: `@related-{type}`, `@depends-{type}`
- **Invalid Tags**: `@nfr:`, `@fr:`, `@contract:`, `@tests:` (deprecated, do NOT use)

---

## Validation Rules Reference

ID naming standards are enforced by automated validators. For the complete error code registry and validation rules, see [VALIDATION_STANDARDS.md](./VALIDATION_STANDARDS.md).

### Quick Error Code Reference

| Code | Severity | Issue | Resolution |
|------|----------|-------|------------|
| IDPAT-E001 | Error | Inconsistent document ID format | Use `TYPE-NN+` (2+ digits) |
| IDPAT-E002 | Error | Inconsistent element ID format | Use `TYPE.NN.TT.SS` format |
| IDPAT-E003 | Error | Mixed ID notation | Normalize to dot notation |
| IDPAT-W001 | Warning | Legacy ID format detected | Update to unified format |
| ELEM-E001 | Error | Undefined element type code | Use valid code from table (01-31) |
| ELEM-W001 | Warning | Undocumented custom code | Document custom codes (50-99) |
| FWDREF-E001 | Error | Downstream ID in upstream doc | Remove specific ID, use descriptive text |
| FWDREF-E002 | Error | Non-existent downstream reference | Create document or remove reference |

### Common Violations and Fixes

**Mixed ID Notation** (IDPAT-E003):
```markdown
[FAIL] Incorrect: BRD-01.02, PRD-001.AC.05
 Correct: BRD.01.7499, PRD.001.8ab9
```

**Legacy ID Format** (IDPAT-W001):
```markdown
[FAIL] Legacy: FR-001, AC-005, NFR-003
 Unified: REQ.01.6c3d, REQ.01.1678, SYS.01.0212
```

**Forward Reference** (FWDREF-E001):
```markdown
[FAIL] In PRD: "See ADR-01 for database decision"
 In PRD: "Architecture decisions required for: database selection"
```

### Running Validators

```bash
# Validate ID patterns
mcp_sdd `sdd_validate` (requirement ID validation)

# Validate forward references
mcp_sdd `sdd_validate` (forward reference validation)

# Run all validators
mcp_sdd `sdd_validate` --all
```

---

## Checklist

- H1 titles contain IDs for 02_PRD/06_SYS/03_EARS/07_REQ/05_ADR/08_CTR/11_TASKS/BRD where applicable (use `TYPE-DOC_NUM` format).
- BDD tags are markdown links with valid relative paths and anchors.
- Spec files named `SPEC-DOC_NUM_{slug}.yaml`; inside, `id:` is snake_case and used by `@spec` tags; `requirements_source`/`architecture`/`verification` links resolve.
- All document types follow universal numbering pattern: DOC_NUM = 2+ digits (01-99, 100-999, 1000+).
- Element ID DOC_NUM MUST match filename digit count exactly.
- All documents are monolithic (single self-contained file) up to 50,000 tokens. If a document exceeds 50,000 tokens, create a new document of the same type with its own scope.
- Internal element IDs use unified 4-segment format: `TYPE.DOC_NUM.TT.SS`.
- Run mcp_sdd `sdd_validate` (requirement ID validation) and fix any violations before committing.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 3.0 | 2026-03-30 | DEPRECATED section-based file splitting; all documents are monolithic up to 50,000 tokens; removed section file naming patterns, section frontmatter, section templates, split_type metadata; updated ai_dev_flow references to ai_dev_ssd_flow; updated template references to unified YAML format |
| 2.2 | 2026-03-11 | Added QA subcategory codes 91-99 (Performance=91, Reliability=92, Scalability=94, Security=96, Observability=98, Maintainability=99); Added BRD Section-to-Element-Code Mapping table with scope clarification (BRD-specific, other document types need own mappings); Updated reserved range from 74-99 to 74-90 |
| 2.1 | 2026-02-28 | Initial published version with unified element ID format |