# Shared negative fixtures

Curated broken artifacts used by `tests/scripts/test-acceptance.sh` Phase 1.2
to verify the plugin's gating skills detect regressions in audit/lint
sensitivity.

These fixtures are **shared across all examples** because they exercise
structural defects, not domain-specific failure modes. Per-example
additions (e.g. domain-specific business-rule violations) belong under
`examples/<NAME>/negative-fixtures/` and are merged on top at run time.

See `examples/url-shortener/ACCEPTANCE_TEST_PLAN.md` §5.2 for the
detection contract.

## Fixture index

| File | Layer | What's broken | Expected detection (code) | Deterministic? |
|---|---|---|---|:---:|
| `brd-broken-sections.md` | BRD | Missing `Functional Requirements` section | `STRUCT01` | ✅ |
| `brd-broken-tags.md` | BRD | Trace-tags use 3-segment form (`BRD.01.aaaa`) instead of canonical 4-segment | `ID01` | ✅ |
| `prd-broken-upstream-ref.md` | PRD | References well-formed but non-existent `@brd: BRD.99.01.aaaa` | `doc-validator` (live) reports unresolved reference | ❌ live |
| `ears-score-7.md` | EARS | Vague content + placeholders → low audit score; also tripwires several lint codes | `STRUCT01`/`PH01`/`TAG01` + `doc-ears-audit` (live) reports low score | ✅ partial / live for score |
| `adr-missing-sequence-diagram.md` | ADR | Missing `sequenceDiagram`; lint catches several missing sections incidentally | `STRUCT01` + `doc-adr-audit` (live) reports diagram contract violation | ✅ partial / live for diagram |
| `chain-trace-broken/` | full chain | PRD references well-formed `@brd: BRD.01.99.f7f7` with no matching section/hash in BRD | `doc-validator` (live) reports broken trace | ❌ live |

## Detection layers

Fixtures split into two detection categories:

- **Deterministic (lint-based)**: `brd-broken-sections.md`, `brd-broken-tags.md`,
  `ears-score-7.md` (partial), `adr-missing-sequence-diagram.md` (partial) —
  detected by `sdd_doc_lint` without any LLM cost. Phase 1.2 can verify
  these in `--no-live` mode.
- **LLM-based (audit/validator)**: `prd-broken-upstream-ref.md`,
  `chain-trace-broken/` (full), plus the audit-score portion of
  `ears-score-7.md` and `adr-missing-sequence-diagram.md` — require live
  invocation of `doc-<layer>-audit` or `doc-validator`. Exercised in
  `--live` mode only.

## Authoring guidance

When adding a new fixture:

1. Start from the corresponding golden chain artifact at
   `tests/acceptance/fixtures/fullpath/golden_chain/<NN>_<LAYER>/`.
2. Introduce a single, minimal defect — one fixture should exercise one
   detection rule, not multiple.
3. Add the fixture and its expected detection code (or live skill) to the
   table above.
4. Add an entry to `test-acceptance.sh`'s Phase 1.2 fixture loop so the
   assertion is actually checked.

Never edit golden fixtures to create negatives — copy first.

## Why ears-score-7 and adr-missing-sequence-diagram are multi-defect

Real low-quality EARS / ADR artifacts typically exhibit multiple defects
simultaneously (missing sections, placeholder text, missing traces).
Cleaning these fixtures down to a single defect would misrepresent the
real-world failure mode. Phase 1.2's job is to verify gating skills
catch broken artifacts; the detection codes table records what's
*expected* to fire, not what *only* fires.
