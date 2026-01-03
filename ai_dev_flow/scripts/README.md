---
title: "Traceability Matrix Automation Scripts"
tags:
  - index-document
  - shared-architecture
custom_fields:
  document_type: readme
  priority: shared
---

# Traceability Matrix Automation Scripts

This directory contains Python scripts for automated generation, validation, and maintenance of traceability matrices for the AI-Driven Specification-Driven Development (SDD) framework.

Note: See README.md → “Using This Repo” for path mapping and validator guidance specific to this repository.

Path mapping reminder: Examples often show a `docs/` prefix. In this repository, artifact directories are at the root of `ai_dev_flow/` — drop the `docs/` prefix when running commands here.

## Traceability Rules (REQUIRED vs OPTIONAL)

All validation scripts enforce these centralized traceability rules:

| Document Type | Upstream Traceability | Downstream Traceability |
|---------------|----------------------|------------------------|
| **BRD** | OPTIONAL (to other BRDs) | OPTIONAL |
| **All Other Documents** | REQUIRED | OPTIONAL |

**Key Rules**:
- **Upstream REQUIRED** (except BRD): Document MUST reference its upstream sources
- **Downstream OPTIONAL**: Only link to documents that already exist
- **No-TBD Rule**: NEVER use placeholder IDs (TBD, XXX, NNN) - leave empty or omit section

---

## Scripts Overview

### 1. generate_traceability_matrix.py

Automatically generates traceability matrices by scanning document directories and extracting metadata.

**Usage:**
```bash
python generate_traceability_matrix.py --type ADR --input ../ADR/ --output TRACEABILITY_MATRIX_ADR.md
```

**Features:**
- Scans directories for documents matching TYPE-NN pattern
- Extracts metadata from section 7 Traceability
- Calculates coverage metrics automatically
- Generates inventory tables and Mermaid diagrams
- Supports all document types: BRD, PRD, EARS, BDD, ADR, SYS, REQ, IMPL, CTR, SPEC, TASKS, IPLAN

**Parameters:**
- `--type`: Document type (required)
- `--input`: Input directory containing documents (required)
- `--output`: Output file path for generated matrix (required)
- `--template`: Path to matrix template (optional)

**Examples:**
```bash
# Generate ADR matrix
python generate_traceability_matrix.py --type ADR --input ../ADR/ --output ../ADR/TRACEABILITY_MATRIX_ADR.md

# Generate REQ matrix from specific domain
python generate_traceability_matrix.py --type REQ --input ../REQ/api/ --output ../REQ/api/matrix.md

# Generate SPEC matrix
python generate_traceability_matrix.py --type SPEC --input ../SPEC/ --output ../SPEC/TRACEABILITY_MATRIX_SPEC.md
```

---

### 2. validate_traceability_matrix.py

Validates traceability matrices against actual documents to ensure consistency and completeness.

**Usage:**
```bash
python3 validate_traceability_matrix.py --matrix TRACEABILITY_MATRIX_ADR.md --input ../ADR/
```

**Features:**
- Validates document counts match actual files
- Checks all cross-references resolve to real documents
- Verifies coverage percentages are accurate
- Identifies orphaned documents and broken links
- Generates detailed validation reports
- Supports strict mode (warnings treated as errors)

**Parameters:**
- `--matrix`: Path to traceability matrix file to validate (required)
- `--input`: Input directory containing actual documents (required)
- `--strict`: Enable strict mode (treat warnings as errors)
- `--output`: Output file for validation report (optional)

**Examples:**
```bash
# Validate ADR matrix
python3 validate_traceability_matrix.py --matrix ../ADR/TRACEABILITY_MATRIX_ADR.md --input ../ADR/

# Strict validation (warnings = errors)
python3 validate_traceability_matrix.py --matrix ../REQ/matrix.md --input ../REQ/ --strict

# Save validation report
python3 validate_traceability_matrix.py --matrix ../SPEC/matrix.md --input ../SPEC/ --output validation_report.md
```

**Exit Codes:**
- `0`: Validation passed
- `1`: Validation failed (critical errors or errors found)

---

### 3. update_traceability_matrix.py

Incrementally updates existing traceability matrices by detecting new, modified, and deleted documents.

**Usage:**
```bash
python3 update_traceability_matrix.py --matrix TRACEABILITY_MATRIX_ADR.md --input ../ADR/
```

**Features:**
- Detects new documents added since last update
- Detects removed documents
- Updates metadata for changed documents
- Recalculates statistics and coverage metrics
- Preserves manual edits outside auto-generated sections
- Creates backups before updating
- Generates update changelogs

**Parameters:**
- `--matrix`: Path to traceability matrix file to update (required)
- `--input`: Input directory containing actual documents (required)
- `--dry-run`: Preview changes without modifying matrix file
- `--changelog`: Output file for update changelog (optional)

**Examples:**
```bash
# Update ADR matrix
python3 update_traceability_matrix.py --matrix ../ADR/TRACEABILITY_MATRIX_ADR.md --input ../ADR/

# Preview changes without modifying file
python3 update_traceability_matrix.py --matrix ../SPEC/matrix.md --input ../SPEC/ --dry-run

# Update and save changelog
python3 update_traceability_matrix.py --matrix ../REQ/matrix.md --input ../REQ/ --changelog changelog.md
```

---

### 4. validate_iplan_naming.py

Validates IPLAN (Implementation Plan) files against non-timestamped naming conventions.

**Usage:**
```bash
python3 validate_iplan_naming.py [base_path]
```

**Features:**
- Validates filename format: `IPLAN-NN_{descriptive_slug}.md`
- Checks sequential ID format (2+ digits, zero-padded)
- Validates descriptive slug (lowercase, underscore-separated)
- Confirms H1 ID inside file matches filename ID
- Detects sequential ID gaps (warnings only)
- Skips template files (IPLAN-TEMPLATE.md, IPLAN-00_*.md)

**Parameters:**
- `base_path`: Base directory path (optional, defaults to script parent directory)

**Examples:**
```bash
# Validate IPLAN files in default location
python3 validate_iplan_naming.py

# Validate IPLAN files in specific project
python3 validate_iplan_naming.py /path/to/project/ai_dev_flow/

# Use in CI/CD pipeline
python3 validate_iplan_naming.py || exit 1
```

**Validation Checks:**
1. **Filename Pattern**: `IPLAN-NN_{slug}.md`
2. **ID Format**: 2+ digits with zero-padding
3. **Slug Format**: Lowercase alphanumeric with underscores only, no consecutive/leading/trailing underscores
4. **H1 ID Match**: Header ID in file matches filename ID
5. **Sequential Order**: Warns if ID gaps exist (non-blocking)

**Exit Codes:**
- `0`: Validation passed (warnings allowed)
- `1`: Validation failed (errors found)

**Example Output:**
```
Validating IPLAN files in: IPLAN/
================================================================================

✅ IPLAN Naming Validation PASSED
================================================================================
All IPLAN files follow naming conventions.
```

**Error Examples:**
```
❌ IPLAN Naming Validation FAILED
================================================================================

ERRORS:
  • IPLAN-01_test_20251113_140000.md: ID must be 3-4 digits (found 2 digits)
  • IPLAN-01_Test_Plan_20251113_140000.md: Slug must be lowercase (found 'Test_Plan')
  • IPLAN-01_test-plan_20251313_140000.md: Invalid month 13 (expected 1-12)
  • IPLAN-01_test-plan_20251113_140000.md: H1 ID mismatch (filename has IPLAN-01, H1 has IPLAN-02)

⚠️  WARNINGS:
  • Sequential gap: Expected IPLAN-02, found IPLAN-03 in IPLAN-03_refactor_20251114_100000.md
```

---

### 5. validate_documentation_paths.py

Validates path references in markdown documentation to identify broken links, missing files, and path inconsistencies.

**Usage:**
```bash
python3 validate_documentation_paths.py [--strict] [--root PATH]
```

**Features:**
- Detects broken markdown links (space characters, invalid syntax)
- Identifies missing referenced files
- Detects case mismatches in file references
- Validates path resolution and existence
- Filters out intentional placeholders and example references
- Supports severity levels: HIGH, MEDIUM, LOW

**Parameters:**
- `--strict`: Exit with non-zero status if HIGH or MEDIUM issues found (optional)
- `--root`: Root directory to scan (optional, defaults to framework root)

**Examples:**
```bash
# Validate all documentation paths
python3 validate_documentation_paths.py

# Strict mode for CI/CD pipelines
python3 validate_documentation_paths.py --strict

# Validate specific project
python3 validate_documentation_paths.py --root /path/to/project/
```

**Validation Checks:**
1. **Broken Links** (HIGH): Space characters in paths, invalid syntax
2. **Missing Files** (HIGH): Referenced files that don't exist
3. **Case Mismatches** (MEDIUM): Incorrect filename case
4. **Path Resolution** (MEDIUM): Incorrect relative path depths

**Placeholder Detection:**
Automatically skips intentional placeholders:
- Template patterns: `XXX`, `NNN`, `PPP`, `{variable}`
- Example IDs: `BRD-NN`, `REQ-NN`, `ADR-NN`, etc.
- Example keywords: `example`, `some_`, `your_`, `_file`

**Exit Codes:**
- `0`: Validation passed (no HIGH severity issues)
- `1`: Validation failed (HIGH severity issues found) OR strict mode with MEDIUM issues

**Example Output:**
```
Scanning documentation in: /opt/data/docs_flow_framework
Found 118 markdown files

================================================================================
DOCUMENTATION PATH VALIDATION REPORT
================================================================================

Total Issues Found: 0
  HIGH:   0
  MEDIUM: 0
  LOW:    0

✅ No issues found! All documentation paths are valid.

================================================================================

✅ VALIDATION PASSED
```

**Error Examples:**
```
HIGH SEVERITY ISSUES
--------------------------------------------------------------------------------

ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md:966
  [HIGH] SPACE_IN_LINK
  Space character in link path: '(.. /DOCUMENT_ID_CORE_RULES.md)'
  💡 Suggestion: Remove space: change '(.. /' to '(../'

.claude/skills/doc-flow/SKILL.md:860
  [HIGH] MISSING_FILE
  Referenced file not found: '../../PROJECT_CORE_PRINCIPLES.md'
  💡 Suggestion: Verify the file exists or update the link
```

---

### 13. validate_cross_document.py

Cross-document validation for the SDD framework. Validates semantic consistency between documents across all layers, ensuring proper traceability and reference integrity.

**Usage:**
```bash
# Per-document validation (Phase 1) - nested folder structure (DEFAULT)
python scripts/validate_cross_document.py --document docs/ADR/ADR-NN_cloud_migration/ADR-NN.0_cloud_migration_index.md --auto-fix

# Layer validation (Phase 2)
python scripts/validate_cross_document.py --layer ADR --auto-fix

# Full validation (Phase 3)
python scripts/validate_cross_document.py --full --auto-fix
```

**Features:**
- Validates cumulative tagging hierarchy (Layer N must have all tags from Layers 1 to N-1)
- Verifies referenced upstream documents exist
- Checks cross-document links resolve correctly
- Auto-fixes missing tags, broken links, and formatting issues
- Creates .bak backup files before applying fixes
- Enforces strict hierarchy (missing upstream removes dependent functionality)
- Three validation phases: per-document, per-layer, full project

**Parameters:**
- `--document`: Path to specific document to validate
- `--layer`: Validate all documents in a specific layer (BRD, PRD, EARS, etc.)
- `--full`: Run full project validation across all layers
- `--auto-fix`: Automatically fix detected issues without confirmation
- `--strict`: Treat warnings as errors
- `--output`: Output file for validation report (optional)

**Examples:**
```bash
# Validate single REQ document with auto-fix
python scripts/validate_cross_document.py --document docs/REQ/REQ-NN_api_validation.md --auto-fix

# Validate all SPEC documents
python scripts/validate_cross_document.py --layer SPEC --auto-fix

# Full validation before release
python scripts/validate_cross_document.py --full --auto-fix --strict

# Generate validation report
python scripts/validate_cross_document.py --full --output validation_report.md
```

**Validation Codes:**

| Code | Description | Severity | Auto-Fix |
|------|-------------|----------|----------|
| XDOC-001 | Referenced requirement ID not found | ERROR | No |
| XDOC-002 | Missing cumulative tag | ERROR | Yes |
| XDOC-003 | Upstream document not found | ERROR | No |
| XDOC-004 | Link target file missing | WARNING | No |
| XDOC-005 | Anchor in link not found | WARNING | No |
| XDOC-006 | Tag format invalid | ERROR | Yes |
| XDOC-007 | Gap in cumulative tag chain | ERROR | Yes |
| XDOC-008 | Circular reference detected | ERROR | No |
| XDOC-009 | Missing traceability section | ERROR | Yes |
| XDOC-010 | Orphaned document (no upstream refs) | WARNING | No |

**Layer-Specific Tag Requirements:**

| Layer | Artifact | Required Tags | Count |
|-------|----------|---------------|-------|
| 1 | BRD | (none - root) | 0 |
| 2 | PRD | @brd | 1 |
| 3 | EARS | @brd, @prd | 2 |
| 4 | BDD | @brd, @prd, @ears | 3 |
| 5 | ADR | @brd, @prd, @ears, @bdd | 4 |
| 6 | SYS | @brd, @prd, @ears, @bdd, @adr | 5 |
| 7 | REQ | @brd, @prd, @ears, @bdd, @adr, @sys | 6 |
| 8 | IMPL | @brd through @req | 7 |
| 9 | CTR | @brd through @req (+ optional @impl) | 7-8 |
| 10 | SPEC | @brd through @req (+ optional @impl, @ctr) | 7-9 |
| 11 | TASKS | @brd through @spec (+ optional @impl, @ctr) | 8-10 |
| 12 | IPLAN | @brd through @tasks (+ optional @impl, @ctr) | 9-11 |

**Auto-Fix Actions:**

| Issue | Fix Action |
|-------|------------|
| Missing cumulative tag | Add tag with placeholder reference to upstream document |
| Invalid tag format | Correct to TYPE.NN.TT.SS or TYPE-NN format |
| Broken relative link | Recalculate path from current document location |
| Missing traceability section | Insert standard traceability section from template |
| Incorrect Document Control format | Apply standardized format |

**Validation Phases:**

1. **Phase 1 (Per-Document)**: Run immediately after creating each artifact
   - Validates single document
   - Must pass with 0 errors before proceeding

2. **Phase 2 (Per-Layer)**: Run when all documents in a layer are complete
   - Validates all documents in specified layer
   - Cross-validates internal references within layer

3. **Phase 3 (Full Validation)**: Run before major milestones
   - Validates entire project
   - Checks cross-layer consistency
   - Generates comprehensive report

**Exit Codes:**
- `0`: Validation passed
- `1`: Validation failed (errors found)

**Example Output:**
```
Cross-Document Validation Report
================================================================================
Phase: Per-Document
Document: docs/REQ/REQ-NN_api_validation.md
Layer: 7 (REQ)

Checking cumulative tags...
  ✅ @brd: BRD.NN.NN.NN
  ✅ @prd: PRD.NN.NN.NN
  ✅ @ears: EARS.NN.24.NN
  ✅ @bdd: BDD.NN.13.NN
  ✅ @adr: ADR-NN, ADR-NN
  ✅ @sys: SYS.NN.25.NN

Checking upstream references...
  ✅ BRD-NN exists: docs/BRD/BRD-NN_platform/BRD-NN.0_platform_index.md
  ✅ PRD-NN exists: docs/PRD/PRD-NN_integration/PRD-NN.0_integration_index.md
  ✅ EARS-NN exists: docs/EARS/EARS-NN_risk.md
  ✅ BDD-NN exists: docs/BDD/BDD-NN_limits/BDD-NN.1_limits.feature
  ✅ ADR-NN exists: docs/ADR/ADR-NN_database/ADR-NN.0_database_index.md
  ✅ SYS-NN exists: docs/SYS/SYS-NN_example.md

Checking internal links...
  ✅ 12 links validated

================================================================================
✅ VALIDATION PASSED - 0 errors, 0 warnings
================================================================================
```

---

## Bash Validation Scripts

The following bash scripts validate artifact-specific document structure and compliance:

### 6. validate_brd_template.sh

Validates Business Requirements Document (BRD) structure and template compliance.

**Usage:**
```bash
# For nested folder structure (DEFAULT)
./scripts/validate_brd_template.sh docs/BRD/BRD-01_platform_architecture/BRD-01.0_platform_architecture_index.md

# For monolithic files (OPTIONAL for <25KB)
./scripts/validate_brd_template.sh docs/BRD/BRD-01_platform_architecture.md
```

### 7. validate_req_template.sh

Validates REQ documents against the 12-section REQ v3.0 format.

**Usage:**
```bash
./scripts/validate_req_template.sh docs/REQ/REQ-01_*.md
```

### 8. validate_ctr.sh

Validates CTR (Contract) documents for dual-file format compliance (.md + .yaml).

**Usage:**
```bash
./scripts/validate_ctr.sh docs/CTR/CTR-01_*.md
```

**Features:**
- Verifies both .md and .yaml files exist
- Validates YAML syntax
- Checks OpenAPI/JSON Schema compliance
- Validates cross-references between files

### 9. validate_impl.sh

Validates IMPL documents for 4-PART structure compliance.

**Usage:**
```bash
./scripts/validate_impl.sh docs/IMPL/IMPL-01_*.md
```

**Validates:**
- PART 1: Project Context
- PART 2: Implementation Strategy
- PART 3: Risk Management
- PART 4: Traceability

### 10. validate_tasks.sh

Validates TASKS documents including Section 8 Implementation Contracts.

**Usage:**
```bash
./scripts/validate_tasks.sh docs/TASKS/TASKS-01_*.md
```

**Features:**
- Validates 8-section TASKS format
- Checks Section 8 Implementation Contracts structure
- Verifies `@icon` tag integration
- Validates cumulative tagging hierarchy

### 11. validate_iplan.sh

Validates IPLAN (Implementation Plan) session-based execution plans.

**Usage:**
```bash
./scripts/validate_iplan.sh docs/IPLAN/IPLAN-01_*.md
```

**Features:**
- Validates filename format (no timestamps)
- Checks session structure
- Verifies bash command syntax
- Validates cumulative tagging (Layers 1-11)

### 12. validate_icon.sh

Validates ICON (Implementation Contracts) documents.

**Usage:**
```bash
./scripts/validate_icon.sh docs/ICON/ICON-01_*.md
```

**Features:**
- Validates contract type definitions
- Checks provider/consumer documentation
- Verifies protocol interface syntax
- Validates `@icon` tag references

### 13. validate_ears.py

Comprehensive EARS document validator against EARS_VALIDATION_RULES.md.

**Usage:**
```bash
python3 validate_ears.py                                # Validate all EARS docs
python3 validate_ears.py --path docs/EARS/EARS-01.md    # Validate single file
python3 validate_ears.py --verbose                       # Show all checks
python3 validate_ears.py --fix-suggestions               # Show fix commands
```

**Features:**
- Validates metadata (tags, custom_fields, document_type)
- Checks EARS syntax patterns (WHEN-THE-SHALL-WITHIN)
- Validates requirement ID format (EARS.NN.TT.SSS)
- Verifies traceability tags (@brd, @prd)
- Checks structural sections (Document Control, Traceability)
- Detects malformed tables and formatting issues

**Validation Categories:**
- **Metadata Rules**: Required tags, custom fields, document type
- **Structure Rules**: Required sections (Document Control, Purpose, Traceability)
- **EARS Syntax**: Event-driven, state-driven, unwanted, ubiquitous patterns
- **Requirement IDs**: 4-segment format validation (EARS.NN.TT.SSS)
- **Traceability**: Source document references and tags

### 14. validate_ears_duplicates.sh

Validates EARS documents for duplicate requirement IDs within individual files.

**Usage:**
```bash
./validate_ears_duplicates.sh                    # Use default docs/EARS/
./validate_ears_duplicates.sh /path/to/EARS/     # Custom EARS directory
```

**Features:**
- Detects duplicate requirement IDs within same file
- Extracts requirement IDs using pattern matching
- Reports duplicates with clear error messages
- Provides file-level duplicate analysis

**Exit Codes:**
- `0`: No duplicates found
- `1`: Duplicates detected
- `2`: Invalid arguments or directory not found

**Example Output:**
```
========================================
EARS Duplicate Requirement ID Check
========================================
Directory: docs/EARS/

✅ No duplicate requirement IDs found
Files checked: 11
```

### 15. validate_ears_consistency.sh

Validates structural consistency across all EARS documents for required sections.

**Usage:**
```bash
./validate_ears_consistency.sh                      # Use default, warning mode
./validate_ears_consistency.sh docs/EARS/           # Custom directory
./validate_ears_consistency.sh docs/EARS/ --strict  # Strict mode (fail on missing References)
```

**Required Sections (Critical):**
- Document Control (metadata)
- BDD-Ready Score (quality gate)
- Document Revision History (change tracking)
- Traceability section (upstream/downstream)
- @brd and @prd tags (cumulative tagging)

**Optional Sections (Warning):**
- References section (documentation standards)

**Features:**
- Batch validation across all EARS files
- Critical vs. non-critical section detection
- Strict mode for References section enforcement
- Clear pass/warning/fail status per file

**Exit Codes:**
- `0`: All checks passed or only warnings
- `1`: Critical validation failures
- `2`: Invalid arguments or directory not found

**Example Output:**
```
========================================
EARS Structural Consistency Check
========================================
Directory: docs/EARS/
Strict mode: false

Checking EARS-01_analytics_platform.md...
  ✅ All checks passed

Checking EARS-04_vector_search_embeddings.md...
  ⚠  Missing References section (non-blocking)
  ⚠  Passed with warnings

========================================
Files checked: 11
Files passed: 11
Files with warnings: 8
========================================
✅ All structural consistency checks passed
Note: 8 file(s) have non-blocking warnings
```

---

## Workflow Integration

### Typical Workflow

**1. Initial Matrix Creation**
```bash
# Create new matrix from scratch
python generate_traceability_matrix.py --type ADR --input ../ADR/ --output ../ADR/TRACEABILITY_MATRIX_ADR.md

# Validate newly created matrix
python3 validate_traceability_matrix.py --matrix ../ADR/TRACEABILITY_MATRIX_ADR.md --input ../ADR/
```

**2. Incremental Updates**
```bash
# After adding new ADR documents, update matrix incrementally
python3 update_traceability_matrix.py --matrix ../ADR/TRACEABILITY_MATRIX_ADR.md --input ../ADR/

# Validate updates
python3 validate_traceability_matrix.py --matrix ../ADR/TRACEABILITY_MATRIX_ADR.md --input ../ADR/
```

**3. Regular Validation**
```bash
# Run validation as part of CI/CD pipeline
python3 validate_traceability_matrix.py --matrix ../ADR/TRACEABILITY_MATRIX_ADR.md --input ../ADR/ --strict

# Validate IPLAN naming conventions
python3 validate_iplan_naming.py
```

### Pre-Commit Hook Example

Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash

# Validate all traceability matrices before commit
echo "Validating traceability matrices..."

python3 scripts/validate_traceability_matrix.py --matrix ADR/TRACEABILITY_MATRIX_ADR.md --input ADR/ || exit 1
python3 scripts/validate_traceability_matrix.py --matrix REQ/TRACEABILITY_MATRIX_REQ.md --input REQ/ || exit 1
python3 scripts/validate_traceability_matrix.py --matrix SPEC/TRACEABILITY_MATRIX_SPEC.md --input SPEC/ || exit 1

echo "Validating IPLAN naming conventions..."
python3 scripts/validate_iplan_naming.py || exit 1

echo "All validations passed successfully!"
```

### CI/CD Integration Example

Add to `.github/workflows/validate-docs.yml`:
```yaml
name: Validate Documentation

on: [push, pull_request]

jobs:
  validate-matrices:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Validate ADR Matrix
        run: |
          python3 scripts/validate_traceability_matrix.py \
            --matrix ADR/TRACEABILITY_MATRIX_ADR.md \
            --input ADR/ \
            --strict

      - name: Validate REQ Matrix
        run: |
          python3 scripts/validate_traceability_matrix.py \
            --matrix REQ/TRACEABILITY_MATRIX_REQ.md \
            --input REQ/ \
            --strict

      - name: Validate SPEC Matrix
        run: |
          python3 scripts/validate_traceability_matrix.py \
            --matrix SPEC/TRACEABILITY_MATRIX_SPEC.md \
            --input SPEC/ \
            --strict

      - name: Validate IPLAN Naming
        run: |
          python3 scripts/validate_iplan_naming.py
```

---

## Supported Document Types

All scripts support the following document types:

| Type | Description | Pattern |
|------|-------------|---------|
| BRD | Business Requirements Document | `BRD-NN_*.md` |
| PRD | Product Requirements Document | `PRD-NN_*.md` |
| EARS | Event-Action-Response-State (Engineering Requirements) | `EARS-NN_*.md` |
| BDD | Behavior-Driven Development | `BDD-NN_*.feature` |
| ADR | Architecture Decision Record | `ADR-NN_*.md` |
| SYS | System Requirements | `SYS-NN_*.md` |
| REQ | Atomic Requirements | `REQ-NN_*.md` |
| IMPL | Implementation Plans | `IMPL-NN_*.md` |
| CTR | API Contracts | `CTR-NN_*.md`, `CTR-NN_*.yaml` |
| SPEC | Technical Specifications | `SPEC-NN_*.yaml` |
| TASKS | Code Generation Tasks | `TASKS-NN_*.md` |
| IPLAN | Session Implementation Plans | `IPLAN-NN_*.md` |

Document IDs support both formats:
- Simple: `TYPE-NN` (e.g., `ADR-01`)
- Section files: `TYPE-NN.S` (e.g., `REQ-010.1`)

---

## Requirements

**Python**: 3.7+

**Standard Library Only**: No external dependencies required. Scripts use only Python standard library modules:
- `argparse`
- `os`, `pathlib`
- `re`
- `SYS`
- `datetime`
- `shutil`
- `typing`
- `collections`

---

## Testing

Run scripts with example matrices to verify functionality:

```bash
# Test generation (will warn about missing documents)
python generate_traceability_matrix.py --type ADR --input ../ADR/examples/ --output /tmp/test_matrix.md

# Test validation (use generated matrix)
python3 validate_traceability_matrix.py --matrix /tmp/test_matrix.md --input ../ADR/examples/

# Test update in dry-run mode
python3 update_traceability_matrix.py --matrix /tmp/test_matrix.md --input ../ADR/examples/ --dry-run
```

---

## Troubleshooting

### Common Issues

**Issue**: "Matrix file not found"
- **Solution**: Check that the matrix file path is correct and file exists

**Issue**: "Input directory not found"
- **Solution**: Verify the input directory path is correct and directory exists

**Issue**: "Cannot detect document type from matrix filename"
- **Solution**: Ensure matrix filename contains document type (e.g., `TRACEABILITY_MATRIX_ADR.md`)

**Issue**: "Matrix claims X documents but found Y"
- **Solution**: Run update script to sync matrix with actual documents

**Issue**: "Orphaned documents" warnings
- **Solution**: Review documents without upstream traceability, add links to upstream sources in section 7

---

## Script Design

All three scripts follow consistent design principles:

**Object-Oriented Design:**
- `DocumentMetadata`: Represents extracted document metadata
- `TraceabilityMatrixGenerator`: Generates matrices from documents
- `TraceabilityMatrixValidator`: Validates matrices against documents
- `TraceabilityMatrixUpdater`: Updates existing matrices

**Metadata Extraction:**
- Title from H1 heading
- Status from document control table
- Date from document control table
- Upstream sources from section 7 → Upstream Sources table
- Downstream artifacts from section 7 → Downstream Artifacts table
- Category from directory structure

**Error Handling:**
- Graceful handling of missing files
- Clear error messages
- Non-zero exit codes for failures
- Warnings for non-critical issues

---

## Example Matrices

See the `examples/` directories for example matrices where available:
- `REQ/examples/TRACEABILITY_MATRIX_REQ_EXAMPLE.md`

---

## Template References

Matrix templates for each document type:
- `BRD/BRD-00_TRACEABILITY_MATRIX-TEMPLATE.md`
- `PRD/PRD-00_TRACEABILITY_MATRIX-TEMPLATE.md`
- `EARS/EARS-00_TRACEABILITY_MATRIX-TEMPLATE.md`
- `BDD/BDD-00_TRACEABILITY_MATRIX-TEMPLATE.md`
- `ADR/ADR-00_TRACEABILITY_MATRIX-TEMPLATE.md`
- `SYS/SYS-00_TRACEABILITY_MATRIX-TEMPLATE.md`
- `REQ/REQ-00_TRACEABILITY_MATRIX-TEMPLATE.md`
- `IMPL/IMPL-00_TRACEABILITY_MATRIX-TEMPLATE.md`
- `CTR/CTR-00_TRACEABILITY_MATRIX-TEMPLATE.md`
- `SPEC/SPEC-00_TRACEABILITY_MATRIX-TEMPLATE.md`
- `TASKS/TASKS-00_TRACEABILITY_MATRIX-TEMPLATE.md`
- `IPLAN/IPLAN-00_TRACEABILITY_MATRIX-TEMPLATE.md`
- `TRACEABILITY_MATRIX_COMPLETE-TEMPLATE.md` (master template)

---

## MVP Template Validation

### Overview

MVP (Minimum Viable Product) templates provide streamlined versions of full document templates. These are single-file, monolithic templates designed for rapid development with reduced documentation overhead.

**Available MVP Templates:**
- `BRD/BRD-MVP-TEMPLATE.md` (~600 lines vs ~2,400 lines full)
- `PRD/PRD-MVP-TEMPLATE.md` (~500 lines vs ~1,400 lines full)
- `ADR/ADR-MVP-TEMPLATE.md` (~250 lines vs ~700 lines full)
- `SYS/SYS-MVP-TEMPLATE.md` (~350 lines vs ~1,024 lines full)
- `REQ/REQ-MVP-TEMPLATE.md` (~350 lines vs ~1,400 lines full)

### Validation Behavior

> **Important**: Current validation scripts are designed for full template compliance and will report errors when run against MVP templates. This is expected behavior.

**Why MVP Templates "Fail" Validation:**
1. **Section Requirements**: MVP templates have fewer sections than full templates
2. **Section Numbering**: MVP uses simplified section structure (may not be numbered 0-15)
3. **Placeholder Format**: MVPs use `# TYPE-NN:` placeholder in H1

### How to Handle MVP Template Validation

**Option 1: Exclude MVP Templates from Validation (Recommended)**

```bash
# Validate only produced documents, not templates
python3 scripts/validate_brd.py BRD/ 2>&1 | grep -v "MVP-TEMPLATE"

# Or use find to exclude MVP templates
find BRD/ -name "BRD-*.md" ! -name "*MVP-TEMPLATE*" -exec python3 scripts/validate_brd.py {} \;
```

**Option 2: Validate Produced Documents Only**

When validating a directory, validation scripts automatically detect templates via `"TEMPLATE" in filename` and apply relaxed tag validation. However, structure validation still runs.

```bash
# Validate specific produced documents (not templates)
python3 scripts/validate_brd.py BRD/BRD-01_my_project.md
python3 scripts/validate_prd.py PRD/PRD-01_my_feature.md
```

**Option 3: Accept MVP Template Errors as Expected**

When running validation on the entire framework, MVP template errors are expected and can be filtered:

```bash
# Run validation and filter MVP template results
python3 scripts/validate_all.py 2>&1 | grep -v "MVP-TEMPLATE" | grep -v "Expected for MVP"
```

### MVP Template Compliance Notes

MVP templates maintain framework compliance through:
- ✅ **YAML frontmatter** with correct metadata
- ✅ **Traceability tags** (proper `@type:` format)
- ✅ **Layer identification** (correct `layer-N-artifact` tags)
- ✅ **Document Control** section with required fields
- ⚠️ **Reduced section count** (by design, not an error)
- ⚠️ **Simplified structure** (by design, not an error)

### When to Use Full vs MVP Templates

| Scenario | Template to Use |
|----------|-----------------|
| Rapid MVP/prototype development | `*-MVP-TEMPLATE.md` |
| Production system documentation | `*-TEMPLATE.md` |
| Regulatory/audit requirements | `*-TEMPLATE.md` |
| Quick proof-of-concept | `*-MVP-TEMPLATE.md` |
| Enterprise/large-scale projects | `*-TEMPLATE.md` |
| Startup/agile environments | `*-MVP-TEMPLATE.md` |

### Future Improvement

A future enhancement may add:
- `--mvp` flag to validators for MVP-specific rules
- Separate `validate_*_mvp.py` scripts
- Automatic MVP detection with appropriate rule sets

---

**Version**: 1.2.0
**Author**: AI-Driven SDD Framework
**Last Updated**: 2026-01-03
