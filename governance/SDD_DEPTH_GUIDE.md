# SDD Depth Guide (v3.2)

This guide maps governance depth to the active SDD v3.2 artifact chain.

## Canonical Chain

`BRD->PRD->EARS->BDD->ADR->SPEC->TDD->IPLAN->Code`

## Depth Comparison

| Aspect | Lite | Standard | Full |
|---|---|---|---|
| Artifact count | Minimal | Moderate | Full |
| Chain usage | BRD->PRD->IPLAN | BRD->PRD->EARS->ADR->SPEC->TDD->IPLAN | BRD->PRD->EARS->BDD->ADR->SPEC->TDD->IPLAN |
| CHG gates | Optional | Optional | Required |
| Traceability | Basic | Strong | Full governance + CHG |

## CHG Gate Overlay (v3)

- `GATE-01` business/product
- `GATE-03` requirements/architecture
- `GATE-06` design/test
- `GATE-08` execution plan
- `GATE-CODE` implementation/release

## Scaling Guidance

- Start Lite for constrained scope.
- Add EARS/ADR/SPEC/TDD for stronger validation.
- Add BDD + CHG gates for regulated or high-risk programs.

## References

- `ucx_flow_v3/README.md`
- `ucx_flow_v3/LAYER_REGISTRY.yaml`
- `ucx_flow_v3/CHG/`
