# Implementation Plan - BDD Documentation Consistency Fix

**Created**: 2025-11-30 13:09:01 EST
**Status**: ✅ Completed
**Completed**: 2025-11-30 EST

## Objective

Fix 8 inconsistencies across BDD documentation files (templates, creation rules, validation rules, and schema) to ensure they are fully aligned and ready for BDD generation.

## Context

A comprehensive review of BDD documentation revealed:
- **Overall Assessment**: 85% ready, with 8 inconsistencies to resolve
- **Root Cause**: Documents evolved independently without cross-validation
- **Impact**: Potential validation failures, incorrect status assignments, and confusion during BDD generation

### Key Decisions
- ADR-Ready Score should be **mandatory** (not optional)
- Tag format standardized to include space after colon: `@brd: BRD-NNN:REQ-ID`
- Cumulative tagging (@brd, @prd, @ears) is mandatory for Layer 4 artifacts
- Score-to-status mapping must be enforced in schema

## Task List

### Completed
- [x] Step 1: BDD_CREATION_RULES.md - Fix field count (6 → 7 mandatory)
- [x] Step 2: BDD_CREATION_RULES.md - Add ADR-Ready Score format specification
- [x] Step 3: BDD_CREATION_RULES.md - Add explicit step ordering rule
- [x] Step 4: BDD_SCHEMA.yaml - Make ADR-Ready Score required field
- [x] Step 5: BDD_SCHEMA.yaml - Add cumulative tagging enforcement
- [x] Step 6: BDD_SCHEMA.yaml - Add @threshold pattern validation
- [x] Step 7: BDD_SCHEMA.yaml - Add score-status consistency validation
- [x] Step 8: BDD-TEMPLATE.feature - Verify tag spacing consistency (already correct)
- [x] Step 9: BDD-000_TRACEABILITY_MATRIX-TEMPLATE.md - Fix tag spacing
- [x] Final: Validate all changes are aligned across documents

## Implementation Guide

### Prerequisites
- Read current versions of all 4 files before editing
- Understand YAML schema structure

### Files to Modify

| File | Changes |
|------|---------|
| `ai_dev_flow/BDD/BDD_CREATION_RULES.md` | 3 changes |
| `ai_dev_flow/BDD/BDD_SCHEMA.yaml` | 4 changes |
| `ai_dev_flow/BDD/BDD-TEMPLATE.feature` | 1 verification |
| `ai_dev_flow/BDD/BDD-000_TRACEABILITY_MATRIX-TEMPLATE.md` | 1 change |

### Execution Order

1. **BDD_SCHEMA.yaml** (Steps 4-7) - Schema is reference for validation
2. **BDD_CREATION_RULES.md** (Steps 1-3) - Rules must align with schema
3. **BDD-TEMPLATE.feature** (Step 8) - Template must match rules
4. **BDD-000_TRACEABILITY_MATRIX-TEMPLATE.md** (Step 9) - Examples must match format

### Detailed Changes

#### Step 1: BDD_CREATION_RULES.md - Fix Field Count (Section 3)
**Location**: Section 3 "Document Control Requirements"
**Change**: Update "6 mandatory fields" to:
```markdown
**Required Document Control Fields (7 mandatory)**:
1. Project Name
2. Document Version
3. Date
4. Document Owner
5. Prepared By
6. Status
7. ADR-Ready Score (format: `✅ NN% (Target: ≥90%)`)
```

#### Step 2: BDD_CREATION_RULES.md - Add ADR-Ready Score Format (Section 7)
**Location**: Section 7 "ADR-Ready Scoring System"
**Add**:
```markdown
**ADR-Ready Score Format**: `✅ NN% (Target: ≥90%)`
- Must include checkmark emoji (✅)
- Percentage as 2-digit integer
- Target threshold in parentheses
- Example: `✅ 85% (Target: ≥90%)`
```

#### Step 3: BDD_CREATION_RULES.md - Add Step Ordering (Section 5)
**Location**: Section 5 "Scenario Types and Structure"
**Add**:
```markdown
**Step Ordering Rule**: Steps MUST follow this sequence:
1. Given (preconditions) - FIRST
2. When (actions) - SECOND
3. Then (outcomes) - THIRD
4. And/But (continuations) - After any step type

Invalid: `When` before `Given`, or `Then` before `When`
```

#### Step 4: BDD_SCHEMA.yaml - Make ADR-Ready Score Required
**Location**: `document_control.required_fields` section
**Change**: Move `adr_ready_score` from optional to required_fields list

#### Step 5: BDD_SCHEMA.yaml - Add Cumulative Tagging Enforcement
**Location**: `traceability` section
**Add**:
```yaml
cumulative_tagging:
  enabled: true
  required_upstream_tags:
    - "@brd"
    - "@prd"
    - "@ears"
  enforcement: mandatory
  error_code: "E014"
  error_message: "BDD artifacts require @brd, @prd, and @ears traceability tags"
```

#### Step 6: BDD_SCHEMA.yaml - Add @threshold Pattern
**Location**: `valid_tag_patterns` section
**Add**:
```yaml
threshold:
  pattern: "@threshold: PRD-\\d{3}:[a-z_]+\\.[a-z_]+"
  description: "Threshold registry reference for quantitative values"
  example: "@threshold: PRD-035:perf.api.p95_latency"
  required: false
```

#### Step 7: BDD_SCHEMA.yaml - Add Score-Status Validation
**Location**: `validation_rules` section
**Add**:
```yaml
score_status_consistency:
  rule: "ADR-Ready Score must match document Status"
  mappings:
    - score_range: ">=90"
      required_status: "Approved"
    - score_range: "70-89"
      required_status: "In Review"
    - score_range: "<70"
      required_status: "Draft"
  severity: error
  error_code: "E015"
```

#### Step 8: BDD-TEMPLATE.feature - Verify Tag Spacing
**Location**: Gherkin header comments
**Verify**: All traceability tags use space after colon:
- `@brd: BRD-NNN:REQ-ID`
- `@prd: PRD-NNN:REQ-ID`
- `@ears: EARS-NNN:STMT-ID`

#### Step 9: BDD-000_TRACEABILITY_MATRIX-TEMPLATE.md - Fix Tag Spacing
**Location**: Section 4 "Cumulative Tagging Hierarchy"
**Change**: Update examples to use consistent spacing with space after colon

### Verification

After implementation, verify:
1. **Field Count Alignment**: All 4 BDD docs agree on 7 required fields
2. **Tag Regex Test**: `@brd: BRD-001:FR-001` matches schema pattern
3. **Score-Status Test**: 85% score with "In Review" status passes
4. **Cumulative Tag Test**: Missing @ears tag triggers E014 error

## References

- **Files**:
  - `ai_dev_flow/BDD/BDD-TEMPLATE.feature`
  - `ai_dev_flow/BDD/BDD_CREATION_RULES.md`
  - `ai_dev_flow/BDD/BDD_SCHEMA.yaml`
  - `ai_dev_flow/BDD/BDD_VALIDATION_RULES.md` (reference only)
  - `ai_dev_flow/BDD/BDD-000_TRACEABILITY_MATRIX-TEMPLATE.md`
- **Related Plans**: None
- **Documentation**: `ai_dev_flow/TRACEABILITY.md`

## Inconsistencies Summary

| # | Issue | Files Affected | Fix |
|---|-------|---------------|-----|
| 1 | Field count: 6 vs 7 mandatory | CREATION_RULES, SCHEMA | Standardize to 7 |
| 2 | ADR-Ready Score format missing | CREATION_RULES | Add format spec |
| 3 | Tag spacing inconsistent | TEMPLATE, MATRIX | Use space after colon |
| 4 | Scenario requirements unclear | SCHEMA, VALIDATION | Clarify mandatory vs recommended |
| 5 | Cumulative tagging not enforced | SCHEMA | Add enforcement rule |
| 6 | Score-status mapping missing | SCHEMA | Add validation rule |
| 7 | @threshold pattern missing | SCHEMA | Add pattern |
| 8 | Step ordering implicit | CREATION_RULES | Make explicit |
