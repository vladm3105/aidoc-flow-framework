# STEST-MVP-TEMPLATE Fix Plan

**Document**: STEST-MVP-TEMPLATE_FIX_PLAN.md
**Created**: 2026-02-26
**Status**: COMPLETED
**Priority**: Medium
**Scope**: STEST-only (aligned with FTEST/PTEST/SECTEST fix patterns)

## Executive Summary

This fix plan addresses **6 identified gaps** in STEST template and schema files. Primary issues include YAML template using `upstream` instead of `cumulative_tags`/`type_specific` structure, MD template lacking cumulative tags section, and schema missing `cumulative_tags`/`type_specific` structure.

**Reference**: This plan follows the pattern established in `FTEST-MVP-TEMPLATE_FIX_PLAN.md`, `PTEST-MVP-TEMPLATE_FIX_PLAN.md`, and `SECTEST-MVP-TEMPLATE_FIX_PLAN.md`.

**Note**: STEST has unique type_specific tags (@ears, @bdd, @req) that differ from other subtypes.

## Gap Summary Table

| Gap ID | File | Issue | Severity |
| ------ | ---- | ----- | -------- |
| GAP-01 | STEST-MVP-TEMPLATE.yaml | Traceability uses `upstream` instead of `cumulative_tags`/`type_specific` structure | HIGH |
| GAP-02 | STEST-MVP-TEMPLATE.yaml | Missing cumulative tags (@brd, @prd, @adr, @sys, @spec, @ctr) | HIGH |
| GAP-03 | STEST-MVP-TEMPLATE.md | Traceability section missing cumulative tags section | MEDIUM |
| GAP-04 | STEST-MVP-TEMPLATE.md | AI_CONTEXT only mentions @ears, @bdd, @req - should include cumulative tags | MEDIUM |
| GAP-05 | STEST_MVP_SCHEMA.yaml | Uses `upstream` instead of `cumulative_tags`/`type_specific` structure | MEDIUM |
| GAP-06 | STEST_MVP_SCHEMA.yaml | Tag enum limited to @ears, @bdd, @req - missing cumulative tags | MEDIUM |

---

## Detailed Gap Analysis

### GAP-01: STEST-MVP-TEMPLATE.yaml Uses Wrong Traceability Structure

**Location**: Lines 119-137 (traceability section)

**Current**:

```yaml
traceability:
  upstream:
    - tag: "@ears"
      reference: "EARS.NN.25.01"
      description: "Behavioral requirement"
    - tag: "@bdd"
      reference: "BDD.NN.01.01"
      description: "Feature scenario"
    - tag: "@req"
      reference: "REQ.NN.10.01"
      description: "Functional requirement"
  downstream:
    - tag: "@tasks"
      reference: "TASKS-NN"
      description: "Implementation tasks"
    - tag: "@code"
      reference: "scripts/smoke_test.sh"
      description: "Test script"
```

**Required** (aligned with FTEST/PTEST/SECTEST pattern):

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
    - tag: "@ears"
      reference: "EARS.NN.25.01"
      description: "Behavioral requirement"
    - tag: "@bdd"
      reference: "BDD.NN.01.01"
      description: "Feature scenario"
    - tag: "@req"
      reference: "REQ.NN.10.01"
      description: "Functional requirement"
  downstream:
    - tag: "@tasks"
      reference: "TASKS-NN"
      description: "Implementation tasks"
    - tag: "@code"
      reference: "scripts/smoke_test.sh"
      description: "Test script"
```

**Fix**: Restructure traceability section to use cumulative_tags, type_specific, downstream subsections

---

### GAP-02: STEST-MVP-TEMPLATE.yaml Missing Cumulative Tags

**Location**: traceability.upstream section

**Issue**: Only @ears, @bdd, @req present, missing 6 cumulative tags

**Missing tags**: @brd, @prd, @adr, @sys, @spec, @ctr

**Fix**: Add all cumulative tags (included in GAP-01 fix)

---

### GAP-03: STEST-MVP-TEMPLATE.md Missing Cumulative Tags Section

**Location**: Section 6. Traceability (lines 314-331)

**Current**:

```markdown
### 6.1 Upstream References

| Tag | Reference | Description |
|-----|-----------|-------------|
| @ears | EARS.NN.25.01 | Behavioral requirement |
| @bdd | BDD.NN.01.01 | Feature scenario |
| @req | REQ.NN.10.01 | Functional requirement |
```

**Required**:

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

### 6.2 STEST-Specific Tags

| Tag | Reference | Description |
|-----|-----------|-------------|
| @ears | EARS.NN.25.01 | Behavioral requirement |
| @bdd | BDD.NN.01.01 | Feature scenario |
| @req | REQ.NN.10.01 | Functional requirement |

### 6.3 Downstream References

| Tag | Reference | Description |
|-----|-----------|-------------|
| @tasks | TASKS-NN | Implementation tasks |
| @code | `scripts/smoke_test.sh` | Test script |
| @pipeline | `.github/workflows/smoke.yml` | CI/CD integration |
```

**Fix**: Restructure traceability section in MD template

---

### GAP-04: STEST-MVP-TEMPLATE.md AI_CONTEXT Incomplete

**Location**: Lines 31-44 (AI_CONTEXT block)

**Current**:

```markdown
Constraints:
- Required traceability tags: @ears, @bdd, @req.
```

**Required**:

```markdown
Constraints:
- Required cumulative tags: @brd, @prd, @ears, @bdd, @adr, @sys, @req, @spec, @ctr (if exists).
- Required STEST-specific tags: @ears, @bdd, @req.
```

**Fix**: Update AI_CONTEXT to mention cumulative tags requirement

---

### GAP-05: STEST_MVP_SCHEMA.yaml Uses Wrong Traceability Structure

**Location**: Lines 233-252 (traceability property)

**Current**:

```yaml
traceability:
  type: object
  required:
    - upstream
  properties:
    upstream:
      type: array
      minItems: 3
      items:
        type: object
        required:
          - tag
          - reference
        properties:
          tag:
            type: string
            enum: ["@ears", "@bdd", "@req"]
          reference:
            type: string
```

**Required** (aligned with FTEST/PTEST/SECTEST schema):

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
      description: "STEST-specific traceability tags"
      items:
        type: object
        required:
          - tag
          - reference
        properties:
          tag:
            type: string
            enum: ["@ears", "@bdd", "@req"]
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
            enum: ["@tasks", "@code", "@pipeline"]
          reference:
            type: string
          description:
            type: string
```

**Fix**: Restructure schema traceability to use cumulative_tags, type_specific, downstream

---

### GAP-06: STEST_MVP_SCHEMA.yaml Tag Enum Limited

**Location**: Line 249 (tag enum)

**Current**:

```yaml
enum: ["@ears", "@bdd", "@req"]
```

**Issue**: Schema only validates 3 tags, missing all cumulative tags

**Fix**: Expand to include cumulative tags in cumulative_tags section (included in GAP-05 fix)

---

## Implementation Phase

### Phase 1: STEST YAML and Schema Fixes (GAP-01, GAP-02, GAP-05, GAP-06)

**Files to modify**:

1. `ucx_flow_v3/10_TSPEC/STEST/STEST-MVP-TEMPLATE.yaml` - Restructure traceability with cumulative tags
2. `ucx_flow_v3/10_TSPEC/STEST/STEST_MVP_SCHEMA.yaml` - Update traceability structure

**Steps**:

1. Read STEST-MVP-TEMPLATE.yaml
2. Replace traceability section with cumulative_tags, type_specific, downstream structure
3. Read STEST_MVP_SCHEMA.yaml
4. Update traceability property to use cumulative_tags, type_specific structure
5. Verify YAML syntax

### Phase 2: MD Template Fixes (GAP-03, GAP-04)

**Files to modify**:

1. `ucx_flow_v3/10_TSPEC/STEST/STEST-MVP-TEMPLATE.md` - Update traceability section and AI_CONTEXT

**Steps**:

1. Read STEST-MVP-TEMPLATE.md
2. Update AI_CONTEXT to include cumulative tags mention
3. Restructure Section 6 Traceability with cumulative tags, type-specific, downstream subsections
4. Verify markdown formatting

---

## Verification Commands

```bash
# Verify YAML template has cumulative tags
grep -c "@brd" ucx_flow_v3/10_TSPEC/STEST/STEST-MVP-TEMPLATE.yaml
# Expected: ≥1

# Verify schema has cumulative_tags structure
grep -n "cumulative_tags\|type_specific" ucx_flow_v3/10_TSPEC/STEST/STEST_MVP_SCHEMA.yaml
# Expected: Both sections present

# Verify YAML template structure
grep -n "cumulative_tags\|type_specific" ucx_flow_v3/10_TSPEC/STEST/STEST-MVP-TEMPLATE.yaml
# Expected: Both sections present

# Verify MD template has cumulative tags section
grep -c "Cumulative Tags" ucx_flow_v3/10_TSPEC/STEST/STEST-MVP-TEMPLATE.md
# Expected: ≥1

# Verify AI_CONTEXT mentions cumulative tags (case-insensitive)
grep -i "cumulative" ucx_flow_v3/10_TSPEC/STEST/STEST-MVP-TEMPLATE.md
# Expected: Results showing cumulative tags mention

# Verify schema no longer uses upstream as required
grep -n "required:" ucx_flow_v3/10_TSPEC/STEST/STEST_MVP_SCHEMA.yaml | grep -A2 "traceability"
# Expected: Should show cumulative_tags and type_specific, not upstream
```

---

## Risk Assessment

| Risk | Mitigation |
| ---- | ---------- |
| YAML schema changes break validation | Test with existing STEST documents first |
| Template changes cause autopilot issues | Verify doc-tspec-autopilot skill compatibility |
| Backward compatibility | Existing documents remain valid (additive changes) |
| MD/YAML template drift | Verify both templates have identical traceability structure |
| STEST-specific tags differ from other subtypes | Maintain @ears, @bdd, @req in type_specific section |

---

## Files Modified Summary

| File | Changes |
| ---- | ------- |
| `STEST-MVP-TEMPLATE.yaml` | Restructure traceability with cumulative_tags, type_specific, downstream |
| `STEST_MVP_SCHEMA.yaml` | Update traceability property with new structure |
| `STEST-MVP-TEMPLATE.md` | Add cumulative tags section, update AI_CONTEXT |

---

## Completion Criteria

- [x] STEST-MVP-TEMPLATE.yaml has cumulative_tags subsection in traceability
- [x] STEST-MVP-TEMPLATE.yaml has type_specific subsection in traceability
- [x] STEST_MVP_SCHEMA.yaml traceability uses cumulative_tags, type_specific structure
- [x] STEST_MVP_SCHEMA.yaml tag enums include cumulative tags
- [x] STEST-MVP-TEMPLATE.md Section 6 has Cumulative Tags subsection
- [x] STEST-MVP-TEMPLATE.md AI_CONTEXT mentions cumulative tags
- [x] All verification commands pass

---

## Consistency Check with Other Subtypes

| Element | FTEST | PTEST | SECTEST | STEST (After Fix) |
| ------- | ----- | ----- | ------- | ----------------- |
| cumulative_tags section | Yes (9 tags) | Yes (9 tags) | Yes (9 tags) | Yes (9 tags) |
| type_specific section | @sys, @threshold | @sys, @spec | @sec, @spec, @ctr | @ears, @bdd, @req |
| downstream section | @tasks, @code | @tasks, @code | @tasks, @code | @tasks, @code, @pipeline |
| Schema structure | cumulative_tags/type_specific | cumulative_tags/type_specific | cumulative_tags/type_specific | cumulative_tags/type_specific |
| MD cumulative section | 6.1 Cumulative Tags | 6.1 Cumulative Tags | 6.1 Cumulative Tags | 6.1 Cumulative Tags |

---

## Version History

| Version | Date | Changes | Author |
| ------- | ---- | ------- | ------ |
| 1.1 | 2026-02-26 | All 6 gaps fixed; Status COMPLETED | System |
| 1.0 | 2026-02-26 | Initial fix plan with 6 gaps | System |
