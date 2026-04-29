# ID Naming Standards — SDD v3.2

## Document IDs

Format: `{TYPE}-{NN}` where TYPE is the artifact prefix and NN is a sequential two-digit number.

| Artifact | Prefix | Example |
|----------|--------|---------|
| BRD | BRD | BRD-01 |
| PRD | PRD | PRD-01 |
| EARS | EARS | EARS-01 |
| BDD | BDD | BDD-01 |
| ADR | ADR | ADR-01 |
| SPEC | SPEC | SPEC-01 |
| TDD | TDD | TDD-01 |
| IPLAN | IPLAN | IPLAN-01 |

## Element IDs

Format: `{TYPE}.{doc_id}.{section_id}.{hash}`

- `TYPE` — Upper case artifact prefix (e.g., BRD, SPEC)
- `doc_id` — Two-digit document number (e.g., 01)
- `section_id` — Two-digit section number (e.g., 03)
- `hash` — 4-character hex content hash (SHA256, first 4 chars)

Example: `BRD.01.07.a7f3`

## Tag Format

| Tag | Usage | Example |
|-----|-------|---------|
| `@brd: BRD.NN.SS.xxxx` | BRD references | `@brd: BRD.01.07.a7f3` |
| `@prd: PRD.NN.SS.xxxx` | PRD references | `@prd: PRD.01.09.1dbc` |
| `@ears: EARS.NN.SS.xxxx` | EARS references | `@ears: EARS.01.03.5e2a` |
| `@bdd: BDD.NN.SS.xxxx` | BDD references | `@bdd: BDD.01.03.8f4c` |
| `@adr: ADR.NN.SS.xxxx` | ADR references | `@adr: ADR.01.03.e5b1` |
| `@spec: SPEC.NN` | SPEC references (document-level) | `@spec: SPEC-01` |
| `@tdd: TDD.NN.SS.xxxx` | TDD references (test case level) | `@tdd: TDD.01.04.a3c1` |
| `@iplan: IPLAN-NN` | IPLAN references (document-level) | `@iplan: IPLAN-01` |
| `@threshold: TYPE.NN.key` | Performance thresholds | `@threshold: BRD.01.perf.p95_latency` |
| `@depends: TYPE-NN` | Hard prerequisite | `@depends: BRD-01` |
| `@discoverability: TYPE-NN` | Related document | `@discoverability: BRD-02` |

## File Naming

| File | Format | Example |
|------|--------|---------|
| Template | `{TYPE}-TEMPLATE.yaml` | `BRD-TEMPLATE.yaml` |
| Index | `{TYPE}-00_index.md` | `BRD-00_index.md` |
| Document | `{TYPE}-NN.yaml` | `BRD-01.yaml` |
| README | `README.md` | — |
| IPLAN Index | `{TYPE}-00_index.yaml` | `IPLAN-00_index.yaml` |
