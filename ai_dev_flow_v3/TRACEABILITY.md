# Traceability — SDD v3

## Traceability Chain

```
BRD (L1) → PRD (L2) → EARS (L3) → BDD (L4) → ADR (L5) → TDD (L6) → SPEC (L7) → Code
```

## Cumulative Tagging

Each layer inherits and adds one tag:

```
Layer 1 (BRD):  @brd
Layer 2 (PRD):  @brd @prd
Layer 3 (EARS): @brd @prd @ears
Layer 4 (BDD):  @brd @prd @ears @bdd
Layer 5 (ADR):  @brd @prd @ears @bdd @adr
Layer 6 (TDD):  @brd @prd @ears @bdd @adr @tdd
Layer 7 (SPEC): @brd @prd @ears @bdd @adr @tdd @spec
```

## Upstream/Downstream Validation

| Layer | Required Upstream Tags | Validated Downstream |
|-------|----------------------|---------------------|
| BRD | — | PRD |
| PRD | @brd | EARS |
| EARS | @brd, @prd | BDD |
| BDD | @brd, @prd, @ears | ADR, TDD |
| ADR | @brd, @prd, @ears, @bdd | TDD |
| TDD | @brd, @prd, @ears, @bdd, @adr | SPEC |
| SPEC | @brd, @prd, @ears, @bdd, @adr, @tdd | Code |

## Layer Readiness Gates

Each layer must achieve a readiness score >=90/100 before generating its immediate downstream artifact:

| Gate | Score | Criteria |
|------|-------|----------|
| PRD-Ready | >=90 | BRD completeness in business objectives, requirements, scope |
| EARS-Ready | >=90 | PRD completeness in features, user stories, domain clarity |
| BDD-Ready | >=90 | EARS syntax compliance, atomicity, testability |
| ADR-Ready | >=90 | BDD scenario coverage, Gherkin quality, edge cases |
| TDD-Ready | >=90 | ADR decision completeness, alternatives, consequences |
| CODE-Ready | >=90 | SPEC interface clarity, data model, test contracts |

## Cross-Document Dependencies

- `@depends: TYPE-NN` — Hard prerequisite. Downstream cannot exist without upstream.
- `@discoverability: TYPE-NN` — Related document for AI search context.
- `@threshold: TYPE.NN.key` — Performance or quality threshold reference.
