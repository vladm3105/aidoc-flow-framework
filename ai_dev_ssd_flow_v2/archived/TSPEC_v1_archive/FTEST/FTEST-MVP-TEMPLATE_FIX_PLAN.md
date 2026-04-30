# FTEST-MVP-TEMPLATE Fix Plan

**Document**: FTEST-MVP-TEMPLATE_FIX_PLAN.md
**Created**: 2026-02-26
**Status**: COMPLETED
**Priority**: Medium
**Scope**: FTEST-only (cross-subtype alignment deferred to separate plan)

## Executive Summary

This fix plan addresses **3 identified gaps** in FTEST YAML template and schema files. Primary issues include YAML template missing cumulative tags in traceability section and schema not validating cumulative tags.

**Note**: Cross-subtype template alignment (UTEST, ITEST, STEST, PTEST, SECTEST) is deferred to a separate fix plan: `TSPEC-SUBTYPE-TEMPLATES_FIX_PLAN.md`.

## Gap Summary Table

| Gap ID | File | Issue | Severity |
| ------ | ---- | ----- | -------- |
| GAP-01 | FTEST-MVP-TEMPLATE.yaml | Traceability section missing cumulative tags (@brd, @prd, @ears, @bdd, @adr, @req) | HIGH |
| GAP-02 | FTEST_MVP_SCHEMA.yaml | Tag enum only validates @sys, @threshold, @spec - doesn't include cumulative tags | MEDIUM |
| GAP-03 | FTEST-MVP-TEMPLATE.yaml | Missing @ctr tag in traceability (optional but should be documented) | LOW |

---

## Detailed Gap Analysis

### GAP-01: FTEST-MVP-TEMPLATE.yaml Missing Cumulative Tags

**Location**: Lines 127-144 (traceability.upstream section)

**Current**:

```yaml
traceability:
  upstream:
    - tag: "@sys"
      reference: "SYS.NN.01.01"
      description: "System requirement"
    - tag: "@threshold"
      reference: "TH-PERF-001"
      description: "Performance threshold"
    - tag: "@spec"
      reference: "SPEC-NN"
      description: "Technical specification"
```

**Required** (8-9 cumulative tags for Layer 10):

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
      reference: "SYS.NN.01.01"
      description: "System quality attribute"
    - tag: "@threshold"
      reference: "TH-PERF-001"
      description: "Performance threshold"
  downstream:
    - tag: "@tasks"
      reference: "TASKS-NN"
      description: "Implementation tasks"
    - tag: "@code"
      reference: "tests/functional/test_[scope].py"
      description: "Test implementation"
```

**Fix**: Restructure traceability section to include cumulative_tags, type_specific, and downstream subsections

---

### GAP-02: FTEST_MVP_SCHEMA.yaml Tag Enum Limited

**Location**: Line 213

**Current**:

```yaml
tag:
  type: string
  enum: ["@sys", "@threshold", "@spec"]
```

**Required**:

```yaml
tag:
  type: string
  enum: ["@brd", "@prd", "@ears", "@bdd", "@adr", "@sys", "@req", "@spec", "@ctr", "@threshold"]
```

**Fix**: Expand enum to include all valid cumulative and type-specific tags

---

### GAP-03: FTEST-MVP-TEMPLATE.yaml Missing @ctr Tag

**Location**: traceability.upstream section

**Issue**: @ctr (Data Contract) tag not documented as optional tag

**Fix**: Add @ctr to cumulative_tags with "if exists" notation (included in GAP-01 fix)

---

## Implementation Phase

### Phase 1: FTEST YAML and Schema Fixes (GAP-01, GAP-02, GAP-03)

**Files to modify**:

1. `ucx_flow_v3/10_TSPEC/FTEST/FTEST-MVP-TEMPLATE.yaml` - Restructure traceability with cumulative tags
2. `ucx_flow_v3/10_TSPEC/FTEST/FTEST_MVP_SCHEMA.yaml` - Expand tag enum

**Steps**:

1. Read FTEST-MVP-TEMPLATE.yaml
2. Restructure traceability section with cumulative_tags, type_specific, downstream
3. Read FTEST_MVP_SCHEMA.yaml
4. Expand tag enum to include all cumulative and type-specific tags
5. Verify changes

---

## Verification Commands

```bash
# Verify YAML template has cumulative tags
grep -c "@brd" ucx_flow_v3/10_TSPEC/FTEST/FTEST-MVP-TEMPLATE.yaml
# Expected: ≥1

# Verify schema validates cumulative tags
grep "@brd" ucx_flow_v3/10_TSPEC/FTEST/FTEST_MVP_SCHEMA.yaml
# Expected: Results showing @brd in enum

# Verify traceability structure
grep -n "cumulative_tags\|type_specific" ucx_flow_v3/10_TSPEC/FTEST/FTEST-MVP-TEMPLATE.yaml
# Expected: Both sections present
```

---

## Risk Assessment

| Risk | Mitigation |
| ---- | ---------- |
| YAML schema changes break validation | Test with existing FTEST documents first |
| Template changes cause autopilot issues | Verify doc-tspec-autopilot skill compatibility |
| Backward compatibility | Existing documents remain valid (additive changes) |

---

## Files Modified Summary

| File | Changes |
| ---- | ------- |
| `FTEST-MVP-TEMPLATE.yaml` | Restructure traceability with cumulative_tags, type_specific, downstream |
| `FTEST_MVP_SCHEMA.yaml` | Expand tag enum to include all valid tags |

---

## Completion Criteria

- [x] FTEST-MVP-TEMPLATE.yaml has cumulative_tags subsection in traceability
- [x] FTEST-MVP-TEMPLATE.yaml has type_specific subsection in traceability
- [x] FTEST_MVP_SCHEMA.yaml tag enum includes all cumulative tags (@brd through @ctr)
- [x] All verification commands pass

---

## Related Work

**Deferred to separate fix plan**: Cross-subtype template alignment

The following issues were identified but are out of scope for this FTEST-focused plan:

| Issue | Files Affected | Deferred To |
| ----- | -------------- | ----------- |
| MD templates missing cumulative tags section | UTEST, ITEST, STEST, PTEST, SECTEST | TSPEC-SUBTYPE-TEMPLATES_FIX_PLAN.md |
| AI_CONTEXT missing cumulative tags mention | UTEST, ITEST, STEST, PTEST, SECTEST | TSPEC-SUBTYPE-TEMPLATES_FIX_PLAN.md |
| YAML templates missing cumulative tags | UTEST, ITEST, STEST, PTEST, SECTEST | TSPEC-SUBTYPE-TEMPLATES_FIX_PLAN.md |
| Schema tag enums limited | UTEST, ITEST, STEST, PTEST, SECTEST | TSPEC-SUBTYPE-TEMPLATES_FIX_PLAN.md |

---

## Version History

| Version | Date | Changes | Author |
| ------- | ---- | ------- | ------ |
| 1.3 | 2026-02-26 | Implemented all fixes: GAP-01, GAP-02, GAP-03 completed; Status changed to COMPLETED | System |
| 1.2 | 2026-02-26 | Refocused to FTEST-only scope (Option A); Removed cross-subtype gaps; Deferred to separate plan | System |
| 1.1 | 2026-02-26 | Added Fix Plan Self-Review section identifying scope issues | System |
| 1.0 | 2026-02-26 | Initial fix plan with 8 gaps across 2 phases | System |
