---
title: "Traceability Setup Guide"
tags:
  - framework-guide
  - shared-architecture
custom_fields:
  document_type: guide
  priority: shared
  development_status: active
---

# Traceability Setup Guide

**Version**: 1.0
**Purpose**: Configure automated traceability validation for projects
**Target**: AI Assistants setting up continuous validation
**Status**: Production

---

## Overview

This guide enables AI Assistants to set up automated traceability checking, validation scripts, and CI/CD integration for maintaining complete bidirectional traceability throughout project lifecycle.

---

## Validation Scripts

### Available Scripts

Located in `scripts/` directory after project initialization:

| Script | Purpose | When to Run |
|--------|---------|-------------|
| `validate_requirement_ids.py` | Check REQ ID uniqueness and format | After creating/modifying REQ documents |
| `check_broken_references.py` | Find broken markdown links | After any document creation/modification |
| `generate_traceability_matrix.py` | Generate traceability matrix for document type | End of day, before commits |
| `validate_traceability_matrix.py` | Validate existing matrix against documents | After matrix generation |
| `update_traceability_matrix.py` | Incrementally update matrix | After document updates |
| `make_framework_generic.py` | Maintain placeholder consistency | Framework maintenance only |

---

## Quick Commands

### Tag-Based Traceability (Recommended)

**Extract all tags from codebase:**
```bash
python scripts/extract_tags.py --source src/ docs/ tests/ --output docs/generated/tags.json
```

**Validate tags against documents:**
```bash
python scripts/validate_tags_against_docs.py --tags docs/generated/tags.json --strict
```

**Generate bidirectional matrices:**
```bash
python scripts/generate_traceability_matrices.py --tags docs/generated/tags.json --output docs/generated/matrices/
```

**Complete workflow (extract → validate → generate):**
```bash
python scripts/generate_traceability_matrices.py --auto
```

**Validate only (no output):**
```bash
python scripts/extract_tags.py --validate-only
```

### Cumulative Tagging Validation (Required for Compliance)

**Validate cumulative tagging hierarchy compliance:**
```bash
python scripts/validate_tags_against_docs.py --source src/ docs/ tests/ --docs docs/ --validate-cumulative --strict
```

**What it checks:**
- Each artifact layer includes ALL required upstream tags (no gaps)
- Tag count matches expected range for each layer
- Optional layers (IMPL, CTR) handled correctly
- Tag chain completeness (e.g., if @adr exists, @brd through @bdd must exist)

**Layer-specific validation:**
```bash
# Validate specific artifact type
python scripts/validate_tags_against_docs.py \
  --artifact REQ-045 \
  --expected-layers brd,prd,ears,bdd,adr,sys \
  --strict
```

**Expected tag counts by layer:**
- Layer 1 (BRD): 0 tags (top level)
- Layer 2 (PRD): 1 tag (@brd)
- Layer 3 (EARS): 2 tags (@brd, @prd)
- Layer 4 (BDD): 3+ tags (@brd through @ears)
- Layer 5 (ADR): 4 tags (@brd through @bdd)
- Layer 6 (SYS): 5 tags (@brd through @adr)
- Layer 7 (REQ): 6 tags (@brd through @sys)
- Layer 8 (IMPL): 7 tags (@brd through @req) [optional]
- Layer 9 (CTR): 8 tags (@brd through @impl) [optional]
- Layer 10 (SPEC): 7-9 tags (@brd through @req + optional impl/ctr)
- Layer 11 (TASKS): 8-10 tags (@brd through @spec)
- Layer 12 (IPLAN): 9-11 tags (@brd through @tasks)
- Layer 13 (Code): 9-11 tags (@brd through @tasks)
- Layer 14 (Tests): 10-12 tags (@brd through @code)

**Benefits:**
- Regulatory compliance (SEC, FINRA, FDA, ISO audit trails)
- Complete impact analysis (upstream → downstream traceability)
- Automated validation prevents gaps in traceability chain
- CI/CD enforcement ensures 100% compliance

### Legacy Manual Validation (Optional)

```bash
# Validate requirement IDs
python scripts/validate_requirement_ids.py

# Check for broken links
python scripts/check_broken_references.py
```

---

## Pre-Commit Hook Setup

### Git Hooks Configuration

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Pre-commit hook for tag-based traceability validation with cumulative tagging

echo "Running tag-based traceability validation..."

# Extract and validate tags
python scripts/extract_tags.py --validate-only
if [ $? -ne 0 ]; then
  echo "❌ Tag extraction/format validation failed"
  exit 1
fi

# Validate tags against documents
python scripts/validate_tags_against_docs.py --source src/ docs/ tests/ --docs docs/ --strict
if [ $? -ne 0 ]; then
  echo "❌ Tag validation failed - orphaned or invalid tags found"
  exit 1
fi

# Validate cumulative tagging hierarchy
python scripts/validate_tags_against_docs.py --source src/ docs/ tests/ --docs docs/ --validate-cumulative --strict
if [ $? -ne 0 ]; then
  echo "❌ Cumulative tagging validation failed - missing upstream tags or gaps in chain"
  exit 1
fi

echo "✅ Traceability tag validation passed (including cumulative tagging)"
exit 0
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

### Pre-Commit Framework Configuration

Add to `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: validate-traceability-tags
        name: Validate Traceability Tags
        entry: python scripts/validate_tags_against_docs.py --source src/ docs/ tests/ --docs docs/ --strict
        language: python
        pass_filenames: false
        always_run: true

      - id: validate-cumulative-tagging
        name: Validate Cumulative Tagging Hierarchy
        entry: python scripts/validate_tags_against_docs.py --source src/ docs/ tests/ --docs docs/ --validate-cumulative --strict
        language: python
        pass_filenames: false
        always_run: true
```

---

## CI/CD Integration

### GitHub Actions Workflow

Create `.github/workflows/traceability.yml`:

```yaml
name: Tag-Based Traceability Validation

on:
  pull_request:
    paths:
      - 'src/**'
      - 'docs/**'
      - 'tests/**'
  push:
    branches:
      - main
    paths:
      - 'src/**'
      - 'docs/**'
      - 'tests/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install pyyaml

      - name: Extract Traceability Tags
        run: python scripts/extract_tags.py --source src/ docs/ tests/ --output docs/generated/tags.json

      - name: Validate Tags Against Documents
        run: python scripts/validate_tags_against_docs.py --tags docs/generated/tags.json --strict

      - name: Generate Traceability Matrices
        run: python scripts/generate_traceability_matrices.py --tags docs/generated/tags.json --output docs/generated/matrices/

      - name: Upload Generated Matrices
        uses: actions/upload-artifact@v3
        with:
          name: traceability-matrices
          path: docs/generated/matrices/
```

---

## AI Assistant Automation

### After Each Document Creation

```python
# Pseudocode for AI Assistant

def after_document_created(document_path):
    # Validate immediately
    run_command("python scripts/validate_requirement_ids.py")
    run_command("python scripts/check_broken_references.py")

    # Report results
    if validation_passed:
        print(f"✅ {document_path} validated successfully")
    else:
        print(f"❌ {document_path} has validation errors")
        print("Fix errors before proceeding")
```

### End of Day Automation

```python
# Pseudocode for AI Assistant

def end_of_day_validation():
    # Generate all matrices
    for doc_type in ["ADR", "REQ", "SPEC", "CTR"]:
        generate_matrix(doc_type)
        validate_matrix(doc_type)

    # Summary report
    print("📊 Traceability Summary:")
    print(f"  ADRs: {count_documents('ADR')}")
    print(f"  REQs: {count_documents('REQ')}")
    print(f"  SPECs: {count_documents('SPEC')}")
    print(f"  Broken links: {count_broken_links()}")
```

---

## Monitoring and Alerts

### Metrics to Track

| Metric | Threshold | Alert Action |
|--------|-----------|--------------|
| Broken references | 0 | Block commit |
| Duplicate IDs | 0 | Block commit |
| Missing Section 7 | 0 | Warning |
| Orphaned documents | <5% | Warning |
| Traceability coverage | >95% | Warning if below |

### Dashboard Integration

Integrate with Grafana/Datadog:

```python
# Example: Send metrics to monitoring system
def send_metrics():
    metrics = {
        "total_documents": count_all_documents(),
        "broken_references": count_broken_references(),
        "traceability_coverage": calculate_coverage(),
        "orphaned_documents": count_orphaned()
    }
    send_to_monitoring(metrics)
```

---

## Troubleshooting

### Common Issues

**Issue**: Broken reference to non-existent document

**Resolution**:
1. Check if referenced document exists
2. Verify file path is correct (relative from current document)
3. Verify anchor ID matches document ID
4. Example fix: `[REQ-003](../REQ/risk/REQ-003_position_limit.md#REQ-003)`

**Issue**: Duplicate requirement IDs

**Resolution**:
1. Check REQ-000_index.md for next available ID
2. Rename duplicate document with next sequential ID
3. Update all references to use new ID
4. Re-run validation

---

## References

- [TRACEABILITY.md](./TRACEABILITY.md) - Complete traceability guidelines
- [ID_NAMING_STANDARDS.md](./ID_NAMING_STANDARDS.md) - Document ID rules
- [PROJECT_KICKOFF_TASKS.md](./PROJECT_KICKOFF_TASKS.md) - Day 7 validation tasks

---

**End of Traceability Setup Guide**
