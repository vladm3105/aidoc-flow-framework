# REQ Validation Commands Reference

All validation tools for REQ documents with correct command syntax.

## Quick Reference

```bash
# 1. Quality Gate Validator (16 gates including domain validation)
./validate_req_quality_score.sh <directory>

# 2. SPEC-Readiness Scorer
python3 validate_req_spec_readiness.py --req-file <file.md>
python3 validate_req_spec_readiness.py --directory <folder> [--min-score 90]

# 3. Template Compliance Checker
./validate_req_template.sh <file.md>

# 4. Requirement ID Validator
python3 validate_requirement_ids.py --req-file <file.md> [--all-checks]
python3 validate_requirement_ids.py --directory <folder> [--all-checks]
```

---

## 1. Quality Gate Validator (Corpus-Level)

**Script**: `validate_req_quality_score.sh`  
**Purpose**: Run all 16 quality gates on a corpus of REQ files

### Usage
```bash
cd /opt/data/docs_flow_framework/ai_dev_flow/07_REQ/scripts
./validate_req_quality_score.sh <directory_path>
```

### Example
```bash
# Validate entire REQ-01 corpus
./validate_req_quality_score.sh /opt/data/trading_nexus_v4.2/Nexus_Platform_v4.2/docs/07_REQ/REQ-01_f1_iam

# Validate all REQs
./validate_req_quality_score.sh /opt/data/trading_nexus_v4.2/Nexus_Platform_v4.2/docs/07_REQ
```

### What It Checks (16 Gates)
- GATE-01: Placeholder text detection
- GATE-02: Heading structure compliance
- GATE-03: Broken internal references
- GATE-04: Broken traceability tags
- GATE-05: Required frontmatter metadata
- GATE-06: Implementation_Type allowed values
- GATE-07: Priority field validation
- GATE-08: Status field validation
- GATE-09: Implementation_Phase format
- GATE-10: Requirement Category validation
- GATE-11: Cumulative traceability tags presence
- GATE-12: SPEC-Ready content sections
- **GATE-13: Domain subdirectory classification (metadata)**
- GATE-14: SPEC-Ready quality threshold (≥90)
- GATE-15: 11-section MVP format compliance
- GATE-16: Element numbering scheme validation

### Output
```
✓ All 16 gates passed
Total Errors: 0
Total Warnings: 0
Files Validated: 12
```

---

## 2. SPEC-Readiness Scorer

**Script**: `validate_req_spec_readiness.py`  
**Purpose**: Score individual files or directories for SPEC-generation readiness

### Usage
```bash
cd /opt/data/docs_flow_framework/ai_dev_flow/07_REQ/scripts

# Single file
python3 validate_req_spec_readiness.py --req-file <file.md>

# Directory (all REQ-*.md files)
python3 validate_req_spec_readiness.py --directory <folder>

# Custom threshold (default: 90)
python3 validate_req_spec_readiness.py --directory <folder> --min-score 85
```

### Example
```bash
# Score specific file
python3 validate_req_spec_readiness.py \
  --req-file /opt/data/trading_nexus_v4.2/Nexus_Platform_v4.2/docs/07_REQ/REQ-01_f1_iam/REQ-01.01_jwt_authentication.md

# Score entire corpus
python3 validate_req_spec_readiness.py \
  --directory /opt/data/trading_nexus_v4.2/Nexus_Platform_v4.2/docs/07_REQ/REQ-01_f1_iam \
  --min-score 90
```

### What It Scores
- Protocol/ABC definitions presence
- Pydantic models count
- Exception classes count
- YAML config presence
- Element completeness
- Overall SPEC-ready percentage

### Output
```
SPEC-Ready Score: 95/100
✓ Protocol/ABC definitions present
✓ Pydantic models: 3
✓ Exception classes: 2
✓ YAML config present
```

---

## 3. Template Compliance Checker

**Script**: `validate_req_template.sh`  
**Purpose**: Validate individual file against REQ-MVP-TEMPLATE.md structure

### Usage
```bash
cd /opt/data/docs_flow_framework/ai_dev_flow/07_REQ/scripts
./validate_req_template.sh <file.md>
```

### Example
```bash
# Validate single file
./validate_req_template.sh \
  /opt/data/trading_nexus_v4.2/Nexus_Platform_v4.2/docs/07_REQ/REQ-01_f1_iam/REQ-01.01_jwt_authentication.md
```

### What It Checks
- Frontmatter metadata completeness
- Required sections present (11-section MVP format)
- Section order compliance
- Template version matching
- SPEC-Ready content presence

### Output
```
✓ Template validation passed
Errors: 0
Warnings: 1 (⚠️ Template Version: 1.0 vs expected 1.1)
```

---

## 4. Requirement ID Validator

**Script**: `validate_requirement_ids.py`  
**Purpose**: Validate ID patterns, element codes, and section structure

### Usage
```bash
cd /opt/data/docs_flow_framework/ai_dev_flow/07_REQ/scripts

# Single file
python3 validate_requirement_ids.py --req-file <file.md> [--all-checks]

# Directory
python3 validate_requirement_ids.py --directory <folder> [--all-checks]

# Specific checks
python3 validate_requirement_ids.py --req-file <file.md> --check-id-patterns
python3 validate_requirement_ids.py --req-file <file.md> --check-element-codes
python3 validate_requirement_ids.py --req-file <file.md> --check-v2-sections
```

### Example
```bash
# Full validation on single file
python3 validate_requirement_ids.py \
  --req-file /opt/data/trading_nexus_v4.2/Nexus_Platform_v4.2/docs/07_REQ/REQ-01_f1_iam/REQ-01.01_jwt_authentication.md \
  --all-checks

# Check ID patterns across corpus
python3 validate_requirement_ids.py \
  --directory /opt/data/trading_nexus_v4.2/Nexus_Platform_v4.2/docs/07_REQ/REQ-01_f1_iam \
  --check-id-patterns
```

### Check Types
- **--check-v2-sections**: V2 template section compliance
- **--check-id-patterns**: ID pattern consistency (IDPAT errors)
- **--check-element-codes**: Element type codes validation (ELEM errors)
- **--all-checks**: Run all validation checks

### Output
```
✓ ID patterns valid
✓ Element codes valid
✓ V2 sections present
0 IDPAT errors
0 ELEM errors
```

---

## Unified Validation Helper (Recommended)

**Script**: `validate_all.sh` - Run all validators with one command

### Usage
```bash
cd /opt/data/docs_flow_framework/ai_dev_flow/07_REQ/scripts

# Single file (runs SPEC-readiness, template, IDs validators)
./validate_all.sh --file <file.md>

# Directory (runs quality gates, SPEC-readiness, IDs validators)
./validate_all.sh --directory <folder>

# Custom SPEC-ready threshold
./validate_all.sh --directory <folder> --min-score 85

# Skip specific validators
./validate_all.sh --file <file.md> --skip-template
./validate_all.sh --directory <folder> --skip-quality
```

### Examples
```bash
# Validate single file (all applicable checks)
./validate_all.sh --file /opt/data/trading_nexus_v4.2/Nexus_Platform_v4.2/docs/07_REQ/REQ-01_f1_iam/REQ-01.01_jwt_authentication.md

# Validate entire corpus
./validate_all.sh --directory /opt/data/trading_nexus_v4.2/Nexus_Platform_v4.2/docs/07_REQ/REQ-01_f1_iam

# Full project validation
./validate_all.sh --directory /opt/data/trading_nexus_v4.2/Nexus_Platform_v4.2/docs/07_REQ
```

### Output
```
╔══════════════════════════════════════════════════════════════════╗
║              REQ VALIDATION SUITE                                ║
╚══════════════════════════════════════════════════════════════════╝

Mode:   file
Target: /path/to/file.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶ SPEC-Readiness Validator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
...
✓ SPEC-Readiness Validator PASSED

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶ Template Compliance Checker
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
...
✓ Template Compliance Checker PASSED

╔══════════════════════════════════════════════════════════════════╗
║                    VALIDATION SUMMARY                            ║
╚══════════════════════════════════════════════════════════════════╝

Passed: 3
Failed: 0

✓ All validation checks passed!
```

---

## Individual Validator Workflows

### 1. Pre-Commit Validation (Single File)
```bash
# Using unified helper (recommended)
./validate_all.sh --file <file.md>

# Or individual validators:
./validate_req_template.sh <file.md>
python3 validate_req_spec_readiness.py --req-file <file.md>
python3 validate_requirement_ids.py --req-file <file.md> --all-checks
```

### 2. Corpus Validation (Directory)
```bash
# Using unified helper (recommended)
./validate_all.sh --directory <folder>

# Or individual validators:
./validate_req_quality_score.sh <directory>
python3 validate_req_spec_readiness.py --directory <directory>
python3 validate_requirement_ids.py --directory <directory> --all-checks
```

### 3. Full Project Validation
```bash
# All REQ files across all folders
cd /opt/data/trading_nexus_v4.2/Nexus_Platform_v4.2/docs/07_REQ

# Using unified helper (recommended)
/opt/data/docs_flow_framework/ai_dev_flow/07_REQ/scripts/validate_all.sh --directory .

# Or individual validators:
/opt/data/docs_flow_framework/ai_dev_flow/07_REQ/scripts/validate_req_quality_score.sh .
python3 /opt/data/docs_flow_framework/ai_dev_flow/07_REQ/scripts/validate_req_spec_readiness.py --directory .
python3 /opt/data/docs_flow_framework/ai_dev_flow/07_REQ/scripts/validate_requirement_ids.py --directory . --all-checks
```

---

## Domain Validation (GATE-13)

After domain field changes, GATE-13 validates:
- Domain field present in metadata
- Pattern: `^[a-z_]+$` (lowercase alphanumeric + underscores)
- Content-derived, not from enumerated list
- Example: `domain: auth`

**No hardcoded allowed values** - any valid identifier pattern accepted.

---

## Exit Codes

All validators follow standard exit codes:
- **0**: Success (all checks passed)
- **1**: Validation failures found
- **2**: Script error (invalid arguments, file not found)

---

## Notes

- **All scripts must be run from their directory** or use absolute paths
- **Python scripts require** `--req-file` or `--directory` flags (no positional args)
- **Bash scripts** accept positional arguments (file or directory path)
- **Permission**: All scripts are executable (755)
- **GATE-13** reads domain from metadata, not folder names
