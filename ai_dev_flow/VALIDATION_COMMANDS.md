---
title: "Validation Commands Reference (Framework-Wide)"
tags:
  - validation
  - cli-reference
  - framework-guide
custom_fields:
  document_type: reference-guide
  artifact_type: framework-support
  priority: high
  version: "1.0"
  scope: all-document-types
---

# Validation Commands Reference

Complete CLI reference for validators across all SDD document types (BRD, PRD, EARS, BDD, ADR, SYS, REQ, CTR, SPEC, TASKS).

**Quick Navigation:**
- [REQ Validation](#req-validation) - Requirements documents
- [BRD/PRD/EARS Validation](#brdprdears-validation) - Business requirements
- [SPEC Validation](#spec-validation) - Technical specifications
- [Cross-Document Validation](#cross-document-validation) - Framework-wide

**For architectural guidance**, see [VALIDATION_STRATEGY_GUIDE.md](./VALIDATION_STRATEGY_GUIDE.md).

**For decision-making**, see [AI_VALIDATION_DECISION_GUIDE.md](./AI_VALIDATION_DECISION_GUIDE.md).

---

## REQ Validation

### Master Orchestrator: validate_all.sh

**Location:** `ai_dev_flow/07_REQ/scripts/validate_all.sh`

**Purpose:** Single entry point for all REQ validation workflows

#### Usage

```bash
# Single file validation
bash validate_all.sh --file <file.md>

# Directory validation
bash validate_all.sh --directory <folder>

# Custom SPEC-ready threshold (default: 90%)
bash validate_all.sh --directory <folder> --min-score 85

# Skip specific validators
bash validate_all.sh --directory <folder> --skip-quality --skip-spec
```

#### Examples

```bash
# File-level validation
bash validate_all.sh --file docs/07_REQ/REQ-06.01_cloud_run_deployment.md

# Directory-level validation
bash validate_all.sh --directory docs/07_REQ/REQ-06_f6_infrastructure

# Quick check (skip heavy gates)
bash validate_all.sh --directory . --skip-quality
```

---

### 1. Quality Gate Validator

**Script:** `validate_req_quality_score.sh` (directory-level)

**Purpose:** Run 14 quality gates on REQ corpus

```bash
./validate_req_quality_score.sh <directory>
```

**Gates (14 total):**
- Placeholder detection (TBD, TODO, FIXME)
- ID uniqueness
- Traceability tags (@brd, @prd, @ears)
- Template format (11 sections)
- Domain classification
- Diagram syntax
- Spec-ready content sections
- And 7 more...

**Output:**
```
GATE-01: ✓ PASS
GATE-02: ✓ PASS
GATE-03: ⚠ WARN
...
Total: 14 gates, 12 passed, 2 warnings
```

---

### 2. SPEC-Readiness Scorer

**Script:** `validate_req_spec_readiness.py` (file or directory)

**Purpose:** Score REQ files on readiness for SPEC generation (0-100%)

#### Single File
```bash
python3 validate_req_spec_readiness.py --req-file <file.md>
```

#### Directory
```bash
python3 validate_req_spec_readiness.py --directory <folder> --min-score 90
```

**Scoring Factors:**
- Protocol/ABC definitions presence
- Pydantic models count
- Exception classes count
- YAML config presence
- Element completeness

**Output:**
```
SPEC-Ready Score: 92/100 ✓ PASS
✓ Protocol definitions present
✓ Pydantic models: 3
✓ Exception classes: 2
✓ YAML config present
```

---

### 3. Template Compliance Validator

**Script:** `validate_req_template.sh` (file-level only)

**Purpose:** Validate 11-section MVP template structure

```bash
./validate_req_template.sh <file.md>
```

**Checks:**
- All 11 sections present
- Section order compliance
- Metadata completeness
- Template version matching

**Output:**
```
✓ All 11 sections present
✓ Metadata complete
✓ Template version: 1.0
Template validation: PASS
```

---

### 4. ID Format Validator

**Script:** `validate_requirement_ids.py` (file or directory)

**Purpose:** Validate REQ ID format (REQ-NN.MM), no duplicates, hierarchical organization

#### Single File
```bash
python3 validate_requirement_ids.py --req-file <file.md>
```

#### Directory
```bash
python3 validate_requirement_ids.py --directory <folder>
```

**Checks:**
- ID format compliance (REQ-NN.MM)
- No duplicate IDs
- Hierarchical organization
- Filename consistency

**Output:**
```
✓ ID format valid: REQ-06.01
✓ No duplicate IDs
✓ Hierarchical structure valid
ID validation: PASS
```

---

### 5. Cross-Links Generator (GATE-05 Helper)

**Script:** `add_crosslinks_req.py` (pre-validation step)

**Purpose:** Auto-populate section 10.5 with @depends and @discoverability tags

```bash
python3 add_crosslinks_req.py --req-num <number>
python3 add_crosslinks_req.py --folder <path>
```

**Example:**
```bash
python3 add_crosslinks_req.py --req-num 8
# Output: ✓ Added cross-links to 73 file(s)
```

**Scope:** REQ-03 through REQ-11 (292+ files, 98% coverage)

---

## BRD/PRD/EARS Validation

### Master Validator: validate_all.sh

**Location:** `ai_dev_flow/01_BRD/scripts/validate_all.sh` (or 02_PRD, 03_EARS)

**Purpose:** Unified validation for business requirements documents

#### Usage

```bash
# File validation
bash validate_all.sh --file <brd-file.md>

# Directory validation
bash validate_all.sh --directory <folder>

# Custom readiness threshold
bash validate_all.sh --directory <folder> --min-score 85
```

**Note:** Validators and gates differ from REQ. See REQ-specific documentation at `ai_dev_flow/07_REQ/VALIDATION_COMMANDS.md`.

---

## SPEC Validation

### Master Validator: validate_all.sh

**Location:** `ai_dev_flow/09_SPEC/scripts/validate_all.sh`

**Purpose:** Validate technical specifications against requirements

#### Usage

```bash
# Single SPEC file
bash validate_all.sh --file <spec-file.md>

# SPEC folder
bash validate_all.sh --directory <folder>
```

**Scope:** Code generation readiness, API contract validation, schema compliance.

---

## Cross-Document Validation

### Framework-Wide Validation

**Command:**
```bash
# From project root, validate all documents
python3 scripts/validate_framework.py --all

# Validate specific document type
python3 scripts/validate_framework.py --type REQ

# Validate with strict rules
python3 scripts/validate_framework.py --strict
```

**Checks:**
- Traceability across layers (BRD → PRD → EARS → BDD → REQ)
- ID naming consistency
- Cross-reference integrity
- Tag completeness

---

## Exit Codes (Standard)

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Pass (no errors) | Continue |
| 1 | Warnings only | Review & continue |
| 2 | Errors present | Fix & retry |

---

## Common Patterns

### 1. Pre-Commit Validation (Single File)
```bash
cd ai_dev_flow/07_REQ/scripts
bash validate_all.sh --file path/to/file.md
```

### 2. Release Validation (Directory)
```bash
cd ai_dev_flow/07_REQ/scripts
bash validate_all.sh --directory /full/path/to/REQ-06_infrastructure
```

### 3. CI/CD Integration (Full Project)
```bash
#!/bin/bash
cd /path/to/docs
bash ai_dev_flow/07_REQ/scripts/validate_all.sh --directory ai_dev_flow/07_REQ || exit 1
echo "✓ All REQ validations passed"
```

### 4. Iterative Development (Quick Check)
```bash
# Skip heavy gates for faster feedback
bash validate_all.sh --directory . --skip-quality
```

---

## Troubleshooting

### Permission Denied

```bash
# Make scripts executable
chmod +x ai_dev_flow/*/scripts/*.sh
chmod +x ai_dev_flow/*/scripts/*.py
```

### Module Not Found (Python)

```bash
# Use python3 explicitly
python3 validate_requirement_ids.py --req-file <file>
```

### Path Not Found

```bash
# Use absolute paths
bash /absolute/path/to/validate_all.sh --file /absolute/path/to/file.md
```

### Validation Passes Locally, Fails in CI

```bash
# Ensure CI environment has all dependencies
# Use absolute paths in CI scripts
# Check working directory before running validators
```

---

## Related Documentation

- [VALIDATION_STRATEGY_GUIDE.md](./VALIDATION_STRATEGY_GUIDE.md) - Architecture, gates, patterns
- [AI_VALIDATION_DECISION_GUIDE.md](./AI_VALIDATION_DECISION_GUIDE.md) - Decision-making framework
- [VALIDATION_DECISION_FRAMEWORK.md](./VALIDATION_DECISION_FRAMEWORK.md) - Universal validation rules
- [VALIDATION_STANDARDS.md](./VALIDATION_STANDARDS.md) - Error codes and standards

---

**Last Updated:** 2026-01-24  
**Scope:** Framework-wide validation commands for all SDD document types  
**Audience:** All SDD users (engineers, architects, validators)
