# doc-naming Quick Reference

## Document ID Format

```
TYPE-NN                    Example: BRD-02, PRD-01, ADR-001
```

## Element ID Format

```
TYPE.NN.TT.SS              Example: BRD.02.06.01
│    │   │  │
│    │   │  └── Sequential number (01, 02, ...)
│    │   └───── Element type code (01-31)
│    └───────── Document number (02, 03, ...)
└────────────── Document type (BRD, PRD, ADR, ...)
```

**Regex**: `^[A-Z]{2,5}\.[0-9]{2,}\.[0-9]{2,}\.[0-9]{2,}$`

---

## Element Type Codes

| Code | Type | Documents |
|------|------|-----------|
| 01 | Functional Requirement | BRD, PRD, SYS, REQ |
| 02 | Quality Attribute | BRD, PRD, SYS |
| 03 | Constraint | BRD, PRD |
| 04 | Assumption | BRD, PRD |
| 05 | Dependency | BRD, PRD, REQ |
| 06 | Acceptance Criteria | BRD, PRD, REQ |
| 07 | Risk | BRD, PRD |
| 08 | Metric | BRD, PRD |
| 09 | User Story | PRD |
| 10 | Decision | ADR |
| 11 | Use Case | PRD, SYS |
| 12 | Alternative | ADR |
| 13 | Consequence | ADR |
| 14 | Test Scenario | BDD |
| 15 | Step | BDD, SPEC |
| 16 | Interface | SPEC, CTR |
| 17 | Data Model | SPEC, CTR |
| 18 | Task | TASKS |
| 19 | Command | IPLAN |
| 20 | Contract Clause | CTR |
| 21 | Validation Rule | SPEC |
| 22 | Feature Item | BRD, PRD |
| 23 | Business Objective | BRD |
| 24 | Stakeholder Need | BRD, PRD |
| 25 | EARS Statement | EARS |
| 26 | System Requirement | SYS |
| 27 | Atomic Requirement | REQ |
| 28 | Specification Element | SPEC |
| 29 | Implementation Phase | IMPL |
| 30 | Task Item | TASKS |
| 31 | Plan Step | IPLAN |

---

## Removed Patterns - DO NOT USE

| Legacy | Use Instead |
|--------|-------------|
| `AC-XXX` | `TYPE.NN.06.SS` |
| `FR-XXX` | `TYPE.NN.01.SS` |
| `BC-XXX` | `TYPE.NN.03.SS` |
| `BA-XXX` | `TYPE.NN.04.SS` |
| `QA-XXX` | `TYPE.NN.02.SS` |
| `BO-XXX` | `TYPE.NN.23.SS` |
| `RISK-XXX` | `TYPE.NN.07.SS` |
| `METRIC-XXX` | `TYPE.NN.08.SS` |
| `Feature F-XXX` | `TYPE.NN.22.SS` |
| `Event-XXX` | `TYPE.NN.25.SS` |
| `State-XXX` | `TYPE.NN.25.SS` |
| `TASK-XXX` | `TYPE.NN.18.SS` |
| `T-XXX` | `TYPE.NN.18.SS` |
| `Phase-XXX` | `TYPE.NN.29.SS` |
| `IP-XXX` | `TYPE.NN.29.SS` |
| `IF-XXX` | `TYPE.NN.16.SS` |
| `DM-XXX` | `TYPE.NN.17.SS` |
| `CC-XXX` | `TYPE.NN.20.SS` |

---

## Threshold Tag Format

```
@threshold: TYPE.NN.category.subcategory.attribute
```

**Categories**: perf, timeout, rate, retry, circuit, alert, cache, pool, queue, batch

**Example**: `@threshold: PRD.035.timeout.partner.bridge`

---

## Quick Lookup by Document

| Doc | Common Codes |
|-----|--------------|
| BRD | 01, 02, 03, 04, 05, 06, 07, 08, 22, 23, 24 |
| PRD | 01, 02, 03, 04, 05, 06, 07, 08, 09, 11, 22, 24 |
| EARS | 25 |
| BDD | 14, 15 |
| ADR | 10, 12, 13 |
| SYS | 01, 02, 11, 26 |
| REQ | 01, 05, 06, 27 |
| IMPL | 29 |
| CTR | 16, 17, 20 |
| SPEC | 15, 16, 17, 21, 28 |
| TASKS | 18, 30 |
| IPLAN | 19, 31 |

---

**Full Reference**: `.claude/skills/doc-naming/SKILL.md`
