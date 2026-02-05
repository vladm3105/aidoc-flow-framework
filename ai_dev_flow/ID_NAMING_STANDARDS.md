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
  version: "1.0"
  scope: documentation-only
---

# Document ID & Tagging Standards — ai_dev_flow

Status: Authoritative for this `ai_dev_flow` example set. These rules reflect the naming and linking already used here and supersede repo-wide norms within this directory (do not change existing files to match other guides).

Purpose
- Provide a single, practical guide for IDs, tags, links, file layout, and validation within this example.
- Eliminate duplication while preserving mandatory rules and quick-reference tips.

## Scope Clarification: Documentation Only

**IMPORTANT**: This naming standard applies ONLY to Specification-Driven Development (SDD) **documentation artifacts**. It does NOT apply to source code files.

### ✅ Apply ID_NAMING_STANDARDS To:
- Documentation files in `docs/` directories:
  - `01_BRD/` - Business Requirements Documents
  - `02_PRD/` - Product Requirements Documents
  - `03_EARS/` - EARS Requirements
  - `04_BDD/` - Feature files (`.feature` format only)
  - `05_ADR/` - Architecture Decision Records
  - `06_SYS/` - System Requirements
  - `07_REQ/` - Requirements
  - `08_CTR/` - API Contracts (CTR)
  - `09_SPEC/` - Technical Specifications (YAML)
  - `10_TSPEC/` - Test Specifications (UTEST, ITEST, STEST, FTEST)
  - `11_TASKS/` - AI Task Lists
  - `REF/` - Reference Documents (supplementary, non-workflow documentation)


### ❌ Do NOT Apply ID_NAMING_STANDARDS To:
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

### Exception: BDD Feature Files
BDD test scenarios in `.feature` files (Gherkin format) located in `tests/bdd/` or similar directories **SHOULD** follow ID_NAMING_STANDARDS:

```
tests/bdd/gateway/BDD-01_connection_management.feature
tests/bdd/gateway/BDD-02_error_handling.feature
```

---

## ID Notation Clarification (CRITICAL)

The SDD framework uses **two distinct notations** that serve different purposes. Understanding this distinction is essential:

| Purpose | Notation | Format | Example | References |
|---------|----------|--------|---------|------------|
| **Document Reference** | Dash | `TYPE-NN` | `ADR-01`, `BRD-07` | Whole document/file |
| **Element Reference** | Dot | `TYPE.NN.TT.SS` | `BRD.07.01.01` | Specific element within document |

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
- `BRD.07.01.01` → Functional Requirement #1 inside BRD-07
- `PRD.02.09.05` → User Story #5 inside PRD-02
- `EARS.04.25.08` → EARS Requirement #8 inside EARS-04

**Tag Usage**: `@brd: BRD.07.01.01`, `@prd: PRD.02.09.05`

### Which Artifacts Use Which Notation?

| Notation | Document Types | Rationale |
|----------|---------------|-----------|
| **Dash** (Document-level) | ADR, SPEC, CTR | Referenced as complete units |
| **Dot** (Element-level) | BRD, PRD, EARS, BDD, SYS, REQ, TASKS | Contain multiple numbered elements |

### Common Mistakes to Avoid

| Incorrect | Correct | Explanation |
|-----------|---------|-------------|
| `@brd: BRD-07` | `@brd: BRD.07.01.01` | BRD uses element notation (dot) |
| `@adr: ADR.33.10.01` | `@adr: ADR-33` | ADR uses document notation (dash) |
| `BRD.7.01.01` | `BRD.07.01.01` | Element DOC_NUM must match filename digits |

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

Note on paths: Examples may show a top-level `docs/` prefix; in this ai_dev_flow directory, type folders live at the ai_dev_flow root (e.g., `01_BRD/`, `02_PRD/`, `05_ADR/`). Adjust relative links accordingly.

## General Utility Documents (`{DOC_TYPE}-00_*`)

Definition and Purpose
- `{DOC_TYPE}-000` is reserved across all artifact types to group general-purpose, cross-project, or utility documents that are not directly tied to a specific numbered project document.
- Typical uses: indexes, templates, traceability matrix templates, validation checklists, and reference guides.

Format
- Pattern: `{DOC_TYPE}-00_{slug}.{ext}` (e.g., `REQ-00_TRACEABILITY_MATRIX-TEMPLATE.md`, `TASKS-00_index.md`).
- These do not participate in the sequential DOC_NUM series and are globally recognizable as general/utility artifacts.

## Default Directory Model (All Types)

**Unified Directory Model (All Types)**:

| Structure | Trigger | Format |
|-----------|---------|--------|
| **Flat** (Atomic) | < 20,000 tokens AND 1 file | `{TYPE}/{TYPE}-{ID}_{Slug}.{ext}` |
| **Nested** (Folder) | > 20,000 tokens OR > 1 file | `{TYPE}/{TYPE}-{ID}_{Slug}/{TYPE}-{ID}-{Seq}_{Slug}.{ext}` |

**Rule**: If a document crosses the threshold, **MOVE IT** to a folder. Do not mix patterns for the same ID.

### Flat Structure (Monolithic Documents)

- **Format**: `{TYPE}/{TYPE}-DOC_NUM_{slug}.md` (no folder, no section suffix)
- **Use for**: MVP documents, single-file documents under 25KB, streamlined artifacts
- **H1 Title**: `# TYPE-DOC_NUM: Document Title` (no `.0` suffix)
- **Examples**:
  - `docs/01_BRD/BRD-01_platform_architecture.md`
  - `docs/02_PRD/PRD-02_user_authentication.md`
  - `docs/05_ADR/ADR-15_database_selection.md`
- **Rule**: Do NOT create a folder for monolithic files. The file lives directly in the type directory.

### Nested Structure (Section-Based Documents)

- **Format**: `{TYPE}/{TYPE}-DOC_NUM_{slug}/` folder containing section files
- **Use for**: Large documents (>25KB), documents requiring splitting, complex multi-section artifacts
- **Section files**: `TYPE-DOC_NUM.S_{section_type}.md` where S = section number (0, 1, 2, ...)
- **H1 Title**: `# TYPE-DOC_NUM.S: Section Title` (includes `.S` suffix matching filename)
- **Folder slug MUST match** the index file slug
- **Examples**:
  - `docs/01_BRD/BRD-03_complex_system/BRD-03.0_index.md`
  - `docs/01_BRD/BRD-03_complex_system/BRD-03.1_executive_summary.md`
  - `docs/01_BRD/BRD-03_complex_system/BRD-03.2_requirements.md`

### Type-Specific Exceptions

- **BDD**: Uses nested per-suite folders with section-based `.feature` files at `04_BDD/BDD-DOC_NUM_{slug}/`.
- **CTR**: Dual-file format (both `.md` and `.yaml`) stored together; use nested folder for multi-file contracts.


Universal Numbering Pattern (All Document Types)
- **Primary Number (DOC_NUM)**: Variable-length sequential number starting at 2 digits (01-99, then 100-999, 1000+)
  - **Notation**: "DOC_NUM" represents actual numeric digits (e.g., 01, 42, 99, 100, 1000)
  - **NOT**: Placeholder text like "NN" or "XXX"
  - **Minimum**: 2 digits (01)
  - **Growth**: Automatically expands when needed (99 → 100, 999 → 1000)
  - **Numbering Policy (explicit)**: Document numbers start at `01` and increase sequentially. As the sequence grows, the digit width MAY expand (e.g., `01…99` → `100…999` → `1000…`). Previously created documents keep their original width; new documents adopt the width required by the next number in sequence.
- **Section Number (S)**: 1-2 digit section number for split documents (0-99)
  - **Notation**: "S" represents actual numeric digit (e.g., 0, 1, 2, 10)
  - **Section 0**: Always the index file for split documents
- **Section H1 match**: For section files, the H1 title MUST include the section suffix `.S` to match the filename (e.g., `# BRD-03.1: …`).
- **Format**:
  - **Monolithic Documents (BRD, PRD, ADR)** - flat structure, no section suffix:
    - **Pattern**: `TYPE-DOC_NUM_{slug}.md` (e.g., `BRD-01_platform_architecture.md`)
    - **Use for**: MVP documents, single-file documents under 25KB, streamlined artifacts
    - **H1 Title**: `# TYPE-DOC_NUM: Title` (no `.S` suffix)
    - **Location**: Directly in type directory (no nested folder)
  - **Section-Based Documents (BRD, PRD, ADR)** - nested folder, section suffix required:
    - **Full pattern**: `TYPE-DOC_NUM.S_{folder_slug}_{section_type}.md` (e.g., `BRD-01.0_platform_architecture_index.md`)
    - **Shortened pattern** (PREFERRED): `TYPE-DOC_NUM.S_{section_type}.md` (e.g., `BRD-01.0_index.md`)
    - Section suffix is MANDATORY for all files in nested folders
    - **Shortened Filename Rule**: For section files inside nested folders, the descriptive slug MAY be omitted since the parent folder contains it.
  - **Other Types (REQ, TASKS, SPEC, etc.)** - section optional:
    - Atomic: `TYPE-DOC_NUM_{slug}.md` (e.g., `REQ-01_auth.md`, `TASKS-99_service.md`)
    - Split: `TYPE-DOC_NUM.S_{slug}.md` (e.g., `SPEC-100.1_split.md` for SPEC narrative)
    - Note: For SPEC, splitting applies to Markdown narrative; the SPEC YAML remains a single monolithic file for code generation.
- **Zero-Padding**: Start with 2 digits (01), expand as needed
  - **Index/General Utility Files Use Zeros**: Use all‑zero `DOC_NUM` to separate indexes and general utility artifacts from numbered documents.
    - This repository: uses 3 zeros (`-00_index.md`) consistently; do not rename historical files.
    - New repositories: choose `00` or `000` and keep it consistent across types.
    - General utility files follow `{DOC_TYPE}-00_{slug}.{ext}`.
- **Element ID DOC_NUM**: MUST match filename digit count exactly
  - Filename `BRD-01.0_index.md` → Element ID `BRD.01.01.01`
  - Filename `ADR-100.1_context.md` → Element ID `ADR.100.10.01`
- **Section File Use Cases**: Use `.S` suffix when:
  - Document exceeds 50KB and needs splitting
  - Distinct sections need separate files for maintenance
  - Use `split_type` metadata to distinguish sectional vs related documents
- **Default by Document Type**:
  - **BRD, PRD, ADR**:
    - **Monolithic** (<25KB, MVP): Flat structure `TYPE-DOC_NUM_{slug}.md` - no section suffix
    - **Section-based** (>25KB, complex): Nested folder with section files - section suffix REQUIRED
  - **All others**: Atomic (no section) - section OPTIONAL
- **Uniqueness Rule**: Each DOC_NUM is unique within its type
  - Monolithic: `TYPE-DOC_NUM_{slug}.md` (e.g., `BRD-01_platform.md`)
  - Section-based: `TYPE-DOC_NUM.S_{slug}.md` (e.g., `BRD-01.0_index.md`)
  - ❌ INVALID: Cannot have both `BRD-09_platform.md` AND `BRD-09.0_index.md` (collision - same DOC_NUM, different structure)
  - ✅ VALID: `BRD-09.0_index.md` AND `BRD-09.1_requirements.md` (same DOC_NUM, different sections in nested folder)
- **Vertical ID Alignment (Unified)**:
  - **Rule**: All downstream artifacts (`ADR`, `EARS`, `BDD`, `SYS`, `REQ`, `CTR`, `SPEC`) MUST match the ID of their parent `PRD` (or `BRD` if no PRD exists). **Exception**: `TASKS` have independent sequential numbering.
  - **Mapping**: `PRD-12` → `ADR-12`, `EARS-12`, `BDD-12`, `SPEC-12`, `SYS-12`, `REQ-12`, `CTR-12`.
  - **One-to-One (Flat Structure)**: 
    - Single artifact per PRD uses flat structure without decimal suffix.
    - **Examples**:
      - **ADR**: `PRD-05` → `ADR-05_caching_strategy.md` (single file, flat structure)
      - **SYS**: `PRD-02` → `SYS-02_session_memory.md` (single file, flat structure)
      - **BDD**: `PRD-04` → `BDD-04_authentication.feature` (single file, flat structure)
      - **EARS**: `PRD-06` → `EARS-06_notifications.md` (single file, flat structure)
  - **One-to-Many (Nested Structure)**: 
    - Multiple artifacts of the same type per PRD use decimal suffixes starting from `.01` and increasing sequentially.
    - **MUST use nested folder structure** when one-to-many mapping exists.
    - **Examples**:
      - **ADR**: `PRD-12` → `ADR-12_{slug}/` folder containing `ADR-12.01.md`, `ADR-12.02.md`
      - **SYS**: `PRD-08` → `SYS-08_{slug}/` folder containing `SYS-08.01.md`, `SYS-08.02.md`, `SYS-08.03.md`
      - **BDD**: `PRD-05` → `BDD-05_{slug}/` folder containing `BDD-05.01.feature`, `BDD-05.02.feature`
  - **Roots**: `BRD` and `PRD` maintain independent sequential numbering starting from `01` and increasing sequentially.
  - **Exceptions**: 
    - `REF` and `*-00` utility files remain independent.
    - **TASKS** have independent sequential numbering (not PRD-aligned). TASKS are special document types that provide AI code generation instructions and audit trail of code generation steps.

Document ID Standards (ai_dev_flow)
- Requirements (REQ)
  - **H1 ID**: `REQ-DOC_NUM` (e.g., `# REQ-12: [LEARNING_GOV] ...`).
  - **Directory**: `07_REQ/REQ-{PRD_ID}_{Slug}/` (Vertical Slice Grouping).
  - **Files**: `REQ-{PRD_ID}_{Slug}.md` or `REQ-{TotalSequence}_{Slug}.md` inside.
  - **Alignment Rule**: REQ folder ID MUST match the parent PRD ID (e.g., `07_REQ/REQ-12_learning/` matches `PRD-12`).
  - **Variable Length**: DOC_NUM = 2+ digits (01-99, 100-999, 1000+)
  - **Notes**: Legacy category folders are not used. Use PRD-based vertical slice folders.
- ADRs
  - H1 ID: `ADR-DOC_NUM` (e.g., `# ADR-33: Risk Limit Enforcement Architecture`).
  - **Structure**: Follow Default Directory Model (Flat vs Nested).
  - **Flat**: `docs/05_ADR/ADR-DOC_NUM_{slug}.md`
  - **Nested**: `docs/05_ADR/ADR-DOC_NUM_{slug}/` folder with section files.
  - **ID Alignment**: DOC_NUM MUST match the parent PRD ID (e.g., `PRD-33` -> `ADR-33`).
  - One-to-Many: `ADR-33.01`, `ADR-33.02` if multiple ADRs needed for one PRD.
  - Notes: Use `split_type` metadata to distinguish sectional vs related documents.
  - Examples:
    - Flat: `docs/05_ADR/ADR-01_database_selection.md`
    - Nested: `docs/05_ADR/ADR-100_cloud_migration/ADR-100.0_index.md`
- BDD Features and Tags
  - **File Format Clarification**:
    - **Test Scenarios**: `BDD-DOC_NUM_{slug}.feature` (Gherkin format - `.feature` extension)
    - **Index/Directory**: `BDD-00_index.md` (Markdown format - `.md` extension)
    - **Template**: `BDD-MVP-TEMPLATE.feature` (Gherkin format - `.feature` extension)
    - **Traceability Matrix**: `BDD-00_TRACEABILITY_MATRIX-TEMPLATE.md` (Markdown format - `.md` extension)

  **Section-Based File Organization** (MANDATORY):

  All BDD files use section-based numbering (dot notation) aligned with 02_PRD/BRD standards.

  **Three Valid Patterns**:

  1. **Section-Only Format** (primary pattern):
     - Filename: `04_BDD/BDD-DOC_NUM.SECTION_{slug}.feature`
     - Pattern: `^BDD-\d{2,}\.\d+_[a-z0-9_]+\.feature$`
     - Example: `04_BDD/BDD-02_knowledge_engine/BDD-02.14_query_result_filtering.feature`
     - Use when: Standard section file (< 15,000 tokens)

  2. **Subsection Format** (when section >500 lines):
     - Filename: `04_BDD/BDD-DOC_NUM.SECTION.SUBSECTION_{slug}.feature`
     - Pattern: `^BDD-\d{2,}\.\d+\.\d{2}_[a-z0-9_]+\.feature$`
     - Example: `04_BDD/BDD-02_knowledge_engine/BDD-02.24.01_quality_performance.feature`
     - Use when: Section requires splitting (each subsection ≤500 lines)

  3. **Aggregator Format** (optional redirect stub):
     - Filename: `04_BDD/BDD-DOC_NUM.SECTION.00_{slug}.feature`
     - Pattern: `^BDD-\d{2,}\.\d+\.00_[a-z0-9_]+\.feature$`
     - Example: `04_BDD/BDD-02_knowledge_engine/BDD-02.12.00_query_graph_traversal.feature`
     - Use when: Organizing multiple subsections under one section
     - Requirements: `@redirect` tag, 0 scenarios, references to subsections

  **Numbering Scheme**:
  - `.0` suffix: Index file (e.g., `BDD-02.0_index.md`)
  - `.1`, `.2`, `.3`, etc.: Content sections (e.g., `BDD-02_knowledge_engine/BDD-02.1_ingest.feature`)
  - `.SS.01`, `.SS.02`, etc.: Subsections (e.g., `BDD-02.3.01_learning_path.feature`)
  - `.SS.00`: Aggregator/redirect stub (e.g., `BDD-02.2.00_query.feature`)

  **File Organization**:
  - Nested folder per suite: `04_BDD/BDD-DOC_NUM_{slug}/`
  - All `.feature` files and the index live inside the suite folder
  - Each BDD suite MUST have index file: `BDD-DOC_NUM.0_index.md`
  - Optional companion docs: `BDD-DOC_NUM_README.md`, `BDD-DOC_NUM_TRACEABILITY.md` (inside the suite folder)

  **Hard Limits**:
  - Max file size: 20,000 tokens per `.feature` file (warning: 15,000 tokens)
  - Max scenarios: 12 scenarios per Feature block
  - If section exceeds 20,000 tokens → Split into subsections (`.SS.mm` format)
  - If many subsections → Add aggregator (`.SS.00` format)

  **Prohibited Patterns** (cause validation ERROR):
  - `_partN` suffix (e.g., `BDD-02_query_part1.feature`)
  - Single-file format: `BDD-NN_slug.feature` (legacy format)
  - Directory-based structure: `BDD-NN_{slug}/features/` (legacy format)

  **Section Metadata** (in .feature files):
  - Add section tags: `@section: NN.SS`, `@parent_doc: BDD-NN`, `@index: BDD-NN.0_index.md`
  - Feature title format: `Feature: BDD-NN.SS: Domain Description`
  - Example:
    ```gherkin
    @section: 2.1
    @parent_doc: BDD-02
    @index: BDD-02.0_index.md
    Feature: BDD-02.1: Ingest and Analysis
    ```

  - **ID Alignment**: DOC_NUM MUST match the parent PRD ID (e.g., `PRD-02` -> `BDD-02`).
  - Variable Length: DOC_NUM matches parent PRD.
  - Section Numbers: SECTION = 0 (index), 1+ (content sections)
  - Subsection Numbers: SUBSECTION = 01-99 (subsections), 00 (aggregator)
  - Tags (mandatory):
    - `@brd:BRD.NN.EE.SS` (upstream BRD element)
    - `@prd:PRD.NN.EE.SS` (upstream PRD element)
    - `@ears:EARS.NN.SS.RR` (upstream EARS requirement)
  - Tags appear before `Scenario:` using valid relative paths + anchors
  - Index: Each suite MUST have `04_BDD/BDD-DOC_NUM.0_index.md` listing all sections
- Technical Specifications (SPEC)
  - **Vertical ID Alignment**: SPEC ID MUST match the parent PRD ID (e.g., `PRD-12` -> `SPEC-12`).
  - **Structure**: Follow Default Directory Model (Flat vs Nested).
  - **Flat (Single SPEC)**: `09_SPEC/SPEC-DOC_NUM_{slug}.yaml`
  - **Nested (Micro-SPECs)**: `09_SPEC/SPEC-DOC_NUM_{slug}/` folder containing multiple YAML files.
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
  - Notes: Both .md and .yaml must exist for each CTR-DOC_NUM; slugs must match exactly. Use Section Files when contract documentation exceeds 50KB.

- AI Tasks (TASKS)
  - H1 ID: `TASKS-DOC_NUM` (e.g., `# TASKS-03: [RESOURCE_LIMIT] Service Implementation`)
  - Filename: `10_TASKS/TASKS-DOC_NUM_{slug}.md` with a tasks index at `10_TASKS/TASKS-00_index.md`.
  - **ID Alignment**: DOC_NUM MUST match the parent PRD ID (and associated SPEC ID).
  - Variable Length: DOC_NUM matches parent PRD.
  - Notes: SPEC implementation plans with exact TODOs for code generation. Each TASKS corresponds to one SPEC. Use Section Files when document exceeds 50KB.
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
  - **Structure**: Follow Default Directory Model (Flat for single files, Nested for complex/split docs).
  - **Flat (Preferred for MVP)**: `docs/01_BRD/BRD-DOC_NUM_{slug}.md`
  - **Nested**: `docs/01_BRD/BRD-DOC_NUM_{slug}/` folder with section files.
  - Variable Length: DOC_NUM = 2+ digits (01-99, 100-999, 1000+).
  - **Sequential**: Independent sequential numbering starting from `01`.
  - Notes: Use Flat structure by default. Use Nested structure only when document exceeds 20k tokens or requires splitting.
  - Examples:
    - Flat: `docs/01_BRD/BRD-01_platform_architecture.md`
    - Nested: `docs/01_BRD/BRD-03_complex_system/BRD-03.0_index.md`

PRD, SYS, and EARS Document Types
- Product Requirements Documents (PRD)
  - H1 ID: `PRD-DOC_NUM` (e.g., `# PRD-03: resource Risk Limits`)
  - **Structure**: Follow Default Directory Model (Flat for single files, Nested for complex/split docs).
  - **Flat (Preferred for MVP)**: `docs/02_PRD/PRD-DOC_NUM_{slug}.md`
  - **Nested**: `docs/02_PRD/PRD-DOC_NUM_{slug}/` folder with section files.
  - Variable Length: DOC_NUM = 2+ digits (01-99, 100-999, 1000+).
  - **Sequential**: Independent sequential numbering starting from `01`.
  - Notes: Use Flat structure by default. Use Nested structure only when document exceeds 20k tokens or requires splitting.
  - Examples:
    - Flat: `docs/02_PRD/PRD-01_user_authentication.md`
    - Nested: `docs/02_PRD/PRD-02_complex_feature/PRD-02.0_index.md`
- System Architecture Documents (SYS)
  - H1 ID: `SYS-DOC_NUM` (e.g., `# SYS-03: resource Risk Limits`)
  - **Structure**: Follow Vertical ID Alignment rules (Flat vs Nested).
  - **Flat (One-to-One)**: `06_SYS/SYS-DOC_NUM_{slug}.md`
  - **Nested (One-to-Many)**: `06_SYS/SYS-DOC_NUM_{slug}/` folder containing `SYS-DOC_NUM.01_{slug}.md`, `SYS-DOC_NUM.02_{slug}.md`, etc.
  - **ID Alignment**: DOC_NUM MUST match the parent PRD ID.
  - Variable Length: DOC_NUM matches parent PRD.
  - Notes: Use Section Files (`SYS-DOC_NUM.S_{slug}.md`) when individual document exceeds 50KB.
  - **Examples**:
    - Flat: `06_SYS/SYS-02_Session_Memory.md` (one SYS for PRD-02)
    - Nested: `06_SYS/SYS-08_trading_intelligence/` containing `SYS-08.01_LLM_Context.md`, `SYS-08.02_LLM_Ensemble.md`, `SYS-08.03_Agent_Swarm.md` (three SYS for PRD-08)
- EARS Requirements (EARS)
  - H1 ID: `EARS-DOC_NUM` (e.g., `# EARS-03: [RESOURCE_LIMIT] Enforcement`)
  - Filename: `03_EARS/EARS-DOC_NUM_{slug}.md`
  - **ID Alignment**: DOC_NUM MUST match the parent PRD ID.
  - Variable Length: DOC_NUM matches parent PRD.
  - Notes: Use Section Files (`EARS-DOC_NUM.S_{slug}.md`) when document exceeds 50KB.

One-to-Many Structure Examples (Vertical ID Alignment)

When a single PRD requires multiple downstream artifacts of the same type, ALL artifacts must use decimal suffixes starting from `.01` and must be organized in nested folders.

**Pattern**: `{LAYER}_DIR/{TYPE}-{PRD_ID}_{slug}/` containing `{TYPE}-{PRD_ID}.01_{slug}.md`, `{TYPE}-{PRD_ID}.02_{slug}.md`

**Complete Examples by Artifact Type**:

- **ADR (Architecture Decision Records)**
  ```
  PRD-01 → 05_ADR/ADR-01_iam/
    ├── ADR-01.01_Authentication_Architecture.md
    └── ADR-01.02_4D_Authorization_Matrix.md
  ```

- **SYS (System Requirements)**
  ```
  PRD-08 → 06_SYS/SYS-08_trading_intelligence/
    ├── SYS-08.01_LLM_Context_Automation.md
    ├── SYS-08.02_LLM_Ensemble.md
    └── SYS-08.03_Trading_Agent_Swarm.md
  ```

- **BDD (Behavior-Driven Development)**
  ```
  PRD-03 → 04_BDD/BDD-03_risk_management/
    ├── BDD-03.01_position_limits.feature
    ├── BDD-03.02_margin_requirements.feature
    └── BDD-03.03_circuit_breakers.feature
  ```

- **EARS (Event-Action-Response-State)**
  ```
  PRD-05 → 03_EARS/EARS-05_data_feeds/
    ├── EARS-05.01_market_data_ingestion.md
    └── EARS-05.02_historical_data_sync.md
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
- For large documents (>50KB), use Section Files: `TYPE-DOC_NUM.S_{slug}.md`
- Structure (this example):
  - **Nested Folder Types** (when >20k tokens):
    - Pattern: `01_BRD/BRD-DOC_NUM_{slug}/BRD-DOC_NUM.S_{section_type}.md`
      - Example: `01_BRD/BRD-01_platform_architecture/BRD-01.0_index.md`
    - Folder slug matches document slug.
  - **Flat Types** (Atomic, <20k tokens):
    - Pattern: `TYPE/TYPE-DOC_NUM_{slug}.md`
    - Example: `01_BRD/BRD-01_platform.md`, `05_ADR/ADR-33_risk.md`
  - **Special Cases**:
    - `09_SPEC/SPEC-{PRD_ID}_{Slug}/SPEC-{PRD_ID}-{Seq}_{Slug}.yaml`
    - `08_CTR/CTR-DOC_NUM_{slug}.md` + `CTR-DOC_NUM_{slug}.yaml`
    - `04_BDD/BDD-DOC_NUM_{suite}/` (Always Nested for Suites)

## Section-Based File Splitting (Document Chunking)

**Purpose**: When documents exceed 50KB standard limit (or 100KB maximum), split into section-based files using dot notation. This maintains document cohesion while enabling AI tool processing.

### Three Coexisting ID Patterns

The framework uses three distinct ID patterns for different purposes:

| Pattern | Format | Example | Purpose |
|---------|--------|---------|---------|
| **Document ID** | `TYPE-DOC_NUM` | `BRD-03` | Complete document reference |
| **Section File** | `TYPE-DOC_NUM.S` | `BRD-03.1` | Section S of document TYPE-DOC_NUM |
| **Element ID** | `TYPE.DOC_NUM.TT.SS` | `BRD.03.01.05` | Internal element (all dots, 4-segment) |

**Key Distinction**:
- `BRD-03.1` → Section file (dash before doc number, single dot for section)
- `BRD.03.01.05` → Element ID (all dots, 4-segment format for internal references)
- `@ref: BRD-03.1` → References a **document/section file**, not an element
- Element ID DOC_NUM MUST match filename digit count (e.g., `BRD-03` → `BRD.03.xx.xx`)

### Common Confusion: When to Use Each Format

**Question**: "Is the 4-segment format only for external traceability references?"

**Answer**: NO. The 4-segment format is used for **ALL element references**, both:
- Internal element headings: `### BRD.01.01.05: Feature Name`
- External traceability tags: `@brd: BRD.01.01.05`

**Rule Summary**:

| What You're Referencing | Format | Example |
|------------------------|--------|---------|
<!-- VALIDATOR:IGNORE-LINKS-START -->
| A **document file** | Dash format | `BRD-01`, `[BRD-01](../01_BRD/BRD-01.md)` |
<!-- VALIDATOR:IGNORE-LINKS-END -->
<!-- VALIDATOR:IGNORE-LINKS-START -->
| A **section file** | Dash+dot format | `BRD-01.1`, `[BRD-01.1](../01_BRD/BRD-01.1_summary.md)` |
<!-- VALIDATOR:IGNORE-LINKS-END -->
| A **specific element** (requirement, feature, constraint) | 4-segment dot format | `BRD.01.01.05`, `@brd: BRD.01.01.05` |

**Key Insight**: The 4-segment format unifies internal and external element references to avoid confusion. Use it consistently everywhere you reference a specific element. Element ID DOC_NUM MUST match filename digit count.

### Hyperlinked Traceability References (RECOMMENDED)

For enhanced navigability, traceability tags MAY be converted to clickable hyperlinks. This is **optional but recommended** for improved documentation usability.

**Tag-Only Format** (Primary - Always Valid):
```markdown
@brd: BRD.01.09.01
```

**Hyperlinked Format** (Enhanced - Recommended for Published Docs):
```markdown
[@brd: BRD.01.09.01](../../01_BRD/BRD-01_platform/BRD-01.5_user_stories.md#brd010901-feature-name)
```

**Anchor ID Convention**: Convert element ID to lowercase, remove dots, append slug:
- Element: `BRD.01.09.01` → Anchor: `#brd010901-feature-name`

**Format Comparison**:

| Aspect | Tag-Only | Hyperlinked |
|--------|----------|-------------|
| **Validation** | ✅ Easy regex parsing | ⚠️ Requires link checker |
| **Maintainability** | ✅ No path breakage | ❌ Breaks when files move |
| **Navigation** | ❌ Manual search required | ✅ One-click access |
| **Automation** | ✅ Script-friendly extraction | ⚠️ Complex link parsing |
| **Recommended For** | Working drafts, automation | Published documentation |

**Hybrid Approach** (Best Practice):
1. Use tag-only format during active development
2. Convert to hyperlinked format before documentation release
3. Run link validation after conversion: `./scripts/validate_links.py --path docs/`

**Cross-Document Hyperlink Patterns**:

| Reference Type | Pattern | Example |
|----------------|---------|---------|
| Same folder | Example only | `BRD.01.01.01 -> ./BRD-01.1_summary.md#brd010101` |
| Parent folder | Example only | `BRD.01.01.01 -> ../01_BRD/BRD-01.1_summary.md#brd010101` |
| Nested folder | Example only | `BRD.01.01.01 -> ../01_BRD/BRD-01_platform/BRD-01.1_summary.md#brd010101` |

**Internal Section Links** (within same document or folder):

| Link Type | Format | Example |
|-----------|--------|---------|
| Section reference | Example only | `PRD-01.8 -> ./PRD-01.8_user_stories.md` |
| Index to section | Example only | `PRD-01.9 -> PRD-01.9_functional_requirements.md` |
| Cross-PRD | Example only | `PRD-02 -> ../PRD-02_knowledge_engine/` |

### Section File Naming Pattern

**Nested Folder Types (BRD, PRD, ADR)** - section ALWAYS required:
- **Shortened Pattern** (PREFERRED): `{TYPE}-{DOC_NUM}.{SECTION}_{section_type}.md`
  - Regex: `^(BRD|PRD|ADR)-[0-9]{2,}\.[0-9]+_[a-z_]+\.md$`
  - Examples: `BRD-01.0_index.md`, `PRD-15.2_features.md`, `ADR-100.1_context.md`
- **Full Pattern** (backward compatible): `{TYPE}-{DOC_NUM}.{SECTION}_{folder_slug}_{section_type}.md`
  - Regex: `^(BRD|PRD|ADR)-[0-9]{2,}\.[0-9]+_[a-z0-9_]+_[a-z_]+\.md$`
  - Examples: `BRD-01.0_platform_architecture_index.md`, `PRD-15.2_product_features.md`
- **Combined Regex** (validates both): `^(BRD|PRD|ADR)-[0-9]{2,}\.[0-9]+_([a-z0-9]+_)*[a-z_]+\.md$`

**Flat Types (all others)** - section OPTIONAL:
- **Atomic Pattern**: `{TYPE}-{DOC_NUM}_{slug}.md`
- **Split Pattern**: `{TYPE}-{DOC_NUM}.{SECTION}_{slug}.md`

#### Document Number Width Policy (Unified)

- Start with 2 digits and expand only as needed. Do not use unnecessary leading zeros beyond the active width of the current number.
- Correct examples: `BRD-01`, `BRD-99`, `BRD-102`, `BRD-999`, `BRD-1000`.
- Incorrect examples: `BRD-001`, `BRD-009` (extra leading zero not required by the number).
- This rule is unified across all document types: `BRD`, `PRD`, `EARS`, `BDD`, `ADR`, `SYS`, `REQ`, `CTR`, `SPEC`, `TASKS`.
- Element IDs MUST match filename digit width exactly (e.g., `BRD-06` ⇄ `BRD.06.xx.xx`; `PRD-22` ⇄ `PRD.22.xx.xx`).
- Exception: Reserved infrastructure artifacts use `-000` (e.g., `BRD-00_index.md`, `PRD-00_index.md`) by design.
- Note: Source code and unit test files follow coding standards for their languages and are excluded from this document ID filename policy.
- **Regex**: `^[A-Z]{2,5}-[0-9]{2,}(\.[0-9]+)?_[a-z0-9_]+\.(md|yaml|feature)$`
- **Examples**: `REQ-01_api_auth.md`, `TASKS-99_service.md`, `SPEC-100.1_split.md`

#### Sequential vs Non-Sequential Element IDs

**Document Numbers**: MUST be sequential (01, 02, 03...). No gaps allowed in document numbering.

**Element IDs within Documents**: MAY be non-sequential. Gaps are permitted when:

| Reason | Example | Recommendation |
|--------|---------|----------------|
| Deprecation | `EARS.04.25.008` deprecated, `009` remains | Document deprecation in revision history |
| Historical removal | Requirements removed during review | Add note: "IDs 010-015 removed per review" |
| Logical grouping | IDs 001-050 for auth, 100-150 for data | Document grouping convention |
| Reserved ranges | IDs 900-999 reserved for future use | Document reservation in index |

**Policy Summary**:

| ID Type | Sequential Required | Gaps Allowed | Re-numbering |
|---------|---------------------|--------------|--------------|
| Document numbers (TYPE-NN) | YES | NO | Avoid (breaks references) |
| Element IDs (TYPE.NN.TT.SS) | NO | YES | Avoid (breaks traceability) |
| Section numbers (.S) | YES | NO | Requires index update |

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
| `.` | Dot separator | Separates document number from section |
| `SECTION` | 1-2 digits | Section number (0-99) |
| `_` | Underscore separator | Separates ID from descriptive slug |
| `slug` | lowercase_snake_case | Human-readable description |

**Legacy Regex (backward compatibility)**: `^[A-Z]{2,5}(-REF)?-[0-9]{2,}\.[0-9]+(\.[0-9]+)?_[a-z0-9_]+\.md$`

### When to Split Documents

| File Size | Action | Rationale |
|-----------|--------|-----------|
| <50KB | Keep as single file | Optimal for all AI tools |
| 50-100KB | Consider splitting | May cause issues with some tools |
| >100KB | **MUST split** | Exceeds primary assistant practical limit (see AI_TOOL_OPTIMIZATION_GUIDE.md) |

**Split Triggers**:
1. File exceeds 50KB standard limit
2. Document has clear logical sections (chapters, modules)
3. Sections can stand alone with minimal cross-references
4. Team needs independent section maintenance

### Section Numbering Rules

| Section | Purpose | Content |
|---------|---------|---------|
| **Section 0** | Index/Overview | Document control, section map, navigation |
| **Section 1+** | Content sections | Actual document content, numbered sequentially |

**Section 0 Requirements** (MANDATORY for all split documents):
- Document control metadata
- Complete section map with links
- Version history
- Cross-reference summary
- Reading order guidance

### Mandatory Metadata Header (YAML Frontmatter)

**ALL section files MUST include YAML frontmatter**:

```yaml
---
doc_id: TYPE-DOC_NUM
section: S
title: "Section Title"
parent_doc: TYPE-DOC_NUM.0_index.md      # null for section 0
prev_section: TYPE-DOC_NUM.{S-1}_slug.md  # null for section 0 or 1
next_section: TYPE-DOC_NUM.{S+1}_slug.md  # null for last section
tags:
  - section-file
  - document-type-tag
custom_fields:
  descriptive_slug: folder_slug  # Folder's descriptive name (for shortened filenames)
  total_sections: N
  section_type: content  # or "index" for section 0
  architecture_approach: ai-agent-primary
  priority: primary|fallback|shared
  split_date: YYYY-MM-DD
---
```

**Required Metadata Fields**:

| Field | Required In | Description |
|-------|-------------|-------------|
| `doc_id` | All sections | Parent document ID (TYPE-DOC_NUM) |
| `section` | All sections | Section number (0 = index, 1+ = content) |
| `title` | All sections | Section-specific title |
| `total_sections` | Section 0 | Total number of sections in split document |
| `descriptive_slug` | BRD, PRD, ADR | Folder's descriptive name (enables shortened filenames) |
| `parent_doc` | Content sections | Link to Section 0 index file |
| `prev_section` | Content sections | Link to previous section (if exists) |
| `next_section` | Content sections | Link to next section (if exists) |
| `tags` | All sections | Must include `section-file` or `section-index` |

### Section File Examples

**Source Document**: `BRD-03.0_platform_requirements.md` (150KB)

**Split into Section Files (shortened pattern - PREFERRED)**:

```
docs/01_BRD/
└── BRD-03_platform_example/             # Nested folder with descriptive slug
    ├── BRD-03.0_index.md                        # Section 0: Index/Overview
<!-- VALIDATOR:IGNORE-LINKS-START -->
    ├── BRD-03.1_executive_summary.md            # Section 1: Executive Summary
<!-- VALIDATOR:IGNORE-LINKS-END -->
    ├── BRD-03.2_business_context.md             # Section 2: Business Context
    ├── BRD-03.3_functional_requirements.md      # Section 3: Functional Requirements
    ├── BRD-03.4_non_functional_requirements.md  # Section 4: Non-Functional Requirements
    ├── BRD-03.5_architecture_decisions.md       # Section 5: Architecture Decisions
    └── BRD-03.6_appendices.md                   # Section 6: Appendices
```

**Split into Section Files (full pattern - backward compatible)**:

```
docs/01_BRD/
└── BRD-03_platform_example/             # Nested folder with descriptive slug
    ├── BRD-03.0_platform_example_index.md              # Section 0
    ├── BRD-03.1_platform_example_executive_summary.md  # Section 1
    └── ...
```

**Key Rules**:
- Folder slug (`platform_example`) provides the descriptive context
- Shortened pattern omits redundant slug from filenames (PREFERRED for new documents)
- Full pattern accepted for backward compatibility
- Use `descriptive_slug` metadata field to capture the folder's descriptive name

**Section 0 Header Example** (`BRD-03.0_index.md`):
```markdown
---
doc_id: BRD-03
section: 0
title: "Platform Requirements - Index"
total_sections: 7
original_size_kb: 146
split_date: 2025-12-17
tags:
  - section-index
  - platform-brd
custom_fields:
  descriptive_slug: platform_example  # Folder's descriptive name for tools
  section_type: index
  architecture_approach: ai-agent-primary
  priority: primary
  development_status: active
---

# BRD-03.0: Platform Requirements - Index

## Document Control

| Field | Value |
|-------|-------|
| **Document ID** | BRD-03 |
| **Status** | Active |
| **Total Sections** | 7 |

## Section Map

| Section | Title | Size | Link |
|---------|-------|------|------|
| 0 | Index (this file) | 3KB | [BRD-03.0](BRD-03.0_index.md) |
<!-- VALIDATOR:IGNORE-LINKS-START -->
| 1 | Executive Summary | 8KB | [BRD-03.1](BRD-03.1_executive_summary.md) |
<!-- VALIDATOR:IGNORE-LINKS-END -->
| 2 | Business Context | 25KB | [BRD-03.2](BRD-03.2_business_context.md) |
| 3 | Functional Requirements | 45KB | [BRD-03.3](BRD-03.3_functional_requirements.md) |
| 4 | Non-Functional Requirements | 30KB | [BRD-03.4](BRD-03.4_non_functional_requirements.md) |
| 5 | Architecture Decisions | 20KB | [BRD-03.5](BRD-03.5_architecture_decisions.md) |
| 6 | Appendices | 15KB | [BRD-03.6](BRD-03.6_appendices.md) |

## Reading Order

1. Start with Section 0 (this index) for overview
2. Proceed through sections 1-6 sequentially
3. Reference Section 6 for detailed appendices
```

<!-- VALIDATOR:IGNORE-LINKS-START -->
**Content Section Example** (`BRD-03.1_executive_summary.md`):
<!-- VALIDATOR:IGNORE-LINKS-END -->
```markdown
---
doc_id: BRD-03
section: 1
title: "Executive Summary"
parent_doc: "BRD-03.0_index.md"
prev_section: null
next_section: "BRD-03.2_business_context.md"
tags:
  - section-file
  - platform-brd
custom_fields:
  descriptive_slug: platform_example  # Folder's descriptive name for tools
  total_sections: 7
  section_type: content
  architecture_approach: ai-agent-primary
  priority: primary
---

# BRD-03.1: Executive Summary

> **Navigation**: [Index](BRD-03.0_index.md) | Previous: None | [Next](BRD-03.2_business_context.md)
>
> **Parent Document**: BRD-03
> **Section**: 1 of 7

---

## Section Content

[Section content here...]
```

### Cross-Reference Format for Section Files

**Tagging Section References**:
- `@ref: BRD-03.1` → References section 1 of BRD-03
- `@ref: BRD-03.2.3` → References subsection 2.3 of BRD-03

**Markdown Links to Sections**:
<!-- VALIDATOR:IGNORE-LINKS-START -->
- Same directory: `[BRD-03.1](BRD-03.1_executive_summary.md)`
<!-- VALIDATOR:IGNORE-LINKS-END -->
<!-- VALIDATOR:IGNORE-LINKS-START -->
- Cross-directory: `[BRD-03.1](../01_BRD/BRD-03.1_executive_summary.md)`
<!-- VALIDATOR:IGNORE-LINKS-END -->

### Metadata Tags for Document Type Distinction

All split documents use the unified Section File format (`TYPE-DOC_NUM.S_{slug}.md`). Document behavior is controlled by **metadata tags**, not filename patterns.

#### Primary Tag: `split_type`

| Value | Description | Use Case |
|-------|-------------|----------|
| `section` | Chunks of ONE large document | Split 150KB BRD into manageable parts |
| `related` | Distinct but related documents | Prerequisites + Main Spec + Quick Reference |

#### Supporting Tags

| Tag | Values | Purpose |
|-----|--------|---------|
| `reading_order` | `sequential` / `independent` | Must read in order vs can read standalone |
| `traceability_scope` | `inherited` / `independent` | Uses parent's tags vs has own traceability |
| `index_role` | `true` / `false` | Is this the Section 0 index file |

#### Behavior by `split_type`

| Aspect | `split_type: section` | `split_type: related` |
|--------|----------------------|----------------------|
| **Purpose** | Chunks of one document | Distinct related documents |
| **Reading order** | Sequential (must read in order) | Independent (can read standalone) |
| **Traceability** | Inherited from parent | Each has own tags |
| **Typical use** | Large docs >50KB | Prereqs + Spec + Reference |
| **File naming** | `TYPE-DOC_NUM.S_slug.md` | `TYPE-DOC_NUM.S_slug.md` (same) |
| **Section 0** | Required | Required |
| **Navigation links** | Required | Required |

#### Sectional Document Metadata Example (split large file)

```yaml
---
doc_id: BRD-03
section: 1
title: "Executive Summary"
split_type: section
reading_order: sequential
traceability_scope: inherited
index_role: false
parent_doc: "BRD-03.0_index.md"
prev_section: null
next_section: "BRD-03.2_business_context.md"
---
```

#### Related Documents Metadata Example (distinct but grouped)

```yaml
---
doc_id: BRD-09
section: 1
title: "Provider Integration Prerequisites"
split_type: related
reading_order: independent
traceability_scope: independent
index_role: false
parent_doc: "BRD-09.0_index.md"
prev_section: null
next_section: "BRD-09.2_main_spec.md"
---
```

### Type-Specific Section Templates

Each document type has dedicated section templates providing type-specific metadata, tags, and traceability fields. Use these instead of generic templates for better compliance.

**Template Locations**:

| Type | Layer | Index Template | Content Template |
|------|-------|----------------|------------------|
| BRD | 1 | `01_BRD/BRD-SECTION-0-TEMPLATE.md` | `01_BRD/BRD-SECTION-TEMPLATE.md` |
| PRD | 2 | `02_PRD/PRD-SECTION-0-TEMPLATE.md` | `02_PRD/PRD-SECTION-TEMPLATE.md` |
| EARS | 3 | `03_EARS/EARS-SECTION-0-TEMPLATE.md` | `03_EARS/EARS-SECTION-TEMPLATE.md` |
| BDD | 4 | `04_BDD/BDD-SECTION-0-TEMPLATE.md` | `04_BDD/BDD-SECTION-TEMPLATE.md` |
| ADR | 5 | `05_ADR/ADR-SECTION-0-TEMPLATE.md` | `05_ADR/ADR-SECTION-TEMPLATE.md` |
| SYS | 6 | `06_SYS/SYS-SECTION-0-TEMPLATE.md` | `06_SYS/SYS-SECTION-TEMPLATE.md` |
| REQ | 7 | `07_REQ/REQ-SECTION-0-TEMPLATE.md` | `07_REQ/REQ-SECTION-TEMPLATE.md` |
| CTR | 8 | `08_CTR/CTR-SECTION-0-TEMPLATE.md` | `08_CTR/CTR-SECTION-TEMPLATE.md` |
| SPEC | 9 | `09_SPEC/SPEC-SECTION-0-TEMPLATE.md` | `09_SPEC/SPEC-SECTION-TEMPLATE.md` |

**Types NOT requiring section templates**: TASKS (typically remain under 25KB)

Cross-Reference Link Format (MANDATORY)
- Universal rule: use markdown links for all references.
- Use atomic (DOC_NUM) patterns for standalone documents, Section Files (DOC_NUM.S) for split documents.
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
      - BDD: "`04_BDD/BDD-DOC_NUM_{suite}/BDD-DOC_NUM.SECTION_{slug}.feature(:LNN)`"`
<!-- VALIDATOR:IGNORE-LINKS-END -->
  - BRD in BRD:
    - `[BRD-DOC_NUM](BRD-DOC_NUM_{slug}.md)` (same directory)
    - `[BRD-DOC_NUM.S](BRD-DOC_NUM.S_{slug}.md)` (section file reference)
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
  - `python 07_REQ/scripts/validate_requirement_ids.py`
  - Optional: `python scripts/validate_links.py` (broken references)
  - Optional: `python scripts/validate_traceability_matrix.py` (matrix compliance)
- Quick regexes (conceptual):
  - **Unified Element ID** (all document types): `^[A-Z]{2,5}\.[0-9]{2,9}\.[0-9]{2,9}\.[0-9]{2,9}$`
  - **Internal Heading**: `^###\s+[A-Z]{2,5}\.[0-9]{2,9}\.[0-9]{2,9}\.[0-9]{2,9}:\s+.+$`
  - **Cross-Reference Tag**: `^@[a-z]+:\s+[A-Z]{2,5}\.[0-9]{2,9}\.[0-9]{2,9}\.[0-9]{2,9}$`
- Document filename regexes (atomic documents - dash format for files):
  - REQ H1 ID: `^#\sREQ-\d{2,}:.+$`
  - REQ filename: `REQ-\d{2,}_.+\.md$`
  - ADR H1 ID: `^#\sADR-\d{2,}:.+$`
  - ADR filename: `ADR-\d{2,}_.+\.md$`
  - BDD filename: `BDD-\d{2,}_.+\.feature$`
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
- Section file regexes (dot notation for document chunks):
  - Section filename (full or shortened): `[A-Z]{2,5}(-REF)?-[0-9]{2,}\.[0-9]+(\.[0-9]+)?_[a-z0-9_]+\.md$`
  - Section H1 ID: `^#\s[A-Z]{2,5}(-REF)?-[0-9]{2,}\.[0-9]+(\.[0-9]+)?:.+$`
  - Section reference tag: `@ref:\s+[A-Z]{2,5}(-REF)?-[0-9]{2,}\.[0-9]+(\.[0-9]+)?`
  - Section 0 (index) filename: `[A-Z]{2,5}(-REF)?-[0-9]{2,}\.0_[a-z_]+\.md$`
- Nested folder type filename patterns (BRD, PRD, ADR):
  - Shortened pattern (PREFERRED): `^(BRD|PRD|ADR)-[0-9]{2,}\.[0-9]+_[a-z_]+\.md$`
    - Example: `BRD-03.0_index.md`, `PRD-01.1_overview.md`, `ADR-15.2_decision.md`
  - Full pattern (backward compatible): `^(BRD|PRD|ADR)-[0-9]{2,}\.[0-9]+_[a-z0-9_]+_[a-z_]+\.md$`
    - Example: `BRD-03.0_platform_example_index.md`
  - Combined regex (validates both): `^(BRD|PRD|ADR)-[0-9]{2,}\.[0-9]+_([a-z0-9]+_)*[a-z_]+\.md$`

Examples (ai_dev_flow) - Atomic Documents (DOC_NUM)
- **Nested Folder Types (monolithic option, still in nested folder)**:
  - BRD: `docs/01_BRD/BRD-01_foundation/BRD-01.0_foundation_overview.md` (H1: `# BRD-01.0: Foundation & Overview`)
  - PRD: `02_PRD/PRD-03_risk_limits/PRD-03.0_risk_limits_overview.md` (H1: `# PRD-03.0: resource Risk Limits`)
  - ADR: `05_ADR/ADR-33_risk_enforcement/ADR-33.0_risk_enforcement_architecture.md` (H1: `# ADR-33.0: Risk Limit Enforcement Architecture`)
- **Flat Types**:
  - SYS: `06_SYS/SYS-03_position_risk_limits.md` (H1: `# SYS-03: resource Risk Limits`)
  - EARS: `03_EARS/EARS-03_resource_limit_enforcement.md` (H1: `# EARS-03: [RESOURCE_LIMIT - e.g., request quota, concurrent sessions] Enforcement`)
  - REQ: `07_REQ/risk/lim/REQ-03_resource_limit_enforcement.md` (H1: `# REQ-03: [RESOURCE_LIMIT - e.g., request quota, concurrent sessions] Enforcement`)
- CTR: `08_CTR/CTR-01_position_risk_validation.md` + `CTR-01_position_risk_validation.yaml` (H1: `# CTR-01: resource Risk Validation Contract`, YAML: `contract_id: position_risk_validation`)
- SPEC: `09_SPEC/SPEC-03_resource_limit_service.yaml` (id: `resource_limit_service`)
- TASKS: `10_TASKS/TASKS-03_resource_limit_service.md` (H1: `# TASKS-03: [RESOURCE_LIMIT - e.g., request quota, concurrent sessions] Service Implementation`)


Examples (ai_dev_flow) - Section Files (DOC_NUM.S) - Nested Folder Structure
- Split BRD document (150KB original → 7 sections):
  - Index: `docs/01_BRD/BRD-03_platform_example/BRD-03.0_platform_example_index.md` (H1: `# BRD-03.0: Platform Requirements - Index`)
  - Section 1: `docs/01_BRD/BRD-03_platform_example/BRD-03.1_platform_example_executive_summary.md` (H1: `# BRD-03.1: Executive Summary`)
  - Section 2: `docs/01_BRD/BRD-03_platform_example/BRD-03.2_platform_example_business_context.md` (H1: `# BRD-03.2: Business Context`)
  - Section 3: `docs/01_BRD/BRD-03_platform_example/BRD-03.3_platform_example_functional_requirements.md` (H1: `# BRD-03.3: Functional Requirements`)
- Split PRD document with subsections:
  - Index: `docs/02_PRD/PRD-15_product_features/PRD-15.0_product_features_index.md`
  - Section 2.1: `docs/02_PRD/PRD-15_product_features/PRD-15.2.1_product_features_api.md` (H1: `# PRD-15.2.1: API Features`)
  - Section 2.2: `docs/02_PRD/PRD-15_product_features/PRD-15.2.2_product_features_ui.md` (H1: `# PRD-15.2.2: UI Features`)
- Split ADR document:
  - Index: `docs/05_ADR/ADR-01_database_selection/ADR-01.0_database_selection_index.md` (H1: `# ADR-01.0: Database Selection - Index`)
  - Section 1: `docs/05_ADR/ADR-01_database_selection/ADR-01.1_database_selection_context.md` (H1: `# ADR-01.1: Context`)
  - Section 2: `docs/05_ADR/ADR-01_database_selection/ADR-01.2_database_selection_decision.md` (H1: `# ADR-01.2: Decision`)

Component Abbreviations (examples)
- SVC (Service), CL (Client), SRV (Server), GW (Gateway), AGG (Aggregator), MGR (Manager), CTRL (Controller), ADPT (Adapter), REPO (Repository), PROC (Processor), VAL (Validator), ORCH (Orchestrator), PROV (Provider)
- IB ([EXTERNAL_SERVICE - e.g., Payment Gateway, CRM System]), AV ([EXTERNAL_DATA_PROVIDER - e.g., Weather API, item Data API]), MKT (Market), ORD (Order), EXEC (Execution), POS (resource), LIM (Limit), RISK (Risk), ACCT (Account), PFOL (resource collection), CFG (Configuration), AUTH (Authentication), AUTHZ (Authorization), REDIS, PUBSUB, BQ (BigQuery), CSQL (Cloud SQL), GCR (Cloud Run), GSM (Secrets Manager)

BDD Tag Examples
```gherkin
# Document-level references (dash format for file links)
@requirement:[REQ-03](../07_REQ/risk/lim/REQ-03_resource_limit_enforcement.md#REQ-03)
@adr:[ADR-33](../05_ADR/ADR-33_risk_enforcement/ADR-33.0_risk_enforcement_index.md#ADR-33)

# Internal element references (dot format for element IDs)
# Format: TYPE.DOC_NUM.ELEM_TYPE.SEQ
# DOC_NUM in element ID MUST match filename digit count
@brd: BRD.01.01.05    # BRD doc 01, Functional Requirement #5
@brd: BRD.01.03.02    # BRD doc 01, Constraint #2
@prd: PRD.02.07.15    # PRD doc 02, User Story #15
@adr: ADR.03.10.01    # ADR doc 03, Decision #1
```

Anchors & Linking
- Use ID anchors where applicable (e.g., `#REQ-01`, `#ADR-32`).
- Prefer stable ID anchors over line anchors. If a line anchor (e.g., `#L28`) is used, revalidate after edits.

Local Clarifications (ai_dev_flow)
- Variable-length numeric filename prefixes (DOC_NUM) are required here for readability and ordering; do not rename to match other directories' styles.
- DOC_NUM starts at 2 digits (01) and grows as needed (100, 1000).
- SPEC filenames keep `SPEC-DOC_NUM_{slug}.yaml`; the YAML `id:` is the stable spec identifier used by tags and prose.
- Keep tag headers at top of files (first non-empty lines) for machine-readability as shown in TRACEABILITY.md.
- For large documents (>50KB), use Section Files (`TYPE-DOC_NUM.S_{slug}.md`) instead of creating separate related documents.

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

> ⚠️ **REMOVED PATTERNS**: The following formats are INVALID:
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
| 30 | Task Item | TASKS |
| 31 | Plan Step | TASKS (Section 4) |
| 32 | Architecture Topic | BRD |
| 33-39 | Reserved for future use | - |
| 40 | Unit Test | TSPEC (UTEST) |
| 41 | Integration Test | TSPEC (ITEST) |
| 42 | Smoke Test | TSPEC (STEST) |
| 43 | Functional Test | TSPEC (FTEST) |
| 44 | Performance Test | TSPEC (PTEST) - Reserved |
| 45 | Security Test | TSPEC (SECTEST) - Reserved |
| 46-99 | Reserved for future use | - |

### Examples

| ID | Length | Meaning |
|----|--------|---------|
| `BRD.01.01.01` | 12 | BRD #1, Functional Requirement #1 |
| `BRD.01.03.05` | 12 | BRD #1, Constraint #5 |
| `PRD.02.07.42` | 12 | PRD #2, User Story #42 |
| `ADR.01.10.01` | 12 | ADR #1, Decision #1 |
| `TASKS.01.17.128` | 15 | TASKS #1, Task #128 |
| `BRD.99.01.9999` | 15 | BRD #99, Functional Requirement #9999 |
| `SPEC.01.15.03` | 13 | SPEC #1, Interface #3 |
| `BRD.01.32.01` | 12 | BRD #1, Architecture Topic #1 (Infrastructure) |

### Growth Pattern

IDs automatically expand as needed without schema changes:

```text
BRD.01.01.01      → Start (minimum)
BRD.01.01.99      → Approaching 2-digit limit
BRD.01.01.100     → Auto-expand to 3 digits
BRD.01.01.9999    → Still valid (4 digits)
BRD.99.99.999999  → Maximum practical scale
```

### Cross-Reference Tag Format

| Tag Format | Example | Meaning |
|------------|---------|---------|
| `@brd: BRD.01.01.01` | BRD doc 1, FR #1 | Functional requirement reference |
| `@prd: PRD.02.07.05` | PRD doc 2, User Story #5 | User story reference |
| `@adr: ADR.03.10.01` | ADR doc 3, Decision #1 | Architecture decision reference |
| `@spec: SPEC.01.15.02` | SPEC doc 1, Interface #2 | Interface specification reference |

### AI-First Design Rationale

This format is optimized for AI-assisted documentation workflows:

1. **Token efficiency**: 12 chars minimum vs 15+ for human-readable formats
2. **AI translation**: Human asks "what is BRD.01.03.05?", AI responds "Constraint #5: Budget limit $50K"
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
| BRD | `### BRD.NN.TT.SS: Name` | `### BRD.01.01.01: Market Data Feed` |
| PRD | `### PRD.NN.TT.SS: Name` | `### PRD.02.07.01: User Dashboard` |
| EARS | `### EARS.NN.TT.SS: Name` | `### EARS.01.01.01: Data Validation` |
| BDD | `### BDD.NN.TT.SS: Name` | `### BDD.01.13.01: Login Scenario` |
| SYS | `### SYS.NN.TT.SS: Name` | `### SYS.01.01.01: API Gateway` |
| ADR | `### ADR.NN.TT.SS: Name` | `### ADR.01.10.01: Database Selection` |

**Format Breakdown**:

| Component | Description | Example |
|-----------|-------------|---------|
| `TYPE` | Document type in SDD framework | `BRD`, `PRD`, `ADR`, `SPEC` |
| `.NN` | Document number (2+ digits) | `.01` = document 1 |
| `.TT` | Element type code (see table above) | `.01` = Functional Requirement |
| `.SS` | Sequential within element type | `.01` = first item of this type |

**Example**: `BRD.01.03.05` = BRD document 01, Constraint (type 03), item #5

**Validation Regex**:

```python
INTERNAL_HEADING_PATTERN = r'^###\s+[A-Z]{2,5}\.[0-9]{2,9}\.[0-9]{2,9}\.[0-9]{2,9}:\s+.+$'
# Matches: ### BRD.01.01.01: Feature Name
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
| `### BRD.017.001: Feature` | `### BRD.17.01.01: Feature` |
| `### Feature F-01: User Dashboard` | `### PRD.01.07.01: User Dashboard` |

---

## Architecture Decision Topic Subsection Format

**Purpose**: Document Section 7.2 "Architecture Decision Requirements" contains numbered subsections identifying architectural topics requiring formal ADR decisions. These use the standard 4-segment format with element type code `10` (Decision).

**Subsection ID Pattern**: `{DOC_TYPE}.NN.10.SS` (using Decision element type)

| Component | Description | Example |
|-----------|-------------|---------|
| `{DOC_TYPE}` | Document type (BRD, PRD, etc.) | `BRD` |
| `.NN` | Document number (2+ digits) | `.01` = BRD-01 |
| `.10` | Element type code for Decision | `.10` = Decision type |
| `.SS` | Sequential topic number | `.03` = third topic |

**Heading Format**:

```markdown
#### BRD.01.10.03: [Topic Name]

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
| BRD-01 | 3 | `BRD.01.10.03` | Third architecture decision topic in BRD-01 |
| BRD-17 | 1 | `BRD.17.10.01` | First architecture decision topic in BRD-17 |
| BRD-03 | 12 | `BRD.03.10.12` | Twelfth architecture decision topic in BRD-03 |

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
# Matches: ### BRD.01.10.03: ... OR #### PRD.17.10.01: ...
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
❌ Incorrect: BRD-01.02, PRD-001.AC.05
✓ Correct: BRD.01.02.01, PRD.001.06.05
```

**Legacy ID Format** (IDPAT-W001):
```markdown
❌ Legacy: FR-001, AC-005, NFR-003
✓ Unified: REQ.01.01.001, REQ.01.06.005, SYS.01.02.003
```

**Forward Reference** (FWDREF-E001):
```markdown
❌ In PRD: "See ADR-01 for database decision"
✓ In PRD: "Architecture decisions required for: database selection"
```

### Running Validators

```bash
# Validate ID patterns
python3 07_REQ/scripts/validate_requirement_ids.py .

# Validate forward references
python3 scripts/validate_forward_references.py .

# Run all validators
python3 scripts/validate_all.py . --all
```

---

## Checklist

- H1 titles contain IDs for 02_PRD/06_SYS/03_EARS/07_REQ/05_ADR/08_CTR/10_TASKS/BRD where applicable (use `TYPE-DOC_NUM` format).
- BDD tags are markdown links with valid relative paths and anchors.
- Spec files named `SPEC-DOC_NUM_{slug}.yaml`; inside, `id:` is snake_case and used by `@spec` tags; `requirements_source`/`architecture`/`verification` links resolve.
- All document types follow universal numbering pattern: DOC_NUM = 2+ digits (01-99, 100-999, 1000+).
- Element ID DOC_NUM MUST match filename digit count exactly.
- 01_BRD/02_PRD/ADR: Section suffix is ALWAYS required (`.0` minimum for single-file documents).
- Other types: Section suffix is OPTIONAL (used when splitting large documents).
- For large documents (>50KB), use Section Files (`TYPE-DOC_NUM.S_{slug}.md`) with appropriate `split_type` metadata.
- Internal element IDs use unified 4-segment format: `TYPE.DOC_NUM.TT.SS`.
- Run `python 07_REQ/scripts/validate_requirement_ids.py` and fix any violations before committing.