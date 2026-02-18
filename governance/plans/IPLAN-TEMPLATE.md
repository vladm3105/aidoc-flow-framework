# IPLAN-NNN: {Title}

**Phase**: {N} (or "Cross-phase")
**Status**: Draft | Approved | In Progress | Complete | Superseded
**Created**: {DATE}
**Issues**: #{ISSUE_NUMBER} or list of affected issues
**Epic**: #{EPIC_NUMBER} (parent epic)
**Applies Before**: {MILESTONE_OR_DATE}

---

## SDD Traceability (if source:sdd)

<!-- Complete if issue has source:sdd label, otherwise delete this section -->

| Tag | Reference | Description |
|-----|-----------|-------------|
| @tasks | TASKS-NN.MM.PP | Source task element |
| @spec | SPEC-NN | Technical specification |
| @req | REQ-NN:REQ.NN.MM | Atomic requirement |
| @sys | SYS-NN:SYS.NN.MM | System requirement |
| @adr | ADR-NN | Architecture decision |
| @ears | EARS-NN:EARS.NN.MM | Formal requirement |
| @brd | BRD-NN:BRD.NN.MM | Business requirement |

**TASKS Source File**: `docs/11_TASKS/TASKS-NN_{slug}.yaml`

---

## Purpose

{One paragraph describing what this plan addresses and why it's needed.}

---

## Findings

| # | Finding | Severity | Impact |
|---|---------|----------|--------|
| 1 | {Description} | HIGH/MEDIUM/LOW | {Impact description} |
| 2 | {Description} | HIGH/MEDIUM/LOW | {Impact description} |

---

## Analysis

### Current State

{Describe the current state of the system/process being addressed.}

### Target State

{Describe the desired end state after this plan is executed.}

### Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| #{ISSUE} | Blocks | Open/Closed |
| #{ISSUE} | Depends on | Open/Closed |

---

## Corrected Dependency Graph (if applicable)

**Before:**
```
Issue A → Issue B → Issue C
```

**After:**
```
Issue A  Issue B
           Issue C (parallel)
```

---

## Revised Schedule (if applicable)

| Task | Original Date | New Date | Reason |
|------|--------------|----------|--------|
| {Task} | {DATE} | {DATE} | {Reason for change} |

---

## Change Execution Checklist

### Pre-Implementation
- [ ] Review related governance docs
- [ ] Confirm dependencies are resolved
- [ ] Notify stakeholders if needed

### Implementation
- [ ] {Concrete action item with issue reference}
- [ ] {Concrete action item with file reference}
- [ ] {Concrete action item with verification step}

### Post-Implementation
- [ ] Update PROJECT_PLAN.md if needed
- [ ] Update ROADMAP.md if schedule changed
- [ ] Close/update related issues
- [ ] Mark this plan as Complete

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| {Risk description} | LOW/MEDIUM/HIGH | LOW/MEDIUM/HIGH | {Mitigation strategy} |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {DATE} | {AUTHOR} | Initial draft |
