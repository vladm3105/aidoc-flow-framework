# IPLAN-001: Phase Issue Review & Corrections

**Phase**: 1
**Status**: Template
**Created**: {DATE}
**Issues**: #{PHASE_1_ISSUES}
**Epic**: #{PHASE_1_EPIC}
**Applies Before**: Phase 1 Sprint Start

---

## Purpose

Review all Phase 1 issues before sprint begins to identify and correct any dependency ordering issues, missing acceptance criteria, or scope concerns. This is a template for conducting pre-sprint issue audits.

---

## Findings

| # | Finding | Severity | Impact |
|---|---------|----------|--------|
| 1 | Issue #{N} missing acceptance criteria | MEDIUM | Cannot verify completion |
| 2 | Issue #{N} depends on #{M} but not documented | HIGH | Blocked work |
| 3 | Issue #{N} scope too large for single sprint | MEDIUM | Risk of incomplete delivery |

---

## Analysis

### Current State

Phase 1 issues have been created based on PROJECT_PLAN.md but require validation before sprint execution:
- Dependency ordering may not reflect actual implementation needs
- Acceptance criteria may be incomplete or ambiguous
- Estimates may not account for discovered complexity

### Target State

All Phase 1 issues are:
- Properly ordered by dependency
- Have complete, verifiable acceptance criteria
- Right-sized for sprint capacity
- Labeled correctly for AI processing

### Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| PROJECT_PLAN.md finalized | Blocks | Complete |
| GitHub Project Board created | Blocks | Complete |
| Labels configured | Blocks | Complete |

---

## Change Execution Checklist

### Pre-Implementation
- [ ] Read PROJECT_PLAN.md §2 (Current State)
- [ ] Review Phase 1 epic and child issues
- [ ] Check label configuration matches GOVERNANCE_RULES.md

### Implementation
- [ ] Update issue #{N}: Add missing acceptance criteria
- [ ] Update issue #{N}: Add `Depends on #{M}` to body
- [ ] Split issue #{N} into #{N}a and #{N}b (scope too large)
- [ ] Reorder issues by corrected dependencies
- [ ] Apply `phase:1` label to all Phase 1 issues
- [ ] Apply `ai:ready` label to first issue in sequence

### Post-Implementation
- [ ] Update PROJECT_PLAN.md task list if issues split
- [ ] Verify GitHub Project Board shows correct order
- [ ] Document any scope changes in this plan
- [ ] Mark this plan as Complete

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Discovery of new dependencies mid-sprint | MEDIUM | MEDIUM | Reserve 20% capacity buffer |
| Acceptance criteria ambiguity | LOW | HIGH | Require "Given/When/Then" format |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {DATE} | {AUTHOR} | Initial template |
