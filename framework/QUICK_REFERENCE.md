# Quick Reference

## 8-Layer Chain

```
BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code
```

## Templates

| Layer | Template | Upstream Tags |
|-------|----------|---------------|
| L1 BRD | [BRD-TEMPLATE.yaml](layers/01_BRD/BRD-TEMPLATE.yaml) | — |
| L2 PRD | [PRD-TEMPLATE.yaml](layers/02_PRD/PRD-TEMPLATE.yaml) | @brd |
| L3 EARS | [EARS-TEMPLATE.yaml](layers/03_EARS/EARS-TEMPLATE.yaml) | @prd |
| L4 BDD | [BDD-TEMPLATE.yaml](layers/04_BDD/BDD-TEMPLATE.yaml) | @ears |
| L5 ADR | [ADR-TEMPLATE.yaml](layers/05_ADR/ADR-TEMPLATE.yaml) | @ears @bdd |
| L6 SPEC | [SPEC-TEMPLATE.yaml](layers/06_SPEC/SPEC-TEMPLATE.yaml) | @ears @bdd @adr |
| L7 TDD | [TDD-TEMPLATE.yaml](layers/07_TDD/TDD-TEMPLATE.yaml) | @ears @bdd @adr @spec |
| L8 IPLAN | [IPLAN-TEMPLATE.yaml](layers/08_IPLAN/IPLAN-TEMPLATE.yaml) | @spec @tdd |

## Key Files

| File | Purpose |
|------|---------|
| [LAYER_REGISTRY.yaml](registry/LAYER_REGISTRY.yaml) | Authoritative layer definitions |
| [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) | SDD methodology |
| [ID_NAMING_STANDARDS.md](governance/ID_NAMING_STANDARDS.md) | Document and element ID formats |
| [TRACEABILITY.md](governance/TRACEABILITY.md) | Cross-layer traceability rules |
| [DIAGRAM_STANDARDS.md](governance/DIAGRAM_STANDARDS.md) | Mermaid diagram conventions |
| [THRESHOLD_NAMING_RULES.md](governance/THRESHOLD_NAMING_RULES.md) | Threshold key naming |
| [SECURITY_REVIEW.md](governance/SECURITY_REVIEW.md) | Safety checks for agent-authored artifacts |
| [REVIEW_REMEDIATION_FLOW.md](governance/REVIEW_REMEDIATION_FLOW.md) | Review→remediation→gate loop + trigger points |
| [TESTING_STRATEGY_TDD.md](TESTING_STRATEGY_TDD.md) | TDD integration |

## Readiness Gates

| Gate | Target | Check |
|------|--------|-------|
| PRD-Ready | >=90/100 | BRD objectives, requirements, scope complete |
| EARS-Ready | >=90/100 | PRD features, user stories, domain clarity |
| BDD-Ready | >=90/100 | EARS syntax, atomicity, testability |
| ADR-Ready | >=90/100 | BDD scenarios, scenario quality, edge cases |
| TDD-Ready | >=90/100 | SPEC interfaces, data models, behavior contracts |
| IPLAN-Ready | >=90/100 | TDD test case coverage, threshold definitions |
| EXEC-Ready | >=90/100 | IPLAN file manifest completeness, execution commands, contracts |
