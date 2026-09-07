# {PROJECT_NAME} - Project Plan

**Project**: {PROJECT_NAME} (`{PROJECT_PREFIX}`)
**Total Duration**: {TOTAL_DURATION}
**Total Sprints**: {TOTAL_SPRINTS}
**Estimated Tasks**: {ESTIMATED_TASKS}
**AI-Optimized**: {AI_OPTIMIZATION_NOTE}

> **Template Usage**: Replace all `{PLACEHOLDER}` values with project-specific content. Remove this note when complete.

---

## 1. Project Phases Overview

### Timeline Visualization

```
{TIMELINE_YEAR}
{TIMELINE_MONTHS}
 |          |          |          |          |
 v          v          v          v          v
{TIMELINE_PHASES}
```

### Phase Summary Table

| Phase | Name | Duration | Sprints | Start | End | Board Status | Epic |
|:-----:|:-----|:--------:|:-------:|:------|:----|:-------------|:----:|
| S0 | {PHASE_S0_NAME} | {DURATION} | -- | {START} | {END} | {STATUS} | -- |
| P1 | {PHASE_1_NAME} | {DURATION} | {SPRINTS} | {START} | {END} | {STATUS} | #{EPIC} |
| P2 | {PHASE_2_NAME} | {DURATION} | {SPRINTS} | {START} | {END} | {STATUS} | #{EPIC} |
| P3 | {PHASE_3_NAME} | {DURATION} | {SPRINTS} | {START} | {END} | {STATUS} | #{EPIC} |

### Phase Dependencies

```mermaid
graph TD
    S0[Sprint 0: {S0_NAME}] --> P1[Phase 1: {P1_NAME}]
    P1 --> P2[Phase 2: {P2_NAME}]
    P2 --> P3[Phase 3: {P3_NAME}]
```

| Dependency | Reason |
|:-----------|:-------|
| S0 → P1 | {DEPENDENCY_REASON_1} |
| P1 → P2 | {DEPENDENCY_REASON_2} |
| P2 → P3 | {DEPENDENCY_REASON_3} |

### Phase Descriptions

| Phase | Scope | Key Deliverables | Exit Criteria |
|:------|:------|:-----------------|:--------------|
| **S0** | {SCOPE} | {DELIVERABLES} | {EXIT_CRITERIA} |
| **P1** | {SCOPE} | {DELIVERABLES} | {EXIT_CRITERIA} |
| **P2** | {SCOPE} | {DELIVERABLES} | {EXIT_CRITERIA} |
| **P3** | {SCOPE} | {DELIVERABLES} | {EXIT_CRITERIA} |

---

## 2. Current State Analysis

### GitHub Issues Summary

| Type | Count | Issues | State | Board Status |
|:-----|:-----:|:-------|:------|:-------------|
| Phase 1 Epic | 1 | #{ISSUE} | Open | In Progress |
| Phase 2+ Epics | {COUNT} | #{ISSUES} | Open | Todo |
| Phase 1 Sub-tasks | {COUNT} | #{ISSUES} | Open | Backlog |

### Board Status Rules

| Status | Assignment | Meaning |
|:-------|:-----------|:--------|
| **Todo** | Default (automatic) | All new issues receive this via built-in workflow |
| **Backlog** | Manual (nearest phase only) | Sub-tasks of the next phase to execute; ready for sprint pull |
| **In Progress** | Manual | Actively being worked on |
| **In Review** | Manual / label sync | PR submitted, awaiting review |
| **Done** | Automatic | Issue closed or PR merged |

### Gap Analysis

| Item | Roadmap | GitHub | Gap |
|:-----|:-------:|:------:|:----|
| Sprint 0 Tasks | {COUNT} | {COUNT} | {GAP_STATUS} |
| Phase 1 Tasks | {COUNT} | {COUNT} | {GAP_STATUS} |
| Phase 2 Tasks | {COUNT} | {COUNT} | {GAP_STATUS} |

---

## 3. Sprint 0: {S0_NAME}

**Duration**: {DURATION}
**Epic**: N/A (standalone)
**Milestone**: `{PROJECT_PREFIX} - Sprint 0: {S0_NAME}`

| ID | Task | Priority | Labels | Blocks | Issue |
|:---|:-----|:---------|:-------|:-------|:------|
| 0.1 | {TASK_NAME} | P0 | `type:research` | {BLOCKS} | #{ISSUE} |
| 0.2 | {TASK_NAME} | P0 | `type:research` | {BLOCKS} | #{ISSUE} |

**Exit Criteria**: {EXIT_CRITERIA}

---

## 4. Phase 1: {P1_NAME}

**Duration**: {DURATION}
**Epic**: #{EPIC} `[Phase 1] {P1_NAME}`
**Milestone**: `{PROJECT_PREFIX} - Phase 1: {P1_NAME}`
**Depends On**: {DEPENDENCIES}
**Reference**: {REFERENCE_DOC}
**Total Effort**: {EFFORT_HOURS}
**Time Analysis**: [AI_TIME_ESTIMATION.md](./AI_TIME_ESTIMATION.md)

### Sprint 1.1: {SPRINT_NAME}

| Attribute | Value |
|:----------|:------|
| **Sprint** | 1.1 |
| **Duration** | {DURATION} |
| **Start Date** | {START_DATE} |
| **End Date** | {END_DATE} |
| **Total Effort** | {EFFORT} |
| **Buffer** | 20% included |
| **Sprint Goal** | {SPRINT_GOAL} |

#### Sprint Capacity

| Resource | Capacity | Hours/Day | Total Hours | Notes |
|:---------|:--------:|:---------:|:-----------:|:------|
| AI Agent | {PERCENT}% | {HOURS} | {TOTAL} | {NOTES} |
| Human | {PERCENT}% | {HOURS} | {TOTAL} | {NOTES} |

#### Task Details

| ID | Task | Pri | AI | AI Time | Human | Total | Depends | Reference |
|:---|:-----|:---:|:--:|:-------:|:-----:|:-----:|:--------|:----------|
| 1.0 | {TASK_NAME} | P0 | Y | {TIME} | {TIME} | {TIME} | -- | {REF} |
| 1.1 | {TASK_NAME} | P0 | Y | {TIME} | {TIME} | {TIME} | 1.0 | {REF} |

**Legend**: Y = AI-implementable, N = Human required
All estimates include **20% buffer** for reviews, test deployment, and changes.

### Task Specifications

<details>
<summary><strong>1.0 {TASK_NAME}</strong></summary>

**Priority**: P0 | **Size**: S | **AI**: Y | **Labels**: `type:infra`, `phase:1`
**Blocks**: {BLOCKS} | **Reference**: {REFERENCE}

**Summary**: {TASK_SUMMARY}

**Acceptance Criteria**:

- [ ] {CRITERION_1}
- [ ] {CRITERION_2}
- [ ] {CRITERION_3}

**Technical Notes**:

- {NOTE_1}
- {NOTE_2}

</details>

### Phase 1 Exit Criteria

| Criterion | Target | Verification Method |
|:----------|:-------|:--------------------|
| {CRITERION} | {TARGET} | {METHOD} |

---

## 5. Phase 2: {P2_NAME}

**Duration**: {DURATION}
**Epic**: #{EPIC} `[Phase 2] {P2_NAME}`
**Milestone**: `{PROJECT_PREFIX} - Phase 2: {P2_NAME}`
**Depends On**: {DEPENDENCIES}

### Sprint 2.1: {SPRINT_NAME}

| ID | Task | Priority | Labels | Blocks | Size |
|:---|:-----|:---------|:-------|:-------|:-----|
| 2.1 | {TASK_NAME} | P0 | `type:feature` | {BLOCKS} | M |

**Exit Criteria**: {EXIT_CRITERIA}

---

## 6. Summary Statistics

| Metric | Value |
|:-------|:------|
| Total Phases | {COUNT} |
| Total Sprints | {COUNT} |
| Total Tasks | {COUNT} |
| Duration | {DURATION} |
| P0 Tasks | {COUNT} |
| P1 Tasks | {COUNT} |
| Total Effort | {HOURS} |
| Buffer | 20% included |

### Tasks by Component

| Component | Tasks |
|:----------|:-----:|
| `component:{NAME}` | {COUNT} |

---

## 7. Deployment Model

This project uses **phase-gated deployment** with a 4-stage iterative QA loop. See [AI_ISSUE_LIFECYCLE.md](./AI_ISSUE_LIFECYCLE.md) and [plans/](./plans/) for full details.

### Deployment Flow

```
Development → Deployment → QA Testing → Bug Fix (max 3 iterations)
                              ↓
                         Production
```

| Stage | Issue Label | Purpose |
|:------|:------------|:--------|
| Development | `ai:development` | Feature/fix implementation |
| Deployment | `ai:deployment` | Staging deployment verification |
| QA Testing | `ai:qa-testing` | Automated test execution |
| Bug Fix | `ai:development` + `bug` + `iteration:N` | Fix failures (max 3) |

**Quality Gates**: Each phase must pass QA before production deployment.

---

## Version History

| Version | Date | Changes |
|:--------|:-----|:--------|
| 1.0 | {DATE} | Initial project plan |

---

## Placeholder Reference

| Placeholder | Description | Example |
|:------------|:------------|:--------|
| `{PROJECT_NAME}` | Full project name | AI Cost Monitoring |
| `{PROJECT_PREFIX}` | Short prefix | AIOCTO |
| `{TOTAL_DURATION}` | Project duration | 20 weeks |
| `{PHASE_N_NAME}` | Phase name | Foundation Infrastructure |
| `{DURATION}` | Phase/sprint duration | 2 weeks |
| `{SPRINTS}` | Sprint identifiers | 2.1, 2.2 |
| `{START}` / `{END}` | Start/end dates | Mar 3, 2026 |
| `{EPIC}` | Epic issue number | 12 |
| `{TASK_NAME}` | Task description | Create Terraform modules |
| `{BLOCKS}` | What this task blocks | Phase 2 |
| `{EFFORT}` | Time estimate | ~36 hours |
| `{EXIT_CRITERIA}` | Phase completion criteria | All tests passing |
