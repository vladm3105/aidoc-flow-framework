# doc-naming Quick Reference

## Document ID Format

```
TYPE-NN                    Example: BRD-02, PRD-01, ADR-001
```

TYPE ∈ {BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN}

## Element ID Format (4-segment)

```
TYPE.NN.SS.xxxx          Example: BRD.01.07.a7f3
│    │  │   │
│    │  │   └───── Content hash (4-8 hex chars, SHA256 first 4)
│    │  └───────── Section number (07, 03, ...)
│    └──────────── Document number (01, 02, ...)
└───────────────── Document type (BRD, PRD, EARS, BDD, ADR, TDD)
```

**Regex**: `^[A-Z]+\.[0-9]{2,}\.[0-9]{2,}\.[a-f0-9]{4,8}$`

There are NO numeric element-type codes in the 8-layer model. Element identity
is `TYPE.NN.SS.xxxx` (section + hash), not a fixed type code.

---

## Reference Granularity (Element vs Document)

| Layer | # | Reference form | Example |
|-------|---|----------------|---------|
| BRD   | 1 | element (dotted) | `BRD.01.07.a7f3` |
| PRD   | 2 | element (dotted) | `PRD.01.09.1dbc` |
| EARS  | 3 | element (dotted) | `EARS.01.03.5e2a` |
| BDD   | 4 | element (dotted) | `BDD.01.03.8f4c` |
| ADR   | 5 | element (dotted) + doc `ADR-NN` | `ADR.01.03.e5b1` |
| SPEC  | 6 | document (dash) | `SPEC-01` |
| TDD   | 7 | element (dotted) | `TDD.01.04.a3c1` |
| IPLAN | 8 | document (dash) | `IPLAN-01` |

Dash refs (`SPEC-NN`, `ADR-NN`, `IPLAN-NN`) point at a whole document; dotted
refs (`TYPE.NN.SS.xxxx`) point at an element within one. Test categories
(unit/integration/smoke/functional) live as TDD test-case content, not ID codes.

---

## Removed Patterns - DO NOT USE

| Legacy | Use Instead |
|--------|-------------|
| `AC-XXX` | `TYPE.NN.SS.xxxx` |
| `FR-XXX` | `TYPE.NN.SS.xxxx` |
| `BC-XXX` | `TYPE.NN.SS.xxxx` |
| `BA-XXX` | `TYPE.NN.SS.xxxx` |
| `QA-XXX` | `TYPE.NN.SS.xxxx` |
| `BO-XXX` | `TYPE.NN.SS.xxxx` |
| `RISK-XXX` | `TYPE.NN.SS.xxxx` |
| `METRIC-XXX` | `TYPE.NN.SS.xxxx` |
| `Feature F-XXX` | `TYPE.NN.SS.xxxx` |
| `Event-XXX` | `TYPE.NN.SS.xxxx` |
| `State-XXX` | `TYPE.NN.SS.xxxx` |
| `DEC-XXX` | `ADR.NN.SS.xxxx` |
| `ALT-XXX` | `ADR.NN.SS.xxxx` |
| `CON-XXX` | `ADR.NN.SS.xxxx` |
| `TYPE.NN.xxxx` (3-segment) | `TYPE.NN.SS.xxxx` (4-segment) |

---

## Threshold Tag Format

```
@threshold: TYPE.NN.category.subcategory.attribute
```

**Categories**: perf, timeout, rate, retry, circuit, alert, cache, pool, queue, batch

**Example**: `@threshold: PRD.035.timeout.partner.bridge`

---

## Traceability Tags

| Tag | Example |
|-----|---------|
| `@brd:` | `@brd: BRD.01.07.a7f3` |
| `@prd:` | `@prd: PRD.01.09.1dbc` |
| `@ears:` | `@ears: EARS.01.03.5e2a` |
| `@bdd:` | `@bdd: BDD.01.03.8f4c` |
| `@adr:` | `@adr: ADR.01.03.e5b1` |
| `@spec:` | `@spec: SPEC-01` |
| `@tdd:` | `@tdd: TDD.01.04.a3c1` |
| `@iplan:` | `@iplan: IPLAN-01` |

---

**Full Reference**: `../doc-naming/SKILL.md`
