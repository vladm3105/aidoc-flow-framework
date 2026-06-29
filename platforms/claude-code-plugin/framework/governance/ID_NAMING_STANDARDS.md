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

### Cross-layer cardinality (CLEANUP-PR-F item 18)

**Document numbers are per-layer sequential and INDEPENDENT across
layers.** `BRD-01` and `PRD-01` are *not* causally related — `PRD-01`
is simply the first PRD authored, just as `BRD-01` is the first BRD.
A PRD authored after `BRD-01` does **not** inherit `01` from its
upstream; it picks the next-free number in the PRD layer.

The framework supports both **one-to-many** and **many-to-one**
cross-layer relationships:

- **One-to-many** — one BRD MAY drive multiple downstream PRDs. A
  single `BRD-01` covering a complex business need may decompose
  into `PRD-01`, `PRD-02`, `PRD-03` — each PRD declares
  `@brd: BRD-01` as its upstream citation. All three PRDs are
  legitimate siblings of `BRD-01`, not duplicates or orphans.
- **Many-to-one** — one PRD MAY cite multiple upstream BRDs via
  multiple `@brd:` citations. A `PRD-01` synthesizing requirements
  from `BRD-01` *and* `BRD-02` simply lists both upstream tags.

The cascade harness's standard example (`examples/url-shortener/`)
happens to use 1:1 numbering across all 8 layers (BRD-01 → PRD-01 →
... → IPLAN-01). **That alignment is coincidence, not contract.** A
reader inferring "doc numbers cascade across layers" from the
example is reading a pattern that isn't there.

**For authors:** when reserving an ID at any layer, pick the
next-free number in *your* layer's index. The upstream's number is
irrelevant to your choice.

**For auditors:** apparent-orphan downstream docs (e.g., `PRD-02`
declaring `@brd: BRD-01` when `PRD-01` already exists with the same
upstream) MAY be valid siblings, not actual orphans. Validate the
trace by tag resolution, not by number alignment.

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
  and `@adr: ADR.NN.SS.xxxx` citations plus the Protocol method names declared
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

### Reference granularity (GD-03)

Functionality is defined in **elements** (each functional requirement, EARS
statement, BDD scenario, ADR decision, TDD case is a discrete unit); the document
is a container. A trace citation must therefore name the **element**, not the
document — a document-level ref discards the granularity at which the work is
actually specified.

- An `@<layer>:` **trace citation** to an **element-declaring** layer (`@brd`,
  `@prd`, `@ears`, `@bdd`, `@adr`, `@tdd`) **MUST be element-level**
  (`TYPE.NN.SS.xxxx`). This holds for **every** trace context — inline body
  citations **and** the **necessary-upstream / feature-level** tag (e.g. an
  IPLAN's `Source TDD` tag). A unit that realizes **multiple** upstream elements
  pipe-delimits them (`@ears: EARS.01.03.aaaa | @ears: EARS.01.03.bbbb`) — the
  union of the elements its sub-units (scenarios / cases) realize. A genuine
  whole-document dependency is recorded in **prose**, never as a document-level
  trace tag.
- **BDD carrier (YAML-BDD-SCHEMA, D-0038):** a BDD doc carries its `@ears`
  upstream trace as a structured `ears:` list on each scenario (YAML), not
  `@ears` tags. Each entry is element-level — enforced by `REFGRAN01` (via the
  linter's synthetic edges) + `BDD-SCHEMA-001` — and the Feature carries no
  aggregate tag: its coverage is the computed union of its scenarios' `ears`.
  Downstream layers still cite BDD scenarios via element-level
  `@bdd: BDD.NN.SS.xxxx` tags.
- `@spec:` and `@iplan:` citations are **document-level** — those layers are
  element-ID-exempt (they are not required to declare canonical elements; see the
  SPEC §5 / IPLAN §4 exemption above).
- **Self-tags** (a document citing its own id, e.g. `@bdd: BDD-01` on `BDD-01`)
  and **downstream forward-pointers** (a higher layer naming a lower one for
  navigation) are document-level and are **not** trace citations — they are
  exempt from this rule.

Enforced by `sdd_doc_lint REFGRAN01` (CFB-PR-3).

## File Naming

| File | Format | Example |
|------|--------|---------|
| Template | `{TYPE}-TEMPLATE.yaml` | `BRD-TEMPLATE.yaml` |
| Index | `{TYPE}-00_index.md` (Layers 1-7) / `{TYPE}-00_index.yaml` (IPLAN) | `BRD-00_index.md` / `IPLAN-00_index.yaml` |
| Index template | `{TYPE}-00_index.TEMPLATE.{md,yaml}` | `BRD-00_index.TEMPLATE.md` / `IPLAN-00_index.TEMPLATE.yaml` |
| Document | `{TYPE}-NN.yaml` (BRD: `{TYPE}-NN_{slug}.yaml`) | `BRD-01_kyc_onboarding.yaml` |
| README | `README.md` | — |
| IPLAN Index | `{TYPE}-00_index.yaml` | `IPLAN-00_index.yaml` |
