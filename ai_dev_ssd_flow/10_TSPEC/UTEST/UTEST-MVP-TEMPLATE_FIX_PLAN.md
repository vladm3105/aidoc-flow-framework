# UTEST-MVP-TEMPLATE Fix Plan

**Document**: UTEST-MVP-TEMPLATE_FIX_PLAN.md
**Created**: 2026-02-26
**Status**: COMPLETED
**Priority**: Medium
**Scope**: UTEST-only (aligned with FTEST/ITEST fix patterns)

## Executive Summary

This fix plan addresses **5 identified gaps** in UTEST template and schema files. Primary issues include YAML template using `upstream` instead of `cumulative_tags`/`type_specific` structure, schema using deprecated structure, and MD template lacking cumulative tags section.

**Alignment Note**: Fixes follow the same pattern established in `FTEST-MVP-TEMPLATE_FIX_PLAN.md` and `ITEST-MVP-TEMPLATE_FIX_PLAN.md` for cross-subtype consistency.

**Note**: UTEST has unique type_specific tags (@req, @spec) that focus on atomic requirements and specifications.

## Gap Summary Table

| Gap ID | File | Issue | Severity |
| ------ | ---- | ----- | -------- |
| GAP-01 | UTEST-MVP-TEMPLATE.yaml | Traceability uses `upstream` instead of `cumulative_tags`/`type_specific` structure | HIGH |
| GAP-02 | UTEST_MVP_SCHEMA.yaml | Traceability uses `upstream` instead of `cumulative_tags`/`type_specific` structure | HIGH |
| GAP-03 | UTEST_MVP_SCHEMA.yaml | x-validation-rules reference `upstream` instead of `type_specific` | MEDIUM |
| GAP-04 | UTEST-MVP-TEMPLATE.md | Section 6 missing cumulative tags subsection | MEDIUM |
| GAP-05 | UTEST-MVP-TEMPLATE.md | AI_CONTEXT only mentions @req, @spec - should include cumulative tags | LOW |

---

## Detailed Gap Analysis

### GAP-01: UTEST-MVP-TEMPLATE.yaml Uses Wrong Traceability Structure

**Location**: Lines 114-128 (traceability section)

**Current**:

```yaml
traceability:
  upstream:
    - tag: "@req"
      reference: "REQ.NN.10.01"
      description: "[Requirement title]"
    - tag: "@spec"
      reference: "SPEC-NN"
      description: "[Specification reference]"
  downstream:
    - tag: "@tasks"
      reference: "TASKS-NN"
      description: "Implementation tasks"
    - tag: "@code"
      reference: "tests/unit/test_[component].py"
      description: "Test implementation"
```

**Required** (9 cumulative tags for Layer 10 + UTEST-specific):

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
      description: "Data contract (if exists)"
  type_specific:
    - tag: "@req"
      reference: "REQ.NN.10.01"
      description: "Atomic requirement for unit coverage"
    - tag: "@spec"
      reference: "SPEC-NN"
      description: "Specification section reference"
  downstream:
    - tag: "@tasks"
      reference: "TASKS-NN"
      description: "Implementation tasks"
    - tag: "@code"
      reference: "tests/unit/test_[component].py"
      description: "Test implementation"
```

**Fix**: Restructure traceability section with cumulative_tags, type_specific, and downstream subsections

---

### GAP-02: UTEST_MVP_SCHEMA.yaml Uses Wrong Traceability Structure

**Location**: Lines 284-319 (traceability property)

**Current**:

```yaml
traceability:
  type: object
  required:
    - upstream
  properties:
    upstream:
      type: array
      minItems: 2
      items:
        type: object
        required:
          - tag
          - reference
        properties:
          tag:
            type: string
            enum: ["@req", "@spec", "@brd", "@prd", "@ears", "@bdd", "@adr", "@sys", "@ctr"]
          reference:
            type: string
          description:
            type: string
    downstream:
      ...
```

**Required** (aligned with FTEST/ITEST schema):

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
      description: "UTEST-specific traceability tags"
      items:
        type: object
        required:
          - tag
          - reference
        properties:
          tag:
            type: string
            enum: ["@req", "@spec"]
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
            enum: ["@tasks", "@code", "@impl"]
          reference:
            type: string
          description:
            type: string
```

**Fix**: Restructure schema traceability to validate new structure with three subsections

---

### GAP-03: UTEST_MVP_SCHEMA.yaml x-validation-rules Reference "upstream"

**Location**: Lines 322-328 (x-validation-rules section)

**Current**:

```yaml
x-validation-rules:
  req_tag_required:
    description: "At least one @req tag must be present in upstream traceability"
    check: "upstream contains tag='@req'"
  spec_tag_required:
    description: "At least one @spec tag must be present in upstream traceability"
    check: "upstream contains tag='@spec'"
```

**Required**:

```yaml
x-validation-rules:
  req_tag_required:
    description: "At least one @req tag must be present in type_specific traceability"
    check: "type_specific contains tag='@req'"
  spec_tag_required:
    description: "At least one @spec tag must be present in type_specific traceability"
    check: "type_specific contains tag='@spec'"
```

**Fix**: Update x-validation-rules to reference `type_specific` instead of `upstream`

---

### GAP-04: UTEST-MVP-TEMPLATE.md Section 6 Missing Cumulative Tags

**Location**: Lines 259-275 (Section 6. Traceability)

**Current**: Only has "6.1 Upstream References" and "6.2 Downstream References"

**Required**: Add "6.1 Cumulative Tags (Layer 1-9)", "6.2 UTEST-Specific Tags", "6.3 Downstream References"

```markdown
### 6.1 Cumulative Tags (Layer 1-9)

| Tag | Reference | Description |
|-----|-----------|-------------|
| @brd | BRD.NN.TT.SS | Business requirement |
| @prd | PRD.NN.TT.SS | Product requirement |
| @ears | EARS.NN.25.SS | EARS statement |
| @bdd | BDD.NN.14.SS | BDD scenario |
| @adr | ADR-NN | Architecture decision |
| @sys | SYS.NN.26.SS | System requirement |
| @req | REQ.NN.27.SS | Atomic requirement |
| @spec | SPEC-NN | Technical specification |
| @ctr | CTR-NN | Data contract (if exists) |

### 6.2 UTEST-Specific Tags

| Tag | Reference | Description |
|-----|-----------|-------------|
| @req | REQ.NN.10.01 | Atomic requirement for unit coverage |
| @spec | SPEC-NN | Specification section reference |

### 6.3 Downstream References

| Tag | Reference | Description |
|-----|-----------|-------------|
| @tasks | TASKS-NN | Implementation tasks |
| @code | `tests/unit/test_[component].py` | Test implementation |
```

**Fix**: Restructure Section 6 with cumulative tags subsection

---

### GAP-05: UTEST-MVP-TEMPLATE.md AI_CONTEXT Incomplete

**Location**: Lines 31-43 (AI_CONTEXT block)

**Current**:

```markdown
Constraints:
- Required traceability tags: @req, @spec.
```

**Required**:

```markdown
Constraints:
- Required cumulative tags: @brd, @prd, @ears, @bdd, @adr, @sys, @req, @spec, @ctr (if exists).
- Required UTEST-specific tags: @req (atomic requirement), @spec (specification).
```

**Fix**: Update AI_CONTEXT to document cumulative tag requirements

---

## Implementation Phase

### Phase 1: YAML Template and Schema Fixes (GAP-01, GAP-02, GAP-03)

**Files to modify**:

1. `ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST-MVP-TEMPLATE.yaml` - Restructure traceability
2. `ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST_MVP_SCHEMA.yaml` - Update traceability structure and x-validation-rules

**Steps**:

1. Read UTEST-MVP-TEMPLATE.yaml
2. Restructure traceability section with cumulative_tags, type_specific, downstream
3. Read UTEST_MVP_SCHEMA.yaml
4. Update traceability property to use cumulative_tags, type_specific structure
5. Update x-validation-rules to reference type_specific instead of upstream
6. Verify changes

### Phase 2: MD Template Fixes (GAP-04, GAP-05)

**Files to modify**:

1. `ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST-MVP-TEMPLATE.md` - Update Section 6 and AI_CONTEXT

**Steps**:

1. Read UTEST-MVP-TEMPLATE.md
2. Update AI_CONTEXT with cumulative tags mention
3. Restructure Section 6 with cumulative tags subsection
4. Verify changes

---

## Verification Commands

```bash
# Verify YAML template has cumulative tags
grep -c "@brd" ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST-MVP-TEMPLATE.yaml
# Expected: >=1

# Verify traceability structure in YAML
grep -n "cumulative_tags\|type_specific" ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST-MVP-TEMPLATE.yaml
# Expected: Both sections present

# Verify schema has cumulative_tags structure
grep -n "cumulative_tags\|type_specific" ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST_MVP_SCHEMA.yaml
# Expected: Both sections present

# Verify MD template has cumulative tags section
grep -n "Cumulative Tags" ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST-MVP-TEMPLATE.md
# Expected: Section header present

# Verify AI_CONTEXT updated
grep "cumulative" ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST-MVP-TEMPLATE.md
# Expected: Mention of cumulative tags

# Verify x-validation-rules updated (reference type_specific)
grep "type_specific" ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST_MVP_SCHEMA.yaml
# Expected: Multiple results including x-validation-rules
```

---

## Risk Assessment

| Risk | Mitigation |
| ---- | ---------- |
| YAML schema changes break validation | Test with existing UTEST documents first |
| Template changes cause autopilot issues | Verify doc-tspec-autopilot skill compatibility |
| Backward compatibility | Existing documents remain valid (additive changes) |
| Cross-subtype inconsistency | Follow FTEST/ITEST fix pattern exactly |
| UTEST-specific tags differ from other subtypes | Maintain @req, @spec in type_specific section |

---

## Files Modified Summary

| File | Changes |
| ---- | ------- |
| `UTEST-MVP-TEMPLATE.yaml` | Restructure traceability with cumulative_tags, type_specific, downstream |
| `UTEST_MVP_SCHEMA.yaml` | Update traceability property and x-validation-rules |
| `UTEST-MVP-TEMPLATE.md` | Update AI_CONTEXT; restructure Section 6 with cumulative tags |

---

## Completion Criteria

- [x] UTEST-MVP-TEMPLATE.yaml has cumulative_tags subsection in traceability
- [x] UTEST-MVP-TEMPLATE.yaml has type_specific subsection in traceability
- [x] UTEST_MVP_SCHEMA.yaml traceability uses cumulative_tags, type_specific structure
- [x] UTEST_MVP_SCHEMA.yaml x-validation-rules reference type_specific (not upstream)
- [x] UTEST-MVP-TEMPLATE.md Section 6 has cumulative tags subsection
- [x] UTEST-MVP-TEMPLATE.md AI_CONTEXT mentions cumulative tags
- [x] All verification commands pass

---

## UTEST-Specific Considerations

**Type-Specific Tags for UTEST**:
- `@req` - Primary: Unit tests validate atomic requirements
- `@spec` - Secondary: Specification section references

**Differentiation from Other Subtypes**:
- FTEST focuses on `@sys, @threshold` for functional/performance thresholds
- ITEST focuses on `@ctr, @sys` for contract compliance
- PTEST focuses on `@sys, @spec` for performance baselines
- SECTEST focuses on `@sec, @spec, @ctr` for security requirements
- STEST focuses on `@ears, @bdd, @req` for smoke test behavior
- UTEST focuses on `@req, @spec` for atomic unit coverage

All share the same 9 cumulative tags structure.

---

## Self-Review

**Review Date**: 2026-02-26

### Files Already Aligned (No Changes Needed)

| File | Status | Notes |
| ---- | ------ | ----- |
| `UTEST_MVP_CREATION_RULES.md` | ALIGNED | Lines 87-91 already document cumulative tags correctly |
| `UTEST_MVP_VALIDATION_RULES.md` | ALIGNED | Lines 93-97 already have cumulative tag patterns |

### Schema Tag Enum Status

| Current | Status | Notes |
| ------- | ------ | ----- |
| Tag enum includes all 9 tags | ALIGNED | Line 300 has complete enum |

**Note**: Schema tag enum is already correct, only structure needs update.

---

## Consistency Check with Other Subtypes

| Element | FTEST | ITEST | STEST | UTEST (After Fix) |
| ------- | ----- | ----- | ----- | ----------------- |
| cumulative_tags section | Yes (9 tags) | Yes (9 tags) | Yes (9 tags) | Yes (9 tags) |
| type_specific section | @sys, @threshold | @ctr, @sys | @ears, @bdd, @req | @req, @spec |
| downstream section | @tasks, @code | @tasks, @code | @tasks, @code, @pipeline | @tasks, @code |
| Schema structure | cumulative_tags/type_specific | cumulative_tags/type_specific | cumulative_tags/type_specific | cumulative_tags/type_specific |
| MD cumulative section | 6.1 Cumulative Tags | 6.1 Cumulative Tags | 6.1 Cumulative Tags | 6.1 Cumulative Tags |

---

## Version History

| Version | Date | Changes | Author |
| ------- | ---- | ------- | ------ |
| 1.1 | 2026-02-26 | All 5 gaps fixed; Status COMPLETED | System |
| 1.0 | 2026-02-26 | Initial fix plan with 5 gaps across 2 phases | System |
