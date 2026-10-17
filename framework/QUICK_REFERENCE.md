# Quick Reference

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-09-07 |
| Author | Framework Maintainer |
| Framework Version | 0.96.1 |


## 10-Layer SDD Framework

```
BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code
                                                        ↓
                                              CHG (governance overlay)
                                              EVAL (evaluation/QA)
```

## Templates

| Layer | Standard Template | Workflow Template (Tier 1) | Graph Template (Tier 2) | Upstream Tags |
|-------|-------------------|----------------------------|-------------------------|---------------|
| L1 BRD | [BRD-TEMPLATE.yaml](layers/01_BRD/BRD-TEMPLATE.yaml) | [BRD-SWF-TEMPLATE.yaml](layers/01_BRD/BRD-SWF-TEMPLATE.yaml) | [BRD-GRAPH-TEMPLATE.yaml](layers/01_BRD/BRD-GRAPH-TEMPLATE.yaml) | — |
| L2 PRD | [PRD-TEMPLATE.yaml](layers/02_PRD/PRD-TEMPLATE.yaml) | [PRD-SWF-TEMPLATE.yaml](layers/02_PRD/PRD-SWF-TEMPLATE.yaml) | [PRD-GRAPH-TEMPLATE.yaml](layers/02_PRD/PRD-GRAPH-TEMPLATE.yaml) | @brd |
| L3 EARS | [EARS-TEMPLATE.yaml](layers/03_EARS/EARS-TEMPLATE.yaml) | [EARS-SWF-TEMPLATE.yaml](layers/03_EARS/EARS-SWF-TEMPLATE.yaml) | [EARS-GRAPH-TEMPLATE.yaml](layers/03_EARS/EARS-GRAPH-TEMPLATE.yaml) | @prd |
| L4 BDD | [BDD-TEMPLATE.yaml](layers/04_BDD/BDD-TEMPLATE.yaml) | [BDD-SWF-TEMPLATE.yaml](layers/04_BDD/BDD-SWF-TEMPLATE.yaml) | [BDD-GRAPH-TEMPLATE.yaml](layers/04_BDD/BDD-GRAPH-TEMPLATE.yaml) | ears (YAML carrier) |
| L5 ADR | [ADR-TEMPLATE.yaml](layers/05_ADR/ADR-TEMPLATE.yaml) | [ADR-SWF-TEMPLATE.yaml](layers/05_ADR/ADR-SWF-TEMPLATE.yaml) | [ADR-GRAPH-TEMPLATE.yaml](layers/05_ADR/ADR-GRAPH-TEMPLATE.yaml) | @ears @bdd |
| L6 SPEC | [SPEC-TEMPLATE.yaml](layers/06_SPEC/SPEC-TEMPLATE.yaml) | [SPEC-SWF-TEMPLATE.yaml](layers/06_SPEC/SPEC-SWF-TEMPLATE.yaml) | [SPEC-GRAPH-TEMPLATE.yaml](layers/06_SPEC/SPEC-GRAPH-TEMPLATE.yaml) | @ears @bdd @adr |
| L7 TDD | [TDD-TEMPLATE.yaml](layers/07_TDD/TDD-TEMPLATE.yaml) | [TDD-SWF-TEMPLATE.yaml](layers/07_TDD/TDD-SWF-TEMPLATE.yaml) | [TDD-GRAPH-TEMPLATE.yaml](layers/07_TDD/TDD-GRAPH-TEMPLATE.yaml) | @ears @bdd @adr @spec |
| L8 IPLAN | [IPLAN-TEMPLATE.yaml](layers/08_IPLAN/IPLAN-TEMPLATE.yaml) | [IPLAN-SWF-TEMPLATE.yaml](layers/08_IPLAN/IPLAN-SWF-TEMPLATE.yaml) | [IPLAN-GRAPH-TEMPLATE.yaml](layers/08_IPLAN/IPLAN-GRAPH-TEMPLATE.yaml) | @spec @tdd |
| L9 CHG | [CHG-TEMPLATE.yaml](layers/09_CHG/CHG-TEMPLATE.yaml) | [CHG-SWF-TEMPLATE.yaml](layers/09_CHG/CHG-SWF-TEMPLATE.yaml) | [CHG-GRAPH-TEMPLATE.yaml](layers/09_CHG/CHG-GRAPH-TEMPLATE.yaml) | governance overlay |
| L10 EVAL | [EVAL-TEMPLATE.yaml](layers/10_EVAL/EVAL-TEMPLATE.yaml) | [EVAL-SWF-TEMPLATE.yaml](layers/10_EVAL/EVAL-SWF-TEMPLATE.yaml) | [EVAL-GRAPH-TEMPLATE.yaml](layers/10_EVAL/EVAL-GRAPH-TEMPLATE.yaml) | @ears @bdd @tdd @iplan |

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
| PRD-Ready | BTV PASS | BRD objectives, requirements, scope complete |
| EARS-Ready | BTV PASS | PRD features, user stories, domain clarity |
| BDD-Ready | BTV PASS | EARS syntax, atomicity, testability |
| ADR-Ready | BTV PASS | BDD scenarios, scenario quality, edge cases |
| SPEC-Ready | BTV PASS | ADR decisions, alternatives, consequences complete |
| TDD-Ready | BTV PASS | SPEC interfaces, data models, behavior contracts |
| IPLAN-Ready | BTV PASS | TDD test case coverage, threshold definitions |
| EXEC-Ready | BTV PASS | IPLAN file manifest completeness, execution commands, contracts |
