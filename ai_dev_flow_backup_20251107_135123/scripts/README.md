# Traceability Matrix Automation Scripts

This directory contains Python scripts for automated generation, validation, and maintenance of traceability matrices for the AI-Driven Specification-Driven Development (SDD) framework.

## Scripts Overview

### 1. generate_traceability_matrix.py

Automatically generates traceability matrices by scanning document directories and extracting metadata.

**Usage:**
```bash
python generate_traceability_matrix.py --type ADR --input ../adrs/ --output TRACEABILITY_MATRIX_ADR.md
```

**Features:**
- Scans directories for documents matching TYPE-NNN pattern
- Extracts metadata from Section 7 Traceability
- Calculates coverage metrics automatically
- Generates inventory tables and Mermaid diagrams
- Supports all document types: BRD, PRD, EARS, BDD, ADR, SYS, REQ, IMPL, CTR, SPEC, TASKS

**Parameters:**
- `--type`: Document type (required)
- `--input`: Input directory containing documents (required)
- `--output`: Output file path for generated matrix (required)
- `--template`: Path to matrix template (optional)

**Examples:**
```bash
# Generate ADR matrix
python generate_traceability_matrix.py --type ADR --input ../adrs/ --output ../adrs/TRACEABILITY_MATRIX_ADR.md

# Generate REQ matrix from specific domain
python generate_traceability_matrix.py --type REQ --input ../reqs/api/ --output ../reqs/api/matrix.md

# Generate SPEC matrix
python generate_traceability_matrix.py --type SPEC --input ../specs/ --output ../specs/TRACEABILITY_MATRIX_SPEC.md
```

---

### 2. validate_traceability_matrix.py

Validates traceability matrices against actual documents to ensure consistency and completeness.

**Usage:**
```bash
python validate_traceability_matrix.py --matrix TRACEABILITY_MATRIX_ADR.md --input ../adrs/
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
python validate_traceability_matrix.py --matrix ../adrs/TRACEABILITY_MATRIX_ADR.md --input ../adrs/

# Strict validation (warnings = errors)
python validate_traceability_matrix.py --matrix ../reqs/matrix.md --input ../reqs/ --strict

# Save validation report
python validate_traceability_matrix.py --matrix ../specs/matrix.md --input ../specs/ --output validation_report.md
```

**Exit Codes:**
- `0`: Validation passed
- `1`: Validation failed (critical errors or errors found)

---

### 3. update_traceability_matrix.py

Incrementally updates existing traceability matrices by detecting new, modified, and deleted documents.

**Usage:**
```bash
python update_traceability_matrix.py --matrix TRACEABILITY_MATRIX_ADR.md --input ../adrs/
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
python update_traceability_matrix.py --matrix ../adrs/TRACEABILITY_MATRIX_ADR.md --input ../adrs/

# Preview changes without modifying file
python update_traceability_matrix.py --matrix ../specs/matrix.md --input ../specs/ --dry-run

# Update and save changelog
python update_traceability_matrix.py --matrix ../reqs/matrix.md --input ../reqs/ --changelog changelog.md
```

---

## Workflow Integration

### Typical Workflow

**1. Initial Matrix Creation**
```bash
# Create new matrix from scratch
python generate_traceability_matrix.py --type ADR --input ../adrs/ --output ../adrs/TRACEABILITY_MATRIX_ADR.md

# Validate newly created matrix
python validate_traceability_matrix.py --matrix ../adrs/TRACEABILITY_MATRIX_ADR.md --input ../adrs/
```

**2. Incremental Updates**
```bash
# After adding new ADR documents, update matrix incrementally
python update_traceability_matrix.py --matrix ../adrs/TRACEABILITY_MATRIX_ADR.md --input ../adrs/

# Validate updates
python validate_traceability_matrix.py --matrix ../adrs/TRACEABILITY_MATRIX_ADR.md --input ../adrs/
```

**3. Regular Validation**
```bash
# Run validation as part of CI/CD pipeline
python validate_traceability_matrix.py --matrix ../adrs/TRACEABILITY_MATRIX_ADR.md --input ../adrs/ --strict
```

### Pre-Commit Hook Example

Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash

# Validate all traceability matrices before commit
echo "Validating traceability matrices..."

python ai_dev_flow/scripts/validate_traceability_matrix.py --matrix ai_dev_flow/adrs/TRACEABILITY_MATRIX_ADR.md --input ai_dev_flow/adrs/ || exit 1
python ai_dev_flow/scripts/validate_traceability_matrix.py --matrix ai_dev_flow/reqs/TRACEABILITY_MATRIX_REQ.md --input ai_dev_flow/reqs/ || exit 1
python ai_dev_flow/scripts/validate_traceability_matrix.py --matrix ai_dev_flow/specs/TRACEABILITY_MATRIX_SPEC.md --input ai_dev_flow/specs/ || exit 1

echo "All matrices validated successfully!"
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
          python ai_dev_flow/scripts/validate_traceability_matrix.py \
            --matrix ai_dev_flow/adrs/TRACEABILITY_MATRIX_ADR.md \
            --input ai_dev_flow/adrs/ \
            --strict

      - name: Validate REQ Matrix
        run: |
          python ai_dev_flow/scripts/validate_traceability_matrix.py \
            --matrix ai_dev_flow/reqs/TRACEABILITY_MATRIX_REQ.md \
            --input ai_dev_flow/reqs/ \
            --strict

      - name: Validate SPEC Matrix
        run: |
          python ai_dev_flow/scripts/validate_traceability_matrix.py \
            --matrix ai_dev_flow/specs/TRACEABILITY_MATRIX_SPEC.md \
            --input ai_dev_flow/specs/ \
            --strict
```

---

## Supported Document Types

All scripts support the following document types:

| Type | Description | Pattern |
|------|-------------|---------|
| BRD | Business Requirements Document | `BRD-NNN_*.md` |
| PRD | Product Requirements Document | `PRD-NNN_*.md` |
| EARS | Easy Approach to Requirements Syntax | `EARS-NNN_*.md` |
| BDD | Behavior-Driven Development | `BDD-NNN_*.feature` |
| ADR | Architecture Decision Record | `ADR-NNN_*.md` |
| SYS | System Requirements | `SYS-NNN_*.md` |
| REQ | Atomic Requirements | `REQ-NNN_*.md` |
| IMPL | Implementation Plans | `IMPL-NNN_*.md` |
| CTR | API Contracts | `CTR-NNN_*.md`, `CTR-NNN_*.yaml` |
| SPEC | Technical Specifications | `SPEC-NNN_*.yaml` |
| TASKS | Code Generation Tasks | `TASKS-NNN_*.md` |

Document IDs support both formats:
- Simple: `TYPE-NNN` (e.g., `ADR-001`)
- Hierarchical: `TYPE-NNN-YY` (e.g., `REQ-010-01`)

---

## Requirements

**Python**: 3.7+

**Standard Library Only**: No external dependencies required. Scripts use only Python standard library modules:
- `argparse`
- `os`, `pathlib`
- `re`
- `sys`
- `datetime`
- `shutil`
- `typing`
- `collections`

---

## Testing

Run scripts with example matrices to verify functionality:

```bash
# Test generation (will warn about missing documents)
python generate_traceability_matrix.py --type ADR --input ../adrs/examples/ --output /tmp/test_matrix.md

# Test validation (expected to find issues with example matrices)
python validate_traceability_matrix.py --matrix ../adrs/examples/TRACEABILITY_MATRIX_ADR_EXAMPLE.md --input ../adrs/examples/

# Test update in dry-run mode
python update_traceability_matrix.py --matrix ../adrs/examples/TRACEABILITY_MATRIX_ADR_EXAMPLE.md --input ../adrs/examples/ --dry-run
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
- **Solution**: Review documents without upstream traceability, add links to upstream sources in Section 7

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
- Upstream sources from Section 7 → Upstream Sources table
- Downstream artifacts from Section 7 → Downstream Artifacts table
- Category from directory structure

**Error Handling:**
- Graceful handling of missing files
- Clear error messages
- Non-zero exit codes for failures
- Warnings for non-critical issues

---

## Example Matrices

See the `examples/` directories for complete example matrices:
- `adrs/examples/TRACEABILITY_MATRIX_ADR_EXAMPLE.md`
- `reqs/examples/TRACEABILITY_MATRIX_REQ_EXAMPLE.md`
- `specs/examples/TRACEABILITY_MATRIX_SPEC_EXAMPLE.md`

---

## Template References

Matrix templates for each document type:
- `brds/BRD-000_TRACEABILITY_MATRIX-TEMPLATE.md`
- `prd/PRD-000_TRACEABILITY_MATRIX-TEMPLATE.md`
- `ears/EARS-000_TRACEABILITY_MATRIX-TEMPLATE.md`
- `bbds/BDD-000_TRACEABILITY_MATRIX-TEMPLATE.md`
- `adrs/ADR-000_TRACEABILITY_MATRIX-TEMPLATE.md`
- `sys/SYS-000_TRACEABILITY_MATRIX-TEMPLATE.md`
- `reqs/REQ-000_TRACEABILITY_MATRIX-TEMPLATE.md`
- `impl_plans/IMPL-000_TRACEABILITY_MATRIX-TEMPLATE.md`
- `contracts/CTR-000_TRACEABILITY_MATRIX-TEMPLATE.md`
- `specs/SPEC-000_TRACEABILITY_MATRIX-TEMPLATE.md`
- `ai_tasks/TASKS-000_TRACEABILITY_MATRIX-TEMPLATE.md`
- `TRACEABILITY_MATRIX_COMPLETE-TEMPLATE.md` (master template)

---

**Version**: 1.0.0
**Author**: AI-Driven SDD Framework
**Last Updated**: 2025-01-15
