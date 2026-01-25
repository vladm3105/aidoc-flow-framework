# CTR Validation Suite - Complete Reference

**Version:** 1.0.0  
**Framework:** AI Dev Flow  
**Layer:** 8 (Contracts)  
**Created:** 2024-01-25

## Overview

This directory contains a comprehensive validation suite for CTR (Contract) artifacts in the AI Dev Flow framework. These scripts ensure that all contracts meet Layer 8 standards for API specifications, data models, error handling, and traceability.

## Main Validators

### 1. `validate_ctr_all.sh` - Aggregate Runner
**Purpose:** Master orchestrator that runs all CTR validators sequentially  
**Usage:**
```bash
# Validate a single file
./validate_ctr_all.sh --file docs/08_CTR/CTR-01_iam.md

# Validate entire directory
./validate_ctr_all.sh --directory docs/08_CTR

# Skip specific validators
./validate_ctr_all.sh --directory docs/08_CTR --skip-quality --skip-ids
```

**Flags:**
- `--file <path>`: Validate single markdown file
- `--directory <path>`: Validate all .md files in directory
- `--skip-quality`: Skip quality gate validation
- `--skip-spec`: Skip spec-readiness scorer
- `--skip-template`: Skip template validator
- `--skip-ids`: Skip ID validator
- `--min-score <number>`: Minimum spec-readiness score to pass (default: 90)

**Output:** 
- Combined report from all validators
- Exit codes: 0 (pass), 1 (warnings), 2 (errors)

---

### 2. `validate_ctr.sh` - Template Compliance
**Purpose:** Validates markdown file structure against CTR-MVP-TEMPLATE.md  
**Usage:**
```bash
./validate_ctr.sh docs/08_CTR/CTR-01_iam.md
```

**Checks (12 total):**
1. Filename format (CTR-NN_name.md)
2. YAML frontmatter (artifact_type, layer, contract_type)
3. Document control table (required fields)
4. Required sections (Overview, API Spec, Data Models, Error Handling, Versioning, Traceability)
5. API endpoint validation (summary table required)
6. Data model validation (typed schemas)
7. Error handling section (HTTP error codes documented)
8. Versioning strategy (semantic versioning, breaking changes)
9. Element ID format validation
10. Traceability tags (7+ required: @brd, @prd, @ears, @bdd, @adr, @sys, @req, @spec)
11. YAML companion file validation
12. OpenAPI/Swagger compliance

**Output:**
- Detailed check results with ✅/❌ status
- Error summaries and recommendations
- Exit codes: 0 (pass), 1 (warnings), 2 (errors)

---

### 3. `validate_ctr_ids.py` - ID & Filename Consistency
**Purpose:** Validates CTR ID format and consistency across files  
**Usage:**
```bash
python3 validate_ctr_ids.py <file_or_directory>
```

**Validations:**
- Filename matches CTR-NN pattern
- H1 heading contains CTR ID
- No duplicate IDs in corpus
- Consistent naming convention across project

**Output:**
- ID extraction report
- Duplicate detection
- Format compliance summary

---

### 4. `validate_ctr_spec_readiness.py` - Readiness Scorer
**Purpose:** Scores CTR completeness 0-100% for SPEC generation readiness  
**Usage:**
```bash
python3 validate_ctr_spec_readiness.py <file_or_directory>
```

**Scoring Dimensions (10 points each = 100%):**
1. API Specification section presence
2. Data Models with type annotations
3. Error Handling section
4. Versioning strategy
5. Testing guidance
6. Endpoint definitions (summary table)
7. OpenAPI 3.0+ specification reference
8. No placeholder text remaining
9. Type annotations (Pydantic-style)
10. Recovery strategies & examples

**Threshold:** ≥90% required for MVP readiness  
**Features:**
- Ignores placeholders inside code blocks
- Flexible section pattern matching
- Per-file and aggregate scoring

**Output:**
- Percentage score per file
- Breakdown of passed/failed checks
- Recommendations for improvement

---

### 5. `validate_ctr_quality_score.sh` - Quality Gates
**Purpose:** Corpus-level quality validation (15 gates)  
**Usage:**
```bash
./validate_ctr_quality_score.sh docs/08_CTR
```

**Gates:**
1. No placeholder text remaining (FUTURE, TBD, TODO)
2. All CTR files have required frontmatter
3. All CTRs have Document Control tables
4. Index file lists all planned CTRs
5. Index file references existing contracts
6. No orphaned YAML files (without .md partner)
7. Endpoint counts consistent across files
8. Error codes documented (not generic)
9. No circular dependencies between contracts
10. Version bumps documented in changelogs
11. All CTRs have YAML companions (.yaml files)
12. All required tags present in traceability section
13. No duplicate contract IDs
14. File sizes within reasonable bounds (5KB-50KB)
15. Cross-references are resolvable

**Output:**
- Gate-by-gate results
- Aggregate pass/fail with warnings
- Recommendations per failed gate

---

## Test Utilities (in `/utils`)

### `test_yaml_check.sh`
Isolated test for YAML companion file validation logic.  
**Purpose:** Debug YAML syntax checking in isolation

### `test_tags.sh`
Isolated test for traceability tag detection.  
**Purpose:** Debug tag grep patterns before full validation

---

## Quick Start for New Projects

### 1. Setup
```bash
cd your_project/ai_dev_flow/08_CTR/scripts
# All validators are ready to use
```

### 2. Create CTR Template
```bash
cp ../CTR-MVP-TEMPLATE.md ../CTR-NN_name.md
# Fill in your contract details
```

### 3. Validate
```bash
# Quick validation of single file
./validate_ctr_all.sh --file ../CTR-NN_name.md

# Detailed template check
./validate_ctr.sh ../CTR-NN_name.md

# Check ID consistency
python3 validate_ctr_ids.py ../CTR-NN_name.md

# Check spec-readiness score
python3 validate_ctr_spec_readiness.py ../CTR-NN_name.md
```

### 4. Final Quality Check
```bash
# Validate entire directory before merge
./validate_ctr_all.sh --directory ..

# Check corpus-level quality
./validate_ctr_quality_score.sh ..
```

---

## Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| **0** | ✅ PASS | No errors or warnings. Ready to merge. |
| **1** | ⚠️ WARNING | Warnings present but no errors. Review and merge with caution. |
| **2** | ❌ ERROR | Critical errors found. Fix before merging. |

---

## Common Issues & Fixes

### Issue: SPEC-Readiness Score too low (< 90%)
**Cause:** Missing sections or incomplete documentation  
**Fix:**
1. Run spec-readiness validator: `python3 validate_ctr_spec_readiness.py CTR-01_*.md`
2. Check which checks failed
3. Add missing content (e.g., endpoint table, error codes)
4. Re-validate

### Issue: Traceability tags not found
**Cause:** Tag format incorrect  
**Expected:** `@brd:`, `@prd:`, `@ears:`, etc.  
**Fix:** Check tag section in traceability markdown, ensure tags are on own lines with `:` suffix

### Issue: YAML companion file not found
**Cause:** Missing .yaml file or wrong filename  
**Expected:** If CTR-01_iam.md exists, need CTR-01_iam.yaml  
**Fix:** Generate .yaml companion file with OpenAPI 3.0 schema

### Issue: Placeholder text still present
**Cause:** [TBD], (future), etc. left in document  
**Fix:** Search and replace all placeholder patterns; ignore placeholders inside code blocks

---

## Framework Integration

These validators integrate with the **AI Dev Flow Framework**:
- **Template:** CTR-MVP-TEMPLATE.md (14-section structure)
- **Standards:** ID_NAMING_STANDARDS.md (CTR-NN format)
- **Readiness:** 90% SPEC-readiness threshold for MVP
- **Tagging:** 8 traceability tags required (@brd, @prd, @ears, @bdd, @adr, @sys, @req, @spec)

---

## Development & Customization

### Extending validate_ctr.sh
1. Add new CHECK section following existing pattern
2. Use flexible regex patterns (avoid hardcoded section numbers)
3. Update check count in summary
4. Test with isolated script in `/utils/`

### Extending validate_ctr_quality_score.sh
1. Add new GATE section
2. Use grep -F for literal strings (avoid regex issues)
3. Increment TOTAL_GATES count
4. Document new gate in README

### Extending validate_ctr_spec_readiness.py
1. Add new scoring dimension (10 points each)
2. Update CHECKS list with new pattern
3. Update total points calculation
4. Test with sample CTR files

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| **1.0.0** | 2024-01-25 | Initial validation suite: validate_ctr_all, validate_ctr, validate_ctr_ids, validate_ctr_spec_readiness, validate_ctr_quality_score |

---

## License & Attribution

Part of the **AI Dev Flow Framework**  
Framework Location: `/opt/data/docs_flow_framework/ai_dev_flow/`  
Last Updated: 2024-01-25
