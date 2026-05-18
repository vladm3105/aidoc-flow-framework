# ITEST-MVP-TEMPLATE Fix Plan

**Document**: ITEST-MVP-TEMPLATE_FIX_PLAN.md
**Created**: 2026-02-26
**Status**: COMPLETED
**Priority**: Medium
**Scope**: ITEST-only (aligned with FTEST fix pattern)

## Executive Summary

This fix plan addresses **5 identified gaps** in ITEST template and schema files. Primary issues include YAML template missing cumulative tags structure, schema incomplete tag enum, and MD template missing cumulative tags section.

**Alignment Note**: Fixes follow the same pattern established in `FTEST-MVP-TEMPLATE_FIX_PLAN.md` for cross-subtype consistency.

## Gap Summary Table

| Gap ID | File | Issue | Severity |
| ------ | ---- | ----- | -------- |
| GAP-01 | ITEST-MVP-TEMPLATE.yaml | Traceability uses flat `upstream` instead of `cumulative_tags`/`type_specific` structure | HIGH |
| GAP-02 | ITEST_MVP_SCHEMA.yaml | Tag enum incomplete - missing @ears, @bdd, @adr | MEDIUM |
| GAP-03 | ITEST_MVP_SCHEMA.yaml | Traceability schema uses `upstream` instead of `cumulative_tags`/`type_specific` structure | HIGH |
| GAP-04 | ITEST-MVP-TEMPLATE.md | Section 6 missing cumulative tags subsection | MEDIUM |
| GAP-05 | ITEST-MVP-TEMPLATE.md | AI_CONTEXT missing cumulative tags mention (only lists @ctr, @sys, @spec) | LOW |

---

## Detailed Gap Analysis

### GAP-01: ITEST-MVP-TEMPLATE.yaml Missing Cumulative Tags Structure

**Location**: Lines 127-144 (traceability section)

**Current**:

```yaml
traceability:
  upstream:
    - tag: "@ctr"
      reference: "CTR-NN"
      description: "API contract specification"
    - tag: "@sys"
      reference: "SYS.NN.01.01"
      description: "System requirement"
    - tag: "@spec"
      reference: "SPEC-NN"
      description: "Technical specification"
  downstream:
    - tag: "@tasks"
      reference: "TASKS-NN"
      description: "Implementation tasks"
    - tag: "@code"
      reference: "tests/integration/test_[scope].py"
      description: "Test implementation"
```

**Required** (9 cumulative tags for Layer 10 + ITEST-specific):

```yaml
traceability:
  cumulative_tags:
    - tag: "@brd"
      reference: "BRD.NN.TT.SS"
      description: "Business requirement"
    - tag: "@prd"
      reference: "PRD.NN.TT.SS"
      description: "Product requirement"
    - tag: "@ears"
      reference: "EARS.NN.25.SS"
      description: "EARS statement"
    - tag: "@bdd"
      reference: "BDD.NN.14.SS"
      description: "BDD scenario"
    - tag: "@adr"
      reference: "ADR-NN"
      description: "Architecture decision"
    - tag: "@sys"
      reference: "SYS.NN.26.SS"
      description: "System requirement"
    - tag: "@req"
      reference: "REQ.NN.27.SS"
      description: "Atomic requirement"
    - tag: "@spec"
      reference: "SPEC-NN"
      description: "Technical specification"
    - tag: "@ctr"
      reference: "CTR-NN"
      description: "Data contract"
  type_specific:
    - tag: "@ctr"
      reference: "CTR-NN"
      description: "API contract for integration points"
    - tag: "@sys"
      reference: "SYS.NN.01.01"
      description: "System integration requirement"
  downstream:
    - tag: "@tasks"
      reference: "TASKS-NN"
      description: "Implementation tasks"
    - tag: "@code"
      reference: "tests/integration/test_[scope].py"
      description: "Test implementation"
```

**Fix**: Restructure traceability section with cumulative_tags, type_specific, and downstream subsections

---

### GAP-02: ITEST_MVP_SCHEMA.yaml Tag Enum Incomplete

**Location**: Line 236

**Current**:

```yaml
tag:
  type: string
  enum: ["@ctr", "@sys", "@spec", "@req", "@brd", "@prd"]
```

**Missing**: @ears, @bdd, @adr

**Required**:

```yaml
tag:
  type: string
  enum: ["@brd", "@prd", "@ears", "@bdd", "@adr", "@sys", "@req", "@spec", "@ctr"]
```

**Fix**: Expand enum to include all valid cumulative tags

---

### GAP-03: ITEST_MVP_SCHEMA.yaml Traceability Structure Outdated

**Location**: Lines 220-241

**Current**: Uses flat `upstream` array

**Required**: Match FTEST pattern with `cumulative_tags`, `type_specific`, and `downstream` subsections

```yaml
traceability:
  type: object
  required:
    - cumulative_tags
    - type_specific
  properties:
    cumulative_tags:
      type: array
      minItems: 3
      description: "Layer 1-9 upstream artifact references"
      items:
        type: object
        required:
          - tag
          - reference
        properties:
          tag:
            type: string
            enum: ["@brd", "@prd", "@ears", "@bdd", "@adr", "@sys", "@req", "@spec", "@ctr"]
          reference:
            type: string
          description:
            type: string
    type_specific:
      type: array
      minItems: 1
      description: "ITEST-specific traceability tags"
      items:
        type: object
        required:
          - tag
          - reference
        properties:
          tag:
            type: string
            enum: ["@ctr", "@sys"]
          reference:
            type: string
          description:
            type: string
    downstream:
      type: array
      description: "Downstream artifact references"
      items:
        type: object
        required:
          - tag
          - reference
        properties:
          tag:
            type: string
            enum: ["@tasks", "@code"]
          reference:
            type: string
          description:
            type: string
```

**Fix**: Restructure traceability schema to validate new structure with three subsections

---

### GAP-04: ITEST-MVP-TEMPLATE.md Section 6 Missing Cumulative Tags

**Location**: Lines 251-267 (Section 6. Traceability)

**Current**: Only has "6.1 Upstream References" and "6.2 Downstream References"

**Required**: Add "6.1 Cumulative Tags", "6.2 Type-Specific Tags", "6.3 Downstream References"

**Fix**: Restructure Section 6 with cumulative tags subsection

---

### GAP-05: ITEST-MVP-TEMPLATE.md AI_CONTEXT Missing Cumulative Tags

**Location**: Lines 31-44 (AI_CONTEXT block)

**Current**:

```
- Required traceability tags: @ctr, @sys, @spec.
```

**Required**:

```
- Cumulative traceability: @brd, @prd, @ears, @bdd, @adr, @sys, @req, @spec, @ctr.
- ITEST-specific tags: @ctr (contract), @sys (integration requirement).
```

**Fix**: Update AI_CONTEXT to document cumulative tag requirements

---

## Implementation Phase

### Phase 1: YAML Template and Schema Fixes (GAP-01, GAP-02, GAP-03)

**Files to modify**:

1. `ucx_flow_v3/10_TSPEC/ITEST/ITEST-MVP-TEMPLATE.yaml` - Restructure traceability
2. `ucx_flow_v3/10_TSPEC/ITEST/ITEST_MVP_SCHEMA.yaml` - Expand enum and restructure schema

**Steps**:

1. Read ITEST-MVP-TEMPLATE.yaml
2. Restructure traceability section with cumulative_tags, type_specific, downstream
3. Read ITEST_MVP_SCHEMA.yaml
4. Expand tag enum to include all cumulative tags
5. Restructure traceability schema validation
6. Verify changes

### Phase 2: MD Template Fixes (GAP-04, GAP-05)

**Files to modify**:

1. `ucx_flow_v3/10_TSPEC/ITEST/ITEST-MVP-TEMPLATE.md` - Update Section 6 and AI_CONTEXT

**Steps**:

1. Read ITEST-MVP-TEMPLATE.md
2. Update AI_CONTEXT with cumulative tags mention
3. Restructure Section 6 with cumulative tags subsection
4. Verify changes

---

## Verification Commands

```bash
# Verify YAML template has cumulative tags
grep -c "@brd" ucx_flow_v3/10_TSPEC/ITEST/ITEST-MVP-TEMPLATE.yaml
# Expected: >=1

# Verify schema validates cumulative tags
grep "@brd" ucx_flow_v3/10_TSPEC/ITEST/ITEST_MVP_SCHEMA.yaml
# Expected: Results showing @brd in enum

# Verify traceability structure in YAML
grep -n "cumulative_tags\|type_specific" ucx_flow_v3/10_TSPEC/ITEST/ITEST-MVP-TEMPLATE.yaml
# Expected: Both sections present

# Verify MD template has cumulative tags section
grep -n "Cumulative Tags" ucx_flow_v3/10_TSPEC/ITEST/ITEST-MVP-TEMPLATE.md
# Expected: Section header present

# Verify AI_CONTEXT updated
grep "cumulative" ucx_flow_v3/10_TSPEC/ITEST/ITEST-MVP-TEMPLATE.md
# Expected: Mention of cumulative traceability
```

---

## Risk Assessment

| Risk | Mitigation |
| ---- | ---------- |
| YAML schema changes break validation | Test with existing ITEST documents first |
| Template changes cause autopilot issues | Verify doc-tspec-autopilot skill compatibility |
| Backward compatibility | Existing documents remain valid (additive changes) |
| Cross-subtype inconsistency | Follow FTEST fix pattern exactly |

---

## Files Modified Summary

| File | Changes |
| ---- | ------- |
| `ITEST-MVP-TEMPLATE.yaml` | Restructure traceability with cumulative_tags, type_specific, downstream |
| `ITEST_MVP_SCHEMA.yaml` | Expand tag enum; restructure traceability schema |
| `ITEST-MVP-TEMPLATE.md` | Update AI_CONTEXT; restructure Section 6 with cumulative tags |

---

## Completion Criteria

- [x] ITEST-MVP-TEMPLATE.yaml has cumulative_tags subsection in traceability
- [x] ITEST-MVP-TEMPLATE.yaml has type_specific subsection in traceability
- [x] ITEST_MVP_SCHEMA.yaml tag enum includes all cumulative tags (@brd through @ctr)
- [x] ITEST_MVP_SCHEMA.yaml traceability schema validates new structure
- [x] ITEST-MVP-TEMPLATE.md Section 6 has cumulative tags subsection
- [x] ITEST-MVP-TEMPLATE.md AI_CONTEXT mentions cumulative tags
- [x] All verification commands pass

---

## ITEST-Specific Considerations

**Type-Specific Tags for ITEST**:
- `@ctr` - Primary: Integration tests validate API contracts
- `@sys` - Secondary: System integration requirements

**Differentiation from FTEST**:
- FTEST focuses on `@threshold` for performance thresholds
- ITEST focuses on `@ctr` for contract compliance
- Both share the same cumulative tags structure

---

## Fix Plan Self-Review

**Review Date**: 2026-02-26

### Files Already Aligned (No Changes Needed)

| File | Status | Notes |
| ---- | ------ | ----- |
| `ITEST_MVP_CREATION_RULES.md` | ALIGNED | Lines 73-86 already document cumulative tags correctly |
| `ITEST_MVP_VALIDATION_RULES.md` | ALIGNED | Lines 89-101 already have cumulative tag patterns |

### Minor Inconsistencies Noted (Non-Blocking)

| Location | Issue | Impact |
| -------- | ----- | ------ |
| `ITEST_MVP_VALIDATION_RULES.md:48` | Section 6 says "@ctr, @sys, @spec" but body (89-101) documents full cumulative tags | Low - body is correct |

### Gap Specification Improvements

| Gap | Original Issue | Improvement |
| --- | -------------- | ----------- |
| GAP-03 | "Restructure schema" - underspecified | Added full YAML schema specification with all three subsections |

---

## Version History

| Version | Date | Changes | Author |
| ------- | ---- | ------- | ------ |
| 1.2 | 2026-02-26 | All 5 gaps fixed; Status COMPLETED | System |
| 1.1 | 2026-02-26 | Self-review: Verified supporting files alignment; Enhanced GAP-03 with full schema YAML | System |
| 1.0 | 2026-02-26 | Initial fix plan with 5 gaps across 2 phases | System |
