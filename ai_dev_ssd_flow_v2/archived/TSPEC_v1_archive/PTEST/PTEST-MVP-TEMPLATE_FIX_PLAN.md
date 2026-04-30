# PTEST-MVP-TEMPLATE Fix Plan

**Document**: PTEST-MVP-TEMPLATE_FIX_PLAN.md
**Created**: 2026-02-26
**Status**: COMPLETED
**Priority**: Medium
**Scope**: PTEST-only (aligned with FTEST fix patterns)

## Executive Summary

This fix plan addresses **6 identified gaps** in PTEST template and schema files. Primary issues include YAML template missing cumulative tags structure, MD template lacking cumulative tags section, and schema x-validation-rules referencing deprecated structure.

**Reference**: This plan follows the pattern established in `FTEST-MVP-TEMPLATE_FIX_PLAN.md`.

## Gap Summary Table

| Gap ID | File | Issue | Severity |
| ------ | ---- | ----- | -------- |
| GAP-01 | PTEST-MVP-TEMPLATE.yaml | Traceability uses `upstream` instead of `cumulative_tags`/`type_specific` structure | HIGH |
| GAP-02 | PTEST-MVP-TEMPLATE.yaml | Missing cumulative tags (@brd, @prd, @ears, @bdd, @adr, @req, @ctr) | HIGH |
| GAP-03 | PTEST-MVP-TEMPLATE.md | Traceability section missing cumulative tags section | MEDIUM |
| GAP-04 | PTEST-MVP-TEMPLATE.md | AI_CONTEXT only mentions @sys, @spec - should include cumulative tags | MEDIUM |
| GAP-05 | PTEST_MVP_SCHEMA.yaml | Uses `upstream` instead of `cumulative_tags`/`type_specific` structure | MEDIUM |
| GAP-06 | PTEST_MVP_SCHEMA.yaml | x-validation-rules reference "upstream" (lines 406-421) - needs update | MEDIUM |

---

## Detailed Gap Analysis

### GAP-01: PTEST-MVP-TEMPLATE.yaml Uses Wrong Traceability Structure

**Location**: Lines 147-161 (traceability section)

**Current**:

```yaml
traceability:
  upstream:
    - tag: "@sys"
      reference: "SYS.NN.01"
      description: "[Performance requirement title]"
    - tag: "@spec"
      reference: "SPEC-NN"
      description: "[Specification reference]"
  downstream:
    - tag: "@tasks"
      reference: "TASKS-NN"
      description: "Implementation tasks"
    - tag: "@code"
      reference: "tests/performance/test_[component].py"
      description: "Test implementation"
```

**Required** (aligned with FTEST pattern):

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
    - tag: "@sys"
      reference: "SYS.NN.01"
      description: "Performance requirement"
    - tag: "@spec"
      reference: "SPEC-NN"
      description: "Specification reference"
  downstream:
    - tag: "@tasks"
      reference: "TASKS-NN"
      description: "Implementation tasks"
    - tag: "@code"
      reference: "tests/performance/test_[component].py"
      description: "Test implementation"
```

**Fix**: Restructure traceability section to use cumulative_tags, type_specific, downstream subsections

---

### GAP-02: PTEST-MVP-TEMPLATE.yaml Missing Cumulative Tags

**Location**: traceability.upstream section

**Issue**: Only @sys and @spec present, missing 7 cumulative tags

**Missing tags**: @brd, @prd, @ears, @bdd, @adr, @req, @ctr

**Fix**: Add all cumulative tags (included in GAP-01 fix)

---

### GAP-03: PTEST-MVP-TEMPLATE.md Missing Cumulative Tags Section

**Location**: Section 6. Traceability (lines 288-303)

**Current**:

```markdown
### 6.1 Upstream References

| Tag | Reference | Description |
|-----|-----------|-------------|
| @sys | SYS.NN.01 | [Performance requirement title] |
| @sys | SYS.NN.02 | [Performance requirement title] |
| @spec | SPEC-NN | [Specification reference] |
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

### 6.2 PTEST-Specific Tags

| Tag | Reference | Description |
|-----|-----------|-------------|
| @sys | SYS.NN.01 | [Performance requirement title] |
| @spec | SPEC-NN | [Specification reference] |

### 6.3 Downstream References

| Tag | Reference | Description |
|-----|-----------|-------------|
| @tasks | TASKS-NN | Implementation tasks |
| @code | `tests/performance/test_[component].py` | Test implementation |
```

**Fix**: Restructure traceability section in MD template

---

### GAP-04: PTEST-MVP-TEMPLATE.md AI_CONTEXT Incomplete

**Location**: Lines 31-43 (AI_CONTEXT block)

**Current**:

```markdown
Constraints:
- Required traceability tags: @sys, @spec.
```

**Required**:

```markdown
Constraints:
- Required cumulative tags: @brd, @prd, @ears, @bdd, @adr, @sys, @req, @spec, @ctr (if exists)
- Required PTEST-specific tags: @sys, @spec.
```

**Fix**: Update AI_CONTEXT to mention cumulative tags requirement

---

### GAP-05: PTEST_MVP_SCHEMA.yaml Uses Wrong Traceability Structure

**Location**: Lines 368-403 (traceability property)

**Current**:

```yaml
traceability:
  type: object
  required:
    - upstream
  properties:
    upstream:
      type: array
      ...
```

**Required** (aligned with FTEST schema):

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
      description: "PTEST-specific traceability tags"
      items:
        type: object
        required:
          - tag
          - reference
        properties:
          tag:
            type: string
            enum: ["@sys", "@spec"]
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

**Fix**: Restructure schema traceability to use cumulative_tags, type_specific, downstream

---

### GAP-06: PTEST_MVP_SCHEMA.yaml x-validation-rules Reference "upstream"

**Location**: Lines 406-421 (x-validation-rules section)

**Current**:

```yaml
x-validation-rules:
  sys_tag_required:
    description: "At least one @sys tag must be present in upstream traceability"
    check: "upstream contains tag='@sys'"
  spec_tag_required:
    description: "At least one @spec tag must be present in upstream traceability"
    check: "upstream contains tag='@spec'"
```

**Required**:

```yaml
x-validation-rules:
  sys_tag_required:
    description: "At least one @sys tag must be present in type_specific traceability"
    check: "type_specific contains tag='@sys'"
  spec_tag_required:
    description: "At least one @spec tag must be present in type_specific traceability"
    check: "type_specific contains tag='@spec'"
```

**Fix**: Update x-validation-rules to reference `type_specific` instead of `upstream`

---

## Implementation Phase

### Phase 1: PTEST YAML and Schema Fixes (GAP-01, GAP-02, GAP-05, GAP-06)

**Files to modify**:

1. `ucx_flow_v3/10_TSPEC/PTEST/PTEST-MVP-TEMPLATE.yaml` - Restructure traceability with cumulative tags
2. `ucx_flow_v3/10_TSPEC/PTEST/PTEST_MVP_SCHEMA.yaml` - Update traceability structure and x-validation-rules

**Steps**:

1. Read PTEST-MVP-TEMPLATE.yaml
2. Replace traceability section with cumulative_tags, type_specific, downstream structure
3. Read PTEST_MVP_SCHEMA.yaml
4. Update traceability property to use cumulative_tags, type_specific structure
5. Update x-validation-rules to reference type_specific instead of upstream
6. Verify YAML syntax

### Phase 2: MD Template Fixes (GAP-03, GAP-04)

**Files to modify**:

1. `ucx_flow_v3/10_TSPEC/PTEST/PTEST-MVP-TEMPLATE.md` - Update traceability section and AI_CONTEXT

**Steps**:

1. Read PTEST-MVP-TEMPLATE.md
2. Update AI_CONTEXT to include cumulative tags mention
3. Restructure Section 6 Traceability with cumulative tags, type-specific, downstream subsections
4. Verify markdown formatting

---

## Verification Commands

```bash
# Verify YAML template has cumulative tags
grep -c "@brd" ucx_flow_v3/10_TSPEC/PTEST/PTEST-MVP-TEMPLATE.yaml
# Expected: ≥1

# Verify schema has cumulative_tags structure
grep -n "cumulative_tags\|type_specific" ucx_flow_v3/10_TSPEC/PTEST/PTEST_MVP_SCHEMA.yaml
# Expected: Both sections present

# Verify YAML template structure
grep -n "cumulative_tags\|type_specific" ucx_flow_v3/10_TSPEC/PTEST/PTEST-MVP-TEMPLATE.yaml
# Expected: Both sections present

# Verify MD template has cumulative tags section
grep -c "Cumulative Tags" ucx_flow_v3/10_TSPEC/PTEST/PTEST-MVP-TEMPLATE.md
# Expected: ≥1

# Verify AI_CONTEXT mentions cumulative tags (case-insensitive)
grep -i "cumulative" ucx_flow_v3/10_TSPEC/PTEST/PTEST-MVP-TEMPLATE.md
# Expected: Results showing cumulative tags mention

# Verify x-validation-rules updated (no "upstream" references)
grep -c "upstream" ucx_flow_v3/10_TSPEC/PTEST/PTEST_MVP_SCHEMA.yaml
# Expected: 0 (no upstream references remain)

# Verify x-validation-rules reference type_specific
grep "type_specific" ucx_flow_v3/10_TSPEC/PTEST/PTEST_MVP_SCHEMA.yaml
# Expected: Multiple results including x-validation-rules
```

---

## Risk Assessment

| Risk | Mitigation |
| ---- | ---------- |
| YAML schema changes break validation | Test with existing PTEST documents first |
| Template changes cause autopilot issues | Verify doc-tspec-autopilot skill compatibility |
| Backward compatibility | Existing documents remain valid (additive changes) |
| MD/YAML template drift | Verify both templates have identical traceability structure |

---

## Files Modified Summary

| File | Changes |
| ---- | ------- |
| `PTEST-MVP-TEMPLATE.yaml` | Restructure traceability with cumulative_tags, type_specific, downstream |
| `PTEST_MVP_SCHEMA.yaml` | Update traceability property and x-validation-rules |
| `PTEST-MVP-TEMPLATE.md` | Add cumulative tags section, update AI_CONTEXT |

---

## Completion Criteria

- [x] PTEST-MVP-TEMPLATE.yaml has cumulative_tags subsection in traceability
- [x] PTEST-MVP-TEMPLATE.yaml has type_specific subsection in traceability
- [x] PTEST_MVP_SCHEMA.yaml traceability uses cumulative_tags, type_specific structure
- [x] PTEST_MVP_SCHEMA.yaml x-validation-rules reference type_specific (not upstream)
- [x] PTEST-MVP-TEMPLATE.md Section 6 has Cumulative Tags subsection
- [x] PTEST-MVP-TEMPLATE.md AI_CONTEXT mentions cumulative tags
- [x] All verification commands pass

---

## Consistency Check with FTEST

| Element | FTEST | PTEST (After Fix) |
|---------|-------|-------------------|
| cumulative_tags section | Yes (9 tags) | Yes (9 tags) |
| type_specific section | Yes (@sys, @threshold) | Yes (@sys, @spec) |
| downstream section | Yes (@tasks, @code) | Yes (@tasks, @code) |
| Schema structure | cumulative_tags/type_specific | cumulative_tags/type_specific |
| MD cumulative section | 6.1 Cumulative Tags | 6.1 Cumulative Tags |

---

## Version History

| Version | Date | Changes | Author |
| ------- | ---- | ------- | ------ |
| 1.2 | 2026-02-26 | All 6 gaps fixed; Status COMPLETED | System |
| 1.1 | 2026-02-26 | Added GAP-06 (x-validation-rules); Fixed verification commands; Updated criteria | System |
| 1.0 | 2026-02-26 | Initial fix plan with 5 gaps | System |
