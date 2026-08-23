# ID Naming Standards — SDD

## Document IDs

Format: `{TYPE}-{NN}` where TYPE is the artifact prefix and NN is a sequential number of **two or more digits** (two-digit is the common case; the authoritative pattern is `registry/LAYER_REGISTRY.yaml` `id_patterns.document` = `^[A-Z]+-\d{2,}$`, which the registry README declares wins on any discrepancy).

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

### Hash algorithm (the canonicalization target)

The SHA-256 form below is the **canonicalization target** — the by-hand↔tool parity
anchor (PROVISIONAL-IDS-001) that *any* generator (an engine's ID generator or a
hand author) should converge on:

1. **Input string** (exact, colon-separated, from the element's OWN content — not
   upstream): `"{doc_id}:{section_id}:{title}:{description}"`, where `title` and
   `description` are each passed through the **normalization transform** below.
2. **Compute**: `hashlib.sha256(input.encode("utf-8")).hexdigest()[:4]`.
3. **Collision**: if two distinct elements in scope yield the same 4-char prefix,
   extend BOTH to 8 chars (`[:8]`).

The hash segment is `[a-f0-9]+` (lowercase hex; `ELEM_FORM`). A hand-authored hash
applies this algorithm by hand; it *should* be byte-identical to an engine's
generated hash.

#### Normalization transform (normative — PROVISIONAL-IDS-002)

`title` and `description` are each normalized by this **exact, ordered** transform
before assembly into the input string. This is the load-bearing contract: the
verifier (`rehash --check`) and any future generator or `--fix` MUST apply it
identically, or two tools compute different hashes for the same content.

1. **NFC** — Unicode normalization form C.
2. **casefold** — Unicode case-folding (lowercase).
3. **strip** — delete every character not in `[a-z0-9 ]` (space kept).
4. **collapse** — replace every run of whitespace with a single space.
5. **trim** — strip leading/trailing spaces.
6. **truncate** — take the first 100 characters.

**Limitation (intentional for Phase 1):** step 3 deletes all non-Latin scripts
(CJK → empty) and accents NFC leaves composed (`café` → `caf`), so two distinct
non-ASCII fields can normalize to the same string and collide on the 4-hex prefix —
the collision rule (`[:8]`) covers that. A Unicode-category-based strip is a
PROVISIONAL-IDS-002 Phase-2 option.

#### Field extraction (normative — BRD §7 Functional-Requirement bullets)

For a BRD §7 FR bullet
`- **<ID> — <Title>** (band): <description…>`, `title` and `description` are
extracted **byte-exactly** so the recompute is reproducible:

- **title** — the text between the `— ` (em/en/hyphen) separator and the closing
  `**` of the bold ID+title span.
- **description** — the text after the closing `**`, skipping the leading
  `(band)` parenthetical up to its `):` separator (so a band that itself contains
  a nested `(...)` is stripped whole, not to its first `)`), then **accumulating
  continuation lines** (the wrapped body) — joining with single spaces — until the
  first of: a blank line, the next `- ` bullet, a `## ` heading, or the
  `Acceptance criteria:` label. (The band parenthetical MAY itself wrap across
  lines — corpus `882c` — so extraction joins the logical bullet first, then
  splits band from description.)

**Phase-1 coverage boundary:** `rehash --check` covers **only BRD §7 gated FR
elements** (`scan_fr_content`). Other element-bearing BRD sections (e.g. §4
constraint IDs) and the other seven layers are **NOT** verified in Phase 1; their
`canonical` IDs remain unverified until later PROVISIONAL-IDS-002 phases extend the
extractor.

> **Scope of the guarantee (verifiable on demand via the opt-in `rehash --check`).**
> This algorithm is the target form. As of PROVISIONAL-IDS-002 Phase 1 the
> normalization + extraction contract is formalized (above) and `rehash --check`
> **can verify** a `canonical` BRD's §7 FR IDs against it **on demand** — but the
> check is an **explicit opt-in command, NOT run by the default `sdd_doc_lint`
> pass**, and it is **not run over the example corpus** (whose IDs are LLM-generated
> stable strings, not real hashes — they remain unverified until the Phase-2 corpus
> reconciliation). So a `canonical` ID is a **stable opaque string that SHOULD match
> the algorithm and is now verifiable for BRD §7 via `rehash --check`** — it is
> **not** globally "verified": a mismatch (a "canonical leak") is reported as the
> advisory `IDDRIFT01` when the command is run, and is still **not shape-detectable**
> by the default lint (only non-hex `xxxx` is flagged, via `PH01`).

### Provisional vs canonical IDs

Hand-authored hashes are **placeholders until canonicalized**. A document declares
its state once, in frontmatter:

- `id_state: canonical` (default when omitted) — the IDs are **intended as** content
  hashes (the canonicalization target). For a BRD's §7 FR elements this is now
  **verifiable on demand** via `rehash --check` (emits `IDDRIFT01` on a mismatch);
  elsewhere it remains unverified until later PROVISIONAL-IDS-002 phases, per the
  scope note above. `rehash --check` runs **only on `id_state: canonical` docs** — a
  `provisional` doc is exempt (its IDs are declared placeholders, not hashes).
- `id_state: provisional` — the IDs are placeholders; canonicalize (recompute the
  hashes per the algorithm above) before downstream layers cite them. The linter
  emits one doc-level `PROV01` advisory.

**Provisional ID form:** use **section-ordinal hex** — `BRD.01.07.0001`,
`.0002`, … (distinct per element within a section). This is `ELEM_FORM`-valid
(so the doc lints cleanly) and FR-scanner-visible, while clearly not yet a
content hash. Do NOT use `xxxx` (non-hex — it fails `ELEM_FORM` and surfaces a
confusing `ID03`). Element-ID uniqueness (`HASH01`) applies regardless of
`id_state`, so distinct ordinals are required. `id_state` governs ID *stability*
only — provisional elements are still subject to coverage and traceability gates.

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
| `@spec: SPEC-NN` | SPEC references (document-level) | `@spec: SPEC-01` |
| `@tdd: TDD.NN.SS.xxxx` | TDD references (test case level) | `@tdd: TDD.01.04.a3c1` |
| `@iplan: IPLAN-NN` | IPLAN references (document-level) | `@iplan: IPLAN-01` |
| `@threshold: TYPE.NN.key` | Performance thresholds | `@threshold: BRD.01.perf.p95_latency` |
| `@depends: TYPE-NN` | Hard prerequisite | `@depends: BRD-01` |
| `@discoverability: TYPE-NN` | Related document | `@discoverability: BRD-02` |
| `@chg: CHG-NN` | Change back-reference (provenance) | `@chg: CHG-01` |

> **Templated `xxxx` is a template-only placeholder.** The `TYPE.NN.SS.xxxx`
> form above is *pattern notation* — the shape of a future ID — and is valid
> only in the layer templates and illustrative README snippets. A **produced**
> document artifact MUST carry a real element ID (4–8 lowercase hex, e.g.
> `BDD.01.03.d7a2`); the templated placeholder must never survive into one.
> `ID03` (malformed element id) and `ID01` (malformed trace-tag id) reject the
> templated form in any authored document — in an `id:` declaration, an `@`-tag
> citation, or free prose. Regression-locked by
> `tests/acceptance/fixtures/negative/brd-templated-ids.md`.

### Reference granularity (GD-03)

Functionality is defined in **elements** (each functional requirement, EARS
statement, BDD scenario, ADR decision, TDD case is a discrete unit); the document
is a container. A trace citation must therefore name the **element**, not the
document — a document-level ref discards the granularity at which the work is
actually specified.

**Derivable Principle:**
- **Oracle layers (EARS requirement or BDD scenario):** citing an oracle layer in a verification or design realization context **MUST be element-level** (`TYPE.NN.SS.xxxx`). Citing a document-level ID (e.g. `BDD-01` instead of `BDD.01.03.xxxx`) in a verification context discards fine-grained traceability and silently zeroes element-level coverage.
- **Design & realization layers (SPEC / IPLAN):** citing an upstream design doc as an architectural unit or provenance (e.g. TDD citing `SPEC-01`, IPLAN citing `SPEC-01`) is **document-level permitted**, because SPEC and IPLAN are the two element-ID-exempt layers — they are not required to declare canonical elements, so a citation cannot rely on one existing. Citing an **element-declaring** layer — a concrete test case in TDD, a decision in ADR — remains element-level (`TYPE.NN.SS.xxxx`); a genuine whole-document dependency on one of those is recorded in prose, never as a document-level trace tag.

- An `@<layer>:` **trace citation** to an **element-declaring oracle/behavior layer** (`@brd`,
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

### Status field scopes and legal values

The `status:` field appears across different scopes with distinct legal-value enumerations:

- **Document Lifecycle (Layers 1-4, 6-7):** `Draft` | `In Review` | `Approved`
- **ADR Lifecycle (Layer 5):** `Proposed` | `Accepted` | `Deprecated` | `Superseded`
- **IPLAN Lifecycle (Layer 8):** `Draft` | `In Progress` | `Completed`
- **Option / Item Status:** `Selected` | `Pending` | `Rejected`

## File Naming

| File | Format | Example |
|------|--------|---------|
| Template | `{TYPE}-TEMPLATE.yaml` | `BRD-TEMPLATE.yaml` |
| Index | `{TYPE}-00_index.md` (Layers 1-7) / `{TYPE}-00_index.yaml` (IPLAN) | `BRD-00_index.md` / `IPLAN-00_index.yaml` |
| Index template | `{TYPE}-00_index.TEMPLATE.{md,yaml}` | `BRD-00_index.TEMPLATE.md` / `IPLAN-00_index.TEMPLATE.yaml` |
| Document | `{TYPE}-NN.yaml` (BRD, IPLAN: `{TYPE}-NN_{slug}.yaml`) | `BRD-01_kyc_onboarding.yaml` |
| README | `README.md` | — |
