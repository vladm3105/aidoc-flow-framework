# UCX v1.9.4 Changelog - BRD Validation Compliance

**Release Date**: 2026-03-11
**Focus**: QA Subcategory Codes, Section Mapping Compliance, Pattern Standardization

---

## Summary

This release brings the UCX BRD validator into full compliance with `ID_NAMING_STANDARDS.md v2.2`. Key changes include support for Quality Attribute subcategory codes (91-99), complete section-to-code mapping, and standardized traceability tag patterns.

---

## Breaking Changes

None. All changes are backward-compatible.

---

## New Features

### 1. QA Subcategory Codes (91-99)

Added hierarchical element type codes for Quality Attribute subcategories:

| Code | Element Type | BRD Section |
|------|--------------|-------------|
| **91** | Performance Requirement | 7.3 |
| **92** | Reliability Requirement | 7.4 |
| **94** | Scalability Requirement | 7.5 |
| **96** | Security Requirement | 7.6 |
| **98** | Observability Requirement | 7.7 |
| **99** | Maintainability Requirement | 7.8 |

**Rationale**: Hierarchical codes provide stronger traceability and self-documenting IDs. Pattern search capability: `grep -r "\.96\."` finds all Security requirements.

**Files Changed**:
- `UCX/ucx/validators/brd/schema.py` - Added codes to `VALID_BRD_CODES` and `SECTION_CODE_MAP`
- `UCX/ucx/validators/common/error_codes.py` - Updated BRD-E020 message
- `ai_dev_ssd_flow/scripts/validate_standardized_element_codes.py` - Added codes to validation

### 2. Complete Section-to-Code Mapping

Added missing section mappings to `SECTION_CODE_MAP`:

| Section | Code | Element Type |
|---------|------|--------------|
| 2 (Business Objectives) | 23 | Business Objective |
| **3 (Project Scope)** | **22** | **Feature Item** |
| **4 (Stakeholders)** | **24** | **Stakeholder Need** |
| 5 (User Stories) | 09 | User Story |

**Files Changed**:
- `UCX/ucx/validators/brd/schema.py`
- `ai_dev_ssd_flow/scripts/validate_standardized_element_codes.py`
- `ai_dev_ssd_flow/ID_NAMING_STANDARDS.md`
- `ai_dev_ssd_flow/01_BRD/BRD_VALIDATION_RULES.md`

### 3. Preferred Section Codes

Added `PREFERRED_SECTION_CODES` dictionary to indicate canonical codes when multiple are valid:

```python
PREFERRED_SECTION_CODES = {
    "6": "01",   # Functional Requirements (01 over 06)
    "7.2": "10", # Decision (10 over 32)
    "7.3": "91", # Performance
    "7.4": "92", # Reliability
    "7.5": "94", # Scalability
    "7.6": "96", # Security
    "7.7": "98", # Observability
    "7.8": "99", # Maintainability
    "10": "07",  # Risk (07 over 05)
}
```

---

## Bug Fixes

### 1. GATE-06 Tier Classification

**Issue**: Docstring in `quality_gate.py` stated GATE-06 was "Tier 2, advisory" but `schema.py` defined it as Tier 1.

**Fix**: Updated docstring to match schema (Tier 1 is correct per BRD_VALIDATION_RULES.md).

**File**: `UCX/ucx/validators/brd/quality_gate.py`

### 2. ADR Filename Pattern

**Issue**: ADR filename pattern used `\d{3,}` (required 3+ digits) but should allow 2+ digits like other patterns.

**Fix**: Changed to `\d{2,}` in `FILE_NAME_PATTERNS["adr"]`.

**File**: `UCX/ucx/validators/common/patterns.py`

### 3. TAG_PATTERNS Digit Requirements

**Issue**: Traceability tag patterns used `\d+` (1+ digits) but should require `\d{2,}` per ID_NAMING_STANDARDS.md.

**Fix**: Updated all TAG_PATTERNS to use `\d{2,}`:
- `@brd: BRD-\d{2,}`
- `@prd: PRD-\d{2,}`
- `@ears: EARS-\d{2,}`
- `@bdd: BDD-\d{2,}`
- `@adr: ADR-\d{2,}`
- `@sys: SYS-\d{2,}`
- `@ctr: CTR-\d{2,}`
- `@spec: SPEC-\d{2,}`
- `@tasks: TASKS-\d{2,}`
- `@ref: [A-Z]+-\d{2,}`

**File**: `UCX/ucx/validators/common/patterns.py`

### 4. REQ Tag Pattern

**Issue**: REQ tag pattern was `REQ\.\d+\.\d+\.\d+` but should match full element ID format.

**Fix**: Changed to `REQ\.\d{2,}\.\d{2}\.\d{2,}` to match `TYPE.DOC_NUM.TT.SS` format.

**File**: `UCX/ucx/validators/common/patterns.py`

### 5. BDD Element Code Reference

**Issue**: `BDD_MVP_QUALITY_GATE_VALIDATION.md` incorrectly stated code 24 for BDD scenarios.

**Fix**: Corrected to code 14 (Test Scenario) per ID_NAMING_STANDARDS.md.

**File**: `ai_dev_ssd_flow/04_BDD/BDD_MVP_QUALITY_GATE_VALIDATION.md`

---

## Documentation Updates

### Updated Files

| File | Changes |
|------|---------|
| `UCX/README.md` | Added Valid Element Type Codes section; Updated Version History |
| `UCX/ucx/validators/README.md` | Added Element Type Codes table, Section-to-Code Mapping, Tag Patterns, Changelog |
| `UCX/docs/QUICK_START.md` | Updated validation examples |
| `ai_dev_ssd_flow/ID_NAMING_STANDARDS.md` | Added QA codes 91-99; Added Section-to-Code Mapping table; Added Version History |
| `ai_dev_ssd_flow/01_BRD/BRD_VALIDATION_RULES.md` | Updated Section-Code Semantic Rules; Added v2.2 changelog |
| `ai_dev_ssd_flow/01_BRD/BRD_MVP_VALIDATION_RULES.md` | Expanded CHECK 25 element codes table; Added v1.5.0 changelog |
| `ai_dev_ssd_flow/01_BRD/BRD-MVP-TEMPLATE.md` | Added sections 7.6-7.8; Updated element codes to 91-99 |
| `ai_dev_ssd_flow/01_BRD/BRD_MVP_SCHEMA.yaml` | Changed Architecture Topic code from 32 to 10 |

### Version Synchronization

| Component | Old Version | New Version |
|-----------|-------------|-------------|
| UCX Framework | 1.9.3 | 1.9.4 |
| ID_NAMING_STANDARDS.md | 2.1 | 2.2 |
| BRD_VALIDATION_RULES.md | 2.1 | 2.2 |
| BRD_MVP_VALIDATION_RULES.md | 1.4.0 | 1.5.0 |

---

## Files Changed (23 total)

### UCX Python Package

| File | Lines Changed | Description |
|------|---------------|-------------|
| `ucx/version.py` | +15 | Version bump to 1.9.4 with changelog |
| `ucx/validators/brd/schema.py` | +40 | Added codes 91-99, Section 3/4 mappings |
| `ucx/validators/brd/element_codes.py` | +195 | Enhanced validation with preferred codes |
| `ucx/validators/brd/quality_gate.py` | +2 | Fixed GATE-06 docstring |
| `ucx/validators/brd/structure.py` | +58 | Enhanced structure validation |
| `ucx/validators/brd/__init__.py` | +1 | Export updates |
| `ucx/validators/common/patterns.py` | +24 | Fixed tag patterns and ADR filename |
| `ucx/validators/common/error_codes.py` | +2 | Updated BRD-E020 message |
| `ucx/validators/common/result.py` | +220 | Report formatting enhancements |
| `ucx/validators/common/diagrams.py` | +21 | Diagram validation improvements |
| `ucx/cli/main.py` | +46 | CLI improvements |

### UCX Documentation

| File | Lines Changed | Description |
|------|---------------|-------------|
| `UCX/README.md` | +127 | Element codes, version history |
| `UCX/ucx/validators/README.md` | +79 | Complete validator documentation |
| `UCX/docs/QUICK_START.md` | +68 | Updated examples |

### SSD Framework Documentation

| File | Lines Changed | Description |
|------|---------------|-------------|
| `ai_dev_ssd_flow/ID_NAMING_STANDARDS.md` | +60 | QA codes, section mapping, version history |
| `ai_dev_ssd_flow/01_BRD/BRD_VALIDATION_RULES.md` | +62 | Section-code rules, version history |
| `ai_dev_ssd_flow/01_BRD/BRD_MVP_VALIDATION_RULES.md` | +33 | CHECK 25 expansion |
| `ai_dev_ssd_flow/01_BRD/BRD-MVP-TEMPLATE.md` | +91 | New QA sections |
| `ai_dev_ssd_flow/01_BRD/BRD_MVP_SCHEMA.yaml` | +6 | Architecture Topic code fix |
| `ai_dev_ssd_flow/04_BDD/BDD_MVP_QUALITY_GATE_VALIDATION.md` | +2 | Element code fix |
| `ai_dev_ssd_flow/METADATA_TAGGING_GUIDE.md` | +2 | Element code reference fix |
| `ai_dev_ssd_flow/scripts/validate_standardized_element_codes.py` | +37 | Added codes 91-99, section mappings |

---

## Validation Architecture

```
┌──────────────────────────────────────────────────────┐
│        ID_NAMING_STANDARDS.md (Canonical v2.2)       │
│        - Element codes 01-32, 91-99                  │
│        - Section-to-Code mapping                     │
│        - 2+ digit DOC_NUM requirement                │
└──────────────────────────────────────────────────────┘
                        ↓ synced ↓
┌────────────────────┬────────────────────┬────────────┐
│ UCX schema.py      │ BRD_VALIDATION_    │ patterns.py│
│ VALID_BRD_CODES    │ RULES.md           │ TAG/FILE   │
│ SECTION_CODE_MAP   │ Section-Code table │ patterns   │
└────────────────────┴────────────────────┴────────────┘
```

---

## Testing

Run UCX tests to verify changes:

```bash
cd /opt/data/docs_flow_framework
source .venv/bin/activate
python -m pytest UCX/tests/ -v
```

Validate BRD documents:

```bash
ucx validate brd docs/01_BRD/BRD-01/ --tier1-only
ucx validate brd docs/01_BRD/BRD-02/ --tier1-only
```

---

## Migration Notes

### For Existing BRD Documents

1. **QA sections 7.3-7.8**: Update element IDs from code 02 to specific 91-99 codes
   - Example: `BRD.01.02.05` → `BRD.01.91.05` (Performance)

2. **Section 7.2 Architecture Decisions**: Update code 32 to code 10
   - Example: `BRD.01.32.01` → `BRD.01.10.01`

3. **New sections**: Add sections 7.6-7.8 if documenting Security, Observability, Maintainability requirements

### Backward Compatibility

- Code 02 still accepted in QA sections (legacy tolerance)
- Code 05 still accepted in Section 10 (legacy tolerance)
- Code 32 still accepted in Section 7.2 (legacy tolerance)

Validators emit warnings (BRD-W023) for legacy codes but don't fail validation.

---

## Related Documents

- [ID_NAMING_STANDARDS.md](../../../ai_dev_ssd_flow/ID_NAMING_STANDARDS.md) - Canonical element code reference
- [BRD_VALIDATION_RULES.md](../../../ai_dev_ssd_flow/01_BRD/BRD_VALIDATION_RULES.md) - Script execution contract
- [BRD_MVP_VALIDATION_RULES.md](../../../ai_dev_ssd_flow/01_BRD/BRD_MVP_VALIDATION_RULES.md) - 25 validation checks
- [validators/README.md](../ucx/validators/README.md) - Validator architecture
