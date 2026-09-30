# Test Scenarios Catalog

> Catalog of what the deterministic suites cover. Add a row when you add a
> test; remove a row when you remove one. (Plugin/harness-era tiers were
> retired with the platforms, CHG-08 #670; their rows are deleted below —
> the record lives in `plans/ACCEPTANCE-HISTORY.md`.)

## Conventions

- **ID:** `<tier>.<group>.<n>` (e.g. `T3.brd.01` for tier-3 BRD scenario 1).
- **Layer:** 1–8 if layer-scoped; "—" if cross-cutting.
- **Plan task:** the implementation task that built it.

## Tier 1 — Static

| ID | Layer | Proof | Plan task |
|----|:-:|---|----|
| T1.01 | — | YAML templates parse and have required top keys | 1.1 |
| T1.03 | — | STRUCT01 fires on missing required section | 1.3 |
| T1.04 | — | sdd_doc_lint `--format=json` produces structured findings | 1.3 |

## Tier 2 — Unit

| ID | Layer | Proof | Plan task |
|----|:-:|---|----|
| T2.03 | — | Each lint code fires only on its target fixture | 2.2 |
| T2.04 | — | Sync scripts are idempotent | 2.3 |
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

## Tier 4 — Full-path acceptance

| ID | Layer | Proof | Plan task |
|----|:-:|---|----|
| T4.01 | 1-8 | Golden chain lint passes | 5.1 |
| T4.02 | 1-8 | Every layer has one artifact | 5.1 |
| T4.03 | 1-8 | Every layer has required sections | 5.1 |
| T4.04 | 1-8 | Forward-tag closure | 5.1 |
| T4.05 | 1-8 | Broken-chain fixture exists + carries marker | 5.1b |
