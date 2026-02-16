---
id: CHG-XX
title: Title of Change
tags:
  - change-document
  - architectural-change
  - shared-architecture
custom_fields:
  document_type: change-record
  artifact_type: CHG
  layer: null
  change_level: L3
  change_source: null
  development_status: proposed
status: Proposed
date: YYYY-MM-DDTHH:MM:SS
author: [Author Name]
supersedes: [List, of, Artifact, IDs]
---

# CHG-XX: [Title of Change]

> **Change Level**: L3 (Major) - Full CHG process required
> **Change Source**: [Upstream | Midstream | Downstream | External | Feedback]
> **Entry Gate**: [GATE-01 | GATE-05 | GATE-09 | GATE-12]

## Gate Information

| Attribute | Value |
|-----------|-------|
| **Entry Gate** | GATE-XX |
| **Gate Status** | [ ] Pending / [ ] In Progress / [ ] Passed / [ ] Failed |
| **Validation Date** | YYYY-MM-DDTHH:MM:SS |
| **Validation Result** | [Exit code: 0/1/2] |

### Gate Cascade Path

| Gate | Status | Errors | Warnings | Date |
|------|--------|--------|----------|------|
| GATE-01 | [ ] N/A / [ ] Passed / [ ] Failed | | | |
| GATE-05 | [ ] N/A / [ ] Passed / [ ] Failed | | | |
| GATE-09 | [ ] N/A / [ ] Passed / [ ] Failed | | | |
| GATE-12 | [ ] N/A / [ ] Passed / [ ] Failed | | | |

---

## 1. Overview

[Brief summary of the change. What is changing and why?]

### 1.1 Change Classification

| Attribute | Value |
|-----------|-------|
| **Change Level** | L3 - Major (Architectural Pivot) |
| **Change Source** | [See Section 1.2] |
| **Estimated Impact** | [Low / Medium / High / Critical] |
| **Regeneration Scope** | [List affected layers] |

### 1.2 Change Source Identification

| Source Type | Applicable? | Details |
|-------------|-------------|---------|
| **Upstream** (L1-L4) | Yes/No | Business/Product requirement change |
| **Midstream** (L5-L11) | Yes/No | Architecture/Design decision |
| **Downstream** (L12-L14) | Yes/No | Implementation defect bubbling up |
| **External** | Yes/No | Dependency/Security/Third-party change |
| **Feedback** | Yes/No | Production incident/User feedback |

### 1.3 Reason for Change

1. **[Reason 1]**: [Explanation]
2. **[Reason 2]**: [Explanation]

## 2. Scope & Impact Analysis

### 2.1 Scope Definition

> **Critical**: Explicitly define what is changing and what is *NOT* changing.

| Category | Items |
|----------|-------|
| **Replacing** | [List components/services being retired] |
| **Retaining** | [List related components staying active] |
| **Adding** | [List new components being introduced] |
| **Reasoning** | [Why this specific scope?] |

### 2.2 Impact Matrix (15-Layer V-Model)

> **Rule**: You MUST identify impacted artifacts at EVERY affected layer. Do not skip layers.

| Layer | Type | Archived Artifacts (Old) | New Artifacts (Replacement) | Impact |
|-------|------|--------------------------|-----------------------------|---------|
| 0 | Strategy | - | - | ○ None |
| 1 | BRD | `BRD-XX` | `BRD-YY` | ○/● |
| 2 | PRD | `PRD-XX` | `PRD-YY` | ○/● |
| 3 | EARS | `EARS-XX` | `EARS-YY` | ○/● |
| 4 | BDD | `BDD-XX` | `BDD-YY` | ○/● |
| 5 | ADR | `ADR-XX` | `ADR-YY` | ○/● |
| 6 | SYS | `SYS-XX` | `SYS-YY` | ○/● |
| 7 | REQ | `REQ-XX` | `REQ-YY` | ○/● |
| 8 | CTR | `CTR-XX` | `CTR-YY` | ○/● |
| 9 | SPEC | `SPEC-XX` | `SPEC-YY` | ○/● |
| 10 | **TSPEC** | `TSPEC-XX` | `TSPEC-YY` | ○/● |
| 11 | TASKS | `TASKS-XX` | `TASKS-YY` | ○/● |
| 12 | Code | `src/...` | `src/...` | ○/● |
| 13 | Tests | `tests/...` | `tests/...` | ○/● |
| 14 | Validation | `validation/...` | `validation/...` | ○/● |

**Legend**: ○ No impact | ● Impacted

### 2.3 Dependency Check

- [ ] **Upstream**: Have I checked all documents creating requirements for these components?
- [ ] **Downstream**: Have I checked all code/configs that depend on these components?
- [ ] **Cross-references**: Have I searched for all traceability tags referencing affected artifacts?
- [ ] **Search**: Have I grepped the `docs/` folder for relevant keywords?

```bash
# Example search commands
grep -r "ARTIFACT_ID" docs/
grep -r "keyword" docs/ --include="*.md" --include="*.yaml"
```

### 2.4 Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk 1] | Low/Med/High | Low/Med/High | [Mitigation strategy] |
| [Risk 2] | Low/Med/High | Low/Med/High | [Mitigation strategy] |

## 3. Migration Steps

See `implementation_plan.md` in this directory for the detailed audit log.

### 3.1 Summary

| Step | Action | Status |
|------|--------|--------|
| 1 | **Initialize** | ☐ Pending |
| 2 | **Archive & Deprecate** | ☐ Pending |
| 3 | **Create New Artifacts** | ☐ Pending |
| 4 | **Repair Traceability** | ☐ Pending |
| 5 | **Execute & Validate** | ☐ Pending |
| 6 | **Close** | ☐ Pending |

### 3.2 Step Details

1. **Initialize**: Create CHG directory and implementation plan
2. **Archive & Deprecate**: Move old artifacts to `archive/` with deprecation notices
3. **Create New Artifacts**: Generate replacement artifacts in standard locations
4. **Repair Traceability**: Update all upstream/downstream references
5. **Execute & Validate**: Implement TASKS, run TSPEC tests, validate
6. **Close**: Update status to Completed, document lessons learned

## 4. Rollback Plan

If this change fails verification:

| Step | Action | Command/Procedure |
|------|--------|-------------------|
| 1 | Stop implementation | [How to halt] |
| 2 | Restore archived artifacts | `mv archive/* ../original_locations/` |
| 3 | Revert code changes | `git revert` or `git reset` |
| 4 | Notify stakeholders | [Communication plan] |
| 5 | Post-mortem | Document failure reasons |

## 5. Verification Criteria

### 5.1 Success Criteria

- [ ] All new artifacts pass validation scripts
- [ ] All TSPEC tests pass
- [ ] Traceability matrix is complete (no orphans)
- [ ] No references to archived artifacts in active documents
- [ ] Code builds and deploys successfully

### 5.2 Quality Gates

| Gate | Threshold | Validation Command |
|------|-----------|-------------------|
| TSPEC Coverage | ≥85% | `python 10_TSPEC/scripts/validate_tspec.py` |
| Traceability | 100% | `python scripts/validate_traceability_matrix.py` |
| Tests Pass | 100% | `pytest tests/` |

## 6. Traceability

### 6.1 Cross-Linking Tags

```markdown
@depends: [CHG-NN if this depends on another change]
@discoverability: [Related CHG documents for AI search]
```

### 6.2 Upstream References

| Tag | Reference | Description |
|-----|-----------|-------------|
| @source | [Source document/request] | Origin of change request |

### 6.3 Downstream References

| Tag | Reference | Description |
|-----|-----------|-------------|
| @impl | [Implementation artifacts] | Where change is implemented |

## 7. Approval & Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Change Author | | | ☐ |
| Technical Lead | | | ☐ |
| Product Owner | | | ☐ |
| QA Lead | | | ☐ |

---

## Appendix: Implementation Plan Reference

The detailed implementation plan is maintained in:
`implementation_plan.md` (in this CHG directory)

This document serves as the frozen audit log of all execution steps.
