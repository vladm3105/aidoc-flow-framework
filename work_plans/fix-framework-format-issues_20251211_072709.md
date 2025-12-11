# Implementation Plan - Fix Framework Format Issues

**Created**: 2025-12-11 07:27:09 EST
**Status**: Ready for Implementation

## Objective

Fix 3 identified issues in the SDD framework to ensure production readiness:
1. Create missing BRD_SCHEMA.yaml (marked as OPTIONAL)
2. Fix validator regex pattern mismatch in validate_req_template.sh
3. Update BRD-TEMPLATE.md to reference the new optional schema

## Context

During a comprehensive framework review, the following issues were identified:

### Production Readiness Assessment Summary
- **Framework Documents**: Minor issues (1 missing schema, 1 validator mismatch)
- **Claude Skills**: READY (33 skills validated, consistent)
- **Validation Scripts**: OPERATIONAL (all scripts functional)
- **Templates**: COMPLETE (33 templates across 12 artifact types)
- **Schemas**: 11/12 complete (BRD schema intentionally missing by design, now to be added as optional)

### Key Decisions
- BRD is Layer 1 human-authored entry point - schema should be OPTIONAL, not required
- The PRD-TEMPLATE.md "bracket imbalance" on line 1047 is a FALSE POSITIVE - the interval notation `[a, b)` is mathematically correct
- Validator pattern `### Upstream Sources` doesn't match template's `### 11.1 Upstream Sources`

## Task List

### Completed
- [x] Review framework document formats and schemas
- [x] Review Claude skills for format consistency
- [x] Run validation scripts
- [x] Check cross-references and traceability
- [x] Provide production readiness assessment

### Pending
- [ ] Create `ai_dev_flow/BRD/BRD_SCHEMA.yaml` (marked as OPTIONAL)
- [ ] Fix regex patterns in `ai_dev_flow/scripts/validate_req_template.sh`
- [ ] Update `ai_dev_flow/BRD/BRD-TEMPLATE.md` schema references
- [ ] Run validation to confirm fixes

## Implementation Guide

### Prerequisites
- Access to `/opt/data/docs_flow_framework/` directory
- Reference file: `ai_dev_flow/PRD/PRD_SCHEMA.yaml` (pattern for new schema)

### Execution Steps

#### Step 1: Create BRD_SCHEMA.yaml

**File**: `ai_dev_flow/BRD/BRD_SCHEMA.yaml`

Create new file following PRD_SCHEMA.yaml pattern with key differences:
- Add header comments marking it as OPTIONAL
- Add `schema_status: optional` field
- Set `layer: 1`
- Include metadata, structure, and traceability sections

Key content to include:
```yaml
# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of BRD-TEMPLATE.md (OPTIONAL SCHEMA)
# - Authority: BRD-TEMPLATE.md is the single source of truth for BRD structure
# - Purpose: Machine-readable validation rules (OPTIONAL - Layer 1 is human-authored)
# - Usage: Optional automated validation for consistency checking
# - On conflict: Defer to BRD-TEMPLATE.md
# =============================================================================

schema_version: "1.0"
artifact_type: BRD
layer: 1
last_updated: "2025-12-11"
schema_status: optional  # BRD is human-authored, schema validation not required
```

#### Step 2: Fix validate_req_template.sh

**File**: `ai_dev_flow/scripts/validate_req_template.sh`

**Line 111**: Change from:
```bash
if grep -q "### Upstream Sources" "$REQ_FILE"; then
```
To:
```bash
if grep -q "### .*Upstream Sources" "$REQ_FILE"; then
```

**Line 118**: Change from:
```bash
if grep -q "### Downstream Artifacts" "$REQ_FILE"; then
```
To:
```bash
if grep -q "### .*Downstream Artifacts" "$REQ_FILE"; then
```

#### Step 3: Update BRD-TEMPLATE.md

**File**: `ai_dev_flow/BRD/BRD-TEMPLATE.md`

**Line 5**: Change from:
```
# - Schema: None (Layer 1 entry point, human-authored)
```
To:
```
# - Schema: BRD_SCHEMA.yaml (OPTIONAL - Layer 1 entry point, human-authored)
```

**Lines 25-26**: Change from:
```yaml
  schema_reference: "none"
  schema_version: "n/a"
```
To:
```yaml
  schema_reference: "BRD_SCHEMA.yaml"
  schema_version: "1.0"
  schema_status: optional
```

**Line 30**: Change from:
```markdown
> - **Schema**: None (Layer 1 entry point, human-authored)
```
To:
```markdown
> - **Schema**: `BRD_SCHEMA.yaml` (OPTIONAL - Layer 1 entry point, human-authored)
```

### Verification

```bash
# 1. Verify BRD schema exists and is valid YAML
ls -la ai_dev_flow/BRD/BRD_SCHEMA.yaml
python3 -c "import yaml; yaml.safe_load(open('ai_dev_flow/BRD/BRD_SCHEMA.yaml')); print('✓ Valid YAML')"

# 2. Run REQ validator - should now pass
bash ai_dev_flow/scripts/validate_req_template.sh ai_dev_flow/REQ/REQ-TEMPLATE.md

# 3. Verify BRD-TEMPLATE references updated
grep -n "schema" ai_dev_flow/BRD/BRD-TEMPLATE.md | head -10

# 4. Count all schema files (should be 12 now)
find ai_dev_flow -name "*_SCHEMA.yaml" | wc -l
```

## References

- **Plan file**: `/home/ya/.claude/plans/ancient-greeting-unicorn.md`
- **PRD Schema (reference pattern)**: `ai_dev_flow/PRD/PRD_SCHEMA.yaml`
- **BRD Template**: `ai_dev_flow/BRD/BRD-TEMPLATE.md`
- **Validator script**: `ai_dev_flow/scripts/validate_req_template.sh`
- **REQ Template**: `ai_dev_flow/REQ/REQ-TEMPLATE.md`

## Notes

- The PRD-TEMPLATE.md bracket issue on line 1047 (`[a, b)`) is NOT an error - it's correct mathematical interval notation
- BRD schema is intentionally OPTIONAL to preserve the "human-authored Layer 1 entry point" design philosophy
- The regex fix allows matching both `### Upstream Sources` and `### 11.1 Upstream Sources` heading formats
