# ID Naming Standards — SDD

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

### Element-ID exemptions (CLEANUP-PR-C item 13)

Six of the eight layers (BRD, PRD, EARS, BDD, ADR, TDD) **MUST** carry
element IDs on every distinct content unit per their template's required
sections. The remaining two layers carry a documented exemption:

- **SPEC layer:** §5 fail-closed rules, §3 Protocol method specifications,
  and similar policy statements **MAY** carry `SPEC.NN.SS.xxxx` element
  IDs but are not required to. The traceability surface for SPEC content
  is provided by upstream `@ears: EARS.NN.SS.xxxx`, `@bdd: BDD.NN.SS.xxxx`,
  and `@adr: ADR-NN` citations plus the Protocol method names declared
  in the SPEC's typed contract.
- **IPLAN layer:** §4 implementation contracts, §2 file manifest entries,
  and step-level operations **MAY** carry `IPLAN.NN.SS.xxxx` element IDs
  but are not required to. The traceability surface is provided by
  upstream `@spec: SPEC-NN` and `@tdd: TDD.NN.SS.xxxx` citations plus the
  per-step file-path declarations in the manifest table.

**Rationale.** SPEC and IPLAN content is overwhelmingly already-bound to
upstream content via mandatory `@<layer>:` citations. Adding layer-local
element IDs would create a second naming surface for what is, in
practice, a derived/translated view of upstream content. The other six
layers introduce content not present upstream (business rules, scenarios,
decisions, etc.), making layer-local IDs load-bearing for downstream
traceability.

**For authors:** when authoring SPEC or IPLAN content, prefer
upstream-citation-based traceability. Only assign a layer-local element
ID when a SPEC rule or IPLAN step has no clean upstream binding — then
the ID gives downstream consumers a stable anchor.

**For auditors:** do not penalize SPEC §5 / IPLAN §4 content for missing
layer-local element IDs as long as upstream citations resolve cleanly.
The `@<layer>:` chain plus method/file names is sufficient evidence of
traceability.

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
| Index | `{TYPE}-00_index.md` (Layers 1-7) / `{TYPE}-00_index.yaml` (IPLAN) | `BRD-00_index.md` / `IPLAN-00_index.yaml` |
| Index template | `{TYPE}-00_index.TEMPLATE.{md,yaml}` | `BRD-00_index.TEMPLATE.md` / `IPLAN-00_index.TEMPLATE.yaml` |
| Document | `{TYPE}-NN.yaml` (BRD: `{TYPE}-NN_{slug}.yaml`) | `BRD-01_kyc_onboarding.yaml` |
| README | `README.md` | — |
| IPLAN Index | `{TYPE}-00_index.yaml` | `IPLAN-00_index.yaml` |
