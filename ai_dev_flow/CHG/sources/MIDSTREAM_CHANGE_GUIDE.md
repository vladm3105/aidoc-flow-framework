---
title: "Midstream Change Guide"
tags:
  - change-management
  - change-source
  - midstream
  - shared-architecture
custom_fields:
  document_type: guide
  artifact_type: CHG
  change_source: midstream
  origin_layers: [5, 6, 7, 8, 9, 10, 11]
  development_status: active
---

# Midstream Change Guide

**Change Source**: Midstream (Architecture/Design-Driven)
**Origin Layers**: L5-L11 (ADR, SYS, REQ, CTR, SPEC, TSPEC, TASKS)
**Direction**: Bi-directional (may cascade down or bubble up)
**Entry Gate**: GATE-05 or GATE-09 (depending on origin layer)

---

## Gate Entry Point

| Origin Layer | Entry Gate | Cascade Path |
|--------------|------------|--------------|
| L5-L8 (ADR, SYS, REQ, CTR) | **GATE-05** | GATE-05 → GATE-09 → GATE-12 |
| L9-L11 (SPEC, TSPEC, TASKS) | **GATE-09** | GATE-09 → GATE-12 |

**Important**: If change affects L1-L4 (business/product), bubble up to GATE-01 first.

| Attribute | Value |
|-----------|-------|
| **Bubble-Up Check** | Does change affect BRD/PRD/EARS/BDD? |
| **If Yes** | Start at GATE-01 → GATE-05 → GATE-09 → GATE-12 |
| **Validation Script** | `./CHG/scripts/validate_gate05.sh` or `validate_gate09.sh` |
| **Routing Script** | `python CHG/scripts/validate_chg_routing.py` |
| **Full Workflow** | `workflows/MIDSTREAM_WORKFLOW.md` |

**Before proceeding, check routing:**
```bash
python CHG/scripts/validate_chg_routing.py <CHG_FILE> --check-bubble-up
```

---

## 1. Overview

Midstream changes originate from architecture decisions, design improvements, or technical discoveries. They can propagate both downstream (implementation) and upstream (requirements clarification).

```
┌─────────────────────────────────────────────────────────────┐
│                   MIDSTREAM CHANGE FLOW                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                 ┌─────────────────┐                         │
│      BUBBLE UP  │  CHANGE ORIGIN  │  CASCADE DOWN           │
│         ▲       │   L5-L11        │       ▼                 │
│         │       └────────┬────────┘       │                 │
│         │                │                │                 │
│  ┌──────┴──────┐         │        ┌───────┴──────┐         │
│  │  L1-L4      │         │        │  L12-L14     │         │
│  │  May need   │◄────────┴───────►│  Regenerate  │         │
│  │  clarify    │                  │  downstream  │         │
│  └─────────────┘                  └──────────────┘         │
│                                                             │
│  MIDSTREAM LAYERS:                                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ L5 ADR → L6 SYS → L7 REQ → L8 CTR → L9 SPEC →      │   │
│  │                            L10 TSPEC → L11 TASKS    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 2. Common Triggers

| Trigger | Example | Typical Level | Entry Point |
|---------|---------|---------------|-------------|
| Architecture pivot | "Switch to microservices" | L3 | ADR |
| Technology decision | "Use GraphQL over REST" | L3 | ADR |
| System req change | "Need 99.99% availability" | L2-L3 | SYS |
| Requirement refinement | "Clarify edge case" | L1-L2 | REQ |
| Contract change | "API v2 breaking change" | L2-L3 | CTR |
| Spec optimization | "Better algorithm" | L1-L2 | SPEC |
| Test strategy change | "Add performance tests" | L2 | TSPEC |
| Task restructure | "Split into phases" | L1-L2 | TASKS |

## 3. Bi-Directional Impact

### 3.1 When to Bubble Up

Midstream changes require upstream updates when:

| Condition | Action |
|-----------|--------|
| ADR contradicts BRD constraint | Update BRD or revise ADR |
| SYS cannot meet PRD feature | Clarify PRD scope |
| REQ discovers ambiguity | Clarify EARS/BDD |
| SPEC reveals impossibility | Escalate to ADR/REQ |
| TSPEC finds untestable req | Clarify REQ/BDD |

### 3.2 When to Cascade Down

Midstream changes cascade downstream when:

| Condition | Cascade To |
|-----------|------------|
| ADR changes architecture | SYS → ... → L14 |
| SYS changes quality attrs | REQ → ... → L14 |
| REQ adds/modifies reqs | CTR → ... → L14 |
| CTR changes contracts | SPEC → ... → L14 |
| SPEC changes design | TSPEC → ... → L14 |
| TSPEC changes tests | TASKS → ... → L14 |
| TASKS restructures work | Code → L14 |

## 4. Layer-Specific Guidance

### 4.1 ADR Changes (Layer 5)

**Architectural Decision Records are high-impact changes.**

| ADR Change Type | Level | Process |
|-----------------|-------|---------|
| New ADR (additive) | L2 | Create ADR, cascade to SYS+ |
| ADR modification | L2-L3 | Assess breaking impact |
| ADR supersession | L3 | Full CHG, archive old ADR |
| Technology pivot | L3 | Full CHG, cascade all |

**ADR Change Workflow**:
```
1. Assess if change is breaking
   - Breaking → L3 Major CHG
   - Non-breaking → L2 Minor CHG

2. Create/update ADR
   - Document context, decision, consequences
   - Link to upstream triggers

3. Assess upstream impact
   - Does BRD/PRD support this?
   - If not → Clarify upstream first

4. Cascade downstream
   - Update SYS quality attributes
   - Update REQ with new constraints
   - Update CTR if API affected
   - Regenerate SPEC/TSPEC/TASKS/Code
```

### 4.2 SYS Changes (Layer 6)

**System Requirements define quality attributes.**

| SYS Change Type | Level | Process |
|-----------------|-------|---------|
| New quality attribute | L2 | Add to SYS, cascade |
| Threshold change | L2 | Update SYS, update TSPEC |
| Attribute removal | L3 | CHG with deprecation |

**SYS Change Workflow**:
```
1. Update SYS document
   - Modify quality attributes
   - Update thresholds

2. Update TSPEC
   - FTEST thresholds must match
   - Add/remove test cases

3. Update REQ if atomic reqs affected

4. Cascade to SPEC/TASKS/Code
```

### 4.3 REQ Changes (Layer 7)

**Atomic Requirements are granular and testable.**

| REQ Change Type | Level | Process |
|-----------------|-------|---------|
| New requirement | L2 | Add REQ, generate downstream |
| Clarification | L1 | Update REQ, verify alignment |
| Requirement split | L2 | Create child REQs |
| Deprecation | L2-L3 | CHG, update traceability |

**REQ Change Workflow**:
```
1. Identify if change is clarification vs. modification
   - Clarification → L1, update in place
   - Modification → L2, may need upstream check

2. Update REQ document
   - Increment version
   - Update traceability tags

3. Check TSPEC alignment
   - UTEST covers REQ?
   - Update test specs if needed

4. Cascade to CTR/SPEC/TASKS/Code
```

### 4.4 CTR Changes (Layer 8)

**API Contracts define interfaces.**

| CTR Change Type | Level | Process |
|-----------------|-------|---------|
| New endpoint (additive) | L2 | Add to CTR, extend |
| Breaking change | L3 | API versioning, full CHG |
| Schema modification | L2 | Update .md + .yaml |
| Deprecation | L3 | Deprecation notice, timeline |

**CTR Change Workflow**:
```
1. Assess breaking vs. non-breaking
   - Adding optional field → Non-breaking (L2)
   - Removing field → Breaking (L3)
   - Changing type → Breaking (L3)

2. Update CTR (both .md and .yaml)
   - Dual-file format must stay in sync

3. Update SPEC to implement changes

4. Update TSPEC
   - ITEST must cover contract changes

5. Regenerate TASKS and Code
```

### 4.5 SPEC Changes (Layer 9)

**Technical Specifications define HOW to build.**

| SPEC Change Type | Level | Process |
|-----------------|-------|---------|
| Algorithm improvement | L1-L2 | Update SPEC, regenerate |
| Design optimization | L2 | Update SPEC/TSPEC/TASKS |
| Interface change | L2-L3 | May affect CTR upstream |

**SPEC Change Workflow**:
```
1. Update SPEC YAML
   - Modify classes, methods, algorithms

2. Check upstream contracts
   - Does CTR still align?
   - If not → Update CTR first

3. Update TSPEC
   - UTEST for new/changed methods
   - ITEST for integration points

4. Regenerate TASKS

5. Implement Code
```

### 4.6 TSPEC Changes (Layer 10)

**Test Specifications drive TDD workflow.**

| TSPEC Change Type | Level | Process |
|------------------|-------|---------|
| Add test cases | L1-L2 | Update TSPEC, run tests |
| Test strategy change | L2 | Update TSPEC structure |
| Coverage improvement | L1 | Add missing tests |
| Test deprecation | L2 | Remove obsolete tests |

**TSPEC Change Workflow**:
```
1. Identify test type (UTEST/ITEST/STEST/FTEST)

2. Update appropriate TSPEC document
   - Add/modify test cases
   - Update I/O tables
   - Update pseudocode

3. Verify upstream alignment
   - Does test match REQ/SPEC?

4. Update TASKS if workflow changes

5. Implement/update Tests (L13)
```

### 4.7 TASKS Changes (Layer 11)

**Task Breakdowns structure implementation work.**

| TASKS Change Type | Level | Process |
|------------------|-------|---------|
| Task refinement | L1 | Update TASKS |
| Task restructure | L2 | May affect timeline |
| Phase reorganization | L2 | Update execution plan |

**TASKS Change Workflow**:
```
1. Update TASKS document
   - Modify TODOs
   - Update execution commands

2. Verify SPEC alignment
   - All SPEC elements covered?

3. Verify TSPEC alignment
   - Test tasks included?

4. Implement Code changes
```

## 5. Architecture Pivot Process

For major architecture changes (L3):

```
┌─────────────────────────────────────────────────────────────┐
│               ARCHITECTURE PIVOT PROCESS                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. CREATE CHG                                              │
│     └── CHG-XX_architecture_pivot/                         │
│         ├── CHG-XX_architecture_pivot.md                   │
│         ├── implementation_plan.md                         │
│         └── archive/                                        │
│                                                             │
│  2. ASSESS UPSTREAM IMPACT                                  │
│     └── Does BRD/PRD support new architecture?             │
│         ├── Yes → Proceed                                  │
│         └── No → Clarify/update upstream first             │
│                                                             │
│  3. ARCHIVE OLD ADR                                         │
│     └── Move ADR-XX to archive/                            │
│         └── Add deprecation notice                         │
│                                                             │
│  4. CREATE NEW ADR                                          │
│     └── ADR-YY with new architecture                       │
│         └── "Supersedes: ADR-XX"                           │
│                                                             │
│  5. CASCADE DOWNSTREAM                                      │
│     └── SYS → REQ → CTR → SPEC → TSPEC → TASKS            │
│         └── Archive old, create new for each               │
│                                                             │
│  6. IMPLEMENT & VALIDATE                                    │
│     └── Regenerate Code, run all tests                     │
│                                                             │
│  7. CLOSE CHG                                               │
│     └── Status: Completed                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 6. Examples

### 6.1 Example: Algorithm Optimization

**Trigger**: "Found 10x faster sorting algorithm"

```
Change Level: L2 Minor
Entry Point: SPEC-05

Actions:
1. Create CHG-03_algorithm_optimization/
2. Update SPEC-05 with new algorithm
3. Update TSPEC UTEST for new method
4. Update TASKS with implementation changes
5. Implement in Code
6. Run tests (should be faster)
7. Close CHG
```

### 6.2 Example: Database Technology Change

**Trigger**: "Switch from PostgreSQL to MongoDB"

```
Change Level: L3 Major
Entry Point: ADR

Actions:
1. Create CHG-04_mongodb_migration/
2. Check BRD constraints (data consistency?)
3. Archive ADR-05_postgresql.md
4. Create ADR-15_mongodb.md
5. Update SYS data layer requirements
6. Update REQ persistence requirements
7. Update CTR data models
8. Regenerate SPEC
9. Update TSPEC (ITEST for new DB)
10. Regenerate TASKS
11. Implement migration
12. Validate all tests pass
13. Close CHG
```

---

**Related Documents**:
- [CHANGE_MANAGEMENT_GUIDE.md](../CHANGE_MANAGEMENT_GUIDE.md)
- [UPSTREAM_CHANGE_GUIDE.md](./UPSTREAM_CHANGE_GUIDE.md)
- [DOWNSTREAM_CHANGE_GUIDE.md](./DOWNSTREAM_CHANGE_GUIDE.md)
