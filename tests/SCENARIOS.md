# Test Scenarios Catalog

> Source of truth for what the suite covers. Add a row when you add a test;
> remove a row when you remove one. Cross-check against the plan's acceptance
> criteria (`plans/PLUGIN-TEST-SUITE-PLAN.md` §14).

## Conventions

- **ID:** `<tier>.<group>.<n>` (e.g. `T3.brd.01` for tier-3 BRD scenario 1).
- **Layer:** 1–8 if layer-scoped; "—" if cross-cutting.
- **Plan task:** the implementation task that built it.

## Tier 1 — Static

| ID | Layer | Proof | Plan task |
|----|:-:|---|----|
| T1.01 | — | YAML templates parse and have required top keys | 1.1 |
| T1.02 | — | `claude plugin validate --strict` passes | 1.2 |
| T1.03 | — | STRUCT01 fires on missing required section | 1.3 |
| T1.04 | — | sdd_doc_lint `--format=json` produces structured findings | 1.3 |

## Tier 2 — Unit

| ID | Layer | Proof | Plan task |
|----|:-:|---|----|
| T2.01 | — | Every SKILL.md has required frontmatter | 2.1 |
| T2.02 | — | framework_spec_version matches framework/VERSION | 2.1 |
| T2.03 | — | Each lint code fires only on its target fixture | 2.2 |
| T2.04 | — | Sync scripts are idempotent | 2.3 |
| T2.05 | — | Non-layer skills carry valid contracts | 6.5.3 |
| T2.06 | — | _spec.py helpers resolve | 0.2 |
| T2.07 | — | No orphan governance files | 0.3 |

## Tier 3 — Per-layer acceptance (deterministic)

| ID | Layer | Proof | Plan task |
|----|:-:|---|----|
| T3.brd.01-04 | 1 | BRD golden passes lint + sections + broken codes + no upstream tags | 3.2 |
| T3.prd.01-05 | 2 | PRD: standard 4 + customer-facing has ≥3 substantive categories | 3.3 |
| T3.ears.01-05 | 3 | EARS: standard 4 + WHEN-THE-SHALL-WITHIN form | 3.4 |
| T3.bdd.01-04 | 4 | BDD: standard 3 + Given/When/Then per scenario | 3.5 |
| T3.adr.01-05 | 5 | ADR: standard 4 + Status enum valid | 3.6 |
| T3.spec.01-04 | 6 | SPEC: standard 3 + YAML parses, metadata.layer == 6 | 3.7 |
| T3.tdd.01-04 | 7 | TDD: standard 3 + every case has valid type | 3.8 |
| T3.iplan.01-05 | 8 | IPLAN: standard 3 + manifest tests-first + first session directive | 3.9 |

## Tier 3 — Per-layer acceptance (live)

| ID | Layer | Proof | Plan task |
|----|:-:|---|----|
| T3L.brd.01 | 1 | doc-brd produces template-conformant BRD from seed | 4.2 |
| T3L.prd.01 | 2 | doc-prd produces conformant PRD from staged BRD | 4.3 |
| T3L.ears.01 | 3 | doc-ears emits WHEN-THE-SHALL-WITHIN requirements | 4.4 |
| T3L.bdd.01 | 4 | doc-bdd emits Given-When-Then scenarios | 4.5 |
| T3L.adr.01 | 5 | doc-adr emits decision with Status | 4.6 |
| T3L.spec.01 | 6 | doc-spec emits YAML C4-L3 component spec | 4.7 |
| T3L.tdd.01 | 7 | doc-tdd emits test cases mapped to BDD | 4.8 |
| T3L.iplan.01 | 8 | doc-iplan emits manifest with tests-first ordering | 4.9 |

## Tier 4 — Full-path acceptance

| ID | Layer | Proof | Plan task |
|----|:-:|---|----|
| T4.01 | 1-8 | Golden chain lint passes | 5.1 |
| T4.02 | 1-8 | Every layer has one artifact | 5.1 |
| T4.03 | 1-8 | Every layer has required sections | 5.1 |
| T4.04 | 1-8 | Forward-tag closure | 5.1 |
| T4.05 | 1-8 | Broken-chain fixture exists + carries marker | 5.1b |
| T4L.01 | 1-8 | Live autopilot chain produces all 8 layers | 5.2 |

## Tier 5 — Packaging

| ID | Proof | Plan task |
|----|---|----|
| T5.01 | Bundle byte-identity via allow-list parse | 6.1 |
| T5.02 | VERSION + FRAMEWORK_SPEC_VERSION aligned | 6.2 |
| T5.03 | claude plugin validate --strict passes | 1.2 |

## Tier 3b — Non-layer skill probes

| ID | Skill | Proof | Plan task |
|----|---|---|----|
| T3b.01 | doc-flow | Dual-axis + anti-confab | 6.5.1 |
| T3b.02 | doc-validator | sdd_doc_lint surfaces STRUCT01 on broken fixture | 6.5.2 |

## Tier 6 — Release gate

| ID | Proof | Plan task |
|----|---|----|
| T6.01 | CHANGELOG has version section + no placeholders | 7.1 |
| T6.02 | Bundle ≤ size cap, skill count ≤ cap | 7.2 |
| T6.03 | No network egress in plugin code | 7.3 |
| T6.04 | No `--dangerously-skip-permissions` defaults in SKILL.md | 7.3 |
| T6.05 | Plugin manifest schema present | 7.3 |

## Tier 7 — Post-deploy smoke

| ID | Proof | Plan task |
|----|---|----|
| T7.01 | Install plugin + doc-flow probe + no confab phrases | 8.1 |

## Tier 8 — LLM code review (opt-in)

| ID | Proof | Plan task |
|----|---|----|
| T8.01 | Reviewer emits no BLOCKER/CRITICAL findings | 9.1 |
