# Traceability — SDD

## Traceability Chain

```
BRD (L1) → PRD (L2) → EARS (L3) → BDD (L4) → ADR (L5) → SPEC (L6) → TDD (L7) → IPLAN (L8) → Code
```

## Cumulative Tagging

Each layer inherits and adds one tag:

```
Layer 1 (BRD):   @brd
Layer 2 (PRD):   @brd @prd
Layer 3 (EARS):  @brd @prd @ears
Layer 4 (BDD):   @brd @prd @ears @bdd
Layer 5 (ADR):   @brd @prd @ears @bdd @adr
Layer 6 (SPEC):  @brd @prd @ears @bdd @adr @spec
Layer 7 (TDD):   @brd @prd @ears @bdd @adr @spec @tdd
Layer 8 (IPLAN): @brd @prd @ears @bdd @adr @spec @tdd @iplan
```

Maximum 8 cumulative tags at IPLAN layer.

## Upstream/Downstream Validation

| Layer | Required Upstream Tags | Validated Downstream |
|-------|----------------------|---------------------|
| BRD | — | PRD |
| PRD | @brd | EARS |
| EARS | @brd, @prd | BDD |
| BDD | @brd, @prd, @ears | ADR |
| ADR | @brd, @prd, @ears, @bdd | SPEC |
| SPEC | @brd, @prd, @ears, @bdd, @adr | TDD |
| TDD | @brd, @prd, @ears, @bdd, @adr, @spec | IPLAN |
| IPLAN | @brd, @prd, @ears, @bdd, @adr, @spec, @tdd | Code |

## Layer Readiness Gates

Each layer must achieve a readiness score >=90/100 before generating its immediate downstream artifact:

| Gate | Score | Criteria |
|------|-------|----------|
| PRD-Ready | >=90 | BRD completeness in business objectives, requirements, scope |
| EARS-Ready | >=90 | PRD completeness in features, user stories, domain clarity |
| BDD-Ready | >=90 | EARS syntax compliance, atomicity, testability, spec_trace links |
| ADR-Ready | >=90 | BDD scenario coverage, Gherkin quality, edge cases |
| TDD-Ready | >=90 | SPEC interface clarity, data model, behavior contracts |
| IPLAN-Ready | >=90 | TDD test case coverage, threshold definitions, execution order |
| EXEC-Ready | >=90 | IPLAN file manifest completeness, execution commands, session handoff |

## Cross-Document Dependencies

- `@depends: TYPE-NN` — Hard prerequisite. Downstream cannot exist without upstream.
- `@discoverability: TYPE-NN` — Related document for AI search context.
- `@threshold: TYPE.NN.key` — Performance or quality threshold reference.
