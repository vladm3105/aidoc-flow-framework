# Phase 1 benchmark — frozen task set (30 tasks)

Model: Muse Code, powered by Meta Muse Spark (single named model for all passes).
Rubric: exact match on (flow code, entry gate, verification key) per task.
Repeats: 3 per task per arm, majority vote. Task order shuffled per pass.
Retrieval steps recorded per task per pass (median reported, not gated).

Ground-truth source: `framework/governance/CHG_REQUEST_FLOWS.md` §1 (canonical)
plus the Spec → GATE-SPEC row of `framework/governance/chg/README.md`.
Frozen 2026-10-26 before any arm was run. No edits after freezing.

## Classification tasks (T01–T24)

| ID | Change description | Flow | Entry gate | Verification key |
|----|--------------------|------|-----------|------------------|
| T01 | Payment service down in production, needs an immediate fix before any authorization | HOTFIX | Post-hoc | Post-mortem verification |
| T02 | Active data-loss incident in production, fix must deploy now, documents follow | HOTFIX | Post-hoc | Post-mortem verification |
| T03 | Security breach being exploited, emergency patch required tonight | HOTFIX | Post-hoc | Post-mortem verification |
| T04 | Production outage, fix first and write the post-mortem within 48h | HOTFIX | Post-hoc | Post-mortem verification |
| T05 | Working authentication code exists but was never specified; specs must be written from the code | CODE2S | GATE-CODE | Phase-3 battery |
| T06 | Implemented feature predates its BDD scenarios; reverse-author the specs from ground truth | CODE2S | GATE-CODE | Phase-3 battery |
| T07 | Empirical prototype works and needs reconciling backward Code→TDD→SPEC→BDD→EARS | CODE2S | GATE-CODE | Phase-3 battery |
| T08 | Verified codebase has no EARS coverage; propagate it backward to SDD layers | CODE2S | GATE-CODE | Phase-3 battery |
| T09 | Defect found in EVAL, traceable to a Completed parent IPLAN | CODE2C | GATE-CODE | Regression suite |
| T10 | Field-reported bug with a Verified parent IPLAN; needs a repair-scoped fix | CODE2C | GATE-CODE | Regression suite |
| T11 | Manual testing surfaced a defect in a shipped increment with a Completed IPLAN | CODE2C | GATE-CODE | Regression suite |
| T12 | Regression in deployed code whose parent IPLAN is Completed | CODE2C | GATE-CODE | Regression suite |
| T13 | New capability added to an already implemented product | SEED2C | GATE-01 / 03 / 06 / GATE-SPEC | EVAL cycles + live closeout |
| T14 | Product behavior change on a shipped product requiring cross-layer updates | SEED2C | GATE-01 / 03 / 06 / GATE-SPEC | EVAL cycles + live closeout |
| T15 | Change a gate-approval table inside a framework governance template (change_source: spec) | SEED2C | GATE-SPEC | EVAL cycles + live closeout |
| T16 | Change a lint-rule severity in LINT_RULES.md (change_source: spec) | SEED2C | GATE-SPEC | EVAL cycles + live closeout |
| T17 | Fix a typo in the consumer README, no prior IPLAN, no behavior change | DIR2C | GATE-CODE | Covering tests + verification commands |
| T18 | Add a new pre-commit hook script requested by a maintainer | DIR2C | GATE-CODE | Covering tests + verification commands |
| T19 | Tweak a CI workflow file, docs-only scope, no product change | DIR2C | GATE-CODE | Covering tests + verification commands |
| T20 | Restructure a docs page, no behavior change, no prior IPLAN | DIR2C | GATE-CODE | Covering tests + verification commands |
| T21 | Brand-new product, no implementation exists, starting from BRD | SDD2C | GATE-01 | EVAL cycles + live closeout |
| T22 | New layer chain BRD→PRD→…→Code with no prior code | SDD2C | GATE-01 | EVAL cycles + live closeout |
| T23 | First implementation of an approved PRD where nothing is built yet | SDD2C | GATE-01 | EVAL cycles + live closeout |
| T24 | Greenfield module chain through all 10 SDD layers | SDD2C | GATE-01 | EVAL cycles + live closeout |

Frozen note on T15/T16: the `spec` change_source occurs only in the SEED2C
row, so the doc-derived flow ground truth is SEED2C even though the DIR2C
trigger ("no product-behavior change") also reads plausibly. This ambiguity
is a property of the document, identical across arms; it is analyzed, not
re-frozen, in the results.

## Retrieval tasks (T25–T30)

| ID | Query | Expected |
|----|-------|----------|
| T25 | Which flow identifier corresponds to legacy alias F2? | `iplan_to_code` (DIR2C) |
| T26 | Which entry gate does the Direct source route to? | GATE-CODE |
| T27 | What IPLAN shape does a CODE2C fix carry? | Bugfix-subtype (`parent_iplan` + `source_chg`, repair-scoped manifest, rollback) |
| T28 | State the router's first-match order. | HOTFIX → CODE2S → CODE2C → SEED2C → DIR2C → SDD2C |
| T29 | Which flow declares `sdd_lifecycle: []`? | DIR2C |
| T30 | Which source routes to GATE-SPEC? | Spec |
