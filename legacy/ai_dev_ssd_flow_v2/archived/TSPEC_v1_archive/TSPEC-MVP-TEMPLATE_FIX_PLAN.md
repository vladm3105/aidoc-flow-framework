# TSPEC-MVP-TEMPLATE Fix Plan

**Document**: TSPEC-MVP-TEMPLATE_FIX_PLAN.md
**Created**: 2026-02-26
**Status**: PENDING
**Priority**: High

## Executive Summary

This fix plan addresses **36 identified gaps** across TSPEC template files, skill documentation, reviewer/fixer skills, and validator rules. Issues include incorrect path references (`ucx_flow_v3` vs `ucx_flow_v3`), missing test type codes (44-45 for PTEST/SECTEST) across multiple skills, inconsistent cumulative tag formats, section count mismatches between templates (6 sections) and validator (7 sections), missing quick reference file, and **traceability structure modernization** (UTEST, ITEST, STEST templates/schemas still use deprecated `upstream` structure instead of `cumulative_tags`/`type_specific`).

## Gap Summary Table

| Gap ID | File | Issue | Severity | Phase |
| ------ | ---- | ----- | -------- | ----- |
| GAP-01 | TSPEC-MVP-TEMPLATE.md | Template paths use `ucx_flow_v3/` instead of `ucx_flow_v3/` | HIGH | 1 |
| GAP-02 | doc-tspec/SKILL.md | All template paths use `ucx_flow_v3/` (14+ occurrences) | HIGH | 1 |
| GAP-03 | doc-tspec-validator/SKILL.md | All template paths use `ucx_flow_v3/` (12+ occurrences) | HIGH | 1 |
| GAP-04 | doc-tspec-autopilot/SKILL.md | Template path at line 759 uses `ucx_flow_v3/` | HIGH | 1 |
| GAP-05 | doc-tspec/SKILL.md | Missing PTEST (code 44) and SECTEST (code 45) support | MEDIUM | 2 |
| GAP-06 | doc-tspec-validator/SKILL.md | Missing PTEST (code 44) and SECTEST (code 45) validation | MEDIUM | 2 |
| GAP-07 | doc-tspec-autopilot/SKILL.md | Missing PTEST (code 44) and SECTEST (code 45) in workflow | MEDIUM | 2 |
| GAP-08 | doc-tspec-autopilot/SKILL.md | @spec tag uses dot notation `SPEC.NN.TT.SS` instead of dash `SPEC-NN` | MEDIUM | 3 |
| GAP-09 | TSPEC-MVP-TEMPLATE.md | AI_CONTEXT says "5 required sections" but template has 5 main + appendix | LOW | 3 |
| GAP-10 | doc-tspec-validator/SKILL.md | Validates 7 sections but aggregator template has 5 sections | MEDIUM | 3 |
| GAP-11 | TSPEC-MVP-TEMPLATE.md | Appendix shows flat structure instead of nested folder structure | MEDIUM | 4 |
| GAP-12 | README.md | Scripts directory shows `scripts/` but actual path is `ucx_flow_v3/10_TSPEC/scripts/` | LOW | 4 |
| GAP-13 | N/A | Missing `.claude/skills/doc-tspec_quickref.md` file | MEDIUM | 5 |
| GAP-14 | doc-tspec/SKILL.md | Version 1.0 needs update after fixes | LOW | 8 |
| GAP-15 | doc-tspec-validator/SKILL.md | Version 1.1 needs update after fixes | LOW | 8 |
| GAP-16 | doc-tspec-autopilot/SKILL.md | Version 2.4 needs update after fixes | LOW | 8 |
| GAP-17 | doc-tspec-validator/SKILL.md | Section 6 Naming Compliance shows non-nested directory structure | MEDIUM | 4 |
| GAP-18 | TSPEC-MVP-TEMPLATE.yaml | Missing PTEST and SECTEST in test_documents section | MEDIUM | 2 |
| GAP-19 | doc-tspec-reviewer/SKILL.md | Line 27 says "4 types" but should be "6 types" (missing PTEST/SECTEST) | MEDIUM | 2 |
| GAP-20 | doc-tspec-reviewer/SKILL.md | Lines 119-124 nested folder table missing PTEST/SECTEST directories | MEDIUM | 2 |
| GAP-21 | doc-tspec-reviewer/SKILL.md | Line 287 element type codes "40, 41, 42, 43" missing 44, 45 | MEDIUM | 2 |
| GAP-22 | doc-tspec-fixer/SKILL.md | Lines 115-120 nested folder table missing PTEST/SECTEST directories | MEDIUM | 2 |
| GAP-23 | doc-tspec-fixer/SKILL.md | Lines 369-381 Type Code Mapping table missing 44 (PTEST) and 45 (SECTEST) | MEDIUM | 2 |
| GAP-24 | doc-tspec-validator/SKILL.md | Section 0 nested folder table missing PTEST/SECTEST directories | MEDIUM | 2 |
| GAP-25 | Subtype templates | Templates say "6 sections" but validator says "7 sections" - mismatch | MEDIUM | 7 |
| GAP-26 | doc-tspec-reviewer/SKILL.md | Version 1.4 needs update after fixes | LOW | 8 |
| GAP-27 | doc-tspec-fixer/SKILL.md | Version 2.1 needs update after fixes | LOW | 8 |
| GAP-28 | UTEST-MVP-TEMPLATE.yaml | Uses `upstream` instead of `cumulative_tags`/`type_specific` structure | HIGH | 9 |
| GAP-29 | UTEST_MVP_SCHEMA.yaml | Uses `upstream` structure; x-validation-rules reference `upstream` | HIGH | 9 |
| GAP-30 | UTEST-MVP-TEMPLATE.md | Section 6.1 "Upstream References" not "Cumulative Tags"; AI_CONTEXT missing cumulative tags | MEDIUM | 9 |
| GAP-31 | ITEST-MVP-TEMPLATE.yaml | Uses `upstream` instead of `cumulative_tags`/`type_specific` structure | HIGH | 9 |
| GAP-32 | ITEST_MVP_SCHEMA.yaml | Uses `upstream` structure; x-validation-rules reference `upstream` | HIGH | 9 |
| GAP-33 | ITEST-MVP-TEMPLATE.md | Section 6.1 "Upstream References" not "Cumulative Tags"; AI_CONTEXT missing cumulative tags | MEDIUM | 9 |
| GAP-34 | STEST-MVP-TEMPLATE.yaml | Uses `upstream` instead of `cumulative_tags`/`type_specific` structure | HIGH | 9 |
| GAP-35 | STEST_MVP_SCHEMA.yaml | Uses `upstream` structure; x-validation-rules reference `upstream` | HIGH | 9 |
| GAP-36 | STEST-MVP-TEMPLATE.md | Section 6.1 "Upstream References" not "Cumulative Tags"; AI_CONTEXT missing cumulative tags | MEDIUM | 9 |

## Detailed Gap Analysis

### GAP-01: TSPEC-MVP-TEMPLATE.md Template Paths

**Location**: Lines 25-31

**Current**:

```markdown
> - **Subtype Templates**: Use subtype-specific templates for individual test documents:
>   - `UTEST/UTEST-MVP-TEMPLATE.md` - Unit tests
>   - `ITEST/ITEST-MVP-TEMPLATE.md` - Integration tests
>   - `STEST/STEST-MVP-TEMPLATE.md` - System tests
>   - `FTEST/FTEST-MVP-TEMPLATE.md` - Functional tests
>   - `PTEST/PTEST-MVP-TEMPLATE.md` - Performance tests
>   - `SECTEST/SECTEST-MVP-TEMPLATE.md` - Security tests
```

**Issue**: Template paths are relative but should reference `ucx_flow_v3/10_TSPEC/` prefix for consistency with other skills.

**Fix**: Paths are correct as relative references within same directory. No change needed for GAP-01.

---

### GAP-02: doc-tspec/SKILL.md Template Paths

**Location**: Lines 56-60, 432-439, 461-464, 581-588

**Current**:

```markdown
- UTEST: `ucx_flow_v3/10_TSPEC/UTEST/UTEST-MVP-TEMPLATE.md`
- ITEST: `ucx_flow_v3/10_TSPEC/ITEST/ITEST-MVP-TEMPLATE.md`
```

**Required**:

```markdown
- UTEST: `ucx_flow_v3/10_TSPEC/UTEST/UTEST-MVP-TEMPLATE.md`
- ITEST: `ucx_flow_v3/10_TSPEC/ITEST/ITEST-MVP-TEMPLATE.md`
```

**Fix**: Replace all `ucx_flow_v3/10_TSPEC/` with `ucx_flow_v3/10_TSPEC/`

---

### GAP-03: doc-tspec-validator/SKILL.md Template Paths

**Location**: Lines 52-58, 403-416, 529-545

**Current**:

```markdown
| TSPEC Index | `ucx_flow_v3/10_TSPEC/TSPEC-00_index.md` |
| UTEST Template | `ucx_flow_v3/10_TSPEC/UTEST/UTEST-MVP-TEMPLATE.md` |
```

**Required**:

```markdown
| TSPEC Index | `ucx_flow_v3/10_TSPEC/TSPEC-00_index.md` |
| UTEST Template | `ucx_flow_v3/10_TSPEC/UTEST/UTEST-MVP-TEMPLATE.md` |
```

**Fix**: Replace all `ucx_flow_v3/10_TSPEC/` with `ucx_flow_v3/10_TSPEC/`

---

### GAP-04: doc-tspec-autopilot/SKILL.md Template Path

**Location**: Line 759

**Current**:

```markdown
- **TSPEC Template**: `ucx_flow_v3/10_TSPEC/TSPEC-TEMPLATE.md`
```

**Required**:

```markdown
- **TSPEC Template**: `ucx_flow_v3/10_TSPEC/TSPEC-MVP-TEMPLATE.md`
```

**Fix**: Update path and filename to MVP template

---

### GAP-05: doc-tspec/SKILL.md Missing PTEST/SECTEST

**Location**: Lines 90-102, 106-114, 199-250

**Current**: Only defines codes 40-43 (UTEST, ITEST, STEST, FTEST)

**Required**: Add codes 44-45 (PTEST, SECTEST) to all element type tables and type-specific requirements

**Fix**: Add PTEST (code 44) and SECTEST (code 45) sections

---

### GAP-06: doc-tspec-validator/SKILL.md Missing PTEST/SECTEST Validation

**Location**: Lines 180-188, 320-361

**Current**: Only validates codes 40-43

**Required**: Add validation for codes 44-45

**Fix**: Add PTEST and SECTEST validation rules and type-specific requirements

---

### GAP-07: doc-tspec-autopilot/SKILL.md Missing PTEST/SECTEST

**Location**: Lines 181-189, 214-228

**Current**: Test Types table only shows 4 types (UTEST, ITEST, STEST, FTEST)

**Required**: Add PTEST (code 44) and SECTEST (code 45) to workflow

**Fix**: Add PTEST and SECTEST to test type tables and coverage matrix

---

### GAP-08: doc-tspec-autopilot/SKILL.md @spec Tag Format

**Location**: Line 371

**Current**:

```markdown
@spec: SPEC.NN.TT.SS
```

**Required**:

```markdown
@spec: SPEC-NN
```

**Rationale**: SPEC uses dash notation (TYPE-NN) per SDD framework tag format convention

**Fix**: Change `SPEC.NN.TT.SS` to `SPEC-NN`

---

### GAP-09: TSPEC-MVP-TEMPLATE.md AI_CONTEXT Section Count

**Location**: Line 45

**Current**:

```markdown
- 5 required sections.
```

**Required**:

```markdown
- 5 required sections (Sections 1-5) plus appendix.
```

**Fix**: Clarify section count includes appendix reference

---

### GAP-10: doc-tspec-validator/SKILL.md Section Count Mismatch

**Location**: Lines 152-163

**Current**: Lists 7 required sections for all TSPEC types

**Issue**: The TSPEC-MVP-TEMPLATE.md (aggregator) has 5 sections, individual test type templates may have 7 sections

**Fix**: Clarify that 7-section requirement applies to individual test type documents (UTEST, ITEST, STEST, FTEST, PTEST, SECTEST), while aggregator uses 5 sections

---

### GAP-11: TSPEC-MVP-TEMPLATE.md Appendix Directory Structure

**Location**: Lines 232-247

**Current**:

```markdown
10_TSPEC/
 TSPEC-NN_{component}_overview.md  (this document)
 UTEST/
    UTEST-NN_{component}_unit_tests.md
```

**Required** (nested folder structure):

```markdown
10_TSPEC/
 TSPEC-NN_{component}/
    TSPEC-NN_{component}.md  (this document)
 UTEST/
    UTEST-NN_{component}/
       UTEST-NN_{component}.md
```

**Fix**: Update appendix to show nested folder structure (mandatory per doc-tspec-validator Section 0)

---

### GAP-12: README.md Scripts Path Reference

**Location**: Lines 96-107

**Current**: Shows `scripts/` relative path

**Issue**: Actual path is `ucx_flow_v3/10_TSPEC/scripts/`

**Fix**: Clarify relative path is from within `10_TSPEC/` directory (no change needed, relative paths are correct)

---

### GAP-13: Missing doc-tspec_quickref.md

**Location**: N/A (file does not exist)

**Issue**: Other artifacts have quick reference files (e.g., `doc-spec_quickref.md`) but TSPEC does not

**Fix**: Create `.claude/skills/doc-tspec_quickref.md` with essential TSPEC reference information

---

### GAP-14: doc-tspec/SKILL.md Version Update

**Location**: Line 17, version history section

**Current**: Version 1.0, last_updated 2026-02-10

**Fix**: Update to version 1.1 after applying fixes

---

### GAP-15: doc-tspec-validator/SKILL.md Version Update

**Location**: Line 18, version history section

**Current**: Version 1.1, last_updated 2026-02-11

**Fix**: Update to version 1.2 after applying fixes

---

### GAP-16: doc-tspec-autopilot/SKILL.md Version Update

**Location**: Line 18, version history section

**Current**: Version 2.4, last_updated 2026-02-10

**Fix**: Update to version 2.5 after applying fixes

---

### GAP-17: doc-tspec-validator/SKILL.md Directory Structure in Naming Compliance

**Location**: Lines 226-239

**Current**:

```markdown
docs/10_TSPEC/
  UTEST/
    UTEST-01_{slug}.md
```

**Required** (shows nested folder but then shows flat):

```markdown
docs/10_TSPEC/
  UTEST/
    UTEST-01_{slug}/
      UTEST-01_{slug}.md
```

**Fix**: Update Section 6 to show nested folder structure consistent with Section 0

---

### GAP-18: TSPEC-MVP-TEMPLATE.yaml Missing PTEST/SECTEST

**Location**: Lines 65-100 (traceability.test_documents section)

**Current**: Only includes unit_tests, integration_tests, system_tests, functional_tests, performance_tests, security_tests

**Issue**: Already includes all 6 types but needs verification of PTEST/SECTEST link paths

**Fix**: Verify PTEST and SECTEST links use correct paths (./PTEST/ and ./SECTEST/)

---

### GAP-19: doc-tspec-reviewer/SKILL.md Test Type Count

**Location**: Line 27

**Current**:

```markdown
checking test coverage across all 4 types (UTEST, ITEST, STEST, FTEST)
```

**Required**:

```markdown
checking test coverage across all 6 types (UTEST, ITEST, STEST, FTEST, PTEST, SECTEST)
```

**Fix**: Update to include all 6 test types

---

### GAP-20: doc-tspec-reviewer/SKILL.md Nested Folder Table

**Location**: Lines 119-124

**Current**: Only lists UTEST, ITEST, STEST, FTEST in nested folder table

**Required**: Add PTEST and SECTEST rows:

```markdown
| PTEST | `docs/10_TSPEC/PTEST/PTEST-NN_{slug}/PTEST-NN_{slug}.md` |
| SECTEST | `docs/10_TSPEC/SECTEST/SECTEST-NN_{slug}/SECTEST-NN_{slug}.md` |
```

**Fix**: Add PTEST and SECTEST to nested folder required structure table

---

### GAP-21: doc-tspec-reviewer/SKILL.md Element Type Codes

**Location**: Line 287 (Section 8. Naming Compliance)

**Current**:

```markdown
- Element type codes valid for TSPEC (40, 41, 42, 43)
```

**Required**:

```markdown
- Element type codes valid for TSPEC (40, 41, 42, 43, 44, 45)
```

**Fix**: Add codes 44 and 45 to valid element type codes

---

### GAP-22: doc-tspec-fixer/SKILL.md Nested Folder Table

**Location**: Lines 115-120

**Current**: Only lists UTEST, ITEST, STEST, FTEST in required structure table

**Required**: Add PTEST and SECTEST rows:

```markdown
| PTEST | `docs/10_TSPEC/PTEST/PTEST-NN_{slug}/PTEST-NN_{slug}.md` |
| SECTEST | `docs/10_TSPEC/SECTEST/SECTEST-NN_{slug}/SECTEST-NN_{slug}.md` |
```

**Fix**: Add PTEST and SECTEST to nested folder required structure table

---

### GAP-23: doc-tspec-fixer/SKILL.md Type Code Mapping

**Location**: Lines 369-381

**Current**: Type Code Mapping table only shows codes 40-43

**Required**: Add entries for 44 and 45:

```markdown
| 44 | PTEST | Performance Test Case |
| 45 | SECTEST | Security Test Case |
```

**Fix**: Add PTEST (44) and SECTEST (45) to valid TSPEC type codes table

---

### GAP-24: doc-tspec-validator/SKILL.md Section 0 Nested Folder Table

**Location**: Lines 69-74

**Current**: Only lists UTEST, ITEST, STEST, FTEST in required structure table

**Required**: Add PTEST and SECTEST rows:

```markdown
| PTEST | `docs/10_TSPEC/PTEST/PTEST-NN_{slug}/PTEST-NN_{slug}.md` |
| SECTEST | `docs/10_TSPEC/SECTEST/SECTEST-NN_{slug}/SECTEST-NN_{slug}.md` |
```

**Fix**: Add PTEST and SECTEST to nested folder required structure table

---

### GAP-25: Section Count Mismatch Between Templates and Validator

**Location**: Multiple files

**Current**:

- UTEST/ITEST/STEST/FTEST/PTEST/SECTEST-MVP-TEMPLATE.md AI_CONTEXT says "6 sections required"
- doc-tspec-validator/SKILL.md Section 2 says "7 required sections"

**Analysis**: The individual templates define 6 main sections:

1. Document Control
2. Test Scope
3. Test Case Index
4. Test Case Details
5. Coverage Matrix
6. Traceability

The validator lists 7 sections including "Error Cases" as section 7.

**Fix Options**:

1. Update validator to say 6 sections (align with templates)
2. Update templates to add Error Cases as section 7
3. Clarify that Error Cases is within Test Case Details (subsection)

**Recommended Fix**: Update validator to 6 sections - Error Cases is covered within Test Case Details section per templates

---

### GAP-26: doc-tspec-reviewer/SKILL.md Version Update

**Location**: Line 19, version history section

**Current**: Version 1.4, last_updated 2026-02-11

**Fix**: Update to version 1.5 after applying fixes

---

### GAP-27: doc-tspec-fixer/SKILL.md Version Update

**Location**: Line 19, version history section

**Current**: Version 2.1, last_updated 2026-02-11

**Fix**: Update to version 2.2 after applying fixes

---

### GAP-28: UTEST-MVP-TEMPLATE.yaml Uses Wrong Traceability Structure

**Location**: Line 115 (traceability section)

**Current**:

```yaml
traceability:
  upstream:
    - tag: "@req"
      reference: "REQ.NN.27.SS"
      description: "[Requirement description]"
```

**Required** (aligned with FTEST/PTEST pattern):

```yaml
traceability:
  cumulative_tags:
    - tag: "@brd"
      reference: "BRD.NN.TT.SS"
      description: "Business requirement"
    # ... (9 cumulative tags total)
  type_specific:
    - tag: "@req"
      reference: "REQ.NN.27.SS"
      description: "Atomic requirement"
    - tag: "@spec"
      reference: "SPEC-NN"
      description: "Specification reference"
  downstream:
    - tag: "@tasks"
      reference: "TASKS-NN"
      description: "Implementation tasks"
```

**Fix**: Restructure traceability to use cumulative_tags, type_specific, downstream

---

### GAP-29: UTEST_MVP_SCHEMA.yaml Uses Wrong Traceability Structure

**Location**: Lines 287-328

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

**Required**:

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
      ...
    type_specific:
      type: array
      minItems: 1
      description: "UTEST-specific traceability tags"
      ...
```

**Fix**: Restructure schema traceability; Update x-validation-rules to reference `type_specific`

---

### GAP-30: UTEST-MVP-TEMPLATE.md Missing Cumulative Tags Section

**Location**: Lines 261+ (Section 6)

**Current**:

```markdown
### 6.1 Upstream References
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

### 6.2 UTEST-Specific Tags
...
### 6.3 Downstream References
```

**Fix**: Restructure Section 6; Update AI_CONTEXT to mention cumulative tags

---

### GAP-31: ITEST-MVP-TEMPLATE.yaml Uses Wrong Traceability Structure

**Location**: Line 128 (traceability section)

**Current**: Uses `upstream` structure

**Required**: Use `cumulative_tags`, `type_specific`, `downstream` structure (same pattern as FTEST/PTEST)

**Fix**: Restructure traceability section

---

### GAP-32: ITEST_MVP_SCHEMA.yaml Uses Wrong Traceability Structure

**Location**: Lines 223-225

**Current**:

```yaml
required:
  - upstream
properties:
  upstream:
```

**Required**:

```yaml
required:
  - cumulative_tags
  - type_specific
properties:
  cumulative_tags:
  type_specific:
```

**Fix**: Restructure schema traceability; Update x-validation-rules to reference `type_specific`

---

### GAP-33: ITEST-MVP-TEMPLATE.md Missing Cumulative Tags Section

**Location**: Lines 253+ (Section 6)

**Current**: Section 6.1 is "Upstream References"

**Required**: Section 6.1 should be "Cumulative Tags (Layer 1-9)"

**Fix**: Restructure Section 6 with cumulative tags, type-specific, downstream; Update AI_CONTEXT

---

### GAP-34: STEST-MVP-TEMPLATE.yaml Uses Wrong Traceability Structure

**Location**: Line 120 (traceability section)

**Current**: Uses `upstream` structure

**Required**: Use `cumulative_tags`, `type_specific`, `downstream` structure (same pattern as FTEST/PTEST)

**Fix**: Restructure traceability section

---

### GAP-35: STEST_MVP_SCHEMA.yaml Uses Wrong Traceability Structure

**Location**: Lines 236-238

**Current**:

```yaml
required:
  - upstream
properties:
  upstream:
```

**Required**:

```yaml
required:
  - cumulative_tags
  - type_specific
properties:
  cumulative_tags:
  type_specific:
```

**Fix**: Restructure schema traceability; Update x-validation-rules to reference `type_specific`

---

### GAP-36: STEST-MVP-TEMPLATE.md Missing Cumulative Tags Section

**Location**: Lines 316+ (Section 6)

**Current**: Section 6.1 is "Upstream References"

**Required**: Section 6.1 should be "Cumulative Tags (Layer 1-9)"

**Fix**: Restructure Section 6 with cumulative tags, type-specific, downstream; Update AI_CONTEXT

---

## Implementation Phases

### Phase 1: Path Corrections (GAP-01, GAP-02, GAP-03, GAP-04)

**Files to modify**:

1. `.claude/skills/doc-tspec/SKILL.md` - Replace `ucx_flow_v3/` with `ucx_flow_v3/`
2. `.claude/skills/doc-tspec-validator/SKILL.md` - Replace `ucx_flow_v3/` with `ucx_flow_v3/`
3. `.claude/skills/doc-tspec-autopilot/SKILL.md` - Fix template path

**Verification**:

```bash
grep -r "ucx_flow_v3/10_TSPEC" .claude/skills/
# Expected: No results
```

---

### Phase 2: Add PTEST/SECTEST Support (GAP-05, GAP-06, GAP-07, GAP-18, GAP-19, GAP-20, GAP-21, GAP-22, GAP-23, GAP-24)

**Files to modify**:

1. `.claude/skills/doc-tspec/SKILL.md` - Add PTEST (44) and SECTEST (45) to element type tables and type-specific sections
2. `.claude/skills/doc-tspec-validator/SKILL.md` - Add PTEST and SECTEST validation rules and nested folder table
3. `.claude/skills/doc-tspec-autopilot/SKILL.md` - Add PTEST and SECTEST to test type tables
4. `.claude/skills/doc-tspec-reviewer/SKILL.md` - Update test type count (4→6), add to nested folder table, add codes 44-45
5. `.claude/skills/doc-tspec-fixer/SKILL.md` - Add to nested folder table, add codes 44-45 to type mapping
6. `ucx_flow_v3/10_TSPEC/TSPEC-MVP-TEMPLATE.yaml` - Verify PTEST/SECTEST link paths

**Element Type Code Reference**:

| Type | Code | Purpose |
| ---- | ---- | ------- |
| UTEST | 40 | Unit tests |
| ITEST | 41 | Integration tests |
| STEST | 42 | Smoke tests |
| FTEST | 43 | Functional tests |
| PTEST | 44 | Performance tests |
| SECTEST | 45 | Security tests |

---

### Phase 3: Cumulative Tag Format Fix (GAP-08, GAP-09)

**Files to modify**:

1. `.claude/skills/doc-tspec-autopilot/SKILL.md` - Fix @spec tag format from `SPEC.NN.TT.SS` to `SPEC-NN`
2. `ucx_flow_v3/10_TSPEC/TSPEC-MVP-TEMPLATE.md` - Clarify section count in AI_CONTEXT

**Verification**:

```bash
grep -n "@spec: SPEC\." .claude/skills/doc-tspec-autopilot/SKILL.md
# Expected: No results (should use SPEC-NN format)
```

---

### Phase 4: Directory Structure Consistency (GAP-11, GAP-12, GAP-17)

**Files to modify**:

1. `ucx_flow_v3/10_TSPEC/TSPEC-MVP-TEMPLATE.md` - Update appendix to show nested folder structure
2. `.claude/skills/doc-tspec-validator/SKILL.md` - Update Section 6 to show nested folder structure

---

### Phase 5: Create Quick Reference (GAP-13)

**File to create**:

`.claude/skills/doc-tspec_quickref.md`

**Content summary**:

- Layer: 10
- Artifact Type: TSPEC
- Test Type Codes: 40-45
- Output path pattern
- Required tags (8-9 cumulative)
- Template locations
- Nested folder rule

---

### Phase 6: Section Count Clarification (GAP-10, GAP-25)

**Files to modify**:

1. `.claude/skills/doc-tspec-validator/SKILL.md` - Update Section 2 from "7 required sections" to "6 required sections" to align with templates
2. Remove "Error Cases" as a separate section (it's a subsection of Test Case Details)

**Reasoning**: The subtype templates (UTEST, ITEST, STEST, FTEST, PTEST, SECTEST) all define 6 sections with Error Cases embedded within Test Case Details. The validator should align with the templates.

---

### Phase 7: Aggregator vs Individual Template Clarification (GAP-09)

**Files to modify**:

1. `ucx_flow_v3/10_TSPEC/TSPEC-MVP-TEMPLATE.md` - Clarify that aggregator has 5 sections vs individual test types which have 6 sections
2. Add note distinguishing aggregator template purpose from individual test type templates

---

### Phase 8: Version Updates (GAP-14, GAP-15, GAP-16, GAP-26, GAP-27)

**Files to modify**:

1. `.claude/skills/doc-tspec/SKILL.md` - Update to version 1.1
2. `.claude/skills/doc-tspec-validator/SKILL.md` - Update to version 1.2
3. `.claude/skills/doc-tspec-autopilot/SKILL.md` - Update to version 2.5
4. `.claude/skills/doc-tspec-reviewer/SKILL.md` - Update to version 1.5
5. `.claude/skills/doc-tspec-fixer/SKILL.md` - Update to version 2.2

---

### Phase 9: Traceability Structure Modernization (GAP-28 through GAP-36)

**Overview**: FTEST and PTEST have been updated to use the modern `cumulative_tags`/`type_specific` traceability structure. UTEST, ITEST, and STEST still use the deprecated `upstream` structure and need to be aligned.

**Files to modify**:

| Subtype | YAML Template | Schema | MD Template |
| ------- | ------------- | ------ | ----------- |
| UTEST | UTEST-MVP-TEMPLATE.yaml | UTEST_MVP_SCHEMA.yaml | UTEST-MVP-TEMPLATE.md |
| ITEST | ITEST-MVP-TEMPLATE.yaml | ITEST_MVP_SCHEMA.yaml | ITEST-MVP-TEMPLATE.md |
| STEST | STEST-MVP-TEMPLATE.yaml | STEST_MVP_SCHEMA.yaml | STEST-MVP-TEMPLATE.md |

**Changes per subtype** (9 files total):

1. **YAML Template** (`*-MVP-TEMPLATE.yaml`):
   - Replace `upstream:` with `cumulative_tags:` + `type_specific:` + `downstream:` structure
   - Add 9 cumulative tags (@brd, @prd, @ears, @bdd, @adr, @sys, @req, @spec, @ctr)
   - Move subtype-specific tags (e.g., @req for UTEST) to `type_specific` section

2. **Schema** (`*_MVP_SCHEMA.yaml`):
   - Change `required: - upstream` to `required: - cumulative_tags - type_specific`
   - Replace `upstream:` property with `cumulative_tags:` and `type_specific:` properties
   - Update `x-validation-rules` to reference `type_specific` instead of `upstream`

3. **MD Template** (`*-MVP-TEMPLATE.md`):
   - Rename "6.1 Upstream References" to "6.1 Cumulative Tags (Layer 1-9)"
   - Add cumulative tags table (9 tags)
   - Add "6.2 {SUBTYPE}-Specific Tags" section
   - Rename downstream section to "6.3 Downstream References"
   - Update AI_CONTEXT to mention cumulative tags requirement

**Reference patterns** (already implemented):

- `FTEST-MVP-TEMPLATE.yaml` - Line 128: `cumulative_tags:`
- `PTEST-MVP-TEMPLATE.yaml` - Line 148: `cumulative_tags:`
- `FTEST-MVP-TEMPLATE.md` - Section 6.1: "Cumulative Tags (Required)"

**Subtype-specific tags reference**:

| Subtype | Type-Specific Tags | Type Code |
| ------- | ------------------ | --------- |
| UTEST | @req, @spec | 40 |
| ITEST | @req, @spec, @ctr | 41 |
| STEST | @spec | 42 |
| FTEST | @sys, @threshold | 43 |
| PTEST | @sys, @spec | 44 |
| SECTEST | @sec, @spec, @ctr | 45 |

**Verification**:

```bash
# Verify YAML templates use cumulative_tags structure
grep -n "cumulative_tags\|type_specific" ucx_flow_v3/10_TSPEC/UTEST/UTEST-MVP-TEMPLATE.yaml
grep -n "cumulative_tags\|type_specific" ucx_flow_v3/10_TSPEC/ITEST/ITEST-MVP-TEMPLATE.yaml
grep -n "cumulative_tags\|type_specific" ucx_flow_v3/10_TSPEC/STEST/STEST-MVP-TEMPLATE.yaml
# Expected: Both sections present in each

# Verify schemas use cumulative_tags structure (no upstream in required)
grep -n "upstream" ucx_flow_v3/10_TSPEC/UTEST/UTEST_MVP_SCHEMA.yaml
grep -n "upstream" ucx_flow_v3/10_TSPEC/ITEST/ITEST_MVP_SCHEMA.yaml
grep -n "upstream" ucx_flow_v3/10_TSPEC/STEST/STEST_MVP_SCHEMA.yaml
# Expected: 0 results or only in description text

# Verify MD templates have Cumulative Tags section
grep -c "Cumulative Tags" ucx_flow_v3/10_TSPEC/UTEST/UTEST-MVP-TEMPLATE.md
grep -c "Cumulative Tags" ucx_flow_v3/10_TSPEC/ITEST/ITEST-MVP-TEMPLATE.md
grep -c "Cumulative Tags" ucx_flow_v3/10_TSPEC/STEST/STEST-MVP-TEMPLATE.md
# Expected: ≥1 each

# Verify AI_CONTEXT mentions cumulative tags
grep -i "cumulative" ucx_flow_v3/10_TSPEC/UTEST/UTEST-MVP-TEMPLATE.md
grep -i "cumulative" ucx_flow_v3/10_TSPEC/ITEST/ITEST-MVP-TEMPLATE.md
grep -i "cumulative" ucx_flow_v3/10_TSPEC/STEST/STEST-MVP-TEMPLATE.md
# Expected: Results showing cumulative tags in AI_CONTEXT
```

---

## Verification Commands

```bash
# Phase 1: Verify no old paths remain in all TSPEC skills
grep -rn "ucx_flow_v3/10_TSPEC" .claude/skills/doc-tspec*.md

# Phase 2: Verify PTEST/SECTEST codes present in all 5 skill files
grep -n "code 44\|code 45\|PTEST\|SECTEST" .claude/skills/doc-tspec/SKILL.md
grep -n "PTEST\|SECTEST" .claude/skills/doc-tspec-validator/SKILL.md
grep -n "PTEST\|SECTEST" .claude/skills/doc-tspec-autopilot/SKILL.md
grep -n "PTEST\|SECTEST" .claude/skills/doc-tspec-reviewer/SKILL.md
grep -n "PTEST\|SECTEST" .claude/skills/doc-tspec-fixer/SKILL.md

# Phase 3: Verify @spec format uses dash notation
grep -n "@spec: SPEC\." .claude/skills/doc-tspec-autopilot/SKILL.md
# Expected: No results (should use SPEC-NN format)

# Phase 4: Verify nested folder structure documented
grep -A5 "Appendix" ucx_flow_v3/10_TSPEC/TSPEC-MVP-TEMPLATE.md

# Phase 5: Verify quick reference exists
ls -la .claude/skills/doc-tspec_quickref.md

# Phase 6: Verify section count alignment (should be 6, not 7)
grep -n "7 required sections" .claude/skills/doc-tspec-validator/SKILL.md
# Expected: No results after fix

# Phase 8: Verify version updates in all 5 skill files
grep "version:" .claude/skills/doc-tspec/SKILL.md
grep "version:" .claude/skills/doc-tspec-validator/SKILL.md
grep "version:" .claude/skills/doc-tspec-autopilot/SKILL.md
grep "version:" .claude/skills/doc-tspec-reviewer/SKILL.md
grep "version:" .claude/skills/doc-tspec-fixer/SKILL.md
```

## Risk Assessment

| Risk | Mitigation |
| ---- | ---------- |
| Breaking existing validation scripts | Scripts reference correct paths already in `ucx_flow_v3/` |
| Missing PTEST/SECTEST in existing documents | Graceful degradation - codes 44-45 are optional |
| Confusion with section counts | Clear documentation distinguishes aggregator (5) vs individual (6) sections |
| Reviewer/fixer not aligned | Both updated in same phase to maintain consistency |
| Phase 9: Schema changes break validation | Test with existing documents before deployment; changes are additive |
| Phase 9: Inconsistency between subtypes | Use FTEST/PTEST as reference patterns; verify all 6 subtypes consistent |
| Phase 9: MD/YAML template drift | Verify both templates have identical traceability structure per subtype |

## Files Modified Summary

| File | Phase(s) | Changes |
| ---- | -------- | ------- |
| `.claude/skills/doc-tspec/SKILL.md` | 1, 2, 8 | Path fix, PTEST/SECTEST, version |
| `.claude/skills/doc-tspec-validator/SKILL.md` | 1, 2, 4, 6, 8 | Path fix, PTEST/SECTEST, nested folders, section count, version |
| `.claude/skills/doc-tspec-autopilot/SKILL.md` | 1, 2, 3, 8 | Path fix, PTEST/SECTEST, @spec format, version |
| `.claude/skills/doc-tspec-reviewer/SKILL.md` | 2, 8 | PTEST/SECTEST (count, table, codes), version |
| `.claude/skills/doc-tspec-fixer/SKILL.md` | 2, 8 | PTEST/SECTEST (table, codes), version |
| `ucx_flow_v3/10_TSPEC/TSPEC-MVP-TEMPLATE.md` | 4, 7 | Nested folder structure, section clarification |
| `.claude/skills/doc-tspec_quickref.md` | 5 | New file creation |
| `ucx_flow_v3/10_TSPEC/UTEST/UTEST-MVP-TEMPLATE.yaml` | 9 | Traceability: cumulative_tags + type_specific structure |
| `ucx_flow_v3/10_TSPEC/UTEST/UTEST_MVP_SCHEMA.yaml` | 9 | Schema traceability + x-validation-rules update |
| `ucx_flow_v3/10_TSPEC/UTEST/UTEST-MVP-TEMPLATE.md` | 9 | Section 6 restructure + AI_CONTEXT cumulative tags |
| `ucx_flow_v3/10_TSPEC/ITEST/ITEST-MVP-TEMPLATE.yaml` | 9 | Traceability: cumulative_tags + type_specific structure |
| `ucx_flow_v3/10_TSPEC/ITEST/ITEST_MVP_SCHEMA.yaml` | 9 | Schema traceability + x-validation-rules update |
| `ucx_flow_v3/10_TSPEC/ITEST/ITEST-MVP-TEMPLATE.md` | 9 | Section 6 restructure + AI_CONTEXT cumulative tags |
| `ucx_flow_v3/10_TSPEC/STEST/STEST-MVP-TEMPLATE.yaml` | 9 | Traceability: cumulative_tags + type_specific structure |
| `ucx_flow_v3/10_TSPEC/STEST/STEST_MVP_SCHEMA.yaml` | 9 | Schema traceability + x-validation-rules update |
| `ucx_flow_v3/10_TSPEC/STEST/STEST-MVP-TEMPLATE.md` | 9 | Section 6 restructure + AI_CONTEXT cumulative tags |

## Completion Criteria

### Phases 1-8 (Completed)

- [x] All `ucx_flow_v3/` paths replaced with `ucx_flow_v3/`
- [x] PTEST (code 44) and SECTEST (code 45) added to all 5 skill files
- [x] @spec tag format uses dash notation (SPEC-NN)
- [x] Nested folder structure documented consistently (includes PTEST/SECTEST)
- [x] Quick reference file created
- [x] Section count aligned: 6 sections for individual templates
- [x] Version histories updated for all 5 skill files
- [x] Phases 1-8 verification commands pass

### Phase 9: Traceability Structure Modernization (Pending)

- [ ] UTEST-MVP-TEMPLATE.yaml uses `cumulative_tags`/`type_specific` structure
- [ ] UTEST_MVP_SCHEMA.yaml uses `cumulative_tags`/`type_specific`; x-validation-rules reference `type_specific`
- [ ] UTEST-MVP-TEMPLATE.md Section 6.1 is "Cumulative Tags (Layer 1-9)"; AI_CONTEXT mentions cumulative tags
- [ ] ITEST-MVP-TEMPLATE.yaml uses `cumulative_tags`/`type_specific` structure
- [ ] ITEST_MVP_SCHEMA.yaml uses `cumulative_tags`/`type_specific`; x-validation-rules reference `type_specific`
- [ ] ITEST-MVP-TEMPLATE.md Section 6.1 is "Cumulative Tags (Layer 1-9)"; AI_CONTEXT mentions cumulative tags
- [ ] STEST-MVP-TEMPLATE.yaml uses `cumulative_tags`/`type_specific` structure
- [ ] STEST_MVP_SCHEMA.yaml uses `cumulative_tags`/`type_specific`; x-validation-rules reference `type_specific`
- [ ] STEST-MVP-TEMPLATE.md Section 6.1 is "Cumulative Tags (Layer 1-9)"; AI_CONTEXT mentions cumulative tags
- [ ] Phase 9 verification commands pass

---

## Extended Implementation: Subtype Files

Beyond the original 27 gaps in skill files and main templates, the following subtype-specific files were also updated to align with the fixes:

### Files Updated

| Subtype | Creation Rules | Validation Rules | Quality Gates |
| ------- | -------------- | ---------------- | ------------- |
| UTEST | ✓ Nested folder + Cumulative tags | ✓ Folder validation (BLOCKING) + Cumulative tags | ✓ Checklist + Commands |
| ITEST | ✓ Nested folder + Cumulative tags | ✓ Folder validation (BLOCKING) + Cumulative tags | ✓ Checklist + Commands |
| STEST | ✓ Nested folder + Cumulative tags | ✓ Folder validation (BLOCKING) + Cumulative tags | ✓ Checklist + Commands |
| FTEST | ✓ Nested folder + Cumulative tags | ✓ Folder validation (BLOCKING) + Cumulative tags | ✓ Checklist + Commands |
| PTEST | ✓ Nested folder + Cumulative tags | ✓ Folder validation (BLOCKING) + Cumulative tags | ✓ Checklist + Commands |
| SECTEST | ✓ Nested folder + Cumulative tags | ✓ Folder validation (BLOCKING) + Cumulative tags | ✓ Checklist + Commands |

### Changes Applied to Each Subtype

**Creation Rules (_MVP_CREATION_RULES.md)**:
- Added nested folder structure documentation with example directory tree
- Added Cumulative Tags section (Layer 10 - 8-9 Required tags)
- Added subtype-specific required tags section
- Updated validation command paths to use nested folder structure

**Validation Rules (_MVP_VALIDATION_RULES.md)**:
- Added Folder Structure Validation (BLOCKING) section at top
- Added Cumulative Tags (Layer 10 - 8-9 Required) section with regex patterns
- Added subtype-specific tags section

**Quality Gates (_MVP_QUALITY_GATES.md)**:
- Updated TASKS-Ready checklist with:
  - "Document in nested folder structure" requirement
  - "Cumulative tags present (8-9 tags)" requirement
  - Subtype-specific tags requirement
- Updated validation commands to use nested folder paths

### Verification

```bash
# Verify nested folder rule in all subtypes
grep -rn "Nested Folder Rule" ucx_flow_v3/10_TSPEC/*/
# Expected: 12 results (2 per subtype: Creation Rules + Validation Rules)

# Verify cumulative tags in all subtypes
grep -rn "Cumulative Tags" ucx_flow_v3/10_TSPEC/*/
# Expected: 12+ results (Creation Rules, Validation Rules, some templates)

# Verify quality gate checklists updated
grep -rn "Document in nested folder" ucx_flow_v3/10_TSPEC/*/
# Expected: 6 results (one per subtype Quality Gates file)
```

---

## Version History

| Version | Date | Changes | Author |
| ------- | ---- | ------- | ------ |
| 1.5 | 2026-02-26 | Added Phase 9 (GAP-28 through GAP-36) for traceability structure modernization; UTEST/ITEST/STEST templates and schemas need cumulative_tags/type_specific structure; Status changed to PENDING; Now 36 gaps total | System |
| 1.4 | 2026-02-26 | Extended implementation to all 6 subtype files (18 files total); Added nested folder + cumulative tags to Creation Rules, Validation Rules, Quality Gates | System |
| 1.3 | 2026-02-26 | IMPLEMENTED all 27 gaps across 8 phases; Updated status to IMPLEMENTED; Marked all completion criteria as done | System |
| 1.2 | 2026-02-26 | Fixed markdown linting issues (MD060 table column style, MD031 fenced code blocks) | System |
| 1.1 | 2026-02-26 | Added 9 new gaps (GAP-19 through GAP-27) for reviewer/fixer skills; Updated to 8 phases; Added file summary table | System |
| 1.0 | 2026-02-26 | Initial fix plan with 18 gaps across 7 phases | System |
