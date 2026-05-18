# SECTEST-MVP-TEMPLATE Fix Plan

**Document**: SECTEST-MVP-TEMPLATE_FIX_PLAN.md
**Created**: 2026-02-26
**Status**: COMPLETED
**Priority**: Medium
**Scope**: SECTEST-only (aligned with FTEST/PTEST fix patterns)

## Executive Summary

This fix plan addresses **6 identified gaps** in SECTEST template and schema files. Primary issues include YAML template using `upstream` instead of `cumulative_tags`/`type_specific` structure, MD template lacking cumulative tags section, and schema x-validation-rules referencing deprecated structure.

**Reference**: This plan follows the pattern established in `FTEST-MVP-TEMPLATE_FIX_PLAN.md` and `PTEST-MVP-TEMPLATE_FIX_PLAN.md`.

## Gap Summary Table

| Gap ID | File | Issue | Severity |
| ------ | ---- | ----- | -------- |
| GAP-01 | SECTEST-MVP-TEMPLATE.yaml | Traceability uses `upstream` instead of `cumulative_tags`/`type_specific` structure | HIGH |
| GAP-02 | SECTEST-MVP-TEMPLATE.yaml | Missing cumulative tags (@brd, @prd, @ears, @bdd, @adr, @sys, @req) | HIGH |
| GAP-03 | SECTEST-MVP-TEMPLATE.md | Traceability section missing cumulative tags section | MEDIUM |
| GAP-04 | SECTEST-MVP-TEMPLATE.md | AI_CONTEXT only mentions @sec, @spec - should include cumulative tags | MEDIUM |
| GAP-05 | SECTEST_MVP_SCHEMA.yaml | Uses `upstream` instead of `cumulative_tags`/`type_specific` structure | MEDIUM |
| GAP-06 | SECTEST_MVP_SCHEMA.yaml | x-validation-rules reference "upstream" (lines 396-401) - needs update | MEDIUM |

---

## Detailed Gap Analysis

### GAP-01: SECTEST-MVP-TEMPLATE.yaml Uses Wrong Traceability Structure

**Location**: Lines 140-155 (traceability section)

**Current**:

```yaml
traceability:
  upstream:
    - tag: "@sec"
      reference: "SEC.NN.01"
      description: "[Security requirement title]"
    - tag: "@spec"
      reference: "SPEC-NN"
      description: "[Specification reference]"
  downstream:
    - tag: "@tasks"
      reference: "TASKS-NN"
      description: "Implementation tasks"
    - tag: "@code"
      reference: "tests/security/test_[component].py"
      description: "Test implementation"
```

**Required** (aligned with FTEST/PTEST pattern):

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
    - tag: "@sec"
      reference: "SEC.NN.01"
      description: "Security requirement"
    - tag: "@spec"
      reference: "SPEC-NN"
      description: "Specification reference"
  downstream:
    - tag: "@tasks"
      reference: "TASKS-NN"
      description: "Implementation tasks"
    - tag: "@code"
      reference: "tests/security/test_[component].py"
      description: "Test implementation"
```

**Fix**: Restructure traceability section to use cumulative_tags, type_specific, downstream subsections

---

### GAP-02: SECTEST-MVP-TEMPLATE.yaml Missing Cumulative Tags

**Location**: traceability.upstream section

**Issue**: Only @sec and @spec present, missing 7 cumulative tags

**Missing tags**: @brd, @prd, @ears, @bdd, @adr, @sys, @req, @ctr

**Fix**: Add all cumulative tags (included in GAP-01 fix)

---

### GAP-03: SECTEST-MVP-TEMPLATE.md Missing Cumulative Tags Section

**Location**: Section 6. Traceability (lines 293-310)

**Current**:

```markdown
### 6.1 Upstream References

| Tag | Reference | Description |
|-----|-----------|-------------|
| @sec | SEC.NN.01 | [Security requirement title] |
| @sec | SEC.NN.02 | [Security requirement title] |
| @spec | SPEC-NN | [Specification reference] |
| @ctr | CTR-NN | [Contract reference] |
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

### 6.2 SECTEST-Specific Tags

| Tag | Reference | Description |
|-----|-----------|-------------|
| @sec | SEC.NN.01 | [Security requirement title] |
| @sec | SEC.NN.02 | [Security requirement title] |
| @spec | SPEC-NN | [Specification reference] |
| @ctr | CTR-NN | [Contract reference] |

### 6.3 Downstream References

| Tag | Reference | Description |
|-----|-----------|-------------|
| @tasks | TASKS-NN | Implementation tasks |
| @code | `tests/security/test_[component].py` | Test implementation |
```

**Fix**: Restructure traceability section in MD template

---

### GAP-04: SECTEST-MVP-TEMPLATE.md AI_CONTEXT Incomplete

**Location**: Lines 31-44 (AI_CONTEXT block)

**Current**:

```markdown
Constraints:
- Required traceability tags: @sec, @spec.
```

**Required**:

```markdown
Constraints:
- Required cumulative tags: @brd, @prd, @ears, @bdd, @adr, @sys, @req, @spec, @ctr (if exists)
- Required SECTEST-specific tags: @sec, @spec.
```

**Fix**: Update AI_CONTEXT to mention cumulative tags requirement

---

### GAP-05: SECTEST_MVP_SCHEMA.yaml Uses Wrong Traceability Structure

**Location**: Lines 357-392 (traceability property)

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

**Required** (aligned with FTEST/PTEST schema):

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
      description: "SECTEST-specific traceability tags"
      items:
        type: object
        required:
          - tag
          - reference
        properties:
          tag:
            type: string
            enum: ["@sec", "@spec", "@ctr"]
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

### GAP-06: SECTEST_MVP_SCHEMA.yaml x-validation-rules Reference "upstream"

**Location**: Lines 394-414 (x-validation-rules section)

**Current**:

```yaml
x-validation-rules:
  sec_tag_required:
    description: "At least one @sec tag must be present in upstream traceability"
    check: "upstream contains tag='@sec'"
  spec_tag_required:
    description: "At least one @spec tag must be present in upstream traceability"
    check: "upstream contains tag='@spec'"
```

**Required**:

```yaml
x-validation-rules:
  sec_tag_required:
    description: "At least one @sec tag must be present in type_specific traceability"
    check: "type_specific contains tag='@sec'"
  spec_tag_required:
    description: "At least one @spec tag must be present in type_specific traceability"
    check: "type_specific contains tag='@spec'"
```

**Fix**: Update x-validation-rules to reference `type_specific` instead of `upstream`

---

## Implementation Phase

### Phase 1: SECTEST YAML and Schema Fixes (GAP-01, GAP-02, GAP-05, GAP-06)

**Files to modify**:

1. `ucx_flow_v3/10_TSPEC/SECTEST/SECTEST-MVP-TEMPLATE.yaml` - Restructure traceability with cumulative tags
2. `ucx_flow_v3/10_TSPEC/SECTEST/SECTEST_MVP_SCHEMA.yaml` - Update traceability structure and x-validation-rules

**Steps**:

1. Read SECTEST-MVP-TEMPLATE.yaml
2. Replace traceability section with cumulative_tags, type_specific, downstream structure
3. Read SECTEST_MVP_SCHEMA.yaml
4. Update traceability property to use cumulative_tags, type_specific structure
5. Update x-validation-rules to reference type_specific instead of upstream
6. Verify YAML syntax

### Phase 2: MD Template Fixes (GAP-03, GAP-04)

**Files to modify**:

1. `ucx_flow_v3/10_TSPEC/SECTEST/SECTEST-MVP-TEMPLATE.md` - Update traceability section and AI_CONTEXT

**Steps**:

1. Read SECTEST-MVP-TEMPLATE.md
2. Update AI_CONTEXT to include cumulative tags mention
3. Restructure Section 6 Traceability with cumulative tags, type-specific, downstream subsections
4. Verify markdown formatting

---

## Verification Commands

```bash
# Verify YAML template has cumulative tags
grep -c "@brd" ucx_flow_v3/10_TSPEC/SECTEST/SECTEST-MVP-TEMPLATE.yaml
# Expected: ≥1

# Verify schema has cumulative_tags structure
grep -n "cumulative_tags\|type_specific" ucx_flow_v3/10_TSPEC/SECTEST/SECTEST_MVP_SCHEMA.yaml
# Expected: Both sections present

# Verify YAML template structure
grep -n "cumulative_tags\|type_specific" ucx_flow_v3/10_TSPEC/SECTEST/SECTEST-MVP-TEMPLATE.yaml
# Expected: Both sections present

# Verify MD template has cumulative tags section
grep -c "Cumulative Tags" ucx_flow_v3/10_TSPEC/SECTEST/SECTEST-MVP-TEMPLATE.md
# Expected: ≥1

# Verify AI_CONTEXT mentions cumulative tags (case-insensitive)
grep -i "cumulative" ucx_flow_v3/10_TSPEC/SECTEST/SECTEST-MVP-TEMPLATE.md
# Expected: Results showing cumulative tags mention

# Verify x-validation-rules updated (no "upstream" references in rules)
grep "upstream" ucx_flow_v3/10_TSPEC/SECTEST/SECTEST_MVP_SCHEMA.yaml
# Expected: 0 or only in description text (not in required/check fields)

# Verify x-validation-rules reference type_specific
grep "type_specific" ucx_flow_v3/10_TSPEC/SECTEST/SECTEST_MVP_SCHEMA.yaml
# Expected: Multiple results including x-validation-rules
```

---

## Risk Assessment

| Risk | Mitigation |
| ---- | ---------- |
| YAML schema changes break validation | Test with existing SECTEST documents first |
| Template changes cause autopilot issues | Verify doc-tspec-autopilot skill compatibility |
| Backward compatibility | Existing documents remain valid (additive changes) |
| MD/YAML template drift | Verify both templates have identical traceability structure |

---

## Files Modified Summary

| File | Changes |
| ---- | ------- |
| `SECTEST-MVP-TEMPLATE.yaml` | Restructure traceability with cumulative_tags, type_specific, downstream |
| `SECTEST_MVP_SCHEMA.yaml` | Update traceability property and x-validation-rules |
| `SECTEST-MVP-TEMPLATE.md` | Add cumulative tags section, update AI_CONTEXT |

---

## Completion Criteria

- [x] SECTEST-MVP-TEMPLATE.yaml has cumulative_tags subsection in traceability
- [x] SECTEST-MVP-TEMPLATE.yaml has type_specific subsection in traceability
- [x] SECTEST_MVP_SCHEMA.yaml traceability uses cumulative_tags, type_specific structure
- [x] SECTEST_MVP_SCHEMA.yaml x-validation-rules reference type_specific (not upstream)
- [x] SECTEST-MVP-TEMPLATE.md Section 6 has Cumulative Tags subsection
- [x] SECTEST-MVP-TEMPLATE.md AI_CONTEXT mentions cumulative tags
- [x] All verification commands pass

---

## Consistency Check with FTEST/PTEST

| Element | FTEST | PTEST | SECTEST (After Fix) |
| ------- | ----- | ----- | ------------------- |
| cumulative_tags section | Yes (9 tags) | Yes (9 tags) | Yes (9 tags) |
| type_specific section | Yes (@sys, @threshold) | Yes (@sys, @spec) | Yes (@sec, @spec, @ctr) |
| downstream section | Yes (@tasks, @code) | Yes (@tasks, @code) | Yes (@tasks, @code) |
| Schema structure | cumulative_tags/type_specific | cumulative_tags/type_specific | cumulative_tags/type_specific |
| MD cumulative section | 6.1 Cumulative Tags | 6.1 Cumulative Tags | 6.1 Cumulative Tags |

---

## Version History

| Version | Date | Changes | Author |
| ------- | ---- | ------- | ------ |
| 1.1 | 2026-02-26 | All 6 gaps fixed; Status COMPLETED | System |
| 1.0 | 2026-02-26 | Initial fix plan with 6 gaps | System |
