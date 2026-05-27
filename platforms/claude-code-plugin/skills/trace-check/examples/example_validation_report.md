# Traceability Validation Report - Example

**Project**: [PROJECT_NAME]
**Validation Date**: 2025-11-11 17:40:01 EST
**Scope**: All artifacts (8 SPEC files)
**Execution Time**: 4.2 seconds

## Summary

- ✅ **Overall Status**: PASS (with warnings)
- 📊 **Coverage**: 88% (7/8 complete)
- 🔗 **Consistency**: 75% (6/8 links bidirectional)
- ⚠️ **Warnings**: 1 missing reverse link
- ❌ **Errors**: 0 blocking issues

## Broken Links (0 found)

No broken links detected.

## Missing Traceability (1 artifact)

| Artifact | Issue | Severity | Recommendation |
|----------|-------|----------|----------------|
| SPEC-03 | No TDD reference in Section 7.2 | Info | Add TDD-NN when tests created |

**Details**:

- **File**: `{project_root}/docs/06_SPEC/SPEC-03_data_service.yaml`
- **Line**: 45-52 (Section 7: Traceability)
- **Issue**: Downstream section lists "To Be Created" but no specific TDD reference
- **Impact**: Low (common for new specifications before test creation)

## Bidirectional Inconsistencies (1 found)

| Forward Link | Reverse Link | Status | Fix Command |
|--------------|--------------|--------|-------------|
| SPEC-01 → ADR-02 | ADR-02 → SPEC-01 | ❌ Missing | Add to ADR-02:463 |

### Fix Details

**Issue**: SPEC-01 references ADR-02 (line 56), but ADR-02 does not reference SPEC-01 back.

**Current State** (ADR-02:462-467):

```markdown
## 7.2 Downstream Artifacts

**To Be Created:**
- SPEC-NN: Technical implementation specifications
```

**Recommended Fix** (ADR-02:462-470):

```markdown
## 7.2 Downstream Artifacts

**In Progress:**
- [SPEC-01](../06_SPEC/SPEC-01_connection_service.yaml#connection_service) - Connection Service (Status: Draft, Created: 2025-11-11)

**To Be Created:**
- SPEC-02+: Additional technical specifications (TBD)
```

**Auto-fix Command**:

```bash
/skill trace-check --auto-fix true --artifact-types SPEC
```

## ID Format Compliance (8/8 PASS)

All SPEC artifacts follow correct ID naming conventions (document refs are
`SPEC-NN`, two-digit, per `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`):

| Artifact | ID Format | H1 Header | Zero-Padding | Status |
|----------|-----------|-----------|--------------|--------|
| SPEC-01 | ✅ Valid | ✅ Present | ✅ 01 | PASS |
| SPEC-02 | ✅ Valid | ✅ Present | ✅ 02 | PASS |
| SPEC-03 | ✅ Valid | ✅ Present | ✅ 03 | PASS |
| SPEC-04 | ✅ Valid | ✅ Present | ✅ 04 | PASS |
| SPEC-05 | ✅ Valid | ✅ Present | ✅ 05 | PASS |
| SPEC-06 | ✅ Valid | ✅ Present | ✅ 06 | PASS |
| SPEC-07 | ✅ Valid | ✅ Present | ✅ 07 | PASS |
| SPEC-08 | ✅ Valid | ✅ Present | ✅ 08 | PASS |

## Link Resolution (24/24 PASS)

All markdown links resolve to valid files with correct anchors. SPEC (Layer 6)
upstream sources are BRD, PRD, EARS, BDD, and ADR — there is no SYS or REQ
layer in the 8-layer model:

| Source | Target | Type | Anchor | Status |
|--------|--------|------|--------|--------|
| SPEC-01 | BRD-01 | .md | #BRD-01 | ✅ |
| SPEC-01 | EARS-02 | .md | #service_connection | ✅ |
| SPEC-01 | EARS-01 | .md | #EARS-01 | ✅ |
| SPEC-01 | ADR-02 | .md | #ADR-02 | ✅ |
| SPEC-02 | BRD-01 | .md | #BRD-01 | ✅ |
| SPEC-02 | EARS-03 | .md | #EARS-03 | ✅ |
| ... | ... | ... | ... | ... |

## Coverage Metrics

| Type | Total | Complete | Coverage | Target | Status |
|------|-------|----------|----------|--------|--------|
| SPEC | 8     | 7        | 88%      | 100%   | ⚠️     |

**Complete**: Artifacts with Section 7 containing upstream sources and downstream artifacts (or "To Be Created" note)

**Incomplete**:

- SPEC-03: Missing specific TDD reference (has generic "To Be Created")

## Orphaned Artifacts (0 found)

No orphaned artifacts detected. All SPEC files have:

- ✅ At least one upstream source (BRD, PRD, EARS, BDD, or ADR)
- ✅ At least one downstream artifact or "To Be Created" note

## Recommendations

### High Priority

**1. Fix SPEC-01 → ADR-02 reverse link**

- **Issue**: Impacts traceability integrity (bidirectional consistency at 75%)
- **Action**: Add SPEC-01 reference to ADR-02 Section 7.2
- **Estimated Time**: 2 minutes (manual edit)
- **Auto-fix**: Available via `--auto-fix true` flag

### Medium Priority

**2. Add TDD reference to SPEC-03**

- **Issue**: Missing downstream test reference
- **Action**: Create TDD-NN test specification and update SPEC-03
- **Estimated Time**: 30 minutes (TDD creation + link update)
- **Note**: Normal for new specifications; address during test planning

### Maintenance

**3. Run trace-check weekly**

- **Purpose**: Catch new traceability issues early
- **Schedule**: Before weekly team review or sprint planning
- **Command**: `/skill trace-check --strictness-level strict`
- **Expected Time**: <30 seconds for current 8 SPEC files

## Validation Details

**Artifacts Scanned**: 8
**Links Validated**: 24
**ID Format Checks**: 8
**Bidirectional Pairs Checked**: 8
**Execution Time**: 4.2 seconds

**Validation Parameters**:

- `project_root_path`: `{project_root}/docs/`
- `artifact_types`: `["SPEC"]`
- `strictness_level`: `"strict"`
- `auto_fix`: `false`
- `report_format`: `"markdown"`

## Next Steps

1. **Immediate**: Review and approve ADR-02 fix (see Fix Details above)
2. **Short-term**: Add TDD reference to SPEC-03 when tests are created
3. **Ongoing**: Run trace-check before all documentation commits
4. **Future**: Consider CI/CD integration for automated traceability validation

---

**Report Generated By**: trace-check skill v3.0.0
**Report Format**: Markdown
**Total Report Generation Time**: 4.2 seconds
